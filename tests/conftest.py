# SPDX-License-Identifier: MIT
"""Test collection and isolation.

The fuzz tests need hypothesmith, which the `test` group leaves out; and every test caches
installed modules' reads (`constricter.fix.installed`) in a directory of its own, never the user's.
"""

import importlib.util

import pytest

collect_ignore: list[str] = [] if importlib.util.find_spec("hypothesmith") else ["test_fuzz.py"]


@pytest.fixture(autouse=True)  # ruff: ignore[pytest-fixture-autouse]  # every test, or the user's cache
def _own_cache(tmp_path_factory: pytest.TempPathFactory, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("XDG_CACHE_HOME", str(tmp_path_factory.mktemp("cache")))
