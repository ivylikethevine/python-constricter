# SPDX-License-Identifier: MIT
"""`--fix` for a module's type alias, declared `TypeAlias` where its value can only be a type."""

import ast
import textwrap
from typing import Final, TypeAlias

import pytest

from constricter import Checks, FixPolicy, Offence, check_source
from constricter.fix.core.known import Known
from constricter.fix.values import aliased
from constricter.fix.values.doubts import Facts

# Each offence's fix and whether it's a guess.
_Fixed: TypeAlias = dict[str, tuple[str | None, bool]]
_ALIAS: Final = "TypeAlias"
_TABLE: Final = "Table"
_ALL: Final = Checks(all_scopes=True)
_MODERN: Final = Checks(all_scopes=True, min_python=(3, 10))
_ADDED: Final = ("from typing import TypeAlias",)
_IMPORT: Final = "from typing import TypeAlias\n"
SOURCE: Final = """
import re
import typing as t
from collections.abc import Callable
from typing import Generic, Optional, TypeAlias, TypeVar, Union
from weakref import WeakValueDictionary

T = TypeVar("T")


class Box(Generic[T]):
    pass


class Plain:
    Inner = dict[str, int]


Either = Union[int, str]
Table = dict[str, int]
Handler = Callable[..., int]
Maybe = Optional[Plain]
Boxed = Box[int]
Cache = WeakValueDictionary[str, Plain]
Spelled = t.Union[int, str]
Number = int | None
Mixed = Plain | Box[int] | None
Flags = re.I | re.M
First = Second = dict[str, int]
Copied = Table
Listed = [Table]
Bare = Plain
Looked = lookup[1]
Called = make()[int]
Reached = make().kind[int]
Unknown = int | Missing
Twice = list[int]
Twice = list[str]
if t.TYPE_CHECKING:
    Checked = list[int]


def f() -> None:
    Local = dict[str, int]
"""


def _fixes(source: str, checks: Checks = _ALL) -> _Fixed:
    found: list[Offence] = check_source(textwrap.dedent(source), checks=checks)
    return {o.name: (o.fix, o.unsafe) for o in found}


def test_a_type_made_of_others_is_declared_an_alias() -> None:
    """A module body's subscript of a generic or a special form, or a union of types, is an alias.

    So is a copy of an alias. Not arithmetic on values (`re.I | re.M`), a bare class's alias, a
    subscript of anything else, a chained assignment, anything else made of an alias (`TypeAlias`
    isn't its value's type), a name bound twice, or a function's or a class body's.
    """
    fixes: _Fixed = _fixes(SOURCE)
    aliases: list[str] = [name for name, (fix, _) in fixes.items() if fix == _ALIAS]
    assert aliases == [
        "Either",
        "Table",
        "Handler",
        "Maybe",
        "Boxed",
        "Cache",
        "Spelled",
        "Number",
        "Mixed",
        "Copied",
        "Checked",
    ]
    assert not any(fixes[name][1] for name in aliases)  # the module imports `TypeAlias`
    untyped: list[str] = ["Inner", "Flags", "First", "Second", "Listed", "Bare", "Looked", "Called"]
    assert [fixes[name][0] for name in (*untyped, "Reached", "Unknown", "Twice", "Local")] == [None] * 12


