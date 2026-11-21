"""Fix a fresh copy of one corpus as a hinted step does, printing each round's hints and fixes in a file.

  local/.venv/bin/python -m scripts.scratch.hint_rounds CORPUS FILE FIRST LAST [OPTION ...]

FILE is the copy's path ending (`matplotlib/animation.py`), FIRST and LAST the lines to print, each
OPTION goes to the fix (`--unsafe-fixes --infer-with=pyrefly`, `--infer-fresh` to ask the checkers
again rather than read the store). For each round of `rounds.settled`, to standard error: the files
it changed since the round before, the checkers' hints on those lines as the round asked for them,
and the fixes made there. In one process, so it runs in a sandbox; matplotlib with pyrefly took
about 2 minutes on 16CPU/60GB. The copy is kept under `local/scratch/hint-rounds/CORPUS/`.
"""

import os
import sys
from collections.abc import Callable, Sequence
from pathlib import Path

from constricter.cli import rounds
from constricter.cli.command import main as fix
from constricter.cli.runs import CheckRun, FileRun
from constricter.fix.core.known import Hints, Outside
from constricter.fix.index import project
from tests.corpus import catalog, launch, trees

OUT: Path = Path(__file__).resolve().parents[2] / "local" / "scratch" / "hint-rounds"


def main() -> int:
    name, file, first, last, *options = sys.argv[1:]
    low: int = int(first)
    high: int = int(last)
    tree: trees.Tree = trees.found(catalog.load().entries[name], settle=False)
    where: launch.Place
    where, _ = launch.copied(tree, OUT / name.replace(" ", "-") / "work")
    original: Callable[..., tuple[list[FileRun], project.Index]] = rounds.checked_all
    seen: dict[Path, str] = {}
    count: list[int] = [0]

    def logged(
        paths: Sequence[Path],
        check: Callable[[Path, Outside], FileRun],
        given: rounds.Options,
        session: "rounds.hints.Session | None" = None,
        known: rounds._Known = rounds._FIRST,  # noqa: SLF001
    ) -> tuple[list[FileRun], project.Index]:
        count[0] += 1
        now: dict[Path, str] = {path: path.read_text(encoding="utf-8") for path in where.target.rglob("*.py")}
        changed: list[str] = sorted(
            str(path.relative_to(where.target)) for path in now if now[path] != seen.get(path)
        )
        seen.clear()
        seen.update(now)
        on: list[Path] = [path for path in paths if str(path).endswith(file)]
        _say(f"--- round {count[0]}: {len(paths)} files, {file} {'in' if on else 'not in'} it")
        if count[0] > 1:
            _say(f"    changed since the round before: {changed}")
        if on and session is not None:
            asked: dict[Path, str] = {on[0]: on[0].read_text(encoding="utf-8")}
            found: Hints
            for found in session.hints(asked)[on[0]]:
                for (line, column), text in sorted(found.types.items()):
                    if low <= line <= high:
                        _say(f"    hint {found.checker} {line}:{column} {text}")
        runs: list[FileRun]
        modules: project.Index
        runs, modules = original(paths, check, given, session, known)
        for path, run in zip(paths, runs, strict=True):
            if str(path).endswith(file) and isinstance(run, CheckRun):
                for made in run.made:
                    if low <= made.offence.line <= high:
                        _say(f"    made {made.offence.line} {made.offence.name}: {made.offence.fix}")
        return runs, modules

    rounds.checked_all = logged
    os.environ.update(launch.environment(where))
    os.chdir(where.cwd)
    target: str = os.path.relpath(where.target, where.cwd)
    status: int = fix(
        ["--fix", *options, "--level=suffocate", "--no-gitignore", "--all-scopes", "--jobs=1", target]
    )
    _say(f"exit {status}")
    return 0


def _say(line: str) -> None:
    print(line, file=sys.stderr)


if __name__ == "__main__":
    sys.exit(main())
