# SPDX-License-Identifier: MIT
"""`--fix` for the standard library, from tables generated from typeshed, resolved through the imports."""

import ast
import importlib
import json
import pkgutil
import sys
import textwrap
import warnings
from pathlib import Path
from typing import TYPE_CHECKING, Final, TypeAlias, cast

import pytest

from constricter import Offence, check_source
from constricter.fix.core import imports
from constricter.fix.core.known import ImportPlan, Inference, Known, LibraryNames
from constricter.fix.libraries import stdlib

if TYPE_CHECKING:
    from types import ModuleType

UNANNOTATED: Final = "LVA001"
PYPY: Final = "pypy"
Configs: TypeAlias = list[str]  # platforms and Python versions: `linux-3.12`
# Where each entry only some platforms and Python versions have is (see `stdlib_tables.generate.PARTIAL`).
PARTIAL: Final = cast(
    "dict[str, Configs]",
    json.loads((Path(__file__).parents[3] / "stdlib_tables" / "partial.json").read_text(encoding="utf-8")),
)
LINUX: Final = "linux"
SOURCE: Final = """
import os
import os.path as osp
import time as t
from os import environ, getpid
from textwrap import dedent as dd
from other import getpid as not_std


def f(name: str, data: bytes, unknown, box: "Box") -> None:
    a = t.time()
    b = getpid()
    c = dd("x")
    d = os.path.join(name, "x")
    e = osp.join(data, b"y")
    g = osp.join(name, unknown)
    h = os.environ.get("HOME")
    i = environ.get("HOME", "/")
    j = os.getenv("X", 3)
    k = not_std()
    m = os.path.getsize(name)
    n = os.getenv("X", default="y")
    r = os.path.getsize(filename=name)
    p = osp.join(name, data)
    q = box.time()
    s = os.environ.copy()
    u = environ.copy()
"""


def test_a_table_function_is_typed_however_it_is_imported() -> None:
    """`import m`, `import m as a` and `from m import f` all resolve; a same-named function doesn't.

    An `AnyStr` function is typed only when its arguments agree on `str` or `bytes`; an environment
    lookup is `str | None`, or `str` with a `str` default (`os.getenv`'s, the default's type).
    """
    found: list[Offence] = check_source(textwrap.dedent(SOURCE))
    fixed: dict[str, tuple[str | None, bool]] = {
        o.name: (o.fix, o.unsafe) for o in found if o.code == UNANNOTATED
    }
    assert fixed == {
        "a": ("float", False),
        "b": ("int", False),
        "c": ("str", False),
        "d": ("str", False),
        "e": ("bytes", False),
        "g": ("str", False),  # only the `str` signature takes `name`
        "h": ("str | None", False),
        "i": ("str", False),
        "j": ("str | int", False),
        "k": (None, False),
        "m": ("int", False),
        "n": ("str", False),
        "r": ("int", False),  # but not a fixed return's
        "p": (None, False),  # `str` and `bytes` together: no `AnyStr`
        "q": (None, False),
        "s": ("dict[str, str]", False),  # the environment's own copy, a plain `dict`
        "u": ("dict[str, str]", False),
    }


def test_a_functions_own_import_is_resolved_in_it() -> None:
    """A name a function's own imports alone bind is what they import, in it and the functions inside it.

    Not one it binds another way too, nor one two of its imports bind to different things; and a
    type of a module only a function imports is imported for type checking alone.
    """
    source: str = """
    import os
    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from inspect import Signature


    def f(name: str, flag: bool) -> None:
        import os.path as osp
        import time
        from inspect import signature
        from subprocess import run

        if flag:
            from os import getpid
        else:
            from threading import get_ident as getpid
        try:
            import shutil
        except ImportError:
            shutil = None

        a = time.time()
        b = osp.basename(name)
        c = signature(f)
        d = run([name], text=True)
        e = getpid()
        g = shutil.which(name)

        def inner() -> None:
            h = time.monotonic()


    def g(name: str) -> None:
        x = time.time()
        y = os.getpid()
    """
    found: list[Offence] = check_source(textwrap.dedent(source))
    assert {o.name: o.fix for o in found if o.code == UNANNOTATED} == {
        "a": "float",
        "b": "str",
        "c": "Signature",
        "d": "CompletedProcess[str]",
        "e": None,
        "g": None,
        "h": "float",
        "x": None,
        "y": "int",
    }
    assert [(o.name, o.edit.guarded) for o in found if o.edit is not None and o.edit.guarded] == [
        ("d", ("from subprocess import CompletedProcess",)),
    ]
    assert not [o.name for o in found if o.edit is not None and o.edit.imports]


