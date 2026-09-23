# SPDX-License-Identifier: MIT
"""`--fix` that adds an import: a standard-library class, `open`'s file object, LVA012's `Final`."""

import ast
import json
import textwrap
from pathlib import Path
from typing import Final, TypeAlias, cast

import pytest

from constricter import Checks, Offence, check_source
from constricter.cli import command as cli
from constricter.fix import fixes, imports
from constricter.fix.known import ImportPlan
from constricter.offences import Edit, Fix, FixPolicy

_Json: TypeAlias = dict[str, "_Json"] | list["_Json"] | str | int | float | bool | None
_Object: TypeAlias = dict[str, _Json]
_Sources: TypeAlias = dict[str, list[str]]
_DEFAULT: Final = Checks()
_FINAL: Final = Checks(final=True)
_Cell: TypeAlias = dict[str, str | list[str] | dict[str, str]]


def _fixed(source: str, checks: Checks = _DEFAULT, *, unsafe: bool = False) -> str:
    """Apply every fix `check_source` offers (guesses too, if `unsafe`).

    Returns:
      The fixed source.

    """
    text: str = textwrap.dedent(source).lstrip("\n")
    offences: list[Offence] = [
        o for o in check_source(text, checks=checks) if o.fix and (unsafe or not o.unsafe)
    ]
    return "".join(fixes.apply(text.splitlines(keepends=True), offences))


def _twice(source: str, checks: Checks = _DEFAULT) -> str:
    """Fix `source`, then check a second pass offers nothing more.

    Returns:
      The once-fixed source.

    """
    once: str = _fixed(source, checks)
    assert _fixed(once, checks) == once
    return once


def _plan(source: str) -> ImportPlan:
    """Read a module's import plan.

    Returns:
      It.

    """
    return imports.plan(ast.parse(textwrap.dedent(source)))


@pytest.mark.parametrize(
    ("source", "qualified", "spelled", "added"),
    [
        ("from io import BytesIO\n", "io.BytesIO", "BytesIO", {}),
        ("import io as i\n", "io.BytesIO", "i.BytesIO", {}),
        ("", "io.BytesIO", "BytesIO", {"BytesIO": "from io import BytesIO"}),
        ("BytesIO = 1\n", "io.BytesIO", "io.BytesIO", {"io": "import io"}),
        ("BytesIO = 1\nio = 2\n", "io.BytesIO", None, {}),
        ("Path = 1\n", "pathlib.Path", "pathlib.Path", {"pathlib": "import pathlib"}),
        ("", "os.path.PathLike", "PathLike", {"PathLike": "from os.path import PathLike"}),
        ("PathLike = 1\n", "os.path.PathLike", None, {}),  # a dotted module is never imported whole
        (
            "",
            "files.open",
            "files.open",
            {"files": "import files"},
        ),  # `from files import open`: shadows the builtin
        (  # only a type checker's import: `BytesIO` isn't bound when the module runs
            "from typing import TYPE_CHECKING\nif TYPE_CHECKING:\n  from io import BytesIO\n",
            "io.BytesIO",
            "io.BytesIO",
            {"io": "import io"},
        ),
        ("try:\n  from io import BytesIO\nexcept ImportError:\n  pass\n", "io.BytesIO", "BytesIO", {}),
        ("if True:\n  import io\n", "io.BytesIO", "io.BytesIO", {}),
        ("from . import io\n", "io.BytesIO", "BytesIO", {"BytesIO": "from io import BytesIO"}),
    ],
)
def test_a_plan_spells_a_class_as_the_module_can(
    source: str,
    qualified: str,
    spelled: str | None,
    added: dict[str, str],
) -> None:
    """An existing import is reused; else a free name is imported; never over a name already taken."""
    plan: ImportPlan = _plan(source)
    assert plan.spell(qualified) == spelled
    assert plan.added == added


def test_a_plan_adds_each_import_once() -> None:
    """A name the plan imported is free to it again, but not for another import."""
    plan: ImportPlan = _plan("")
    assert [plan.spell(name) for name in ("io.BytesIO", "io.BytesIO", "other.BytesIO")] == [
        "BytesIO",
        "BytesIO",
        "other.BytesIO",
    ]
    assert plan.added == {"BytesIO": "from io import BytesIO", "other": "import other"}


