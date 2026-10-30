"""`--fix` on the members of a checked file's own generic classes, bound by the receiver's arguments."""

import ast
import sys
import textwrap
from pathlib import Path
from typing import Final

import pytest

from constricter import Checks, check_source
from constricter.cli import command as cli
from constricter.fix.index import project
from constricter.source.declarations import defaulted_type_vars, generic_classes

_CLASS: Final = "C"
_GENERIC: Final = "Generic"
_SOURCE: str = """
from typing import Generic, TypeVar

T = TypeVar("T")
K = TypeVar("K")
V = TypeVar("V")
D = TypeVar("D")

class Row: ...

class Result(Generic[T]):
    items: list[T]

    def __init__(self) -> None:
        self.last: T | None = None

    def first(self) -> T | None:
        return None

    def all(self) -> list[T]:
        return self.items

    def count(self) -> int:
        return 0

    def copied(self) -> "Self":
        return self

    def get(self, default: D) -> T | D:
        return default

    @property
    def head(self) -> T:
        return self.items[0]

class Pairs(Generic[K, V]):
    def pair(self) -> tuple[K, V]: ...

class Keyed(Pairs[str, V]):
    def count(self): ...

class Rows(Result[Row]):
    def m(self) -> None:
        own_first = self.first()
        own_items = self.items

def f(
    rows: Result[Row], bare: Result, maybe: Result[int | None], keyed: Keyed[float], wrong: Pairs[int]
) -> None:
    first = rows.first()
    every = rows.all()
    counted = rows.count()
    items = rows.items
    last = rows.last
    head = rows.head
    copied = rows.copied()
    got = rows.get(1)
    bare_first = bare.first()
    bare_count = bare.count()
    once = maybe.first()
    pair = keyed.pair()
    keyed_count = keyed.count()
    wrong_pair = wrong.pair()
"""


def _found(source: str) -> dict[str, tuple[str | None, bool]]:
    return {o.name: (o.fix, o.unsafe) for o in check_source(textwrap.dedent(source), checks=Checks())}


def test_a_generic_classes_members_are_bound_by_the_receivers_arguments() -> None:
    """A member naming its parameters takes the receiver's arguments; one naming none is as declared.

    Not where the receiver is bare (a checker knows nothing of its parameters), nor given another
    number of arguments, nor for a member naming another type variable. A generic base's members are
    bound by the class's own arguments, unless the class binds the name itself.
    """
    assert _found(_SOURCE) == {
        "own_first": ("Row | None", False),
        "own_items": ("list[Row]", False),
        "first": ("Row | None", False),
        "every": ("list[Row]", False),
        "counted": ("int", False),
        "items": ("list[Row]", False),
        "last": ("Row | None", True),  # a read of a union, as any class's
        "head": ("Row", False),
        "copied": ("Result[Row]", False),  # `Self`, quoted
        "got": (None, False),  # `D`, the method's own
        "bare_first": (None, False),
        "bare_count": ("int", False),
        "once": ("int | None", False),
        "pair": ("tuple[str, float]", False),
        "keyed_count": (None, False),  # bound by `Keyed` itself, with no return
        "wrong_pair": (None, False),
    }


def test_a_generic_method_returning_self_gives_the_receiver() -> None:
    """`Self`, bare, is the receiver's own type, its arguments too."""
    source: str = """
    from typing import Generic, Self, TypeVar

    T = TypeVar("T")

    class Box(Generic[T]):
        def again(self) -> Self:
            return self

    def f(box: Box[int]) -> None:
        again = box.again()
    """
    assert _found(source) == {"again": ("Box[int]", False)}


@pytest.mark.skipif(sys.version_info < (3, 12), reason="`class C[T]` is Python 3.12's syntax")
def test_a_type_parameter_list_names_the_parameters() -> None:
    """`class Box[T]`'s parameters are its list's; one with a `ParamSpec` or `TypeVarTuple` has none known."""
    source: str = """
    class Box[T]:
        def get(self) -> T: ...

    class Call[**P, R]:
        def result(self) -> R: ...

    def f(box: Box[int], call: Call[[int], str]) -> None:
        got = box.get()
        result = call.result()
    """
    assert _found(source) == {"got": ("int", False), "result": (None, False)}


