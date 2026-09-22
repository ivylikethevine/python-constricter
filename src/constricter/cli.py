"""The `constricter` command (see README)."""

import argparse
import re
import sys
from collections.abc import Iterator, Sequence
from fnmatch import fnmatch
from pathlib import Path
from typing import cast

from constricter import __version__
from constricter.checker import CODE, Offence, check_source

_SKIPPED_DIRS: frozenset[str] = frozenset(
    {"__pycache__", "node_modules", "venv", "site-packages", "build", "dist"}
)
_NOQA: re.Pattern[str] = re.compile(
    r"#\s*noqa(?::\s*(?P<codes>[A-Z]+[0-9]+(?:[,\s]+[A-Z]+[0-9]+)*))?", re.IGNORECASE
)


def _suppressed(line: str) -> bool:
    """Return whether `line` has a `# noqa` covering this rule."""
    match_: re.Match[str] | None = _NOQA.search(line)
    if match_ is None:
        return False
    codes: str | None = match_.group("codes")
    return codes is None or CODE in re.split(r"[,\s]+", codes.upper())


def _excluded(path: Path, patterns: Sequence[str]) -> bool:
    text: str = path.as_posix()
    return any(fnmatch(text, p) or fnmatch(path.name, p) for p in patterns)


def python_files(paths: Sequence[Path], exclude: Sequence[str] = ()) -> Iterator[Path]:
    """Yield each file given and each `*.py` under each directory given."""
    for path in paths:
        if not path.is_dir():
            if not _excluded(path, exclude):
                yield path
            continue
        for found in sorted(path.rglob("*.py")):
            parts: tuple[str, ...] = found.relative_to(path).parts[:-1]
            if any(p.startswith(".") or p in _SKIPPED_DIRS for p in parts):
                continue
            if not _excluded(found, exclude):
                yield found


def check_file(path: Path) -> list[Offence]:
    """Return the offences in `path` that no `# noqa` suppresses."""
    source: str = path.read_text(encoding="utf-8")
    lines: list[str] = source.splitlines()
    return [
        o
        for o in check_source(source, str(path))
        if not (o.line <= len(lines) and _suppressed(lines[o.line - 1]))
    ]


def main(argv: Sequence[str] | None = None) -> int:
    parser: argparse.ArgumentParser = argparse.ArgumentParser(
        prog="constricter",
        description="Report local variables that aren't annotated where they're first bound.",
    )
    _ = parser.add_argument("paths", nargs="*", type=Path, help="files and directories (default: .)")
    _ = parser.add_argument(
        "--exclude",
        action="append",
        default=[],
        metavar="GLOB",
        help="skip paths matching this glob (repeatable), e.g. 'tests/fixtures/*'",
    )
    _ = parser.add_argument("--quiet", "-q", action="store_true", help="don't print the summary line")
    _ = parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    args: argparse.Namespace = parser.parse_args(argv)
    paths: list[Path] = cast("list[Path]", args.paths) or [Path()]
    exclude: list[str] = cast("list[str]", args.exclude)
    quiet: bool = cast("bool", args.quiet)

    count: int = 0
    files: int = 0
    failed: bool = False
    for path in python_files(paths, exclude):
        files += 1
        try:
            offences: list[Offence] = check_file(path)
        except (OSError, UnicodeDecodeError, SyntaxError) as error:
            print(f"{path}: error: {error}", file=sys.stderr)
            failed = True
            continue
        for o in offences:
            print(f"{path}:{o.line}:{o.col + 1}: {CODE} {o.message}")
        count += len(offences)
    if not quiet:
        print(f"Found {count} unannotated local(s) in {files} file(s).")
    return 2 if failed else 1 if count else 0


if __name__ == "__main__":
    sys.exit(main())
