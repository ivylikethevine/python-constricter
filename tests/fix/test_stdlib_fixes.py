# SPDX-License-Identifier: MIT
"""`--fix` for the standard library, from tables generated from typeshed, resolved through the imports."""

import ast
import pkgutil
import sys
import textwrap
import warnings
from typing import Final, cast

import pytest

from constricter import Offence, check_source
from constricter.fix import imports, stdlib
from constricter.fix.known import ImportPlan, Inference, Known, LibraryNames

UNANNOTATED: Final = "LVA001"
PYPY: Final = "pypy"
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
"""


def test_a_table_function_is_typed_however_it_is_imported() -> None:
    """`import m`, `import m as a` and `from m import f` all resolve; a same-named function doesn't.

    An `AnyStr` function is typed only when its arguments agree on `str` or `bytes`; an environment
    lookup is `str | None`, or `str` with a `str` default.
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
        "g": (None, False),
        "h": ("str | None", False),
        "i": ("str", False),
        "j": (None, False),
        "k": (None, False),
        "m": ("int", False),
        "n": (None, False),  # a keyword argument decides nothing
        "r": ("int", False),  # but not a fixed return's
        "p": (None, False),  # `str` and `bytes` together: no `AnyStr`
        "q": (None, False),
    }


@pytest.mark.parametrize("name", sorted(stdlib.KNOWN))
def test_every_table_function_exists(name: str) -> None:
    """Each table entry names a real standard-library function, as Linux CPython has it.

    The tables are what each minor release's latest patch release has, on every platform typeshed
    covers. CI's Linux jobs run those patch releases, so they must have every entry. Elsewhere an
    entry may be missing, and is skipped: PyPy lacks some of CPython's own (`tracemalloc`,
    `gc.get_count`), Windows has no `curses`, and macOS and Windows stop at the last patch release
    with an installer (3.11.9, 3.12.10), before security releases' additions like
    `tarfile.LinkFallbackError`. What's there must still be callable.
    """
    found: bool | None = _callable(name)
    if found is None and (sys.implementation.name == PYPY or sys.platform != LINUX):
        pytest.skip("not in this platform's build")
    assert found


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
