"""`--jobs` workers (constricter.cli.workers): how each starts."""

import concurrent.futures
import multiprocessing
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Final

import pytest

from constricter.cli import command, workers
from tests.cli import loaded

# Each starts `--jobs` workers of its own: one at a time, where the tests run at once (`pytest -n`).
JOBS: pytest.MarkDecorator = pytest.mark.xdist_group("jobs")
_SPAWN: Final = "spawn"  # the start method whose workers import what they need themselves


def _files(root: Path, count: int) -> list[Path]:
    found: list[Path] = []
    at: int
    for at in range(count):
        path: Path = root / f"m{at}.py"
        _ = path.write_text(f"x{at}: int = {at}\n", encoding="utf-8")
        found.append(path)
    return found


@JOBS
def test_a_worker_starts_with_constricter_imported(tmp_path: Path) -> None:
    """A worker a fork server or a fork starts has constricter imported already; a spawned one doesn't."""
    pool: workers.Workers
    with workers.Workers(_files(tmp_path, 2), 2) as pool:
        found: list[bool] = [each.submit(loaded.imported, command.__name__).result() for each in pool.pools]
    assert found == [multiprocessing.get_start_method() != _SPAWN] * 2


class _Context:
    """A start method's context, as `workers` asks it: how it starts processes, and what to preload."""

    def __init__(self, method: str) -> None:
        """Start processes by `method`."""
        self.method: str = method
        self.preloaded: list[list[str]] = []

    def get_start_method(self) -> str:
        """Say how it starts a process.

        Returns:
          The method.

        """
        return self.method

    def set_forkserver_preload(self, module_names: list[str]) -> None:
        """Note what a fork server is to import."""
        self.preloaded.append(module_names)


@pytest.mark.parametrize(
    ("method", "preloaded"),
    [("forkserver", [[command.__name__]]), ("fork", []), (_SPAWN, [])],
)
def test_only_a_fork_server_is_told_to_preload_constricter(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    method: str,
    preloaded: list[list[str]],
) -> None:
    """A fork server imports constricter for its workers; a fork has it, and a spawned worker imports it."""
    context: _Context = _Context(method)
    monkeypatch.setattr(multiprocessing, "get_context", lambda: context)
    monkeypatch.setattr(concurrent.futures, "ProcessPoolExecutor", ThreadPoolExecutor)
    with workers.Workers(_files(tmp_path, 1), 1):
        pass
    assert context.preloaded == preloaded
