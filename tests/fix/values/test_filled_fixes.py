# SPDX-License-Identifier: MIT
"""`--fix` for an empty container filled later in its function (a guess)."""

import textwrap
from typing import Final, TypeAlias

from constricter import Checks, FixPolicy, Offence, check_source

# Each offence's fix and whether it's a guess.
_Fixed: TypeAlias = dict[str, tuple[str | None, bool]]
UNANNOTATED: Final = "LVA001"
SOURCE: Final = """
def f(items: list[int], names: list[str], pairs: dict[str, int], other) -> list[str]:
    a = []
    for i in items:
        a.append(i)
    b = {}
    for n in names:
        b[n] = len(n)
    c = set()
    c.add("x")
    c.discard("y")
    d = []
    d.append(1)
    d.append("x")
    e = []
    e.extend(items)
    e.extend(range(3))
    g = []
    g.append(1)
    other(g)
    h = list()
    h.insert(0, "x")
    h.sort()
    k = []

    def inner() -> None:
        k.append(1)

    m = []
    m.append(1)
    p = dict()
    _ = p.setdefault("a", 1.5)
    q = {}
    q["a"] += 1
    r = []
    s = r
    t = []
    t[0:1] = [1]
    u = []
    v = []
    v.append(other)
    w = {}
    w[other] = 1
    x = []
    x.append(1, 2)
    z = []
    z.append(1)
    z = []
    A = set()
    A.update(names)
    A.add("x")
    B = {}
    B.update(pairs)
    B["k"] = 1
    C = []
    C.extend(items)
    C.append("x")
    D = []
    D.extend(other)
    E = {}
    E.update(k=1)
    F = set()
    F.update(names, names)
    G = {}
    G.update(names)
    print(len(m), ", ".join(h), sorted(a), c if c else None, f"{p}", not u, [y for y in m], m[0])
    return h
"""


def _fixed(checks: Checks | None = None) -> _Fixed:
    found: list[Offence] = check_source(textwrap.dedent(SOURCE), checks=checks or Checks())
    return {o.name: (o.fix, o.unsafe) for o in found if o.code == UNANNOTATED and len(o.name) == 1}


def test_an_empty_container_is_typed_by_what_is_added() -> None:
    """Every fill typed and agreeing, every other use unable to add: a guess; anything else, nothing."""
    fixed: _Fixed = _fixed()
    assert {name: fix for name, fix in fixed.items() if fix[0]} == {
        "a": ("list[int]", True),
        "b": ("dict[str, int]", True),
        "c": ("set[str]", True),
        "e": ("list[int]", True),  # `extend`: its argument's elements
        "h": ("list[str]", True),
        "m": ("list[int]", True),
        "p": ("dict[str, float]", True),
        "A": ("set[str]", True),  # `update`, a set's
        "B": ("dict[str, int]", True),  # and a `dict`'s: another's keys and values
    }
    # Mixed types (d), passed elsewhere (g), a nested function (k), `+=` into it (q), aliased (r), a
    # slice (t), never filled (u), an unknown element (v) or key (w), a bad call (x), rebound (z);
    # `extend` of other elements (C) or unknown ones (D), `update` by keyword (E), with two
    # arguments (F), or with what isn't a `dict` (G).
    assert {name for name, fix in fixed.items() if not fix[0]} >= set("dgkqrtuvwxzCDEFG")


def test_what_the_function_narrows_isnt_the_elements_type() -> None:
    """A name added where a test has narrowed it has another type there than it's declared."""
    source: str = """
    def g(items: list[int | str], flags: list[bool]):
        kept = []
        whole = []
        seen = []
        for item in items:
            whole.append(len(items))
            if isinstance(item, int):
                kept.append(item)
        for flag in flags:
            seen.append(flag)
    """
    found: list[Offence] = check_source(textwrap.dedent(source))
    assert {o.name: o.fix for o in found if o.name in {"kept", "whole", "seen"}} == {
        "kept": None,
        "whole": "list[int]",
        "seen": "list[bool]",
    }


def test_a_use_that_cannot_add_leaves_it_typed() -> None:
    """An operand, an unpacking, any `join`'s argument and a returned tuple's part only read it."""
    source: str = """
    def g(sep: str):
        a = []
        a.append("x")
        b = []
        b.append(1)
        c = []
        c.append(1)
        d = []
        d.append(1)
        e = []
        e.append(1)
        pair = (e, 1)
        print(sep.join(a), b + [2], [*c])
        return d, len(a)
    """
    found: list[Offence] = check_source(textwrap.dedent(source))
    assert {o.name: o.fix for o in found if len(o.name) == 1} == {
        "a": "list[str]",
        "b": "list[int]",
        "c": "list[int]",
        "d": "list[int]",
        "e": None,  # in a tuple bound to a name: aliased
    }


