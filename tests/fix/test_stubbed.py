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
            shaped as shaped,
            sized as sized,
            Sub as Sub,
            Other as Other,
            Mixed as Mixed,
            Double as Double,
            Floats as Floats,
            Numbers as Numbers,
            Grid as Grid,
            Pairs as Pairs,
            Loose as Loose,
            Maybe as Maybe,
            Nested as Nested,
            Literally as Literally,
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
        from typing_extensions import LiteralString, Self
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
        Grid: TypeAlias = Array[_S]
        Pairs: TypeAlias = Array[tuple[_T, int]]
        Loose: TypeAlias = Array[Any]
        Maybe: TypeAlias = Array[_S] | None
        Nested: TypeAlias = _Arr[_S]
        Literally: TypeAlias = Array[Literal[1]]

        class Scalar: ...
        class Float(Scalar, float): ...
        _Sh = TypeVar("_Sh", bound=tuple[int, ...])
        _B2 = TypeVar("_B2", bound=Scalar)
        _Same = Array

        class Array(Generic[_S]):
            def first(self) -> _S: ...
            def same(self) -> Self: ...
            def plain(self): ...
            @overload
            def cast(self, kind: type[_T]) -> _Same[_T]: ...
            @overload
            def cast(self, kind: None = None) -> Array[_S]: ...
            def only(self: Array[Float]) -> int: ...
            @staticmethod
            def build() -> int: ...
            @overload
            def total(self: Array[Float], axis: None = None) -> Float: ...
            @overload
            def total(self: _Arr[_B2], axis: int) -> Array[_B2]: ...
            def weird(self: Literal[1]) -> int: ...
            def pair(self: Array[tuple[int, ...]]) -> int: ...
            def tail(self: Array[tuple[int, int]]) -> str: ...
            def either(self: Array[Float] | Array[Other]) -> bytes: ...
            def twice(self: Array[tuple[_T, _T]]) -> _T: ...
            def fill(self: Array[_T], value: _T) -> _T: ...
            def anything(self: Array[Any]) -> int: ...
            def three(self: Array[Other] | Array[Scalar] | Array[Float]) -> str: ...
            def head(self: Array[tuple[_T, Any]]) -> _T: ...
            def second(self: Array[tuple[Any, _T]]) -> _T: ...

        class Other(Scalar): ...
        class Mixed(Scalar, Array[_S]): ...
        class Loop(Looped): ...
        class Looped(Loop): ...

        class Sub(Missing, Array[_S], f()): ...
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

        @overload
        def shaped(shape: SupportsIndex) -> int: ...
        @overload
        def shaped(shape: _Sh) -> _Sh: ...

        @overload
        def sized(x: list[int]) -> int: ...
        @overload
        def sized(x: list[str]) -> str: ...
        @overload
        def sized(x: dict[str, int]) -> bytes: ...
        @overload
        def sized(x: tuple) -> float: ...
    """,
    "loose/__init__.pyi": "from typing import TypeVar\n_T = TypeVar('_T')\ndef same(x: _T) -> _T: ...\n",
}
MAIN: Final = """
import shapes
from shapes import make, pick, mode, size, either, loose, first, wrap, listed, nothing, odd, label
from shapes import Array, Grid
import loose as untyped


def run(
    n: int,
    s: str,
    sub: shapes.Sub[shapes.Float],
    bare: Array,
    others: Array[shapes.Other],
    ai: Array[int],
    t1: Array[tuple[int, int]],
    t2: Array[tuple[int]],
    t3: Array[tuple[int, ...]],
    t4: Array[shapes.Float, shapes.Float],
    t5: Array[tuple[int, str]],
    mi: Array[Missing],
    sa: Array[shapes.Sub[shapes.Float]],
    mx: shapes.Mixed[shapes.Float],
    gr: Grid[shapes.Float],
    go: Grid[shapes.Other],
    fl: shapes.Floats,
    pr: shapes.Pairs[str],
    lo: shapes.Loose,
    mb: shapes.Maybe[shapes.Float],
    ne: shapes.Nested[shapes.Float],
    li: shapes.Literally,
) -> None:
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
    cc = shapes.shaped((n, 2))
    dd = shapes.shaped(n)
    ee = shapes.sized([1])
    ff = shapes.sized(["a"])
    gg = shapes.sized((1, 2))
    hh = a.first()
    ii = a.same()
    jj = a.cast(shapes.Scalar)
    kk = a.only()
    mm = sub.first()
    oo = a.plain()
    pp = s.first()
    qq = bare.same()
    print(qq)
    r1 = a.total()
    r2 = c.total()
    r3 = c.total(1)
    r4 = a.weird()
    r5 = t1.pair()
    r6 = t1.tail()
    r7 = t3.tail()
    r8 = t2.tail()
    r9 = t4.total()
    s1 = a.either()
    s2 = c.either()
    s3 = others.either()
    s4 = ai.total(1)
    s5 = sub.total()
    s6 = bare.total()
    s7 = mi.total()
    s8 = sa.total()
    s9 = t5.twice()
    u1 = a.fill(1)
    u2 = a.anything()
    u3 = a.three()
    u4 = mx.first()
    print(u2, u3, u4)
    v1 = gr.total()
    v2 = go.total()
    v3 = gr.first()
    v4 = gr.same()
    v5 = fl.first()
    v6 = pr.head()
    v7 = pr.second()
    v8 = lo.anything()
    v9 = lo.first()
    w1 = mb.first()
    w2 = ne.first()
    w3 = li.first()
    w4 = t3.pair()
    print(v1, v2, v3, v4, v5, v6, v7, v8, v9, w1, w2, w3, w4)
    print(r1, r2, r3, r4, r5, r6, r7, r8, r9, s1, s2, s3, s4, s5, s6, s7, s8, s9, u1)
    print(a, b, c, d, e, f, g, h, i, j, k, m, o, p, q, r, t, u, v, w, x, y, z, aa, bb)
    print(cc, dd, ee, ff, gg, hh, ii, jj, kk, mm, oo, pp)
