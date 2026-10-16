"""Build this checkout's compiled wheel and install it in `local/.venv-compiled`, for a corpus run.

    python3 scratch/compiled_venv.py

Builds the sdist and, from it, the wheel mypyc compiles (`HATCH_BUILD_HOOK_ENABLE_MYPYC=1 python -m
build --no-isolation`, with `local/.venv`'s dev group, which has the `mypyc` group) into
`local/dist-compiled/`; makes `local/.venv-compiled` on the same Python as `local/.venv`; installs
the `corpus` group's packages there (`uv sync --frozen`), whose types `--fix` reads: without them
the fixes that name those types are lost, which looks like a compile bug and isn't; then the wheel,
over nothing else. `tests/corpus/runs/compiled.toml` runs it as the version `compiled`. The build
takes every CPU for some minutes: run it with nothing else measuring. Needs the network for the
corpus group's packages the first time.
"""

import glob
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEV = ROOT / "local" / ".venv"
COMPILED = ROOT / "local" / ".venv-compiled"
DIST = ROOT / "local" / "dist-compiled"


def main() -> int:
    """Build, then install; stop at the first command that fails.

    Returns:
      0, or the failed command's status.
    """
    base = Path(os.path.realpath(DEV / "bin" / "python"))  # the interpreter the dev venv is made from
    built = {**os.environ, "HATCH_BUILD_HOOK_ENABLE_MYPYC": "1"}  # as `pyproject.toml`'s hook settings build it
    steps = [
        ([str(DEV / "bin" / "python"), "-m", "build", "--no-isolation", "--outdir", str(DIST)], built),
        (["uv", "venv", "--clear", "--prompt", "constricter-compiled", "--python", str(base), str(COMPILED)], None),
        (
            ["uv", "sync", "--frozen", "--no-install-project", "--only-group", "corpus"],
            {**os.environ, "UV_PROJECT_ENVIRONMENT": str(COMPILED)},
        ),
    ]
    command: list[str]
    environment: dict[str, str] | None
    for command, environment in steps:
        print("$", " ".join(command), flush=True)
        if status := subprocess.run(command, cwd=ROOT, env=environment, check=False).returncode:
            return status
    wheels = sorted(glob.glob(str(DIST / "python_constricter-*-cp3*.whl")))
    if not wheels:
        print(f"no compiled wheel in {DIST}", file=sys.stderr)
        return 1
    install = ["uv", "pip", "install", "--python", str(COMPILED), "--no-deps", "--reinstall", wheels[-1]]
    print("$", " ".join(install), flush=True)
    return subprocess.run(install, cwd=ROOT, check=False).returncode


if __name__ == "__main__":
    sys.exit(main())
