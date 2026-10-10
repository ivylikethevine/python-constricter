# SPDX-License-Identifier: MIT
"""List every guess `--fix --unsafe-fixes` makes on each suite's checkout, with what blames or bears it out.

For each package: its fixes (certain and guessed) as `corpus_suite.fixed_and_listed` lists them, the
type errors its last kept run blamed on a fix, and, where its tests' trace is kept, what each fixed
binding held at run time. Written as JSON lines, one fix a line, in `local/scratch/guesses/`.

  local/.venv/bin/python -m scratch.guess_census            # every suite, about 15 minutes
  local/.venv/bin/python -m scratch.guess_census NAME ...   # only these

Outside a sandbox, and with no corpora run going: it fixes each checkout in place, then resets it.
The blamed errors are those of the package's last kept super or mega corpora run, the trace the one
its last `traced` step left in the checkout. `scratch.guess_report` reads what this writes.
"""

import glob
import hashlib
import json
import pickle
import sys
from pathlib import Path

from tests.corpus import corpus_suite, mega_corpora

REPO = Path(__file__).resolve().parents[1]
OUT = REPO / "local" / "scratch" / "guesses"
TRACE = ".venv/corpus-suite-trace.json"


def suites() -> dict[str, corpus_suite.Suite]:
    found = dict(corpus_suite.SUITES)
    for name, package in mega_corpora.packages().items():
        if package.suite is not None:
            found[name] = package.suite
    return found


def blamed(name: str) -> tuple[dict[tuple[str, int, str], int], int, bool]:
    """The errors of the package's last kept `--fix --unsafe-fixes` type check, by the fix blamed."""
    kept = sorted(
        glob.glob(str(REPO / "local" / "*-corpora" / "0.3.6-*" / name.replace(" ", "-") / "types.pickle")),
        key=lambda path: Path(path).stat().st_mtime,
    )
    if not kept:
        return {}, 0, False
    with open(kept[-1], "rb") as file:
        value = pickle.load(file).value
    errors: dict[tuple[str, int, str], int] = {}
    untraced = 0
    for label, compared in value.fixed:
        if label != "--fix --unsafe-fixes":
            continue
        for each in compared.new:
            if each.fix is None:
                untraced += 1
            else:
                key = (each.fix.path, each.fix.line, each.fix.name)
                errors[key] = errors.get(key, 0) + 1
    return errors, untraced, True


def seen(root: Path) -> dict[str, dict[str, dict[str, list[str]]]]:
    """The trace's bindings, by the file's path: only files whose text is what was traced."""
    path = root / TRACE
    if not path.exists():
        return {}
    found = {}
    for digest, each in json.loads(path.read_text(encoding="utf-8"))["files"].items():
        file = root / each["path"]
        if file.exists() and hashlib.sha256(file.read_bytes()).hexdigest() == digest:
            found[each["path"]] = each["bindings"]
    return found


def main(names: list[str]) -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    every = suites()
    for name in names or every:
        suite = every[name]
        root = corpus_suite.checkout(name, suite)
        corpus_suite.reset(root, suite)
        traced = seen(root)
        errors, untraced, checked = blamed(name)
        try:
            fixes, change = corpus_suite.fixed_and_listed(root, suite, "--unsafe-fixes")
        finally:
            corpus_suite.reset(root, suite)
        rows = []
        for path, listed in fixes.items():
            bindings = traced.get(path, {})
            for fix in listed:
                rows.append(
                    {
                        "package": name,
                        "path": fix.path,
                        "line": fix.line,
                        "name": fix.name,
                        "annotation": fix.annotation,
                        "kinds": fix.kinds,
                        "unsafe": fix.unsafe,
                        "errors": errors.get((fix.path, fix.line, fix.name), 0),
                        "checked": checked,
                        "seen": bindings.get(str(fix.line), {}).get(fix.name),
                    },
                )
        with open(OUT / f"{name}.jsonl", "w", encoding="utf-8") as file:
            for row in rows:
                file.write(json.dumps(row) + "\n")
        guesses = sum(row["unsafe"] for row in rows)
        print(
            f"{name}: {len(rows)} fixes, {guesses} guesses, {sum(errors.values())} blamed errors "
            f"({untraced} untraced), {sum(row['seen'] is not None for row in rows)} seen at run time; {change}",
            flush=True,
        )
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
