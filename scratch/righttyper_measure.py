"""Measure RightTyper's signatures on a corpus: the fixes they add to `--fix`, and the type errors.

  python3 scratch/righttyper_measure.py CHECKOUT --source PKG (--module pytest | --script PATH) \\
      [--args "..."] [--check "basedpyright PKG"] [--out DIR]

On copies of the suite's CHECKOUT (its `.venv` is the environment): RightTyper 0.1.0 runs its tests
(`--module`, or `--script` with `--args`) with `--ignore-annotations`, from a copy of it patched to
write a test-local class's name without `<locals>.` (it crashes on one otherwise); of what it wrote
under PKG, only the annotations the package lacked are taken (`righttyper_added.py`); `--fix
--show-fixes` runs on a plain copy and on that one (`local/.venv`'s constricter, the checkout's
environment), and `--check`, a type checker run in each copy, after the fix. Prints the signatures
added, the certain fixes each copy got and those only one did, and the checker's errors on each
(`errorCount` from a pyright's `--outputjson`, else the lines that say `error`). Writes everything
under `--out` (default `local/righttyper/<checkout's name>`). Its forked workers and the tests' own
want what the sandbox denies: run it from a shell. pydantic, 2026-10-24: 3 fixes more, 45 errors.
"""

import argparse
import json
import os
import shlex
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RIGHTTYPER = "righttyper==0.1.0"  # its only release since 2025-06
CONSTRICTER = ROOT / "local" / ".venv" / "bin" / "constricter"
_LOCALS = "<locals>."


def copied(checkout: Path, target: Path) -> Path:
    if target.exists():
        shutil.rmtree(target)
    shutil.copytree(checkout, target, ignore=shutil.ignore_patterns(".venv", ".git"), symlinks=True)
    return target


def patched_righttyper(python: Path, out: Path) -> Path:
    """Copy RightTyper's package out of `uv`'s cache, its annotation writer patched (see the docstring)."""
    where = subprocess.run(
        [*_uv(python), "python", "-c", "import righttyper, os; print(os.path.dirname(righttyper.__file__))"],
        check=True,
        text=True,
        capture_output=True,
    ).stdout.strip()
    target = out / "rt-patch" / "righttyper"
    if target.exists():
        shutil.rmtree(target)
    shutil.copytree(where, target)
    writer = target / "unified_transformer.py"
    text = writer.read_text(encoding="utf-8")
    old = "cst.parse_expression(str(annotation))"
    if old not in text:
        sys.exit(f"RightTyper's {writer.name} has changed: the patch doesn't apply")
    writer.write_text(
        text.replace(old, f'cst.parse_expression(str(annotation).replace("{_LOCALS}", ""))'), encoding="utf-8"
    )
    return target.parent


def _uv(python: Path) -> list[str]:
    return ["uv", "run", "--no-project", "--python", str(python), "--with", RIGHTTYPER]


def annotated(python: Path, copy: Path, patch: Path, source: str, tests: list[str]) -> int:
    """Run the tests under RightTyper in `copy`, which it rewrites."""
    start = (
        "import runpy, sys; "
        f"sys.path.insert(0, {str(patch)!r}); "
        "sys.argv = ['righttyper', *sys.argv[1:]]; "
        "runpy.run_module('righttyper', run_name='__main__', alter_sys=True)"
    )
    options = ["--ignore-annotations", "--output-files", "--overwrite", "--include-files", f"/{source}/"]
    print("+ righttyper", *options, *tests, flush=True)
    return subprocess.run(
        [*_uv(python), "python", "-c", start, *options, *tests], cwd=copy, check=False
    ).returncode


def fixes(copy: Path, source: str, environment: Path, out: Path) -> set[tuple[str, int, str]]:
    listed = out / f"{copy.name}.fixes.json"
    with listed.open("w", encoding="utf-8") as file:
        _ = subprocess.run(
            [
                str(CONSTRICTER),
                "--fix",
                "--show-fixes",
                "--format=json",
                "--level=suffocate",
                "--all-scopes",
                source,
            ],
            cwd=copy,
            env=os.environ | {"VIRTUAL_ENV": str(environment)},
            stdout=file,
            check=False,
        )
    found = json.loads(listed.read_text(encoding="utf-8") or "[]")
    return {(each["path"], each["line"], each["name"]) for each in found if each.get("fixed")}


def errors(copy: Path, check: str, environment: Path) -> int:
    command = shlex.split(check)
    pyright = "pyright" in command[0]
    if pyright:
        command += ["--outputjson", "--pythonpath", str(environment / "bin" / "python")]
    done = subprocess.run(command, cwd=copy, check=False, text=True, capture_output=True)
    if pyright:
        return int(json.loads(done.stdout)["summary"]["errorCount"])
    return sum("error" in line for line in (done.stdout + done.stderr).splitlines())


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("checkout", type=Path)
    parser.add_argument("--source", required=True)
    tests = parser.add_mutually_exclusive_group(required=True)
    tests.add_argument("--module")
    tests.add_argument("--script")
    parser.add_argument("--args", default="")
    parser.add_argument("--check", default="")
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    checkout: Path = args.checkout.resolve()
    environment = checkout / ".venv"
    python = environment / "bin" / "python"
    out: Path = (args.out or ROOT / "local" / "righttyper" / checkout.name).resolve()
    out.mkdir(parents=True, exist_ok=True)
    patch = patched_righttyper(python, out)
    rewritten = copied(checkout, out / "rewritten")
    run = ["-m", args.module] if args.module else [args.script]
    status = annotated(python, rewritten, patch, args.source, [*run, *shlex.split(args.args)])
    print(f"tests under RightTyper: exit {status}")
    plain = copied(checkout, out / "plain")
    merged = copied(checkout, out / "merged")
    _ = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scratch" / "righttyper_added.py"),
            str(checkout / args.source),
            str(rewritten / args.source),
            str(merged / args.source),
        ],
        check=True,
    )
    before, after = fixes(plain, args.source, environment, out), fixes(merged, args.source, environment, out)
    print(f"certain and guessed fixes: {len(before)} plain, {len(after)} with its signatures")
    print(f"  only with them: {len(after - before)}, only without: {len(before - after)}")
    if args.check:
        print(
            f"{args.check}: {errors(plain, args.check, environment)} errors plain, "
            f"{errors(merged, args.check, environment)} with its signatures, each after its fix"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
