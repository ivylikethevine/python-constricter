# SPDX-License-Identifier: MIT
"""`--fix` for a call of a value whose type says what calling it gives: a `Callable`, a `type[C]`."""

import textwrap
from pathlib import Path
from typing import Final, TypeAlias

from constricter import Offence, check_source
from constricter.cli import schedule
from constricter.fix.index import project

# Each offence's fix and whether it's a guess.
_Fixes: TypeAlias = dict[str, tuple[str | None, bool]]
_SOURCE: Final = """
from collections.abc import Callable
from typing import Any, Self, TypeVar

T = TypeVar("T")


class Row:
    handler: Callable[[int], str]
    hooks: list[Callable[[int], str]]

    def __init__(self) -> None:
        self.callback = Row()

    def __call__(self, n: int) -> bytes:
        return b""

    @classmethod
    def make(cls) -> "Row":
        made = cls()
        return made

    @classmethod
    def clone(cls) -> Self:
        cloned = cls()
        return cloned

    def copy(self) -> Self:
        copied = type(self)()
        again = type(copied)()
        called = self(1)
        return copied

    @classmethod
    def blank(cls) -> Self:
        fresh = cls.__new__(cls)
        raw = object.__new__(Row)
        return fresh

    def plain(self, kind: type["Row"], anything: type[Any], other) -> None:
        new = kind.__new__(kind)
        newer = object.__new__(type(self))
        newest = Row.__new__(Row)
        unmade = other.__new__(other)
        vague = anything.__new__(anything)
        unknown = Row.__new__()
        odd = object.__new__(self)
        built = type(self)()
        hooked = self.hooks[0](1)
        handled = self.handler(2)
        back = self.callback(3)


def use(
    handler: Callable[[int], str],
    make: Callable[..., Row],
    kind: type[Row],
    row: Row,
    anything: Callable[..., Any],
    nothing: Callable[[], None],
    maybe: Callable[[], int] | None,
    quoted: "Callable[[], Row]",
    generic: Callable[[], T],
    other,
) -> T:
    a = handler(1)
    b = make()
    c = kind()
    d = row(1)
    e = anything()
    g = nothing()
    h = maybe()
    i = quoted()
    j = generic()
    k = other()
    m = other.attr()
    n = Row.missing(1)
    o = Row()
    p = o(1)
    return j
"""
_HANDLERS: Final = """
class Handler:
    def __call__(self, source: str, /) -> int:
        return 0

    def __enter__(self) -> bytes:
        return b""
"""
_USING: Final = """
from pkg.handlers import Handler


def use(handler: Handler) -> None:
    schema = handler("x")
    with handler as entered:
        pass
"""


def test_a_call_of_a_typed_value_is_what_its_type_gives() -> None:
    """A `Callable`'s return, the class a `type[C]` names, and what a class's `__call__` declares.

    Not a vague or `None` return, a callable that may be `None`, or a callee of no known type. What
    typed a callee that isn't a plain local is among the fix's kinds, and a guessed callee makes a
    guess.
    """
    found: list[Offence] = check_source(textwrap.dedent(_SOURCE))
    fixes: _Fixes = {o.name: (o.fix, o.unsafe) for o in found}
    assert fixes == {
        "made": ("Row", False),
        "cloned": ("Self", False),  # in a method whose signature says `Self`
        "copied": ("Self", False),
        "again": ("Self", False),
        "called": ("bytes", False),
        "fresh": ("Self", False),
        "raw": ("Row", False),
        "new": ("Row", False),
        "newer": ("Row", False),
        "newest": ("Row", False),
        "built": ("Row", False),
        "hooked": ("str", False),
        "handled": ("str", False),
        "back": ("bytes", True),  # `self.callback`, typed by its assignment
        "a": ("str", False),
        "b": ("Row", False),
        "c": ("Row", False),
        "d": ("bytes", False),
        "i": ("Row", False),
        "j": ("T", False),
        "o": ("Row", True),
        "p": ("bytes", True),
        **dict.fromkeys(("unmade", "vague", "unknown", "odd", *"eghkmn"), (None, False)),
    }
    kinds: dict[str, frozenset[str]] = {o.name: o.edit.kinds for o in found if o.edit is not None}
    assert kinds["a"] == {"call"}
    assert kinds["d"] == {"method"}
    assert kinds["handled"] == {"attribute", "call"}
    assert kinds["hooked"] == {"attribute", "call", "subscript"}
    assert kinds["copied"] == {"builtin", "call", "copy"}


def test_another_files_class_is_called_by_its_declared_call(tmp_path: Path) -> None:
    """The index passes a file what it takes of a class without naming it: `__call__`, `__enter__`."""
    name: str
    source: str
    for name, source in {"pkg/__init__.py": "", "pkg/handlers.py": _HANDLERS, "using.py": _USING}.items():
        path: Path = tmp_path / name
        path.parent.mkdir(parents=True, exist_ok=True)
        _ = path.write_text(source, encoding="utf-8")
    using: Path = tmp_path / "using.py"
    catalog: project.Index = project.index(sorted(tmp_path.rglob("*.py")))
    assert project.imported(catalog, using).classes.methods == {
        "Handler": {"__call__": "int", "__enter__": "bytes"},
    }
    found: list[Offence] = check_source(_USING, outside=schedule.outside(catalog, using, {}))
    assert {o.name: (o.fix, o.unsafe) for o in found} == {
        "schema": ("int", False),
        "entered": ("bytes", False),
    }
