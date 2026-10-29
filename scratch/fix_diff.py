"""The fixes `--show-fixes --unsafe-fixes` lists on pydantic, by HEAD's code and by the working tree's.

  local/.venv/bin/python -m scratch.fix_diff [REF] [--source PACKAGE_DIR] [--jobs N] [--top N]

`--source` checks another package's directory instead (xarray's from its sdist, say), copied as
pydantic is; `--top` prints only that many of each side's lines, after a count of them by type.

Copies `constricter/` as of REF (HEAD by default, with the tree's generated tables and `_version.py`)
and as the tree has it into `local/scratch/fix-diff/`, and the installed pydantic beside them, then
checks the copy with each, one process, from its parent (`python -P`: the code is `PYTHONPATH`'s
alone, so the installed packages resolve as a corpus run's do). Prints each side's count and the
fixes only one side has; each side's listing is kept. About 30s a side, 1 worker on 16CPU/60GB.
"""

import argparse
import io
import shutil
import subprocess
import sys
import tarfile
from collections import Counter
from pathlib import Path

import pydantic

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "local" / "scratch" / "fix-diff"
CODE = "constricter"


def _copy(ref: str | None, into: Path) -> None:
    shutil.rmtree(into, ignore_errors=True)
    into.mkdir(parents=True)
    ignored = shutil.ignore_patterns("__pycache__", "*.so")
    if ref is None:
        shutil.copytree(ROOT / CODE, into / CODE, ignore=ignored)
        return
    archive = subprocess.run(["git", "-C", str(ROOT), "archive", ref, CODE], check=True, capture_output=True)
    with tarfile.open(fileobj=io.BytesIO(archive.stdout)) as tar:
        tar.extractall(into, filter="data")
    shutil.copytree(ROOT / CODE / "fix" / "tables", into / CODE / "fix" / "tables", dirs_exist_ok=True)
    shutil.copy2(ROOT / CODE / "_version.py", into / CODE / "_version.py")


def _fixes(code: Path, corpus: Path, name: str, jobs: int) -> list[str]:
    done = subprocess.run(
        [sys.executable, "-P", "-m", CODE, "--show-fixes", "--unsafe-fixes", "--exit-zero", f"--jobs={jobs}", name],
        cwd=corpus,
        env={"PYTHONPATH": str(code), "PATH": "/usr/bin:/bin"},
        capture_output=True,
        text=True,
        check=False,
    )
    if done.returncode:
        sys.exit(done.stderr)
    return sorted(line for line in done.stdout.splitlines() if ": fix '" in line)


def _annotation(line: str) -> str:
    return line.split(": fix '", 1)[1].split("'", 1)[0]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("ref", nargs="?", default="HEAD")
    parser.add_argument("--source", type=Path, default=Path(pydantic.__file__).parent)
    parser.add_argument("--jobs", type=int, default=1)
    parser.add_argument("--top", type=int, default=None)
    args = parser.parse_args()
    ref = args.ref
    name = args.source.name
    corpus = OUT / "corpus"
    shutil.rmtree(corpus, ignore_errors=True)
    shutil.copytree(args.source, corpus / name, ignore=shutil.ignore_patterns("__pycache__"))
    sides = {}
    for label, source in ((ref, ref), ("tree", None)):
        _copy(source, OUT / label.replace("/", "-"))
        sides[label] = _fixes(OUT / label.replace("/", "-"), corpus, name, args.jobs)
        (OUT / f"{label.replace('/', '-')}.txt").write_text("\n".join(sides[label]) + "\n", encoding="utf-8")
        print(f"{label}: {len(sides[label])} fixes")
    old, new = (set(each) for each in sides.values())
    for sign, lines in (("-", sorted(old - new)), ("+", sorted(new - old))):
        print(f"{sign} {len(lines)} lines:", ", ".join(f"{a} {n}" for a, n in Counter(map(_annotation, lines)).most_common(12)))
        for line in lines[: args.top]:
            print(f"{sign} {line}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
