"""Pack run folders as `corpus-runs/` commits a run's: its `report.json` and its `listings.jsonl.gz`.

  local/.venv/bin/python scratch/pack_run.py DEST FOLDER...

For each FOLDER (a run's as `python -m tests.corpus` wrote it, or as an earlier layout committed
it), writes DEST/<its name>/report.json, its report with every table (`tables/*.csv`) under
`tables`, and DEST/<its name>/listings.jsonl.gz, its guesses and each listing `archive.LISTINGS` names,
a line each with its listing, corpus and version (`archive.gather`'s format): from the folder's
run-level listing files where it has them, else gathered from its corpora's under `records/`. Every
text is scrubbed as a run writes it (`run_config.scrubbed`). DEST may be FOLDER's own parent, to
pack it in place; another folder of its name in DEST is left as it is. Writes nothing else and
removes nothing.
"""

import csv
import gzip
import json
import sys
from pathlib import Path

from tests.corpus import archive
from tests.corpus.run_config import REPORT, scrubbed


def _lines(path: Path) -> list[dict]:
    return (
        [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()] if path.is_file() else []
    )


def pack(folder: Path, dest: Path) -> list[Path]:
    """Write `folder`'s report and listings into `dest`, scrubbed."""
    dest.mkdir(parents=True, exist_ok=True)
    report = json.loads((folder / REPORT).read_text(encoding="utf-8"))
    if not report.get("tables"):
        report["tables"] = {}
        for table in sorted((folder / "tables").glob("*.csv")):
            with table.open(encoding="utf-8", newline="") as file:
                report["tables"][table.stem] = list(csv.reader(file))
    corpora = [
        (corpus, version) for corpus, versions in report[archive.RECORDS].items() for version in versions
    ]
    lines = [{archive.LISTING: archive.GUESSES} | row for row in _lines(folder / "guesses.jsonl")]
    for name, step, suffix in archive.LISTINGS:
        whole = folder / f"{step}{suffix}"  # an earlier layout's run-level file, with each line's corpus
        if whole.is_file():
            lines += [{archive.LISTING: name} | row for row in _lines(whole)]
            continue
        for corpus, version in corpora:
            path = folder / archive.RECORDS / corpus.replace(" ", "-") / version / f"{step}{suffix}"
            head = {archive.LISTING: name, "corpus": corpus, "constricter": version}
            lines += [head | row for row in _lines(path)]
    (dest / REPORT).write_text(scrubbed(json.dumps(report, indent=2)) + "\n", encoding="utf-8")
    written = [dest / REPORT]
    if lines:
        written.append(dest / archive.LISTED)
        text = scrubbed("".join(f"{json.dumps(line)}\n" for line in lines)).encode("utf-8")
        written[-1].write_bytes(gzip.compress(text, compresslevel=9, mtime=0))
    return written


def main(argv: list[str]) -> int:
    dest: Path = Path(argv[0])
    for folder in map(Path, argv[1:]):
        target = dest / folder.name
        if target.exists() and target.resolve() != folder.resolve():
            print(f"{target} is there: left as it is")
            continue
        written = pack(folder, target)
        print(
            f"{folder.name}: {', '.join(f'{path.name} {path.stat().st_size / 1e6:.1f} MB' for path in written)}"
        )
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
