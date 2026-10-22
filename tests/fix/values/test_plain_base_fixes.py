"""`--fix` for a plain class's variables: the bases a plain class may have.

A builtin exception or value class, a generic or abstract class, and those `fix-plain-bases` lists,
here or in a checked file: a class under one is plain, unless it hides what a base annotates.
"""

import ast
import textwrap
from pathlib import Path
from typing import Final, TypeAlias

import pytest

from constricter import Checks, Offence, check_source
from constricter.cli import command as cli
from constricter.fix.index import plain, project
from constricter.fix.values import classvars

# Each offence's fix and whether it's a guess.
_Fixed: TypeAlias = dict[str, tuple[str | None, bool]]
_ALL: Final = Checks(all_scopes=True)
BUILTINS: Final = """
class Mixin:
    code: str
    limit: int | None = None

    def __init__(self) -> None:
        self.label: str | None = None


class Failed(Mixin, ValueError):
    code = "failed"
    limit = 3
    label = "x"
    retries = 2
    args = ("a",)


class Missing(Failed):
    kind = "missing"
    with_traceback = 1


class Io(OSError):
    errno = 5
    slow = True


class Text(str):
    strip = "both"
    lowered = True


class Meta(type):
    registry = 1
"""
FAILURES: Final = """
class Failure(ValueError):
    status: int | None = None
"""
FAILING: Final = """
from pkg.failures import Failure


class Gone(Failure):
    status = 404
    reason = "gone"


class Lost(Failure):
    args = ("lost",)


class Late(Failure):
    seconds = 30
"""


def _fixed(source: str, checks: Checks = _ALL) -> _Fixed:
    found: list[Offence] = check_source(textwrap.dedent(source), checks=checks)
    return {o.name: (o.fix, o.unsafe) for o in found}


def test_a_class_under_a_builtin_exception_or_value_class_is_plain() -> None:
    """Its variables are its own: but one the builtin has itself, or a class above annotates otherwise.

    A type checker holds a variable to what its base declares: `limit: int | None` above makes
    `limit: int` an incompatible override, as `errno` under `OSError` is.
    """
    fixed: _Fixed = _fixed(BUILTINS)
    assert {name: fix for name, fix in fixed.items() if fix[0]} == {
        "code": ("str", True),  # as the mixin declares it
        "retries": ("int", True),
        "kind": ("str", True),
        "slow": ("bool", True),
        "lowered": ("bool", True),
    }
    # Annotated as another type above (`limit`, and `label` by its `self.label: ...`), a builtin
    # base's own (`args`, `with_traceback` through `Failed`, `errno`, `strip`), and a metaclass's.
    assert {name for name, fix in fixed.items() if not fix[0]} == {
        "limit",
        "label",
        "args",
        "with_traceback",
        "errno",
        "strip",
        "registry",
    }
    tree: ast.Module = ast.parse(textwrap.dedent(BUILTINS))
    assert classvars.plain(tree, {}) == {"Mixin", "Failed", "Missing", "Io", "Text"}
    assert classvars.allowed("KeyError")
    assert not classvars.allowed("type")


def test_a_builtin_the_module_binds_itself_is_no_plain_base() -> None:
    """`ValueError = ...` somewhere in the module: the base may be anything."""
    source: str = "def f(ValueError): ...\n\n\nclass Odd(ValueError):\n    odd = 1\n"
    assert _fixed(source) == {"odd": (None, False)}
    assert classvars.plain(ast.parse(source), {}) == frozenset()


def test_another_files_base_holds_a_variable_to_its_type(tmp_path: Path) -> None:
    """The index sees what a file can't: its class's bases in other files, and what they declare.

    A class hiding what a base there annotates as another type, or a builtin above that base has
    itself, isn't plain; one that doesn't is.
    """
    files: dict[str, str] = {"pkg/__init__.py": "", "pkg/failures.py": FAILURES, "failing.py": FAILING}
    paths: list[Path] = []
    name: str
    source: str
    for name, source in files.items():
        path: Path = tmp_path / name
        path.parent.mkdir(parents=True, exist_ok=True)
        _ = path.write_text(source, encoding="utf-8")
        paths.append(path)
    catalog: project.Index = plain.settled(project.index(paths))
    assert catalog.modules["pkg.failures"].plain == {"Failure"}
    assert catalog.modules["failing"].members == {
        "Gone": {"status": "int", "reason": "str"},
        "Lost": {"args": "tuple[str]"},
        "Late": {"seconds": "int"},
    }
    assert catalog.modules["failing"].plain == {"Late"}


FRAMEWORK: Final = """
import enum

from django.db import models
from django.views.generic import ListView
from rest import Serializer


class Status(models.TextChoices):
    DRAFT = "draft"


class Article(models.Model):
    per_page = 20
    title = models.CharField(max_length=10)


class Articles(ListView):
    paginate_by = 10


class Colour(enum.Enum):
    RED = 1


class Row(Serializer):
    many = True
"""


