# SPDX-License-Identifier: MIT
"""The kept trees' budget: sized by the machine's memory."""

import os
from pathlib import Path
from typing import Final

import pytest

from constricter.rules import parsed

_GB: Final = 1 << 30
_PAGE: Final = 4096


def _sysconf(pages: int) -> object:
    def sysconf(name: str) -> int:
        return {"SC_PHYS_PAGES": pages, "SC_PAGE_SIZE": _PAGE}[name]

    return sysconf


@pytest.mark.parametrize(
    ("available", "expected"),
    [
        (None, 40 << 20),  # not known: what every run kept before
        (2 * _GB, 40 << 20),  # a small machine keeps as much
        (4 * _GB, 40 << 20),
        (8 * _GB, 8 * _GB // 4 // 26),
        (64 * _GB, 64 * _GB // 4 // 26),
    ],
)
def test_the_budget_is_a_quarter_of_the_memory_and_a_gigabyte_at_least(
    available: int | None,
    expected: int,
) -> None:
    """A tree takes 26 bytes for each byte of source: a quarter of the memory holds that many bytes of it."""
    assert parsed.sized(available) == expected


def test_memory_is_the_machines_or_its_control_groups_limit(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """The lower of the two; the machine's where the group has no limit, or there's no group."""
    limit: Path = tmp_path / "memory.max"
    monkeypatch.setattr(os, "sysconf", _sysconf(16 * _GB // _PAGE), raising=False)
    monkeypatch.setattr(parsed, "_GROUP_LIMIT", limit)
    assert parsed.memory() == 16 * _GB  # no control group
    _ = limit.write_text("max\n", encoding="ascii")
    assert parsed.memory() == 16 * _GB
    _ = limit.write_text(f"{2 * _GB}\n", encoding="ascii")
    assert parsed.memory() == 2 * _GB
    _ = limit.write_text(f"{64 * _GB}\n", encoding="ascii")
    assert parsed.memory() == 16 * _GB


def test_memory_isnt_known_where_the_system_doesnt_say(monkeypatch: pytest.MonkeyPatch) -> None:
    """Windows has no `sysconf`: the budget is then its least."""
    monkeypatch.delattr(os, "sysconf", raising=False)
    assert parsed.memory() is None
    assert parsed.sized(parsed.memory()) == 40 << 20
