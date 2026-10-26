"""The fixes `--show-fixes --unsafe-fixes` lists on pydantic, by HEAD's code and by the working tree's.

  local/.venv/bin/python -m scratch.fix_diff [REF]

Copies `constricter/` as of REF (HEAD by default, with the tree's generated tables and `_version.py`)
and as the tree has it into `local/scratch/fix-diff/`, and the installed pydantic beside them, then
checks the copy with each, one process, from its parent (`python -P`: the code is `PYTHONPATH`'s
alone, so the installed packages resolve as a corpus run's do). Prints each side's count and the
fixes only one side has; each side's listing is kept. About 30s a side, 1 worker on 16CPU/60GB.
"""

import io
import shutil
import subprocess
import sys
import tarfile
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


def _fixes(code: Path, corpus: Path) -> list[str]:
    done = subprocess.run(
        [sys.executable, "-P", "-m", CODE, "--show-fixes", "--unsafe-fixes", "--exit-zero", "pydantic"],
        cwd=corpus,
        env={"PYTHONPATH": str(code), "PATH": "/usr/bin:/bin"},
        capture_output=True,
        text=True,
        check=False,
    )
    if done.returncode:
        sys.exit(done.stderr)
    return sorted(line for line in done.stdout.splitlines() if ": fix '" in line)


def main() -> int:
    ref = sys.argv[1] if len(sys.argv) > 1 else "HEAD"
    corpus = OUT / "corpus"
    shutil.rmtree(corpus, ignore_errors=True)
    shutil.copytree(
        Path(pydantic.__file__).parent, corpus / "pydantic", ignore=shutil.ignore_patterns("__pycache__")
    )
    sides = {}
    for label, source in ((ref, ref), ("tree", None)):
        _copy(source, OUT / label.replace("/", "-"))
        sides[label] = _fixes(OUT / label.replace("/", "-"), corpus)
        (OUT / f"{label.replace('/', '-')}.txt").write_text("\n".join(sides[label]) + "\n", encoding="utf-8")
        print(f"{label}: {len(sides[label])} fixes")
    old, new = (set(each) for each in sides.values())
    for line in sorted(old - new):
        print(f"- {line}")
    for line in sorted(new - old):
        print(f"+ {line}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
