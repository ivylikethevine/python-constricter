# SPDX-License-Identifier: MIT
"""`--fix` for a function or a bound method bound to a name: a `Callable[..., R]`."""

import textwrap
from typing import Final

from constricter import Checks, Offence, check_source

_SOURCE: Final = """
import functools
import json
import os.path
from collections.abc import Callable


class Item:
    def grow(self, by: int = 1) -> int:
        return by

    def loose(self, by):
        return by

    def nothing(self) -> None:
        return None


def plain(x: int, y: str = "") -> bool:
    return True


@functools.cache
def cached() -> int:
    return 1


def untyped(x):
    return 1


def use(item: Item, names: list[str], unknown) -> None:
    dump = json.dumps
    join = os.path.join
    grow = item.grow
    made = Item().grow
    func = plain
    size = len
    pop = names.pop
    parse = json.loads
    loose = item.loose
    nothing = item.nothing
    free = untyped
    klass = Item
    text = str
    lost = unknown.method
    run = cached
    run.cache_clear()
    key = lambda row: row.size
    first = lambda: 1
    const = lambda row, *rest: "x"
    shadow = lambda item: item
    held = lambda: item
    held.__name__
    print(func(1, y="a"), grow(by=2))


shared = json.dumps


class Holder:
    dump = json.dumps
"""
_DUMP: Final = "dump"
_DUMPS: Final = "dumps"
_PARSE: Final = "parse"
_NO_IMPORT: Final = "import json\n\n\ndef use() -> None:\n    dump = json.dumps\n"


def test_a_function_bound_to_a_name_is_a_callable_of_what_its_call_gives() -> None:
    """Whatever it's passed; not a class, an undeclared callee, or a name whose attribute is read."""
    fixes: dict[str, tuple[str | None, bool]] = {
        o.name: (o.fix, o.unsafe) for o in check_source(textwrap.dedent(_SOURCE))
    }
    assert fixes == {
        "dump": ("Callable[..., str]", False),
        "grow": ("Callable[..., int]", False),
        "made": ("Callable[..., int]", True),  # of a guessed receiver
        "func": ("Callable[..., bool]", False),
        "size": ("Callable[..., int]", False),
        "pop": ("Callable[..., str]", False),
        "first": ("Callable[[], int]", False),  # a lambda that takes nothing, by its body
        "const": ("Callable[..., str]", False),
        # `os.path.join`'s arguments decide its type, and `json.loads` gives an `Any`.
        **dict.fromkeys(("join", "parse", "loose", "nothing", "free"), (None, False)),
        **dict.fromkeys(("klass", "text", "lost", "run", "key"), (None, False)),
        # A body resting on a parameter, and a name whose attribute is read.
        **dict.fromkeys(("shadow", "held"), (None, False)),
    }
    kinds: dict[str, frozenset[str]] = {
        o.name: o.edit.kinds for o in check_source(textwrap.dedent(_SOURCE)) if o.edit is not None
    }
    assert kinds["dump"] == {"callable", "stdlib"}
    assert kinds["grow"] == {"callable", "method"}


def test_a_callable_of_any_is_written_where_vague_allows() -> None:
    """`json.loads` returns `Any`: one vague part, inside a type that says the rest."""
    vague: list[Offence] = check_source(textwrap.dedent(_SOURCE), checks=Checks(vague=1))
    assert [o.fix for o in vague if o.name == _PARSE] == ["Callable[..., Any]"]


def test_callable_is_imported_where_the_module_doesnt() -> None:
    """From `collections.abc`, with the fix."""
    imports: list[tuple[str, ...]] = [o.edit.imports for o in check_source(_NO_IMPORT) if o.edit is not None]
    assert imports == [("from collections.abc import Callable",)]
    taken: str = _NO_IMPORT.replace("import json\n", "import json\n\nCallable = 1\n")
    assert [o.fix for o in check_source(taken) if o.name == _DUMP] == [None]  # no way to name it


_BODIES: Final = """
import json

dump = json.dumps
keep = json.dumps
first = lambda: 1
a = b = json.dumps


class Plain:
    dumps = json.dumps
    one = lambda: 1

    def size(self) -> int:
        return 1

    def loose(self):
        return 1

    length = size
    other = loose
    missing = unknown
    again = json.dumps
    again = json.dumps


@decorated
class Model:
    dumps = json.dumps


print(keep.__name__)
"""


