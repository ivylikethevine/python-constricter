# SPDX-License-Identifier: MIT
"""List every fix the last super and mega corpora runs made on each suite, with what blames or bears it out.

  local/.venv/bin/python -m scratch.guess_census            # every suite the runs kept
  local/.venv/bin/python -m scratch.guess_census NAME ...   # only these

It reads what the runs kept in `local/super-corpora/` and `local/mega-corpora/` (each package's
newest `tests`, `types` and `traced` steps) and runs nothing: the fixes of the one fixed run
(`--fix --unsafe-fixes`), the type errors that run's check traced to each, and how each fixed
binding's values stood to its annotation as the traced tests ran (`verdict`: how many fit, didn't,
and couldn't be told), with the types the trace spells for them (`seen`). Written as JSON lines,
one fix a line, in `local/scratch/guesses/`, which `scratch.guess_report` reads.
"""

import json
import pickle
import sys
from pathlib import Path

from tests.corpus import corpus_guesses, corpus_suite
from tests.corpus.corpora_steps import Tested, Traced, Typechecked

REPO = Path(__file__).resolve().parents[1]
OUT = REPO / "local" / "scratch" / "guesses"


def newest(name: str, step: str) -> object:
    """A package's newest kept step, or None."""
    kept = sorted(
        (REPO / "local").glob(f"*-corpora/*/{name.replace(' ', '-')}/{step}.pickle"),
        key=lambda path: path.stat().st_mtime,
    )
    if not kept:
        return None
    with open(kept[-1], "rb") as file:
        return pickle.load(file).value


def packages() -> list[str]:
    return sorted({path.parent.name for path in (REPO / "local").glob("*-corpora/*/*/tests.pickle")})


def main(names: list[str]) -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    for name in names or packages():
        tested = newest(name, "tests")
        checked = newest(name, "types")
        traced = newest(name, "traced")
        if not isinstance(tested, Tested) or not isinstance(tested.fixes, dict) or not tested.fixes:
            print(f"{name}: no fixes kept")
            continue
        errors: dict[tuple[str, int, str], int] = {}
        if isinstance(checked, Typechecked):
            for each in dict(checked.fixed)[corpus_suite.ALL[0]].new:
                if each.fix is not None:
                    key = (each.fix.path, each.fix.line, each.fix.name)
                    errors[key] = errors.get(key, 0) + 1
        seen = traced.seen if isinstance(traced, Traced) else {}
        judged = traced.verdicts if isinstance(traced, Traced) else {}
        rows = [
            {
                "package": name,
                "path": fix.path,
                "line": fix.line,
                "name": fix.name,
                "annotation": fix.annotation,
                "kinds": fix.kinds,
                "unsafe": fix.unsafe,
                "likely": fix.likely,
                "errors": errors.get((fix.path, fix.line, fix.name), 0),
                "checked": isinstance(checked, Typechecked),
                "seen": list(corpus_guesses.held(seen, fix.path, fix.line, fix.name)) or None,
                "verdict": list(corpus_guesses.verdict(judged, fix.path, fix.line, fix.name)),
            }
            for fixes in tested.fixes.values()
            for fix in fixes
        ]
        with open(OUT / f"{name}.jsonl", "w", encoding="utf-8") as file:
            for row in rows:
                file.write(json.dumps(row) + "\n")
        print(
            f"{name}: {len(rows)} fixes, {sum(row['unsafe'] for row in rows)} guesses, "
            f"{sum(errors.values())} blamed errors, {sum(any(row['verdict'][:2]) for row in rows)} told at run time",
            flush=True,
        )
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
