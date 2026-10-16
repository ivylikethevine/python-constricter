# SPDX-License-Identifier: MIT
"""What the CLI sends its `--jobs` workers, pickled: frozen dataclasses, by their fields."""

import pickle
from typing import cast

import pytest

from constricter.empty import Empty
from constricter.fix.core.known import Outside, Returns
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


def test_an_empty_default_is_read_only_equal_to_an_empty_dict_and_pickles() -> None:
    """A record's empty mapping (`Empty`): it holds nothing, takes nothing, and pickles as another."""
    empty: Empty[str, int] = Empty()
    nothing: dict[str, int] = {}
    assert empty == nothing
    assert nothing == empty  # `dict` asks `Empty` back
    assert not empty
    assert not list(empty)
    assert repr(empty) == f"{Empty.__name__}()"
    with pytest.raises(KeyError):
        _ = empty["anything"]
    restored: Returns = cast("Returns", pickle.loads(pickle.dumps(Returns(), pickle.HIGHEST_PROTOCOL)))
    assert isinstance(restored.calls, Empty)
