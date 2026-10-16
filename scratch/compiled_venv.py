"""Build this checkout's pure and compiled wheels, each in a venv of its own with the same packages.

    python3 scratch/compiled_venv.py

Builds the sdist and, from it, the wheel (`python -m build --no-isolation`, with `local/.venv`'s dev
group, which has the `mypyc` group) twice: as it is, into `local/dist-pure/`, and compiled by mypyc
(`HATCH_BUILD_HOOK_ENABLE_MYPYC=1`), into `local/dist-compiled/`. Each goes in a venv on
`local/.venv`'s Python, `local/.venv-pure` and `local/.venv-compiled`, beside the `corpus` group's
packages and nothing else (`uv sync --frozen`): `--fix` reads the types of what's installed beside
it, so the two differ by the build alone, and a compiled build compared with `dev` (whose venv has
the dev group's packages too) differs by those. `tests/corpus/runs/compiled.toml` runs them as
`pure` and `compiled`. The compiled build takes every CPU for some minutes: run it with nothing else
measuring. Needs the network for the corpus group's packages the first time.
"""

import glob
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEV = ROOT / "local" / ".venv"
BUILDS = {  # each build's name: its wheel's folder, its venv, and whether mypyc compiles it
    "pure": (ROOT / "local" / "dist-pure", ROOT / "local" / ".venv-pure", False),
    "compiled": (ROOT / "local" / "dist-compiled", ROOT / "local" / ".venv-compiled", True),
}


def _ran(command: list[str], environment: dict[str, str] | None = None) -> int:
    print("$", " ".join(command), flush=True)
    return subprocess.run(command, cwd=ROOT, env=environment, check=False).returncode


def _built(name: str) -> int:
    """Build one wheel and install it in its venv, beside the `corpus` group's packages.

    Returns:
      0, or the failed command's status.

    """
    dist, venv, compiled = BUILDS[name]
    base = Path(os.path.realpath(DEV / "bin" / "python"))  # the interpreter the dev venv is made from
    built = {**os.environ, "HATCH_BUILD_HOOK_ENABLE_MYPYC": "1"} if compiled else None  # as the hook's settings say
    synced = {**os.environ, "UV_PROJECT_ENVIRONMENT": str(venv)}
    steps: list[tuple[list[str], dict[str, str] | None]] = [
        ([str(DEV / "bin" / "python"), "-m", "build", "--no-isolation", "--outdir", str(dist)], built),
        (["uv", "venv", "--clear", "--prompt", f"constricter-{name}", "--python", str(base), str(venv)], None),
        (["uv", "sync", "--frozen", "--no-install-project", "--only-group", "corpus"], synced),
    ]
    for command, environment in steps:
        if status := _ran(command, environment):
            return status
    wheels = sorted(glob.glob(str(dist / ("python_constricter-*-cp3*.whl" if compiled else "python_constricter-*-py3-*.whl"))))
    if not wheels:
        print(f"no {name} wheel in {dist}", file=sys.stderr)
        return 1
    return _ran(["uv", "pip", "install", "--python", str(venv), "--no-deps", "--reinstall", wheels[-1]])


def main() -> int:
    """Build the pure wheel, then the compiled one; stop at the first command that fails.

    Returns:
      0, or the failed command's status.

    """
    for name in BUILDS:
        if status := _built(name):
            return status
    return 0


if __name__ == "__main__":
    sys.exit(main())
