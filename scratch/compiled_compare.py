"""Check a tree with this checkout and with a compiled wheel's install: the same findings, and the time each took.

  local/.venv/bin/python -m scratch.compiled_compare SITE TREE [TREE ...] [--runs N] [--jobs N] [--fix]

SITE is the `site-packages` the compiled wheel is installed in (`uv venv local/.venv-compiled`, then
`uv pip install --python local/.venv-compiled --no-deps dist/python_constricter-*-cp3*.whl`), put
first on `PYTHONPATH` for this checkout's interpreter, so both see the same installed packages (whose
types `--fix` reads). Each runs `python -m constricter --level=suffocate
--all-scopes --format=json --exit-zero --jobs=N` (1 unless given) on each TREE from `$TMPDIR` (so
neither imports the checkout by the working directory), `--runs` times (3), and prints the median
seconds of each and whether their findings are the same, the first that differs if not. With
`--fix`, `--diff --unsafe-fixes` instead, its output compared. Writes nothing. Outside a sandbox
for `--jobs` above 1.
"""

import json
import os
import statistics
import subprocess
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INTERPRETED = ROOT / "local" / ".venv" / "bin" / "python"


def run(site: str, tree: str, jobs: str, *, fix: bool) -> tuple[float, str]:
    """Check (or fix) `tree`, with the constricter in `site` if given; return the seconds and the output."""
    mode = ["--diff", "--unsafe-fixes"] if fix else ["--format=json", "--exit-zero"]
    command = [str(INTERPRETED), "-m", "constricter", "--level=suffocate", "--all-scopes", *mode, f"--jobs={jobs}", tree]
    start = time.perf_counter()
    env = {**os.environ, "PYTHONPATH": site} if site else dict(os.environ)
    done = subprocess.run(command, capture_output=True, text=True, cwd=tempfile.gettempdir(), env=env, check=False)
    seconds = time.perf_counter() - start
    if done.returncode > 2:  # noqa: PLR2004  # 0-2: clean, found, or a file that doesn't parse
        sys.exit(f"{site or 'this checkout'} on {tree} exited {done.returncode}:\n{done.stderr[-2000:]}")
    return seconds, done.stdout


def main(argv: list[str]) -> int:
    runs = int(argv[argv.index("--runs") + 1]) if "--runs" in argv else 3
    jobs = argv[argv.index("--jobs") + 1] if "--jobs" in argv else "1"
    fix = "--fix" in argv
    values = {argv[i + 1] for i, arg in enumerate(argv) if arg in {"--runs", "--jobs"}}
    compiled, *trees = [arg for arg in argv if not arg.startswith("--") and arg not in values]
    differs = 0
    for tree in trees:
        found: dict[str, tuple[list[float], str]] = {}
        for name, site in (("interpreted", ""), ("compiled", compiled)):
            seconds: list[float] = []
            output = ""
            for _ in range(runs):
                took, output = run(site, os.path.abspath(tree), jobs, fix=fix)
                seconds.append(took)
            found[name] = (seconds, output)
        same = found["interpreted"][1] == found["compiled"][1]
        differs += not same
        medians = {name: statistics.median(each[0]) for name, each in found.items()}
        print(
            f"{tree}: interpreted {medians['interpreted']:.1f}s, compiled {medians['compiled']:.1f}s "
            f"({medians['interpreted'] / medians['compiled']:.2f}x), {'same output' if same else 'OUTPUT DIFFERS'}",
            flush=True,
        )
        if not same and not fix:
            left, right = (json.loads(found[name][1]) for name in ("interpreted", "compiled"))
            pairs = zip(left, right, strict=False)
            first = next(((a, b) for a, b in pairs if a != b), None)
            print(f"  {len(left)} and {len(right)} findings; first differing: {first}")
    return 1 if differs else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
