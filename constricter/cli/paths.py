"""Which files to check: the paths given, directories walked, and what's excluded."""

import os
import shutil
import subprocess  # asks git which files it tracks, or would
from collections.abc import Iterable, Iterator, Sequence
from fnmatch import fnmatch
from pathlib import Path
from typing import Final

from constricter import notebook

# Skipped in a directory walk unless `--exclude` says otherwise: hidden directories, and common
# tool/vendor ones. Merged with `exclude`'s globs (matched per directory name), not replaced by them.
_DEFAULT_EXCLUDES: Final = (".*", "__pycache__", "node_modules", "venv", "site-packages", "build", "dist")
STDIN: Final = Path("-")
_KINDS: Final = ("*.py", f"*{notebook.SUFFIX}")  # the files a directory walk finds


def excluded(path: Path, patterns: Sequence[str], text: str | None = None) -> bool:
    """Check `path` (or its `text`, as given) against `patterns`: the whole path, or its name.

    Returns:
      Whether any glob matches either.

    """
    text = path.as_posix() if text is None else text
    return any(fnmatch(text, p) or fnmatch(path.name, p) for p in patterns)


def python_files(
    paths: Sequence[Path],
    exclude: Sequence[str] = (),
    *,
    tracked: bool = False,
) -> Iterator[Path]:
    """Find the files to check.

    A directory walk skips `_DEFAULT_EXCLUDES` and `exclude`'s globs by directory name, and `exclude`
    by whole path or file name; a file named directly is checked regardless. With `tracked`, a
    directory in a git checkout has only what git tracks there or would (`_listed`), so nothing its
    `.gitignore` files name.

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
        listed: list[Path] | None = _listed(path) if tracked else None
        for found in sorted(_walked(path, globs) if listed is None else _under(path, listed, globs)):
            if not excluded(found, exclude):
                yield found


def _listed(top: Path) -> list[Path] | None:
    """Ask git for the files to check under `top`: those it tracks, and the untracked it doesn't ignore.

    By its `.gitignore` files, its `info/exclude` and the user's own, as git reads them.

    Returns:
      Them; `None` where there's no git or `top` is in no checkout, and where git lists none: a
      directory it ignores was still named, and is walked whole.

    """
    git: str | None
    if (git := shutil.which("git")) is None:
        return None
    asking: list[str] = [git, "-C", str(top), "ls-files", "-z", "--cached", "--others", "--exclude-standard"]
    try:
        ran: subprocess.CompletedProcess[bytes] = subprocess.run(
            [*asking, "--", *_KINDS],
            capture_output=True,
            check=False,
            env=os.environ | {"GIT_OPTIONAL_LOCKS": "0"},  # reads the index: never waits to write it
        )
    except OSError:
        return None
    if ran.returncode or not ran.stdout:
        return None
    return [top / os.fsdecode(name) for name in ran.stdout.split(b"\0") if name]


def _under(top: Path, listed: Iterable[Path], globs: Sequence[str]) -> Iterator[Path]:
    """Keep the files git listed under `top` that a walk would reach: there, in no skipped directory.

    Yields:
      Each (one tracked and since deleted isn't there).

    """
    found: Path
    for found in listed:
        inside: tuple[str, ...] = found.relative_to(top).parts[:-1]
        if not any(fnmatch(part, glob) for part in inside for glob in globs) and found.is_file():
            yield found


def _walked(top: Path, globs: Sequence[str]) -> Iterator[Path]:
    """Walk `top` for the files to check, entering no directory whose name a glob of `globs` matches.

    Yields:
      Each `*.py` file and notebook under it, in no order.

    """
    directory: str
    inner: list[str]
    names: list[str]
    for directory, inner, names in os.walk(top):
        inner[:] = [name for name in inner if not any(fnmatch(name, glob) for glob in globs)]
        name: str
        for name in names:
            if any(fnmatch(name, kind) for kind in _KINDS):
                yield Path(directory, name)


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
