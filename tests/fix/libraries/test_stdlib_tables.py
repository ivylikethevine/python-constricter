# SPDX-License-Identifier: MIT
"""The standard-library tables are current: generated from the pinned stubs by this generator."""

import json
import subprocess  # imports the generator apart: it imports `constricter`'s modules without its `__init__`
import sys
from pathlib import Path
from typing import Final, TypeAlias, cast

ROOT: Final = Path(__file__).parents[3]
LOADS_TABLES: Final = "constricter/fix/libraries/stdlib.py"
_Read: TypeAlias = list[list[str | int]]  # each configuration (a platform, a minor version), as read
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
# `readings`, with a pool that maps in this process, one that can't start, and one core.
_READINGS: Final = """
import json
from pathlib import Path
import stdlib_tables.generate as generate
from stdlib_tables.stubs import CONFIGS


class Pool:
    started = []

    def __init__(self, workers):
        self.started.append(workers)

    def __enter__(self):
        return self

    def __exit__(self, *raised):
        return None

    def map(self, function, *each):
        return [("pool", *function(*arguments)) for arguments in zip(*each)]


class Refused(Pool):
    def __enter__(self):
        raise PermissionError


def reads(pool, cores):
    generate.ProcessPoolExecutor = pool
    generate.os.cpu_count = lambda: cores
    return generate.readings(Path("stubs"))


generate.read_config = lambda config, root: (config[0], config[1], root.name)
print(json.dumps([reads(Pool, 4), reads(Refused, 64), reads(Pool, 1), reads(Pool, None), CONFIGS]))
print(json.dumps(Pool.started))
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


def test_each_configuration_is_read_in_a_worker_where_it_can_be() -> None:
    """In `CONFIGS`' order, by as many workers as cores; in this process with one, or with none to start."""
    read: str
    started: str
    read, started = _run(_READINGS).splitlines()
    pooled: _Read
    serial: list[_Read]
    configs: _Read
    pooled, *serial, configs = cast("list[_Read]", json.loads(read))
    assert pooled == [["pool", *config, "stubs"] for config in configs]
    assert serial == [[[*config, "stubs"] for config in configs]] * 3
    assert json.loads(started) == [4, len(configs)]
