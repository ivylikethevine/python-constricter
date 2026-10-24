"""Cross-module `--fix`: calls to functions, and uses of classes, other checked files define."""

import textwrap
from pathlib import Path
from typing import Final

import pytest

from constricter import Offence, check_source
from constricter.cli import command as cli
from constricter.fix.core.known import Classes, Guarded, Outside, Returns
from constricter.fix.index import crossed, linked, project

# Each starts `--jobs` workers of its own: one at a time, where the tests run at once (`pytest -n`).
JOBS: pytest.MarkDecorator = pytest.mark.xdist_group("jobs")

UTIL: Final = """
from pkg.types import Row
import pkg.types as t

class Local:
    pass

def helper() -> int:
    return 1

def row() -> Row:
    return Row()

def trow() -> t.Row:
    return t.Row()

def local() -> Local:
    return Local()

def text() -> "list[str]":
    return []

def length() -> len:
    return len
"""
MAIN: Final = """
from pkg import helper
from pkg.util import row, local, length
from pkg.types import Row
import pkg.util as u
import pkg.util

def run() -> None:
    a = helper()
    b = row()
    c = local()
    d = u.helper()
    e = pkg.util.text()
    f = u.trow()
    g = length()
"""
SERIAL: Final = "\n  require_serial: true\n"
DEEP: Final = "    x: int = helper()\n    y = far()\n"
FIXED: Final = """
from pkg import helper
from pkg.util import row, local, length
from pkg.types import Row
import pkg.util as u
import pkg.util
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    import pkg.types as t

def run() -> None:
    a: int = helper()
    b: Row = row()
    c: u.Local = local()
    d: int = u.helper()
    e: list[str] = pkg.util.text()
    f: t.Row = u.trow()
    g: len = length()
"""


