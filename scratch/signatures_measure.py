"""Fix a copy of a corpus pass after pass, with and without the signature codes, and count each pass.

  local/.venv/bin/python -m scratch.signatures_measure CORPUS [--modes certain,likely,unsafe,signed]
      [--select LVA014,LVA015] [--passes 4] [--jobs 1] [--label NAME]

For each mode (`certain`: `--fix`; `likely`: `--fix --likely`; `unsafe`: `--fix --unsafe-fixes`),
a copy of the corpus laid out as its checkout (`launch.copied`) is fixed at `suffocate` in every
scope, pass after pass until a pass fixes nothing (`--passes` at most): once as the runner's fix
steps do, and once with `--extend-select` of the signature codes. The `signed` mode is the
workflow a user would follow: `--fix --unsafe-fixes --select` of the signature codes alone first
(the signatures written, every guess among them), then `--fix` passes. Each pass's `--show-fixes
--format=json` listing is kept, and `--coverage` is run after the last. Prints one row per pass:
the fixes made, split certain, likely and guess, those of each signature code, and the coverage
at the end (`typed/bindings`, the `--coverage` total: first bindings, not signatures).

Everything goes under `local/scratch/signatures/LABEL/` (`--label`, default the corpus's name).
Inside a sandbox `--jobs 1`; a suite's checkout is cloned and installed the first time.
"""

import argparse
import json
import sys
from pathlib import Path

from tests.corpus import catalog, launch, trees
from tests.corpus.corpus_table import _TYPED
from tests.corpus.run_config import DEV

OUT = Path(__file__).resolve().parents[1] / "local" / "scratch" / "signatures"
MODES = {"certain": [], "likely": ["--likely"], "unsafe": ["--unsafe-fixes"], "signed": []}
SIGNATURES = ("LVA014", "LVA015")


def fixed_rows(output: str):
    try:
        return [row for row in json.loads(output) if row.get("fixed")]
    except json.JSONDecodeError:
        return []


def count(rows):
    certain = sum(1 for r in rows if r["fix"] and not r["fix"]["unsafe"] and not r["fix"].get("likely"))
    likely = sum(1 for r in rows if r["fix"] and r["fix"].get("likely"))
    guess = sum(1 for r in rows if r["fix"] and r["fix"]["unsafe"] and not r["fix"].get("likely"))
    codes = {code: sum(1 for r in rows if r["code"] == code) for code in SIGNATURES}
    return certain, likely, guess, codes


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("corpus")
    parser.add_argument("--modes", default="certain,likely,unsafe")
    parser.add_argument("--select", default="LVA014")
    parser.add_argument("--passes", type=int, default=4)
    parser.add_argument("--jobs", type=int, default=1)
    parser.add_argument("--label", default=None)
    args = parser.parse_args()
    label = args.label or args.corpus
    out = OUT / label
    out.mkdir(parents=True, exist_ok=True)
    tree = trees.found(catalog.load().entries[args.corpus])
    print(
        "label mode selected pass fixed certain likely guess " + " ".join(SIGNATURES) + " seconds", flush=True
    )
    for mode in args.modes.split(","):
        for selected in (True,) if mode == "signed" else (False, True):
            tag = f"{mode}-{'signatures' if selected else 'plain'}"
            where, _ = launch.copied(tree, out / "work" / tag)
            options = ["--level=suffocate", *MODES[mode]]
            if selected and mode != "signed":
                options.append(f"--extend-select={args.select}")
            if mode == "signed":
                first = [
                    "--fix",
                    "--show-fixes",
                    "--format=json",
                    "--level=suffocate",
                    "--unsafe-fixes",
                    f"--select={args.select}",
                ]
                ran = launch.run(DEV, where, first, args.jobs)
                (out / f"{tag}.pass0.json").write_text(ran.output, encoding="utf-8")
                certain, likely, guess, codes = count(fixed_rows(ran.output))
                print(
                    f"{label} {mode} yes 0 {len(fixed_rows(ran.output))} {certain} {likely} {guess} "
                    + " ".join(str(codes[code]) for code in SIGNATURES)
                    + f" {ran.seconds:.0f}",
                    flush=True,
                )
            for number in range(1, args.passes + 1):
                ran = launch.run(DEV, where, ["--fix", "--show-fixes", "--format=json", *options], args.jobs)
                (out / f"{tag}.pass{number}.json").write_text(ran.output, encoding="utf-8")
                if ran.errors.strip():
                    (out / f"{tag}.pass{number}.err").write_text(ran.errors, encoding="utf-8")
                rows = fixed_rows(ran.output)
                certain, likely, guess, codes = count(rows)
                print(
                    f"{label} {mode} {'yes' if selected else 'no'} {number} {len(rows)} {certain} {likely} {guess} "
                    + " ".join(str(codes[code]) for code in SIGNATURES)
                    + f" {ran.seconds:.0f}",
                    flush=True,
                )
                if not rows:
                    break
            coverage = launch.run(DEV, where, ["--coverage"], args.jobs)
            found = _TYPED.search(coverage.output)
            typed = f"{found.group(1)}/{found.group(2)}" if found else "?"
            print(f"{label} {mode} {'yes' if selected else 'no'} coverage {typed}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
