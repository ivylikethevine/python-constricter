"""Say whose settings pyrefly and ty take for each corpus's copy: the copy's own, or this checkout's.

  local/.venv/bin/python -m scratch.checker_roots [CORPUS ...]

A run's copy of a corpus lies under this checkout with the settings files `launch.copied` gives it
(`checker_settings.FILES`, a suite's, then an empty one of each checker's it lacks). For each corpus
this lays those files out under `local/scratch/checker-roots/CORPUS/` with one empty module where
the package would be, and asks `pyrefly dump-config` for its configuration file and import root, and
`ty check -vv` for its first-party search path and environment, each run from there with the
corpus's environment as `VIRTUAL_ENV`, as a run starts them. The command-line tools stand for the
servers a run starts. Prints a row a corpus: whether each checker's root is the copy (`own`) or
this checkout (`above`), then the counts. Runs in a sandbox, a few seconds a corpus.
"""

import re
import shutil
import subprocess
import sys
from pathlib import Path

from tests.corpus import catalog, checker_settings, launch, trees

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "local" / "scratch" / "checker-roots"
CONFIGURATION = re.compile(r"Configuration at `([^`]+)`")
DEFAULT = re.compile(r"Default configuration|No config")
FIRST_PARTY = re.compile(r"Adding first-party search path `([^`]+)`")
ENVIRONMENT = re.compile(r"site-packages directory in sys.prefix (\S+)")


def placed(root: Path, where: Path) -> str:
    return (
        "own"
        if root == where or where in root.parents
        else "above"
        if root in (ROOT, *ROOT.parents)
        else str(root)
    )


def main() -> int:
    names = sys.argv[1:]
    tools = Path(sys.executable).parent
    counts: dict[str, int] = {}
    print(f"{'corpus':22} {'pyrefly':8} {'ty':8} ty's environment")
    for name, entry in catalog.load().entries.items():
        if names and name not in names:
            continue
        tree = trees.found(entry, settle=False)
        where = OUT / name.replace(" ", "-")
        shutil.rmtree(where, ignore_errors=True)
        target = where / (tree.root.relative_to(tree.base) if tree.base else tree.root.name)
        target.mkdir(parents=True)
        probe = target / "probe.py"
        probe.write_text("VALUE = 1\n", encoding="utf-8")
        base = tree.base
        for each in checker_settings.FILES if base is not None else ():
            if base is not None and (base / each).is_file():
                shutil.copyfile(base / each, where / each)
        checker_settings.own(where)
        env = launch.environment(launch.Place(where, target, tree.environment))
        relative = str(probe.relative_to(where))
        dumped = subprocess.run(
            [str(tools / "pyrefly"), "dump-config", relative],
            cwd=where,
            env=env,
            capture_output=True,
            text=True,
            check=False,
        )
        told = dumped.stdout + dumped.stderr
        found = CONFIGURATION.search(told)
        pyrefly = placed(Path(found[1]).parent, where) if found else "none" if DEFAULT.search(told) else "?"
        checked = subprocess.run(
            [str(tools / "ty"), "check", "-vv", relative],
            cwd=where,
            env=env,
            capture_output=True,
            text=True,
            check=False,
        )
        said = checked.stdout + checked.stderr
        first = FIRST_PARTY.search(said)
        ty = placed(Path(first[1]), where) if first else "?"
        prefix = ENVIRONMENT.search(said)
        environment = (
            "?"
            if prefix is None
            else "the dev venv"
            if Path(prefix[1]) == ROOT / "local" / ".venv"
            else "its own"
        )
        print(f"{name:22} {pyrefly:8} {ty:8} {environment}")
        for key in (f"pyrefly {pyrefly}", f"ty {ty}"):
            counts[key] = counts.get(key, 0) + 1
    print(", ".join(f"{key}: {count}" for key, count in sorted(counts.items())))
    return 0


if __name__ == "__main__":
    sys.exit(main())
