"""The corpus runs' witness: a value held to the annotation a fix gave its name (`witness.holds`)."""

import collections
import collections.abc
import importlib
import io
import json
import tempfile
import types
import typing
from collections.abc import Callable
from pathlib import Path
from typing import Final, TypeAlias, TypeVar, cast
from unittest import mock

import pytest

from constricter import trace
from tests.corpus import corpus_guesses

_Holds: TypeAlias = Callable[[object, object], bool | None]
_Patched: TypeAlias = Callable[[object, str], bool]
_Case: TypeAlias = tuple[object, object, bool | None]  # a value, an annotation, and whether it holds
_T = TypeVar("_T")
_Judged: TypeAlias = list[str | int | list[int] | list[str]]  # a binding as a witness process writes it
_HELD: Final[tuple[_Case, ...]] = (
    ([1, 2], list[int], True),
    ([1, "a", 3], list[int], False),
    ([], list[int], True),
    ([1, None], list[int | None], True),
    ([1.0, 2], list[float], True),
    ([1, "a"], collections.abc.Sequence[int], False),
    ([1, "a"], list, True),
    ({1, "a"}, set[int], False),
    (frozenset({1}), frozenset[int], True),
    (collections.deque([1, "a"]), collections.deque[int], False),
    ({"a": 1, "b": "c"}, dict[str, int], False),
    ({"a": 1, 2: 3}, dict[str, int], False),
    ({"a": [1, "b"]}, dict[str, list[int]], False),
    ({"a": "b"}, collections.abc.Mapping[str, int], False),
    ({"a": 1}, dict[str, typing.Any], True),
    ((1, "a"), tuple[int, str], True),
    ((1, 2), tuple[int, str], False),
    ((1,), tuple[int, str], False),
    ((1, 2, "a"), tuple[int, ...], False),
    ((1, 2), tuple[int, ...], True),
    ((), tuple[()], True),
    ((1,), tuple[()], False),
    ((1, "a"), tuple, True),
    # What can't be told of an element can't be told of its container, unless another differs.
    ([mock.MagicMock()], list[int], None),
    (cast("object", mock.sentinel.dist_info), str, None),  # `mock.sentinel`'s, a test's stand-in as a mock is
    (["a"], types.GenericAlias(list, (_T,)), None),  # `list[_T]`, written where no function binds `_T`
    ([mock.MagicMock(), "a"], list[int], False),
    # A container whose arguments aren't its elements' types is held to its class alone.
    (collections.Counter("ab"), collections.Counter[str], True),
    (collections.Counter("ab"), dict[str, int], True),
)


class _Rows(list[object]):  # ruff: ignore[subclass-builtin]  # a subclass of the builtin is the case
    """A list of a class of its own: reading it may run that class's code."""


@pytest.fixture(name="holds", scope="module")
def _holds() -> _Holds:
    """Import the witness, which makes itself `constricter.trace`'s recorder, and undo that.

    Returns:
      Its `holds`.

    """
    with mock.patch.dict(trace.__dict__):
        return typing.cast(
            "_Holds",
            importlib.import_module("tests.corpus.witness.constricter_witness").holds,
        )


@pytest.mark.parametrize(("value", "hint", "held"), _HELD)
def test_a_builtin_container_is_held_to_its_arguments(
    holds: _Holds,
    value: object,
    hint: object,
    *,
    held: bool | None,
) -> None:
    """Its elements, its keys and values, a tuple's parts; a class alone where that isn't what they are."""
    assert holds(value, hint) is held


class _Framed:  # pylint: disable=too-few-public-methods
    """A base the classes these tests make share, which names their type."""


def _made() -> type[_Framed]:
    class Frame(_Framed):  # pylint: disable=too-few-public-methods
        """A class this function defines anew at each call."""

    return Frame


def test_a_class_made_again_is_the_annotations(holds: _Holds) -> None:
    """By a function or a module imported anew, by its module and qualified name; another name is another."""
    first: type[_Framed] = _made()
    assert holds(_made()(), first) is True
    assert holds(type("Frame", (), {"__module__": "pkg.core"})(), first) is False
    named: dict[str, str] = {"__module__": _Framed.__module__, "__qualname__": _Framed.__qualname__}
    assert holds(type("_Framed", (), named)(), _Framed) is True


