# SPDX-License-Identifier: MIT
"""`--fix` for what `with mock.patch(...) as name:` binds: the mock it makes."""

import textwrap
from typing import Final

from constricter import check_source

_SOURCE: Final = """
from unittest import mock
from unittest.mock import patch


class Thing:
    def run(self) -> int:
        return 1


def test(kwargs) -> None:
    with mock.patch("os.getcwd") as getcwd:
        pass
    with patch.object(Thing, "run", autospec=True) as run:
        pass
    with patch("os.getcwd", return_value="x") as configured:
        pass
    with patch("os.getcwd", new=3) as replaced:
        pass
    with patch("os.getcwd", 3) as placed:
        pass
    with patch.object(Thing, "run", new_callable=mock.Mock) as made:
        pass
    with patch("os.getcwd", **kwargs) as unpacked:
        pass
    with patch.dict("os.environ") as environ:
        pass
"""
_SHADOWED: Final = """
from unittest.mock import patch

MagicMock = 1


def test() -> None:
    with patch("x") as m:
        pass
"""


def test_a_patch_binds_the_mock_it_makes() -> None:
    """A `MagicMock`, or an `AsyncMock`: not where the call gives its replacement, or may."""
    assert {o.name: o.fix for o in check_source(textwrap.dedent(_SOURCE))} == {
        "getcwd": "mock.MagicMock | mock.AsyncMock",
        "run": "mock.MagicMock | mock.AsyncMock",
        "configured": "mock.MagicMock | mock.AsyncMock",
        **dict.fromkeys(("replaced", "placed", "made", "unpacked", "environ")),
    }


def test_a_module_that_cant_name_the_mocks_has_no_fix() -> None:
    """One binding `MagicMock` another way."""
    assert [o.fix for o in check_source(textwrap.dedent(_SHADOWED))] == [None]
