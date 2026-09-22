# SPDX-License-Identifier: MIT
"""Baseline files: the offences a codebase already has, so only new ones are reported.

An entry is a file, a code and a variable name, with how many times it occurs; line numbers aren't
kept, so a baseline survives code moving around. Paths are relative to the baseline file.
"""

import json
import os
from collections import Counter
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Final, TypeAlias, cast

from constricter import jsonc
from constricter.checker import Offence

VERSION: Final = 1
Entries: TypeAlias = dict[str, dict[str, int]]  # file -> "CODE name" -> count
_Json: TypeAlias = "str | int | float | bool | list[_Json] | dict[str, _Json] | None"


def key(path: Path, baseline: Path) -> str:
    """Make `path` relative to the baseline at `baseline`.

    Returns:
      `path` as the baseline records it: relative to it, with `/`.

    """
    return Path(os.path.relpath(path.resolve(), baseline.resolve().parent)).as_posix()


def _entry(offence: Offence) -> str:
    return f"{offence.code} {offence.name}"


def read(baseline: Path) -> Entries:
    """Return the entries in the baseline file `baseline`.

    Returns:
      Each file's count of each `CODE name` entry.

    Raises:
      ValueError: It can't be read, or isn't a baseline.

    """
    message: str
    document: _Json
    try:
        document = cast("_Json", jsonc.loads(baseline.read_bytes()))
    except (OSError, ValueError) as error:
        message = f"{baseline}: can't read the baseline ({error}); create it with --write-baseline"
        raise ValueError(message) from error
    files: dict[str, _Json]
    entries: Entries = {}
    match document:
        case {"version": 1, "offences": dict() as files}:
            path: str
            counts: _Json
            for path, counts in files.items():
                if not isinstance(counts, dict) or not all(jsonc.is_int(n) for n in counts.values()):
                    break
                entries[path] = {entry: n for entry, n in counts.items() if isinstance(n, int)}
            else:
                return entries
        case _:
            pass
    message = f"{baseline}: not a constricter baseline (version {VERSION})"
    raise ValueError(message)


def write(baseline: Path, found: Mapping[str, Sequence[Offence]]) -> int:
    """Write every offence in `found` (keyed as `key` makes them) to `baseline`.

    Returns:
      How many it wrote.

    """
    files: Entries = {
        path: dict(sorted(Counter(_entry(o) for o in offences).items()))
        for path, offences in sorted(found.items())
        if offences
    }
    _ = baseline.write_text(
        json.dumps({"version": VERSION, "offences": files}, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    return sum(len(offences) for offences in found.values())


def remaining(offences: Sequence[Offence], counts: Mapping[str, int]) -> tuple[list[Offence], int]:
    """Match one file's offences against the baseline's `counts` for it.

    Returns:
      The offences it doesn't cover, and how many it does.

    """
    left: Counter[str] = Counter(counts)
    kept: list[Offence] = []
    o: Offence
    for o in offences:
        if left[_entry(o)] > 0:
            left[_entry(o)] -= 1
        else:
            kept.append(o)
    return kept, len(offences) - len(kept)
