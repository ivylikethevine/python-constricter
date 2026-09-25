# SPDX-License-Identifier: MIT
"""What an installed package's stub declares for its overloads: `constricter.fix.declared`."""

import ast
import sys
import textwrap
from typing import Final

import pytest

from constricter.fix.declared import Alias, Declarations, Protocol, Signature, Variable, declarations

STUB: Final = """
from typing import Protocol, TypeAlias, TypeVar, overload
import typing as t
from m import a as a, b
from n import *

_T = TypeVar("_T")
_B = TypeVar("_B", bound=int)
_C = t.TypeVar("_C", int, str)
_P = ParamSpec("_P")
Pair: TypeAlias = tuple[_T, _T]
Either = int | str
Named = t.Any
Dotted = t.List
Called = make()
value = 1
annotated: int

@overload
def f(x: int) -> int: ...
@overload
def f(x: str, /, *args: int, y: bytes = ..., **kwargs: str) -> str: ...
def f(x): ...
@overload
def f(x: float) -> float: ...

def plain(x: int) -> int: ...
def generic(x: _T) -> list[_T]: ...
@staticmethod
def decorated(x: _T) -> _T: ...
def untyped(x): ...
def again(x: _T) -> _T: ...
def again(x: int) -> int: ...

class Sized(Protocol):
    __slots__ = ()
    def __len__(self) -> int: ...
    async def wait(self) -> None: ...

class Named(t.Protocol[_T]):
    name: str

class Holder(Protocol):
    @property
    def value(self) -> int: ...

class Box(list[_T]): ...
class Fixed(list[int]): ...
class Plain: ...
class Own(Generic[_T], list[_T]): ...
"""


def _read(source: str) -> Declarations:
    return declarations(ast.parse(textwrap.dedent(source)))


def test_overloads_are_read_in_order_and_the_implementation_is_left_out() -> None:
    """Each `@overload` as written; a plain def after them isn't one callers see."""
    read: Declarations = _read(STUB)
    assert read.signatures["f"] == (
        Signature((("x", "e", False, "int"),), "int"),
        Signature(
            (
                ("x", "p", False, "str"),
                ("args", "a", True, "int"),
                ("y", "k", True, "bytes"),
                ("kwargs", "w", True, "str"),
            ),
            "str",
        ),
        Signature((("x", "e", False, "float"),), "float"),
    )


def test_only_functions_a_type_variable_or_overload_decides_are_kept() -> None:
    """A return naming a module type variable; not a plain, decorated or redefined one."""
    read: Declarations = _read(STUB)
    assert read.signatures["generic"] == (Signature((("x", "e", False, "_T"),), "list[_T]"),)
    assert {"plain", "decorated", "untyped", "again"}.isdisjoint(read.signatures)  # `again`: its last def


def test_aliases_and_type_variables() -> None:
    """Aliases by `TypeAlias` or a type-shaped value; type variables' bounds and constraints."""
    read: Declarations = _read(STUB)
    assert read.aliases == {
        "Pair": Alias("tuple[_T, _T]"),
        "Either": Alias("int | str"),
        "Named": Alias("t.Any"),
        "Dotted": Alias("t.List"),
    }
    assert read.variables == {
        "_T": Variable(None),
        "_B": Variable("int"),
        "_C": Variable("int | str", constrained=True),
        "_P": Variable("*"),
    }


def test_protocols_and_bases() -> None:
    """A protocol's members (machinery left out), and whether one is an attribute or property."""
    read: Declarations = _read(STUB)
    assert read.protocols == {
        "Sized": Protocol(frozenset({"__len__", "wait"}), properties=False),
        "Named": Protocol(frozenset({"name"}), properties=True),
        "Holder": Protocol(frozenset({"value"}), properties=True),
    }
    assert read.bases == {"Box": frozenset({"_T"}), "Fixed": frozenset({"int"})}


def test_exports() -> None:
    """`__all__` where set; else public definitions and redundant aliases; open after a `*` import."""
    assert _read(STUB).exports is None
    assert _read("__all__ = ['a']\n__all__ += ('b', 1)\nc = 1\n").exports == frozenset({"a", "b"})
    source: str = (
        "from m import a as a, b\nimport c as c\nclass D: ...\n"
        "def e(): ...\n_f = 1\ng: int\nif h:\n    i = 1\n"
    )
    assert _read(source).exports == frozenset({"a", "c", "D", "e", "g"})


@pytest.mark.skipif(sys.version_info < (3, 12), reason="PEP 695 syntax")
def test_type_parameters() -> None:
    """Python 3.12+'s own type parameters, on functions and `type` aliases, and their exports."""
    source: str = """
    type Pair[T: int, *Ts] = tuple[T, T]
    def f[T: str, **P](x: T) -> T: ...
    class G[T](list[T]): ...
    """
    read: Declarations = _read(source)
    assert read.aliases["Pair"] == Alias("tuple[T, T]", ("T", "Ts"))
    assert read.signatures["f"] == (Signature((("x", "e", False, "T"),), "T", (("T", "str"), ("P", "*"))),)
    assert not read.bases  # `G`'s parameters are its own
    assert read.exports == frozenset({"Pair", "f", "G"})