def _write(path: Path, source: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    _ = path.write_text(textwrap.dedent(source), encoding="utf-8", newline="\n")
    return path


def _package(root: Path) -> None:
    """Write `pkg` (a re-export in `__init__`, a helper module, a deep relative import) under `root`."""
    _ = _write(root / "pkg" / "__init__.py", "from .util import helper\nfrom . import types\n")
    _ = _write(root / "pkg" / "types.py", "class Row:\n    pass\n")
    _ = _write(root / "pkg" / "util.py", UTIL)
    _ = _write(root / "pkg" / "sub" / "__init__.py", "")
    _ = _write(
        root / "pkg" / "sub" / "deep.py",
        "from ..util import helper\nfrom ...outside import far\n\ndef go() -> None:\n"
        + DEEP.replace(": int", ""),
    )


@JOBS
@pytest.mark.parametrize("jobs", ["1", "2"])
def test_fix_annotates_calls_to_other_modules(tmp_path: Path, jobs: str) -> None:
    """`--fix` types a call to another checked file's function, when the file can name its type."""
    _package(tmp_path)
    main: Path = _write(tmp_path / "main.py", MAIN)
    assert cli.main(["--fix", "-q", f"--jobs={jobs}", str(tmp_path)]) == cli.EXIT_FOUND
    assert main.read_text(encoding="utf-8") == FIXED
    assert (tmp_path / "pkg" / "sub" / "deep.py").read_text(encoding="utf-8").endswith(DEEP)


def test_module_names_follow_packages(tmp_path: Path) -> None:
    """A file's module name starts at the outermost folder with an `__init__.py`."""
    _package(tmp_path)
    names: list[str] = [
        project.module_name(tmp_path / "pkg" / "sub" / "deep.py"),
        project.module_name(tmp_path / "pkg" / "__init__.py"),
        project.module_name(tmp_path / "main.py"),
    ]
    assert names == ["pkg.sub.deep", "pkg", "main"]


def test_index_reads_names_and_skips_what_it_cannot(tmp_path: Path) -> None:
    """The index records each top-level binding's origin, and skips unparsable and non-`.py` files."""
    source: Path = _write(
        tmp_path / "mod.py",
        "import os.path\nimport json as j\nx, (y, z) = 1, (2, 3)\nw: int = 1\nw += 1\nif w:\n    pass\n",
    )
    broken: Path = _write(tmp_path / "broken.py", "def (\n")
    sheet: Path = _write(tmp_path / "sheet.ipynb", "{}")
    index: project.Index = project.index([source, broken, sheet, tmp_path / "gone.py"])
    assert list(index.modules) == ["mod"]
    assert index.modules["mod"].names == {
        "os": ("os", None),
        "j": ("json", None),
        "x": ("mod", "x"),
        "y": ("mod", "y"),
        "z": ("mod", "z"),
        "w": ("mod", "w"),
    }


def test_calls_skip_what_they_cannot_resolve(tmp_path: Path) -> None:
    """Nothing for unindexed files, re-export loops, local names, or unknown modules."""
    loop: Path = _write(
        tmp_path / "loop.py",
        "from loop import f\nfrom other import g\ndef h() -> int:\n    return 1\n",
    )
    index: project.Index = project.index([loop])
    assert not project.calls(index, loop)
    assert not project.calls(index, tmp_path / "sheet.ipynb")
    assert not project.calls(index, tmp_path / "unknown.py")
    cycle: dict[str, project.Module] = {
        "a": project.Module(name="a", returns={}, names={"f": ("b", "f")}),
        "b": project.Module(name="b", returns={}, names={"f": ("a", "f")}),
    }
    assert not project.calls(project.Index(cycle, sorted(cycle)), Path("a.py"))


def test_split_run_misses_what_the_serial_hook_fixes(tmp_path: Path) -> None:
    """Split across processes (as pre-commit does by default), `main.py` can't see `pkg`'s types.

    So the `constricter-fix` hook asks pre-commit for one process (`require_serial`).
    """
    _package(tmp_path)
    main: Path = _write(tmp_path / "main.py", MAIN)
    assert cli.main(["--fix", "-q", str(main)]) == cli.EXIT_FOUND
    assert main.read_text(encoding="utf-8") != FIXED
    assert cli.main(["--fix", "-q", str(main), str(tmp_path / "pkg")]) == cli.EXIT_FOUND
    assert main.read_text(encoding="utf-8") == FIXED
    hooks: list[str] = (
        (Path(__file__).parents[3] / ".pre-commit-hooks.yaml").read_text(encoding="utf-8").split("- id: ")
    )
    fix: str = next(hook for hook in hooks if hook.startswith("constricter-fix\n"))
    assert SERIAL in fix


MODELS: Final = """
from typing import Self

from pkg.types import Tag


class Row:
    size: int
    tag: Tag
    local: "Hidden"

    @property
    def label(self) -> str:
        return ""

    def total(self) -> float:
        return 0.0

    def again(self) -> Self:
        return self


class Hidden:
    pass
"""
USES: Final = """
import pkg.models as m
from pkg import Row
from pkg.types import Tag


def f(row: Row, other: m.Row) -> None:
    a = row.size
    b = row.label
    c = row.total()
    d = row.again()
    e = other.again()
    g = row.tag
    h = other.tag
    i = row.local
    j = other.missing
"""


def test_imported_classes_type_their_members(tmp_path: Path) -> None:
    """An imported class's attributes, properties and methods type their uses, as in its own module.

    Through `from pkg import Row` (a re-export) and `import pkg.models as m`; a `Self` return is the
    class as the file spells it; a type the file doesn't import (`Hidden`) is written through the
    module it does (`m.Hidden`).
    """
    _ = _write(tmp_path / "pkg" / "__init__.py", "from .models import Row\n")
    _ = _write(tmp_path / "pkg" / "types.py", "class Tag:\n    pass\n")
    _ = _write(tmp_path / "pkg" / "models.py", MODELS)
    main: Path = _write(tmp_path / "main.py", USES)
    imported: project.Imported = crossed.imported(project.index(sorted(tmp_path.rglob("*.py"))), main)
    offences: list[Offence] = check_source(
        main.read_text(encoding="utf-8"),
        outside=Outside(classes=imported.classes),
    )
    assert {o.name: o.fix for o in offences} == {
        "a": "int",
        "b": "str",
        "c": "float",
        "d": "Row",
        "e": "m.Row",
        "g": "Tag",
        "h": "Tag",
        "i": "m.Hidden",
        "j": None,
    }
    assert crossed.imported(project.Index({}, []), main) == project.Imported({}, Classes({}, {}))


BASES: Final = """
from __future__ import annotations

from typing import Self


class Root:
    def size(self) -> int:
        return 1

    def clone(self) -> Self:
        return self

    def label(self) -> str:
        return ""

    def root(self) -> Root:
        return self


class Base(Root):
    label = None

    def base(self) -> Base:
        return self

    def name(self) -> bytes:
        return b""
"""
DERIVED: Final = """
import other
import pkg.bases as b
from pkg.bases import Base


class Own:
    def own(self) -> float:
        return 1.5


class Child(Own, Base):
    def f(self, base: Base) -> None:
        a = self.size()
        b = self.name()
        c = self.own()
        d = self.clone()
        e = self.base()
        g = self.root()
        h = self.label()
        i = base.size()
        j = base.clone()


class Spelled(b.Base, Own):
    def g(self) -> None:
        k = self.name()
        m = self.own()


class Hidden(other.Thing, Base):
    def h(self) -> None:
        n = self.size()
"""


def test_a_class_takes_methods_from_another_files_base(tmp_path: Path) -> None:
    """The base's own, and those it takes from its file's classes; not past it, nor what may be `Self`."""
    _ = _write(tmp_path / "pkg" / "__init__.py", "")
    _ = _write(tmp_path / "pkg" / "bases.py", BASES)
    main: Path = _write(tmp_path / "main.py", DERIVED)
    imported: project.Imported = crossed.imported(project.index(sorted(tmp_path.rglob("*.py"))), main)
    offences: list[Offence] = check_source(
        main.read_text(encoding="utf-8"),
        outside=Outside(classes=imported.classes),
    )
    assert {o.name: o.fix for o in offences} == {
        "a": "int",  # `Root`'s, through `Base`
        "b": "bytes",
        "c": "float",
        "d": None,  # `Self`: a `Child` here, which `Base` doesn't say
        "e": None,  # `Base`, or its `Self`
        "g": "Root",
        "h": None,  # `Base` binds `label` itself
        "i": "int",
        "j": "Base",
        "k": "bytes",
        "m": None,  # `Own` comes after a class of another file
        "n": None,  # a base out of sight comes first
    }


TYPING: Final = """
from typing import TypeVar

T = TypeVar("T")
"""
GENERIC: Final = """
from pkg._typing import T

class Box:
    def get(self, x: T) -> T:
        return x

def same(x: T) -> T:
    return x

def run(box: Box) -> None:
    a = same(1)
    b = box.get(1)
"""
USES_GENERIC: Final = """
from pkg.generic import Box, same

def run(box: Box) -> None:
    c = same(1)
    d = box.get(1)
"""


def test_an_imported_type_variable_is_never_a_calls_type(tmp_path: Path) -> None:
    """A return naming a type variable its module imports depends on the arguments, in or out of it."""
    _ = _write(tmp_path / "pkg" / "__init__.py", "")
    _ = _write(tmp_path / "pkg" / "_typing.py", TYPING)
    generic: Path = _write(tmp_path / "pkg" / "generic.py", GENERIC)
    uses: Path = _write(tmp_path / "uses.py", USES_GENERIC)
    catalog: project.Index = project.index(sorted(tmp_path.rglob("*.py")))
    assert project.type_vars(catalog, generic) == {"T"}
    assert project.type_vars(catalog, uses) == set()
    assert project.type_vars(catalog, tmp_path / "missing.py") == set()
    imported: project.Imported = crossed.imported(catalog, uses)
    assert imported.calls == {}
    assert imported.classes.methods == {"Box": {}}
    inside: list[Offence] = check_source(
        generic.read_text(encoding="utf-8"),
        outside=Outside(type_vars=project.type_vars(catalog, generic)),
    )
    outside: list[Offence] = check_source(
        uses.read_text(encoding="utf-8"),
        outside=Outside(calls=imported.calls, classes=imported.classes),
    )
    assert {o.name: o.fix for o in (*inside, *outside)} == dict.fromkeys(("a", "b", "c", "d"))


USES_REEXPORTED: Final = """
import pkg as p
import pkg.api

def run() -> None:
    a = p.make()
    b = pkg.api.make()
    c = p.bare()
    d = p.missing()
"""


def test_a_call_through_a_module_follows_its_reexports(tmp_path: Path) -> None:
    """`p.make()` is typed by the function `pkg/__init__.py` imports in turn, if it declares its return.

    Not by one typed by its `return`s alone, which waits on its own module's check.
    """
    _ = _write(tmp_path / "pkg" / "__init__.py", "from pkg.api import Thing, make, bare\n")
    _ = _write(tmp_path / "pkg" / "api.py", "from pkg.impl import Thing, make, bare\n")
    _ = _write(
        tmp_path / "pkg" / "impl.py",
        "class Thing:\n    pass\n\ndef make() -> Thing:\n    return Thing()\n\ndef bare():\n    return 1\n",
    )
    uses: Path = _write(tmp_path / "uses.py", USES_REEXPORTED)
    catalog: project.Index = project.index(sorted(tmp_path.rglob("*.py")))
    guarded: dict[str, Guarded] = {}
    assert project.calls(catalog, uses, guarded) == {"p.make": "Thing", "pkg.api.make": "Thing"}
    assert [needed.statement for needed in guarded.values()] == ["from pkg.impl import Thing"]
    assert project.returned(catalog, uses, {}).calls == {}


def test_a_file_read_again_takes_its_modules_place(tmp_path: Path) -> None:
    """A file `--fix` changed replaces its module, keeping what the other files told of it.

    Not a module several files are named (but a `conftest.py`, by its directory), nor one the index
    hasn't.
    """
    lib: Path = _write(tmp_path / "lib.py", "def make():\n    return 1\n")
    near: Path = _write(tmp_path / "a" / "conftest.py", "")
    far: Path = _write(tmp_path / "b" / "conftest.py", "")
    twin: Path = _write(tmp_path / "c" / "twin.py", "")
    paths: list[Path] = [lib, near, far, twin, _write(tmp_path / "d" / "twin.py", "")]
    catalog: project.Index = linked.with_returned(project.index(paths), {"lib": Returns({"make": "int"})})
    _ = _write(lib, "def make() -> int:\n    return 1\n")
    _ = _write(near, "LIMIT: int = 1\n")
    _ = _write(far, "LIMIT: int = 2\n")
    _ = _write(twin, "LIMIT: int = 3\n")
    again: list[Path] = [lib, near, far, twin, _write(tmp_path / "new.py", ""), tmp_path / "gone.py"]
    spliced: project.Index = project.spliced(catalog, [project.read(path) for path in again])
    assert spliced.modules["lib"].returns == {"make": "int"}
    assert spliced.modules["lib"].returned == catalog.modules["lib"].returned
    assert spliced.conftests[str(near.parent.resolve())].names.keys() == {"LIMIT"}
    assert spliced.modules["conftest"] is spliced.conftests[str(far.parent.resolve())]
    assert spliced.modules["twin"] is catalog.modules["twin"]
    assert spliced.modules.keys() == catalog.modules.keys()  # not `new`
    assert spliced.memo is not catalog.memo


LAZY_INIT: Final = """
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .adapter import Adapter


def __getattr__(name):
    from importlib import import_module

    return getattr(import_module(".adapter", __name__), name)
"""
ADAPTER: Final = """
class Schema:
    pass


class Adapter:
    schema: Schema

    def validate(self, value: object) -> int:
        return 1
"""
LAZY_USER: Final = """
from pkg import Adapter


def use(adapter: Adapter):
    schema = adapter.schema
    checked = adapter.validate(1)
    return schema, checked
"""
LAZY_FIXED: Final = """
from pkg import Adapter
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from pkg.adapter import Schema


def use(adapter: Adapter):
    schema: Schema = adapter.schema
    checked: int = adapter.validate(1)
    return schema, checked
"""


def test_a_class_a_package_exports_for_type_checking_alone_is_followed(tmp_path: Path) -> None:
    """Its `__init__` imports it only when asked for (pydantic's): its members type what's read of it."""
    _ = _write(tmp_path / "pkg" / "__init__.py", LAZY_INIT)
    _ = _write(tmp_path / "pkg" / "adapter.py", ADAPTER)
    user: Path = _write(tmp_path / "user.py", LAZY_USER)
    assert cli.main(["--fix", "-q", "--select=LVA001", str(tmp_path)]) == cli.EXIT_CLEAN
    assert user.read_text(encoding="utf-8") == textwrap.dedent(LAZY_FIXED)


IMPL: Final = "class Thing:\n    pass\n\ndef make() -> Thing:\n    return Thing()\n"
SKIPPING: Final = """
import pytest
from pytest import importorskip

top = pytest.importorskip("pkg.impl")


def test_local() -> None:
    m = pytest.importorskip("pkg.impl")
    a = m.make()
    b = top.make()
    c = importorskip(modname="pkg.impl").make()


def test_again() -> None:
    import pkg.impl as again

    again = pytest.importorskip("pkg.impl")
    d = again.make()


def test_other() -> None:
    other = pytest.importorskip("pkg.impl")
    other = 1
    named = pytest.importorskip("pkg.impl")
    caught = pytest.importorskip("pkg.impl")
    try:
        pass
    except ValueError as caught:
        pass
    e = pytest.importorskip("pkg.api").make()
    f = pytest.importorskip(name)


def named() -> None:
    pass


def test_parameter(given) -> None:
    given = pytest.importorskip("pkg.impl")
"""


def test_importorskip_binds_its_module_as_an_import_does(tmp_path: Path) -> None:
    """`m = pytest.importorskip("pkg.impl")`, then `m.make()`: typed as after `import pkg.impl as m`.

    In a function or at the top, however `importorskip` is imported, with `import pkg.impl as m`
    beside it; not a name bound otherwise anywhere, or to another module.
    """
    _ = _write(tmp_path / "pkg" / "__init__.py", "")
    _ = _write(tmp_path / "pkg" / "api.py", "")
    _ = _write(tmp_path / "pkg" / "impl.py", IMPL)
    uses: Path = _write(tmp_path / "test_uses.py", SKIPPING)
    catalog: project.Index = project.index(sorted(tmp_path.rglob("*.py")))
    module: project.Module = catalog.modules["test_uses"]
    assert {name: module.names[name] for name in ("top", "m", "again")} == {
        "top": ("pkg.impl", None),
        "m": ("pkg.impl", None),
        "again": ("pkg.impl", None),
    }
    assert not {"other", "caught", "given"} & module.names.keys()
    assert module.names["named"] == ("test_uses", "named")
    guarded: dict[str, Guarded] = {}
    assert project.calls(catalog, uses, guarded) == {
        "m.make": "Thing",
        "top.make": "Thing",
        "again.make": "Thing",
    }


def test_a_type_from_a_skipped_module_is_imported_for_type_checking(tmp_path: Path) -> None:
    """The import a fix adds from a module `importorskip` takes goes under `if TYPE_CHECKING:`.

    The module may be missing when the file runs: the test is skipped then, not failed.
    """
    _ = _write(tmp_path / "pkg" / "__init__.py", "")
    _ = _write(tmp_path / "pkg" / "impl.py", IMPL)
    uses: Path = _write(
        tmp_path / "test_uses.py",
        """\
        import pytest


        def test_local() -> None:
            m = pytest.importorskip("pkg.impl")
            a = m.make()
        """,
    )
    _ = cli.main(["--fix", "-q", "--select=LVA001", str(tmp_path)])
    assert uses.read_text(encoding="utf-8") == textwrap.dedent(
        """\
        import pytest
        from typing import TYPE_CHECKING
        if TYPE_CHECKING:
            from pkg.impl import Thing


        def test_local() -> None:
            m = pytest.importorskip("pkg.impl")
            a: Thing = m.make()
        """,
    )


DESCRIBED: Final = """
from typing import Any, overload


class Impl: ...


class Plain:
    def __get__(self, instance: Any, owner: Any) -> Impl:
        return Impl()


class Over:
    @overload
    def __get__(self, instance: None, owner: Any) -> "Over": ...
    @overload
    def __get__(self, instance: object, owner: Any) -> Impl: ...
    def __get__(self, instance: Any, owner: Any) -> Any:
        return self
"""
FRAME: Final = """
from pkg.described import Over, Plain


class Frame:
    plain: Plain = Plain()
    over: Over = Over()
"""
GUARD: Final = "from typing import TYPE_CHECKING\nif TYPE_CHECKING:\n    from pkg.described import Impl\n"
FRAME_READ: Final = f"""\
from pkg.frame import Frame
{GUARD}

def read(frame: Frame) -> None:
    a: Impl = frame.plain
    b = frame.over
"""


@JOBS
@pytest.mark.parametrize("jobs", ["1", "2"])
def test_another_files_descriptor_is_read_by_its_get(tmp_path: Path, jobs: str) -> None:
    """An attribute of another file's descriptor class, read through an instance, is its `__get__`'s return.

    Its import written for type checking; an overloaded `__get__`'s, which a checker picks among, is no fix.
    """
    _ = _write(tmp_path / "pkg" / "__init__.py", "")
    _ = _write(tmp_path / "pkg" / "described.py", DESCRIBED)
    _ = _write(tmp_path / "pkg" / "frame.py", FRAME)
    uses: Path = _write(tmp_path / "use.py", FRAME_READ.replace("a: Impl", "a").replace(GUARD, ""))
    _ = cli.main(["--fix", "-q", "--select=LVA001", f"--jobs={jobs}", str(tmp_path)])
    assert uses.read_text(encoding="utf-8") == FRAME_READ
