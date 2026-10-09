# SPDX-License-Identifier: MIT
"""`--fix` for calls to decorated functions: a declared return under a decorator that gives it back."""

import ast
import textwrap
from pathlib import Path
from typing import Final, TypeAlias

import pytest

from constricter import Offence, check_source
from constricter.fix.core.known import Guarded, Outside
from constricter.fix.index import decorated, project
from constricter.rules import decorators
from constricter.rules.decorators import Held, Pass

_Fixes: TypeAlias = dict[str, str | None]
_LOCAL: Final = """
import abc
import functools
import functools as ft
import typing_extensions as te
import warnings
from collections.abc import Callable
from functools import cache, lru_cache as memo, partial
from typing import ParamSpec, TypeVar, final

import other

F = TypeVar("F")
P = ParamSpec("P")
T = TypeVar("T")


def same(func: F) -> F:
    return func


def wrapping(func: Callable[P, T]) -> Callable[P, T]:
    return func


def named(name: str) -> Callable[[F], F]:
    return same


def counted(func: Callable[..., int]) -> Callable[..., int]:
    return func


def other_kind(func: other.F) -> other.F:
    return func


def two(func: F, flag: bool) -> F:
    return func


def changing(func: F) -> int:
    return 1


@cache
def a() -> int:
    return 1


@functools.lru_cache(maxsize=4)
def b() -> str:
    return ""


@memo
@final
def c() -> bytes:
    return b""


@ft.wraps(a)
@te.deprecated("old")
@warnings.deprecated("old")
def d() -> float:
    return 1.5


@same
@wrapping
@named("n")
def e() -> list[int]:
    return []


@cache()
def not_called() -> int:
    return 1


@ft.wraps
def not_bare() -> int:
    return 1


@partial
def unknown() -> int:
    return 1


@counted
def not_a_type_variable() -> bool:
    return True


@other_kind
def not_a_name() -> int:
    return 1


@two
def not_one_parameter() -> int:
    return 1


@changing
def not_given_back() -> int:
    return 1


@named
def factory_bare() -> int:
    return 1


@same()
def bare_called() -> int:
    return 1


@other.registry["x"]
def not_spelled() -> int:
    return 1


class Shape(abc.ABC):
    @abc.abstractmethod
    def area(self) -> float:
        raise NotImplementedError

    @same
    def sides(self) -> int:
        return 4

    @changing
    def changed(self) -> int:
        return 1


def use(shape: Shape) -> None:
    ra = a()
    rb = b()
    rc = c()
    rd = d()
    re = e()
    area = shape.area()
    sides = shape.sides()
    na = not_called()
    nb = not_bare()
    nc = unknown()
    nd = not_a_type_variable()
    ne = not_a_name()
    nf = not_one_parameter()
    ng = not_given_back()
    nh = factory_bare()
    ni = bare_called()
    nj = not_spelled()
    nk = shape.changed()
"""
_TYPING: Final = """
from collections.abc import Callable
from typing import Any, TypeVar

F = TypeVar("F", bound=Callable[..., Any])


class NotOne:
    pass
"""
_DECORATORS: Final = """
from collections.abc import Callable

from pkg._typing import F, NotOne


def set_module(module: str) -> Callable[[F], F]:
    def decorator(func: F) -> F:
        return func

    return decorator


def kept(func: F) -> F:
    return func


def swapped(func: NotOne) -> NotOne:
    return func
"""
_API: Final = """
import functools

import pkg._decorators as deco
from pkg._decorators import set_module, swapped
from pkg._typing import F


class Index:
    pass


def mine(func: F) -> F:
    return func


def boxed(func: int) -> int:
    return func


@set_module("pkg")
@functools.cache
def ranged(count: int) -> Index:
    return Index()


@deco.kept
@mine
def kept() -> float:
    return 1.5


@swapped
def other() -> str:
    return ""


@boxed
def number() -> str:
    return ""


@set_module("pkg")
def echo(func: F) -> F:
    return func


def f() -> None:
    a = ranged(1)
    b = kept()
    c = other()
    d = echo(f)
"""
_MAIN: Final = """
from pkg.api import kept, other, ranged


def g() -> None:
    a = ranged(1)
    b = kept()
    c = other()
"""


