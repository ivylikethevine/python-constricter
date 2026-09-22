# SPDX-License-Identifier: MIT
"""Check a large real codebase for crashes and slowdowns.

CI's Corpus job runs this against its Python's standard library; run it by hand against a larger
one:

  local/.venv/bin/python tests/corpus.py [PATH]   # default: this Python's standard library

It runs constricter at `suffocate` with `--all-scopes` over every CPU, then prints how long that
took, how many files it read, the offences per code, and the files Python itself can't parse. A
crash prints its traceback and exits non-zero.
"""

import contextlib
import io
import json
import sys
import sysconfig
import time
from collections import Counter
from collections.abc import Sequence
from pathlib import Path
from typing import Final, TypeAlias, cast

from constricter.cli import command as cli
from constricter.cli import paths

_Json: TypeAlias = "str | int | list[_Json] | dict[str, _Json] | None"
_UNPARSABLE: Final = ": error: "  # how the command reports a file it can't read or parse


def main(argv: Sequence[str]) -> int:
    """Check the corpus and print what it found; a crash isn't caught.

    Returns:
      0.

    """
    root: Path = Path(argv[0]) if argv else Path(sysconfig.get_paths()["stdlib"])
    files: int = sum(1 for _ in paths.python_files([root]))
    out: io.StringIO = io.StringIO()
    err: io.StringIO = io.StringIO()
    start: float = time.perf_counter()
    with (
        contextlib.redirect_stdout(out),
        contextlib.redirect_stderr(err),
    ):  # a crash propagates, traceback and all
        _ = cli.main(["--format=json", "--level=suffocate", "--all-scopes", "--jobs=0", str(root)])
    seconds: float = time.perf_counter() - start
    results: list[dict[str, _Json]] = cast("list[dict[str, _Json]]", json.loads(out.getvalue() or "[]"))
    unparsable: list[str] = [line for line in err.getvalue().splitlines() if _UNPARSABLE in line]
    _ = sys.stdout.write(f"{root}: {files} files in {seconds:.1f}s ({files / seconds:.0f} files/s)\n")
    code: str
    count: int
    for code, count in sorted(Counter(str(r["code"]) for r in results).items()):
        _ = sys.stdout.write(f"  {code}: {count}\n")
    _ = sys.stdout.write(f"  unparsable by Python itself: {len(unparsable)}\n")
    line: str
    for line in unparsable[:10]:
        _ = sys.stdout.write(f"    {line}\n")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
