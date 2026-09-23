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


def shares(paths: Sequence[Path], workers: int) -> list[list[int]]:
    """Share the files among the workers, the biggest first to the least loaded: a check's time goes by size.

    Returns:
      Each worker's files, by their place in `paths` (no more workers than files).

    """
    loads: list[int] = [0] * min(workers, len(paths))
    found: list[list[int]] = [[] for _ in loads]
    sizes: list[int] = [_size(path) for path in paths]
    index: int
    for index in sorted(range(len(paths)), key=lambda at: -sizes[at]):
        least: int = loads.index(min(loads))
        found[least].append(index)
        loads[least] += sizes[index] or 1
    return [sorted(share) for share in found if share]


def _size(path: Path) -> int:
    """Find a file's size, to balance the workers by.

    Returns:
      It, or 0 if it can't be read (checking it reports that).

    """
    try:
        return path.stat().st_size
    except OSError:
        return 0
