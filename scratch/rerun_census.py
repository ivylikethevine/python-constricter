"""A corpus run's fixed test runs that weren't the released tests', and what the `tests` step made of each.

    local/.venv/bin/python -m scratch.rerun_census corpus-runs/FOLDER

For every suite's `tests` record: each fixed run whose first outcome wasn't the released tests'
(not one implied by another part, nor one whose patch was refused), with its counts, how many
failures were new and gone, whether its other counts were some released run's (`calm`), whether it
differs, how many times it ran again, and the released tests' samples the run had (`samples`,
`again`). Prints a line a run, then the totals: the runs that ran again, and those with nothing
new or gone that did.
"""

import json
import sys
from pathlib import Path


def main(argv: list[str]) -> int:
    folder: Path = Path(argv[0])
    rows: list[tuple[str, str, dict[str, int], int, int, bool | None, bool, int]] = []
    samples: dict[str, list[str]] = {}
    for path in sorted(folder.glob("records/*/*/tests.json")):
        corpus: str = path.parents[1].name
        record = json.loads(path.read_text(encoding="utf-8"))
        samples[corpus] = sorted(record.get("samples", {})) + (["again"] if "again" in record else [])
        for step, ran in record.get("fixed", {}).items():
            if ran.get("same") or "implied" in ran or "error" in ran:
                continue
            rows.append(
                (
                    corpus,
                    step,
                    ran["counts"],
                    len(ran.get("new", [])),
                    len(ran.get("gone", [])),
                    ran.get("calm"),
                    bool(ran.get("differs")),
                    len(ran.get("again", [])),
                ),
            )
    for corpus, step, counts, new, gone, calm, differs, again in rows:
        print(f"{corpus:20} {step:20} {counts} new {new} gone {gone} calm {calm} differs {differs} again {again}")
    for corpus, had in samples.items():
        if had:
            print(f"{corpus}: samples {', '.join(had)}")
    reran: int = sum(1 for row in rows if row[7])
    idle: int = sum(1 for row in rows if row[7] and not row[3] and not row[4])
    print(f"{len(rows)} fixed runs weren't the released tests'; {reran} ran again, {idle} of them with nothing new or gone")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
