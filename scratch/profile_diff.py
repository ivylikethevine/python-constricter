"""Compare two `py-spy` sample files `tests/corpus/corpus_profile.py` wrote: what got slower, and where.

  local/.venv/bin/python scratch/profile_diff.py BEFORE.txt AFTER.txt [--top N] [--under MODULE.FUNCTION]

Each frame is named by its module (constricter's dotted from its package, wherever the checkout is;
another's by its file's name) and its function, without the line, so two versions' functions match.
Prints each one's own and whole seconds (100 samples a second, as the profiler takes them) in both,
the modules by own time, then the functions by how much their whole and their own time grew.
`--under`: only the samples with that function on the stack (`constricter.fix.index.modules.read`).
"""

import sys
from collections import Counter
from pathlib import Path

RATE = 100  # samples a second, as `corpus_profile` records
PACKAGE = "/constricter/"


def name(frame: str) -> tuple[str, str]:
    """Name a frame `function (path:line)` as `(module, function)`."""
    function, _, place = frame.rpartition(" (")
    path = place.rstrip(")").rpartition(":")[0]
    if PACKAGE in path:
        module = "constricter." + path.rpartition(PACKAGE)[2].removesuffix(".py").replace("/", ".")
        return module.removesuffix(".__init__"), function
    return Path(path).name, function


def read(samples: Path, under: str = "") -> tuple[Counter[tuple[str, str]], Counter[tuple[str, str]]]:
    """Count each function's own samples and those it was anywhere in the stack of (`under`'s alone)."""
    own: Counter[tuple[str, str]] = Counter()
    whole: Counter[tuple[str, str]] = Counter()
    for line in samples.read_text(encoding="utf-8").splitlines():
        stack, _, count = line.rpartition(" ")
        if not count.isdigit():
            continue
        frames = [name(frame) for frame in stack.split(";") if not frame.startswith("process ")]
        if not frames or (under and under not in {f"{module}.{function}" for module, function in frames}):
            continue
        own[frames[-1]] += int(count)
        for each in set(frames):
            whole[each] += int(count)
    return own, whole


def main() -> None:
    args = sys.argv[1:]
    top = int(args[args.index("--top") + 1]) if "--top" in args else 30
    paths = [Path(arg) for arg in args if arg.endswith(".txt")]
    under = args[args.index("--under") + 1] if "--under" in args else ""
    (own0, whole0), (own1, whole1) = read(paths[0], under), read(paths[1], under)
    total0, total1 = sum(own0.values()) / RATE, sum(own1.values()) / RATE
    print(f"before {total0:.1f}s, after {total1:.1f}s, {total1 - total0:+.1f}s\n")
    modules0: Counter[str] = Counter()
    modules1: Counter[str] = Counter()
    for (module, _), count in own0.items():
        modules0[module] += count
    for (module, _), count in own1.items():
        modules1[module] += count
    print("| Module | Own before (s) | Own after (s) | Change (s) |\n| --- | ---: | ---: | ---: |")
    for module in sorted(modules0.keys() | modules1.keys(), key=lambda m: modules0[m] - modules1[m])[:top]:
        print(
            f"| `{module}` | {modules0[module] / RATE:.2f} | {modules1[module] / RATE:.2f} | {(modules1[module] - modules0[module]) / RATE:+.2f} |"
        )
    for title, before, after in (("whole", whole0, whole1), ("own", own0, own1)):
        print(
            f"\n| Function, by {title} time | Before (s) | After (s) | Change (s) |\n| --- | ---: | ---: | ---: |"
        )
        keys = sorted(before.keys() | after.keys(), key=lambda k: before[k] - after[k])[:top]
        for module, function in keys:
            key = (module, function)
            print(
                f"| `{module}.{function}` | {before[key] / RATE:.2f} | {after[key] / RATE:.2f} | {(after[key] - before[key]) / RATE:+.2f} |"
            )


if __name__ == "__main__":
    main()
