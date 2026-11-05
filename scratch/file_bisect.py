"""Find which file of a commit's change to `constricter/` makes one binding's fix go or come.

    local/.venv/bin/python -m scratch.file_bisect GOOD BAD --source PACKAGE_DIR --path SUFFIX --line N
        [--option=FLAG ...] [--python EXE]

Copies `constricter/` as of GOOD (with the tree's generated tables and `_version.py`) once for each
file BAD changes under it, that file alone taken from BAD, into `local/scratch/file-bisect/`, and
checks a copy of PACKAGE_DIR with each (`--format=json --unsafe-fixes`, one process, `python -P` from
the copy's parent, as `scratch.fix_diff` checks). Prints, for GOOD, BAD and each file, the fix or the
`unfixed` reason of the binding on line N of the checked file whose path ends with SUFFIX. A file
BAD adds is copied in; one it deletes is removed. A file that needs another of BAD's changes fails to
import, printed as `failed`. About a minute a copy on pandas, 16CPU/60GB.
"""

import argparse
import io
import json
import shutil
import subprocess
import sys
import tarfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "local" / "scratch" / "file-bisect"
CODE = "constricter"


def _archive(ref: str, into: Path) -> None:
    shutil.rmtree(into, ignore_errors=True)
    into.mkdir(parents=True)
    archive = subprocess.run(["git", "-C", str(ROOT), "archive", ref, CODE], check=True, capture_output=True)
    with tarfile.open(fileobj=io.BytesIO(archive.stdout)) as tar:
        tar.extractall(into, filter="data")
    shutil.copytree(ROOT / CODE / "fix" / "tables", into / CODE / "fix" / "tables", dirs_exist_ok=True)
    shutil.copy2(ROOT / CODE / "_version.py", into / CODE / "_version.py")


def _changed(good: str, bad: str) -> list[str]:
    done = subprocess.run(
        ["git", "-C", str(ROOT), "diff", "--name-only", good, bad, "--", CODE],
        check=True,
        capture_output=True,
        text=True,
    )
    return [line for line in done.stdout.splitlines() if line.endswith(".py")]


def _overlay(code: Path, bad: str, name: str) -> None:
    shown = subprocess.run(
        ["git", "-C", str(ROOT), "show", f"{bad}:{name}"], capture_output=True, check=False
    )
    target = code / name
    if shown.returncode:
        target.unlink(missing_ok=True)
        return
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(shown.stdout)


def _verdict(code: Path, corpus: Path, name: str, args: argparse.Namespace) -> str:
    done = subprocess.run(
        [args.python, "-P", "-m", CODE, "--format=json", "--unsafe-fixes", "--exit-zero", *args.option, name],
        cwd=corpus,
        env={"PYTHONPATH": str(code), "PATH": "/usr/bin:/bin"},
        capture_output=True,
        text=True,
        check=False,
    )
    if done.returncode:
        return f"failed: {done.stderr.strip()[-200:]}"
    for row in json.loads(done.stdout or "[]"):
        if row["path"].endswith(args.path) and row["line"] == args.line:
            fix = row["fix"]
            return f"fix {fix['annotation']} {sorted(fix['kinds'])}" if fix else f"no fix: {row['unfixed']}"
    return "no binding there"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("good")
    parser.add_argument("bad")
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--path", required=True)
    parser.add_argument("--line", type=int, required=True)
    parser.add_argument("--option", action="append", default=[])
    parser.add_argument("--python", default=sys.executable)
    args = parser.parse_args()
    name = args.source.name
    corpus = OUT / "corpus"
    shutil.rmtree(corpus, ignore_errors=True)
    shutil.copytree(args.source, corpus / name, ignore=shutil.ignore_patterns("__pycache__"))
    for label, ref in (("good", args.good), ("bad", args.bad)):
        _archive(ref, OUT / label)
        print(f"{label} {ref}: {_verdict(OUT / label, corpus, name, args)}", flush=True)
    for changed in _changed(args.good, args.bad):
        code = OUT / "one"
        _archive(args.good, code)
        _overlay(code, args.bad, changed)
        print(f"{args.good} + {changed}: {_verdict(code, corpus, name, args)}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
