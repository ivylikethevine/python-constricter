# SPDX-License-Identifier: MIT
"""`--fix` for a plain class's variables, typed by their literal values (a guess: `member`)."""

import ast
import textwrap
from pathlib import Path
from typing import Final, TypeAlias

from constricter import Checks, FixPolicy, Offence, check_source
from constricter.cli import command as cli
from constricter.fix import classvars, project, stdlib

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
        self.stored = 1

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
        "maxDiff": ("int", True),  # under a test case
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
    catalog: project.Index = project.with_plain(project.index(paths))
    assert catalog.modules["pkg.bases"].plain == {"Base", "Wide", "Case"}  # `Mixin` is a model's
    assert catalog.modules["pkg.models"].plain == frozenset()
    assert catalog.modules["using"].plain == {"Child", "Tests", "Other"}
    assert project.plain_classes(catalog, paths[-1]) == frozenset({"Child", "Tests", "Other"})
    assert project.plain_classes(catalog, tmp_path / "missing.py") is None
    assert project.imported(catalog, paths[-1]).members == {
        "Base": {"size": "int"},
        "Case": {"retries": "int"},
        "bases.Base": {"size": "int"},
        "bases.Wide": {"width": "int"},
        "bases.Case": {"retries": "int"},
    }
    assert project.with_plain(project.Index({}, [])) == project.Index({}, [])


def test_one_run_fixes_the_class_and_what_reads_it(tmp_path: Path) -> None:
    """The class's file and the files reading its variables, in one pass: a second changes nothing."""
    paths: list[Path] = _package(tmp_path)
    arguments: list[str] = ["--fix", "--unsafe-fixes", "--all-scopes", "-q", "--jobs=1", str(tmp_path)]
    for _ in range(2):
        assert cli.main(arguments) == cli.EXIT_FOUND
        assert paths[-1].read_text(encoding="utf-8") == USED
        assert paths[1].read_text(encoding="utf-8") == FIXED_BASES
