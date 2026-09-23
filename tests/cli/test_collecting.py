# SPDX-License-Identifier: MIT
"""The garbage collector, run by hand while the command runs."""

import gc
from collections.abc import Generator

import pytest

from constricter.cli import collecting

_FREEZES: bool = hasattr(gc, "freeze")  # PyPy's collector has no freezing


@pytest.fixture
def restored() -> Generator[None]:
    """Leave the collector as each test found it."""
    was: bool = gc.isenabled()
    yield
    if was:
        gc.enable()
    else:
        gc.disable()


@pytest.mark.usefixtures("restored")
def test_by_hand_turns_collection_off_and_back_on() -> None:
    """Off for the run, on again afterwards, with nothing left frozen."""
    gc.enable()
    with collecting.by_hand():
        assert not gc.isenabled()
        collecting.indexed()
        assert not _FREEZES or gc.get_freeze_count() > 0
        collecting.sweep()
    assert gc.isenabled()
    assert not _FREEZES or gc.get_freeze_count() == 0


@pytest.mark.usefixtures("restored")
def test_by_hand_leaves_collection_off_if_it_was() -> None:
    """A caller that had turned the collector off finds it still off."""
    gc.disable()
    with collecting.by_hand():
        assert not gc.isenabled()
    assert not gc.isenabled()