"""
FIXED: Final = (
    "    a: Array[shapes.Float] = make(n)\n",
    "    b: Array[shapes.Float] = shapes.make(3, kind=shapes.Float)\n",
    "    c: Array[shapes.Scalar] = make(n, shapes.Scalar)\n",
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
    "    x: Array[shapes.Double] = make(n, shapes.Double)\n",  # an alias of a class, as written
    "    y: Array[shapes.Floats] = make(n, shapes.Floats)\n",
    "    z = make(n, shapes.Numbers)\n",  # an alias of a union: not a class
    "    aa = make(n, shapes.make)\n",  # a function
    "    bb: int = label(s)\n",
    "    cc: tuple[int, int] = shapes.shaped((n, 2))\n",  # a bounded type variable, bound to the tuple
    "    dd: int = shapes.shaped(n)\n",
    "    ee: int = shapes.sized([1])\n",  # by the list's elements
    '    ff: str = shapes.sized(["a"])\n',
    "    gg: float = shapes.sized((1, 2))\n",
    "    hh: shapes.Float = a.first()\n",  # the class's type parameter, bound by the receiver's type
    "    ii: Array[shapes.Float] = a.same()\n",  # `Self`: the receiver's type
    "    jj: Array[shapes.Scalar] = a.cast(shapes.Scalar)\n",
    "    kk: int = a.only()\n",  # declares its `self`: its one signature, all the same
    "    mm: shapes.Float = sub.first()\n",  # inherited
    "    oo = a.plain()\n",
    "    pp = s.first()\n",
    "    qq = bare.same()\n",  # `Array` without its argument: not written bare
    "    r1: shapes.Float = a.total()\n",  # `self: Array[Float]`, as the receiver is
    "    r2 = c.total()\n",  # an `Array[Scalar]` is neither overload's `self`, with no axis
    "    r3: Array[shapes.Scalar] = c.total(1)\n",  # `_B2` bound to `Scalar`, within its bound
    "    r4: int = a.weird()\n",  # a `self` it can't match: its one signature, all the same
    "    r5: int = t1.pair()\n",
    "    r6: str = t1.tail()\n",
    "    r7: str = t3.tail()\n",  # any length: its one signature
    "    r8 = t2.tail()\n",  # one element, not two
    "    r9: shapes.Float = t4.total()\n",
    "    s1: bytes = a.either()\n",
    "    s2 = c.either()\n",
    "    s3: bytes = others.either()\n",
    "    s4 = ai.total(1)\n",  # `int` isn't within `_B2`'s bound
    "    s5: shapes.Float = sub.total()\n",  # a subclass: the first may be the one, the second isn't
    "    s6: shapes.Float = bare.total()\n",  # without its argument: the first may be the one
    "    s7: shapes.Float = mi.total()\n",  # an unknown argument: likewise
    "    s8: shapes.Float = sa.total()\n",  # a class whose lineage has a gap: likewise
    "    s9 = t5.twice()\n",  # `_T` bound two ways
    "    u1 = a.fill(1)\n",  # `_T` bound by the receiver and the argument apart
    "    u2: int = a.anything()\n",
    "    u3: str = a.three()\n",
    "    u4: shapes.Float = mx.first()\n",  # its second base's
    # Receivers typed through a public alias of the class: its methods, matched as the class.
    "    v1: shapes.Float = gr.total()\n",
    "    v2 = go.total()\n",
    "    v3: shapes.Float = gr.first()\n",  # the class's parameter, as the alias binds it
    "    v4: Grid[shapes.Float] = gr.same()\n",  # `Self`, as the receiver's written
    "    v5: shapes.Float = fl.first()\n",
    "    v6: str = pr.head()\n",
    "    v7 = pr.second()\n",  # bound to what the alias writes (`int`), which the module doesn't
    "    v8: int = lo.anything()\n",
    "    v9 = lo.first()\n",  # `Any`: unwritable
    "    w1 = mb.first()\n",  # an alias of a union
    "    w2 = ne.first()\n",  # an alias of an alias
    "    w3 = li.first()\n",  # a `Literal` argument
    "    w4: int = t3.pair()\n",  # `tuple[int, ...]` both
)

THROUGH: Final = """
from pkg._typing import st


def f(g: st.Grid[st.Float]) -> None:
    a = g.first()
    print(a)
"""
THROUGH_FIXED: Final = "    a: st.Float = g.first()\n"
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


def test_a_package_imported_through_another_module_is_followed(tmp_path: Path, site: Path) -> None:
    """`from pkg._typing import st`, where `_typing` imports the package: its aliases, as pandas's `npt`."""
    assert site.is_dir()
    package: Path = tmp_path / "pkg"
    package.mkdir()
    _ = (package / "__init__.py").write_text("", encoding="utf-8")
    _ = (package / "_typing.py").write_text("import shapes as st\n", encoding="utf-8")
    main: Path = package / "main.py"
    _ = main.write_text(THROUGH, encoding="utf-8")
    _ = cli.main(["--fix", "-q", str(package)])
    assert THROUGH_FIXED in main.read_text(encoding="utf-8")


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
    assert stubbed.methods(catalog, tmp_path / "other.py") == stubbed.Methods({}, {}, {}, {})
    assert stubbed.methods(catalog, main) == stubbed.methods(catalog, main)  # the second from the memo
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
