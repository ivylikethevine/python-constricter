"""Count a run's third-party calls with no fix whose package typeshed's third-party stubs cover.

  local/.venv/bin/python scratch/typeshed_reach.py RUN_FOLDER [STUBS_DIR]

STUBS_DIR defaults to the dev venv's basedpyright `typeshed-fallback/stubs` (201 sets), each set's
top-level packages and modules read from its directory. Reads each corpus's `census.rows.jsonl`:
a binding with neither a fix nor a guess, from a third-party call (`origin` "third-party"), counted
under the stub set covering its dotted name's first part, with the census's reason it has no fix
(`unfixed`). Prints the reach by set and by reason, and the corpora each set's calls are in.
"""

import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

_VENV = Path(__file__).resolve().parents[1] / ".venv"


def covered(stubs: Path) -> dict[str, str]:
    """Each top-level package or module a stub set types, to the set's name."""
    found: dict[str, str] = {}
    for each in sorted(stubs.iterdir()):
        for part in each.iterdir():
            name: str = part.name.removesuffix(".pyi").removesuffix("-stubs")
            if part.name != "METADATA.toml" and not part.name.startswith("@"):
                found.setdefault(name, each.name)
    return found


def main(argv: list[str]) -> int:
    run: Path = Path(argv[0])
    stubs: Path = (
        Path(argv[1])
        if len(argv) > 1
        else next(_VENV.glob("lib/python3.*/site-packages/basedpyright/dist/typeshed-fallback/stubs"))
    )
    sets: dict[str, str] = covered(stubs)
    reach: Counter[str] = Counter()
    reasons: Counter[str] = Counter()
    corpora: dict[str, set[str]] = defaultdict(set)
    third: int = 0
    for path in sorted(run.glob("records/*/*/census.rows.jsonl")):
        for line in path.read_text(encoding="utf-8").splitlines():
            row = json.loads(line)
            if row["fixed"] or row["unsafe"] or row["origin"] != "third-party" or not row["dotted"]:
                continue
            third += 1
            stub: str | None = sets.get(row["dotted"].split(".", 1)[0])
            if stub is not None:
                reach[stub] += 1
                reasons[row["unfixed"] or "(none)"] += 1
                corpora[stub].add(row["corpus"])
    print(
        f"{third:,} third-party bindings with no fix; {sum(reach.values()):,} into a package typeshed stubs\n"
    )
    print("| Stub set | Bindings | Corpora |")
    print("| --- | ---: | --- |")
    for stub, count in reach.most_common():
        print(f"| {stub} | {count:,} | {', '.join(sorted(corpora[stub]))} |")
    print("\n| Why no fix | Bindings |")
    print("| --- | ---: |")
    for reason, count in reasons.most_common():
        print(f"| {reason} | {count:,} |")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