def test_a_listed_base_is_one_a_plain_class_may_have() -> None:
    """Django's classes read no annotation in a class body, but its `Choices`, which are enums.

    Other bases are listed by `plain_bases`: a class, or a package; `!` leaves one out.
    """
    assert _fixed(FRAMEWORK) == {
        "DRAFT": (None, False),
        "per_page": ("int", True),
        "title": (None, False),
        "paginate_by": ("int", True),
        "many": (None, False),
    }
    bases: tuple[str, ...] = ("rest", "django.db", "!django.db.models.TextChoices")
    found: _Fixed = _fixed(FRAMEWORK, Checks(all_scopes=True, plain_bases=bases))
    assert {name for name, fix in found.items() if fix[0]} == {"per_page", "many"}
    assert classvars.listed("pkg.Base", ["pkg.Base"])
    assert not classvars.listed("pkg.Based", ["pkg.Base"])
    assert not classvars.listed("pkg.Base", [])


WEB: Final = """
def registered(cls):
    return cls


@registered
class View:
    limit: int | None = None


class Mixin:
    shared = 1


@registered
class Mixed(Mixin):
    pass
"""
PAGES: Final = """
from web.base import View


class Page(View):
    title = "page"


class Short(View):
    limit = 3
"""


def test_a_listed_base_a_checked_file_defines_is_one_too(tmp_path: Path) -> None:
    """A framework's own files, checked: a class under its decorated base is plain where it's listed.

    What the base annotates still holds its subclasses' variables, and a listed class's mixin is plain.
    """
    files: dict[str, str] = {"web/__init__.py": "", "web/base.py": WEB, "pages.py": PAGES}
    paths: list[Path] = []
    name: str
    source: str
    for name, source in files.items():
        path: Path = tmp_path / name
        path.parent.mkdir(parents=True, exist_ok=True)
        _ = path.write_text(source, encoding="utf-8")
        paths.append(path)
    catalog: project.Index = project.index(paths)
    unlisted: project.Index = plain.settled(catalog)
    assert unlisted.modules["pages"].plain == frozenset()
    assert unlisted.modules["web.base"].plain == frozenset()
    listed: project.Index = plain.settled(catalog, ["web"])
    assert listed.modules["pages"].plain == {"Page"}
    assert listed.modules["web.base"].plain == {"Mixin"}


def test_the_command_takes_listed_bases_from_a_flag_and_pyproject(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """`--fix-plain-bases`, or `[tool.constricter]`'s `fix-plain-bases`, adds to the built-in ones."""
    monkeypatch.chdir(tmp_path)
    path: Path = tmp_path / "rows.py"
    source: str = "from rest import Serializer\n\n\nclass Row(Serializer):\n    many = True\n"
    _ = path.write_text(source, encoding="utf-8")
    arguments: list[str] = ["--fix", "--unsafe-fixes", "--all-scopes", "-q", "rows.py"]
    assert cli.main(arguments) == cli.EXIT_FOUND
    assert path.read_text(encoding="utf-8") == source
    fixed: str = source.replace("many = True", "many: bool = True")
    assert cli.main([*arguments, "--fix-plain-bases=rest.Serializer, !rest.Enum"]) == cli.EXIT_CLEAN
    assert path.read_text(encoding="utf-8") == fixed
    _ = path.write_text(source, encoding="utf-8")
    _ = (tmp_path / "pyproject.toml").write_text(
        '[tool.constricter]\nfix-plain-bases = ["rest"]\n',
        encoding="utf-8",
    )
    assert cli.main(arguments) == cli.EXIT_CLEAN
    assert path.read_text(encoding="utf-8") == fixed
    _ = capsys.readouterr()


GENERICS: Final = """
import abc
import typing
from abc import ABC
from typing import Generic, NamedTuple, Protocol, TypeVar

T = TypeVar("T")


class Box(Generic[T]):
    limit = 3


class Wide(Box[int]):
    width = 2.5


class Names(list[str]):
    sep = ","


class Shape(ABC):
    sides = 0


class Square(Shape, typing.Generic[T], abc.ABC):
    sides = 4


class Speaks(Protocol[T]):
    volume = 1


class Row(NamedTuple):
    size: int = 0


class Made(make()[T]):
    made = 1
"""


def test_a_generic_or_abstract_class_is_plain() -> None:
    """`Generic[T]`, `abc.ABC` and a plain base's subscript make no field of an annotation; a protocol may."""
    tree: ast.Module = ast.parse(textwrap.dedent(GENERICS))
    assert classvars.plain(tree, classvars.imported(tree)) == {"Box", "Wide", "Names", "Shape", "Square"}
    assert _fixed(GENERICS) == {
        "limit": ("int", True),
        "width": ("float", True),
        "sep": ("str", True),
        "sides": ("int", True),
        "volume": (None, False),
        "made": (None, False),
    }


def test_a_base_passed_over_is_one_where_a_checked_file_defines_it(tmp_path: Path) -> None:
    """The standard library, checked: a class under its `abc.ABC` (given a metaclass) is still plain."""
    files: dict[str, str] = {
        "abc.py": "class ABC(metaclass=type):\n    pass\n",
        "shapes.py": "from abc import ABC\n\n\nclass Shape(ABC):\n    sides = 0\n",
    }
    paths: list[Path] = []
    name: str
    source: str
    for name, source in files.items():
        path: Path = tmp_path / name
        _ = path.write_text(source, encoding="utf-8")
        paths.append(path)
    settled: project.Index = plain.settled(project.index(paths))
    assert settled.modules["shapes"].plain == {"Shape"}
    assert settled.modules["abc"].plain == frozenset()
