# SPDX-License-Identifier: MIT
"""Check that this checkout's generator writes the standard-library tables there now, byte for byte.

  local/.venv/bin/python -m scratch.tables_unchanged

Runs `stdlib_tables.generate.generate()` in memory and compares each table it gives with the file
in `constricter/fix/tables/`, leaving out `source.json`, whose stamp changes with the generator's
code (see `stdlib_tables.generate.current`). For a refactor of `stdlib_tables/` or of what it imports:
the tables must come out the same. Prints each table that differs, with its first differing line,
and exits 1 if one does. Writes nothing. Outside a sandbox: the generator reads each configuration
in a worker process.
"""

import sys

from stdlib_tables.generate import OUTPUT, generate

_STAMP = "source.json"


def main() -> int:
    """Compare; return 1 if a table differs."""
    files = generate()
    differs = 0
    for path, text in sorted(files.items()):
        if path.name == _STAMP:
            continue
        was = path.read_text(encoding="utf-8") if path.exists() else None
        if was == text:
            continue
        differs += 1
        if was is None:
            print(f"{path.name}: new")
            continue
        line = next(
            (n for n, (a, b) in enumerate(zip(was.splitlines(), text.splitlines(), strict=False), 1) if a != b),
            min(len(was.splitlines()), len(text.splitlines())) + 1,
        )
        print(f"{path.name}: differs from line {line}")
    gone = sorted(p.name for p in OUTPUT.glob("*.json") if p not in files)
    for name in gone:
        print(f"{name}: no longer generated")
    print(f"{len(files) - 1} tables, {differs + len(gone)} differ")
    return 1 if differs or gone else 0


if __name__ == "__main__":
    sys.exit(main())
