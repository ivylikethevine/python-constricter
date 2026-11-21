"""What a step asking the type checkers for hints holds, where no run has measured it.

By its checker (`HINTED_SIZES`): a base, bytes for each byte of the corpus's Python (each server's
again where each holds the whole program), and for each byte of what the corpus imports from its
environment (`imported`). Fitted to the peaks of the 121 hinted steps two runs asked afresh
(`mega-11-11-2026-1113`, `alt-fresh-11-20-2026-1800`; `scripts/scratch/hinted_sizes.py`), the whole
step's, its constricter's too: each held a median 0.9 to 1.0 of its fit, at most 1.8 to 2.7
(dask's, optuna's, pandas's). Each server's own measure (`protocol.SERVERS`), which caps a real
server's heap, held a fifth to a tenth of the bytes for the corpus's own files.
"""

import contextlib
import re
import sys
from functools import cache
from pathlib import Path
from typing import Final, NamedTuple

from constricter.cli import paths

_GIB: Final = 1 << 30


class Hinted(NamedTuple):
    """A checker's hinted step, unmeasured: a base, bytes for each byte of the corpus's and of its imports."""

    base: int
    own: int  # each server's again where each holds the whole program
    imported: int

    def held(self, servers: int, size: int, outside: int, *, whole: bool) -> int:
        """Estimate the step's bytes: `servers` servers, the corpus's Python `size`, its imports' `outside`.

        Returns:
          Them.

        """
        return self.base + self.own * size * (servers if whole else 1) + self.imported * outside


HINTED_SIZES: Final = {
    "basedpyright": Hinted(_GIB * 157 // 100, 225, 47),
    "ty": Hinted(_GIB * 63 // 100, 422, 23),
    "pyrefly": Hinted(_GIB * 39 // 100, 652, 23),
}
_IMPORT: Final = re.compile(r"^[ \t]*(?:from[ \t]+(\w+)|import[ \t]+(\w+))", re.MULTILINE)
_SOURCE: Final = ".py"
_STUB: Final = ".pyi"


@cache
def imported(root: Path, environment: Path | None) -> int:
    """Count the bytes of what a tree's files import from its environment: each package they name.

    Each top-level name an `import` or `from` names, but the tree's own and the standard library's,
    as its environment's `site-packages` has it (`Lib/site-packages` on Windows): a package's
    modules (each's stub where it has one beside it, else its source) and its `-stubs` package's, or
    a module. Once a run: a checker's servers load what the files import.

    Returns:
      Them; 0 for a tree with no environment.

    """
    if environment is None:
        return 0
    names: set[str] = set()
    path: Path
    for path in paths.python_files([root]):
        with contextlib.suppress(OSError):
            found: list[tuple[str, str]] = _IMPORT.findall(path.read_text("utf-8", "replace"))
            names.update(first or second for first, second in found)
    names -= {root.name, "__future__", *sys.stdlib_module_names}
    total: int = 0
    site: Path
    name: str
    for site in (*environment.glob("lib/python3*/site-packages"), environment / "Lib" / "site-packages"):
        for name in names:
            total += sum(_package(folder) for folder in (site / name, site / f"{name}-stubs"))
            total += sum(
                module.stat().st_size
                for module in (site / f"{name}{_SOURCE}", site / f"{name}{_STUB}")
                if module.is_file()
            )
    return total


def _package(folder: Path) -> int:  # a package's modules' bytes: each one's stub where it has one beside it
    return sum(
        each.stat().st_size
        for each in folder.rglob(f"*{_SOURCE}*")
        if each.suffix == _STUB or (each.suffix == _SOURCE and not each.with_suffix(_STUB).exists())
    )
