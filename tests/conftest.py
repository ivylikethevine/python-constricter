# SPDX-License-Identifier: MIT
"""Test collection and isolation.

The fuzz tests need hypothesmith, which the `test` group leaves out; every test caches installed
modules' reads (`constricter.fix.index.installed`) in a directory of its own, never the user's; and
on a build mypyc compiled, a test marked `interpreted` is skipped: it patches a module whose callers,
compiled, call past the patch.
"""

import importlib.util
from typing import Final

import pytest

from constricter.rules import checker

collect_ignore: list[str] = [] if importlib.util.find_spec("hypothesmith") else ["test_fuzz.py"]
COMPILED: Final = not checker.__file__.endswith(".py")  # an extension module's `.so` or `.pyd`


def pytest_collection_modifyitems(items: list[pytest.Item]) -> None:
    """Skip the tests marked `interpreted` on a compiled build."""
    skip: pytest.MarkDecorator = pytest.mark.skip(reason="it patches a module mypyc compiled")
    item: pytest.Item
    for item in items:
        if COMPILED and item.get_closest_marker("interpreted"):
            item.add_marker(skip)


@pytest.fixture(autouse=True)  # ruff: ignore[pytest-fixture-autouse]  # every test, or the user's cache
def _own_cache(tmp_path_factory: pytest.TempPathFactory, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("XDG_CACHE_HOME", str(tmp_path_factory.mktemp("cache")))
