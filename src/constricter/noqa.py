# SPDX-License-Identifier: MIT
"""`# noqa` comments, read the same way by the CLI and the pylint plugin (flake8 reads its own)."""

import io
import re
from collections.abc import Sequence

from constricter.checker import Offence

_NOQA: re.Pattern[str] = re.compile(
  r"#\s*noqa(?::\s*(?P<codes>[A-Z]+[0-9]+(?:[,\s]+[A-Z]+[0-9]+)*))?", re.IGNORECASE
)


def lines(text: str) -> list[str]:
  """Split `text` into lines as Python does (LF, CRLF or CR), keeping each line's ending."""
  return io.StringIO(text, newline="").readlines()


def suppressed(line: str, code: str) -> bool:
  """Return whether `line` has a `# noqa` covering `code`: a bare one, or one naming it."""
  match_: re.Match[str] | None
  if (match_ := _NOQA.search(line)) is None:
    return False
  codes: str | None = match_.group("codes")
  return codes is None or code in re.split(r"[,\s]+", codes.upper())


def unsuppressed(offences: Sequence[Offence], source: Sequence[str]) -> list[Offence]:
  """Return the offences no `# noqa` on their line (in `source`'s lines) suppresses."""
  return [o for o in offences if not (o.line <= len(source) and suppressed(source[o.line - 1], o.code))]
