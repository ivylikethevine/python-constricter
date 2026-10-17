# SPDX-License-Identifier: MIT
"""Time corpora as the `timing` step would with no warm-up, alone and side by side on disjoint CPU sets.

  local/.venv/bin/python -m scratch.timed_tail_trial                                # django, sqlalchemy, twisted
  local/.venv/bin/python -m scratch.timed_tail_trial --runs 5 --jobs 4 --cpus-each 5 pint altair click

Each corpus is checked at `suffocate` in one process and with `--jobs`, by `hyperfine -N -i` with no
`--warmup`, `--runs` times a way, so the first run of each way shows what a warm-up would have hidden
(the installed-modules cache is warm from the run's `check` step; a cold one would show as a slow
first run). First each corpus alone, in turn; then every corpus at once, each under `taskset -c` on
its own `--cpus-each` CPUs. For each corpus, way and mode: the runs, the median, the relative
standard deviation and the range, and the instructions where hyperfine counts them; then the
side-by-side medians against the alone ones. Markdown and the raw JSON land in
`local/scratch/timed-tail-trial/`. Outside a sandbox: `--jobs` needs the forkserver's socket. Nothing
else should run meanwhile.
"""

import argparse
import json
import os
import shlex
import statistics
import subprocess
from pathlib import Path

from tests.corpus import catalog, launch, trees
from tests.corpus.run_config import DEV

OUT = Path(__file__).resolve().parents[1] / "local" / "scratch" / "timed-tail-trial"
OPTIONS = ["--level=suffocate", "--exit-zero", "-q", "--output-file", os.devnull]
WAYS = ("one", "every")


def _hyperfine_command(where: launch.Place, way: str, runs: int, jobs: int, exported: Path) -> list[str]:
    count = 1 if way == "one" else jobs
    check = shlex.join(launch.command(DEV, where, OPTIONS, count))
    return ["hyperfine", "-N", "-i", "--runs", str(runs), "--style", "none", "--export-json", str(exported), check]


def _read(exported: Path) -> tuple[list[float], list[float]]:
    measured = json.loads(exported.read_text(encoding="utf-8"))["results"][0]["measurements"]
    seconds = [run["time_wall_clock"]["value"] for run in measured]
    instructions = [run["instructions"]["value"] / 1e9 for run in measured if "instructions" in run]
    return seconds, instructions


def _popen(where: launch.Place, args: list[str], prefix: list[str]) -> subprocess.Popen[str]:
    return subprocess.Popen(
        [*prefix, *args], cwd=where.cwd, env=launch.environment(where), text=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE
    )


def _stats(values: list[float]) -> str:
    median = statistics.median(values)
    rsd = 100 * statistics.stdev(values) / statistics.fmean(values) if len(values) > 1 else 0.0
    spread = 100 * (max(values) - min(values)) / median
    return f"{median:.2f} | {rsd:.1f}% | {spread:.1f}%"


def main() -> int:
    parser = argparse.ArgumentParser(description=(__doc__ or "").splitlines()[0])
    parser.add_argument("corpora", nargs="*", default=["django", "sqlalchemy", "twisted"])
    parser.add_argument("--runs", type=int, default=5)
    parser.add_argument("--jobs", type=int, default=4)
    parser.add_argument("--cpus-each", type=int, default=5)
    args = parser.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    places: dict[str, launch.Place] = {}
    for name in args.corpora:
        tree = trees.found(catalog.load().entry(name), settle=False)
        places[name] = launch.place(tree, OUT / "neutral")

    results: dict[tuple[str, str, str], tuple[list[float], list[float]]] = {}
    # Alone, in turn: each corpus's ways one after the other, as the timing step runs them.
    for name, where in places.items():
        for way in WAYS:
            exported = OUT / f"{name}-alone-{way}.json"
            done = _popen(where, _hyperfine_command(where, way, args.runs, args.jobs, exported), [])
            _, err = done.communicate()
            if done.returncode:
                print(f"{name} alone {way}: hyperfine failed ({done.returncode}): {err[-500:]}")
                return 1
            results[(name, way, "alone")] = _read(exported)
            print(f"{name} alone {way}: done", flush=True)

    # Side by side: every corpus at once, each on its own CPUs, its ways in turn.
    running: list[tuple[str, launch.Place, subprocess.Popen[str]]] = []
    for index, (name, where) in enumerate(places.items()):
        first = index * args.cpus_each
        cpus = f"{first}-{first + args.cpus_each - 1}"
        script = " && ".join(
            shlex.join(_hyperfine_command(where, way, args.runs, args.jobs, OUT / f"{name}-beside-{way}.json")) for way in WAYS
        )
        running.append((name, where, _popen(where, ["sh", "-c", script], ["taskset", "-c", cpus])))
    for name, _, done in running:
        _, err = done.communicate()
        if done.returncode:
            print(f"{name} beside: failed ({done.returncode}): {err[-500:]}")
            return 1
        for way in WAYS:
            results[(name, way, "beside")] = _read(OUT / f"{name}-beside-{way}.json")
        print(f"{name} beside: done", flush=True)

    lines = [
        "| corpus | way | mode | runs (s) | median | rsd | range | first vs rest | G instr median | instr rsd |",
        "| --- | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for (name, way, mode), (seconds, instructions) in sorted(results.items(), key=lambda item: (item[0][0], item[0][1], item[0][2] != "alone")):
        rest = statistics.median(seconds[1:]) if len(seconds) > 1 else seconds[0]
        first = 100 * (seconds[0] - rest) / rest
        instr = f"{statistics.median(instructions):.1f} | {100 * statistics.stdev(instructions) / statistics.fmean(instructions):.2f}%" if len(instructions) > 1 else "- | -"
        lines.append(f"| {name} | {way} | {mode} | {' '.join(f'{s:.2f}' for s in seconds)} | {_stats(seconds)} | {first:+.1f}% | {instr} |")
    lines += ["", "| corpus | way | alone median | beside median | change |", "| --- | --- | ---: | ---: | ---: |"]
    for name in places:
        for way in WAYS:
            alone = statistics.median(results[(name, way, "alone")][0])
            beside = statistics.median(results[(name, way, "beside")][0])
            lines.append(f"| {name} | {way} | {alone:.2f} | {beside:.2f} | {100 * (beside - alone) / alone:+.1f}% |")
    report = "\n".join(lines)
    (OUT / "report.md").write_text(report + "\n", encoding="utf-8")
    print(report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
