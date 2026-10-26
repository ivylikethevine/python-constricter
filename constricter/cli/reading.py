"""A file's text, in the encoding Python reads it in; `-` is standard input."""

import io
import sys
import tokenize
from pathlib import Path
from typing import Final

from constricter import notebook
from constricter.cli.paths import STDIN

# What reading or parsing a file raises: UnicodeDecodeError is a ValueError; a bad encoding
# declaration, a SyntaxError.
READ_ERRORS: Final = (OSError, ValueError, SyntaxError)


def encoding_of(path: Path, data: bytes) -> str:
    """Find the encoding of `path`, whose bytes are `data`: a notebook's is UTF-8 (it's JSON).

    Returns:
      A module's, as Python finds it: a PEP 263 declaration (`# -*- coding: latin-1 -*-`), a BOM
      (`utf-8-sig`), or UTF-8. Raises `SyntaxError` for an unknown or contradictory one.

    """
    return (
        "utf-8" if path.suffix == notebook.SUFFIX else tokenize.detect_encoding(io.BytesIO(data).readline)[0]
    )


def read_text(path: Path) -> str:
    """Read `path`, in its encoding; `-` is standard input.

    Returns:
      Its text.

    """
    if path == STDIN:
        return sys.stdin.read()
    data: bytes = path.read_bytes()
    return data.decode(encoding_of(path, data))