def test_it_is_trusted_or_ignored_as_a_mechanism() -> None:
    """`unsafe-fix-select = ["filled"]` makes it certain; `fix-ignore = ["filled"]` drops it."""
    assert _fixed(Checks(fixes=FixPolicy(unsafe_select=frozenset({"filled"}))))["a"] == ("list[int]", False)
    assert _fixed(Checks(fixes=FixPolicy(ignore=frozenset({"filled"}))))["a"] == (None, False)


def test_a_local_bound_to_it_that_only_reads_it_leaves_it_typed() -> None:
    """`alias = x`: every use of the alias reads; one that adds, or a nested scope's, leaves it alone."""
    source: str = """
    class Box:
        def __init__(self) -> None:
            self.items = []
            self.loud = []

        def add(self, x: int) -> None:
            self.items.append(x)
            self.loud.append(x)

        def show(self) -> int:
            items = self.items
            loud = self.loud
            loud.append(2)
            return len(items)


    def g() -> int:
        a = []
        a.append("x")
        read = a
        b = []
        b.append(1)
        grown = b
        grown.append(2)
        c = []
        c.append(1)
        seen = c
        d = []
        d.append(1)
        unused = d
        return len(read) + len([lambda: seen])
    """
    found: list[Offence] = check_source(textwrap.dedent(source))
    assert {o.name: o.fix for o in found} == {
        "a": "list[str]",
        "read": "list[str]",
        "d": "list[int]",
        "unused": "list[int]",
        "items": "list[int]",  # `self.items`, by its class's fills
        **dict.fromkeys(("b", "grown", "c", "seen", "loud")),
    }


_PASSED: Final = """
from typing import Any


def add(names: list[str], extra: str) -> None:
    names.append(extra)


async def collect(*, into: list[int]) -> None:
    into.append(1)


def index(table: dict[str, int], /, seen: set[bytes]) -> None:
    pass


def loose(names, vague: list[Any], many: "list[str]", *, items: tuple[int, ...] = ()) -> None:
    pass


def spread(*names: list[str]) -> None:
    pass


@decorated
def wrapped(names: list[str]) -> None:
    pass


def twice(names: list[str]) -> None:
    pass


def twice(names: list[int]) -> None:
    pass


class Holder:
    pass


def run(flag: bool, add_local: int) -> None:
    names = []
    add(names, "a")
    nums = []
    collect(into=nums)
    table = {}
    seen = set()
    index(table, seen=seen)
    both = []
    add(both, "a")
    both.append("b")
    clash = []
    add(clash, "a")
    clash.append(1)
    lost = []
    loose(lost, [], [])
    vague = []
    loose(1, vague, [])
    quoted = []
    loose(1, [], quoted)
    wrong = {}
    add(wrong, "a")
    by_position = []
    index(by_position, set())
    starred = []
    add(*[1], starred)
    varied = []
    spread(varied)
    hidden = []
    wrapped(hidden)
    redefined = []
    twice(redefined)
    unknown = []
    missing(unknown)
    named = []
    add(named, extra=named)
    nested = []
    add((nested, 1), "a")
    by_name = []
    add(extra="a", names=by_name)
    unpacked = []
    add(**{"names": unpacked})
"""


def test_an_empty_container_is_typed_by_the_parameter_it_is_passed_to() -> None:
    """A checked function's, declared a container of its kind; with its fills, where they agree."""
    found: list[Offence] = check_source(textwrap.dedent(_PASSED))
    assert {o.name: (o.fix, o.unsafe) for o in found} == {
        "names": ("list[str]", True),
        "nums": ("list[int]", True),
        "table": ("dict[str, int]", True),
        "seen": ("set[bytes]", True),
        "both": ("list[str]", True),
        "by_name": ("list[str]", True),
        # A fill of another type; a parameter that says nothing, or something vague or quoted.
        **dict.fromkeys(("clash", "lost", "vague", "quoted"), (None, False)),
        # Another kind of container, a position only a keyword could fill, arguments unpacked.
        **dict.fromkeys(("wrong", "by_position", "starred", "unpacked"), (None, False)),
        # A function that takes any number, is decorated, defined twice, or isn't the module's.
        **dict.fromkeys(("varied", "hidden", "redefined", "unknown"), (None, False)),
        # Passed twice, once as what the parameter isn't; and inside another value.
        **dict.fromkeys(("named", "nested"), (None, False)),
    }
    kinds: dict[str, frozenset[str]] = {o.name: o.edit.kinds for o in found if o.edit is not None}
    assert kinds["names"] == {"filled"}
    shadowed: str = textwrap.dedent(_PASSED).replace("add_local: int", "add: int")
    assert {o.name: o.fix for o in check_source(shadowed)}["names"] is None  # a local of that name
