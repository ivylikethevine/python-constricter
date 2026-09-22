# SPDX-License-Identifier: MIT
"""JSON with comments and trailing commas (constricter.jsonc)."""

import json

import pytest

from constricter import jsonc


def test_comments_and_trailing_commas_are_allowed() -> None:
  """`//` and `/* */` comments and trailing commas are ignored; strings are left alone."""
  text: str = """
  // a baseline
  {
    "a": "// not a comment, /* nor this */",  /* a block
    comment */
    "b": [1, 2,],
    "c": "a trailing comma, ]",
  }
  """
  assert jsonc.loads(text) == {
    "a": "// not a comment, /* nor this */",
    "b": [1, 2],
    "c": "a trailing comma, ]",
  }
  assert jsonc.loads(b'{"escaped \\" // quote": 1,}') == {'escaped " // quote': 1}


def test_errors_keep_the_original_positions() -> None:
  """An error's line and column are the original text's, comments and all."""
  error: pytest.ExceptionInfo[json.JSONDecodeError]
  with pytest.raises(json.JSONDecodeError) as error:
    _ = jsonc.loads('/* x */ {\n  // y\n  "a" 1\n}')
  assert (error.value.lineno, error.value.colno) == (3, 7)
