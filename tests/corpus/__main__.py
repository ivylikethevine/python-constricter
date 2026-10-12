# SPDX-License-Identifier: MIT
"""Measure corpora as a run file says, into a folder of that run's own.

    local/.venv/bin/python -m tests.corpus RUN.toml                   # a new folder, named by label and time
    local/.venv/bin/python -m tests.corpus RUN.toml --resume FOLDER   # carry on a stopped run in its folder
    local/.venv/bin/python -m tests.corpus RUN.toml --only NAME       # on that corpus or set alone

The run file (`run_config`) names the corpora (`corpora.toml`'s), the constricter versions, the
steps and the formats. Each execution writes `<output>/<label>-<month>-<day>-<year>-<time>/`:

    run.toml      the run file, copied
    facts.toml    the run as it was read, the commit and the machine
    records/      <corpus>/<version>/<step>.json, and each fix's patch: what every output is made from
    logs/         what each step's constricter wrote to standard error
    report.json   report.md   tables/*.csv

Corpora are measured `at-once` at a time, each one's steps side by side, then its suite's own
tests and checks in a process of their own. Every step starts constricter one way (`launch.run`)
on one tree a corpus (`trees.Tree`), so a count in one table is the count in another.
"""

import itertools
import os
import platform
import shutil
import subprocess  # asks git for the commit
import sys
import threading
from collections.abc import Sequence
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from functools import partial
from pathlib import Path
from typing import IO, Final, TypeAlias, cast

from constricter import __version__
from tests.corpus import catalog, pipeline, render, suite_steps, trees
from tests.corpus.pipeline import Record
from tests.corpus.run_config import Run, read

_Measured: TypeAlias = tuple[trees.Tree | None, list[str]]  # a corpus's tree, and its steps that failed
_RESUME: Final = "--resume"
_SAID: Final = 2000  # the characters kept of why a corpus couldn't be had: the end of its build's output
_ONLY: Final = "--only"  # then a corpus or a set: the run file's, on that alone
_STEP: Final = "--step"  # then a run's folder, a corpus and a version: that corpus's suite steps
_ROOT: Final = Path(__file__).resolve().parents[2]


def _facts(run: Run, started: datetime) -> Record:
    """Gather what a run's outputs say of the run itself.

    Returns:
      The run file's values, this checkout's version and commit, and the machine.

    """
    commit: str = subprocess.run(
        ["git", "rev-parse", "--short=12", "HEAD"],
        capture_output=True,
        text=True,
        check=False,
        cwd=_ROOT,
    ).stdout.strip()
    return {
        "label": run.label,
        "started": started.isoformat(timespec="seconds"),
        "versions": list(run.versions),
        "formats": list(run.formats),
        "jobs": run.jobs,
        "at-once": run.at_once,
        "corpora": list(run.include),
        "check": run.steps.check,
        "fix": list(run.steps.fix),
        "coverage": run.steps.coverage,
        "infer-with": list(run.steps.infer),
        "census": run.steps.census,
        "tests": run.steps.tests,
        "types": run.steps.types,
        "traced": run.steps.traced,
        "timing": run.steps.timing,
        "profile": run.steps.profile,
        "install": run.install,
        "constricter": __version__,
        "commit": commit,
        "python": platform.python_version(),
        "machine": platform.processor() or platform.machine(),
        "cpus": os.cpu_count() or 1,
    }


def _toml(facts: Record) -> str:
    """Write flat facts as TOML: strings, numbers, booleans and lists of strings.

    Returns:
      The text.

    """

    def value(each: object) -> str:
        if isinstance(each, bool):
            return str(each).lower()
        if isinstance(each, list):
            return "[" + ", ".join(value(one) for one in cast("list[object]", each)) + "]"
        return (
            str(each)
            if isinstance(each, int)
            else '"' + str(each).replace("\\", "\\\\").replace('"', '\\"') + '"'
        )

    return "".join(f"{key} = {value(each)}\n" for key, each in facts.items())


