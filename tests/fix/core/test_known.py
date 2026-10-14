# SPDX-License-Identifier: MIT
"""What the CLI sends its `--jobs` workers, pickled: frozen dataclasses, by their fields."""

import pickle

import pytest

from constricter.fix.core.known import Outside
from constricter.fix.index.modules import Module


@pytest.mark.parametrize(
    "frozen",
    [
        Outside(calls={"f": "int"}, type_vars=frozenset({"T"})),
        Module(name="m", returns={"f": "int"}, names={"g": ("other", "g")}),
    ],
)
def test_a_frozen_dataclass_pickles_by_its_fields(frozen: Outside | Module) -> None:
    """Each field as it was, set past the class's refusal: a build mypyc compiled has no other way."""
    assert pickle.loads(pickle.dumps(frozen, pickle.HIGHEST_PROTOCOL)) == frozen