def test_an_attribute_naming_classes_is_written_as_the_module_can() -> None:
    """An attribute or a module variable typed with classes' own arguments is spelled part by part.

    `Signature`'s `parameters`, `ast.Module`'s `body`, one a class inherits (`SECTCRE`), and
    `sys.modules`; a type imported for type checking alone names a receiver too.
    """
    source: str = """
    import ast
    import configparser
    import inspect
    import sys
    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from pathlib import PurePath


    def f(sig: inspect.Signature, tree: ast.Module, parser: configparser.ConfigParser, p: "PurePath") -> None:
        a = sig.parameters
        b = list(sig.parameters.values())
        for c in tree.body:
            d = c.lineno
        e = parser.SECTCRE
        g = sys.modules
        h = sys.modules["os"]
        i = sys._getframe(1)
        j = i.f_code
        k = p.parents
        m = p.with_name("x")
    """
    found: list[Offence] = check_source(textwrap.dedent(source))
    assert {o.name: o.fix for o in found if o.code in {UNANNOTATED, "LVA002"}} == {
        "a": "MappingProxyType[str, inspect.Parameter]",
        "b": "list[inspect.Parameter]",
        "c": "ast.stmt",
        "d": "int",
        "e": "Pattern[str]",
        "g": "dict[str, ModuleType]",
        "h": "ModuleType",
        "i": "FrameType",
        "j": "CodeType",
        "k": "Sequence[PurePath]",
        "m": "PurePath",
    }


def test_a_bare_generic_return_is_written_with_its_defaults() -> None:
    """`SubElement` returns a bare `Element`, whose `_Tag` defaults to `str`: an `Element[str]`.

    A capitalised function the tables can't type (`Comment`) isn't guessed to construct one.
    """
    source: str = """
    import xml.etree.ElementTree as ET
    from xml.etree.ElementTree import Comment, SubElement


    def f(root: ET.Element) -> None:
        a = SubElement(root, "a")
        b = ET.SubElement(root, "b")
        c = Comment("c")
        d = ET.Comment("d")
        e = Thing()
    """
    found: list[Offence] = check_source(textwrap.dedent(source))
    fixed: dict[str, tuple[str | None, bool]] = {
        o.name: (o.fix, o.unsafe) for o in found if o.code == UNANNOTATED
    }
    assert fixed == {
        "a": ("ET.Element[str]", False),
        "b": ("ET.Element[str]", False),
        "c": (None, False),
        "d": (None, False),
        "e": ("Thing", True),
    }


@pytest.mark.parametrize("name", sorted(stdlib.KNOWN | stdlib.FUNCTIONS))
def test_every_table_function_exists(name: str) -> None:
    """Each table entry names a real standard-library function, as Linux CPython has it.

    The tables are what each minor release's latest patch release has, on the platforms typeshed
    covers: `stdlib_tables/partial.json` lists an entry only some have. CI's Linux jobs run those
    patch releases, so they must have every entry listed for them. Elsewhere an entry may be missing, and
    is skipped: PyPy lacks some of CPython's own (`tracemalloc`, `gc.get_count`), and macOS and
    Windows stop at the last patch release with an installer (3.11.9, 3.12.10), before security
    releases' additions like `tarfile.LinkFallbackError`. A module built only where a system
    library is (`nis` with `libnsl`, `dbm.gnu` with `gdbm`) may be missing anywhere. What's there
    must still be callable.
    """
    found: bool | None = _callable(name)
    here: str = f"{sys.platform}-{sys.version_info.major}.{sys.version_info.minor}"
    if found is None and (sys.implementation.name == PYPY or sys.platform != LINUX):
        pytest.skip("not in this platform's build")
    if name in PARTIAL and here not in PARTIAL[name]:
        pytest.skip("not in the stubs for this platform and version")
    if found is None and not _built(name):
        pytest.skip("its module isn't built into this Python")
    assert found


