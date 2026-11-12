"""Compare a checker's hints on a corpus's copy as a run makes it, and with an empty config of the checker's own in it.

  local/.venv/bin/python -m scripts.scratch.hint_config_trial CHECKER CORPUS [FILE] [--stubless] [--python-first]

A run's copy lies under this checkout (`corpus-runs/<run>/work/`), with the corpus's
`pyproject.toml`, `pyrightconfig.json` and `pyrefly.toml` where it has them. A checker that finds
no settings of its own there walks up to this checkout's (`[tool.pyrefly]`, `[tool.ty]`,
`pyrightconfig.json`): this checkout as the import root, its dev venv's packages, Python 3.11. This
copies CORPUS as a fix step does (`launch.copied`) and lists `--show-fixes --unsafe-fixes
--infer-with=CHECKER` at `suffocate` twice: the copy as it is, then with an empty `pyrefly.toml`,
`ty.toml` or `pyrightconfig.json` at its root, so the checker takes the copy as its project and
`VIRTUAL_ENV` as its environment. FILE (relative to the directory checked) checks that file alone,
the checker still reading the whole copy. `--stubless` removes the copy's `.pyi` files first, as a
copy was before stubs were copied. `--python-first` compares another thing: the copy and its
settings as they are, then with the corpus's environment's `bin` first on `PATH`, where a run puts
the dev venv's (`launch.environment`), since Pyright asks the first `python` there for its packages
and not `VIRTUAL_ENV`. Prints each side's fixes, those by the checker, and how many
only one side has or types otherwise; the listings are kept under
`local/scratch/hint-config-trial/CORPUS-CHECKER/`. Runs in a sandbox, one process: about 3 minutes
a side on pandas with pyrefly, 16CPU/60GB.

A run's copy has had each checker's empty settings and its environment's Python first on the path
since (`checker_settings.own`, `launch.environment`), so both sides now give the same: this is how
the difference was measured before.
"""

import os
import re
import sys
from pathlib import Path

from tests.corpus import catalog, launch, trees
from tests.corpus.run_config import DEV

OUT = Path(__file__).resolve().parents[2] / "local" / "scratch" / "hint-config-trial"
OWN = {"pyrefly": ("pyrefly.toml", ""), "ty": ("ty.toml", ""), "basedpyright": ("pyrightconfig.json", "{}\n")}
FIX = re.compile(
    r"^(?P<path>[^:]+):(?P<line>\d+):\d+: fix '(?P<name>[^']+)': `(?P<type>[^`]*)`.*\[(?P<kinds>[^\]]*)\]"
)
STUBLESS = "--stubless"
FIRST = "--python-first"


def listed(where: launch.Place, checker: str) -> dict[tuple[str, str, str], tuple[str, str]]:
    options = ["--show-fixes", "--unsafe-fixes", f"--infer-with={checker}", "--level=suffocate"]
    ran = launch.run(DEV, where, options, 1)
    found = {}
    for line in (ran.output + ran.errors).splitlines():
        if match := FIX.match(line):
            found[match["path"], match["line"], match["name"]] = (match["type"], match["kinds"])
    return found


def main() -> int:
    given = [each for each in sys.argv[1:] if each not in {STUBLESS, FIRST}]
    checker, name, *files = given
    out = OUT / f"{name.replace(' ', '-')}-{checker}"
    tree = trees.found(catalog.load().entries[name], settle=False)
    where, _ = launch.copied(tree, out / "work")
    if STUBLESS in sys.argv:
        for stub in where.target.rglob("*.pyi"):
            stub.unlink()
    if files:
        where = where._replace(target=where.target / files[0])
    sides = {"as a run copies it": listed(where, checker)}
    own, text = OWN[checker]
    kept = (where.cwd / own).read_text(encoding="utf-8") if (where.cwd / own).is_file() else None
    if FIRST in sys.argv and where.environment is not None:
        plain = launch.environment
        environment = where.environment

        def ahead(place: launch.Place) -> dict[str, str]:
            found = plain(place)
            return {**found, "PATH": os.pathsep.join((str(environment / "bin"), found["PATH"]))}

        launch.environment = ahead
        sides["with its environment's python first"] = listed(where, checker)
    else:
        print(f"{own} in the copy already: {kept is not None}")
        if kept is None:
            (where.cwd / own).write_text(text, encoding="utf-8")
        sides[f"with its own {own}"] = listed(where, checker)
    first, second = sides.values()
    for side, fixes in sides.items():
        hinted = sum("checker" in kinds for _, kinds in fixes.values())
        lines = [
            f"{path}:{line} {each}: {kind} [{kinds}]"
            for (path, line, each), (kind, kinds) in sorted(fixes.items())
        ]
        (out / f"{side.replace(' ', '-')}.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
        print(f"-- {side}: {len(fixes)} fixes, {hinted} by the checker")
    only = [key for key in first if key not in second]
    new = [key for key in second if key not in first]
    other = [key for key in first if key in second and first[key][0] != second[key][0]]
    print(
        f"only as a run copies it {len(only)}, only on the other side {len(new)}, typed otherwise {len(other)}"
    )
    for key in (*only[:15], *new[:15], *other[:30]):
        print("  ", ":".join(key), first.get(key, ("-",))[0], "|", second.get(key, ("-",))[0])
    return 0


if __name__ == "__main__":
    sys.exit(main())
