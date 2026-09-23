# SPDX-License-Identifier: MIT
"""`--fix` for standard-library functions with a builtin result, resolved through the imports."""

import pkgutil
import textwrap
from typing import Final, cast

import pytest

from constricter import Offence, check_source
from constricter.fix import stdlib

UNANNOTATED: Final = "LVA001"
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
        "p": (None, False),  # `str` and `bytes` together: no `AnyStr`
        "q": (None, False),
    }


@pytest.mark.parametrize("name", sorted(stdlib.KNOWN))
def test_every_table_function_exists(name: str) -> None:
    """Each table entry names a real standard-library function, on every platform CI runs."""
    assert callable(cast("object", pkgutil.resolve_name(name)))