@pytest.mark.parametrize(
    ("source", "after"),
    [
        ("x = 1\n", 0),
        ('"""Doc."""\nx = 1\n', 1),
        ('"""Doc."""\nfrom __future__ import annotations\n\nimport os\nx = 1\n', 4),
        ("import os\nif TYPE_CHECKING:\n  import io\n", 1),
        ("x = 1\n'''not a docstring'''\n", 0),
    ],
)
def test_an_import_goes_after_the_modules_leading_imports(source: str, after: int) -> None:
    """After the docstring and the imports the module starts with, before anything else."""
    assert _plan(source).after == after


@pytest.mark.parametrize(
    ("mode", "annotation"),
    [
        ("", "TextIOWrapper"),
        (", 'r'", "TextIOWrapper"),
        (", 'wt'", "TextIOWrapper"),
        (", 'a+'", "TextIOWrapper"),
        (", 'rb'", "BufferedReader"),
        (", 'wb'", "BufferedWriter"),
        (", 'xb'", "BufferedWriter"),
        (", 'ab'", "BufferedWriter"),
        (", 'r+b'", "BufferedRandom"),
        (", mode='rb'", "BufferedReader"),
        (", encoding='utf-8'", "TextIOWrapper"),
        (", mode", None),  # not a literal
        (", 'rb', 0", None),  # unbuffered: an `io.FileIO`
        (", 'rb', buffering=0", None),
        (", opener=o", None),
        (", **options", None),
        (", 'rw'", None),  # not a mode `open` takes
        (", 'rbb'", None),
        (", 'bt'", None),
        (", 'rtb'", None),
        (", 'q'", None),
    ],
)
def test_open_is_typed_by_its_literal_mode(mode: str, annotation: str | None) -> None:
    """`open(path, mode)` gives a text wrapper, or a buffered reader, writer, or both."""
    source: str = f"def f(p: str, mode: str, o, options) -> None:\n  x = open(p{mode})\n"
    assert [o.fix for o in check_source(source)] == [annotation]


def test_open_is_only_the_builtin_or_io_open() -> None:
    """`io.open` is the builtin; a module's own `open` (or a call on anything else) isn't."""
    assert _twice("import io\ndef f(p: str) -> None:\n  x = io.open(p, 'rb')\n").splitlines()[2:] == [
        "  x: io.BufferedReader = io.open(p, 'rb')",
    ]
    assert [o.fix for o in check_source("def open(p): ...\ndef f(p: str) -> None:\n  x = open(p)\n")] == [
        None,
    ]
    assert [o.fix for o in check_source("def f(p: str) -> None:\n  x = p.open()\n")] == [None]


def test_a_copy_of_an_opened_file_is_typed_and_certain() -> None:
    """What `open` gives is no guess: a copy of it is certain too, and needs the same import."""
    assert [
        (o.name, o.fix, o.unsafe) for o in check_source("def f() -> None:\n  a = open('x')\n  b = a\n")
    ] == [
        ("a", "TextIOWrapper", False),
        ("b", "TextIOWrapper", False),
    ]


def test_with_open_declares_the_file_before_the_statement() -> None:
    """`with open(...) as f` declares `f` first, and the import is added after the module's own."""
    source: str = """
    \"\"\"Doc.\"\"\"
    from __future__ import annotations

    import os


    def f(p: str) -> None:
        with open(p, "rb") as data, open(p) as text, lock as (held, _), lock:
            copy = text
    """
    assert _twice(source) == textwrap.dedent(
        """\
        \"\"\"Doc.\"\"\"
        from __future__ import annotations

        import os
        from io import BufferedReader
        from io import TextIOWrapper


        def f(p: str) -> None:
            data: BufferedReader
            text: TextIOWrapper
            with open(p, "rb") as data, open(p) as text, lock as (held, _), lock:
                copy: TextIOWrapper = text
        """,
    )


def test_an_async_with_isnt_declared() -> None:
    """`open`'s file object isn't an asynchronous context manager: nothing to type there."""
    source: str = "async def f(p: str) -> None:\n  async with open(p) as g:\n    pass\n"
    assert [(o.name, o.fix) for o in check_source(source)] == [("g", None)]


