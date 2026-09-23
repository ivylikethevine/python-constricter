# SPDX-License-Identifier: MIT
"""Run CI's checks locally, read from `.github/workflows/ci.yml` itself, all at once.

  local/.venv/bin/python tests/ci_local.py                 # the Lint, Docs and Test jobs' checks
  local/.venv/bin/python tests/ci_local.py lint docs       # just these jobs
  local/.venv/bin/python tests/ci_local.py interpreters    # the tests on the Test job's other Pythons
  local/.venv/bin/python tests/ci_local.py --install-hook  # and run it before every `git push`

Each job's `run:` steps are taken from the workflow, so the list can't drift from CI's, and run in
parallel with `local/.venv/bin` first on `PATH`. A step fails by its exit status, never its output
(pylint still rates a run with one finding 10.00/10), and every failing step's output is printed
in full at the end; the command exits 1 if any failed. What only makes sense on a runner is
adapted: `npm ci` runs only when `.github/node_modules` is missing, lychee is the one on `PATH`
(the step is skipped without it), and the Test job's `COVERAGE` is `--cov`.

`interpreters` runs the tests on each Python in the Test job's matrix (PyPy and free-threaded builds
included) but the one `local/.venv` has: each in its own `local/.venv-<python>`, with the dependency
group its matrix entry installs. uv downloads an interpreter it doesn't find. Operating systems aren't
covered: only CI runs macOS and Windows.
"""

import argparse
import os
import shutil
import subprocess  # runs each step's shell command, as the runner does
import sys
import sysconfig
import time
from collections.abc import Mapping, Sequence
from concurrent.futures import Future, ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Final, NamedTuple, TypeAlias, cast

import yaml

_ROOT: Final = Path(__file__).resolve().parent.parent
_WORKFLOW: Final = _ROOT / ".github" / "workflows" / "ci.yml"
_VENV_BIN: Final = _ROOT / "local" / ".venv" / "bin"
_JOBS: Final = ("lint", "docs", "test", "interpreters")
_INTERPRETERS: Final = "interpreters"  # not a workflow job: the Test job's matrix, by Python
_PYPY: Final = "pypy"  # `sys.implementation.name`, and the prefix of its matrix names
_RUN: Final = "run"  # a step's shell command
_EXPRESSION: Final = "${{"  # the start of a GitHub Actions expression
_NPM_CI: Final = "npm ci --prefix .github"
_LYCHEE: Final = '"$RUNNER_TEMP/bin/lychee"'
# The values a step's `${{ ... }}` environment takes here, by name (an unlisted one is empty).
_LOCAL_ENV: Final = {"COVERAGE": "--cov"}
_HOOK: Final = """\
#!/bin/sh
# Installed by tests/ci_local.py: CI's Lint, Docs and Test checks, on every Python, before every push.
exec local/.venv/bin/python tests/ci_local.py
"""
_Yaml: TypeAlias = "str | int | bool | list[_Yaml] | dict[str, _Yaml] | None"


class Step(NamedTuple):
    """One `run:` step: its job, its shell command, and the environment it adds."""

    job: str
    command: str
    env: Mapping[str, str]


class Outcome(NamedTuple):
    """How one step went: its exit status (`None`: skipped), what it printed, and how long it took."""

    step: Step
    status: int | None
    output: str
    seconds: float


def steps(jobs: Sequence[str]) -> list[Step]:
    """Read each of `jobs`' `run:` steps from the workflow, adapted to run here.

    Returns:
      Them, in the workflow's order.

    """
    defined: dict[str, _Yaml] = _defined()
    found: list[Step] = []
    job: str
    for job in jobs:
        if job == _INTERPRETERS:
            found.extend(_interpreter_steps(defined))
            continue
        raw: _Yaml
        for raw in cast("list[_Yaml]", cast("dict[str, _Yaml]", defined[job])["steps"]):
            step: dict[str, _Yaml] = cast("dict[str, _Yaml]", raw)
            if _RUN not in step:
                continue
            env: dict[str, str] = {
                name: _LOCAL_ENV.get(name, "") if _EXPRESSION in str(value) else str(value)
                for name, value in cast("dict[str, _Yaml]", step.get("env", {})).items()
            }
            found.append(Step(job, str(step[_RUN]).strip(), env))
    return found


def _defined() -> dict[str, _Yaml]:
    """Read the workflow's jobs.

    Returns:
      Them, by id.

    """
    workflow: dict[str, _Yaml] = cast(
        "dict[str, _Yaml]",
        yaml.safe_load(_WORKFLOW.read_text(encoding="utf-8")),  # type: ignore[no-untyped-call]
    )
    return cast("dict[str, _Yaml]", workflow["jobs"])


def _this_python() -> str:
    """Name the running interpreter as the workflow's matrix does (`3.14`, `3.14t`, `pypy3.11`).

    Returns:
      Its name.

    """
    version: str = f"{sys.version_info.major}.{sys.version_info.minor}"
    if sys.implementation.name == _PYPY:
        return f"{_PYPY}{version}"
    return f"{version}t" if sysconfig.get_config_var("Py_GIL_DISABLED") else version


