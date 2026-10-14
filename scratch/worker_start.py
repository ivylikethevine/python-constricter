# SPDX-License-Identifier: MIT
"""Time a `--jobs` check of one-line files, mostly its workers' start, by `python -m` and by the script.

  local/.venv/bin/python -m scratch.worker_start                          # this checkout
  local/.venv/bin/python -m scratch.worker_start ROOT ... [--jobs 8] [--runs 20]

Each ROOT's constricter (on `PYTHONPATH`, ahead of the editable install; its tables generated:
copy `constricter/fix/tables/` into a worktree) checks as many one-line files as `--jobs`, run as
`python -m constricter` and as `local/.venv/bin/constricter`, whose fork server imports the script
and so constricter, where under `-m` it imports nothing. And with `--jobs=1`, which starts no
worker: the difference is the workers' start. `hyperfine` times each (one warm-up run); its
medians and the instructions each run took print as a table, and its JSON is kept in
`local/scratch/worker-start/`. Outside a sandbox: the fork server needs a socket.

  local/.venv/bin/python -m scratch.worker_start --alone [--jobs 8] [--runs 20]

With `--alone`, in this process, through `constricter.cli.workers.Workers` as a run starts them:
the fork server's own start (it preloads constricter), then, `--runs` times, `--jobs` workers
started and each asked one empty task, their median milliseconds, one's alone too; and the fork
server's and one worker's resident and proportional set sizes, from `/proc`.
"""

import argparse
import json
import os
import shlex
import statistics
import subprocess
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
OUT = HERE / "local" / "scratch" / "worker-start"
BIN = HERE / "local" / ".venv" / "bin"


def _memory(pid: int) -> str:
    """Read a process's resident and proportional set sizes, in MB."""
    rollup = Path(f"/proc/{pid}/smaps_rollup").read_text(encoding="utf-8").splitlines()
    sizes = {line.split()[0].rstrip(":"): int(line.split()[1]) for line in rollup[1:]}
    return f"RSS {sizes['Rss'] / 1024:.0f} MB, PSS {sizes['Pss'] / 1024:.0f} MB"


def alone(jobs: int, runs: int) -> None:
    """Time workers' start as a run starts them, and read the fork server's memory."""
    import multiprocessing.forkserver  # noqa: PLC0415
    import time  # noqa: PLC0415

    from constricter.cli import schedule  # noqa: PLC0415
    from constricter.cli.workers import Workers  # noqa: PLC0415
    from constricter.fix.index import project  # noqa: PLC0415

    empty = schedule.sent(project.Index({}, []))

    def started(count: int) -> float:
        start = time.perf_counter()
        with Workers([Path(f"m{at}.py") for at in range(count)], count) as workers:
            workers.tell(schedule.know, empty)
            return 1000 * (time.perf_counter() - start)

    print(f"first start, with the fork server's: {started(1):.1f} ms")
    server = multiprocessing.forkserver._forkserver._forkserver_pid  # noqa: SLF001
    print(f"fork server: {_memory(server)}")
    for count in sorted({1, jobs}):
        times = [started(count) for _ in range(runs)]
        print(f"{count} worker(s): median {statistics.median(times):.1f} ms, min {min(times):.1f} ms")
    with Workers([Path("m.py")], 1) as workers:
        workers.tell(schedule.know, empty)
        pid = workers.pools[0].submit(os.getpid).result()
        print(f"one worker: {_memory(pid)}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("roots", nargs="*", type=Path, default=[HERE])
    parser.add_argument("--jobs", type=int, default=8)
    parser.add_argument("--runs", type=int, default=20)
    parser.add_argument("--alone", action="store_true")
    args = parser.parse_args()
    if args.alone:
        alone(args.jobs, args.runs)
        return 0
    OUT.mkdir(parents=True, exist_ok=True)
    rows = ["| checkout | run as | jobs | median ms | G instructions |", "|---|---|---|---|---|"]
    with tempfile.TemporaryDirectory() as files:
        for at in range(args.jobs):
            (Path(files) / f"m{at}.py").write_text(f"x{at}: int = {at}\n", encoding="utf-8")
        for root in args.roots:
            env = {**os.environ, "PYTHONPATH": str(root.resolve())}
            for way, command in (("-m", [str(BIN / "python"), "-m", "constricter"]), ("script", [str(BIN / "constricter")])):
                for jobs in (1, args.jobs):
                    exported = OUT / f"{root.resolve().name}-{way.strip('-')}-{jobs}.json"
                    line = shlex.join([*command, "-q", f"--jobs={jobs}", files])
                    subprocess.run(
                        ["hyperfine", "-N", "-i", "--warmup", "1", "--runs", str(args.runs), "--style", "none",
                         "--export-json", str(exported), line],
                        check=True, env=env, cwd=files,
                    )
                    measured = json.loads(exported.read_text(encoding="utf-8"))["results"][0]["measurements"]
                    seconds = statistics.median(run["time_wall_clock"]["value"] for run in measured)
                    counted = [run.get("instructions", {}).get("value") for run in measured]
                    instructions = statistics.median(counted) / 1e9 if None not in counted else float("nan")
                    rows.append(f"| {root} | {way} | {jobs} | {1000 * seconds:.0f} | {instructions:.2f} |")
    print("\n".join(rows))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