@pytest.mark.parametrize(
    ("imports", "checks", "fix", "added", "unsafe"),
    [
        ("from typing import TypeAlias\n", _ALL, "TypeAlias", (), False),
        ("from typing_extensions import TypeAlias\n", _ALL, "TypeAlias", (), False),
        ("import typing_extensions\n", _ALL, "typing_extensions.TypeAlias", (), False),
        ("import typing\n", _ALL, "typing.TypeAlias", (), True),  # Python 3.9's has none
        ("import typing\n", _MODERN, "typing.TypeAlias", (), False),
        ("", _ALL, "TypeAlias", _ADDED, True),
        ("", _MODERN, "TypeAlias", _ADDED, False),
        ("", Checks(all_scopes=True, min_python=(3, 9)), "TypeAlias", _ADDED, True),
        ("TypeAlias = typing = 1\n", _MODERN, None, (), False),  # no name is free to import it by
    ],
)
def test_an_alias_is_certain_where_every_python_has_typealias(
    imports: str,
    checks: Checks,
    fix: str | None,
    added: tuple[str, ...],
    *,
    unsafe: bool,
) -> None:
    """`TypeAlias` is named as the module can, else imported from `typing`, which has it from 3.10.

    Certain where the module imports the name already, or `min-python` says every Python has it; a
    guess otherwise.
    """
    found: list[Offence] = check_source(f"{imports}Table = dict[str, int]\n", checks=checks)
    table: Offence = next(o for o in found if o.name == _TABLE)
    assert (table.fix, table.unsafe) == (fix, unsafe)
    assert (table.edit.imports if table.edit else ()) == added
    assert (table.edit.kinds if table.edit else None) == (None if fix is None else {aliased.KIND})


def test_a_declared_alias_is_fixed_as_one_just_declared_is() -> None:
    """A second pass finds what the first did: a copy of an alias is one, and nothing else is typed by it."""
    source: str = (
        "Table = dict[str, int]\nRows = Table\nListed = [Table]\n\ndef f() -> None:\n    local = Table\n"
    )
    again: str = source.replace("Table =", "Table: TypeAlias =").replace("Rows =", "Rows: TypeAlias =")
    first: _Fixed = _fixes(_IMPORT + source)
    assert first == {
        _TABLE: (_ALIAS, False),
        "Rows": (_ALIAS, False),
        "Listed": (None, False),
        "local": (None, False),
    }
    assert _fixes(_IMPORT + again) == {"Listed": (None, False), "local": (None, False)}
    spelled: str = "import typing\nTable: typing.TypeAlias = dict[str, int]\nRows = Table\n"
    assert _fixes(spelled, _MODERN) == {"Rows": ("typing.TypeAlias", False)}


def test_a_guessed_alias_can_be_trusted() -> None:
    """`unsafe-fix-select` makes the guess certain; `fix-ignore` drops the fix."""
    source: str = "Table = dict[str, int]\n"
    trusted: Checks = _ALL._replace(fixes=FixPolicy(unsafe_select=frozenset({aliased.KIND})))
    ignored: Checks = _ALL._replace(fixes=FixPolicy(ignore=frozenset({aliased.KIND})))
    assert _fixes(source) == {_TABLE: (_ALIAS, True)}
    assert _fixes(source, trusted) == {_TABLE: (_ALIAS, False)}
    assert _fixes(source, ignored) == {_TABLE: (None, False)}


@pytest.mark.parametrize(
    "source",
    [
        "dict = make()\nTable = dict[str, int]\n",  # not the builtin
        "int = make()\nNumber = int | None\n",
        "from typing import Union\ndef f(Union): ...\nEither = Union[int, str]\n",  # a value, somewhere
        "class Plain: ...\ndef f(Plain): ...\nMaybe = Plain | None\n",
        "from other import Thing\nMaybe = Thing | None\n",  # a class?
    ],
)
def test_a_name_that_may_be_a_value_makes_no_alias(source: str) -> None:
    """A builtin the module binds itself, or a name it binds as a value somewhere, may not be a type."""
    assert [fix for fix, _ in _fixes(_IMPORT + source).values() if fix == _ALIAS] == []


def test_a_module_not_read_for_its_names_declares_no_alias() -> None:
    """Without the module's imports (its plan) or its rebound names, nothing says the value is a type."""
    tree: ast.Module = ast.parse("Table = dict[str, int]\n")
    stmt: ast.stmt = tree.body[0]
    assert isinstance(stmt, ast.Assign)
    target: ast.expr = stmt.targets[0]
    assert isinstance(target, ast.Name)
    assert (
        aliased.declared(target, stmt.value, Known({}, frozenset(), {}, {}), Facts(), (frozenset(), None))
        is None
    )
