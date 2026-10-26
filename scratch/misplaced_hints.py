"""Find a corpus run's checker fixes that can't be the value's type: a hint applied to the wrong name.

  local/.venv/bin/python -m scratch.misplaced_hints corpus-runs/0.4.0-rc.3-10-18-2026-1010 pandas local/corpus-suites/pandas-v3.0.6/pandas

Reads each `records/<corpus>/<version>/infer-*.fixes.jsonl` of the run, and for every fix whose
only mechanism is `checker` looks up the binding's line in the package's source (`ROOT`, the
directory the fixes' paths are relative to): a name bound to an empty display (`{}`, `[]`, `set()`)
whose annotation isn't a container's is a hint that belongs to another name (one with the same end
column some lines below, by the declaration lines an earlier round inserted above it). Prints each,
and the count against every checker fix on an empty display.
"""

import argparse
import json
import re
from pathlib import Path

_EMPTY = r"\s*{name}\s*=\s*(\{{\}}|\[\]|set\(\)|dict\(\)|list\(\))\s*(#.*)?$"
_CONTAINERS = (
    "dict",
    "list",
    "set",
    "Dict",
    "List",
    "Set",
    "defaultdict",
    "collections",
    "Mapping",
    "MutableMapping",
)


def main() -> int:
    parser = argparse.ArgumentParser(description=(__doc__ or "").splitlines()[0])
    parser.add_argument("run", type=Path)
    parser.add_argument("corpus")
    parser.add_argument("root", type=Path)
    args = parser.parse_args()
    empty = 0
    misplaced = 0
    for fixes in sorted((args.run / "records" / args.corpus).glob("*/infer-*.fixes.jsonl")):
        for line in fixes.read_text(encoding="utf-8").splitlines():
            fix = json.loads(line)
            if fix["kinds"] != ["checker"]:
                continue
            try:
                source = (args.root / fix["path"]).read_text(encoding="utf-8").splitlines()[fix["line"] - 1]
            except (OSError, IndexError, UnicodeDecodeError):
                continue
            if re.match(_EMPTY.format(name=re.escape(fix["name"])), source) is None:
                continue
            empty += 1
            if not fix["annotation"].startswith(_CONTAINERS):
                misplaced += 1
                print(
                    f"{fixes.name}: {fix['path']}:{fix['line']} {fix['name']}: {fix['annotation']}  | {source.strip()}"
                )
    print(f"misplaced {misplaced} of {empty} checker fixes on an empty display")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
