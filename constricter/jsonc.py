# SPDX-License-Identifier: MIT
"""JSON with comments (`//`, `/* */`) and trailing commas, for the files constricter reads.

Comments and trailing commas become spaces (newlines kept), so every position the JSON parser reports
is still the original file's. What constricter writes stays plain JSON.
"""

import json
import re
from typing import TypeGuard, cast

# A string (left alone), or a comment.
_COMMENT: re.Pattern[str] = re.compile(r'"(?:\\.|[^"\\])*"|//[^\n]*|/\*.*?\*/', re.DOTALL)
# A string (left alone), or a comma with only whitespace before the `]` or `}` it trails.
_TRAILING: re.Pattern[str] = re.compile(r'"(?:\\.|[^"\\])*"|,(?=\s*[\]}])')


def _blank(match: re.Match[str]) -> str:
    text: str = match.group()
    return text if text.startswith('"') else re.sub(r"[^\n]", " ", text)


def as_text(value: str | bytes) -> str:
    """Decode `value` if it's bytes.

    Returns:
      It, as text.

    """
    return value.decode("utf-8") if isinstance(value, bytes) else value


def is_int(value: object) -> TypeGuard[int]:
    """Check whether `value` is a plain whole number, not a `bool` (a `bool` is an `int` in Python).

    Returns:
      Whether it is.

    """
    return isinstance(value, int) and not isinstance(value, bool)


def loads(text: str | bytes) -> object:
    """Parse JSON that may have comments and trailing commas.

    Returns:
      The value. Raises `ValueError` as `json.loads` does.

    """
    return cast("object", json.loads(_TRAILING.sub(_blank, _COMMENT.sub(_blank, as_text(text)))))