def test_a_generic_classes_listed_parameters_are_its_whichever_module_defines_them() -> None:
    """`Generic[T, S]`, `S` another module's: a `Generic[...]` takes nothing but type variables."""
    source: str = """
    from typing import Generic, TypeVar

    from other import S

    T = TypeVar("T")

    class Pair(Generic[T, S]):
        def first(self) -> T: ...

    def f(pair: Pair[int, str]) -> None:
        first = pair.first()
    """
    assert _found(source) == {"first": ("int", False)}


def test_a_member_is_looked_for_eight_generic_bases_up_at_most() -> None:
    """Past them, it's left untyped."""
    chain: str = "\n".join(f"class C{at}(C{at - 1}[T]): ..." for at in range(1, 10))
    source: str = f"""
from typing import Generic, TypeVar

T = TypeVar("T")

class C0(Generic[T]):
    def get(self) -> T: ...

{chain}

def f(deep: C8[int], deeper: C9[int]) -> None:
    found = deep.get()
    lost = deeper.get()
"""
    assert _found(source) == {"found": ("int", False), "lost": (None, False)}


_RESULTS: str = """
from typing import Generic, TypeVar

from pkg.rows import Row

T = TypeVar("T")

class Result(Generic[T]):
    def first(self) -> T | None:
        return None

    def rows(self) -> list[tuple[T, Row]]:
        return []

    def count(self) -> int:
        return 0
"""
_USER: str = """
from pkg.results import Result
import pkg.results as r

def f(result: Result[int], other: "r.Result[str]", bare: Result) -> None:
    first = result.first()
    rows = result.rows()
    spelled = other.first()
    counted = bare.count()
    unknown = bare.first()
"""
_USER_FIXED: str = """
from pkg.results import Result
import pkg.results as r
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from pkg.rows import Row

def f(result: Result[int], other: "r.Result[str]", bare: Result) -> None:
    first: int | None = result.first()
    rows: list[tuple[int, Row]] = result.rows()
    spelled: str | None = other.first()
    counted: int = bare.count()
    unknown = bare.first()
"""


def test_another_files_generic_class_is_bound_by_the_receivers_arguments(tmp_path: Path) -> None:
    """As the file's own: its members' other names written as the file can, by an import if need be."""
    (tmp_path / "pkg").mkdir()
    sources: dict[str, str] = {
        "pkg/__init__.py": "",
        "pkg/rows.py": "class Row: ...\n",
        "pkg/results.py": _RESULTS,
        "user.py": _USER,
    }
    name: str
    source: str
    for name, source in sources.items():
        _ = (tmp_path / name).write_text(textwrap.dedent(source), encoding="utf-8")
    _ = cli.main(["--fix", "-q", "--jobs=1", "--select=LVA001", str(tmp_path)])
    assert (tmp_path / "user.py").read_text(encoding="utf-8") == textwrap.dedent(_USER_FIXED)


def test_a_class_whose_subscripted_base_passes_no_type_variable_is_plain() -> None:
    """`class Data(Mapping[Hashable, "Box"])` binds every parameter: written bare, its members read."""
    source: str = """
    from collections.abc import Hashable, Mapping

    class Box: ...

    class Data(Mapping[Hashable, "Box"]):
        def total(self) -> int: ...

    def f() -> None:
        data = Data()
        total = data.total()
    """
    assert _found(source) == {"data": ("Data", True), "total": ("int", True)}  # on a guessed receiver


