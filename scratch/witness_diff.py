"""Compare two runs' differing traced fixes: those the witness found differing in one run and not the other.

  local/.venv/bin/python -m scratch.witness_diff OLD_RUN NEW_RUN [TIER=certain]

Reads each run's verdicts from its `listings.jsonl` (a stopped run's, each corpus's under
`records/`) and keys a fix by its corpus, path, name and annotation (its line moves with the fixes
above it). Prints the fixes that differ in the new run alone, then those in the old alone, each
with its line, its kinds and the types the trace saw, and what the other run's traced fix of that
binding was (`no fix` where it made none), and the counts.
"""

import json
import sys
from pathlib import Path

from tests.corpus import archive

_Key = tuple[str, str, str, str]


def verdicts(run: Path) -> list[tuple[str, dict]]:
    """Read every verdict in `run`, with its corpus's directory: the run's one listing, or each corpus's."""
    if (run / archive.LISTED).is_file():  # a finished run's, every corpus's lines with its corpus
        return [(row["corpus"].replace(" ", "-"), row) for row in archive.listed(run, "verdicts")]
    return [
        (path.parts[-3], json.loads(line))
        for path in sorted(run.glob("records/*/*/traced.verdicts.jsonl"))
        for line in path.read_text(encoding="utf-8").splitlines()
    ]


def differing(run: Path, tier: str) -> dict[_Key, list[str]]:
    """Read each fix of `tier` a traced value didn't fit in `run`, with what the trace saw."""
    found: dict[_Key, list[str]] = {}
    for corpus, row in verdicts(run):
        if row["tier"] == tier and row["verdict"][1]:
            found[corpus, row["path"], row["name"], row["annotation"]] = [
                f"line {row['line']}",
                "+".join(row["kinds"]),
                *row["seen"],
            ]
    return found


def told(run: Path) -> dict[tuple[str, str, str], str]:
    """Read every traced fix in `run`, a test told of or not: its corpus, path and name to its annotation."""
    return {(corpus, row["path"], row["name"]): row["annotation"] for corpus, row in verdicts(run)}


def main() -> int:
    old: dict[_Key, list[str]] = differing(Path(sys.argv[1]), sys.argv[3] if len(sys.argv) > 3 else "certain")
    new: dict[_Key, list[str]] = differing(Path(sys.argv[2]), sys.argv[3] if len(sys.argv) > 3 else "certain")
    for title, these, those, other in (
        ("new alone", new, old, Path(sys.argv[1])),
        ("old alone", old, new, Path(sys.argv[2])),
    ):
        alone = sorted(set(these) - set(those))
        made: dict[tuple[str, str, str], str] = told(other)
        print(f"## {title}: {len(alone)}")
        for key in alone:
            line, kinds, *seen = these[key]
            there: str = made.get(key[:3], "no fix")
            print(" | ".join(key), f"| {line} | {kinds} | other run: {there} | seen:", ", ".join(seen[:4]))
    print(f"old {len(old)}, new {len(new)}, both {len(set(old) & set(new))}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
