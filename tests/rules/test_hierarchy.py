# SPDX-License-Identifier: MIT
"""A project's own type hierarchy (`narrower`), over the built-in one, for LVA008-LVA010."""

import ast
import textwrap
from pathlib import Path

import pytest

from constricter import Checks, check_source
from constricter.cli import command as cli
from constricter.cli import config
from constricter.rules.flow import Hierarchy, Narrower, parse_narrower

SOURCE: str = textwrap.dedent(
    """
    from ids import UserId

    def make() -> UserId: ...

    def f() -> None:
        total: float = 0
        who: str = make()
        other: UserId = "x"
    """,
)


def _codes(narrower: tuple[Narrower, ...]) -> list[tuple[str, str]]:
    checks: Checks = Checks(narrower=narrower)
    return [(o.name, o.code) for o in check_source(SOURCE, checks=checks)]


def test_without_one_the_defaults_apply_and_imported_types_are_left_alone() -> None:
    """`int` fits `float`; `UserId`, imported, is never compared."""
    assert _codes(()) == [("total", "LVA008")]


def test_a_projects_entries_replace_the_defaults_per_type_and_vouch_for_its_types() -> None:
    """`int=` drops `int`'s default parent; `UserId=str` makes the imported type comparable."""
    assert _codes((("int", ()), ("UserId", ("str",)))) == [
        ("total", "LVA009"),
        ("who", "LVA008"),
        ("other", "LVA009"),
    ]


def test_an_entry_overrides_what_the_module_says() -> None:
    """A module class's own bases give way to the project's say."""
    tree: ast.Module = ast.parse("class Base: ...\nclass Child(Base): ...\n")
    assert Hierarchy.for_module(tree).fits("Child", "Base")
    assert not Hierarchy.for_module(tree, {"Child": frozenset()}).fits("Child", "Base")


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("", ()),
        ("B=A", (("B", ("A",)),)),
        ("B=A, C=A C=D", (("B", ("A",)), ("C", ("A", "D")))),
        ("int=", (("int", ()),)),
    ],
)
def test_the_plugins_spelling(text: str, expected: tuple[Narrower, ...]) -> None:
    """`narrower=wider` entries, comma- or space-separated; `name=` alone says it has none."""
    assert parse_narrower(text) == expected


def test_the_table_in_pyproject(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """`[tool.constricter.narrower]` sets the CLI's hierarchy."""
    _ = (tmp_path / "pyproject.toml").write_text(
        '[tool.constricter]\nlevel = "suffocate"\n\n[tool.constricter.narrower]\nint = []\n',
        encoding="utf-8",
    )
    _ = (tmp_path / "m.py").write_text("def f() -> None:\n    total: float = 0\n", encoding="utf-8")
    assert config.config_defaults(tmp_path)["narrower"] == {"int": []}
    monkeypatch.chdir(tmp_path)
    assert cli.main(["-q", "--select", "LVA008", "m.py"]) == cli.EXIT_CLEAN
    assert cli.main(["-q", "--select", "LVA009", "m.py"]) == cli.EXIT_FOUND
