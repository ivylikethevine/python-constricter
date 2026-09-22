# SPDX-License-Identifier: MIT
"""`--fix`: add the annotations offences offer, to a file's lines or a notebook cell's."""

from collections.abc import Sequence

from constricter.checker import Offence


def apply(lines: Sequence[str], offences: Sequence[Offence]) -> list[str]:
  """Return `lines` with each fixable offence's annotation added after its name.

  Returns:
    New lines; `lines` is left as it was. An offence's `line` indexes `lines` from 1.

  """
  text: list[str] = list(lines)
  o: Offence
  for o in sorted((o for o in offences if o.fix), key=lambda o: (o.line, o.col), reverse=True):
    raw: bytes = text[o.line - 1].encode()
    end: int = o.col + len(o.name.encode())  # `col` counts bytes, as `ast` does
    text[o.line - 1] = (raw[:end] + f": {o.fix}".encode() + raw[end:]).decode()
  return text
