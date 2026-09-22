# SPDX-License-Identifier: MIT
"""JSON with comments (`//`, `/* */`) and trailing commas, for the files constricter reads.

Comments and trailing commas become spaces (newlines kept), so every position the JSON parser reports
is still the original file's. What constricter writes stays plain JSON.
"""

import json
import re
from typing import cast

# A string (left alone), or a comment.
_COMMENT: re.Pattern[str] = re.compile(r'"(?:\\.|[^"\\])*"|//[^\n]*|/\*.*?\*/', re.DOTALL)
# A string (left alone), or a comma with only whitespace before the `]` or `}` it trails.
_TRAILING: re.Pattern[str] = re.compile(r'"(?:\\.|[^"\\])*"|,(?=\s*[\]}])')


def _blank(match: re.Match[str]) -> str:
  text: str = match.group()
  return text if text.startswith('"') else re.sub(r"[^\n]", " ", text)


def loads(text: str | bytes) -> object:
  """Parse JSON that may have comments and trailing commas. Raises `ValueError` as `json.loads` does."""
  source: str = text.decode("utf-8") if isinstance(text, bytes) else text
  return cast("object", json.loads(_TRAILING.sub(_blank, _COMMENT.sub(_blank, source))))
