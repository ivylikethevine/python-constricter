# SPDX-License-Identifier: MIT
"""`fix-widen`: wider types than a value's own, each line marked, and replaced once its type is known."""

import json
import textwrap
from pathlib import Path
from typing import Final, TypeAlias

import pytest

from constricter import Checks, FixPolicy, Offence, annotation_coverage, check_source
from constricter.cli import command as cli
from constricter.fix.core import fixes
from constricter.noqa import lines
from constricter.rules import widened
from constricter.rules.checker import Coverage

_WIDEN: Final = Checks(fixes=FixPolicy(widen=frozenset({"untyped-parameters"})))
_ANY: Final = ("Any", False, frozenset({"untyped-parameters"}))
# Each offence's fix, whether it's a guess, and the mechanisms that decided it.
_Found: TypeAlias = dict[str, tuple[str | None, bool, frozenset[str]]]
_IMPORTED: Final = "from typing import Any\ndef f(reader):\n    a: Any = reader  # constricter: auto\n"
_MARK: Final = "# constricter: auto\n"
_MARKED: Final = [
    "    a: Any = reader  # constricter: auto\n",
    "    b: Any = reader.read()  # constricter: auto\n",
    "    c: Any = count  # constricter: auto\n",
    "    j: Any = only  # constricter: auto\n",
    "    reader2: Any = reader  # note  # constricter: auto\n",
    "        y: Any = other  # constricter: auto\n",
    "        w: Any = given  # constricter: auto\n",
]
_REPLACED: Final = [
    "    a: io.StringIO = reader\n",
    "    b: str = reader.read()  # note\n",
    "    c: Any = count  # constricter: auto\n",
    "    d: Any = Box()  # constricter: auto\n",
]
SOURCE: Final = """
from typing import Any


def f(reader, count, flag=False, *rest, key: str = "k", only, **more):
    a = reader
    b = reader.read()
    c = count
    d = flag
    e = reader.name
    g = reader.read(
        1,
    )
    h = key
    i = rest
    j = only
    k = j
    m = n = count
    reader2 = reader  # note
    reader2 = count.next()


class C:
    def m(self, other):
        x = self
        y = other

    @classmethod
    def make(cls, given):
        z = cls
        w = given


def bound_again(seen, kept):
    seen = list(seen)
    p = seen
    for kept in seen:
        q = kept


top = f
"""


def _found(source: str, checks: Checks = _WIDEN) -> _Found:
    found: list[Offence] = check_source(textwrap.dedent(source), checks=checks)
    return {o.name: (o.fix, o.unsafe, o.edit.kinds if o.edit else frozenset()) for o in found}


def test_what_comes_of_an_untyped_parameter_is_any() -> None:
    """A copy of it, or its method's call, on one line: certain, and its own kind.

    Not a parameter with a default (a checker types it by that), `*args` or `**kwargs`, `self` or
    `cls`, one bound again, an attribute of one, or a chained assignment's names.
    """
    found: _Found = _found(SOURCE)
    assert {name: fix for name, fix in found.items() if fix == _ANY} == dict.fromkeys(
        ["a", "b", "c", "j", "reader2", "y", "w"],
        _ANY,
    )
    assert {name for name, fix in found.items() if fix[0] is None} == {
        "d",
        "e",
        "g",
        "i",
        "k",
        "m",
        "n",
        "p",
        "q",
    }


def test_a_widening_is_off_unless_asked_for() -> None:
    """Without `fix-widen`, nothing; `fix-ignore` drops it as it does any kind."""
    assert _found(SOURCE, Checks())["a"] == (None, False, frozenset())
    ignoring: Checks = Checks(
        fixes=FixPolicy(ignore=frozenset({"untyped-parameters"}), widen=frozenset({"untyped-parameters"})),
    )
    assert _found(SOURCE, ignoring)["a"] == (None, False, frozenset())


def test_a_widening_needs_the_module_to_name_any() -> None:
    """`Any` is imported where it isn't, as `typing.Any` where the name's taken; else there's no fix."""
    source: str = "def f(reader):\n    a = reader\n"
    found: list[Offence] = check_source(source, checks=_WIDEN)
    assert "".join(fixes.apply(lines(source), found)) == _IMPORTED
    assert [fix[0] for fix in _found("Any = 1\n\n\ndef f(reader):\n    a = reader\n").values()] == [
        "typing.Any",
    ]
    assert [fix[0] for fix in _found("Any = typing = 1\n\n\ndef f(reader):\n    a = reader\n").values()] == [
        None,
    ]
    assert [o.fix for o in check_source("a = b\n", checks=_WIDEN._replace(all_scopes=True))] == [None]


def test_a_widenings_line_is_marked_and_its_edits_say_so() -> None:
    """The mark goes at the line's end, after a comment there; each report format's edits carry it."""
    source: str = textwrap.dedent(SOURCE)
    found: list[Offence] = check_source(source, checks=_WIDEN)
    fixed: list[str] = fixes.apply(lines(source), found)
    assert [line for line in fixed if line.endswith(_MARK)] == _MARKED
    first: Offence = next(o for o in found if o.edit and o.edit.marked)
    edits: tuple[fixes.Replacement, ...] = fixes.replacements(lines(source), first)
    assert [(edit.prefix, edit.deleted, edit.text) for edit in edits] == [
        ("    a", "", ": Any"),
        ("    a = reader", "", "  # constricter: auto"),
    ]


