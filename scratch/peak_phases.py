"""Check a tree in this process, and print its memory over time by the check's phases.

  python scratch/peak_phases.py PATH [-- OPTIONS...]   (from the checkout, as `peak_rss.py`)

A thread samples the process's resident memory (`/proc/self/statm`) every quarter second; the
phases are marked where they start and end: the index (`project.index`), the index settled with the
installed packages' and the plain bases' (`plain.settled`), and the check of every file in its
rounds (`schedule.checked`). Prints each phase's seconds, its memory at its start and end, and the
most it held, then the run's peak (`ru_maxrss`). One process (`--jobs=1`): Linux only.
"""

import os
import resource
import sys
import threading
import time
import tracemalloc
from collections.abc import Callable
from pathlib import Path

sys.path.insert(0, str(Path.cwd()))

from constricter.cli import rounds  # noqa: E402  # from the working directory's checkout
from constricter.cli.command import main  # noqa: E402
from constricter.rules import parsed  # noqa: E402

_PAGE: int = os.sysconf("SC_PAGE_SIZE")
_GIB: int = 1 << 30
samples: list[tuple[float, int]] = []
marks: list[tuple[str, float]] = []
done: threading.Event = threading.Event()


def resident() -> int:
    return int(Path("/proc/self/statm").read_text(encoding="ascii").split()[1]) * _PAGE


def sample() -> None:
    while not done.wait(0.25):
        samples.append((time.perf_counter(), resident()))


def marked(name: str, function: Callable[..., object]) -> Callable[..., object]:
    def wrapper(*args: object, **kwargs: object) -> object:
        marks.append((f"{name} starts", time.perf_counter()))
        samples.append((time.perf_counter(), resident()))
        try:
            return function(*args, **kwargs)
        finally:
            samples.append((time.perf_counter(), resident()))
            marks.append((f"{name} ends", time.perf_counter()))

    return wrapper


args: list[str] = sys.argv[1:]
# `--no-index-trees`: the index keeps none of its trees for the check, which parses each again; a
# check still keeps a resumable module's (`checker.checked_source`).
indexing: list[bool] = [False]
if "--no-index-trees" in args:
    args.remove("--no-index-trees")
    kept: Callable[..., None] = parsed.keep

    def keep(source: str, tree: parsed.Kept) -> None:
        if not indexing[0]:
            kept(source, tree)

    parsed.keep = keep


def index(*given: object, **named: object) -> object:
    indexing[0] = True
    try:
        return found(*given, **named)
    finally:
        indexing[0] = False


# `--trace-check`: what the first check's rounds allocate and still hold as they end, by line.
tracing: bool = "--trace-check" in args
if tracing:
    args.remove("--trace-check")
    checked: Callable[..., object] = rounds.schedule.checked

    def traced(*given: object, **named: object) -> object:
        if tracemalloc.is_tracing() or not tracing:
            return checked(*given, **named)
        tracemalloc.start(8)
        try:
            return checked(*given, **named)
        finally:
            snapshot: tracemalloc.Snapshot = tracemalloc.take_snapshot()
            tracemalloc.stop()
            stat: tracemalloc.Statistic
            for stat in snapshot.statistics("traceback")[:20]:
                print(f"{stat.size / _GIB:6.3f} GiB {stat.count:9} blocks", file=sys.stderr)
                print("\n".join(f"    {line}" for line in stat.traceback.format(limit=6)), file=sys.stderr)
            print(f"{sum(each.size for each in snapshot.statistics('filename')) / _GIB:.3f} GiB held in all", file=sys.stderr)

    rounds.schedule.checked = traced

found: Callable[..., object] = rounds.project.index
rounds.project.index = marked("index", index)
rounds.plain.settled = marked("settled", rounds.plain.settled)
rounds.schedule.checked = marked("check", rounds.schedule.checked)

extra: list[str] = args[args.index("--") + 1 :] if "--" in args else []
path: str = (args[: args.index("--")] if "--" in args else args)[0]
start: float = time.perf_counter()
threading.Thread(target=sample, daemon=True).start()
_ = main(
    [
        "--jobs=1",
        "--level=suffocate",
        "--all-scopes",
        "--exit-zero",
        "-q",
        "--output-file",
        os.devnull,
        *extra,
        path,
    ],
    leaving=True,
)
done.set()
end: float = time.perf_counter()


def held(begin: float, finish: float) -> tuple[int, int, int]:
    inside: list[int] = [rss for when, rss in samples if begin <= when <= finish] or [0]
    return inside[0], inside[-1], max(inside)


bounds: list[tuple[str, float]] = [("start", start), *marks, ("end", end)]
for (name, begin), (_, finish) in zip(bounds, bounds[1:], strict=False):
    first, last, most = held(begin, finish)
    print(
        f"{name:16} {finish - begin:7.1f}s  {first / _GIB:5.2f} -> {last / _GIB:5.2f} GiB, at most {most / _GIB:5.2f}",
    )
peak: int = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss * 1024
print(f"{end - start:.1f}s, peak {peak / _GIB:.2f} GiB")
