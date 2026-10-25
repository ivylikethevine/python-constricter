"""`--infer-with`'s memory: checkers asked in turn, and a Node server's heap capped at its share."""

import sys
from collections.abc import Callable, Mapping
from pathlib import Path
from typing import TYPE_CHECKING, Final, TypeAlias

import pytest

from constricter.cli.lsp import connection, guard, hints, protocol, remembered
from constricter.cli.options import Options
from tests.cli.sources import FAKE_SERVER

if TYPE_CHECKING:
    from constricter.fix.core.known import Hints

_Task: TypeAlias = Callable[[], connection.Found]  # one server's work (`Checker.tasks`)
_Tasks: TypeAlias = Callable[[hints.Checker, Mapping[Path, str]], list[_Task]]
_CHECKER: Final = "basedpyright"  # on Node: its heap capped
_TY: Final = "ty"
_CAPPED: Final = "--trace-warnings --max-old-space-size=3686"  # nine tenths of 4 GB, after the user's own


def _command(_checker: str) -> list[str]:
    """Start the fake server, whatever the checker.

    Returns:
      Its command.

    """
    return [sys.executable, str(FAKE_SERVER)]


def _fake(monkeypatch: pytest.MonkeyPatch) -> None:
    """Make every checker the fake server, with plenty of memory whatever the machine has."""
    monkeypatch.setattr(hints, "command", _command)
    monkeypatch.setattr(hints, "available_memory", lambda: 64 << 30)
    monkeypatch.setattr(connection, "_TIMEOUT", 5.0)
    monkeypatch.setattr(guard, "GRACE", 0.5)
    monkeypatch.setattr(connection, "_POLL", 0.05)


