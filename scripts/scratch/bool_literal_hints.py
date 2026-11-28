"""Count a run's checker fixes at a binding some checker hints a flag's one value beside other types.

  local/.venv/bin/python -m scripts.scratch.bool_literal_hints corpus-runs/mega-11-27-2026-1715

A checker hints a value whose declared type holds `Literal[True]` or `Literal[False]` (websockets'
`proxy`, `str | Literal[True] | None`) as that union, and `hinted` widened the literal to `bool`, so
after `if proxy is True` a checker still saw `False`. Reads the hint store
(`~/.cache/constricter/hints`) for every hint `hinted.flagged` holds for, where no checker's hint now
types the name; then the run's `infer-union` guesses resting on a checker with `bool` in their
annotation, matched to those sites by file name and line: what the refusal withdraws. Prints the
store's sites and their commonest texts, then the run's fixes there by kind and corpus, how many a
traced run held or differed from, and each one blamed. About two minutes for the store's 2.7 GB on
16CPU/60GB.
"""

import json
import sys
from collections import Counter
from pathlib import Path
from typing import Final, cast

from constricter.fix.values.hinted import flagged
from tests.corpus import archive

STORE: Final = Path.home() / ".cache" / "constricter" / "hints"


def sites() -> tuple[set[tuple[str, int]], Counter[str]]:
    """Find the store's hints that `lone` holds for.

    Returns:
      Their file names and lines, and how often each text was hinted.

    """
    found: set[tuple[str, int]] = set()
    texts: Counter[str] = Counter()
    entry: Path
    for entry in STORE.glob("*.json"):
        raw: str = entry.read_text(encoding="utf-8")
        if "Literal[True]" not in raw and "Literal[False]" not in raw:
            continue
        hints: dict[str, dict[str, list[object]]] = json.loads(raw).get("found", {})
        path: str
        by_place: dict[str, list[object]]
        for path, by_place in hints.items():
            where: str
            value: list[object]
            for where, value in by_place.items():
                text: str = str(value[0])
                if flagged(text):
                    found.add((Path(path).name, int(where.partition(":")[0])))
                    texts[text] += 1
    return found, texts


def main() -> None:
    """Print the counts for the run folder given."""
    folder: Path = Path(sys.argv[1])
    places: set[tuple[str, int]]
    texts: Counter[str]
    places, texts = sites()
    print(f"store: {len(places)} sites")
    text: str
    count: int
    for text, count in texts.most_common(10):
        print(f"  {count:6}  {text}")
    rows: list[archive.Record] = [
        row
        for row in archive.listed(folder, archive.GUESSES)
        if row.get("fix") == "infer-union"
        and "checker" in str(row.get("kinds", "")).split("+")
        and "bool" in str(row["annotation"])
    ]
    hit: list[archive.Record] = [
        row for row in rows if (Path(str(row["path"])).name, int(str(row["line"]))) in places
    ]
    verdicts: list[list[int]] = [cast("list[int]", row["verdict"]) for row in hit]
    print(f"run: {len(hit)} of {len(rows)} checker fixes naming `bool` at those sites")
    print("kinds:", dict(Counter(str(row["kinds"]) for row in hit)))
    print("corpora:", dict(Counter(str(row["package"]) for row in hit).most_common(10)))
    print(
        "held by a traced run:",
        sum(1 for verdict in verdicts if verdict[0]),
        "differed:",
        sum(1 for verdict in verdicts if verdict[1]),
    )
    row: archive.Record
    for row in hit:
        if int(str(row.get("errors", 0))):
            print(
                f"  {row['package']} {row['path']}:{row['line']} {row['name']}: {row['annotation']} "
                f"[{row['kinds']}] errors={row['errors']}",
            )


if __name__ == "__main__":
    main()
