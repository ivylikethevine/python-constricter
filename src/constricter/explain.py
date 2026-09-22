# SPDX-License-Identifier: MIT
"""Each code's rationale and fix, for `constricter --explain`."""

from typing import Final

from constricter.checker import (
    COMMENT_TYPED_TARGET,
    MESSAGES,
    NESTED_TYPE,
    UNANNOTATED,
    UNANNOTATED_MEMBER,
    UNTYPED_TARGET,
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
        "An annotation nested `nesting` deep (5 by default) is hard to read and to change. Name a part\n"
        "of it with an alias (`Row: TypeAlias = tuple[int, set[str]]`, then `dict[str, list[Row]]`)."
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
    return f"{code}: {MESSAGES[code].format(name='`name`')}\n\n{_WHY[code]}\n\n{', '.join(levels)}\n"
