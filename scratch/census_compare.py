"""One corpus's census by the working tree's code, against a finished run's census rows for it.

    CORPUS_JOBS=1 local/.venv/bin/python -m scratch.census_compare corpus-runs/FOLDER NAME ROOT

ROOT is the directory the run checked for NAME (the installed package's, or a source's). Runs the
census as the runner's `census` step does (`tests.corpus.corpus_untyped.census`), then prints the
untyped bindings and those with no fix on each side, and the ones with no fix by `unfixed` reason
(the call's) or shape (any other value's), commonest first. One process; xarray about a minute on
16CPU/60GB. The run's own environment may resolve imports differently: compare the counts, not
binding by binding.
"""

import json
import sys
from collections import Counter
from pathlib import Path

from tests.corpus.corpus_table import Corpus
from tests.corpus.corpus_untyped import census


def _key(row: dict[str, object]) -> str:
    return str(row["unfixed"] or row["shape"])


def main() -> int:
    folder: Path = Path(sys.argv[1])
    name: str = sys.argv[2]
    root: Path = Path(sys.argv[3]).resolve()
    before: list[dict[str, object]] = [
        json.loads(line)
        for path in folder.glob(f"records/{name}/*/census.rows.jsonl")
        for line in path.read_text(encoding="utf-8").splitlines()
    ]
    after: list[dict[str, object]] = [binding._asdict() for binding in census(Corpus(name, "tree", root))[0]]
    sides: dict[str, Counter[str]] = {}
    for label, rows in (("run", before), ("tree", after)):
        missed: list[dict[str, object]] = [row for row in rows if not row["fixed"]]
        sides[label] = Counter(_key(row) for row in missed)
        print(f"{label}: {len(rows):,} untyped, {len(missed):,} with no fix")
    keys: list[str] = [key for key, _ in (sides["run"] + sides["tree"]).most_common(25)]
    for key in keys:
        print(
            f"{sides['run'][key]:7,} {sides['tree'][key]:7,} {sides['tree'][key] - sides['run'][key]:+7,}  {key}"
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
