"""`--fix` for a plain class's variables, typed by their literal values (a guess: `member`)."""

import ast
import textwrap
from pathlib import Path
from typing import Final, TypeAlias

from constricter import Checks, FixPolicy, Offence, check_source
from constricter.cli import command as cli
from constricter.fix.index import crossed, plain, project
from constricter.fix.libraries import stdlib
from constricter.fix.values import classvars

# Each offence's fix and whether it's a guess.
_Fixed: TypeAlias = dict[str, tuple[str | None, bool]]
_ALL: Final = Checks(all_scopes=True)
SOURCE: Final = """
import unittest
from dataclasses import dataclass
from enum import Enum
from unittest import TestCase as Case

import other


class Plain(object):
    limit = 3
    names = ["a", "b"]
    pair = (1, "x")
    ratio = 1 / 2
    made = make()
    copied = limit
    nothing = None
    twice = 1
    twice = 2
    stored = 0
    kept: int = 1
    first = second = 0
    low, high = 0, 1
    for step in (1, 2):
        pass

    def helper(self) -> None:
        self.stored = None

    helper = 0


class Child(Plain):
    extra = 1.5


class Tests(unittest.TestCase):
    maxDiff = 80


class More(Case, Child):
    verbose = True


@dataclass
class Data:
    x = 1


class Mixin:
    shared = 1


class Model(Mixin, other.Base):
    y = 1


class Registry(type):
    z = 1


class Registered(metaclass=Registry):
    w = 1


class Computed(make()):
    v = 1


class Color(Enum):
    RED = 1


class Twice:
    a = 1


class Twice:
    b = 1
"""
READS: Final = """
class Config:
    limit = 3
    names = ["a"]
    MODE = "r"
    label: str = ""

    def read(self) -> None:
        a = self.limit
        b = self.names[0]
        c = self.label

    @classmethod
    def build(cls) -> None:
        d = cls.limit


class Local(Config):
    extra = 1.5

    def read(self) -> None:
        e = self.limit
        g = self.extra


def use(config: Config, other) -> None:
    h = config.limit
    i = config.missing
    j = other.limit
    open("x", Config.MODE)
"""


def _fixed(source: str, checks: Checks = _ALL) -> _Fixed:
    found: list[Offence] = check_source(textwrap.dedent(source), checks=checks)
    return {o.name: (o.fix, o.unsafe) for o in found}


def test_a_plain_class_variable_is_typed_by_its_literal_value() -> None:
    """One bound once, directly in the body, to a literal or a display of them; and nothing else there."""
    fixed: _Fixed = _fixed(SOURCE)
    assert {name: fix for name, fix in fixed.items() if fix[0]} == {
        "limit": ("int", True),
        "names": ("list[str]", True),
        "pair": ("tuple[int, str]", True),
        "ratio": ("float", True),
        "extra": ("float", True),  # under a plain class
        "maxDiff": ("int | None", True),  # under a test case, which declares it so
        "verbose": ("bool", True),  # under both
    }
    # A call (`made`), a copy (`copied`), `None`, a name bound twice (`twice`), an attribute
    # the module stores (`stored`), a chained assignment, an unpacking and a loop; and every variable
    # of a class that isn't plain: decorated (`x`), a model's mixin (`shared`) and the model (`y`),
    # a metaclass (`z`) and its instance (`w`), a computed base (`v`), an enum's (not reported at
    # all), and one defined twice (`a`, `b`).
    untyped: set[str] = {"made", "copied", "nothing", "twice", "stored", "first", "second"}
    assert {name for name, fix in fixed.items() if not fix[0]} == untyped | {"low", "high", "step"} | set(
        "xyzwvab",
    ) | {"shared"}


