# SPDX-License-Identifier: MIT
"""`--fix` for installed packages' calls whose overloads their arguments decide (`fix.stubbed`)."""

import sys
import textwrap
from pathlib import Path
from typing import TYPE_CHECKING, Final

import pytest

from constricter.cli import command as cli
from constricter.fix import installed, project, stubbed

if TYPE_CHECKING:
    from constricter.fix.signatures import ReadSignature

# A typed package whose public module re-exports a private one's functions and classes, as numpy
# does; and an untyped one.
SITE: Final = {
    "shapes/py.typed": "",
    "shapes/__init__.pyi": """
        from shapes._core import (
            Array as Array,
            Float as Float,
            Scalar as Scalar,
            make as make,
            pick as pick,
            mode as mode,
            size as size,
            either as either,
            loose as loose,
            first as first,
            wrap as wrap,
            listed as listed,
            nothing as nothing,
            odd as odd,
            label as label,
            Double as Double,
            Floats as Floats,
            Numbers as Numbers,
        )
        from shapes import _core
        from shapes.typing import Pair as Pair
        import shapes.typing as typing
    """,
    "shapes/typing.pyi": """
        from typing import TypeAlias, TypeVar
        _T = TypeVar("_T")
        Pair: TypeAlias = tuple[_T, _T]
        __all__ = ["Pair"]
    """,
    "shapes/_core.pyi": """
        import typing
        from typing import (
            Annotated, Any, Callable, Generic, Literal, Optional, Protocol, SupportsIndex, TypeAlias,
            TypeVar, Union, overload,
        )
        from typing_extensions import LiteralString
        from _typeshed import Incomplete
        from shapes.typing import Pair
        from shapes.typing import _T as _U

        _S = TypeVar("_S", bound="Scalar")
        _T = TypeVar("_T")
        _C = TypeVar("_C", int, str)
        _Arr: TypeAlias = Array[_T]
        _Private = tuple[_T, int]
        _B = TypeVar("_B", bound=Unknown)
        _Loop: TypeAlias = "_Loop | int"
        Scalars: TypeAlias = int | float
        _Box: TypeAlias = type[_T] | None
        Double: TypeAlias = Float
        Floats: TypeAlias = Array[Float]
        Numbers = int | float

        class Scalar: ...
        class Float(Scalar, float): ...
        class Array(Generic[_S]): ...
        class _Hidden: ...
        class Bound(Array[Float]): ...
        class Local(Array[_T]): ...
        class Imported(Array[_U]): ...
        class Opaque(Array[Missing]): ...

        class Named(Protocol):
            @property
            def name(self) -> str: ...

        class Lengthy(Protocol):
            def __len__(self) -> int: ...

        @overload
        def make(n: SupportsIndex, kind: None = None) -> _Arr[Float]: ...
        @overload
        def make(n: SupportsIndex, kind: _Box[_S]) -> Array[_S]: ...
        @overload
        def make(n: SupportsIndex, kind: Named | Any = ...) -> Incomplete: ...

        def pick(x: _C) -> _C: ...

        @overload
        def mode(m: Literal["r"]) -> int: ...
        @overload
        def mode(m: Literal["w", 1]) -> "str": ...
        @overload
        def mode(m: str) -> bytes: ...

        @overload
        def size(x: Lengthy, y: None = None) -> int: ...
        @overload
        def size(x: object, y: Optional[int] = None) -> str: ...

        def either(x: Union[_T, None], y: Annotated[_T, "note"]) -> Pair[_T]: ...
        def loose(x: _T) -> _Private[_T]: ...

        @overload
        def first(x: typing.SupportsIndex) -> tuple[int, ...]: ...
        @overload
        def first(x: LiteralString) -> None: ...
        @overload
        def first(x: Callable[..., int]) -> _Hidden: ...

        def wrap(x: _T, extra=...) -> list[_T] | None: ...
        def listed(x: "list[_T]") -> _T: ...
        def nothing(x: Unknown) -> Literal[1] | _T: ...

        @overload
        def odd(x: _Loop, y: Scalars = 0, k: type[Any] = ...) -> _Loop: ...
        @overload
        def odd(x: "1 + 2", y: Unknown = 0) -> Array["1 + 2"]: ...
        @overload
        def odd(x: f()[int], y: typing = 0) -> Callable[[int], int]: ...
        @overload
        def odd(x: "int[", y: Literal[MISSING] = 0) -> Scalar.attr: ...
        @overload
        def odd(x: f().x, y: Unknown.x = 0, z: _B = ...) -> _B: ...

        @overload
        def label(x: Literal["a"] | str) -> int: ...
        @overload
        def label(x: bytes) -> str: ...
    """,
    "loose/__init__.pyi": "from typing import TypeVar\n_T = TypeVar('_T')\ndef same(x: _T) -> _T: ...\n",
}
MAIN: Final = """
import shapes
from shapes import make, pick, mode, size, either, loose, first, wrap, listed, nothing, odd, label
import loose as untyped


def run(n: int, s: str) -> None:
    a = make(n)
    b = shapes.make(3, kind=shapes.Float)
    c = make(n, shapes.Scalar)
    d = make(n, s)
    e = pick(1)
    f = mode("r")
    g = mode("w")
    h = mode(s)
    i = size(s)
    j = size(n)
    k = either(n, n)
    m = loose(n)
    o = first(n)
    p = first("x")
    q = wrap(s)
    r = listed([1])
    t = nothing(1)
    u = untyped.same(1)
    v = shapes.nowhere(1)
    w = odd(1, 2, int, z=3)
    x = make(n, shapes.Double)
    y = make(n, shapes.Floats)
    z = make(n, shapes.Numbers)
    aa = make(n, shapes.make)
    bb = label(s)
    print(a, b, c, d, e, f, g, h, i, j, k, m, o, p, q, r, t, u, v, w, x, y, z, aa, bb)
"""
FIXED: Final = (
    "    a: shapes.Array[shapes.Float] = make(n)\n",
    "    b: shapes.Array[shapes.Float] = shapes.make(3, kind=shapes.Float)\n",
    "    c: shapes.Array[shapes.Scalar] = make(n, shapes.Scalar)\n",
    "    d = make(n, s)\n",  # `Named | Any`: `Incomplete`, unwritable
    "    e = pick(1)\n",  # constrained: `int` or `str`, never bound to the argument's own type
    '    f: int = mode("r")\n',
    '    g: str = mode("w")\n',
    "    h = mode(s)\n",  # a `str` may be one of the literals: every overload is open
    "    i: int = size(s)\n",  # a `str` has `__len__`
    "    j: str = size(n)\n",
    "    k: Pair[int] = either(n, n)\n",  # a public alias, imported from its public module
    "from shapes.typing import Pair\n",
    "    m: tuple[int, int] = loose(n)\n",  # a private alias, written out
    "    o: tuple[int, ...] = first(n)\n",
    '    p = first("x")\n',  # `None`: not worth annotating
    "    q: list[str] | None = wrap(s)\n",
    "    r = listed([1])\n",  # a container's element: not read
    "    t = nothing(1)\n",
    "    u = untyped.same(1)\n",  # untyped: no `py.typed`
    "    v = shapes.nowhere(1)\n",
    "    w = odd(1, 2, int, z=3)\n",
    "    x: shapes.Array[shapes.Double] = make(n, shapes.Double)\n",  # an alias of a class, as written
    "    y: shapes.Array[shapes.Floats] = make(n, shapes.Floats)\n",
    "    z = make(n, shapes.Numbers)\n",  # an alias of a union: not a class
    "    aa = make(n, shapes.make)\n",  # a function
    "    bb: int = label(s)\n",
)