def test_checkers_asked_in_turn_run_one_at_a_time(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """`in_turn`: one checker's servers at a time, each stopped once it's answered; the same hints."""
    _fake(monkeypatch)
    started: list[list[str]] = []  # the checkers with servers running as each is asked
    tasks: _Tasks = hints.Checker.tasks

    def watched(checker: hints.Checker, files: Mapping[Path, str]) -> list[_Task]:
        started.append([each.name for each in session.checkers if each.servers])
        return tasks(checker, files)

    monkeypatch.setattr(hints.Checker, "tasks", watched)
    path: Path = tmp_path / "both.py"
    session: hints.Session
    with hints.Session(["ty", _CHECKER], tmp_path, how=hints.Asking(kept=False, in_turn=True)) as session:
        found: tuple[Hints, ...] = session.hints({path: "x = 1  # hint: int\n"})[path]
        again: tuple[Hints, ...] = session.hints({path: "x = 1  # hint: int\n"})[path]
        assert not [checker.name for checker in session.checkers if checker.servers]
    assert started == [["ty"], [_CHECKER], ["ty"], [_CHECKER]]
    assert [(each.checker, each.types) for each in found] == [
        ("ty", {(1, 1): "int"}),
        (_CHECKER, {(1, 1): "int"}),
    ]
    assert again == found


def test_infer_in_turn_asks_one_checker_at_a_time() -> None:
    """`--infer-in-turn`: off by default."""
    assert not Options.parse([]).infer_in_turn
    assert Options.parse(["--infer-in-turn"]).infer_in_turn


def test_a_node_servers_heap_is_capped_at_its_share_of_the_memory(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """Nine tenths of each server's share, never under a server's own; no other checker's is capped."""
    _fake(monkeypatch)
    monkeypatch.setenv("NODE_OPTIONS", "--trace-warnings")
    path: Path = tmp_path / "heavy.py"
    session: hints.Session
    with hints.Session([_CHECKER, _TY], tmp_path, memory=4 << 30) as session:
        found: tuple[Hints, ...] = session.hints({path: "x = 1  # hint: int\n# heap 3000\n"})[path]
        pyright: hints.Checker = session.checkers[0]
        assert pyright.environment is not None
        assert pyright.environment["NODE_OPTIONS"] == _CAPPED
        assert session.checkers[1].environment is None
    assert [each.types for each in found] == [{(1, 1): "int"}, {(1, 1): "int"}]
    small: hints.Checker = hints.Checker(_CHECKER, tmp_path, 1, 256 << 20)
    small.share(1)
    assert small.environment is not None
    assert small.environment["NODE_OPTIONS"].endswith("--max-old-space-size=600")


def test_a_file_past_a_capped_servers_heap_has_no_hints(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """The server's restarted and asked about each file alone: the rest keep their hints.

    Not remembered as a hang: a larger share may fit it.
    """
    _fake(monkeypatch)
    heavy: Path = tmp_path / "heavy.py"
    files: dict[Path, str] = {
        tmp_path / "fine.py": "x = 1  # hint: int\n",
        heavy: "y = 1  # hint: int\n# heap 5000\n",
    }
    session: hints.Session
    with hints.Session([_CHECKER], tmp_path, memory=1 << 30) as session:
        found: dict[Path, tuple[Hints, ...]] = session.hints(files)
        assert session.abandoned == [(_CHECKER, heavy)]
    assert {path: each.types for path, (each,) in found.items()} == {
        tmp_path / "fine.py": {(1, 1): "int"},
        heavy: {},
    }
    assert not remembered.hung(_CHECKER, session.checkers[0].command, files[heavy], heavy)
    roomy: hints.Session
    with hints.Session([_CHECKER], tmp_path, memory=8 << 30) as roomy:
        assert roomy.hints({heavy: files[heavy]})[heavy][0].types == {(1, 1): "int"}


def test_a_file_an_earlier_run_hung_on_has_no_hints_from_the_start(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """Left out of every server's work as it's asked, it's still answered for: with no hints."""
    _fake(monkeypatch)
    hung: Path = tmp_path / "hung.py"
    files: dict[Path, str] = {tmp_path / "fine.py": "x = 1  # hint: int\n", hung: "y = 1  # hint: int\n"}

    def remembered_hung(_checker: str, _command: list[str], _text: str, path: Path | None = None) -> bool:
        return path == hung

    monkeypatch.setattr(remembered, "hung", remembered_hung)
    session: hints.Session
    with hints.Session([_CHECKER], tmp_path, how=hints.Asking(kept=False)) as session:
        found: dict[Path, tuple[Hints, ...]] = session.hints(files)
        assert session.abandoned == [(_CHECKER, hung)]
    assert {path: each.types for path, (each,) in found.items()} == {
        tmp_path / "fine.py": {(1, 1): "int"},
        hung: {},
    }


def test_a_turn_with_no_file_to_ask_about_stops_no_server(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """Its checker started none: there's none to stop."""
    _fake(monkeypatch)
    session: hints.Session
    with hints.Session([_TY, _CHECKER], tmp_path, how=hints.Asking(kept=False, in_turn=True)) as session:
        assert session.hints({}) == {}
        assert not [checker.name for checker in session.checkers if checker.servers]


def _failing(monkeypatch: pytest.MonkeyPatch, *failures: protocol.HintError) -> None:
    """Have the servers' asks raise `failures`, one each, before they ask as they do."""
    ask: Callable[[connection.Connection, Mapping[Path, str]], connection.Asked] = connection.Connection.ask
    left: list[protocol.HintError] = list(failures)

    def failing(server: connection.Connection, files: Mapping[Path, str]) -> connection.Asked:
        if left:
            raise left.pop(0)
        return ask(server, files)

    monkeypatch.setattr(connection.Connection, "ask", failing)


def test_a_capped_server_gone_before_its_next_batch_is_restarted(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """Its batch is asked about again, alone, on the server started in its place."""
    _fake(monkeypatch)
    _failing(monkeypatch, protocol.ExitedError("basedpyright-langserver exited: broken pipe"))
    path: Path = tmp_path / "one.py"
    session: hints.Session
    with hints.Session([_CHECKER], tmp_path) as session:
        assert session.hints({path: "x = 1  # hint: int\n"})[path][0].types == {(1, 1): "int"}
        assert not session.abandoned


def test_a_failure_asking_alone_past_a_restart_stops_the_run(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """An exit of a server whose heap isn't capped, at once or after a hang: no restart gets past it."""
    _fake(monkeypatch)
    failures: tuple[protocol.HintError, ...]
    for failures in (
        (protocol.ExitedError("ty exited"),),
        (protocol.HungError("ty said nothing"), protocol.ExitedError("ty exited")),
    ):
        _failing(monkeypatch, *failures)
        session: hints.Session
        with (
            hints.Session([_TY], tmp_path) as session,
            pytest.raises(protocol.ExitedError, match="ty exited"),
        ):
            _ = session.hints({tmp_path / "one.py": "x = 1  # hint: int\n"})
