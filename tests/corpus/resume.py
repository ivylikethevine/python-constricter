"""A run's facts (`facts.toml`), and an execution resuming a run's folder or joining its stages.

The facts say what the run was: its run file's values, the checkout's version, commit and changes,
the machine, and the type checkers' versions. An execution with `--resume` carries the folder's
facts on, adds its minutes to the run's, and joins its stage to those already run.
"""

import hashlib
import itertools
import os
import platform
import shutil
import subprocess  # asks git for the commit
import sys
import tomllib
from collections.abc import Sequence
from datetime import datetime
from pathlib import Path
from typing import Final, cast

import tomli_w

from constricter import __version__
from constricter.source import parsed
from tests.corpus import corpus_suite, pipeline, render, sizing, suite_steps, trees
from tests.corpus.pipeline import Record
from tests.corpus.run_config import FACTS, JOIN, LABEL, RESUME, ROOT, STAGE, STARTED, Command, Run, outside

LOG: Final = "runner.log"  # in a run's folder
STAGES: Final = "stages"  # in a run's facts: each stage run, with its commit
_RUNNING: Final = "running"  # and when the one under way started: gone once it ends


def run_facts(run: Run, started: datetime) -> Record:
    """Gather what a run's outputs say of the run itself.

    Returns:
      The run file's values, this checkout's version and commit, the machine's CPUs and memory,
      and the keys a record is comparable across runs by: each type checker's version, and the
      version of what reads a suite's tests' output.

    """
    commit: str = _git("rev-parse", "--short=12", "HEAD").strip()
    return {
        "label": run.label,
        "started": started.isoformat(timespec="seconds"),
        "versions": list(run.versions),
        "formats": list(run.formats),
        "jobs": run.jobs,
        "at-once": run.at_once,
        "corpora": list(run.include),
        "minus": list(run.minus),
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
        "suite-seconds": run.suite_seconds,
        "suite-workers": run.suite_workers,
        "constricter": __version__,
        "commit": commit,
        "changes": changes(run.output),
        "python": platform.python_version(),
        "system": platform.system(),
        "cpus": os.cpu_count() or 1,
        "share": run.share,
        "gigabytes": round((parsed.memory() or 0) / sizing.GIB),
        "checkers": checkers(run),
        "parser": corpus_suite.parser(),
    }


def _git(*args: str) -> str:
    """Ask this checkout's git.

    Returns:
      What it printed.

    """
    return subprocess.run(["git", *args], capture_output=True, text=True, check=False, cwd=ROOT).stdout


def changes(output: Path) -> str:
    """Name the checkout's uncommitted changes: tracked files' and the untracked files git sees.

    Not those under `output`, where the runs write their folders: a run's own output leaves the
    tree the next one measures as clean as it was.

    Returns:
      A hash of them; nothing for a clean tree.

    """
    beside: list[str] = outside(output, ROOT)
    changed: str = _git("diff", "HEAD", "--binary", *beside)
    untracked: list[str] = _git("ls-files", "--others", "--exclude-standard", *beside).splitlines()
    path: str
    for path in untracked:
        changed += f"\n{path}\n" + (ROOT / path).read_text(encoding="utf-8", errors="replace")
    return hashlib.sha256(changed.encode()).hexdigest()[:12] if changed else ""


def checkers(run: Run) -> list[str]:
    """Name each type checker the run's `infer-with` starts, with its version: `--version`'s first line.

    Found as `--infer-with` finds it: on the path, or beside this Python.

    Returns:
      Them; `(not found)` for one that isn't installed.

    """
    found: list[str] = []
    name: str
    for name in run.steps.infer:
        path: str | None
        if (path := shutil.which(name) or shutil.which(name, path=str(Path(sys.executable).parent))) is None:
            found.append(f"{name} (not found)")
            continue
        said: str = subprocess.run([path, "--version"], capture_output=True, text=True, check=False).stdout
        line: str = said.strip().partition("\n")[0]
        found.append(line if line.startswith(name) else f"{name} {line}")
    return found


def facts_toml(facts: Record) -> str:
    """Write flat facts as TOML.

    Returns:
      The text.

    """
    return tomli_w.dumps(facts)


def joined(said: Command, earlier: Record, facts: Record, stage: str | None) -> Record:
    """Join a stage to the folder `--resume` names, noting it and its commit in the run's facts.

    `earlier`: the folder's facts (`resumed_facts`). Its stages carry on to an execution of no stage.

    Returns:
      The facts, with each stage run.

    Raises:
      SystemExit: the folder's stages ran on another commit, other uncommitted changes or another
        run file, and `--join-anyway` isn't given.

    """
    before: list[str] = list(cast("list[str]", earlier.get(STAGES, [])))
    if stage is None:
        return facts | ({STAGES: before} if before else {})
    now: str = _spelled(facts)
    if earlier and not said.join:  # facts read from `--resume`'s folder
        kept: Path = cast("Path", said.resume) / "run.toml"
        message: str = ""
        if _spelled(earlier) != now:
            message = f"the folder's stages ran on {_spelled(earlier)}, this on {now}: run it there"
        elif kept.exists() and kept.read_bytes() != cast("Path", said.run_file).read_bytes():
            message = f"{said.run_file} isn't the run file the folder's stages ran ({kept}): name that one"
        if message:
            message = f"{STAGE} {stage}: {message}, or {JOIN}"
            raise SystemExit(message)
    return facts | {STAGES: [*before, f"{stage} {now}"]}


