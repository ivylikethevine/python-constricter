# SPDX-License-Identifier: MIT
"""A module checked again knowing only its functions' parameters anew starts from its last check."""

import ast
import textwrap
from typing import Final
from unittest.mock import Mock

import pytest

from constricter import Checks
from constricter.fix.core.known import Outside, Seeds
from constricter.fix.values import returned
from constricter.rules.checker import Checked, checked_tree

_SOURCE: Final = """
class Box:
    def __init__(self):
        self.items = []

    def put(self, x):
        self.items.append(x)
        return len(self.items)


def scale(value, factor):
    result = value * factor
    return result


def twice(value):
    doubled = scale(value, 2)
    return doubled


def plain() -> int:
    total = 1
    return total
"""
_SEEDS: Final[Seeds] = {"scale": {"value": ("int", frozenset[str]()), "factor": ("int", frozenset[str]())}}
_CHECKS: Final = Checks()
_STARTS: Final = 6  # the checks that start over, of `test_anything_else_new_starts_over`'s


def _fixes(found: Checked) -> dict[str, str | None]:
    return {o.name: o.fix for o in found.offences}


def test_a_second_check_starts_from_the_first(monkeypatch: pytest.MonkeyPatch) -> None:
    """With only parameters typed anew it checks those functions and what they reach, to the same end."""
    source: str = textwrap.dedent(_SOURCE)
    whole: Checked = checked_tree(ast.parse(source), _CHECKS, outside=Outside(parameters=_SEEDS))
    tree: ast.Module = ast.parse(source)
    first: Checked = checked_tree(tree, _CHECKS, outside=Outside())
    assert _fixes(first) != _fixes(whole)
    settled: Mock = Mock(wraps=returned.Table)  # a check from the start makes a table of its own
    monkeypatch.setattr(returned, "Table", settled)
    again: Checked = checked_tree(tree, _CHECKS, outside=Outside(parameters=_SEEDS))
    assert not settled.called
    assert again == whole
    # `doubled`: what the new type reaches.
    assert {name: _fixes(again)[name] for name in ("result", "doubled")} == {
        "result": "int",
        "doubled": "int",
    }


def test_anything_else_new_starts_over(monkeypatch: pytest.MonkeyPatch) -> None:
    """Other checks, other knowledge from outside, LVA012, or no check kept."""
    source: str = textwrap.dedent(_SOURCE)
    settled: Mock = Mock(wraps=returned.Table)  # a check from the start makes a table of its own
    monkeypatch.setattr(returned, "Table", settled)
    tree: ast.Module = ast.parse(source)
    _ = checked_tree(tree, _CHECKS)  # nothing from outside: nothing to compare
    _ = checked_tree(tree, _CHECKS, outside=Outside())
    _ = checked_tree(tree, _CHECKS, outside=Outside(calls={"other": "int"}))
    _ = checked_tree(tree, Checks(vague=1), outside=Outside(calls={"other": "int"}))
    final: Checks = Checks(final=True)
    _ = checked_tree(tree, final, outside=Outside())
    _ = checked_tree(tree, final, outside=Outside(parameters=_SEEDS))
    assert [settled.call_count] == [_STARTS]
