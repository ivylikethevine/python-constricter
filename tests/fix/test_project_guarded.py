# SPDX-License-Identifier: MIT
"""Cross-module `--fix` for types the calling file doesn't import: imported under `if TYPE_CHECKING:`."""

import textwrap
from pathlib import Path
from typing import Final

import pytest

from constricter import Offence, check_source
from constricter.cli import command as cli
from constricter.fix import fixes, project
from constricter.fix.known import Guarded, Outside

HANDLES: Final = """
from __future__ import annotations

from typing import TYPE_CHECKING, Generic, Literal, TypeVar
import collections as col
import thirdparty as tp

if TYPE_CHECKING:
    from pkg.other import Thing

from pkg.again import Again

T = TypeVar("T")


class Handles(Generic[T]):
    pass


class Plain:
    pass


def handle() -> Handles[str]:
    return Handles()


def bare() -> Handles:
    return Handles()


def thing() -> Thing:
    raise ValueError


def plain() -> Plain:
    return Plain()


def quote() -> Literal["it's"]:
    return "it's"


def counter() -> col.Counter[str]:
    return col.Counter()


def again() -> Again:
    return Again()


def made():
    return plain()


def outer() -> tp.Thing:
    raise ValueError


def boxes():
    return Handles()
"""
OTHER: Final = "class Thing:\n    pass\n"
AGAIN: Final = "from pkg.other import Thing as Again\n"
_SELECT: Final = ("--all-scopes", "--select=LVA001,LVA004")
_TYPED: Final = "    {}: Plain = g()\n"
_UNTYPED: Final = "    y = boxes()\n"
USER: Final = """
\"\"\"Doc.\"\"\"

import typing

from pkg.handles import bare, counter, handle, plain, quote, thing


def f():
    a = handle()
    b = bare()
    c = thing()
    d = counter()
    return a, b, c, d


top = plain()
said = quote()
"""
USER_FIXED: Final = """
\"\"\"Doc.\"\"\"

import typing

from pkg.handles import bare, counter, handle, plain, quote, thing
if typing.TYPE_CHECKING:
    from pkg.handles import Handles
    from pkg.handles import Plain
    from pkg.other import Thing
    from typing import Literal
    import collections as col


def f():
    a: Handles[str] = handle()
    b = bare()
    c: Thing = thing()
    d: col.Counter[str] = counter()
    return a, b, c, d


top: "Plain" = plain()
said: 'Literal["it\\'s"]' = quote()
"""
BLOCK: Final = """
from __future__ import annotations

from typing import TYPE_CHECKING

from pkg.handles import handle, thing

if TYPE_CHECKING:
    from pkg.other import Thing as Named

top = handle()
other = thing()
"""
BLOCK_FIXED: Final = """
from __future__ import annotations

from typing import TYPE_CHECKING

from pkg.handles import handle, thing

if TYPE_CHECKING:
    from pkg.other import Thing as Named
    from pkg.handles import Handles

top: Handles[str] = handle()
other: Named = thing()
"""
LATE_BLOCK: Final = """
from typing import TYPE_CHECKING
from pkg.handles import handle, plain

first = handle()

if TYPE_CHECKING:
    import os


def f():
    y = plain()
    return y
"""
LATE_FIXED: Final = """
from typing import TYPE_CHECKING
from pkg.handles import handle, plain

first: "Handles[str]" = handle()

if TYPE_CHECKING:
    import os
    from pkg.handles import Handles
    from pkg.handles import Plain


def f():
    y: Plain = plain()
    return y
"""
CLASHING: Final = """
from pkg.handles import again, handle, plain


def f(Handles):
    a = handle()
    b = again()
    return a, b, Handles


class Plain:
    pass


x = plain()
"""
UNGUARDABLE: Final = """
from pkg.handles import plain


def f(typing, TYPE_CHECKING):
    x = plain()
    return x, typing, TYPE_CHECKING
"""
THIRD_PARTY: Final = """
from pkg.handles import outer


def f():
    x = outer()
    return x
"""
ALIASED: Final = """
from pkg.handles import Plain as P, plain


def f():
    x = plain()
    return x
"""
CHAINED: Final = """
from pkg.handles import boxes, made


def box():
    y = boxes()
    return y


def g():
    return made()


def h():
    x = g()
    return x
"""