def test_an_import_goes_after_a_shebang_and_coding_line() -> None:
    """A module without a docstring or imports gets its import at the top, below those."""
    source: str = "#!/usr/bin/env python\n# -*- coding: utf-8 -*-\ndef f() -> None:\n  x = open('x')\n"
    assert _twice(source).splitlines()[:3] == [
        "#!/usr/bin/env python",
        "# -*- coding: utf-8 -*-",
        "from io import TextIOWrapper",
    ]


def test_an_import_keeps_the_files_line_endings() -> None:
    """A file with Windows line endings gets its import with them too."""
    lines: list[str] = ["import os\r\n", "x = 1\r\n"]
    offence: Offence = Offence(2, 0, "x", edit=Fix("BytesIO", imports=("from io import BytesIO",), after=1))
    assert fixes.apply(lines, [offence])[:3] == [
        "import os\r\n",
        "from io import BytesIO\r\n",
        "x: BytesIO = 1\r\n",
    ]


def test_an_import_already_there_isnt_added_again() -> None:
    """Two fixes needing one import add it once, and never where the file has it as a line already."""
    lines: list[str] = ["from io import BytesIO\n", "x = 1\n", "y = 2\n"]
    fix: Fix = Fix("BytesIO", imports=("from io import BytesIO",), after=0)
    offences: list[Offence] = [Offence(2, 0, "x", edit=fix), Offence(3, 0, "y", edit=fix)]
    assert "".join(fixes.apply(lines, offences)).count("import") == 1
    assert "".join(fixes.apply(lines[1:], [*offences[:1], Offence(2, 0, "y", edit=fix)])).count("import") == 1


def test_a_notebook_fix_that_needs_an_import_isnt_applied(tmp_path: Path) -> None:
    """A notebook's cells have no import block to add to: that fix is left for a person."""
    cells: list[_Cell] = [
        {"cell_type": "code", "metadata": {}, "source": ["x = open('x')\n", "y = 1\n"]},
    ]
    path: Path = tmp_path / "demo.ipynb"
    _ = path.write_text(json.dumps({"cells": cells, "metadata": {}, "nbformat": 4}), encoding="utf-8")
    assert cli.main(["-q", "--fix", "--all-scopes", str(path)]) == cli.EXIT_FOUND
    notebook: dict[str, list[_Sources]] = cast(
        "dict[str, list[_Sources]]",
        json.loads(path.read_text(encoding="utf-8")),
    )
    assert notebook["cells"][0]["source"] == ["x = open('x')\n", "y: int = 1\n"]


def test_sarif_and_rdjson_carry_the_import(capsys: pytest.CaptureFixture[str], tmp_path: Path) -> None:
    """A fix that adds an import is two edits in each report: the annotation, and the import."""
    path: Path = tmp_path / "opened.py"
    _ = path.write_text(
        "import os\n\n\ndef f() -> None:\n    x = open('x')\n",
        encoding="utf-8",
        newline="\n",
    )
    expected: list[_Json] = [": TextIOWrapper", "from io import TextIOWrapper\n"]
    assert cli.main(["--format=rdjson", "--level=suffocate", str(path)]) == cli.EXIT_FOUND
    rdjson: _Json = cast("_Json", json.loads(capsys.readouterr().out))
    assert _texts(rdjson, "diagnostics", 0, "suggestions") == expected
    assert cli.main(["--format=sarif", "--level=suffocate", str(path)]) == cli.EXIT_FOUND
    sarif: _Json = cast("_Json", json.loads(capsys.readouterr().out))
    changes: _Json = _at(sarif, "runs", 0, "results", 0, "fixes", 0, "artifactChanges", 0, "replacements")
    assert [_at(change, "insertedContent", "text") for change in cast("list[_Json]", changes)] == expected


def _at(document: _Json, *path: str | int) -> _Json:
    """Follow `path` (keys and indices) into a JSON document.

    Returns:
      What's there.

    """
    step: str | int
    for step in path:
        document = (
            cast("list[_Json]", document)[step] if isinstance(step, int) else cast("_Object", document)[step]
        )
    return document


