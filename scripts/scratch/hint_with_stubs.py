"""Ask a checker's hints for one file of a corpus's copy, with the corpus's stubs in the copy and without.

  local/.venv/bin/python -m scripts.scratch.hint_with_stubs CHECKER CORPUS FILE [NAME ...]

FILE is relative to the directory checked (`core/indexes/period.py`). The corpus is copied as a
run's fix step copies it (`launch.copied`: its `.py` files, its stubs, its settings), and FILE alone
is checked there with `--show-fixes --unsafe-fixes --infer-with=CHECKER` at `suffocate`, the checker
reading the whole copy; then every `.pyi` of the copy is removed and it's checked again. Prints the
fixes only one side lists, or each NAME binding's lines on each side. Both listings are kept
under `local/scratch/hint-with-stubs/CORPUS/`. Runs in a sandbox, one process: under a minute a side
on pandas with pyrefly, 16CPU/60GB.
"""

import sys
from pathlib import Path

from tests.corpus import catalog, launch, trees
from tests.corpus.run_config import DEV

OUT = Path(__file__).resolve().parents[2] / "local" / "scratch" / "hint-with-stubs"
FIX = ": fix "


def listed(where: launch.Place, checker: str, file: str) -> list[str]:
    one = where._replace(target=where.target / file)
    ran = launch.run(
        DEV, one, ["--show-fixes", "--unsafe-fixes", f"--infer-with={checker}", "--level=suffocate"], 1
    )
    return [line for line in (ran.output + ran.errors).splitlines() if FIX in line]


def main() -> int:
    checker, name, file, *names = sys.argv[1:]
    out = OUT / name.replace(" ", "-")
    tree = trees.found(catalog.load().entries[name], settle=False)
    where, _ = launch.copied(tree, out / "work")
    sides: dict[str, list[str]] = {"with stubs": listed(where, checker, file)}
    for stub in where.target.rglob("*.pyi"):
        stub.unlink()
    sides["without"] = listed(where, checker, file)
    for side, lines in sides.items():
        (out / f"{side.replace(' ', '-')}.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
        other = set(next(each for key, each in sides.items() if key != side))
        print(f"-- {side}: {len(lines)} fixes")
        for line in lines:
            if any(f"'{each}'" in line for each in names) if names else line not in other:
                print("  ", line)
    return 0


if __name__ == "__main__":
    sys.exit(main())
