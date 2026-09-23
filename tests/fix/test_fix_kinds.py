# SPDX-License-Identifier: MIT
"""Fix levels: each `--fix` mechanism's id, `fix-select`/`fix-ignore`, and `unsafe-fix-select`."""

import textwrap
from pathlib import Path
from typing import Final, TypeAlias

import pytest

from constricter import FIX_KINDS, Checks, FixPolicy, Offence, check_source
from constricter.cli import command as cli

# Each offence's fix, the mechanisms that decided it, and whether it's a guess.
_Found: TypeAlias = tuple[str | None, frozenset[str], bool]
INT: Final = "int"
NARROWABLE: Final = "LVA008"
SOURCE: Final = """
class Point:
    x: int


def make() -> Point:
    return Point()


async def fetch() -> bytes:
    return b""


async def f(s: str, nums: list[int], p: Point, pairs: dict[str, int]) -> None:
    a = 1
    b = s.strip()
    c = Box()
    e = len(s)
    g = [1, 2]
    j = a
    k = nums[0]
    m = p.x
    o = make()
    r = a if s else 2
    t = a + 1
    u = [n for n in nums]
    v = sorted(nums)
    w = await fetch()
    x, y = 1, "z"
    for key, value in pairs.items():
        pass
"""


def _kinds(source: str, checks: Checks | None = None) -> dict[str, _Found]:
    found: list[Offence] = check_source(textwrap.dedent(source), checks=checks or Checks())
    return {o.name: (o.fix, o.edit.kinds if o.edit else frozenset(), o.unsafe) for o in found}


def test_each_mechanism_has_a_stable_id() -> None:
    """Each fix names every mechanism that decided it, parts included."""
    kinds: dict[str, frozenset[str]] = {name: found[1] for name, found in _kinds(SOURCE).items()}
    assert kinds == {
        "a": {"literal"},
        "b": {"method"},
        "c": {"constructor"},
        "e": {"builtin"},
        "g": {"container", "literal"},
        "j": {"copy"},
        "k": {"subscript"},
        "m": {"attribute"},
        "o": {"call"},
        "r": {"conditional", "copy", "literal"},
        "t": {"arithmetic", "copy", "literal"},
        "u": {"comprehension", "copy", "loop"},
        "v": {"builder", "copy", "loop"},
        "w": {"await"},
        "x": {"container", "literal", "unpack"},
        "y": {"container", "literal", "unpack"},
        "key": {"loop", "copy"},
        "value": {"loop", "copy"},
    }
    assert set().union(*kinds.values()) <= set(FIX_KINDS)


def test_fix_select_and_ignore_drop_fixes_not_offences() -> None:
    """A fix any unselected or ignored mechanism decided isn't offered; its offence is still reported."""
    ignored: dict[str, _Found] = _kinds(
        SOURCE,
        Checks(fixes=FixPolicy(ignore=frozenset({"literal"}))),
    )
    assert ignored["a"][0] is None
    assert ignored["g"][0] is None  # a container of literals
    assert ignored["j"][0] == INT  # a copy of `a`: its type is still known
    selected: dict[str, _Found] = _kinds(
        SOURCE,
        Checks(fixes=FixPolicy(select=frozenset({"literal", "copy"}))),
    )
    assert sorted(name for name, found in selected.items() if found[0]) == ["a", "j"]
    assert set(selected) == set(_kinds(SOURCE))


def test_unsafe_fix_select_trusts_a_guess_and_its_copies() -> None:
    """A trusted guessing mechanism makes its guess certain, and so a copy of it."""
    source: str = "def f() -> None:\n    c = Box()\n    d = c\n    n = [Box()]\n"
    assert {name: found[2] for name, found in _kinds(source).items()} == {"c": True, "d": True, "n": True}
    trusted: dict[str, _Found] = _kinds(
        source,
        Checks(fixes=FixPolicy(unsafe_select=frozenset({"constructor"}))),
    )
    assert {name: found[2] for name, found in trusted.items()} == {"c": False, "d": False, "n": False}
    # Trusting something else leaves them guesses.
    other: dict[str, _Found] = _kinds(
        source,
        Checks(fixes=FixPolicy(unsafe_select=frozenset({"narrow"}))),
    )
    assert all(found[2] for found in other.values())


def test_narrowing_is_its_own_mechanism() -> None:
    """LVA008's rewrite is `narrow`: a guess unless trusted, and never offered if ignored."""
    source: str = "def f() -> None:\n    total: float = 0\n    total = 1\n"

    def narrowed(policy: FixPolicy) -> Offence:
        return next(o for o in check_source(source, checks=Checks(fixes=policy)) if o.code == NARROWABLE)

    assert narrowed(FixPolicy()).unsafe
    assert narrowed(FixPolicy()).edit is not None
    assert not narrowed(FixPolicy(unsafe_select=frozenset({"narrow"}))).unsafe
    assert narrowed(FixPolicy(ignore=frozenset({"narrow"}))).edit is None


def test_the_command_takes_them_from_flags_and_pyproject(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """`--fix-select`, `--fix-ignore` and `--unsafe-fix-select`, or their `[tool.constricter]` keys."""
    monkeypatch.chdir(tmp_path)
    path: Path = tmp_path / "demo.py"
    source: str = "def f() -> None:\n    a = 1\n    b = Box()\n"
    _ = path.write_text(source, encoding="utf-8")
    assert cli.main(
        ["--fix", "-q", "--fix-ignore=literal", "--unsafe-fix-select=constructor", "demo.py"],
    ) == (cli.EXIT_FOUND)
    assert path.read_text(encoding="utf-8") == source.replace("b = Box()", "b: Box = Box()")
    _ = path.write_text(source, encoding="utf-8")
    _ = (tmp_path / "pyproject.toml").write_text(
        '[tool.constricter]\nfix-select = ["literal"]\nunsafe-fix-select = ["constructor"]\n',
        encoding="utf-8",
    )
    assert cli.main(["--fix", "-q", "demo.py"]) == cli.EXIT_FOUND
    assert path.read_text(encoding="utf-8") == source.replace("a = 1", "a: int = 1")
    _ = capsys.readouterr()


@pytest.mark.parametrize("flag", ["--fix-select=copy,nope", "--fix-ignore=nope", "--unsafe-fix-select=nope"])
def test_an_unknown_mechanism_exits_2(flag: str, capsys: pytest.CaptureFixture[str]) -> None:
    """A name that isn't a mechanism's id is an error."""
    exit_info: pytest.ExceptionInfo[SystemExit]
    with pytest.raises(SystemExit) as exit_info:
        _ = cli.main([flag, "-q", "."])
    assert exit_info.value.code == cli.EXIT_ERROR
    assert capsys.readouterr().err.endswith("no --fix mechanism is called nope (see docs/FIXES.md)\n")


def test_an_unknown_mechanism_in_pyproject_exits_2(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """`fix-select` naming no mechanism is a bad `[tool.constricter]` value."""
    monkeypatch.chdir(tmp_path)
    _ = (tmp_path / "pyproject.toml").write_text(
        '[tool.constricter]\nfix-ignore = ["nope"]\n',
        encoding="utf-8",
    )
    exit_info: pytest.ExceptionInfo[SystemExit]
    with pytest.raises(SystemExit) as exit_info:
        _ = cli.main([])
    assert exit_info.value.code == cli.EXIT_ERROR
    assert capsys.readouterr().err.endswith("[tool.constricter] has an invalid fix-ignore = ['nope']\n")
