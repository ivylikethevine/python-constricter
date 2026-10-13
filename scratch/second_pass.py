# SPDX-License-Identifier: MIT
"""Fix a copy of one corpus as a run's fix step does, and print what a second pass would still fix.

  local/.venv/bin/python -m scratch.second_pass CORPUS [OPTION ...]   # `--unsafe-fixes`, `--likely`

The copy is kept in `local/scratch/second-pass/CORPUS/`, fixed once: the diff printed is the second
pass's (`--diff`), and `--jobs=1`, so it runs in a sandbox.
"""

import sys
from pathlib import Path

from tests.corpus import catalog, launch, trees

OUT = Path(__file__).resolve().parents[1] / "local" / "scratch" / "second-pass"


def main(name: str, extra: list[str]) -> int:
    tree = trees.found(catalog.load().entry(name))
    where, _ = launch.copied(tree, OUT / name.replace(" ", "-"))
    options = [*extra, "--level=suffocate"]
    first = launch.run("dev", where, ["--fix", *options], 1)
    print(first.output.strip().rsplit("\n", 1)[-1], file=sys.stderr)
    second = launch.run("dev", where, ["--diff", *options], 1)
    print(second.output)
    print(second.errors, file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1], sys.argv[2:]))
