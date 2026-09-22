# SPDX-License-Identifier: MIT
"""Which files to check: the paths given, directories walked, and what's excluded."""

from collections.abc import Iterator, Sequence
from fnmatch import fnmatch
from pathlib import Path
from typing import Final

from constricter import notebook

# Skipped in a directory walk unless `--exclude` says otherwise: hidden directories, and common
# tool/vendor ones. Merged with `exclude`'s globs (matched per directory name), not replaced by them.
_DEFAULT_EXCLUDES: Final = (".*", "__pycache__", "node_modules", "venv", "site-packages", "build", "dist")
STDIN: Final = Path("-")


def excluded(path: Path, patterns: Sequence[str], text: str | None = None) -> bool:
    """Check `path` (or its `text`, as given) against `patterns`: the whole path, or its name.

    Returns:
      Whether any glob matches either.

    """
    text = path.as_posix() if text is None else text
    return any(fnmatch(text, p) or fnmatch(path.name, p) for p in patterns)


def python_files(paths: Sequence[Path], exclude: Sequence[str] = ()) -> Iterator[Path]:
    """Find the files to check.

    A directory walk skips `_DEFAULT_EXCLUDES` and `exclude`'s globs by directory name, and `exclude`
    by whole path or file name; a file named directly is checked regardless.

    Yields:
      Each file given, and each `*.py` under each directory given.

    """
    globs: tuple[str, ...] = (*_DEFAULT_EXCLUDES, *exclude)
    path: Path
    found: Path
    for path in paths:
        if not path.is_dir():
            if not excluded(path, exclude):
                yield path
            continue
        for found in sorted([*path.rglob("*.py"), *path.rglob(f"*{notebook.SUFFIX}")]):
            parts: tuple[str, ...] = found.relative_to(path).parts[:-1]
            if any(fnmatch(part, glob) for part in parts for glob in globs):
                continue
            if not excluded(found, exclude):
                yield found
