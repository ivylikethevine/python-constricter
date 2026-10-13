# SPDX-License-Identifier: MIT
"""What a recorder keeps by class."""

from typing import Final

from constricter import recording

_KEPT: list[str] = ["int", "int", recording.UNKNOWN, recording.UNKNOWN, "Odd", "Odd"]
_ASKED: list[str] = ["int", "float", "float", "Odd", "Odd"]
# A class that can't be hashed: its class of classes has no `__hash__`.
_ODD: Final = type("Unhashed", (type,), {"__hash__": None})("Odd", (), {})


def test_what_a_class_says_is_kept_but_for_one_that_cant_be() -> None:
    """Not a class no annotation names yet, which its module may bind later; nor one with no hash."""
    asked: list[str] = []

    @recording.by_class
    def kept(cls: type) -> str:
        asked.append(cls.__name__)
        return recording.UNKNOWN if cls is float else cls.__name__

    assert [kept(int), kept(int), kept(float), kept(float), kept(_ODD), kept(_ODD)] == _KEPT
    assert asked == _ASKED
