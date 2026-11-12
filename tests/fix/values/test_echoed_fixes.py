"""`--fix` for calls of a method that returns one of its parameters as it's given."""

import textwrap
from typing import Final, TypeAlias

from constricter import Checks, FixPolicy, Offence, check_source

# Each offence's fix, the mechanisms that decided it, and whether it's a guess.
_Fixed: TypeAlias = dict[str, tuple[str | None, frozenset[str], bool]]
KIND: Final = "echoed"
SOURCE: Final = """
class Reader:
    def run(self, raw: bytes) -> None:
        number = self.pick(3)
        named = self.pick(fallback="x")
        flagged = self.pick(b"", strict=True)
        keyed = self.keyed(value=raw)
        hooked = self.hook(raw)
        copied = self.pick(number)
        defaulted = self.pick()
        starred = self.pick(*[1])
        spread = self.keyed(**{"value": 1})
        untyped = self.pick(self.unknown)
        rebound = self.rebound(1)
        annotated = self.annotated(1)
        either = self.either(1, "x")
        gathered = self.gathered(1)
        made = self.made(1)
        first = self.first(1)

    def pick(self, fallback=None, strict=False):
        if strict:
            return fallback
        return fallback

    def keyed(self, *, value):
        return value

    def hook(self, value):
        return value

    def rebound(self, value):
        value = str(value)
        return value

    def annotated(self, value: int):
        return value

    def either(self, first, second):
        if first:
            return first
        return second

    def gathered(self, *values):
        return values

    @staticmethod
    def made(value):
        return value

    def first(self):
        return self


class Sub(Reader):
    def more(self) -> None:
        inherited = self.pick(b"")
        own = self.hook(1)

    def hook(self, value):
        return [value]


def outside(reader: Reader) -> None:
    passed = reader.pick(1.5)
"""


def _fixed(source: str, checks: Checks | None = None) -> _Fixed:
    found: list[Offence] = check_source(textwrap.dedent(source), checks=checks or Checks())
    return {o.name: (o.fix, o.edit.kinds if o.edit else frozenset(), o.unsafe) for o in found}


def test_a_call_is_what_it_passes_for_the_parameter_the_method_returns() -> None:
    """By its place or its name, in the class, one under it, or on any receiver of the class: a guess."""
    fixed: _Fixed = _fixed(SOURCE)
    assert {
        name: fixed[name] for name in ("number", "named", "flagged", "keyed", "copied", "inherited", "passed")
    } == {
        "number": ("int", frozenset({KIND, "literal"}), True),
        "named": ("str", frozenset({KIND, "literal"}), True),
        "flagged": ("bytes", frozenset({KIND, "literal"}), True),
        "keyed": ("bytes", frozenset({KIND, "copy"}), True),
        "copied": ("int", frozenset({KIND, "copy"}), True),
        "inherited": ("bytes", frozenset({KIND, "literal"}), True),
        "passed": ("float", frozenset({KIND, "literal"}), True),
    }


def test_a_call_that_passes_no_typed_argument_for_it_has_no_fix() -> None:
    """Its default, a `*` or a `**`, or a value of no known type."""
    fixed: _Fixed = _fixed(SOURCE)
    assert [fixed[name][0] for name in ("defaulted", "starred", "spread", "untyped")] == [None] * 4


def test_only_a_plain_method_returning_one_bare_parameter_counts() -> None:
    """Not one that rebinds or annotates it, returns either of two, a `*args` or `self`, or is decorated."""
    fixed: _Fixed = _fixed(SOURCE)
    # Each by its `return`s' own type, `self`'s the class.
    assert KIND not in fixed["rebound"][1] | fixed["annotated"][1] | fixed["first"][1]
    assert [fixed[name][0] for name in ("either", "gathered", "made")] == [None] * 3
    # A hook a class under it defines again: neither's call is its argument.
    assert (fixed["hooked"][0], KIND in fixed["own"][1]) == (None, False)


def test_the_guess_is_trusted_by_its_kind() -> None:
    """`unsafe-fix-select = ["echoed"]` makes it certain."""
    checks: Checks = Checks(fixes=FixPolicy(unsafe_select=frozenset({KIND})))
    assert _fixed(SOURCE, checks)["number"] == ("int", frozenset({KIND, "literal"}), False)
