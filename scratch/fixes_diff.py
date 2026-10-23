"""Compare two `--show-fixes` outputs of one package fixed by two versions of the code.

  local/.venv/bin/python -m scratch.fixes_diff OLD.out NEW.out --strip /tmp/x/sa-old/ --strip /tmp/x/sa-new/

Each file is standard output of `constricter --fix --show-fixes ...` on its own copy of the package
(`--strip` takes each copy's root off the paths, so the copies compare by their relative paths).
Prints the fixes only the old output has (withdrawn), only the new one has (added), and those whose
annotation changed, each with its file, line, name and annotation.
"""

import argparse
import re
from pathlib import Path

_FIXED = re.compile(
    r"^(?P<path>.*?):(?P<line>\d+):(?P<col>\d+): fixed '(?P<name>\w+)': `(?P<fix>.*?)`, from (?P<how>.*)$"
)


def fixes(output: Path, strip: list[str]) -> dict[tuple[str, int, int, str], tuple[str, str]]:
    """Read the fixes an output lists, by file, line, column and name.

    Returns:
      Each one's annotation and reason.

    """
    found: dict[tuple[str, int, int, str], tuple[str, str]] = {}
    for line in output.read_text(encoding="utf-8").splitlines():
        if (match := _FIXED.match(line)) is None:
            continue
        path: str = match["path"]
        for prefix in strip:
            path = path.removeprefix(prefix)
        found[path, int(match["line"]), int(match["col"]), match["name"]] = (match["fix"], match["how"])
    return found


def main() -> int:
    parser = argparse.ArgumentParser(description=(__doc__ or "").splitlines()[0])
    parser.add_argument("old", type=Path)
    parser.add_argument("new", type=Path)
    parser.add_argument("--strip", action="append", default=[], help="a prefix to take off the paths")
    args = parser.parse_args()
    old = fixes(args.old, args.strip)
    new = fixes(args.new, args.strip)
    print(f"old {len(old)} fixes, new {len(new)}")
    for title, keys in (
        ("withdrawn", [key for key in old if key not in new]),
        ("added", [key for key in new if key not in old]),
        ("changed", [key for key in old if key in new and old[key][0] != new[key][0]]),
    ):
        print(f"{title}: {len(keys)}")
        for key in keys:
            was: str = f"{old[key][0]} -> " if title == "changed" else ""
            fix, how = new[key] if key in new else old[key]
            print(f"  {key[0]}:{key[1]} {key[3]}: {was}{fix}  ({how[:70]})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
