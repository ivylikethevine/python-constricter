# SPDX-License-Identifier: MIT
"""`--fix`: write the annotations offences offer, to a file's lines or a notebook cell's."""

import contextlib
from collections.abc import Sequence

from constricter.offences import Edit, Fix, Offence


def apply(lines: Sequence[str], offences: Sequence[Offence]) -> list[str]:
    """Return `lines` with each fixable offence's edit made.

    An `Edit.ANNOTATE` adds `: T` after the name; an `Edit.REPLACE` writes over the annotation
    between its span's columns on the offence's line; an `Edit.DECLARE` inserts `name: T` on a line
    of its own before the statement its span names, at that statement's indentation. They're made
    from the last to the first, so no edit moves one still to be made (and two declarations before
    one statement keep their order).

    An edit whose columns don't land on UTF-8 character boundaries in its line (rare: `ast`'s
    column and a re-encoded line's bytes can disagree for some non-ASCII source) is left unmade,
    rather than splitting a multi-byte character and corrupting the line.

    Returns:
      New lines; `lines` is left as it was. An offence's `line` indexes `lines` from 1.

    """
    text: list[str] = list(lines)
    o: Offence
    for o in sorted((o for o in offences if o.edit), key=_position, reverse=True):
        fix: Fix = o.edit or Fix("")
        with contextlib.suppress(UnicodeDecodeError, IndexError):
            if fix.edit is Edit.DECLARE:
                statement: str = text[fix.span[0] - 1]
                indent: str = statement[: len(statement) - len(statement.lstrip())]
                ending: str = statement.removeprefix(statement.rstrip("\r\n")) or "\n"
                text.insert(fix.span[0] - 1, f"{indent}{o.name}: {fix.annotation}{ending}")
                continue
            raw: bytes = text[o.line - 1].encode()
            start: int = fix.span[0] if fix.edit is Edit.REPLACE else o.col + len(o.name.encode())
            end: int = fix.span[1] if fix.edit is Edit.REPLACE else start
            written: str = fix.annotation if fix.edit is Edit.REPLACE else f": {fix.annotation}"
            text[o.line - 1] = raw[:start].decode() + written + raw[end:].decode()
    return text


def _position(offence: Offence) -> tuple[int, int]:
    """Place an offence's edit in the file, to order the edits by.

    Returns:
      Its line and column: a declaration's are the statement's it goes before.

    """
    fix: Fix | None = offence.edit
    return (
        (fix.span[0], offence.col)
        if fix is not None and fix.edit is Edit.DECLARE
        else (offence.line, offence.col)
    )