def test_a_decorator_that_gives_the_function_back_keeps_its_return() -> None:
    """The standard library's, and the module's own by their signatures: nothing else."""
    fixes: _Fixes = {o.name: o.fix for o in check_source(textwrap.dedent(_LOCAL))}
    assert fixes == {
        "ra": "int",
        "rb": "str",
        "rc": "bytes",
        "rd": "float",
        "re": "list[int]",
        "area": "float",
        "sides": "int",
        **dict.fromkeys(("na", "nb", "nc", "nd", "ne", "nf", "ng", "nh", "ni", "nj", "nk")),
    }


def test_a_modules_own_decorators_are_read_by_their_signatures() -> None:
    """One parameter given back, or a factory of such a decorator; with the names to be type variables."""
    assert decorators.passes(ast.parse(textwrap.dedent(_LOCAL))) == {
        "same": Pass(called=False, type_vars=frozenset({"F"})),
        "wrapping": Pass(called=False, type_vars=frozenset({"P", "T"})),
        "named": Pass(called=True, type_vars=frozenset({"F"})),
        "counted": Pass(called=False, type_vars=frozenset({"int"})),
    }
    twice: str = "def d(f: F) -> F: ...\ndef d(f: F) -> F: ...\nasync def e(f: F) -> F: ...\n"
    assert decorators.passes(ast.parse(twice + "@x\ndef g(f: F) -> F: ...\n")) == {}


def _write(path: Path, source: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    _ = path.write_text(textwrap.dedent(source), encoding="utf-8", newline="\n")
    return path


@pytest.fixture(name="catalog")
def _catalog(tmp_path: Path) -> project.Index:
    """Index a package whose functions are decorated by another module's decorators.

    Returns:
      The index, with what they vouch for.

    """
    _ = _write(tmp_path / "pkg" / "__init__.py", "")
    _ = _write(tmp_path / "pkg" / "_typing.py", _TYPING)
    _ = _write(tmp_path / "pkg" / "_decorators.py", _DECORATORS)
    _ = _write(tmp_path / "pkg" / "api.py", _API)
    _ = _write(tmp_path / "main.py", _MAIN)
    return decorated.passed(project.index(sorted(tmp_path.rglob("*.py"))))


def test_another_modules_decorator_is_vouched_for_by_the_index(
    catalog: project.Index,
    tmp_path: Path,
) -> None:
    """Imported under any spelling, with its type variable found to be one; the module's own too."""
    assert catalog.modules["pkg.api"].vouched == {"ranged", "kept", "echo"}
    api: Path = tmp_path / "pkg" / "api.py"
    main: Path = tmp_path / "main.py"
    assert decorated.own(catalog, api) == {"ranged": "Index", "kept": "float", "echo": "F"}
    assert decorated.own(catalog, main) == {}
    assert decorated.own(catalog, tmp_path / "missing.py") == {}
    assert decorated.own(catalog, tmp_path / "notebook.ipynb") == {}
    inside: list[Offence] = check_source(
        api.read_text(encoding="utf-8"),
        outside=Outside(calls=decorated.own(catalog, api), type_vars=project.type_vars(catalog, api)),
    )
    # `echo` returns a type variable the module imports: its calls depend on their arguments.
    assert {o.name: o.fix for o in inside} == {"a": "Index", "b": "float", "c": None, "d": None}
    guarded: dict[str, Guarded] = {}
    outside: list[Offence] = check_source(
        main.read_text(encoding="utf-8"),
        outside=Outside(calls=project.calls(catalog, main, guarded), guarded=guarded),
    )
    assert {o.name: o.fix for o in outside} == {"a": "Index", "b": "float", "c": None}


def test_an_index_with_nothing_held_is_left_as_it_is(tmp_path: Path) -> None:
    """No module is replaced when no decorator is vouched for."""
    _ = _write(tmp_path / "plain.py", "import other\n\n\n@other.deco\ndef f() -> int:\n    return 1\n")
    plain: project.Index = project.index(sorted(tmp_path.rglob("*.py")))
    assert plain.modules["plain"].held == {"f": Held("int", ("other.deco",))}
    assert decorated.passed(plain) is plain