def _write(path: Path, source: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    _ = path.write_text(textwrap.dedent(source), encoding="utf-8", newline="\n")
    return path


def _package(root: Path) -> None:
    _ = _write(root / "pkg" / "__init__.py", "")
    _ = _write(root / "pkg" / "handles.py", HANDLES)
    _ = _write(root / "pkg" / "other.py", OTHER)
    _ = _write(root / "pkg" / "again.py", AGAIN)


@pytest.mark.parametrize("jobs", ["1", "2"])
def test_a_type_the_file_doesnt_import_is_imported_for_type_checking(tmp_path: Path, jobs: str) -> None:
    """A new `if TYPE_CHECKING:` block, spelled as the file imports `typing`; a module body's type quoted.

    Never a generic class without its arguments; a second run has nothing left to fix.
    """
    _package(tmp_path)
    user: Path = _write(tmp_path / "user.py", USER)
    for _ in range(2):  # the second run changes nothing
        assert cli.main(["--fix", "-q", f"--jobs={jobs}", *_SELECT, str(tmp_path)]) == cli.EXIT_FOUND
        assert user.read_text(encoding="utf-8") == textwrap.dedent(USER_FIXED)


@pytest.mark.parametrize(("source", "fixed"), [(BLOCK, BLOCK_FIXED), (LATE_BLOCK, LATE_FIXED)])
def test_an_import_joins_the_files_type_checking_block(tmp_path: Path, source: str, fixed: str) -> None:
    """Indented as it is, anywhere; what it has is used, as it's named; nothing's quoted when postponed."""
    _package(tmp_path)
    user: Path = _write(tmp_path / "user.py", source)
    for _ in range(2):
        assert cli.main(["--fix", "-q", *_SELECT, str(tmp_path)]) == cli.EXIT_FOUND  # `T`, in `pkg`
        assert user.read_text(encoding="utf-8") == textwrap.dedent(fixed)


def test_a_name_the_file_binds_otherwise_isnt_imported(tmp_path: Path) -> None:
    """Not over a parameter, a class, or the name an import binds; the rest are."""
    _package(tmp_path)
    user: Path = _write(tmp_path / "user.py", CLASHING)
    catalog: project.Index = project.index(sorted(tmp_path.rglob("*.py")))
    imported: project.Imported = project.imported(catalog, user)
    assert imported.calls == {"again": "Again", "handle": "Handles[str]"}
    assert imported.guarded == {
        "Again": Guarded(("pkg.again", "Again"), "from pkg.again import Again"),
        "Handles": Guarded(("pkg.handles", "Handles"), "from pkg.handles import Handles"),
    }
    offences: list[Offence] = check_source(
        user.read_text(encoding="utf-8"),
        outside=Outside(imported.calls, imported.classes, guarded=imported.guarded),
    )
    assert {o.name: o.fix for o in offences} == {"a": None, "b": "Again"}
    assert not project.calls(catalog, user)


@pytest.mark.parametrize(
    ("source", "annotation"),
    [(UNGUARDABLE, None), (THIRD_PARTY, None), (ALIASED, "P")],
)
def test_a_type_is_written_as_the_file_can(tmp_path: Path, source: str, annotation: str | None) -> None:
    """Under the name the file imports it by; not where nothing can be `TYPE_CHECKING`.

    Nor from a module that may not be installed: neither checked nor the standard library's.
    """
    _package(tmp_path)
    user: Path = _write(tmp_path / "user.py", source)
    imported: project.Imported = project.imported(project.index(sorted(tmp_path.rglob("*.py"))), user)
    offences: list[Offence] = check_source(
        user.read_text(encoding="utf-8"),
        outside=Outside(imported.calls, guarded=imported.guarded),
    )
    assert [o.fix for o in offences] == [annotation]


def test_a_guarded_type_passes_through_an_unannotated_function(tmp_path: Path) -> None:
    """A file's own function returning another's guarded type types its calls in a third, in one run.

    Never another file's generic class, bare.
    """
    _package(tmp_path)
    _ = _write(tmp_path / "pkg" / "chain.py", CHAINED)
    _ = _write(tmp_path / "use.py", "from pkg.chain import g\n\ndef k():\n    y = g()\n    return y\n")
    assert cli.main(["--fix", "-q", "--unsafe-fixes", "--select=LVA001", str(tmp_path)]) == cli.EXIT_FOUND
    assert _TYPED.format("y") in (tmp_path / "use.py").read_text(encoding="utf-8")
    assert _TYPED.format("x") in (tmp_path / "pkg" / "chain.py").read_text(encoding="utf-8")
    assert _UNTYPED in (tmp_path / "pkg" / "chain.py").read_text(encoding="utf-8")  # generic: bare


def test_another_files_generic_class_is_known_as_the_file_spells_it(tmp_path: Path) -> None:
    """For `--fix` never to write it bare, however it's imported."""
    _package(tmp_path)
    _ = _write(tmp_path / "pkg" / "__init__.py", "from .handles import Handles\n")
    user: Path = _write(
        tmp_path / "user.py",
        "from pkg.handles import Handles as H, Plain\nimport pkg.handles\n",
    )
    imported: project.Imported = project.imported(project.index(sorted(tmp_path.rglob("*.py"))), user)
    assert imported.generics == {"H", "pkg.handles.Handles", "pkg.Handles"}  # the package's re-export too


def test_a_guarded_import_is_a_replacement_too(tmp_path: Path) -> None:
    """SARIF's and rdjson's edits carry the block, as `apply` writes it."""
    _package(tmp_path)
    user: Path = _write(tmp_path / "user.py", "from pkg.handles import plain\n\ndef f():\n    x = plain()\n")
    catalog: project.Index = project.index(sorted(tmp_path.rglob("*.py")))
    imported: project.Imported = project.imported(catalog, user)
    text: list[str] = user.read_text(encoding="utf-8").splitlines(keepends=True)
    offences: list[Offence] = check_source(
        "".join(text),
        outside=Outside(imported.calls, guarded=imported.guarded),
    )
    assert [edit.text for edit in fixes.replacements(text, offences[0])] == [
        ": Plain",
        "from typing import TYPE_CHECKING\nif TYPE_CHECKING:\n    from pkg.handles import Plain\n",
    ]