def _measured(
    run: Run,
    store: pipeline.Store,
    ports: dict[str, threading.Lock],
    entry: catalog.Entry,
) -> _Measured:
    """Measure one corpus with each of the run's versions.

    Its suite's steps run in a process of their own (`--step`): they set what the suite's commands
    need in the environment, and corpora are measured side by side. Suites whose tests bind one
    port run one at a time (`ports`' locks).

    Returns:
      The corpus's tree, and the steps that failed: each has its traceback in its log, and no record.
      No tree, and why, for a corpus that isn't to be had: the run goes on without it.

    """
    try:
        tree: trees.Tree = trees.found(entry, install=run.install)
    except (OSError, RuntimeError, ValueError) as failure:  # it can't be cloned, installed or fetched
        return None, [f"{entry.name}: not found: {str(failure)[-_SAID:]}"]
    failed: list[str] = []
    version: str
    for version in run.versions:
        job: pipeline.Job = pipeline.Job(run, store, tree, version)
        failed += [f"{entry.name}, {job.recorded}: {name}" for name in pipeline.measure(job)]
        if any(store.read(tree.name, job.recorded, name) is None for name in suite_steps.waiting(job)):
            log: Path = store.root / "logs" / tree.name.replace(" ", "-") / job.recorded / "suite.log"
            log.parent.mkdir(parents=True, exist_ok=True)
            file: IO[str]
            with ports[entry.port], log.open("a", encoding="utf-8") as file:
                done: subprocess.CompletedProcess[bytes] = subprocess.run(
                    [sys.executable, "-m", "tests.corpus", _STEP, str(store.root), entry.name, version],
                    stdout=file,
                    stderr=subprocess.STDOUT,
                    check=False,
                    cwd=_ROOT,
                )
            if done.returncode:
                failed.append(f"{entry.name}, {job.recorded}: its suite's steps ({log})")
    return tree, failed


def _step(folder: Path, name: str, version: str) -> int:
    """Run one corpus's suite steps with one version, in the run whose folder is `folder`.

    Returns:
      1 if one failed, else 0.

    """
    run: Run = read(folder / "run.toml")
    tree: trees.Tree = trees.found(catalog.load().entry(name), install=run.install)
    return int(bool(suite_steps.measure(pipeline.Job(run, pipeline.Store(folder), tree, version))))


def main(argv: Sequence[str]) -> int:
    """Run the run file named, write its folder, and say where it is.

    Returns:
      1 if a step failed (the outputs have the rest; `--resume` makes it again) or a fix broke
      something (`render.problems`), else 0.

    """
    if argv[:1] == [_STEP]:
        return _step(Path(argv[1]), argv[2], argv[3])
    run: Run = read(Path(argv[0]))
    if _ONLY in argv:
        run = run._replace(include=(argv[argv.index(_ONLY) + 1],))
    facts: Record = _facts(run, datetime.now().astimezone())
    folder: Path = _folder(argv, run, facts)
    store: pipeline.Store = pipeline.Store(folder)
    measured: list[_Measured] = _all(run, store)
    shutil.rmtree(folder / "work", ignore_errors=True)  # the copies its fixes worked on
    records: render.Records = render.gathered(run, store, [tree for tree, _ in measured if tree])
    written: list[Path] = render.write(records, folder, facts)
    render.publish(records, _ROOT)
    _ = sys.stdout.write("".join(f"{path}\n" for path in written))
    failed: list[str] = [f"failed: {each}" for _, failures in measured for each in failures]
    failed += [f"problem: {each}" for each in render.problems(records)]
    _ = sys.stderr.write("".join(f"{each}\n" for each in failed))
    return int(bool(failed))


def _folder(argv: Sequence[str], run: Run, facts: Record) -> Path:
    """Make the folder this execution writes, or take the one `--resume` names, and keep the run file there.

    Returns:
      The folder.

    """
    resumed: Path | None = Path(argv[argv.index(_RESUME) + 1]) if _RESUME in argv else None
    started: datetime = datetime.fromisoformat(str(facts["started"]))
    folder: Path = (resumed or _ROOT / run.folder(started)).resolve()
    named: str = folder.name
    again: int
    for again in itertools.count(2):  # past another execution of the label, started that minute
        if resumed is not None or not folder.exists():
            break
        folder = folder.with_name(f"{named}-{again}")
    folder.mkdir(parents=True, exist_ok=True)
    if not (resumed and (folder / "run.toml").exists()):
        _ = shutil.copyfile(argv[0], folder / "run.toml")
    _ = (folder / "facts.toml").write_text(_toml(facts), encoding="utf-8")
    return folder


def _all(run: Run, store: pipeline.Store) -> list[_Measured]:
    """Measure each of the run's corpora, `at-once` of them at a time.

    Returns:
      Each one's tree and failed steps, in the run's order.

    """
    known: catalog.Catalog = catalog.load()
    entries: list[catalog.Entry] = [known.entry(name) for name in known.names(list(run.include))]
    ports: dict[str, threading.Lock] = {entry.port: threading.Lock() for entry in entries}
    pool: ThreadPoolExecutor
    with ThreadPoolExecutor(run.at_once) as pool:
        return list(pool.map(partial(_measured, run, store, ports), entries))


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
