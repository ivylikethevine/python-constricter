# SPDX-License-Identifier: MIT
"""Fix a copy of one corpus as a run's fix step does, and print what a second pass would still fix.

  local/.venv/bin/python -m scratch.second_pass CORPUS [OPTION ...]   # `--unsafe-fixes`, `--likely`
  local/.venv/bin/python -m scratch.second_pass --code DIR --label old CORPUS --likely   # another copy's code

The copy is kept in `local/scratch/second-pass/LABEL/CORPUS/`, fixed once: the diff printed is the
second pass's (`--diff`). `--code` runs the `constricter` package under DIR (`python -P`, DIR on
`PYTHONPATH`), else this checkout's; `--jobs` defaults to 1, so it runs in a sandbox. Standard error
gets the first pass's summary line and seconds; `local/scratch/second-pass/LABEL/CORPUS.fixes` each
fix the first pass made, sorted, to diff against another label's.
"""

import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path

from tests.corpus import catalog, launch, trees

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "local" / "scratch" / "second-pass"


def run(code: Path, where: launch.Place, options: list[str], jobs: int) -> tuple[str, float]:
    command = launch.command("dev", where, options, jobs)
    command[1:2] = ["-P"]  # `-I` would ignore `PYTHONPATH`
    environment = launch.environment(where) | {"PYTHONPATH": str(code)}
    start = time.perf_counter()
    done = subprocess.run(command, capture_output=True, text=True, check=False, cwd=where.cwd, env=environment)
    return done.stdout, time.perf_counter() - start


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--code", type=Path, default=ROOT)
    parser.add_argument("--label", default="dev")
    parser.add_argument("--jobs", type=int, default=1)
    parser.add_argument("corpus")
    args, extra = parser.parse_known_args()
    name = args.corpus.replace(" ", "-")
    tree = trees.found(catalog.load().entry(args.corpus))
    where, _ = launch.copied(tree, OUT / args.label / name)
    options = [*extra, "--level=suffocate"]
    output, seconds = run(args.code, where, ["--fix", "--show-fixes", "--format=json", *options], args.jobs)
    made = sorted(
        f"{entry['path']}:{entry['line']}: {entry['message']} -> {entry['fix']['annotation']}"
        f" {sorted(entry['fix']['kinds'])} {'likely' if entry['fix']['likely'] else ''}"
        for entry in json.loads(output)
        if entry.get("fixed")
    )
    _ = (OUT / args.label / f"{name}.fixes").write_text("".join(f"{line}\n" for line in made), encoding="utf-8")
    print(f"{args.label}: fixed {len(made)} in {seconds:.1f}s", file=sys.stderr)
    second, _ = run(args.code, where, ["--diff", *options], args.jobs)
    print(second)
    return 0


if __name__ == "__main__":
    os.environ.pop("PYTHONPATH", None)
    sys.exit(main())
