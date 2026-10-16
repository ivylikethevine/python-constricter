"""Each corpus's size and time from a finished run's records, to sort the corpora into four groups.

Reads `records/<corpus>/<label>/*.json` under each run folder given: files from `check.json`, and
the wall and CPU seconds of every step (`used.seconds`, `used.cpu`, else `seconds`). Prints one row
per corpus, sorted by wall seconds, with the medians the groups split at.

    python3 scratch/corpus_quadrants.py local/corpus-runs/super-... local/corpus-runs/mega-...
"""

import json
import statistics
import sys
from pathlib import Path


def main() -> None:
    rows: list[tuple[str, int, float, float]] = []
    for run in map(Path, sys.argv[1:]):
        for corpus in sorted((run / "records").iterdir()):
            for label in corpus.iterdir():
                files, wall, cpu = 0, 0.0, 0.0
                for record in label.glob("*.json"):
                    data = json.loads(record.read_text())
                    if record.name == "check.json":
                        files = data.get("files", 0)
                    used = data.get("used") or {}
                    wall += used.get("seconds", data.get("seconds", 0.0)) or 0.0
                    cpu += used.get("cpu", 0.0) or 0.0
                rows.append((corpus.name, files, wall, cpu))
    size = statistics.median(row[1] for row in rows)
    time = statistics.median(row[2] for row in rows)
    print(f"median files {size:g}, median wall seconds {time:.0f}")
    print(f"{'corpus':<20} {'files':>6} {'wall s':>8} {'cpu s':>8}  group")
    for name, files, wall, cpu in sorted(rows, key=lambda row: row[2]):
        group = f"{'slow' if wall > time else 'fast'}-{'large' if files > size else 'small'}"
        print(f"{name:<20} {files:>6} {wall:>8.0f} {cpu:>8.0f}  {group}")


if __name__ == "__main__":
    main()