def _texts(document: _Json, *path: str | int) -> list[_Json]:
    """Read the `text` of each object in the list at `path`.

    Returns:
      Them.

    """
    return [_at(found, "text") for found in cast("list[_Json]", _at(document, *path))]


@pytest.mark.parametrize(
    ("source", "expected"),
    [
        (
            "def f() -> None:\n  x: int = 1\n",
            "from typing import Final\ndef f() -> None:\n  x: Final[int] = 1\n",
        ),
        (
            'def f() -> None:\n  x: "int" = 1\n',
            'from typing import Final\ndef f() -> None:\n  x: Final["int"] = 1\n',
        ),
        ("def f() -> None:\n  x = 1\n", "from typing import Final\ndef f() -> None:\n  x: Final[int] = 1\n"),
        ("def f(q) -> None:\n  x = q()\n", "from typing import Final\ndef f(q) -> None:\n  x: Final = q()\n"),
        (
            "import typing as t\ndef f() -> None:\n  x = open('x')\n",
            (
                "import typing as t\nfrom io import TextIOWrapper\n"
                "def f() -> None:\n  x: t.Final[TextIOWrapper] = open('x')\n"
            ),
        ),
        (
            "from typing import Final as F\ndef f() -> None:\n  Final = 1\n",
            "from typing import Final as F\ndef f() -> None:\n  Final: F[int] = 1\n",
        ),
        (
            "def f() -> None:\n  Final = 1\n  typing = 2\n",
            "def f() -> None:\n  Final: int = 1\n  typing: int = 2\n",  # nothing can name it: LVA001's fixes
        ),
        ("def f() -> None:\n  x: (\n    int\n  ) = 1\n", "def f() -> None:\n  x: (\n    int\n  ) = 1\n"),
    ],
)
def test_can_be_final_offers_final(source: str, expected: str) -> None:
    """LVA012 wraps the annotation, or LVA001's, in `Final`; a bare `Final` if there's none."""
    assert _twice(source, _FINAL) == expected


def test_a_final_over_a_guess_is_a_guess() -> None:
    """LVA012 with LVA001's guessed type is as unsafe as it, and LVA001 offers nothing then."""
    offences: list[Offence] = check_source("def f() -> None:\n  x = Box(1)\n", checks=_FINAL)
    assert [(o.code, o.fix, o.unsafe) for o in offences] == [
        ("LVA001", None, False),
        ("LVA012", "Final[Box]", True),
    ]


def test_final_isnt_offered_where_not_selected() -> None:
    """Without the `final` kind, LVA001 keeps its fix; without LVA001's, `Final` is bare."""
    source: str = "def f() -> None:\n  x = 1\n"
    offences: list[Offence] = check_source(
        source,
        checks=Checks(final=True, fixes=FixPolicy(ignore=frozenset({"final"}))),
    )
    assert [(o.code, o.fix) for o in offences] == [("LVA001", "int"), ("LVA012", None)]
    offences = check_source(source, checks=Checks(final=True, fixes=FixPolicy(ignore=frozenset({"literal"}))))
    assert [(o.code, o.fix) for o in offences] == [("LVA001", None), ("LVA012", "Final")]  # no type to wrap
    assert [
        o.edit.edit for o in check_source("def f() -> None:\n  x: int = 1\n", checks=_FINAL) if o.edit
    ] == [
        Edit.REPLACE,
    ]


def test_a_guessed_argument_doesnt_make_opens_type_a_guess() -> None:
    """`open(path)`'s type is its mode's, `getLogger(name)`'s a `Logger`, `len(x)`'s `int`, whatever `x` is.

    Found on the standard library's `http.server`: `f = None`, then `f = open(path, "rb")` with a
    guessed `path`, was typed only once `path` was, on a second pass.
    """
    source: str = """
    import logging
    def f() -> None:
        path = Box()
        a = open(path, "rb")
        b = logging.getLogger(path)
        c = len(path)
        d = None
        d = open(path)
    """
    offences: list[Offence] = check_source(textwrap.dedent(source))
    assert [(o.name, o.fix, o.unsafe) for o in offences] == [
        ("path", "Box", True),
        ("a", "BufferedReader", False),
        ("b", "logging.Logger", False),
        ("c", "int", False),
        ("d", "TextIOWrapper | None", False),
    ]