def test_what_reads_the_variable_is_typed_in_the_same_run() -> None:
    """On an instance, a subclass's, or the class in a classmethod: a guess, resting on `member`."""
    found: list[Offence] = check_source(textwrap.dedent(READS))
    assert {o.name: (o.fix, o.unsafe) for o in found} == {
        "a": ("int", True),
        "b": ("str", True),
        "c": ("str", False),  # declared: certain
        "d": ("int", True),
        "e": ("int", True),  # its base's
        "g": ("float", True),
        "h": ("int", True),
        "i": (None, False),
        "j": (None, False),
    }
    kinds: dict[str, frozenset[str]] = {o.name: o.edit.kinds for o in found if o.edit is not None}
    assert kinds["a"] == {"member"}
    assert kinds["b"] == {"member", "subscript"}
    trusting: Checks = Checks(fixes=FixPolicy(unsafe_select=frozenset({"member"})))
    assert _fixed(READS, trusting)["a"] == ("int", False)
    ignoring: Checks = Checks(all_scopes=True, fixes=FixPolicy(ignore=frozenset({"member"})))
    assert {name for name, fix in _fixed(READS, ignoring).items() if fix[0]} == {"c"}


def test_a_class_constant_passed_to_a_call_keeps_its_type() -> None:
    """`Final`, a module's constant's, isn't a class variable's fix: its value's type is."""
    assert _fixed(READS)["MODE"] == ("str", True)
    assert _fixed('MODE = "r"\nopen("x", MODE)\n')["MODE"] == ("Final", True)


def test_plain_classes_are_settled_by_their_bases() -> None:
    """Every base plain, or a test case; none inherited by a class that isn't."""
    tree: ast.Module = ast.parse(textwrap.dedent(SOURCE))
    assert classvars.plain(tree, stdlib.origins(tree)) == {"Plain", "Child", "Tests", "More"}
    found: dict[str, tuple[str, ...]] = {
        "A": (),
        "B": ("A",),
        "C": ("B", "elsewhere.Base"),
        "E": (classvars.SPECIAL,),
        "F": ("E",),
        "G": ("ok.Case",),
    }
    assert classvars.settled(found, "ok.Case".__eq__) == {"G"}
    assert classvars.settled({"D": ("D",), "H": ("I",), "I": ("H", "unknown")}, "ok.Case".__eq__) == {"D"}
    assert classvars.settled({name: found[name] for name in "AB"}, "ok.Case".__eq__) == {"A", "B"}


BASES: Final = """
import unittest


class Base:
    size = 1


class Wide(Base):
    width = 3


class Case(unittest.TestCase):
    retries = 2


class Mixin:
    flag = True
"""
FIXED_BASES: Final = (
    BASES.replace("size = 1", "size: int = 1")
    .replace("width = 3", "width: int = 3")
    .replace("retries = 2", "retries: int = 2")
)
MODELS: Final = """
from dataclasses import dataclass

from pkg.bases import Mixin


@dataclass
class Model(Mixin):
    x: int = 0
"""
USING: Final = """
import pkg.bases as bases
from pkg.bases import Base, Case, Mixin


class Child(Base):
    depth = 2

    def read(self) -> None:
        a = self.size
        b = self.depth


class Tests(Case):
    slow = False


class Other(bases.Base, Mixin):
    wide = "x"


def use(base: Base, mixin: Mixin) -> None:
    c = base.size
    d = mixin.flag
"""
USED: Final = """
import pkg.bases as bases
from pkg.bases import Base, Case, Mixin


class Child(Base):
    depth: int = 2

    def read(self) -> None:
        a: int = self.size
        b: int = self.depth


class Tests(Case):
    slow: bool = False


class Other(bases.Base, Mixin):
    wide: str = "x"


def use(base: Base, mixin: Mixin) -> None:
    c: int = base.size
    d = mixin.flag
"""


def _package(root: Path) -> list[Path]:
    """Write `pkg` (plain bases, a model under one of them) and a file using it, under `root`.

    Returns:
      Their paths, the using file last.

    """
    files: dict[str, str] = {
        "pkg/__init__.py": "",
        "pkg/bases.py": BASES,
        "pkg/models.py": MODELS,
        "using.py": USING,
    }
    paths: list[Path] = []
    name: str
    source: str
    for name, source in files.items():
        path: Path = root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        _ = path.write_text(source, encoding="utf-8")
        paths.append(path)
    return paths


