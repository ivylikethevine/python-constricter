# SPDX-License-Identifier: MIT
"""`--fix` for calls to unannotated functions whose `return`s decide their type."""

import textwrap
from typing import Final, TypeAlias

from constricter import Checks, FixPolicy, Offence, check_source

# Each offence's fix and whether it's a guess.
_Fixed: TypeAlias = dict[str, tuple[str | None, bool]]
MADE: Final = "made"
SOURCE: Final = """
import functools


def count(items):
    total = 0
    for item in items:
        total += 1
    return total


def label(flag: bool):
    if flag:
        return "yes"
    else:
        return "no"


def maybe(flag: bool):
    if flag:
        return 1


def mixed(flag: bool):
    if flag:
        return 1
    return "x"


def gen():
    yield 1
    return 2


def bare(flag: bool):
    if flag:
        return
    raise ValueError


def guarded(value):
    try:
        return int(value)
    except ValueError:
        raise
    finally:
        pass


def tried(value):
    try:
        number = int(value)
    except ValueError:
        return 0
    else:
        return number


def held(lock):
    with lock:
        return 1.5


@functools.cache
def cached():
    return 1


def twice():
    return 1


def twice():
    return 2


def declared() -> float:
    return 1


async def later():
    return 1


def boxed():
    return Box()


def first(items: list[int]):
    for item in items:
        return item


class Box:
    def size(self):
        return 3

    def nested(self):
        def inner():
            yield 1

        return "x"


def use(box: Box) -> None:
    a = count([])
    b = label(True)
    c = maybe(True)
    d = mixed(True)
    e = gen()
    g = bare(True)
    h = guarded("1")
    i = tried("1")
    j = held(None)
    k = cached()
    m = twice()
    n = declared()
    p = later()
    q = boxed()
    r = box.size()
    s = box.nested()
    t = first([])
"""


def _fixed(checks: Checks | None = None) -> _Fixed:
    found: list[Offence] = check_source(textwrap.dedent(SOURCE), checks=checks or Checks())
    return {o.name: (o.fix, o.unsafe) for o in found if len(o.name) == 1 and o.line > SOURCE.count("\n") - 21}


def test_a_function_is_typed_by_its_returns() -> None:
    """Every `return` giving one certain type, and no way to fall off its end: its calls are typed."""
    assert _fixed() == {
        "a": ("int", False),
        "b": ("str", False),
        "c": (None, False),  # can fall off its end
        "d": (None, False),  # two types
        "e": (None, False),  # a generator
        "g": (None, False),  # a bare `return`
        "h": ("int", False),  # `try`, its handler re-raising
        "i": ("int", False),  # `try`/`except`/`else`
        "j": ("float", False),  # `with`
        "k": (None, False),  # decorated
        "m": (None, False),  # redefined
        "n": ("float", False),  # its declaration, as before
        "p": (None, False),  # `async`
        "q": ("Box", True),  # a guessed `return` value (`Box()`): its calls are guesses too
        "r": ("int", True),  # a method: a subclass may override it
        "s": ("str", True),  # a nested generator is its own function
        "t": (None, False),  # its loop can end without returning
    }


def test_a_methods_guess_rests_on_returned() -> None:
    """Trusting `returned` makes a method's type certain; trusting `constructor` doesn't."""
    trusted: _Fixed = _fixed(Checks(fixes=FixPolicy(unsafe_select=frozenset({"returned"}))))
    assert trusted["r"] == ("int", False)
    assert _fixed(Checks(fixes=FixPolicy(unsafe_select=frozenset({"constructor"}))))["r"] == ("int", True)


def test_nothing_called_needs_no_second_pass() -> None:
    """A module that never calls its typed functions is checked once, and gets the same result."""
    source: str = "def one():\n    return 1\n\n\ndef f() -> None:\n    x = 2\n"
    assert [(o.name, o.fix) for o in check_source(source)] == [("x", "int")]


