"""Time the compiled wheel's build from the sdist, as the release builds it, with mypyc's options varied.

    python3 scratch/compile_time.py [--python 3.12] [--fresh] [VARIANT ...]

Makes a venv of its own (`local/scratch/compile-time/venv`, on `--python`) with the `mypyc` group
from `uv.lock` and `build`, builds the sdist (again with `--fresh`: else the last one's kept, so
variants can run side by side), then for each VARIANT (all, by default) unpacks it fresh and builds the wheel there (`HATCH_BUILD_HOOK_ENABLE_MYPYC=1 python -m build --wheel
--no-isolation`), as cibuildwheel does, printing its wall and CPU seconds and the wheel's size:

- `single`: the hook's options as `pyproject.toml` has them (one C file for every module)
- `multi`: with `multi_file = true` (a C file a module), compiled one after another
- `parallel`: `multi`, its C files compiled on every CPU (`build_ext`'s `parallel`, through
  setuptools's `DIST_EXTRA_CONFIG`, since hatch-mypyc passes `build_ext` no `-j`)

Each wheel's build takes one CPU but `parallel`'s, for minutes: run it with nothing else measuring.
Needs the network for the venv the first time.
"""

import argparse
import os
import re
import resource
import shutil
import subprocess
import sys
import tarfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HERE = ROOT / "local" / "scratch" / "compile-time"
VENV = HERE / "venv"
PYTHON = VENV / "bin" / "python"
VARIANTS = ("single", "multi", "parallel")


def _ran(command: list[str], cwd: Path = ROOT, environment: dict[str, str] | None = None) -> None:
    print("$", " ".join(command), flush=True)
    subprocess.run(command, cwd=cwd, env=environment, check=True)


def _venv(python: str) -> None:
    """Make the venv, with the `mypyc` group and `build`, unless it's there."""
    if PYTHON.exists():
        return
    requirements = HERE / "mypyc.txt"
    _ran(["uv", "venv", "--python", python, str(VENV)])
    _ran(
        [
            "uv",
            "export",
            "--locked",
            "--only-group",
            "mypyc",
            "--no-emit-project",
            "--format",
            "requirements.txt",
            "--output-file",
            str(requirements),
        ]
    )
    _ran(["uv", "pip", "install", "--python", str(PYTHON), "-r", str(requirements), "build"])


def _sdist(fresh: bool) -> Path:
    """Build the sdist into `dist/` here, unless one's there and `fresh` is false."""
    dist = HERE / "dist"
    if fresh:
        shutil.rmtree(dist, ignore_errors=True)
    if not any(dist.glob("*.tar.gz")):
        _ran([str(PYTHON), "-m", "build", "--sdist", "--no-isolation", "--outdir", str(dist)])
    return next(dist.glob("*.tar.gz"))


def _timed(variant: str, sdist: Path) -> tuple[float, float, int]:
    """Build one variant's wheel from a fresh copy of the sdist.

    Returns:
      Its wall seconds, its CPU seconds (the build's processes', user and system) and the wheel's bytes.

    """
    work = HERE / variant
    shutil.rmtree(work, ignore_errors=True)
    with tarfile.open(sdist) as archive:
        archive.extractall(work, filter="data")
    project = next(work.iterdir())
    if variant != "single":
        pyproject = project / "pyproject.toml"
        text, count = re.subn(
            r"^options = \{ (.*) \}$",
            r"options = { \1, multi_file = true }",
            pyproject.read_text(),
            flags=re.MULTILINE,
        )
        if count != 1:
            raise SystemExit("no `options` line in the sdist's pyproject.toml")
        pyproject.write_text(text)
    environment = {**os.environ, "HATCH_BUILD_HOOK_ENABLE_MYPYC": "1"}
    if variant == "parallel":
        config = work / "parallel.cfg"
        config.write_text(f"[build_ext]\nparallel = {os.cpu_count() or 1}\n")
        environment["DIST_EXTRA_CONFIG"] = str(config)
    before = resource.getrusage(resource.RUSAGE_CHILDREN)
    start = time.monotonic()
    _ran(
        [
            str(PYTHON),
            "-m",
            "build",
            "--wheel",
            "--no-isolation",
            "--outdir",
            str(work / "wheel"),
            str(project),
        ],
        cwd=work,
        environment=environment,
    )
    wall = time.monotonic() - start
    after = resource.getrusage(resource.RUSAGE_CHILDREN)
    cpu = after.ru_utime - before.ru_utime + after.ru_stime - before.ru_stime
    return wall, cpu, next((work / "wheel").glob("*.whl")).stat().st_size


def main() -> int:
    """Time each variant asked for, then print the table.

    Returns:
      0.

    """
    parser = argparse.ArgumentParser()
    parser.add_argument("--python", default="3.12")
    parser.add_argument("--fresh", action="store_true", help="build the sdist again from the checkout")
    parser.add_argument("variants", nargs="*", default=list(VARIANTS))
    arguments = parser.parse_args()
    if unknown := set(arguments.variants) - set(VARIANTS):
        parser.error(f"no variant {', '.join(sorted(unknown))}: one of {', '.join(VARIANTS)}")
    HERE.mkdir(parents=True, exist_ok=True)
    _venv(arguments.python)
    sdist = _sdist(arguments.fresh)
    rows = [(variant, *_timed(variant, sdist)) for variant in arguments.variants]
    for variant, wall, cpu, size in rows:
        print(f"{variant:10} {wall:7.1f}s wall {cpu:8.1f}s CPU {size / 1e6:6.2f} MB")
    return 0


if __name__ == "__main__":
    sys.exit(main())
