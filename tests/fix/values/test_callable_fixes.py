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