def test_a_test_modules_class_says_nothing_of_the_annotation(holds: _Holds) -> None:
    """A test's stand-in, passed where the package's class is declared, is neither fit nor differing."""
    module: str
    held: bool | None
    for module, held in (("pkg.tests.test_core", None), ("test_core", None), ("pkg.core", False)):
        stand_in: type[_Framed] = type("FakeProcess", (_Framed,), {"__module__": module})
        assert holds(stand_in(), int) is held
    assert holds(types.SimpleNamespace(), int) is None


def test_a_packages_pytest_plugin_is_a_test_module(holds: _Holds) -> None:
    """Its classes stand in for the package's (`pdm.pytest.Distribution`); pytest's own `_pytest` are real."""
    stand_in: type[_Framed] = type("Distribution", (_Framed,), {"__module__": "pdm.pytest"})
    assert holds(stand_in(), int) is None
    real: type[_Framed] = type("TestReport", (_Framed,), {"__module__": "_pytest.reports"})
    assert holds(real(), int) is False


def test_typings_file_classes_take_what_reads_and_writes(holds: _Holds) -> None:
    """Nothing is an instance of `typing.IO`: a temporary file's wrapper is one all the same."""
    wrapped: typing.IO[str]
    with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8") as wrapped:
        assert holds(wrapped, typing.IO[str]) is True
        assert holds(wrapped, typing.TextIO) is True
    assert holds(io.BytesIO(), typing.BinaryIO) is True
    assert holds("text", typing.IO[str]) is False


def test_an_in_memory_file_stands_in_for_a_file(holds: _Holds) -> None:
    """A `StringIO` where `open`'s `TextIOWrapper` is declared is a test's stand-in, not a differing value."""
    assert holds(io.StringIO(), io.TextIOWrapper) is None
    assert holds(io.BytesIO(), io.BufferedReader) is None
    assert holds(io.StringIO(), str) is False
    assert holds(io.StringIO(), io.StringIO) is True


def test_an_annotation_naming_a_tests_class_outside_the_tests_is_patched() -> None:
    """A module's name a test patched (`humanize.datetime = MockDateTime`): a test's own names its classes."""
    with mock.patch.dict(trace.__dict__):
        patched: _Patched = typing.cast(
            "_Patched",
            importlib.import_module("tests.corpus.witness.constricter_witness").patched,
        )
    stand_in: type[_Framed] = type("MockDateTime", (_Framed,), {"__module__": "humanize_tests.tests"})
    assert patched(stand_in, "django.contrib.humanize")
    assert not patched(stand_in, "humanize_tests.test_more")
    assert not patched(int, "django.contrib.humanize")
    assert not patched("datetime", "django.contrib.humanize")


def test_only_a_builtin_containers_elements_are_read(holds: _Holds) -> None:
    """A subclass's own code may run as it's read: it's held to its class, and a long list by its first."""
    assert holds(_Rows([1, "a"]), list[int]) is True
    assert holds([*range(100), "a"], list[int]) is True
    assert holds({*range(200), "a"}, set[int]) is False


def test_a_verdict_tells_of_the_values_that_differed(tmp_path: Path) -> None:
    """The first ones its processes wrote, each once: the value's class and the annotation's."""
    with mock.patch.dict(trace.__dict__):
        kind: Callable[[_Rows | float], str] = typing.cast(
            "Callable[[_Rows | float], str]",
            importlib.import_module("tests.corpus.witness.constricter_witness").kind_of,
        )
    assert kind(_Rows()) == f"{__name__}:_Rows"
    differed: str = f"{kind(1)} against <class 'str'>"
    written: Path = tmp_path / ".venv" / "corpus-suite-verdicts"
    written.mkdir(parents=True)
    processes: list[list[_Judged]] = [
        [["a.py", 1, "x", [3, 1, 0], [differed]], ["a.py", 2, "y", [1, 0, 0], []]],
        [["a.py", 1, "x", [0, 2, 0], [differed, f"{kind(1.0)} against <class 'str'>"]]],
    ]
    pid: int
    judged: list[_Judged]
    for pid, judged in enumerate(processes):
        _ = (written / f"{pid}.json").write_text(json.dumps(judged), encoding="utf-8")
    verdicts: corpus_guesses.Verdicts = corpus_guesses.verdicts(tmp_path)
    assert verdicts["a.py"][1]["x"] == corpus_guesses.Verdict(
        3,
        3,
        0,
        (differed, "builtins:float against <class 'str'>"),
    )
    assert verdicts["a.py"][2]["y"] == corpus_guesses.Verdict(1, 0, 0)
