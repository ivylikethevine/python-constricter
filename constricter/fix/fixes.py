# SPDX-License-Identifier: MIT
"""`--fix`: write the annotations offences offer, to a file's lines or a notebook cell's."""

import contextlib
import re
import sys
from collections.abc import Sequence
from operator import itemgetter
from typing import Final, NamedTuple, TypeAlias

from constricter.offences import Edit, Fix, Offence

_HEADER: Final = 2  # a file's shebang and coding lines come first, if it has them
_HEADER_LINE: Final = re.compile(r"#!|#.*coding[:=]")
# Lines to insert, and the number of lines before them.
_Run: TypeAlias = tuple[int, list[str]]
# An edit's place, and its offence (`None`: a run of imports).
_Placed: TypeAlias = tuple[tuple[int, int], Offence | None]


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
    between its span's columns on the offence's line (an empty annotation deletes it); an
    `Edit.DECLARE` inserts `name: T` on a line of its own before the statement its span names, at
    that statement's indentation. A declaration's `drop` is a second edit: see `dropped`.

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


def dropped(lines: Sequence[str], offence: Offence) -> Replacement | None:
    """Turn a declaration's `drop` into a text edit: deleting those columns of its statement's line.

    Returns:
      The edit, or none without one (or with columns that don't land on characters, as
      `replacement`'s).

    """
    fix: Fix | None = offence.edit
    if fix is None or fix.drop is None:
        return None
    with contextlib.suppress(UnicodeDecodeError, IndexError):
        raw: bytes = lines[fix.span[0] - 1].encode()
        start: int
        end: int
        start, end = fix.drop
        return Replacement(fix.span[0], raw[:start].decode(), raw[start:end].decode(), "")
    return None


def replacements(lines: Sequence[str], offence: Offence) -> tuple[Replacement, ...]:
    """Turn `offence`'s fix into its text edits: `replacement`'s, `dropped`'s, then its imports'.

    Returns:
      Them; none without a fix.

    """
    edits: list[Replacement | None] = [replacement(lines, offence), dropped(lines, offence)]
    line: int
    added: list[str]
    for line, added in _imported(lines, [offence]):
        edits.append(Replacement(line + 1, "", "", "".join(added)))
    return tuple(edit for edit in edits if edit is not None)


def _imported(lines: Sequence[str], offences: Sequence[Offence]) -> list["_Run"]:
    """Place the imports `offences`' fixes need that `lines` doesn't have yet, each once.

    Those for type checking alone go at the end of the body of the module's `if TYPE_CHECKING:`,
    or, with none, in a new one after the others.

    Returns:
      Each run of lines to insert, with the number of lines before it, the last run first.

    """
    fixes: list[Fix]
    if not (fixes := [o.edit for o in offences if o.edit and (o.edit.imports or o.edit.guarded)]):
        return []
    ending: str = _ending(lines)
    statements: list[str] = _missing(lines, sorted({s for fix in fixes for s in fix.imports}))
    guarded: list[str] = _missing(lines, sorted({s for fix in fixes for s in fix.guarded}))
    line: int = _import_line(lines, next((fix.after for fix in fixes if fix.imports), fixes[0].after))
    runs: list[_Run] = []
    block: tuple[int, int] = fixes[0].block
    if guarded and block != (0, 0):
        indent: str = lines[block[0] - 1][: len(lines[block[0] - 1]) - len(lines[block[0] - 1].lstrip())]
        runs.append((block[1], [f"{indent}{statement}{ending}" for statement in guarded]))
    elif guarded:
        guard: str = next(fix.guard for fix in fixes if fix.guarded)
        statements += [f"if {guard}:", *(f"    {statement}" for statement in guarded)]
    if statements:
        runs.append((line, [f"{statement}{ending}" for statement in statements]))
    return runs


def _missing(lines: Sequence[str], statements: Sequence[str]) -> list[str]:
    """Find the import statements `lines` doesn't have yet (as a line of their own).

    Returns:
      Them, in order.

    """
    if not statements:  # most fixes add none: the file's lines needn't be read for them
        return []
    present: set[str] = {line.strip() for line in lines}
    return [statement for statement in statements if statement not in present]


def _import_line(lines: Sequence[str], after: int) -> int:
    """Place added imports after line `after` (from 1), or at the top below a shebang or coding line.

    Returns:
      The number of lines before them.

    """
    if after:
        return after
    header: Sequence[str] = lines[:_HEADER]
    return next((index for index, line in enumerate(header) if not _HEADER_LINE.match(line)), len(header))


def _ending(lines: Sequence[str]) -> str:
    """Find the file's line ending, from its first line.

    Returns:
      It (a newline for an empty file).

    """
    return next((line.removeprefix(line.rstrip("\r\n")) for line in lines[:1]), "") or "\n"


def apply(lines: Sequence[str], offences: Sequence[Offence]) -> list[str]:
    """Return `lines` with each fixable offence's edit made (see `replacement`).

    The drops go first: each deletes the end of a statement's line (its type comment), so moves no
    other edit, and one statement's is made once however many of its names declare. The rest, and
    the imports the fixes need (each once, see `_imported`), are made from the last to the first, so
    no edit moves one still to be made (and two declarations before one statement keep their
    order); one `replacement` can't make is left unmade.

    Returns:
      New lines; `lines` is left as it was. An offence's `line` indexes `lines` from 1.

    """
    text: list[str] = list(lines)
    o: Offence
    edit: Replacement | None
    drops: dict[tuple[int, int, int], Replacement] = {}
    for o in offences:
        if (edit := dropped(text, o)) is not None:
            drops[edit.line, *edit.byte_columns] = edit
    for edit in (drops[key] for key in sorted(drops, reverse=True)):
        kept: int = edit.columns[1]
        text[edit.line - 1] = edit.prefix + text[edit.line - 1][kept:]
    # Each run of imports goes after its line: before any edit on that line, in this order.
    runs: dict[tuple[int, int], list[str]] = {
        (line, sys.maxsize): run for line, run in _imported(text, offences)
    }
    edits: list[_Placed] = [(_position(o), o) for o in offences if o.edit]
    placed: tuple[int, int]
    fixed: Offence | None
    for placed, fixed in sorted([*edits, *((key, None) for key in runs)], key=itemgetter(0), reverse=True):
        if fixed is None:
            after: int = placed[0]
            text[after:after] = runs[placed]
        elif (edit := replacement(text, fixed)) is None:
            continue
        elif fixed.edit and fixed.edit.edit is Edit.DECLARE:
            text.insert(edit.line - 1, edit.text)  # a declaration: a line of its own
        else:
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
