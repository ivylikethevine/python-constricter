# SPDX-License-Identifier: MIT
"""The standard-library tables are current: generated from the pinned stubs by this generator."""

import json
import subprocess  # imports the generator apart: it imports `constricter`'s modules without its `__init__`
import sys
from pathlib import Path
from typing import Final, cast

ROOT: Final = Path(__file__).parents[2]
LOADS_TABLES: Final = "constricter/fix/stdlib.py"
_IMPORTED: Final = """
import json, sys
from pathlib import Path
import stdlib_tables.generate as generate
modules = list(sys.modules.values())
files = (Path(module.__file__).resolve() for module in modules if getattr(module, "__file__", None))
print(json.dumps(sorted(
    file.relative_to(generate.ROOT).as_posix()
    for file in files
    if any(file.is_relative_to(generate.ROOT / package) for package in ("constricter", "stdlib_tables"))
)))
"""


def _run(code: str) -> str:
    """Run `code` in a new interpreter in the checkout.

    Returns:
      What it printed.

    """
    return subprocess.run(
        [sys.executable, "-c", code],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=True,
    ).stdout


def test_tables_current() -> None:
    """The tables were generated from what's here now: if not, run `python -m stdlib_tables`."""
    current: str = _run("import json, stdlib_tables.generate as g; print(json.dumps(g.current()))")
    assert json.loads(current) is True


def test_digest_covers_imports() -> None:
    """`INPUTS`, which the digest hashes, names every file of the checkout the generator imports."""
    imported: list[str] = cast("list[str]", json.loads(_run(_IMPORTED)))
    inputs: str = _run("import json, stdlib_tables.generate as g; print(json.dumps(g.INPUTS))")
    assert set(imported) <= set(cast("list[str]", json.loads(inputs)))
    assert LOADS_TABLES not in imported