def test_a_marked_annotation_isnt_vague_and_is_counted_apart() -> None:
    """LVA005 passes over it, and `--coverage` counts it widened, not typed."""
    source: str = """
    from typing import Any

    def f(reader, count):
        a: Any = reader  # constricter: auto
        b: Any = reader  # hand-written
        c: int = count
        if count:
            a: Any = count  # constricter: auto
    """
    found: list[Offence] = check_source(textwrap.dedent(source))
    assert [(o.name, o.code, o.fix) for o in found] == [("b", "LVA005", None)]
    assert annotation_coverage(textwrap.dedent(source)) == Coverage(2, 3, 1)
    assert Coverage(2, 3, 1).percent == pytest.approx(200 / 3)


def test_a_marked_annotation_is_replaced_once_its_type_is_known() -> None:
    """Reported LVA005, with the value's own type in its place and the mark dropped; a guess as any is."""
    source: str = textwrap.dedent(
        """
        import io
        from typing import Any

        class Box:
            pass

        def f(reader: io.StringIO, count):
            a: Any = reader  # constricter: auto
            b: Any = reader.read()  # note  # constricter: auto
            c: Any = count  # constricter: auto
            d: Any = Box()  # constricter: auto
            e: Any  # constricter: auto
            g: (
                Any) = reader  # constricter: auto
            h = b
        """,
    )
    found: list[Offence] = check_source(source)
    assert {o.name: (o.code, o.fix, o.unsafe) for o in found} == {
        "a": ("LVA005", "io.StringIO", False),
        "b": ("LVA005", "str", False),
        "d": ("LVA005", "Box", True),
        "h": ("LVA001", "str", False),  # typed by what `b` is now
    }
    fixed: list[str] = fixes.apply(lines(source), [o for o in found if not o.unsafe])
    assert fixed[8:12] == _REPLACED
    ignoring: Checks = Checks(fixes=FixPolicy(ignore=frozenset({"copy"})))
    assert [o.name for o in check_source(source, checks=ignoring)] == ["b", "d", "h"]


def test_a_class_bodys_marked_annotation_is_left() -> None:
    """A class body is no scope `--fix` writes in: the annotation stays, unreported."""
    source: str = "class C:\n    limit: object = 3  # constricter: auto\n"
    assert check_source(source, checks=Checks(all_scopes=True)) == []


def test_marks_are_found_by_their_columns() -> None:
    """The mark and the space before it, in UTF-8 bytes; not a longer word, nor a line without one."""
    found: dict[int, tuple[int, int]] = widened.marks(
        [
            "é: Any = p  # constricter: auto\n",
            "x = 1  # constricter: automatic\n",
            "y = 2\n",
            'z = "# constricter: auto"\n',
            "w: Any = p  # constricter: auto  \r\n",
        ],
    )
    assert found == {1: (11, 32), 5: (10, 31)}


def test_the_command_takes_fix_widen_from_a_flag_and_pyproject(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """`--fix-widen KINDS` (`all`: every one), or `fix-widen` in `[tool.constricter]`, a list or one name."""
    monkeypatch.chdir(tmp_path)
    path: Path = tmp_path / "demo.py"
    source: str = "from typing import Any\n\n\ndef f(reader):\n    a = reader\n"
    fixed: str = source.replace("a = reader", "a: Any = reader  # constricter: auto")
    setting: str
    for setting in ('["untyped-parameters"]', '"all"'):
        _ = path.write_text(source, encoding="utf-8")
        _ = (tmp_path / "pyproject.toml").write_text(f"[tool.constricter]\nfix-widen = {setting}\n", "utf-8")
        assert cli.main(["--fix", "-q", "demo.py"]) == cli.EXIT_CLEAN
        assert path.read_text(encoding="utf-8") == fixed
    (tmp_path / "pyproject.toml").unlink()
    flag: str
    for flag in ("--fix-widen=untyped-parameters", "--fix-widen=all"):
        _ = path.write_text(source, encoding="utf-8")
        assert cli.main(["--fix", "-q", flag, "demo.py"]) == cli.EXIT_CLEAN
        assert path.read_text(encoding="utf-8") == fixed
    assert cli.main(["--coverage", "demo.py"]) == cli.EXIT_CLEAN
    assert capsys.readouterr().out.endswith("Total: 0/1 typed (0.0%), 1 widened in 1 file(s).\n")
    assert cli.main(["--coverage", "--format=json", "demo.py"]) == cli.EXIT_CLEAN
    assert json.loads(capsys.readouterr().out)["widened"] == 1


def test_an_unknown_widening_exits_2(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """A name that isn't a widening's id is an error, as a flag or in `[tool.constricter]`."""
    exit_info: pytest.ExceptionInfo[SystemExit]
    with pytest.raises(SystemExit) as exit_info:
        _ = cli.main(["--fix-widen=literal", "-q", "."])
    assert exit_info.value.code == cli.EXIT_ERROR
    assert capsys.readouterr().err.endswith("no wider type is called literal (see docs/FIXES.md)\n")
    monkeypatch.chdir(tmp_path)
    _ = (tmp_path / "pyproject.toml").write_text('[tool.constricter]\nfix-widen = ["nope"]\n', "utf-8")
    with pytest.raises(SystemExit) as exit_info:
        _ = cli.main([])
    assert exit_info.value.code == cli.EXIT_ERROR
    assert capsys.readouterr().err.endswith("[tool.constricter] has an invalid fix-widen = ['nope']\n")
