# SPDX-License-Identifier: MIT
"""Measure corpora as a run file says, into a folder of that run's own.

    local/.venv/bin/python -m tests.corpus RUN.toml                   # a new folder, named by label and time
    local/.venv/bin/python -m tests.corpus RUN.toml --resume FOLDER   # carry on a stopped run in its folder

The run file (`run_config`) names the corpora (`corpora.toml`'s), the constricter versions, the
steps and the formats. Each execution writes `<output>/<label>-<month>-<day>-<year>-<time>/`:

    run.toml      the run as it was read, the commit and the machine
    records/      <corpus>/<version>/<step>.json, and each fix's patch: what every output is made from
    logs/         what each step's constricter wrote to standard error
    report.json   report.md   tables/*.csv

Every step starts constricter one way (`launch.run`) on one tree a corpus (`catalog.Tree`), so a
count in one table is the count in another.
"""

import os
import platform
import shutil
import subprocess  # asks git for the commit
import sys
from collections.abc import Sequence
from datetime import datetime
from pathlib import Path
from typing import Final, cast

from constricter import __version__
from tests.corpus import catalog, pipeline, render
from tests.corpus.pipeline import Record
from tests.corpus.run_config import Run, read

_RESUME: Final = "--resume"
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
        "corpora": list(run.include),
        "check": run.steps.check,
        "fix": list(run.steps.fix),
        "coverage": run.steps.coverage,
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


def main(argv: Sequence[str]) -> int:
    """Run the run file named, write its folder, and say where it is.

    Returns:
      0.

    """
    resumed: Path | None = Path(argv[argv.index(_RESUME) + 1]) if _RESUME in argv else None
    run: Run = read(Path(argv[0]))
    started: datetime = datetime.now().astimezone()
    folder: Path = (resumed or _ROOT / run.folder(started)).resolve()
    folder.mkdir(parents=True, exist_ok=True)
    facts: Record = _facts(run, started)
    _ = (folder / "run.toml").write_text(_toml(facts), encoding="utf-8")
    store: pipeline.Store = pipeline.Store(folder)
    known: catalog.Catalog = catalog.load()
    trees: list[catalog.Tree] = []
    name: str
    for name in known.names(list(run.include)):
        trees.append(known.tree(name))
        version: str
        for version in run.versions:
            pipeline.measure(pipeline.Job(run, store, trees[-1], version))
    shutil.rmtree(folder / "work", ignore_errors=True)  # the copies its fixes worked on
    written: list[Path] = render.write(render.gathered(run, store, trees), folder, facts)
    _ = sys.stdout.write("".join(f"{path}\n" for path in written))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