MODERN_FIXED: Final = "    a: modern.Array[modern.Float] = modern.empty(n, modern.Float)\n"


def _site(root: Path, files: dict[str, str]) -> Path:
    found: Path = root / "site"
    name: str
    text: str
    for name, text in files.items():
        path: Path = found / name
        path.parent.mkdir(parents=True, exist_ok=True)
        _ = path.write_text(textwrap.dedent(text), encoding="utf-8", newline="\n")
    return found


@pytest.fixture(name="site")
def installed_site(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Install `SITE` on the search path, with a cache of its own.

    Returns:
      Its directory.

    """
    found: Path = _site(tmp_path, SITE)
    monkeypatch.setattr(sys, "path", [str(found), *sys.path])
    monkeypatch.setenv("XDG_CACHE_HOME", str(tmp_path / "cache"))
    return found


def test_calls_are_typed_by_the_overload_their_arguments_match(tmp_path: Path, site: Path) -> None:
    """Each call typed as a type checker would pick among the overloads, or left alone."""
    assert site.is_dir()
    main: Path = tmp_path / "main.py"
    _ = main.write_text(textwrap.dedent(MAIN), encoding="utf-8")
    assert cli.main(["--fix", "-q", str(main)]) == cli.EXIT_FOUND
    missing: list[str] = [line for line in FIXED if line not in main.read_text(encoding="utf-8")]
    assert not missing, main.read_text(encoding="utf-8")


def test_signatures_are_read_once_per_index(tmp_path: Path, site: Path) -> None:
    """A second file calling the same function reads it from the memo; a file not indexed gets none."""
    main: Path = tmp_path / "main.py"
    _ = main.write_text("import shapes\n\nshapes.make(1)\nshapes.make.x()\n", encoding="utf-8")
    catalog: project.Index = installed.with_installed(project.index([main]), installed.search_path())
    first: dict[str, tuple[ReadSignature, ...]] = stubbed.overloaded(catalog, main)
    assert stubbed.overloaded(catalog, main) == first
    assert list(first) == ["shapes.make"]
    assert not stubbed.overloaded(catalog, tmp_path / "other.py")
    assert stubbed.classes(catalog, tmp_path / "other.py") == frozenset()
    # A class generic only through a base is generic where that base passes a type variable.
    generics: frozenset[str] = catalog.modules["shapes._core"].generics
    assert {"Array", "Local", "Imported"} <= generics
    assert generics.isdisjoint({"Bound", "Opaque"})
    assert site.is_dir()


@pytest.mark.skipif(sys.version_info < (3, 12), reason="PEP 695 syntax")
def test_type_parameters_of_their_own(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Python 3.12+'s `def f[T: ...]` and `type X[T] = ...`, as numpy 2.5's stubs write them."""
    modern: Path = _site(
        tmp_path,
        {
            "modern/py.typed": "",
            "modern/__init__.pyi": """
                from typing import SupportsIndex, overload
                class Scalar: ...
                class Float(Scalar): ...
                class Array[T: Scalar]: ...
                type _Array1D[T: Scalar] = Array[T]
                @overload
                def empty(n: SupportsIndex, dtype: None = None) -> _Array1D[Float]: ...
                @overload
                def empty[T: Scalar](n: SupportsIndex, dtype: type[T]) -> _Array1D[T]: ...
            """,
        },
    )
    monkeypatch.setattr(sys, "path", [str(modern), *sys.path])
    monkeypatch.setenv("XDG_CACHE_HOME", str(tmp_path / "cache"))
    main: Path = tmp_path / "main.py"
    _ = main.write_text(
        "import modern\n\n\ndef f(n: int) -> None:\n    a = modern.empty(n, modern.Float)\n",
        encoding="utf-8",
    )
    assert cli.main(["--fix", "-q", str(main)]) == cli.EXIT_CLEAN
    assert MODERN_FIXED in main.read_text(encoding="utf-8")
