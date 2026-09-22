# SPDX-License-Identifier: MIT
"""Run `--fix` over a copy of a large real codebase, and check the fixed code is still valid.

  local/.venv/bin/python tests/corpus_fix.py [PATH]   # default: this Python's standard library

It copies PATH's Python files to local/corpus-fix/, runs `--fix --unsafe-fixes --all-scopes` on the
copy, then compiles every file that compiled before and checks a second `--diff` has nothing left
to change. It prints what broke, if anything, and exits 1 then. Run by hand; CI doesn't.
"""

import contextlib
import io
import shutil
import sys
import sysconfig
import time
import warnings
from collections.abc import Sequence
from pathlib import Path
from typing import Final

from constricter import cli

COPY: Final = Path("local/corpus-fix")
FIX: Final = ["--unsafe-fixes", "--all-scopes", "--jobs=0"]


def _compiles(path: Path) -> bool:
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")  # e.g. invalid escape sequences, which the stdlib's tests have
        try:
            _ = compile(path.read_bytes(), str(path), "exec", dont_inherit=True)
        except (SyntaxError, ValueError):
            return False
    return True


def _run(args: Sequence[str]) -> tuple[int, str]:
    """Run the command in-process.

    Returns:
      Its exit status and output.

    """
    out: io.StringIO = io.StringIO()
    status: int
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(io.StringIO()):
        status = cli.main(args)
    return status, out.getvalue()


def main(argv: Sequence[str]) -> int:
    """Fix the copy and check it.

    Returns:
      1 if a fix broke a file or left more to fix, else 0.

    """
    root: Path = Path(argv[0]) if argv else Path(sysconfig.get_paths()["stdlib"])
    shutil.rmtree(COPY, ignore_errors=True)
    valid: list[Path] = []
    source: Path
    for source in cli.python_files([root]):
        copy: Path = COPY / source.relative_to(root)
        copy.parent.mkdir(parents=True, exist_ok=True)
        _ = shutil.copyfile(source, copy)
        if _compiles(copy):
            valid.append(copy)
    start: float = time.perf_counter()
    summary: str = _run(["--fix", *FIX, str(COPY)])[1].splitlines()[-1]
    seconds: float = time.perf_counter() - start
    broken: list[Path] = [path for path in valid if not _compiles(path)]
    status: int
    diff: str
    status, diff = _run(["--diff", *FIX, str(COPY)])
    _ = sys.stdout.write(f"{root}: {len(valid)} valid files fixed in {seconds:.1f}s. {summary}\n")
    _ = sys.stdout.write(f"  no longer compile: {len(broken)}\n")
    path: Path
    for path in broken[:10]:
        _ = sys.stdout.write(f"    {path}\n")
    _ = sys.stdout.write(f"  left to fix on a second pass: {diff.count(chr(10) + '+++ ')}\n")
    return 1 if broken or status != cli.EXIT_CLEAN else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