def _spelled(facts: Record) -> str:
    """Name the tree a run's facts were made on: its commit, and its uncommitted changes' hash.

    Returns:
      `abc123def456`, or `abc123def456+0123456789ab`.

    """
    changed: str = str(facts.get("changes", ""))
    return f"{facts.get('commit', '')}{f'+{changed}' if changed else ''}"


def missing(run: Run, store: pipeline.Store, measured: Sequence[trees.Tree]) -> list[str]:
    """Name the steps of the run, on every corpus measured and with every version, that have no record.

    Returns:
      Them: one that failed, and one left for the stage it needs.

    """
    found: list[str] = []
    tree: trees.Tree
    version: str
    for tree in measured:
        for version in run.versions:
            job: pipeline.Job = pipeline.Job(run, store, tree, version)
            found += [
                name
                for name in (*pipeline.steps(run), *suite_steps.waiting(job))
                if store.read(tree.name, job.recorded, name) is None
            ]
    return found


def resumed_facts(said: Command) -> Record:
    """Read the facts of the run `--resume` carries on.

    Returns:
      Its folder's `facts.toml`; nothing for a new run, or a folder that has none.

    """
    if said.resume is None:
        return {}
    path: Path = said.resume / FACTS
    return tomllib.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def last_written(said: Command) -> datetime | None:
    """Say when the run `--resume` carries on last wrote its `runner.log`: a step's end.

    Returns:
      The time; `None` for a new run, or one that ended no step.

    """
    if said.resume is None:
        return None
    log: Path = said.resume / LOG
    return datetime.fromtimestamp(log.stat().st_mtime).astimezone() if log.exists() else None


def relabelled(run: Run, said: Command, earlier: Record) -> Run:
    """Give a resumed run the label it was started under, whatever its run file says.

    `earlier`: the facts of the run it carries on (`resumed_facts`).

    Returns:
      The run, under that label.

    Raises:
      SystemExit: `--label` names another, which would measure every corpus again beside it.

    """
    label: str | None
    if (label := cast("str | None", earlier.get("label"))) is None:  # `_toml` writes it as a string
        return run
    if said.label is not None and run.label != label:
        message: str = f"{RESUME} carries on the run labelled {label!r}, not {run.label!r}: leave out {LABEL}"
        raise SystemExit(message)
    return run._replace(label=label)


def carried(facts: Record, earlier: Record, last: datetime | None) -> Record:
    """Carry a stopped run's start and time into a resumed one's facts.

    `earlier`: the stopped run's facts; `last`: when it last ended a step. Its executions' minutes
    are those that ended (`finished`), and one that was stopped from where it started to `last`.

    Returns:
      The facts, with the first execution's start, the minutes before this one, and this one's start.

    """
    now: str = str(facts[STARTED])
    if not earlier:
        return facts | {_RUNNING: now}
    before: float = float(cast("float", earlier.get(render.MINUTES, 0)))
    stopped: str | None = cast("str | None", earlier.get(_RUNNING))
    if stopped is None and render.MINUTES not in earlier:  # no minutes: its one execution was stopped
        stopped = cast("str | None", earlier.get(STARTED))
    if stopped is not None and last is not None:
        before += max(0.0, (last - datetime.fromisoformat(stopped)).total_seconds() / 60)
    return facts | {STARTED: earlier.get(STARTED, now), render.MINUTES: round(before), _RUNNING: now}


def finished(facts: Record, minutes: float) -> Record:
    """Add an execution's minutes to its run's, as it ends.

    Returns:
      The facts, with the run's minutes and none under way.

    """
    total: int = round(float(cast("float", facts.get(render.MINUTES, 0))) + minutes)
    return {key: value for key, value in facts.items() if key != _RUNNING} | {render.MINUTES: total}


def run_folder(said: Command, run: Run, facts: Record) -> Path:
    """Make the folder this execution writes, or take the one `--resume` names, and keep the run file there.

    Returns:
      The folder.

    """
    resumed: Path | None = said.resume
    started: datetime = datetime.fromisoformat(str(facts["started"]))
    folder: Path = (resumed or ROOT / run.folder(started)).resolve()
    named: str = folder.name
    again: int
    for again in itertools.count(2):  # past another execution of the label, started that minute
        if resumed is not None or not folder.exists():
            break
        folder = folder.with_name(f"{named}-{again}")
    folder.mkdir(parents=True, exist_ok=True)
    if not (resumed and (folder / "run.toml").exists()):
        _ = shutil.copyfile(cast("Path", said.run_file), folder / "run.toml")
    _ = (folder / FACTS).write_text(facts_toml(facts), encoding="utf-8")
    return folder
