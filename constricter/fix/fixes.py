# SPDX-License-Identifier: MIT
"""`--fix`: write the annotations offences offer, to a file's lines or a notebook cell's."""

import contextlib
from collections.abc import Sequence
from typing import NamedTuple

from constricter.offences import Edit, Fix, Offence


class Replacement(NamedTuple):
    """One fix as a text edit on `line` (from 1): after `prefix`, `deleted` becomes `text`.

    A declaration inserts a whole line before its statement's: `prefix` and `deleted` are empty.
    """

    line: int
    prefix: str  # the line's text before the edit
    deleted: str
    text: str

    @property
    def columns(self) -> tuple[int, int]:
        """Where the edit starts and ends, in characters from 0."""
        return len(self.prefix), len(self.prefix) + len(self.deleted)

    @property
    def byte_columns(self) -> tuple[int, int]:
        """Where the edit starts and ends, in UTF-8 bytes from 0."""
        start: int = len(self.prefix.encode())
        return start, start + len(self.deleted.encode())


def replacement(lines: Sequence[str], offence: Offence) -> Replacement | None:
    """Turn `offence`'s edit into a text edit on `lines` (indexed from 1 by its line).

    An `Edit.ANNOTATE` adds `: T` after the name; an `Edit.REPLACE` writes over the annotation
    between its span's columns on the offence's line; an `Edit.DECLARE` inserts `name: T` on a line
    of its own before the statement its span names, at that statement's indentation.

    Returns:
      The edit; none without a fix, or when its columns don't land on UTF-8 character boundaries in
      its line (rare: `ast`'s column and a re-encoded line's bytes can disagree for some non-ASCII
      source), rather than splitting a multi-byte character and corrupting the line.

    """
    fix: Fix | None
    if (fix := offence.edit) is None:
        return None
    with contextlib.suppress(UnicodeDecodeError, IndexError):
        if fix.edit is Edit.DECLARE:
            statement: str = lines[fix.span[0] - 1]
            indent: str = statement[: len(statement) - len(statement.lstrip())]
            ending: str = statement.removeprefix(statement.rstrip("\r\n")) or "\n"
            return Replacement(fix.span[0], "", "", f"{indent}{offence.name}: {fix.annotation}{ending}")
        raw: bytes = lines[offence.line - 1].encode()
        start: int = fix.span[0] if fix.edit is Edit.REPLACE else offence.col + len(offence.name.encode())
        end: int = fix.span[1] if fix.edit is Edit.REPLACE else start
        written: str = fix.annotation if fix.edit is Edit.REPLACE else f": {fix.annotation}"
        return Replacement(offence.line, raw[:start].decode(), raw[start:end].decode(), written)
    return None


def apply(lines: Sequence[str], offences: Sequence[Offence]) -> list[str]:
    """Return `lines` with each fixable offence's edit made (see `replacement`).

    They're made from the last to the first, so no edit moves one still to be made (and two
    declarations before one statement keep their order); one `replacement` can't make is left unmade.

    Returns:
      New lines; `lines` is left as it was. An offence's `line` indexes `lines` from 1.

    """
    text: list[str] = list(lines)
    o: Offence
    edit: Replacement | None
    for o in sorted((o for o in offences if o.edit), key=_position, reverse=True):
        if (edit := replacement(text, o)) is None:
            continue
        if o.edit and o.edit.edit is Edit.DECLARE:
            text.insert(edit.line - 1, edit.text)  # a declaration: a line of its own
            continue
        end: int = edit.columns[1]
        text[edit.line - 1] = edit.prefix + edit.text + text[edit.line - 1][end:]
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
