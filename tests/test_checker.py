"""The rule itself (constricter.checker): what it reports and what it exempts."""

import textwrap
from pathlib import Path

import pytest

from constricter import Offence, check_source

EXEMPT = """
import os
from os import path as p

G = 0


class Holder:
    count: int = 0

    def method(self, items: list[int]) -> int:
        total: int = 0
        for i in items:
            total += i
        return total


async def coroutine(items: list[str], *args: str, **kwargs: str) -> str:
    global G
    G = 1
    import re
    match items:
        case [first, *rest] if first:
            pass
        case {**others}:
            pass
        case str() as whole:
            pass
        case _:
            pass
    try:
        raise ValueError
    except ValueError as e:
        pass
    try:
        raise TypeError
    except* TypeError as eg:
        pass
    _ = print()
    with open(os.devnull):
        pass
    joined: str = ",".join(x for x in items)
    n: int
    more: list[int]
    n, *more = 1, 2, 3
    async for item in aiter(items):
        pass
    fh: object
    async with open(os.devnull) as fh:
        pass
    while (n := n - 1) > 0:
        pass
    m: re.Match[str] | None
    assert (m := re.match("x", joined)) or True
    type Alias = list[int]
    square: object = lambda v: (w := v * v)
    total: int = 0
    total += 1

    def nested(value: int) -> int:
        inner: int = value + n
        return inner

    if joined:
        return joined
    else:
        return str(m)
"""

OFFENDING = """
def broken(items: list[int]) -> None:
    plain = 1
    a: int
    a, b = 1, 2
    first, *rest = items
    if (count := len(items)) > 0:
        pass
    with open("x") as fh:
        pass
    plain = 2
    a = count
"""


def _check(source: str) -> list[Offence]:
    return check_source(textwrap.dedent(source))


def test_exempt_bindings_and_declared_locals_pass() -> None:
    assert _check(EXEMPT) == []


def test_each_unannotated_first_binding_is_reported_once_at_its_name() -> None:
    assert _check(OFFENDING) == [
        Offence(3, 4, "plain"),
        Offence(5, 7, "b"),
        Offence(6, 4, "first"),
        Offence(6, 12, "rest"),
        Offence(7, 8, "count"),
        Offence(9, 22, "fh"),
    ]


def test_the_message_names_the_variable() -> None:
    assert Offence(1, 0, "x").message == "local variable 'x' is not annotated where it's first bound"


@pytest.mark.parametrize(
    ("source", "expected"),
    [
        pytest.param(
            """
            def outer() -> None:
                class Local:
                    def method(self) -> None:
                        x = 1
            """,
            [Offence(5, 12, "x")],
            id="method-of-a-class-defined-in-a-function",
        ),
        pytest.param(
            """
            if True:
                def conditional() -> None:
                    x = 1
            try:
                import os
            except ImportError:
                def fallback() -> None:
                    y = 1
            """,
            [Offence(4, 8, "x"), Offence(9, 8, "y")],
            id="functions-inside-module-level-blocks",
        ),
        pytest.param(
            """
            class Outer:
                class Inner:
                    def method(self) -> None:
                        x = 1
            """,
            [Offence(5, 12, "x")],
            id="nested-classes",
        ),
        pytest.param(
            """
            def f(items: list[int]) -> None:
                values: list[int] = [y for x in items if (y := x)]
            """,
            [Offence(3, 46, "y")],
            id="walrus-in-a-comprehension-binds-the-function-local",
        ),
        pytest.param(
            """
            def f() -> None:
                def g() -> None:
                    x = 1
                x: int = 2
            """,
            [Offence(4, 8, "x")],
            id="nested-function-is-its-own-scope",
        ),
        pytest.param(
            """
            def f(flag: bool) -> None:
                if flag:
                    x = 1
                else:
                    x = 2
            """,
            [Offence(4, 8, "x")],
            id="first-binding-in-source-order",
        ),
        pytest.param(
            """
            def f(flag: bool) -> None:
                try:
                    pass
                except ValueError:
                    a = 1
                else:
                    b = 2
                finally:
                    c = 3
            """,
            [Offence(6, 8, "a"), Offence(8, 8, "b"), Offence(10, 8, "c")],
            id="every-try-block",
        ),
        pytest.param(
            """
            def f(obj: object) -> None:
                obj.attr = 1
                obj[0] = 2
            X = 1
            class C:
                y = 2
            """,
            [],
            id="attributes-subscripts-module-and-class-bodies",
        ),
    ],
)
def test_scopes(source: str, expected: list[Offence]) -> None:
    assert _check(source) == expected


def test_its_own_source_follows_the_rule() -> None:
    package: Path = Path(__file__).resolve().parents[1] / "src" / "constricter"
    sources: list[Path] = sorted(package.glob("*.py")) + sorted(Path(__file__).parent.glob("*.py"))
    assert len(sources) > 5
    offences: list[str] = [f"{p}:{o.line}: {o.name}" for p in sources for o in check_source(p.read_text())]
    assert offences == []
