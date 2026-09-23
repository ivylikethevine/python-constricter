# SPDX-License-Identifier: MIT
"""`--fix` beyond `name: T = value`: declarations before a loop or an unpacking, and rewrites.

A loop's target (LVA002) and an unpacking's names (LVA001) are declared (`name: T`) on a line of
their own before the statement; an annotation LVA008 or LVA010 would narrow is rewritten, as a
guess.
"""

import ast
import json
import textwrap
from pathlib import Path
from typing import TypeAlias, cast

import pytest

from constricter import check_source, check_tree
from constricter.cli import command as cli
from constricter.fix import fixes
from constricter.fix.inference import looped
from constricter.fix.known import Inference, Known
from constricter.fix.targets import unpacked
from constricter.offences import COMMENT_TYPED_TARGET as COMMENT_TYPED
from constricter.offences import Edit, Fix, Offence

_NOTHING_KNOWN: Known = Known({}, frozenset(), {}, {})
# A notebook cell as written, and as read back (only its `source` is looked at).
_Cell: TypeAlias = dict[str, str | list[str] | dict[str, str]]
_Sources: TypeAlias = dict[str, list[str]]


def _fixed(source: str, *, unsafe: bool = False) -> str:
    """Apply every fix `check_source` offers (guesses too, if `unsafe`).

    Returns:
      The fixed source.

    """
    text: str = textwrap.dedent(source)
    offences: list[Offence] = [o for o in check_source(text) if o.fix and (unsafe or not o.unsafe)]
    return "".join(fixes.apply(text.splitlines(keepends=True), offences))


@pytest.mark.parametrize(
    ("iterable", "declared", "expected"),
    [
        ("range(3)", {}, "int"),
        ("range()", {}, None),  # no arguments: not really a `range`
        ("names", {"names": "list[str]"}, "str"),
        ("names", {"names": "frozenset[str]"}, "str"),
        ("names", {"names": "tuple[str, ...]"}, "str"),
        ("names", {"names": "tuple[str, int]"}, None),  # which one varies
        ("text", {"text": "str"}, "str"),
        ("blob", {"blob": "bytes"}, "int"),
        ("ages", {"ages": "dict[str, int]"}, "str"),
        ("ages.keys()", {"ages": "dict[str, int]"}, "str"),
        ("ages.values()", {"ages": "dict[str, int]"}, "int"),
        ("ages.items()", {"ages": "dict[str, int]"}, "tuple[str, int]"),
        ("things.items()", {"things": "list[int]"}, None),  # not a `dict`
        ("enumerate(names)", {"names": "list[str]"}, "tuple[int, str]"),
        ("zip(names, ages)", {"names": "list[str]", "ages": "dict[str, int]"}, "tuple[str, str]"),
        ("zip(names, other)", {"names": "list[str]"}, None),  # `other` isn't known
        ("sorted(names)", {"names": "set[str]"}, "str"),
        ("reversed(names)", {"names": "list[str]"}, "str"),
        ("unknown()", {}, None),
    ],
)
def test_a_loops_element_type(iterable: str, declared: dict[str, str], expected: str | None) -> None:
    """What each time round a loop over `iterable` binds."""
    found: Inference | None = looped(ast.parse(iterable, mode="eval").body, _NOTHING_KNOWN, declared)
    assert (None if found is None else found.annotation) == expected


@pytest.mark.parametrize(
    ("target", "annotation", "expected"),
    [
        ("a", "int", [("a", "int")]),
        ("a, b", "tuple[int, str]", [("a", "int"), ("b", "str")]),
        ("[a, b]", "tuple[int, ...]", [("a", "int"), ("b", "int")]),
        ("a, (b, c)", "tuple[int, tuple[str, bytes]]", [("a", "int"), ("b", "str"), ("c", "bytes")]),
        ("a, b", "tuple[int, str, bytes]", [("a", None), ("b", None)]),  # lengths differ
        ("a, *rest", "tuple[int, ...]", [("a", "int"), ("rest", None)]),
        ("a, b", "list[int]", [("a", None), ("b", None)]),
        ("a, b", None, [("a", None), ("b", None)]),
        ("a.x, b", "tuple[int, str]", [("b", "str")]),  # an attribute binds no local
    ],
)
def test_an_unpacking_splits_a_tuple_type(target: str, annotation: str | None, expected: object) -> None:
    """Each name gets its part of a tuple type; a shape that doesn't match gets nothing."""
    statement: ast.stmt = ast.parse(f"{target} = x").body[0]
    assert isinstance(statement, ast.Assign)
    node: ast.expr = statement.targets[0]
    assert [(name.id, part) for name, part in unpacked(node, annotation)] == expected