def _interpreter_steps(defined: Mapping[str, _Yaml]) -> list[Step]:
    """List a step per Python in the Test job's matrix but this one: install its group, run the tests.

    Returns:
      Them, in the matrix's order.

    """
    test: dict[str, _Yaml] = cast("dict[str, _Yaml]", defined["test"])
    matrix: dict[str, _Yaml] = cast("dict[str, _Yaml]", cast("dict[str, _Yaml]", test["strategy"])["matrix"])
    group: str = str(cast("list[_Yaml]", matrix["group"])[0])
    groups: dict[str, str] = {str(python): group for python in cast("list[_Yaml]", matrix["python"])}
    raw: _Yaml
    for raw in cast("list[_Yaml]", matrix.get("include", [])):
        entry: dict[str, _Yaml] = cast("dict[str, _Yaml]", raw)
        groups[str(entry["python"])] = str(entry.get("group", group))
    found: list[Step] = []
    python: str
    for python, group in groups.items():
        if python == _this_python():
            continue  # the Test job's own steps run the tests on it
        venv: str = f"local/.venv-{python}"
        command: str = (
            f"uv sync -q --locked --no-install-project --no-build --python {python} --only-group {group}\n"
            f"uv pip install -q --python {venv} --no-deps --no-build-isolation -e .\n"
            f"{venv}/bin/python -m pytest -q -o cache_dir=local/.pytest_cache-{python}"
        )
        found.append(Step(_INTERPRETERS, command, {"UV_PROJECT_ENVIRONMENT": venv}))
    return found


def _adapted(command: str) -> str | None:
    """Rewrite a runner-only command for this machine.

    Returns:
      The command to run, or `None` to skip it.

    """
    if command == _NPM_CI:
        return None if (_ROOT / ".github" / "node_modules").is_dir() else command
    if _LYCHEE in command:
        lychee: str | None = shutil.which("lychee")
        return None if lychee is None else command.replace(_LYCHEE, lychee)
    return command


def _run(step: Step) -> Outcome:
    """Run one step in the repository's root, with the venv's tools first on `PATH`.

    Returns:
      How it went.

    """
    start: float = time.monotonic()
    command: str | None
    if (command := _adapted(step.command)) is None:
        return Outcome(step, None, "", 0.0)
    env: dict[str, str] = {**os.environ, **step.env, "PATH": f"{_VENV_BIN}{os.pathsep}{os.environ['PATH']}"}
    done: subprocess.CompletedProcess[str] = subprocess.run(
        ["bash", "-e", "-o", "pipefail", "-c", command],  # as the runner runs a `run:` step
        cwd=_ROOT,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )
    return Outcome(step, done.returncode, done.stdout + done.stderr, time.monotonic() - start)


def run(jobs: Sequence[str]) -> int:
    """Run every step of `jobs` at once, reporting each as it finishes and each failure in full.

    Returns:
      The exit status: 1 if any step failed, else 0.

    """
    selected: list[Step] = steps(jobs)
    failed: list[Outcome] = []
    pool: ThreadPoolExecutor
    with ThreadPoolExecutor(max_workers=len(selected)) as pool:
        futures: list[Future[Outcome]] = [pool.submit(_run, step) for step in selected]
        future: Future[Outcome]
        for future in as_completed(futures):
            outcome: Outcome = future.result()
            lines: list[str] = outcome.step.command.splitlines()
            label: str = f"{outcome.step.job}: {lines[-1] if outcome.step.job == _INTERPRETERS else lines[0]}"
            if outcome.status is None:
                _say(f"skip          {label}")
            elif outcome.status:
                failed.append(outcome)
                _say(f"FAIL {outcome.seconds:6.1f}s {label} (exit {outcome.status})")
            else:
                _say(f"ok   {outcome.seconds:6.1f}s {label}")
    for outcome in failed:
        _say(f"\n===== {outcome.step.job}: {outcome.step.command} (exit {outcome.status})\n{outcome.output}")
    _say(f"\n{len(failed)} of {len(selected)} steps failed." if failed else f"\nAll {len(selected)} passed.")
    return 1 if failed else 0


def _say(line: str) -> None:
    """Print one line of the report, at once (steps finish while others still run)."""
    _ = sys.stdout.write(f"{line}\n")
    _ = sys.stdout.flush()


def install_hook() -> Path:
    """Install a `pre-push` git hook that runs this, unless another hook is already there.

    Returns:
      The hook's path.

    Raises:
      SystemExit: a different `pre-push` hook is already installed.

    """
    hooks: str = subprocess.run(
        ["git", "rev-parse", "--git-path", "hooks"],
        cwd=_ROOT,
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()
    hook: Path = _ROOT / hooks / "pre-push"
    if hook.exists() and hook.read_text(encoding="utf-8") != _HOOK:
        message: str = f"{hook} already exists: add a line running tests/ci_local.py to it"
        raise SystemExit(message)
    hook.parent.mkdir(parents=True, exist_ok=True)
    _ = hook.write_text(_HOOK, encoding="utf-8")
    hook.chmod(0o755)
    return hook


def main(argv: Sequence[str] | None = None) -> int:
    """Parse the command line and run the jobs (or install the hook first).

    Returns:
      The exit status.

    """
    parser: argparse.ArgumentParser = argparse.ArgumentParser(description="Run CI's checks locally.")
    _ = parser.add_argument("jobs", nargs="*", help=f"CI jobs to run: {', '.join(_JOBS)} (default: all)")
    _ = parser.add_argument("--install-hook", action="store_true", help="also run this before every git push")
    options: argparse.Namespace = parser.parse_args(argv)
    jobs: list[str] = cast("list[str]", options.jobs)
    unknown: list[str]
    if unknown := sorted(set(jobs) - set(_JOBS)):
        parser.error(f"unknown job: {', '.join(unknown)}")
    if cast("bool", options.install_hook):
        _say(f"Installed {install_hook()}.")
    return run(jobs or _JOBS)


if __name__ == "__main__":
    sys.exit(main())
