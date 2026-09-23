# SPDX-License-Identifier: MIT
"""Each code's rationale and fix, for `constricter --explain`."""

from typing import Final

from constricter.offences import (
    CAN_BE_FINAL,
    COMMENT_TYPED_TARGET,
    LONG_TUPLE,
    MESSAGES,
    MISMATCHED_TYPE,
    NARROWABLE_TYPE,
    NESTED_TYPE,
    OPT_IN,
    REDUNDANT_TYPE,
    UNANNOTATED,
    UNANNOTATED_MEMBER,
    UNTYPED_TARGET,
    UNUSED_UNION_MEMBER,
    VAGUE_TYPE,
    Level,
    Offence,
)

_WHY: Final = {
    UNANNOTATED: (
        "A local's type should be written where it's first bound, not left to inference.\n"
        "Annotate the binding (`count: int = 0`), or declare it first (`first: int`) when unpacking,\n"
        "`:=` or `with ... as` binds it. `--fix` adds the annotation when the value decides it."
    ),
    UNTYPED_TARGET: (
        "A `for` target or `match` capture binds a local with no annotation. Declare it before the\n"
        "statement (`item: str`, then `for item in items:`)."
    ),
    COMMENT_TYPED_TARGET: (
        "A `# type:` comment is the old, Python 2 form of an annotation, which some tools ignore.\n"
        "Declare the variable before the loop instead."
    ),
    UNANNOTATED_MEMBER: (
        "With `all-scopes`, module and class variables need annotating too (`LIMIT: int = 3`). In a\n"
        "dataclass, use `ClassVar[T]`: a plain annotation there makes a field. Dunder names and enum\n"
        "members are exempt."
    ),
    VAGUE_TYPE: (
        "`Any`, `object` and generics without their parameters (`list`, `dict`) say almost nothing\n"
        "about the value. Name the real type: `list[str]`, a `TypedDict`, a union."
    ),
    NESTED_TYPE: (
        "An annotation nested `nesting` deep (3 by default) is hard to read and to change. Name a part\n"
        "of it with an alias (`Row: TypeAlias = tuple[int, set[str]]`, then `dict[str, list[Row]]`)."
    ),
    REDUNDANT_TYPE: (
        "A name annotated the same way twice in one straight-line block says nothing a type checker\n"
        "doesn't already know from the first one. Drop the second annotation (`x = 2`, not `x: int = 2`);\n"
        "branches that never run together (an `if`'s two arms, a `try`'s body and its `except`) aren't\n"
        "compared, since typing the same name the same way in each is normal, not redundant."
    ),
    MISMATCHED_TYPE: (
        "Every value a name is bound to, over its whole lifetime in the scope, should fit its\n"
        'annotation: `count: int = 0` then `count = "done"` makes `count` mean two things. Only a\n'
        "value whose type is certain is checked, against types whose every subclass is known\n"
        "(builtins, and classes the module defines on such bases), so an imported class never is."
    ),
    NARROWABLE_TYPE: (
        "An annotation wider than anything the name ever holds hides what the code really does:\n"
        "`total: float = 0` only ever given `int`s is an `int`. Narrow it, or widen the values if the\n"
        "annotation is the intent. Claimed only for a function's own names, when every value the name\n"
        "is bound to has a certain type and no other scope writes it (`nonlocal`): a module or class\n"
        "variable is state other code rebinds out of sight (`mod.X = ...`, `self.x = ...`)."
    ),
    UNUSED_UNION_MEMBER: (
        "A union member no value ever is (`label: int | str = 3`, never a `str`) is dead weight every\n"
        "reader has to consider. Drop it. Claimed under the same conditions as LVA008."
    ),
    LONG_TUPLE: (
        "A fixed-length tuple listing more than `max-length` types (4 by default) leaves every reader\n"
        "counting positions: what's `row[3]`? Name the fields instead, with a `NamedTuple` or a\n"
        "dataclass. `tuple[int, ...]` (any length) isn't a list of positions, so it's never counted."
    ),
    CAN_BE_FINAL: (
        "A local bound exactly once, by a plain `name = value` outside any loop, and never rebound\n"
        "(not from a nested function either) could say so: `limit: Final = 10`. Off unless selected\n"
        "by its full code (`--extend-select LVA012`): most locals are bound once."
    ),
}


def explain(code: str) -> str:
    """Explain `code`.

    Returns:
      Its message, rationale and the levels that report it.

    """
    offence: Offence = Offence(1, 0, "name", code)
    levels: list[str] = [
        f"{level.name.lower()}: {'error' if offence.is_error(level) else 'warning'}"
        for level in Level
        if offence.is_reported(level)
    ]
    message: str = MESSAGES[code].format(name="`name`", detail="T")
    selected: str = " (only when selected)" if code in OPT_IN else ""
    return f"{code}: {message}\n\n{_WHY[code]}\n\n{', '.join(levels)}{selected}\n"
