"""A run in stages: which steps each runs, what's left for later, and how stages join one folder."""

from pathlib import Path
from typing import TYPE_CHECKING, Final

import pytest

from tests.corpus import render, resume, stages
from tests.corpus.pipeline import Record
from tests.corpus.run_config import parse, read_command
from tests.corpus.stages import BUILT_IN, Stages

if TYPE_CHECKING:
    from collections.abc import Callable

_COMMIT: Final = "abc123def456"
_RUN: Final = "[run]\nlabel = 'staged'\n"
_TESTS: Final = "tests"  # a built-in stage
_STAGES: Final = "stages"  # a joined run's facts: the stages it was made in


@pytest.mark.parametrize(
    ("step", "stage"),
    [
        ("check", "fixes"),
        ("fix-unsafe", "fixes"),
        ("infer-ty", "fixes"),
        ("infer-union", "traced"),  # named outright, before `infer-*`
        ("traced", "traced"),
        ("tests-released", "tests"),
        ("tests-infer-union", "tests"),
        ("types", "tests"),
        ("timing", "timed"),
        ("profile", "timed"),
    ],
)
def test_each_step_is_in_one_built_in_stage(step: str, stage: str) -> None:
    """A step a stage names outright is that stage's; else the first whose pattern matches it."""
    assert stages.stage_of(step, BUILT_IN) == stage


def test_a_step_in_no_stage_is_an_error() -> None:
    """A run file's stages that leave a step out would never run it."""
    with pytest.raises(ValueError, match="'census' is in none"):
        _ = stages.stage_of("census", (("fixes", ("fix-*",)),))


def test_a_run_files_stages_regroup_the_steps() -> None:
    """In the file's order; with none, the built-in ones; a stage that isn't a list is an error."""
    assert parse({}).stages == BUILT_IN
    staged: Stages = parse({"stages": {"one": ["check", "fix-*"], "two": ["*"]}}).stages
    assert staged == (("one", ("check", "fix-*")), ("two", ("*",)))
    assert [stages.stage_of(step, staged) for step in ("fix-certain", "census")] == ["one", "two"]
    with pytest.raises(ValueError, match="isn't a list"):
        _ = parse({"stages": {"one": "check"}})


def test_a_stage_chooses_its_steps_and_must_be_the_runs() -> None:
    """No stage: every step."""
    assert stages.chosen(None, BUILT_IN)("timing")
    fixes: Callable[[str], bool] = stages.chosen("fixes", BUILT_IN)
    assert [fixes(step) for step in ("check", "traced", "timing")] == [True, False, False]
    assert stages.named(_TESTS, BUILT_IN) == _TESTS
    with pytest.raises(SystemExit, match="none of fixes, traced, tests, timed"):
        _ = stages.named("suites", BUILT_IN)


def test_a_step_whose_need_is_another_stages_waits_for_its_record() -> None:
    """And what needs it in turn; a need this execution makes runs first."""
    needs: dict[str, frozenset[str]] = {
        "tests-released": frozenset({"traced"}),
        "tests-fix-unsafe": frozenset({"fix-unsafe", "tests-released"}),
        "tests": frozenset({"tests-released", "tests-fix-unsafe"}),
    }
    names: list[str] = ["tests-released", "tests-fix-unsafe", "tests"]
    recorded: set[str] = {"fix-unsafe"}
    assert stages.runnable(names, needs, recorded.__contains__) == ([], names)
    recorded.add("traced")
    assert stages.runnable(names, needs, recorded.__contains__) == (names, [])


def test_the_stages_left_are_those_with_a_step_with_no_record() -> None:
    """In the table's order."""
    assert stages.left(BUILT_IN, ["timing", "tests-released", "tests"]) == ["tests", "timed"]
    assert stages.left(BUILT_IN, []) == []


def _facts(commit: str = _COMMIT, changes: str = "") -> Record:
    return {"commit": commit, "changes": changes, "label": "staged"}


def test_a_stage_joins_a_folder_of_its_commit_and_run_file(tmp_path: Path) -> None:
    """Noted with its commit; another commit, other changes or another run file are refused, unless told."""
    folder: Path = tmp_path / "run"
    folder.mkdir()
    file: Path = tmp_path / "run.toml"
    _ = file.write_text(_RUN, encoding="utf-8")
    _ = (folder / "run.toml").write_text(_RUN, encoding="utf-8")
    argv: list[str] = [str(file), "--resume", str(folder), "--stage", "tests"]
    earlier: Record = _facts() | {"stages": [f"fixes {_COMMIT}"]}
    assert resume.joined(read_command(argv), earlier, _facts(), "tests")["stages"] == [
        f"fixes {_COMMIT}",
        f"tests {_COMMIT}",
    ]
    with pytest.raises(SystemExit, match=f"ran on {_COMMIT}, this on {_COMMIT}\\+0123"):
        _ = resume.joined(read_command(argv), earlier, _facts(changes="0123"), "tests")
    joined: Record = resume.joined(
        read_command([*argv, "--join-anyway"]),
        earlier,
        _facts("fedcba987654"),
        "tests",
    )
    assert joined["stages"] == [f"fixes {_COMMIT}", "tests fedcba987654"]
    _ = file.write_text(f"{_RUN}jobs = 2\n", encoding="utf-8")
    with pytest.raises(SystemExit, match="isn't the run file"):
        _ = resume.joined(read_command(argv), earlier, _facts(), "tests")
    assert resume.joined(read_command(argv[:3]), earlier, _facts(), None)["stages"] == [f"fixes {_COMMIT}"]
    assert _STAGES not in resume.joined(read_command(argv[:1]), {}, _facts(), None)
    assert resume.joined(read_command([str(file), "--stage", "fixes"]), {}, _facts(), "fixes")["stages"] == [
        f"fixes {_COMMIT}",
    ]


def test_a_staged_runs_report_names_its_stages_and_those_left() -> None:
    """A run made in one sitting says nothing of them."""
    facts: Record = {"stages": [f"fixes {_COMMIT}", f"tests {_COMMIT}+0123"], "stages-left": ["timed"]}
    assert (
        render.staged(facts) == f" Made in stages: fixes on {_COMMIT}, tests on {_COMMIT}+0123; left: timed."
    )
    none: list[str] = []
    assert render.staged(facts | {"stages-left": none}).endswith("+0123.")
    assert not render.staged({})
