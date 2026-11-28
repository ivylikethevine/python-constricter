"""`--infer-with`: no checker's hint types a name one checker hints a flag's one value beside other types."""

import pytest

from constricter import Offence, check_source
from constricter.fix.core.known import Hints, Outside
from constricter.fix.values.hinted import flagged


@pytest.mark.parametrize(
    ("hint", "expected"),
    [
        ("str | Literal[True] | None", True),
        ("Literal[False] | Index", True),
        ("Lock | Literal[False] | None", True),
        ("Literal[False]", False),  # a flag bound once: `bool` is right
        ("Literal[False] | None", False),  # an optional flag
        ("Literal[True] | Literal[False]", False),
        ("Literal[True, False] | None", False),
        ("bool | Literal[True]", False),
        ("Unknown | Literal[False]", False),
        ("(Unknown & ~None) | Literal[True]", False),
        ("Any | Literal[True]", False),
        ("Callable[[], Literal[True]]", False),
        ("str | None", False),
        ("str | Literal[True] |", False),  # not Python
    ],
)
def test_a_union_holding_a_flags_one_value_is_flagged(hint: str, *, expected: bool) -> None:
    """`Literal[True]` or `Literal[False]` alone, beside types the checker knows that aren't `bool`."""
    assert flagged(hint) is expected


def test_no_checkers_hint_types_a_name_one_hints_a_flags_one_value_beside_others() -> None:
    """A binding as websockets' `proxy = self.proxy`: another checker's `str | bool | None` lost it.

    A traced run's type still types it.
    """
    source: str = "def f(q) -> None:\n    x = q.make()\n    y = q.make()\n    z = q.make()\n"
    first: Hints = Hints("ty", {(2, 5): "str | bool | None", (3, 5): "Literal[False]", (4, 5): "bool"})
    second: Hints = Hints(
        "basedpyright",
        {(2, 5): "str | Literal[True] | None", (4, 5): "Unknown | Literal[False]"},
    )
    offences: list[Offence] = check_source(source, outside=Outside(hints=(first, second)))
    assert [(o.name, o.fix) for o in offences] == [("x", None), ("y", "bool"), ("z", "bool")]
    traced: Hints = Hints("trace", {(2, 5): "str"}, kind="traced")
    with_trace: list[Offence] = check_source(source, outside=Outside(hints=(first, second, traced)))
    assert next((o.name, o.fix) for o in with_trace) == ("x", "str")
