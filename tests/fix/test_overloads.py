# SPDX-License-Identifier: MIT
"""`--fix` for standard-library calls whose arguments decide their type, by the signatures they match."""

import textwrap
from typing import Final

import pytest

from constricter import Offence, check_source
from constricter.fix import stdlib
from constricter.fix.stdlib import Accepts, Signature

UNANNOTATED: Final = "LVA001"
SOURCE: Final = """
import ast
import os
import re
from re import compile as rc


def f(fd: int, data: bytes, unknown, parts: list[str], options: dict[str, str]) -> None:
    a = os.listdir()
    b = os.listdir(data)
    c = os.listdir(fd)
    d = os.listdir(unknown)
    e = re.compile("x")
    g = rc(b"x")
    h = ast.parse("x")
    i = ast.parse("x", mode="eval")
    j = os.path.join(*parts)
    k = os.path.join("a", **options)
    m = os.listdir(path=".")
    n = os.listdir(".", ".")
    p = os.listdir(nothing=".")
    q = os.path.split("a/b")
    r = os.getenv("X", None)
"""
SHADOWED: Final = """
import os


def f(list) -> None:
    a = os.listdir()
"""
_EVERY: Final = "y" * 9
_T: Final = Accepts(v=_EVERY, var={"LiteralString": ["T", "str"], "bytes": ["T", "bytes"]})
FAKE: Final = [
    [
        Signature(params=[("a", "e", False, _T), ("b", "e", False, _T)], returns="T"),
    ],
]
RECEIVERS: Final = """
import re
from typing import Any


def g(p: re.Pattern[Any], q: re.Pattern[str], s: str) -> None:
    t = p.match(s)
    u = q.match(s)
"""
UNBOUND: Final = [[Signature(params=[("a", "e", False, None)], returns="tuple[U, ...]")]]
MADE_UP: Final = """
import os


def f() -> None:
    a = os.made_up("x", "y")
    b = os.made_up("x", b"y")
    c = os.unbound(1)
"""


def _fixes(source: str) -> dict[str, str | None]:
    found: list[Offence] = check_source(textwrap.dedent(source))
    return {o.name: o.fix for o in found if o.code == UNANNOTATED}


def test_a_call_is_typed_by_the_signature_its_arguments_match() -> None:
    """The first signature taking them, if every one before certainly refuses them; classes imported.

    A call that unpacks its arguments, or passes one no signature has, is left alone; a literal
    argument picks a `Literal` overload; a type variable takes the argument's type.
    """
    assert _fixes(SOURCE) == {
        "a": "list[str]",
        "b": "list[bytes]",
        "c": "list[str]",
        "d": None,  # `str` or `bytes`: unknown
        "e": "re.Pattern[str]",
        "g": "re.Pattern[bytes]",  # through `import re`
        "h": "ast.Module",
        "i": "ast.Expression",
        "j": None,
        "k": None,
        "m": "list[str]",
        "n": None,
        "p": None,
        "q": "tuple[str, str]",
        "r": "str | None",
    }


def test_a_generic_receiver_binds_its_class_type_parameters() -> None:
    """`Pattern[str]`'s methods declared for `self: Pattern[str]` apply; with `Pattern[Any]` none is sure."""
    assert _fixes(RECEIVERS) == {"t": None, "u": "re.Match[str] | None"}


def test_a_builtin_the_module_rebinds_isnt_written() -> None:
    """`list[str]` means something else where `list` is a parameter."""
    assert _fixes(SHADOWED) == {"a": None}


def test_type_variables_bind_to_one_type_or_none(monkeypatch: pytest.MonkeyPatch) -> None:
    """Two arguments binding one type variable must agree; one no argument binds leaves the call alone."""
    monkeypatch.setitem(stdlib.OVERLOADS, "os.made_up", FAKE)
    monkeypatch.setitem(stdlib.OVERLOADS, "os.unbound", UNBOUND)
    assert _fixes(MADE_UP) == {"a": "str", "b": None, "c": None}