def _built(name: str) -> bool:
    """Check that every module a table entry's path names is here (not an optional one left unbuilt).

    Returns:
      Whether each is.

    """
    parts: list[str] = name.split(".")
    index: int
    for index in range(1, len(parts)):
        module: str = ".".join(parts[:index])
        found: ModuleType
        try:
            found = importlib.import_module(module)
        except ImportError:
            return False
        if not hasattr(found, "__path__"):
            return True  # a module, not a package: the rest is a name in it
    return True


def _callable(name: str) -> bool | None:
    """Resolve a table entry here.

    Returns:
      Whether it's callable, or `None` if it isn't there.

    """
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", DeprecationWarning)  # a deprecated module, still there
        try:
            return callable(cast("object", pkgutil.resolve_name(name)))
        except (AttributeError, ImportError):
            return None


def test_classes_and_what_returns_them_are_certain() -> None:
    """A standard-library class's call, or a function or classmethod returning one, isn't a guess."""
    source: str = textwrap.dedent(
        """\
        import asyncio
        import os
        import random
        import sys
        import unittest
        from datetime import datetime


        def f(path: str) -> None:
            a = asyncio.Lock()
            b = unittest.TestLoader()
            c = os.stat(path)
            d = random.random()
            e = datetime.fromisoformat(path)
            g = sys.intern(path)
        """,
    )
    fixed: dict[str, tuple[str | None, bool]] = {
        o.name: (o.fix, o.unsafe) for o in check_source(source) if o.code == UNANNOTATED
    }
    assert fixed == {
        "a": ("asyncio.Lock", False),
        "b": ("unittest.TestLoader", False),
        "c": ("os.stat_result", False),
        "d": ("float", False),  # a method of the module's own `Random`, bound to a name
        "e": ("datetime", False),
        "g": ("str", False),  # its `LiteralString` overload is a `str` too
    }


def test_what_python_versions_declare_in_different_ways_is_not_typed() -> None:
    """Overloaded on some Pythons and one `def` on others, or a fixed return that became a union: no fix.

    Whether or not the file can name the class one of them returns (`EntryPoints`, bound here).
    """
    source: str = textwrap.dedent(
        """\
        import logging
        import zipimport
        from importlib.metadata import entry_points

        EntryPoints = 1


        def f(record: logging.LogRecord, handler: logging.Handler, zipped: zipimport.zipimporter) -> None:
            a = entry_points()
            b = handler.filter(record)
            c = zipped.get_resource_reader("x")
            d = handler.get_name()
        """,
    )
    fixed: dict[str, str | None] = {o.name: o.fix for o in check_source(source) if o.code == UNANNOTATED}
    assert fixed == {"a": None, "b": None, "c": None, "d": "str"}


def test_a_loop_over_a_library_instance_binds_its_elements() -> None:
    """A file's lines, an `itertools` iterator's elements, a `deque`'s: each by its class's `__iter__`."""
    source: str = textwrap.dedent(
        """\
        import collections
        import io
        import itertools
        import tarfile


        def f(path: str, names: list[str], sizes: list[int], lock: object) -> None:
            for a in open(path):
                pass
            with open(path, "rb") as binary:
                b = list(binary)
            for c in itertools.chain(names, names):
                pass
            for d, e in itertools.combinations(sizes, 2):
                pass
            g = [line.strip() for line in io.StringIO(path)]
            for h in collections.deque(sizes):
                pass
            with tarfile.open(path) as archive:
                for i in archive:
                    pass
            for j in io.StringIO:
                pass
            for k in lock:
                pass
        """,
    )
    fixed: dict[str, tuple[str | None, bool]] = {
        o.name: (o.fix, o.unsafe) for o in check_source(source) if len(o.name) == 1
    }
    assert fixed == {
        "a": ("str", False),
        "b": ("list[bytes]", False),
        "c": ("str", False),
        "d": ("int", False),
        "e": ("int", False),
        "g": ("list[str]", False),
        "h": ("int", False),
        "i": ("tarfile.TarInfo", False),
        "j": (None, False),  # the class, not an instance
        "k": (None, False),
    }


