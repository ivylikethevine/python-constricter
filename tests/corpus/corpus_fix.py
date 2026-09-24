# SPDX-License-Identifier: MIT
"""Run `--fix` over a copy of a large real codebase, and check the fixed code is still valid.

CI's Corpus job runs this against its Python's standard library; run it by hand against a larger
one:

  local/.venv/bin/python tests/corpus/corpus_fix.py [PATH] [OPTION ...]   # default: the standard library

It copies PATH's Python files to local/corpus-fix/ (a package into a folder of its name, so its
absolute imports resolve across files), runs `--fix --unsafe-fixes --all-scopes` on the copy, then
compiles every file that compiled before and checks a second `--diff` has nothing left to change.
It prints what broke, if anything, and exits 1 then.
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

from constricter.cli import command as cli
from constricter.cli import paths

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
    named: list[str] = [arg for arg in argv if not arg.startswith("-")]
    extra: list[str] = [arg for arg in argv if arg.startswith("-")]  # e.g. `--infer-with=basedpyright`
    root: Path = Path(named[0]) if named else Path(sysconfig.get_paths()["stdlib"])
    shutil.rmtree(COPY, ignore_errors=True)
    into: Path = COPY / root.name if (root / "__init__.py").is_file() else COPY
    valid: list[Path] = []
    source: Path
    for source in paths.python_files([root]):
        copy: Path = into / source.relative_to(root)
        copy.parent.mkdir(parents=True, exist_ok=True)
        _ = shutil.copyfile(source, copy)
        if _compiles(copy):
            valid.append(copy)
    start: float = time.perf_counter()
    summary: str = _run(["--fix", *FIX, *extra, str(COPY)])[1].splitlines()[-1]
    seconds: float = time.perf_counter() - start
    broken: list[Path] = [path for path in valid if not _compiles(path)]
    diff: str
    diff = _run(["--diff", *FIX, *extra, str(COPY)])[1]
    left: int = diff.count(chr(10) + "+++ ")
    _ = sys.stdout.write(f"{root}: {len(valid)} valid files fixed in {seconds:.1f}s. {summary}\n")
    _ = sys.stdout.write(f"  no longer compile: {len(broken)}\n")
    path: Path
    for path in broken[:10]:
        _ = sys.stdout.write(f"    {path}\n")
    _ = sys.stdout.write(f"  left to fix on a second pass: {left}\n")
    return 1 if broken or left else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
