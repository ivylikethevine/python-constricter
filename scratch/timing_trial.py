# SPDX-License-Identifier: MIT
"""Time a corpus's check as the `timing` step does, then by `hyperfine` and `pyperf`, and compare their spreads.

  local/.venv/bin/python -m scratch.timing_trial                              # the standard library and pandas
  local/.venv/bin/python -m scratch.timing_trial --runs 10 --jobs 8 pandas    # one corpus, so many runs, so many workers

Each corpus is checked at `suffocate` in one process and with `--jobs`, the command `launch.run`
starts. First as `pipeline.timing` does (the two ways in turn, timed by `perf_counter`, no warm-up),
then by `hyperfine -N --warmup 1`, then by `pyperf command` (a process a value, no warm-up), each
way's runs back to back. For each method and way: the median, mean, standard deviation, relative
deviation, the range and hyperfine's warnings, and the same of the instructions each run took, where
hyperfine counts them (`perf_event_paranoid` permitting); a Markdown
table and the raw runs in `local/scratch/timing-trial/`. A suite's checkout is used as it is, not
reset. A check's exit status is ignored (the standard library's is 2: some of its files don't
parse): by `hyperfine -i`, and for `pyperf`, which has no such option, by `sh -c '...; exit 0'`.
Each method's runs are kept as it ends. Outside a sandbox: `--jobs` needs the forkserver's socket. Nothing else should run meanwhile.
"""

import argparse
import json
import os
import shlex
import statistics
import subprocess
import time
from pathlib import Path

from tests.corpus import catalog, launch, trees
from tests.corpus.run_config import DEV

OUT = Path(__file__).resolve().parents[1] / "local" / "scratch" / "timing-trial"
OPTIONS = ["--level=suffocate", "--exit-zero", "-q", "--output-file", os.devnull]


def stats(seconds: list[float]) -> dict[str, float]:
    mean = statistics.fmean(seconds)
    deviation = statistics.stdev(seconds) if len(seconds) > 1 else 0.0
    return {
        "median": statistics.median(seconds),
        "mean": mean,
        "stdev": deviation,
        "rsd %": 100 * deviation / mean,
        "min": min(seconds),
        "max": max(seconds),
        "range %": 100 * (max(seconds) - min(seconds)) / statistics.median(seconds),
    }


def step(where: launch.Place, runs: int, jobs: int) -> dict[str, list[float]]:
    found: dict[str, list[float]] = {"one": [], "every": []}
    for _ in range(runs):
        found["one"].append(launch.run(DEV, where, OPTIONS, 1).seconds)
        found["every"].append(launch.run(DEV, where, OPTIONS, jobs).seconds)
    return found


def hyperfine(where: launch.Place, runs: int, jobs: int, name: str) -> tuple[dict[str, list[float]], list[str]]:
    found: dict[str, list[float]] = {}
    warnings: list[str] = []
    for way, count in (("one", 1), ("every", jobs)):
        exported = OUT / f"{name}-hyperfine-{way}.json"
        command = shlex.join(launch.command(DEV, where, OPTIONS, count))
        done = subprocess.run(
            ["hyperfine", "-N", "-i", "--warmup", "1", "--runs", str(runs), "--style", "basic",
             "--export-json", str(exported), command],
            capture_output=True, text=True, check=True, cwd=where.cwd, env=launch.environment(where),
        )
        measured = json.loads(exported.read_text(encoding="utf-8"))["results"][0]["measurements"]
        found[way] = [run["time_wall_clock"]["value"] for run in measured]
        if "instructions" in measured[0]:  # hyperfine 2's hardware counters: billions of instructions
            found[f"{way} (G instr)"] = [run["instructions"]["value"] / 1e9 for run in measured]
        warnings += [f"{way}: {line.strip()}" for line in done.stderr.splitlines() if "Warning" in line]
    return found, warnings


def pyperf(where: launch.Place, runs: int, jobs: int, name: str) -> dict[str, list[float]]:
    found: dict[str, list[float]] = {}
    for way, count in (("one", 1), ("every", jobs)):
        exported = OUT / f"{name}-pyperf-{way}.json"
        exported.unlink(missing_ok=True)
        _ = subprocess.run(
            ["pyperf", "command", "-q", "--copy-env", "-p", str(runs), "-n", "1", "-w", "0", "-l", "1",
             "-o", str(exported), "sh", "-c", '"$@"; exit 0', "sh", *launch.command(DEV, where, OPTIONS, count)],
            capture_output=True, text=True, check=True, cwd=where.cwd, env=launch.environment(where),
        )
        benchmark = json.loads(exported.read_text(encoding="utf-8"))["benchmarks"][0]
        found[way] = [value for run in benchmark["runs"] for value in run.get("values", [])]
    return found


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("corpora", nargs="*", default=["standard library", "pandas"])
    parser.add_argument("--runs", type=int, default=10)
    parser.add_argument("--jobs", type=int, default=os.cpu_count() or 1)
    args = parser.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    lines = [
        f"{args.runs} runs each, `--jobs={args.jobs}` for `every`, {time.strftime('%Y-%m-%d %H:%M')}.",
        "",
        "| corpus | method | way | median | mean | stdev | rsd % | min | max | range % |",
        "|---|---|---|---|---|---|---|---|---|---|",
    ]
    for name in args.corpora:
        tree = trees.found(catalog.load().entry(name), settle=False)
        where = launch.place(tree, OUT / "neutral")
        slug = name.replace(" ", "-").replace("/", "-")
        kept = OUT / f"{slug}.json"
        raw: dict[str, object] = {}
        print(f"{name}: step", flush=True)
        by_step = raw["step"] = step(where, args.runs, args.jobs)
        kept.write_text(json.dumps(raw, indent=1), encoding="utf-8")
        print(f"{name}: hyperfine", flush=True)
        by_hyperfine, warnings = hyperfine(where, args.runs, args.jobs, slug)
        raw |= {"hyperfine": by_hyperfine, "warnings": warnings}
        kept.write_text(json.dumps(raw, indent=1), encoding="utf-8")
        print(f"{name}: pyperf", flush=True)
        by_pyperf = raw["pyperf"] = pyperf(where, args.runs, args.jobs, slug)
        kept.write_text(json.dumps(raw, indent=1), encoding="utf-8")
        for method, found in (("step", by_step), ("hyperfine", by_hyperfine), ("pyperf", by_pyperf)):
            for way, seconds in found.items():
                row = " | ".join(f"{value:.2f}" for value in stats(seconds).values())
                lines.append(f"| {name} | {method} | {way} | {row} |")
        lines += [f"| {name} | hyperfine warns | {warning} | | | | | | | |" for warning in warnings]
    report = "\n".join(lines) + "\n"
    (OUT / f"report-{time.strftime('%Y-%m-%d-%H%M')}.md").write_text(report, encoding="utf-8")
    print(report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