@pytest.mark.parametrize(
    ("source", "generic"),
    [
        (
            "from collections.abc import Hashable as H, Mapping as M\nclass C(M[H, 'B']): ...\nclass B: ...",
            False,
        ),
        ("from typing import Literal\nclass C(Base[Literal['|O'], Literal['x']]): ...", False),
        ("import typing as t\nclass C(Base[t.IO[t.Any]]): ...", False),
        ("class C(Base['not an expression (']): ...", False),
        ("from other import Item\nclass C(list[Item]): ...\nitem = Item()", False),
        ("from other import Item\nclass C(list[Item]): ...\nisinstance(x, (int, Item))", False),
        ("from other import Item\nclass C(list[Item]): ...\nItem.__name__", True),
        ("from other import Item\nclass C(list[Item]): ...", True),
        ("from typing import T\nclass C(list[T]): ...\nT.method()", True),
        ("import typing as t\ndef f():\n    T = t.TypeVar('T')\n    class C(t.Generic[T]): ...", True),
        ("from typing import TypeVar\nT: TypeVar = TypeVar('T')\nclass C(list[T]): ...", True),
        ("from other import T\nK = T\nclass C(list[K]): ...", True),
        ("from _typeshed import SupportsRead\nclass C(list[SupportsRead]): ...", True),
        ("import os\nclass C(list[os._T]): ...", True),
    ],
)
def test_a_subscripted_base_is_generic_where_it_may_pass_a_type_variable(
    source: str,
    *,
    generic: bool,
) -> None:
    """No type variable: a builtin, a definition, a public standard-library name, a name used as a class."""
    assert (generic_classes(ast.parse(source)) == {"C"}) is generic


@pytest.mark.parametrize(
    ("source", "bare"),
    [
        (
            "from typing import Generic, TypeVar\nT = TypeVar('T', default=int)\nclass C(Generic[T]): ...",
            True,
        ),
        ("from typing import Generic, TypeVar\nT = TypeVar('T')\nclass C(Generic[T]): ...", False),
        ("from typing import Generic\nfrom other import T\nclass C(Generic[T]): ...", False),  # unknown here
        ("class C(Base['C']): ...\nclass Base: ...", True),  # no type variable: not generic at all
    ],
)
def test_a_generic_class_whose_every_parameter_has_a_default_is_written_bare(
    source: str,
    *,
    bare: bool,
) -> None:
    """A type checker reads it with the defaults: `C`, not `C[int]`."""
    tree: ast.Module = ast.parse(source)
    assert (_CLASS not in generic_classes(tree, defaulted_type_vars(tree))) is bare
    assert _CLASS in generic_classes(tree) or _GENERIC not in source


@pytest.mark.skipif(sys.version_info < (3, 13), reason="type parameter defaults are Python 3.13's")
def test_a_type_parameter_lists_defaults_are_read() -> None:
    """`class C[T = int]`: every one with a default, or not."""
    tree: ast.Module = ast.parse("class C[T = int]: ...\nclass D[T = int, S]: ...")
    assert generic_classes(tree, frozenset()) == {"D"}


_DEFAULTED_TYPES: str = """
from typing import Generic, TypeVar

K = TypeVar("K", default=str)
"""
_DEFAULTED_CLASSES: str = """
from typing import Generic

from pkg.types import K
import pkg.types as t

class Keyed(Generic[K]):
    def size(self) -> int: ...

class Spelled(Generic[t.K]): ...

def make() -> Keyed:
    return Keyed()
"""
_DEFAULTED_USER: str = """
from pkg.classes import Keyed, make

def run() -> None:
    made = make()
    size = made.size()
"""


def test_another_files_type_variable_with_a_default_leaves_its_class_written_bare(tmp_path: Path) -> None:
    """`K = TypeVar("K", default=str)` imported from another file, by name or through its module."""
    (tmp_path / "pkg").mkdir()
    sources: dict[str, str] = {
        "pkg/__init__.py": "",
        "pkg/types.py": _DEFAULTED_TYPES,
        "pkg/classes.py": _DEFAULTED_CLASSES,
        "user.py": _DEFAULTED_USER,
    }
    name: str
    source: str
    for name, source in sources.items():
        _ = (tmp_path / name).write_text(textwrap.dedent(source), encoding="utf-8")
    catalog: project.Index = project.index(sorted(tmp_path.rglob("*.py")))
    assert catalog.modules["pkg.classes"].generics == frozenset()
    assert project.defaulted(catalog, tmp_path / "pkg" / "classes.py") == {"K", "t.K"}
    _ = cli.main(["--fix", "-q", "--jobs=1", "--select=LVA001", str(tmp_path)])
    written: str = (
        textwrap.dedent(_DEFAULTED_USER)
        .replace("    made = ", "    made: Keyed = ")
        .replace("    size = ", "    size: int = ")
    )
    assert (tmp_path / "user.py").read_text(encoding="utf-8") == written