def test_another_files_plain_class_is_a_plain_base(tmp_path: Path) -> None:
    """The index follows a base to its file: plain there, and never a class a model inherits from."""
    paths: list[Path] = _package(tmp_path)
    catalog: project.Index = plain.settled(project.index(paths))
    assert catalog.modules["pkg.bases"].plain == {"Base", "Wide", "Case"}  # `Mixin` is a model's
    assert catalog.modules["pkg.models"].plain == frozenset()
    assert catalog.modules["using"].plain == {"Child", "Tests", "Other"}
    assert plain.classes(catalog, paths[-1]) == frozenset({"Child", "Tests", "Other"})
    assert plain.classes(catalog, tmp_path / "missing.py") is None
    assert crossed.imported(catalog, paths[-1]).members == {
        "Base": {"size": "int"},
        "Case": {"retries": "int"},
        "bases.Base": {"size": "int"},
        "bases.Wide": {"width": "int"},
        "bases.Case": {"retries": "int"},
    }
    assert plain.settled(project.Index({}, [])) == project.Index({}, [])


def test_one_run_fixes_the_class_and_what_reads_it(tmp_path: Path) -> None:
    """The class's file and the files reading its variables, in one pass: a second changes nothing."""
    paths: list[Path] = _package(tmp_path)
    arguments: list[str] = ["--fix", "--unsafe-fixes", "--all-scopes", "-q", "--jobs=1", str(tmp_path)]
    for _ in range(2):
        assert cli.main(arguments) == cli.EXIT_FOUND
        assert paths[-1].read_text(encoding="utf-8") == USED
        assert paths[1].read_text(encoding="utf-8") == FIXED_BASES


GENERIC: Final = """from typing import Generic, TypeVar

T = TypeVar("T")


class Read1:
    pass


class Base(Generic[T]):
    read1 = Read1


class Sub(Base[str]):
    def parse(self) -> None:
        r = self.read1
"""


def test_a_generic_bases_variable_is_read_through_its_arguments(tmp_path: Path) -> None:
    """`self.read1` under `Base[str]` is `Base`'s, as a plain base's is: a second pass changes nothing."""
    path: Path = tmp_path / "parser.py"
    _ = path.write_text(GENERIC, encoding="utf-8")
    arguments: list[str] = ["--fix", "--unsafe-fixes", "--all-scopes", "-q", "--jobs=1", str(tmp_path)]
    fixed: str = GENERIC.replace("read1 = Read1", "read1: type[Read1] = Read1").replace(
        "r = self.read1",
        "r: type[Read1] = self.read1",
    )
    for _ in range(2):
        assert cli.main(arguments) == cli.EXIT_CLEAN
        assert path.read_text(encoding="utf-8") == fixed


def test_a_class_with_no_typed_variable_has_none() -> None:
    """A module whose classes bind nothing a value types isn't read for what they annotate."""
    assert classvars.members(ast.parse("class Empty(ValueError):\n    made = make()\n")) == {}


STORED: Final = """
class Reader:
    closed = False
    count = 0
    names = ["a"]
    label = ""
    size = 0
    ratio = 1.5
    flag = False
    width = 1
    depth = 1
    first = 0
    gone = 0
    typed = 0

    def close(self, size, other) -> None:
        self.closed = True
        self.count += 1
        self.count = self.count = 2
        self.names += ["b"]
        self.label = None
        self.size = size
        self.ratio += size
        self.flag += 1
        self.width, self.depth = 2, 3
        for self.first in (1, 2):
            pass
        del self.gone
        self.typed: int = 1
        other.closed = False
"""


def test_a_variable_the_module_stores_as_the_same_type_is_typed() -> None:
    """`self.closed = True` keeps a `bool`, and `self.count += 1` an `int`; any other store may not."""
    fixed: _Fixed = _fixed(STORED)
    assert {name: fix for name, fix in fixed.items() if fix[0]} == {
        "closed": ("bool", True),
        "count": ("int", True),
        "names": ("list[str]", True),
    }
    # `None`, a parameter, an operator that gives another type, an unpacking, a loop's target, a
    # `del` and an annotated store.
    assert {name for name, fix in fixed.items() if not fix[0]} == {
        "label",
        "size",
        "ratio",
        "flag",
        "width",
        "depth",
        "first",
        "gone",
        "typed",
    }