def test_a_module_or_plain_class_name_bound_to_a_function_is_a_callable() -> None:
    """A class's as a guess, as its variables are, a method of its own too; not where an attribute is read."""
    found: list[Offence] = check_source(textwrap.dedent(_BODIES), checks=Checks(all_scopes=True))
    fixes: dict[str, tuple[str | None, bool]] = {o.name: (o.fix, o.unsafe) for o in found}
    assert fixes == {
        "dump": ("Callable[..., str]", False),
        "first": ("Callable[[], int]", False),
        "length": ("Callable[..., int]", True),
        "one": ("Callable[[], int]", True),
        "again": ("Callable[..., str]", True),
        # An attribute of it read, a chained assignment's, and a class that isn't plain.
        **dict.fromkeys(("keep", "a", "b", "other", "missing"), (None, False)),
        "dumps": (None, False),  # `Model`'s, after `Plain`'s
    }
    kinds: dict[str, frozenset[str]] = {o.name: o.edit.kinds for o in found if o.edit is not None}
    assert kinds["length"] == {"callable", "member", "method"}
    plain: list[Offence] = [o for o in found if o.name == _DUMPS]
    assert [(o.fix, o.unsafe) for o in plain] == [("Callable[..., str]", True), (None, False)]


_LISTED: Final = """
from typing import TypeVar

T = TypeVar("T")


def helper(a: int, b: str) -> bytes:
    return b""


def defaulted(a: int, b: str = "") -> bytes:
    return b""


def generic(a: T) -> int:
    return 1


def nothing() -> int:
    return 1


class Item:
    def grow(self, by: int, /) -> float:
        return 1.5

    @staticmethod
    def make(by: int) -> int:
        return by


def use(item: Item, args: tuple[int, str], unknown) -> None:
    by_position = helper
    by_keyword = helper
    starred = helper
    short = helper
    uncalled = helper
    optional = defaulted
    variable = generic
    empty = nothing
    method = item.grow
    static = item.make
    print(by_position(1, "a"), by_keyword(1, b="a"), starred(*args), short(1), empty(), method(2))
"""


def test_a_callables_parameters_are_listed_where_its_function_takes_them_by_position() -> None:
    """All annotated, with no default; and every call through the name passes as many, none by keyword."""
    found: list[Offence] = check_source(textwrap.dedent(_LISTED))
    assert {o.name: o.fix for o in found} == {
        "by_position": "Callable[[int, str], bytes]",
        "by_keyword": "Callable[..., bytes]",
        "starred": "Callable[..., bytes]",
        "short": "Callable[..., bytes]",
        "uncalled": "Callable[[int, str], bytes]",
        "optional": "Callable[..., bytes]",
        "variable": "Callable[..., int]",
        "empty": "Callable[[], int]",
        "method": "Callable[[int], float]",
        "static": "Callable[..., int]",
    }


_CALLED: Final = """
def use(names: list[str], flag: bool, unknown) -> None:
    double = lambda x: x * 2
    upper = lambda s: s.upper()
    add = lambda x, y, /: x + y
    mixed = lambda x: x
    passed = lambda x: x
    keyword = lambda x: x
    defaulted = lambda x, y=1: x + y
    starred = lambda *xs: xs
    inner = lambda x: x
    rebound = lambda x: x
    untyped = lambda x: x
    opaque = lambda x: x.missing
    made = lambda box: box
    again = lambda x: x
    again = lambda x: x
    n = 1
    if flag:
        n = 2
    print(double(3), upper("a"), add(1, 2.5), add(2, 3.5), mixed(1), mixed("a"), passed)
    print(keyword(x=1), defaulted(1), starred(1), [inner(i) for i in (lambda: inner(1))()])
    print(rebound(n), untyped(unknown), opaque(1), made(Box()), again(1))
    doubled = double(4)
"""


def test_a_lambda_resting_on_its_parameters_is_typed_by_what_its_calls_pass() -> None:
    """Every use a call, each parameter given one type by position: a guess, as a caller's types are."""
    found: list[Offence] = check_source(textwrap.dedent(_CALLED))
    assert {o.name: (o.fix, o.unsafe) for o in found} == {
        "double": ("Callable[..., int]", True),
        "upper": ("Callable[..., str]", True),
        "add": ("Callable[..., float]", True),
        "made": ("Callable[..., Box]", True),
        "doubled": ("int", True),  # by the lambda's type, on a second look
        "n": ("int", False),
        **dict.fromkeys(("mixed", "passed", "keyword", "defaulted", "starred", "inner"), (None, False)),
        **dict.fromkeys(("rebound", "untyped", "opaque", "again"), (None, False)),
    }
    kinds: dict[str, frozenset[str]] = {o.name: o.edit.kinds for o in found if o.edit is not None}
    assert kinds["upper"] == {"callable", "callers", "literal", "method"}
    assert kinds["made"] >= {"callers", "constructor"}
    module: str = "import collections.abc\n\nCallable = 1\n\n" + textwrap.dedent(_CALLED)
    assert {o.name: o.fix for o in check_source(module)}["double"] is None  # no way to name it