def test_a_methods_self_is_its_receivers_own_type() -> None:
    """A method declared to return a type naming `Self` gives the receiver's: `path.iterdir()`'s paths."""
    source: str = textwrap.dedent(
        """\
        import collections
        import pathlib
        from collections.abc import Generator, Iterator
        from pathlib import Path


        class Mine(Path):
            pass


        def f(
            p: Path,
            mine: Mine,
            pure: pathlib.PurePosixPath,
            names: collections.deque[str],
            bare: collections.deque,
        ) -> None:
            for a in mine.iterdir():
                pass
            for b in p.iterdir():
                pass
            c = p.iterdir()
            d = list(p.glob("*"))
            e = sorted(pure.parents)
            g = names.copy()
            h = bare.copy()
            i = p.rglob("*.py")
        """,
    )
    fixed: dict[str, tuple[str | None, bool]] = {
        o.name: (o.fix, o.unsafe) for o in check_source(source) if len(o.name) == 1
    }
    assert fixed == {
        "a": ("Mine", False),  # a class under `Path`: its own
        "b": ("Path", False),
        "c": ("Generator[Path]", False),
        "d": ("list[Path]", False),
        "e": ("list[pathlib.PurePosixPath]", False),  # `parents`, a property: a `Sequence[Self]`
        "g": ("collections.deque[str]", False),
        "h": (None, False),  # a generic class named bare isn't written
        "i": ("Iterator[Path]", False),  # a `Generator` before Python 3.13: an `Iterator` on each
    }


def _known(source: str, *, planned: bool = True) -> Known:
    """Read what a module imports, as `--fix` would.

    Returns:
      What's known of it.

    """
    tree: ast.Module = ast.parse(textwrap.dedent(source))
    plan: ImportPlan | None = imports.plan(tree) if planned else None
    return Known({}, frozenset(), {}, {}, names=LibraryNames(frozenset(), stdlib.origins(tree), plan))


_CALL: Final = cast("ast.Call", ast.parse("x.m()", mode="eval").body)


@pytest.mark.parametrize(
    ("source", "receiver", "name", "call", "expected"),
    [
        ("import argparse", "argparse.ArgumentParser", "prog", None, "str"),
        ("import argparse", "argparse.ArgumentParser", "add_argument", _CALL, "argparse.Action"),
        ("from datetime import datetime", "datetime", "astimezone", _CALL, "datetime"),
        ("from datetime import datetime", "datetime", "year", None, "int"),
        ("import asyncio", "asyncio.locks.Lock", "locked", _CALL, "bool"),  # an alias of `asyncio.Lock`
        ("import io", "io.TextIOWrapper", "read", _CALL, "str"),  # a generic class's, from `TextIOBase`
        ("import io", "io.BufferedReader", "readlines", _CALL, "list[bytes]"),
        ("import io", "io.TextIOWrapper", "encoding", None, "str"),
        ("import argparse", "argparse.ArgumentParser", "prog", _CALL, None),  # not a method
        ("import argparse", "argparse.ArgumentParser", "nothing", None, None),
        ("import argparse", "Box", "prog", None, None),
        ("import argparse", "list[int]", "pop", _CALL, None),
    ],
)
def test_a_library_class_member_is_typed(
    source: str,
    receiver: str,
    name: str,
    call: ast.Call | None,
    expected: str | None,
) -> None:
    """An attribute or a method's return, of a class the module names through its imports."""
    found: Inference | None = stdlib.library_member(receiver, name, call, _known(source))
    assert (None if found is None else found.annotation) == expected
    assert found is None or found.kinds == {"stdlib"}


def test_a_library_class_is_found_through_an_import_fix_adds() -> None:
    """A receiver typed by a class `--fix` is importing resolves through that import too."""
    known: Known = _known("x = 1")
    assert known.names.plan is not None
    spelled: str | None = known.names.plan.spell("pathlib.Path")
    found: Inference | None = stdlib.library_member("Path", "stat", _CALL, known)
    # Imported the same way: `from os import stat_result`.
    assert [spelled, None if found is None else found.annotation] == ["Path", "stat_result"]


def test_a_library_class_member_needs_a_plan_to_name_a_class() -> None:
    """Without an import plan, a member giving a class isn't typed; one giving a builtin still is."""
    known: Known = _known("import argparse", planned=False)
    assert stdlib.library_member("argparse.ArgumentParser", "add_argument", _CALL, known) is None
    found: Inference | None = stdlib.library_member("argparse.ArgumentParser", "prog", None, known)
    assert [None if found is None else found.annotation] == ["str"]