HELD: Final = """
import unittest

from framework import Case


class Tests(unittest.IsolatedAsyncioTestCase):
    maxDiff = 80
    longMessage = False
    retries = 2

    def tune(self) -> None:
        self.maxDiff = 100


class Wrong(unittest.TestCase):
    maxDiff = "all"


class Framed(Case):
    maxDiff = 1


class Whole(unittest.TestCase):
    maxDiff = None
    longMessage = None


class Under(Framed):
    maxDiff = 2


class Free:
    maxDiff = 3


class Failed(ValueError):
    maxDiff = 4
"""


def test_a_variable_a_test_case_declares_has_that_type() -> None:
    """Under one, or a base that may be one: `maxDiff` is an `int | None` to a type checker."""
    found: list[Offence] = check_source(
        textwrap.dedent(HELD),
        checks=Checks(all_scopes=True, plain_bases=("framework",)),
    )
    fixes: list[tuple[str, int, str | None]] = [(o.name, o.line, o.fix) for o in found]
    lines: list[str] = textwrap.dedent(HELD).splitlines()
    assert {(name, lines[line - 1].strip()): fix for name, line, fix in fixes} == {
        ("maxDiff", "maxDiff = 80"): "int | None",  # and a store of an `int` keeps it
        ("longMessage", "longMessage = False"): "bool",
        ("retries", "retries = 2"): "int",
        ("maxDiff", 'maxDiff = "all"'): None,  # not of the type declared
        ("maxDiff", "maxDiff = 1"): "int | None",  # a framework's base may be a test case
        ("maxDiff", "maxDiff = 2"): "int | None",
        ("maxDiff", "maxDiff = None"): "int | None",
        ("longMessage", "longMessage = None"): None,  # a `bool`
        ("maxDiff", "maxDiff = 3"): "int",  # its own
        ("maxDiff", "maxDiff = 4"): "int",
    }
    assert classvars.HELD == {
        "failureException": "type[BaseException]",
        "longMessage": "bool",
        "maxDiff": "int | None",
    }
    assert stdlib.attributes("unittest.IsolatedAsyncioTestCase") == stdlib.attributes("unittest.TestCase")


LIBRARY: Final = """
import datetime as dt
import os
import re
from decimal import Decimal
from pathlib import Path
from re import compile as build

import other


class Config:
    pattern = re.compile("x")
    built = build("y")
    sep = os.sep
    root = Path("a")
    zero = Decimal("0")
    day = dt.timedelta(days=1)
    size = len("abc")
    names = sorted(["b", "a"])
    upper = "a".upper()
    env = os.environ.get("X")
    made = Thing()
    theirs = other.make()
    lock = other.Lock()

    def read(self) -> None:
        a = self.pattern
        b = self.day
"""


def test_a_variable_is_typed_by_what_the_standard_library_gives() -> None:
    """A function's or a class's of its own, an attribute, a builtin: as the module names them."""
    fixed: _Fixed = _fixed(LIBRARY)
    assert {name: fix[0] for name, fix in fixed.items() if fix[0]} == {
        "pattern": "re.Pattern[str]",
        "built": "re.Pattern[str]",
        "sep": "str",
        "root": "Path",
        "zero": "Decimal",
        "day": "dt.timedelta",
        "size": "int",
        "names": "list[str]",
        "upper": "str",
        "a": "re.Pattern[str]",  # and what reads one
        "b": "dt.timedelta",
    }
    # A union (which a read of isn't offered), a class the module doesn't define, another module's.
    assert {name for name, fix in fixed.items() if not fix[0]} == {"env", "made", "theirs", "lock"}