_DEFAULTED_CONTEXT: str = """
from typing import Generic, TypeVar

L = TypeVar("L", default=dict)

class Context(Generic[L]):
    def __init__(self, request, server=None) -> None: ...
"""
_DEFAULTED_SERVER: str = """
from typing import Generic, TypeVar

from pkg.context import Context

T = TypeVar("T")
O = TypeVar("O", default=int)

class Own(Generic[O]):
    def __init__(self, value) -> None: ...

class Request(Generic[T]): ...

class Server(Generic[T]):
    def handle(self, request: Request[T], raw) -> None:
        bound = Context(raw, server=self)
        passed = Context(request)
        own = Own(self)
        plain = Context(raw)

def run(raw) -> None:
    made = Context(raw)
"""


def test_a_class_read_with_its_defaults_is_no_guess_where_its_call_binds_them(tmp_path: Path) -> None:
    """`Context(raw, server=self)` in a generic class's method is a `Context[T]`, not `Context[dict]`."""
    (tmp_path / "pkg").mkdir()
    sources: dict[str, str] = {
        "pkg/__init__.py": "",
        "pkg/context.py": _DEFAULTED_CONTEXT,
        "pkg/server.py": _DEFAULTED_SERVER,
    }
    name: str
    source: str
    for name, source in sources.items():
        _ = (tmp_path / name).write_text(textwrap.dedent(source), encoding="utf-8")
    catalog: project.Index = project.index(sorted(tmp_path.rglob("*.py")))
    assert catalog.modules["pkg.context"].defaulted_generics == {"Context"}
    _ = cli.main(["--fix", "--likely", "-q", "--jobs=1", "--select=LVA001", str(tmp_path)])
    written: str = (
        textwrap.dedent(_DEFAULTED_SERVER)
        .replace("        plain = ", "        plain: Context = ")
        .replace("    made = ", "    made: Context = ")
    )
    assert (tmp_path / "pkg" / "server.py").read_text(encoding="utf-8") == written


_BOUND_BASES: str = """
from typing import Generic, TypeVar

from pkg.types import Buffer

T = TypeVar("T")

class Base(Generic[T]):
    def get(self) -> T: ...

class Codec(Base[Buffer]):
    def size(self) -> int: ...

class Unseen(Base[Missing]): ...  # a name nothing binds: it may be a type variable

def make() -> Codec:
    return Codec()

def own() -> None:
    made = make()
"""
_MADE_BARE: Final = "    made: Codec = make()"
_BOUND_USER: str = """
from pkg.codecs import make

def run() -> None:
    made = make()
"""


def test_a_class_whose_bases_name_another_modules_class_is_written_bare(tmp_path: Path) -> None:
    """`class Codec(Base[Buffer])`, `Buffer` another file's class: it binds its parameter, in either file."""
    (tmp_path / "pkg").mkdir()
    sources: dict[str, str] = {
        "pkg/__init__.py": "",
        "pkg/types.py": "class Buffer: ...\n",
        "pkg/codecs.py": _BOUND_BASES,
        "user.py": _BOUND_USER,
    }
    name: str
    source: str
    for name, source in sources.items():
        _ = (tmp_path / name).write_text(textwrap.dedent(source), encoding="utf-8")
    catalog: project.Index = project.index(sorted(tmp_path.rglob("*.py")))
    assert catalog.modules["pkg.codecs"].generics == {"Base", "Unseen"}
    assert project.defaulted(catalog, tmp_path / "pkg" / "codecs.py") == {"Buffer"}
    _ = cli.main(["--fix", "-q", "--jobs=1", "--select=LVA001", str(tmp_path)])
    # An import of `Codec` added for it, in the file that doesn't define it.
    assert _MADE_BARE in (tmp_path / "user.py").read_text(encoding="utf-8")
    assert _MADE_BARE in (tmp_path / "pkg" / "codecs.py").read_text(encoding="utf-8")
