"""Compile a copy of constricter with mypyc, as the compiled wheel is, and run the tests against it.

  local/.venv-mypyc/bin/python -m scratch.mypyc_trial [--opt 0] [--exclude PATH ...] [-- PYTEST_ARGS]

`local/.venv-mypyc` needs mypy (the version `uv.lock` pins) and setuptools, on this checkout's
Python. The copy goes in `local/scratch/mypyc/` (made fresh): `constricter/`, its `rules` and `fix`
packages compiled but for each `--exclude`d file (`constricter/fix/core/known.py`), as the
`[tool.hatch.build.targets.wheel.hooks.mypyc]` table of `pyproject.toml` lists them, split into a
C file per module and built on every CPU, at `--opt` (0, for a quick check; the wheel's is 3). Then
`local/.venv/bin/pytest` runs this checkout's tests on the copy (`--import-mode=append`, from the
repository's root, with the copy first on `PYTHONPATH`), with PYTEST_ARGS; it first checks that
the compiled modules are the ones imported. Outside a sandbox for the `--jobs` tests.
"""

import os
import shutil
import subprocess
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
COPY = ROOT / "local" / "scratch" / "mypyc"
PYTEST = ROOT / "local" / ".venv" / "bin" / "pytest"
_SETUP = """
from setuptools import setup
from mypyc.build import mypycify

setup(name="constricter_trial", ext_modules=mypycify({files!r}, opt_level={opt!r}, debug_level="0", multi_file=True))
"""
_PROBE = """
import constricter.rules.checker as checker
assert checker.__file__.endswith((".so", ".pyd")), checker.__file__
print("compiled:", checker.__file__)
"""


def configured_excludes() -> list[str]:
    """The files `pyproject.toml`'s mypyc hook leaves interpreted, as paths from the root."""
    with (ROOT / "pyproject.toml").open("rb") as file:
        wheel = tomllib.load(file)["tool"]["hatch"]["build"]["targets"]["wheel"]
    hook = wheel.get("hooks", {}).get("mypyc", {})
    return [pattern.lstrip("/") for pattern in hook.get("exclude", [])]


def main(argv: list[str]) -> int:
    pytest_args = argv[argv.index("--") + 1 :] if "--" in argv else []
    argv = argv[: argv.index("--")] if "--" in argv else argv
    opt = argv[argv.index("--opt") + 1] if "--opt" in argv else "0"
    excluded = {argv[i + 1] for i, arg in enumerate(argv) if arg == "--exclude"} or set(configured_excludes())
    if COPY.name == "mypyc" and COPY.is_dir():
        shutil.rmtree(COPY)
    COPY.mkdir(parents=True)
    shutil.copytree(ROOT / "constricter", COPY / "constricter", ignore=shutil.ignore_patterns("__pycache__"))
    files = sorted(
        path.relative_to(COPY).as_posix()
        for package in ("rules", "fix")
        for path in (COPY / "constricter" / package).rglob("*.py")
        if path.relative_to(COPY).as_posix() not in excluded
    )
    (COPY / "setup.py").write_text(_SETUP.format(files=files, opt=opt), encoding="utf-8")
    print(f"compiling {len(files)} modules, leaving {sorted(excluded)}", flush=True)
    jobs = str(os.cpu_count() or 1)
    built = subprocess.run(
        [sys.executable, "setup.py", "build_ext", "--inplace", "-j", jobs],
        cwd=COPY,
        capture_output=True,
        text=True,
        check=False,
    )
    (COPY / "build.log").write_text(built.stdout + built.stderr, encoding="utf-8")
    if built.returncode:
        print((built.stdout + built.stderr)[-4000:])
        return built.returncode
    env = {**os.environ, "PYTHONPATH": str(COPY)}
    probe = subprocess.run([sys.executable, "-c", _PROBE], cwd=COPY.parent, env=env, check=False)
    if probe.returncode:
        return probe.returncode
    return subprocess.run(
        [PYTEST, "--import-mode=append", *pytest_args],
        cwd=ROOT,
        env=env,
        check=False,
    ).returncode


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