SHAPES: Final = """
import datetime as dt
import re
from decimal import Decimal


class Config:
    pattern = re.compile("x")
    day = dt.timedelta(days=1)
    rate = Decimal("1")
    limit = 3
"""
READING: Final = """
import re

from pkg.shapes import Config


def read(config: Config) -> None:
    a = config.pattern
    b = config.day
    c = config.rate
    d = config.limit
"""
READ: Final = """
import re

from pkg.shapes import Config
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from decimal import Decimal
    import datetime as dt


def read(config: Config) -> None:
    a: re.Pattern[str] = config.pattern
    b: dt.timedelta = config.day
    c: Decimal = config.rate
    d: int = config.limit
"""
CLASHING: Final = """
from pkg import shapes

dt: int = 1
Decimal: int = 2


def read(config: shapes.Config) -> None:
    b = config.day
    c = config.rate
    d = config.limit
"""


def test_another_file_reads_a_library_type_as_it_can_write_it(tmp_path: Path) -> None:
    """By its own imports, or one added for type checking; not where the name means something else."""
    files: dict[str, str] = {
        "pkg/__init__.py": "",
        "pkg/shapes.py": SHAPES,
        "reading.py": READING,
        "clashing.py": CLASHING,
    }
    name: str
    source: str
    for name, source in files.items():
        (tmp_path / name).parent.mkdir(parents=True, exist_ok=True)
        _ = (tmp_path / name).write_text(source, encoding="utf-8")
    arguments: list[str] = ["--fix", "--unsafe-fixes", "--all-scopes", "-q", "--jobs=1", str(tmp_path)]
    for _ in range(2):
        assert cli.main(arguments) == cli.EXIT_FOUND
        assert (tmp_path / "reading.py").read_text(encoding="utf-8") == READ
        assert (tmp_path / "clashing.py").read_text(encoding="utf-8") == CLASHING.replace(
            "d = config.limit",
            "d: int = config.limit",
        )


FORMS: Final = """\
class PasswordForm:
    pass


class OtherForm:
    pass


def make():
    return PasswordForm()
"""
VIEWS: Final = """\
from pkg.forms import PasswordForm, make


class Local:
    pass


class View:
    form_class = PasswordForm
    local_class = Local
    overridden = PasswordForm
    maker = make

    def get(self):
        made = self.local_class()
        return made
"""
SUB: Final = """\
from pkg.forms import OtherForm
from pkg.views import View


class Sub(View):
    overridden = OtherForm
"""
FIXED_VIEWS: Final = """\
from pkg.forms import PasswordForm, make


class Local:
    pass


class View:
    form_class: type[PasswordForm] = PasswordForm
    local_class: type[Local] = Local
    overridden = PasswordForm
    maker = make

    def get(self):
        made: Local = self.local_class()
        return made
"""


def test_a_variable_bound_to_a_checked_files_class_is_its_type(tmp_path: Path) -> None:
    """`type[Class]`: not a function's name, nor one a class above or under it binds to another."""
    files: dict[str, str] = {
        "pkg/__init__.py": "",
        "pkg/forms.py": FORMS,
        "pkg/views.py": VIEWS,
        "pkg/sub.py": SUB,
    }
    name: str
    source: str
    for name, source in files.items():
        (tmp_path / "pkg").mkdir(exist_ok=True)
        _ = (tmp_path / name).write_text(source, encoding="utf-8")
    views: Path = tmp_path / "pkg" / "views.py"
    assert classvars.named(ast.parse(VIEWS)) == {
        "View": {
            "form_class": "PasswordForm",
            "local_class": "Local",
            "overridden": "PasswordForm",
            "maker": "make",
        },
    }
    catalog: project.Index = plain.settled(project.index(sorted(tmp_path.rglob("*.py"))))
    assert plain.members(catalog, views) == {
        "View": {"form_class": "type[PasswordForm]", "local_class": "type[Local]"},
    }
    assert not plain.members(catalog, tmp_path / "missing.py")
    arguments: list[str] = ["--fix", "--unsafe-fixes", "--all-scopes", "-q", "--jobs=1", str(tmp_path)]
    for _ in range(2):  # the second changes nothing
        _ = cli.main(arguments)
        assert views.read_text(encoding="utf-8") == FIXED_VIEWS