def test_loops_and_unpackings_are_declared_before_their_statement() -> None:
    """At the statement's indentation, each name on its own line, in order."""
    source: str = """
    def f(names: list[str], ages: dict[str, int], pair: tuple[int, str]) -> None:
        if names:
            for index, name in enumerate(names):
                pass
        first, second = pair
    """
    assert _fixed(source) == textwrap.dedent(
        """
    def f(names: list[str], ages: dict[str, int], pair: tuple[int, str]) -> None:
        if names:
            index: int
            name: str
            for index, name in enumerate(names):
                pass
        first: int
        second: str
        first, second = pair
    """,
    )


def test_a_loop_over_a_guess_is_declared_only_with_unsafe_fixes() -> None:
    """A loop over a value only guessed (`Box()` may be generic) offers a guess."""
    source: str = """
    class Box:
        def items(self) -> list[int]: ...

    def f() -> None:
        box = Box()
        things = box.items()
        for thing in things:
            pass
    """
    declaration: str = "    thing: int\n"
    assert declaration not in _fixed(source)
    assert declaration in _fixed(source, unsafe=True)


def test_a_declared_loop_target_types_what_follows_in_the_same_pass() -> None:
    """A later `x = target...` is inferred at once, so a second `--fix` pass has nothing left."""
    source: str = """
    def f(ages: dict[str, int]) -> None:
        for name, age in ages.items():
            label = name.upper()
    """
    fixed: str = "        label: str = name.upper()\n"
    assert fixed in _fixed(source)


