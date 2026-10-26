"""The command's tests' fixtures."""

import gc
from collections.abc import Generator
from typing import Final

import pytest

_FREEZES: Final = hasattr(gc, "freeze")  # PyPy's collector has no freezing


@pytest.fixture
def restored() -> Generator[None]:
    """Leave the collector as each test found it, with nothing frozen."""
    was: bool = gc.isenabled()
    yield
    if _FREEZES:
        gc.unfreeze()
    if was:
        gc.enable()
    else:
        gc.disable()
