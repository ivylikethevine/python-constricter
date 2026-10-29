"""The type errors basedpyright finds after `--fix` by REF's code and by the working tree's, on one package.

    local/.venv/bin/python -m scratch.fix_errors [REF] [--source PACKAGE_DIR] [--mode certain|likely|unsafe]
        [--jobs N] [--top N] [--option=FLAG ...]

Copies the package (pydantic's installed one by default) three times under `local/scratch/fix-errors/`:
as it is, fixed by REF's code (HEAD) and fixed by the tree's (as `scratch.fix_diff` copies both), each
fixed from its parent with `python -P` so the installed packages resolve as a corpus run's do. Then
`basedpyright --outputjson` on each, in `standard` mode on `local/.venv`'s packages, and prints the
errors by rule on each side and those only the tree's copy has (by file, rule and message, line left
out), each with the fix the tree wrote on that line where there is one. `--option` passes a flag to
each fix (`--option=--all-scopes`, as the corpus runs fix). One process; xarray about
2 minutes on 16CPU/60GB, sqlalchemy 1.
"""

import argparse
import json
import shutil
import subprocess
import sys
from collections import Counter
from pathlib import Path

import pydantic

from scratch.fix_diff import CODE, _copy

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "local" / "scratch" / "fix-errors"
_MODES = {"certain": [], "likely": ["--likely"], "unsafe": ["--unsafe-fixes"]}


def _fix(code: Path, corpus: Path, name: str, mode: str, jobs: int, options: list[str]) -> None:
    done = subprocess.run(
        [
            sys.executable,
            "-P",
            "-m",
            CODE,
            "--fix",
            *_MODES[mode],
            "--exit-zero",
            "-q",
            f"--jobs={jobs}",
            *options,
            name,
        ],
        cwd=corpus,
        env={"PYTHONPATH": str(code), "PATH": "/usr/bin:/bin"},
        capture_output=True,
        text=True,
        check=False,
    )
    if done.returncode:
        sys.exit(done.stderr)


def _errors(corpus: Path, name: str) -> list[tuple[str, str, str, int]]:
    config = {
        "venvPath": str(ROOT / "local"),
        "venv": ".venv",
        "typeCheckingMode": "standard",
        "include": [name],
    }
    (corpus / "pyrightconfig.json").write_text(json.dumps(config), encoding="utf-8")
    done = subprocess.run(
        [str(ROOT / "local" / ".venv" / "bin" / "basedpyright"), "--project", str(corpus), "--outputjson"],
        cwd=corpus,
        capture_output=True,
        text=True,
        check=False,
    )
    report = json.loads(done.stdout)
    return [
        (
            str(Path(each["file"]).relative_to(corpus)),
            each.get("rule", ""),
            each["message"].splitlines()[0],
            each["range"]["start"]["line"] + 1,
        )
        for each in report["generalDiagnostics"]
        if each["severity"] == "error"
    ]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("ref", nargs="?", default="HEAD")
    parser.add_argument("--source", type=Path, default=Path(pydantic.__file__).parent)
    parser.add_argument("--mode", choices=sorted(_MODES), default="unsafe")
    parser.add_argument("--jobs", type=int, default=1)
    parser.add_argument("--top", type=int, default=40)
    parser.add_argument("--option", action="append", default=[])
    args = parser.parse_args()
    name = args.source.name
    found = {}
    for label, ref in (("plain", None), (args.ref, args.ref), ("tree", "")):
        corpus = OUT / label.replace("/", "-")
        shutil.rmtree(corpus, ignore_errors=True)
        shutil.copytree(args.source, corpus / name, ignore=shutil.ignore_patterns("__pycache__"))
        if ref is not None:
            code = OUT / f"code-{label.replace('/', '-')}"
            _copy(ref or None, code)
            _fix(code, corpus, name, args.mode, args.jobs, args.option)
        found[label] = _errors(corpus, name)
        print(
            f"{label}: {len(found[label])} errors",
            dict(Counter(rule for _, rule, _, _ in found[label]).most_common(8)),
        )
    keyed = {
        label: Counter((path, rule, message) for path, rule, message, _ in errors)
        for label, errors in found.items()
    }
    new = keyed["tree"] - keyed[args.ref]
    gone = keyed[args.ref] - keyed["tree"]
    print(f"new with the tree: {sum(new.values())}, gone: {sum(gone.values())}")
    print(
        " by rule:",
        dict(Counter(rule for (_, rule, _), count in new.items() for _ in range(count)).most_common(10)),
    )
    lines = {(path, rule, message): line for path, rule, message, line in found["tree"]}
    tree = OUT / "tree"
    for key in list(new)[: args.top]:
        path, rule, message = key
        line = lines[key]
        text = (tree / path).read_text(encoding="utf-8").splitlines()[line - 1].strip()
        print(f"+ {path}:{line} [{rule}] {message[:200]}\n      {text[:160]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