def test_a_type_commented_loop_target_is_declared_from_its_comment(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """LVA003's fix declares the comment's type before the loop and drops the comment.

    A tuple target takes the comment's parts; a comment after it stays; a header over several lines,
    or a comment that isn't an annotation, gets no fix; a second pass has nothing left.
    """
    source: str = (
        "def f(items: list[int]) -> None:\n"
        "    for x in items:  # type: int\n"
        "        pass\n"
        "    for a, b in pairs():  # type: int, str  # noqa: E501\n"
        "        pass\n"
        "    for c in (\n"
        "        items\n"
        "    ):  # type: int\n"
        "        pass\n"
        "    for d in items:  # type: not an annotation(\n"
        "        pass\n"
    )
    fixed: dict[str, str | None] = {o.name: o.fix for o in check_source(source) if o.code == COMMENT_TYPED}
    assert fixed == {"x": "int", "a": "int", "b": "str", "c": None, "d": None}
    path: Path = tmp_path / "loops.py"
    _ = path.write_text(source, encoding="utf-8", newline="\n")
    assert cli.main(["--fix", "-q", "--level=suffocate", str(path)]) == cli.EXIT_FOUND
    assert path.read_text(encoding="utf-8").startswith(
        (
            "def f(items: list[int]) -> None:\n"
            "    x: int\n"
            "    for x in items:\n"
            "        pass\n"
            "    a: int\n"
            "    b: str\n"
            "    for a, b in pairs():  # noqa: E501\n"
        ),
    )
    _ = capsys.readouterr()
    assert cli.main(["--diff", "--level=suffocate", str(path)]) == cli.EXIT_CLEAN
    assert not capsys.readouterr().out  # nothing left to fix


def test_a_declaration_keeps_the_files_line_endings() -> None:
    """A file with Windows line endings gets its declarations with them too."""
    lines: list[str] = ["def f() -> None:\r\n", "    for i in range(3):\r\n", "        pass\r\n"]
    offence: Offence = Offence(2, 8, "i", edit=Fix("int", edit=Edit.DECLARE, span=(2, 4)))
    declaration: str = "    i: int\r\n"
    assert fixes.apply(lines, [offence])[1] == declaration


def test_a_notebook_declaration_lands_in_its_cell(tmp_path: Path) -> None:
    """In a notebook, the declaration goes before the statement in the statement's own cell."""
    cells: list[_Cell] = [
        {"cell_type": "code", "metadata": {}, "source": ["x: int = 1\n"]},
        {"cell_type": "code", "metadata": {}, "source": ["for i in range(3):\n", "    pass\n"]},
    ]
    path: Path = tmp_path / "demo.ipynb"
    _ = path.write_text(json.dumps({"cells": cells, "metadata": {}, "nbformat": 4}), encoding="utf-8")
    assert cli.main(["-q", "--fix", "--all-scopes", str(path)]) == cli.EXIT_CLEAN
    notebook: dict[str, list[_Sources]] = cast(
        "dict[str, list[_Sources]]",
        json.loads(path.read_text(encoding="utf-8")),
    )
    fixed: list[str] = notebook["cells"][1]["source"]
    assert fixed == ["i: int\n", "for i in range(3):\n", "    pass\n"]


def test_narrowing_rewrites_the_annotation_only_with_unsafe_fixes() -> None:
    """LVA008's narrowed type, or LVA010's union without its unused members, replaces the annotation."""
    source: str = """
    def f() -> None:
        total: float = 0
        total += 1
        label: int | str | None = 3
        label = 4
        both: float | bytes = 1
    """
    assert _fixed(source) == textwrap.dedent(source)
    assert _fixed(source, unsafe=True) == textwrap.dedent(
        """
    def f() -> None:
        total: int = 0
        total += 1
        label: int = 3
        label = 4
        both: int = 1
    """,
    )


def test_a_multi_line_annotation_isnt_rewritten() -> None:
    """An annotation that doesn't sit on its name's line is left to rewrite by hand."""
    source: str = "def f() -> None:\n    x: (\n        float\n    ) = 0\n"
    offences: list[Offence] = check_source(source)
    assert [(o.code, o.fix) for o in offences] == [("LVA008", None)]


def test_replacing_writes_over_the_annotations_columns() -> None:
    """An `Edit.REPLACE` writes its annotation between its span's columns."""
    offence: Offence = Offence(1, 0, "x", edit=Fix("int", edit=Edit.REPLACE, span=(3, 8)))
    assert fixes.apply(["x: float = 0\n"], [offence]) == ["x: int = 0\n"]


def test_a_chained_assignment_binds_only_its_names() -> None:
    """`x = o.y = 1` binds `x`, not `o.y` (an attribute isn't a local); a starred name is a name."""
    assert [o.name for o in check_source("def f(o: object) -> None:\n    x = o.y = 1\n")] == ["x"]
    source: str = "def f(values: list[int]) -> None:\n    x = a, *rest = values\n"
    assert [o.name for o in check_source(source)] == ["x", "a", "rest"]


def test_a_drop_left_unmade_where_it_cant_be() -> None:
    """A drop whose columns split a character, or a comment not on the header's line, is no edit."""
    split: Offence = Offence(1, 0, "x", edit=Fix("int", edit=Edit.DECLARE, span=(1, 0), drop=(1, 2)))
    assert fixes.dropped(["é = 1\n"], split) is None
    tree: ast.Module = ast.parse(
        "def f(y: list[int]) -> None:\n    for x in y:  # type: int\n        pass\n",
        type_comments=True,
    )
    lines: list[str] = [
        "def f(y: list[int]) -> None:",
        "    for x in y:",
        "        pass",
    ]  # no comment in them
    assert [(o.code, o.edit) for o in check_tree(tree, lines=lines)] == [(COMMENT_TYPED, None)]
