"""Measure what `fix-widen` writes on a corpus, as docs/FIXES.md reports it, and what it costs a type checker.

  local/.venv/bin/python -m scratch.widen_census [CORPUS ...]

For each corpus (default: sqlalchemy and pydantic), three fixed copies under `local/corpus-table/`
(`corpus_table.copied`): `calls`, the two kinds of call alone and no guesses; `all`, every kind with
`--unsafe-fixes`; and `nocalls`, every kind but the calls' with `--unsafe-fixes`. For each: the
bindings each widen kind marks, the total and its share of the corpus's bindings, the share typed or
widened after, and what a second pass still changes (`widen_pass`'s count). For `all`, basedpyright's
errors on the copy before and after, by rule, with those gone and those new. Outside a sandbox;
`CORPUS_JOBS` sets the workers (every CPU, unset). About 10 minutes for both.
"""

import collections
import json
import re
import subprocess
import sys
from pathlib import Path

from constricter.offences import WIDEN_KINDS
from tests.corpus import corpus_table

ROOT = Path(__file__).resolve().parents[1]
BASEDPYRIGHT = ROOT / "local" / ".venv" / "bin" / "basedpyright"
CALLS = ("untyped-calls", "unknown-calls")
CONFIGS: dict[str, tuple[str, tuple[str, ...]]] = {
    "calls": (",".join(CALLS), ()),
    "all": ("all", ("--unsafe-fixes",)),
    "nocalls": (",".join(sorted(WIDEN_KINDS - set(CALLS))), ("--unsafe-fixes",)),
}
BASE = ["--level=suffocate", "--all-scopes", corpus_table.JOBS]
# A line a second pass adds or changes for a binding: not a file's header, nor an import it adds.
BOUND = re.compile(r"^\+(?!\+\+ )(?!\s*(?:from |import |if TYPE_CHECKING))", re.MULTILINE)


def _errors(project: Path, package: str) -> collections.Counter[str]:
    """basedpyright's errors under `project` (its `package`), counted by rule."""
    config = {"venvPath": str(ROOT / "local"), "venv": ".venv", "typeCheckingMode": "standard", "include": [package]}
    (project / "pyrightconfig.json").write_text(json.dumps(config), encoding="utf-8")
    done = subprocess.run([str(BASEDPYRIGHT), "--project", str(project), "--outputjson"], capture_output=True, text=True, check=False)
    found = json.loads(done.stdout)["generalDiagnostics"]
    return collections.Counter(d.get("rule") or "-" for d in found if d["severity"] == "error")


def main() -> None:
    wanted = sys.argv[1:] or ["sqlalchemy", "pydantic"]
    python = sys.executable
    for corpus in corpus_table.corpora():
        if corpus.name not in wanted:
            continue
        print(f"== {corpus.name} {corpus.version}", flush=True)
        for label, (kinds, extra) in CONFIGS.items():
            root, valid = corpus_table.copied(corpus, f"widen-{label}")
            args = [*BASE, *extra, f"--fix-widen={kinds}", str(root)]
            report = json.loads(corpus_table._run(python, ["--format=json", *args]) or "[]")
            widened = [r["fix"] for r in report if r.get("fix") and set(r["fix"]["kinds"]) & WIDEN_KINDS]
            by_kind = collections.Counter(k for fix in widened for k in fix["kinds"] if k in WIDEN_KINDS)
            total = corpus_table.typed_in(root)
            before = _errors(root.parent, root.name) if label == "all" else None
            first = corpus_table._run(python, ["--fix", *args])
            broken = sum(not corpus_table.compiles(path) for path in valid)
            second = len(BOUND.findall(corpus_table._run(python, ["--diff", *args])))
            typed = corpus_table.typed_in(root)
            share = f"{len(widened) / total.total:.1%} of {total.total}" if total else "?"
            kinds_text = ", ".join(f"{n} by {k}" for k, n in by_kind.most_common())
            after_text = f"{typed.typed / typed.total:.1%}" if typed else "?"
            print(
                f"  {label}: {corpus_table.fixed_count(first)} fixed, {len(widened)} widened ({share} bindings): {kinds_text};"
                f" typed or widened after: {after_text}; second pass {second}; broken {broken}",
                flush=True,
            )
            if before is not None:
                after = _errors(root.parent, root.name)
                print(f"  basedpyright: {sum(before.values())} errors before, {sum(after.values())} after; "
                      f"gone {dict(before - after)}; new {dict(after - before)}", flush=True)


if __name__ == "__main__":
    main()
