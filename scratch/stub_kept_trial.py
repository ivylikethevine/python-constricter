"""Try: a file checked again as other text than the index read still reads its own stub. Count its second pass.

  local/.venv/bin/python -m scratch.stub_kept_trial CORPUS [--plain] [--rounds=N] [OPTION ...]

A file's own stub (`mod.pyi` beside `mod.py`) reaches its check through the tables the index keeps
for the text it read (`parsed.keep`): a check of any other text, as `--fix` makes within a round
once a file's first fixes are written, reads the module alone (`checker._parse`). This patches
`checker._parse` in this process to read the stub again for such a text, as `modules._own` does,
fixes a copy of CORPUS with `--fix` and each OPTION (`--unsafe-fixes`, `--infer-with=pyrefly`) in one
process, then asks an unpatched `--diff` what a second pass would still fix. `--plain` leaves the
patch out, for the same run without it (the package reads the stub itself since
`modules.checkable`, so both now give the same); `--rounds=N` lets a file be fixed N times, not
`rounds.HINT_ROUNDS`, to tell a second pass a further round would have made. Prints the fixes and
the second pass's `+` lines; the copy and the diff are kept under
`local/scratch/stub-kept-trial/CORPUS/`. Runs in a sandbox. About 2 minutes on matplotlib and 5 on
pandas with pyrefly's hints, 1 worker on 16CPU/60GB.
"""

import ast
import contextlib
import io
import os
import sys
from pathlib import Path

from constricter.cli import rounds
from constricter.cli.command import main
from constricter.fix.index import modules, own_stubs
from constricter.fix.values.tables import Tables
from constricter.rules import checker
from tests.corpus import catalog, corpus_table, launch, trees
from tests.corpus.run_config import DEV

OUT = Path(__file__).resolve().parents[1] / "local" / "scratch" / "stub-kept-trial"
PLAIN = "--plain"
ROUNDS = "--rounds="
kept_parse = checker._parse
read_again: list[str] = []


def stubbed_parse(source: str | bytes, filename: str) -> tuple[ast.Module, Tables | None]:
    tree, own = kept_parse(source, filename)
    path = Path(filename)
    if own is not None or path.suffix != modules.SUFFIX:
        return tree, own
    named = modules.module_name(path)
    is_package = path.stem == modules.PACKAGE
    if (beside := own_stubs.beside(path, named, is_package=is_package)) is None:
        return tree, None
    alone = modules.module_tables(tree)
    names = modules.origins_of(tree, named, is_package=is_package)
    names.update(modules.skipped(tree, names))
    guarded = modules.guarded_origins(tree, named, is_package=is_package)
    writable = frozenset(names).union(guarded, alone.classes, modules.BUILTINS)
    read_again.append(filename)
    return tree, own_stubs.stubbed(alone, beside[0], lambda each: modules.roots(each) <= writable)


def run() -> int:
    name, *given = sys.argv[1:]
    options = [
        *(each for each in given if each != PLAIN and not each.startswith(ROUNDS)),
        "--level=suffocate",
    ]
    for each in given:
        if each.startswith(ROUNDS):
            rounds.HINT_ROUNDS = int(each.removeprefix(ROUNDS))
    if PLAIN not in given:
        checker._parse = stubbed_parse
    out = OUT / name.replace(" ", "-")
    tree = trees.found(catalog.load().entries[name], settle=False)
    where, valid = launch.copied(tree, out / "work")
    target = os.path.relpath(where.target, where.cwd)
    back = Path.cwd()
    os.chdir(where.cwd)
    os.environ["VIRTUAL_ENV"] = str(where.environment or sys.prefix)
    sys.argv = [
        "constricter",
        "--fix",
        "--show-fixes",
        *options,
        "--no-gitignore",
        "--all-scopes",
        "--jobs=1",
        target,
    ]
    listing = io.StringIO()
    with contextlib.redirect_stdout(listing), contextlib.suppress(SystemExit):
        _ = main()
    os.chdir(back)
    second = launch.run(DEV, where, ["--diff", *options], 1)
    (out / "fixes.txt").write_text(listing.getvalue(), encoding="utf-8")
    (out / "second.diff").write_text(second.output + second.errors, encoding="utf-8")
    print(
        f"{name}: {len(valid)} files, fixed {corpus_table.fixed_count(listing.getvalue())}, "
        f"second pass {corpus_table.added(second.output)}; "
        f"{len(read_again)} checks of {len(set(read_again))} files read their stub again"
    )
    return 0


if __name__ == "__main__":
    sys.exit(run())
