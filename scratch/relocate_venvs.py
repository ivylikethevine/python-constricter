"""Point every venv and symlink under ROOTs at a moved checkout: OLD's prefix becomes NEW's.

A venv names its own absolute path in console-script shebangs, `activate*`, `.pth` files, editable
finders, `direct_url.json` and `pyvenv.cfg`; moving the checkout leaves them all naming OLD. This
rewrites OLD to NEW in each venv's text files (no NUL in the first 8 KiB) where OLD ends a path
component, and re-points each symlink under ROOTs whose target starts with OLD. Binary files and
anything outside a venv but symlinks are left alone. Idempotent while NEW doesn't contain OLD.

    local/.venv/bin/python -I scratch/relocate_venvs.py [--write] OLD NEW ROOT...

Without `--write`, it only counts what it would change.
"""

import argparse
import os
import re
import stat
import sys
from collections import Counter
from pathlib import Path

_PROBE = 8192


def _venvs(roots: list[Path]) -> list[Path]:
    """Return every directory under `roots` holding a `pyvenv.cfg`."""
    found: list[Path] = []
    for root in roots:
        for top, dirs, files in os.walk(root):
            if "pyvenv.cfg" in files:
                found.append(Path(top))
            dirs[:] = [name for name in dirs if not (Path(top) / name).is_symlink()]
    return found


def _kind(path: Path, data: bytes) -> str:
    """Name what a rewritten file is, for the counts."""
    if data.startswith(b"#!"):
        return "shebang"
    if path.suffix == ".pth":
        return ".pth"
    if path.parent.suffix == ".dist-info":
        return "dist-info"
    return "other text"


def _rewrite(path: Path, pattern: re.Pattern[bytes], new: bytes, write: bool) -> bool:
    """Rewrite one file in place, keeping its inode and mode; return whether it changed."""
    try:
        with path.open("rb") as handle:
            if b"\0" in handle.read(_PROBE):
                return False
            _ = handle.seek(0)
            data: bytes = handle.read()
    except OSError:
        return False
    changed: bytes = pattern.sub(new, data)
    if changed == data:
        return False
    if write:
        mode: int = path.stat().st_mode
        if not mode & stat.S_IWUSR:
            path.chmod(mode | stat.S_IWUSR)
        with path.open("r+b") as handle:
            _ = handle.write(changed)
            _ = handle.truncate()
        if not mode & stat.S_IWUSR:
            path.chmod(mode)
    return True


def main(argv: list[str]) -> int:
    """Relocate, or count what would be relocated."""
    parser = argparse.ArgumentParser(description=(__doc__ or "").partition("\n")[0])
    _ = parser.add_argument("--write", action="store_true", help="apply the changes")
    _ = parser.add_argument("old")
    _ = parser.add_argument("new")
    _ = parser.add_argument("roots", nargs="+", type=Path)
    args = parser.parse_args(argv)
    old: str = args.old.rstrip("/")
    new: str = args.new.rstrip("/")
    if old in new:
        parser.error("NEW contains OLD: a second run would rewrite it again")
    pattern: re.Pattern[bytes] = re.compile(re.escape(old.encode()) + rb"(?=[/\"'\s:;,)\]}]|$)")
    counts: Counter[str] = Counter()
    venvs: list[Path] = _venvs(args.roots)
    counts["venvs"] = len(venvs)
    for venv in venvs:
        for top, dirs, files in os.walk(venv):
            dirs[:] = [name for name in dirs if not (Path(top) / name).is_symlink()]
            for name in files:
                path: Path = Path(top) / name
                if path.is_symlink() or not path.is_file():
                    continue
                if _rewrite(path, pattern, new.encode(), args.write):
                    with path.open("rb") as handle:
                        counts[_kind(path, handle.read(2))] += 1
    for root in args.roots:
        for top, dirs, files in os.walk(root):
            for name in dirs + files:
                link: Path = Path(top) / name
                if not link.is_symlink():
                    continue
                target: str = os.readlink(link)
                if not (target == old or target.startswith(old + "/")):
                    continue
                counts["symlink"] += 1
                if args.write:
                    temporary: Path = link.with_name(f".{name}.relocate")
                    os.symlink(new + target[len(old) :], temporary)
                    os.replace(temporary, link)
    print(("changed" if args.write else "would change") + ":")
    for kind, count in sorted(counts.items()):
        print(f"  {kind:<12} {count:>7,}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