def test_a_method_returning_a_guess_rests_on_both() -> None:
    """A method whose `return` is a guess (`Thing()`) makes its calls rest on `returned` and `constructor`."""
    source: str = (
        "class Maker:\n    def make(self):\n        return Thing()\n\n\n"
        "def f(maker: Maker) -> None:\n    made = maker.make()\n"
    )
    only_returned: FixPolicy = FixPolicy(unsafe_select=frozenset({"returned"}))
    both: FixPolicy = FixPolicy(unsafe_select=frozenset({"returned", "constructor"}))
    made: list[Offence] = [
        o for o in check_source(source, checks=Checks(fixes=only_returned)) if o.name == MADE
    ]
    assert [(o.fix, o.unsafe) for o in made] == [("Thing", True)]
    trusted: list[Offence] = [o for o in check_source(source, checks=Checks(fixes=both)) if o.name == MADE]
    assert [(o.fix, o.unsafe) for o in trusted] == [("Thing", False)]


def test_a_long_chain_is_typed_in_call_order() -> None:
    """Callees are checked before their callers: a chain of unannotated calls is typed whole, however long."""
    links: str = "".join(f"def f{n}():\n    return f{n + 1}()\n\n\n" for n in range(30))
    source: str = (
        f"{links}def f30():\n    return 1\n\n\ndef use() -> None:\n    near = f25()\n    far = f0()\n"
    )
    fixed: dict[str, str | None] = {o.name: o.fix for o in check_source(source)}
    assert fixed == {"near": "int", "far": "int"}


def test_a_cycle_is_typed_in_rounds() -> None:
    """Two functions calling each other: the one checked before the other was typed learns it in a round.

    `first` returns what `second` does; `second` returns an `int` of its own, and calls `first` too:
    whichever order the cycle is checked in, `first` is typed.
    """
    source: str = textwrap.dedent(
        """
        def first():
            return second(False)


        def second(again: bool):
            if again:
                first()
            return 1


        def use() -> None:
            a = first()
            b = second(True)
        """,
    )
    assert {o.name: o.fix for o in check_source(source)} == {"a": "int", "b": "int"}


def test_a_module_body_call_is_typed_with_all_scopes() -> None:
    """With `all-scopes`, a module-level call to an unannotated function is typed too (LVA004)."""
    source: str = "def one():\n    return 1\n\n\nLIMIT = one()\n"
    fixed: list[tuple[str, str | None]] = [
        (o.name, o.fix) for o in check_source(source, checks=Checks(all_scopes=True))
    ]
    assert fixed == [("LIMIT", "int")]


def test_a_late_typed_return_is_typed_in_a_round() -> None:
    """A function typed only once finished (`None`, then `int`) types its calls in a round.

    A module body's call to it, checked before that round, is checked again too.
    """
    source: str = textwrap.dedent(
        """
        def late(n: int):
            x = None
            if n:
                x = n
            return x


        def use() -> None:
            a = late(1)


        b = late(2)
        """,
    )
    everywhere: Checks = Checks(all_scopes=True)
    fixed: dict[str, str | None] = {o.name: o.fix for o in check_source(source, checks=everywhere)}
    assert fixed == {"x": "int | None", "a": "int | None", "b": "int | None"}
    # The body's statements are looked through (a class's, an `if`'s, before any function), and
    # without a call there, left alone.
    elsewhere: str = "class C:\n    if True:\n        c = 1\n" + source.replace("b = late(2)", "")
    assert {o.name: o.fix for o in check_source(elsewhere, checks=everywhere)} == {
        "x": "int | None",
        "a": "int | None",
        "c": None,
    }


def test_a_chain_on_a_late_type_stops_after_its_rounds() -> None:
    """Each round types one more link of a chain built on a late-typed return; five rounds reach five."""
    base: str = "def f0(n: int):\n    x = None\n    if n:\n        x = n\n    return x\n\n\n"
    links: str = "".join(f"def f{n}(k: int):\n    return f{n - 1}(k)\n\n\n" for n in range(1, 8))
    source: str = f"{base}{links}def use() -> None:\n    near = f3(1)\n    far = f7(1)\n"
    fixed: dict[str, str | None] = {o.name: o.fix for o in check_source(source)}
    assert fixed == {"x": "int | None", "near": "int | None", "far": None}
