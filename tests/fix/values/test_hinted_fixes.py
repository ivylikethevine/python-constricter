# SPDX-License-Identifier: MIT
"""`--infer-with`: which of a type checker's hints become fixes, spelled how, and what they feed."""

import ast
import textwrap
from typing import Final, TypeAlias

import pytest

from constricter import Checks, Offence, check_source
from constricter.fix.core import fixes
from constricter.fix.core.known import Guarded, Hints, Known, Offered, Outside
from constricter.fix.values.hinted import type_alias
from constricter.offences import Edit, FixPolicy

_CHECKER: Final = "basedpyright"
_DEFAULT: Final = Checks()
_Fixes: TypeAlias = list[tuple[str, str | None, bool]]


def _checked(
    source: str,
    hinted: dict[str, str],
    checks: Checks = _DEFAULT,
    checking: tuple[str, ...] = (),
) -> list[Offence]:
    """Check `source`, the checker hinting each name's every binding as `hinted` says.

    `checking`: the classes the index says it imports for type checking alone.

    Returns:
      The offences.

    """
    text: str = textwrap.dedent(source)
    types: dict[tuple[int, int], str] = {
        (node.lineno, node.end_col_offset or 0): hinted[node.id]
        for node in ast.walk(ast.parse(text))
        if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Store) and node.id in hinted
    }
    own: dict[str, Guarded] = {name: Guarded(("shapes", name), None) for name in checking}
    return check_source(text, checks=checks, outside=Outside(hints=(Hints(_CHECKER, types),), checking=own))


def _fixes(source: str, hinted: dict[str, str]) -> _Fixes:
    """Check `source` with hints.

    Returns:
      Each offence's name, fix and whether it's a guess.

    """
    return [(o.name, o.fix, o.unsafe) for o in _checked(source, hinted)]


@pytest.mark.parametrize(
    ("hint", "fix"),
    [
        ("int", "int"),
        ("Literal[1]", "int"),
        ("Literal[-1, 2]", "int"),
        ("Literal['a', b'b']", "str | bytes"),
        ("Literal[True] | None", "bool | None"),
        ("None | Literal[1] | int", "int | None"),
        ("Literal[None, 1]", "int | None"),
        ("tuple[Literal[1], Literal['a']]", "tuple[int, str]"),
        ("list[LiteralString]", "list[str]"),
        ("Callable[[int], str]", "Callable[[int], str]"),
        ("Callable[..., None]", "Callable[..., None]"),
        ("Literal[Color.RED]", "Color"),
        ("os.stat_result", "os.stat_result"),
        ("stat_result", "os.stat_result"),
        ("Iterator[int]", "Iterator[int]"),
        ("Any", None),  # vague
        ("list[Unknown]", None),  # a name the file can't use
        ("OrderedDict[Any, Any]", None),
        ("None", None),  # says nothing
        ('Module("os")', None),  # not an annotation
        ("(x: int) -> str", None),  # a signature, not valid Python
        ("Self@C", None),
        ("Literal[f()]", None),
        ("list[Literal[f()]]", None),
        ("tuple[Literal[f()], int]", None),
        ("Literal['a'] | Literal[f()]", None),
        ('list["int"]', None),  # a string: its meaning isn't checked
        ("dict[str, dict[str, list[int]]]", None),  # as deep as LVA006 reports
        ("tuple[int, int, int, int, int]", None),  # as long as LVA011 reports
        ("_T", None),  # a type variable, or anything private
        ("dict[<class 'int'>, <class 'Color'>]", "dict[type[int], type[Color]]"),  # ty's class objects
        ("list[int | str]", None),  # a mixed container's elements: read as one member or another
        ("dict[str, list[int | None]]", None),
        ("Callable[[int], Literal['a']]", "Callable[[int], str]"),
        ("Box[Literal['a']]", None),  # a class's argument may be bound to the literals
        ("Box[int]", "Box[int]"),
        ("<class '<unknown>'>", None),
        ("type[_]", None),  # `_` is gettext's, or a throwaway: never the checker's class
        ("dict[int, <class 'A'> | ... omitted 11 union elements]", None),  # cut short
        ("type[Generic]", None),  # a special form itself, not a type
        ("Annotated", None),
        ("Annotated[int, Color]", "Annotated[int, Color]"),
        ("(str & ~AlwaysFalsy) | None", "str | None"),  # ty's: narrowed by a truth test
        ("int & ~AlwaysTruthy", "int"),
        ("Color & Sized", None),  # any other intersection isn't an annotation
        ("~AlwaysFalsy", None),
        ("tuple[str, *tuple[str, ...]]", None),  # Python 3.11's syntax, and no `Unpack` to write it with
    ],
)
def test_a_hint_is_widened_spelled_or_dropped(hint: str, fix: str | None) -> None:
    """A `Literal` is its values' types; what isn't a usable annotation is no fix."""
    source: str = """
    import os
    from enum import Enum
    from gettext import gettext as _
    from collections.abc import Callable, Iterator
    from typing import Annotated, Generic


    class Color(Enum):
        RED = 1


    class Box: ...


    def f(q) -> None:
        x = q.make()
        if x is None:
            return
    """
    assert _fixes(source, {"x": hint}) == [("x", fix, fix is not None)]


def test_a_union_is_a_fix_only_for_a_name_its_function_tests() -> None:
    """Untested, the name is used as one member of the union, which declared would be an error."""
    untested: str = "def f(q) -> None:\n    x = q.find()\n    x.run()\n"
    assert _fixes(untested, {"x": "int | None"}) == [("x", None, False)]
    assert _fixes(untested, {"x": "int | str"}) == [("x", None, False)]
    read: str = "def f(q) -> None:\n    x = q.find()\n    if x.ready and len(x) > 1:\n        x.run()\n"
    assert _fixes(read, {"x": "int | None"}) == [("x", None, False)]
    test: str
    for test in ("x is not None", "not x", "q and isinstance(x, int)", "x"):
        tested: str = f"def f(q) -> None:\n    x = q.find()\n    if {test}:\n        x.run()\n"
        assert _fixes(tested, {"x": "int | None"}) == [("x", "int | None", True)]
    assert [o.fix for o in _checked("x = find()\n", {"x": "int | None"}, Checks(all_scopes=True))] == [
        "int | None",
    ]


def test_a_name_returned_as_self_has_no_fix() -> None:
    """The checker hints the class, which a signature saying `Self` doesn't take."""
    source: str = """
    from typing import Self


    class Box:
        def copy(self, q) -> Self:
            new = q.make()
            other = q.make()
            return new

        def plain(self, q) -> "Box":
            new = q.make()
            return new
    """
    assert _fixes(source, {"new": "Box", "other": "Box"}) == [
        ("new", None, False),
        ("other", "Box", True),
        ("new", "Box", True),
    ]


def test_a_name_bound_again_to_another_or_no_known_type_has_no_fix() -> None:
    """A hint is the first value's type: a later value the checker wasn't asked about may be any."""
    source: str = "def f(q) -> None:\n    x = q.make()\n    x = q.other()\n"
    first: Hints = Hints(_CHECKER, {(2, 5): "int"})
    assert [o.fix for o in check_source(source, checks=_DEFAULT, outside=Outside(hints=(first,)))] == [None]
    assert _fixes(source, {"x": "int"}) == [("x", "int", True)]
    wider: str = "def f(q) -> None:\n    x = q.make()\n    x = 1.5\n"
    assert _fixes(wider, {"x": "int"}) == [("x", None, False)]


@pytest.mark.parametrize(
    ("hint", "fix", "shallow"),
    [
        ("tuple[str, *tuple[str, ...]]", "tuple[str, Unpack[tuple[str, ...]]]", False),
        ("tuple[*tuple[int, ...]]", "tuple[Unpack[tuple[int, ...]]]", False),
        ("tuple[str, *Pair]", "tuple[str, Unpack[Pair]]", True),
        ("Callable[[int, *tuple[str, ...]], None]", "Callable[[int, Unpack[tuple[str, ...]]], None]", False),
        ("tuple[int, str]", "tuple[int, str]", True),
    ],
)
@pytest.mark.parametrize("module", ["typing", "typing_extensions"])
def test_an_unpacked_tuple_is_written_with_unpack(hint: str, fix: str, module: str, *, shallow: bool) -> None:
    """Where the module imports `Unpack`: `*tuple[str, ...]` in a subscript is Python 3.11's syntax.

    `Unpack[...]` nests one deeper, as LVA006 counts it: a fix only if still `shallow` enough.
    """
    source: str = f"""
    from collections.abc import Callable
    from {module} import Unpack

    Pair = tuple[int, str]


    def f(q) -> None:
        x = q.make()
    """
    deeper: Checks = Checks(nesting=4)
    assert [o.fix for o in _checked(source, {"x": hint}, deeper)] == [fix]
    assert [o.fix for o in _checked(source, {"x": hint})] == [fix if shallow else None]
    other: str = source.replace("Unpack", "Self")
    assert [o.fix for o in _checked(other, {"x": hint}, deeper)] == [fix if fix == hint else None]


@pytest.mark.parametrize(
    ("oldest", "kept"),
    [((3, 11), True), ((3, 14), True), ((3, 10), False), (None, False)],
)
def test_an_unpacked_tuple_is_kept_where_every_python_parses_it(
    oldest: tuple[int, int] | None,
    *,
    kept: bool,
) -> None:
    """As the checker printed it, for a project whose oldest Python (`min-python`) is 3.11 or later."""
    source: str = """
    def f(q) -> None:
        x = q.make()
    """
    hint: str = "tuple[str, *tuple[str, ...]]"
    found: list[Offence] = _checked(source, {"x": hint}, Checks(min_python=oldest))
    assert [o.fix for o in found] == [hint if kept else None]


def test_a_type_variable_is_a_fix_only_where_its_function_declares_it() -> None:
    """A type variable ty prints with its scope is the variable; a fix where its function declares it.

    Where neither the function's signature nor its class names it, it's unbound.
    """
    source: str = """
    from typing import Generic, TypeVar

    Model = TypeVar("Model")
    T = TypeVar("T")
    top = make()


    def create_model(base: "type[Model]", q) -> None:
        a = q.make()


    def other(q) -> None:
        b = q.make()


    class Box(Generic[T]):
        def get(self, q) -> None:
            c = q.make()
            d = q.make()

            def inner() -> None:
                e = q.make()
    """
    hints: dict[str, str] = {
        "top": "type[Model]",
        "a": "type[Model@create_model]",
        "b": "type[Model@create_model]",
        "c": "list[T@Box]",
        "d": "list[Model@create_model]",
        "e": "list[T@Box]",
    }
    found: list[Offence] = _checked(source, hints, Checks(all_scopes=True))
    assert {o.name: o.fix for o in found if o.name in hints} == {
        "top": None,  # a module body declares none
        "a": "type[Model]",
        "b": None,
        "c": "list[T]",  # its class's
        "d": None,
        "e": "list[T]",  # a function defined in the method reads its class's too
    }


def test_a_well_known_class_is_imported() -> None:
    """A class a checker prints by its bare name is imported, unless the file has it already."""
    source: str = "def f(q) -> None:\n    x = q.make()\n    y = q.make()\n"
    offences: list[Offence] = _checked(source, {"x": "Iterator[Path]", "y": "Iterator[Path]"})
    fixed: str = "".join(
        fixes.apply(source.splitlines(keepends=True), [o for o in offences if o.edit is not None]),
    )
    expected: str = (
        "from collections.abc import Iterator\n"
        "from pathlib import Path\n"
        "def f(q) -> None:\n"
        "    x: Iterator[Path] = q.make()\n"
        "    y: Iterator[Path] = q.make()\n"
    )
    assert fixed == expected


def test_a_taken_name_is_imported_by_its_module_or_not_at_all() -> None:
    """`Path` bound elsewhere gets `pathlib.Path`; with `pathlib` taken too, no fix.

    A name the module binds at its top level means what it binds there: the checker prints only a
    bare name, and a value of the module's own `Path` is as likely as one of `pathlib`'s.
    """
    source: str = "def g(Path, pathlib) -> None: ...\ndef f(q) -> None:\n    x = q.make()\n"
    assert _fixes(source.replace(", pathlib", ""), {"x": "Path"}) == [("x", "pathlib.Path", True)]
    assert _fixes(source, {"x": "Path"}) == [("x", None, False)]
    assert _fixes("from mine import Path\n" + source, {"x": "Path"}) == [("x", "Path", True)]


def test_a_module_body_uses_only_what_is_bound_before() -> None:
    """A module-level annotation is evaluated where it is: a class defined later can't be used."""
    source: str = """
    x = make()
    class Early: ...
    y = make()
    """
    offences: list[Offence] = _checked(source, {"x": "Early", "y": "Early"}, Checks(all_scopes=True))
    assert [(o.name, o.fix) for o in offences] == [("x", None), ("y", "Early")]


def test_another_name_for_a_class_stays_an_alias() -> None:
    """Declared a `type[C]`, a variable, it could no longer be an annotation: a lowercase local can."""
    source: str = "Number = int\nkind = int\n\n\ndef f(q) -> None:\n    Pair = q.pair\n    cls = q.kind\n"
    hinted: dict[str, str] = dict.fromkeys(("Number", "kind", "Pair", "cls"), "type[int]")
    offences: list[Offence] = _checked(source, hinted, Checks(all_scopes=True))
    assert {o.name: o.fix for o in offences} == {
        "Number": None,
        "kind": None,
        "Pair": None,
        "cls": "type[int]",
    }


def test_a_function_uses_any_name_the_module_binds() -> None:
    """A local's annotation is never evaluated: a class the module defines after it will do."""
    source: str = "def f(q) -> None:\n    x = q.make()\nclass Late: ...\n"
    assert _fixes(source, {"x": "Late"}) == [("x", "Late", True)]


def test_constricters_own_inference_comes_first() -> None:
    """Where `--fix` types a value itself, its own type stands, a guess or not."""
    source: str = "def f() -> None:\n    x = 1\n    y = Box(1)\n"
    assert _fixes(source, {"x": "Literal[1]", "y": "Box[int]"}) == [("x", "int", False), ("y", "Box", True)]


def test_what_follows_from_a_hint_is_a_guess_too() -> None:
    """A copy of a hinted local is typed in the same pass, as a guess resting on the checker."""
    source: str = "def f(q) -> None:\n    x = q.make()\n    y = x\n"
    offences: list[Offence] = _checked(source, {"x": "int"})
    assert [(o.name, o.fix, o.unsafe) for o in offences] == [("x", "int", True), ("y", "int", True)]
    trusted: list[Offence] = _checked(
        source,
        {"x": "int"},
        Checks(fixes=FixPolicy(unsafe_select=frozenset({"checker"}))),
    )
    assert [o.unsafe for o in trusted] == [False, False]
    ignored: list[Offence] = _checked(
        source,
        {"x": "int"},
        Checks(fixes=FixPolicy(ignore=frozenset({"checker"}))),
    )
    assert [o.fix for o in ignored] == [None, None]


def test_loop_with_and_unpacking_targets_are_declared() -> None:
    """A hinted name a statement binds some other way is declared before it."""
    source: str = """
    def f(q) -> None:
        for item in q:
            pass
        with q as held:
            pass
        first, second = q
    """
    offences: list[Offence] = _checked(source, {"item": "int", "held": "str", "first": "bytes"})
    assert [(o.name, o.fix, o.edit.edit if o.edit else None) for o in offences] == [
        ("item", "int", Edit.DECLARE),
        ("held", "str", Edit.DECLARE),
        ("first", "bytes", Edit.DECLARE),
        ("second", None, None),
    ]


def test_a_late_fix_replaces_a_hints() -> None:
    """`None` then one type, or an empty container filled, is typed by `--fix` itself, not the hint."""
    source: str = """
    def f(n: int) -> None:
        x = None
        x = n
        y = []
        y.append(n)
    """
    assert _fixes(source, {"x": "None", "y": "list[Unknown]"}) == [
        ("x", "int | None", False),
        ("y", "list[int]", True),
    ]
    assert _fixes(source, {"x": "int | None", "y": "list[int]"}) == [
        ("x", "int | None", False),
        ("y", "list[int]", True),
    ]


def test_none_then_a_guess_is_a_guess() -> None:
    """`x = None`, then only a hinted value: `T | None`, a guess resting on the checker."""
    source: str = "def f(q) -> None:\n    x = None\n    x = q.make()\n"
    offences: list[Offence] = _checked(source, {"x": "int"})
    assert [(o.fix, o.unsafe, o.edit.kinds if o.edit else None) for o in offences] == [
        ("int | None", True, frozenset({"optional", "checker"})),
    ]


def test_a_class_body_is_never_fixed() -> None:
    """A dataclass's annotation is a field: a class body's hints change nothing."""
    source: str = "class C:\n    x = make()\n"
    assert [o.fix for o in _checked(source, {"x": "int"}, Checks(all_scopes=True))] == [None]


def _offering(
    source: str,
    offered: dict[str, Offered],
    checks: Checks = _DEFAULT,
    shown: str = "Shape",
) -> list[Offence]:
    """Check `source`, the checker hinting each name in `offered` as `shown`, with those edits.

    Returns:
      The offences.

    """
    text: str = textwrap.dedent(source)
    ends: dict[str, tuple[int, int]] = {
        node.id: (node.lineno, node.end_col_offset or 0)
        for node in ast.walk(ast.parse(text))
        if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Store) and node.id in offered
    }
    hints: Hints = Hints(
        _CHECKER,
        dict.fromkeys(ends.values(), shown),
        {where: offered[name] for name, where in ends.items()},
    )
    return check_source(text, checks=checks, outside=Outside(hints=(hints,)))


def _applied(source: str, offences: list[Offence]) -> str:
    """Apply `offences`' fixes to `source`.

    Returns:
      It, fixed.

    """
    return "".join(fixes.apply(source.splitlines(keepends=True), [o for o in offences if o.edit is not None]))


_USE: Final = "def f(q) -> None:\n    x = q.make()\n"
_SHAPE: Final = Offered("Shape", ("from shapes import Shape",))


@pytest.mark.parametrize(
    ("offered", "fixed"),
    [
        (_SHAPE, "    from shapes import Shape\ndef f(q) -> None:\n    x: Shape = q.make()\n"),
        (
            Offered("Shape", ("from .shapes import Shape",)),
            "    from .shapes import Shape\ndef f(q) -> None:\n    x: Shape = q.make()\n",
        ),
        (
            Offered("S", ("from shapes import Shape as S",)),
            "    from shapes import Shape as S\ndef f(q) -> None:\n    x: S = q.make()\n",
        ),
    ],
)
def test_a_class_the_hints_edits_import_is_imported_for_type_checking(offered: Offered, fixed: str) -> None:
    """A class the file doesn't bind is imported from where the checker's own edit says, unrun."""
    expected: str = "from typing import TYPE_CHECKING\nif TYPE_CHECKING:\n" + fixed
    assert _applied(_USE, _offering(_USE, {"x": offered}, shown=offered.text)) == expected


def test_an_edit_importing_a_module_names_no_class() -> None:
    """`import shapes` says the module, not which of its names is a class: no fix."""
    module: Offered = Offered("shapes.Shape", ("import shapes",))
    assert [o.fix for o in _offering(_USE, {"x": module}, shown="shapes.Shape")] == [None]


def test_a_module_bodys_annotation_with_such_a_class_is_quoted() -> None:
    """Evaluated when the module runs, where the class isn't bound: the annotation is a string."""
    source: str = "x = make()\n"
    offences: list[Offence] = _offering(source, {"x": _SHAPE}, Checks(all_scopes=True))
    assert [o.fix for o in offences] == ['"Shape"']


def test_an_import_the_module_runs_is_used_before_one_is_added() -> None:
    """With the class's module imported, or the class under another name, the file names it that way."""
    assert [o.fix for o in _offering("import shapes\n" + _USE, {"x": _SHAPE})] == ["shapes.Shape"]
    assert [o.fix for o in _offering("from shapes import Shape as S\n" + _USE, {"x": _SHAPE})] == ["S"]


def test_a_name_the_module_binds_some_other_way_isnt_imported() -> None:
    """A parameter or a local named like the class would shadow the import, or it them: no fix."""
    source: str = "def g(Shape) -> None: ...\n" + _USE
    assert [o.fix for o in _offering(source, {"x": _SHAPE})] == [None]
    several: Offered = Offered("dict[Shape, Other]", ("from shapes import Shape", "from shapes import Other"))
    assert [o.fix for o in _offering(source, {"x": several})] == [None]


def test_two_hints_naming_one_class_share_its_import_and_a_namesake_has_no_fix() -> None:
    """The first hint's import is what the name means in the file: another module's class isn't it."""
    source: str = "def f(q) -> None:\n    x = q.make()\n    y = q.make()\n    z = q.make()\n"
    other: Offered = Offered("Shape", ("from elsewhere import Shape",))
    offences: list[Offence] = _offering(source, {"x": _SHAPE, "y": _SHAPE, "z": other})
    assert [(o.name, o.fix) for o in offences] == [("x", "Shape"), ("y", "Shape"), ("z", None)]
    assert _applied(source, offences).count("import Shape") == 1


def test_a_name_no_edit_imports_has_no_fix() -> None:
    """An edit importing one of a hint's classes says nothing of another."""
    offered: Offered = Offered("dict[Shape, Other]", ("from shapes import Shape",))
    assert [o.fix for o in _offering(_USE, {"x": offered}, shown="dict[Shape, Other]")] == [None]


def test_an_annotation_is_written_as_the_hint_shows_it_or_as_its_edit_spells_it() -> None:
    """What the hint shows comes first, then its edit's spelling through a module the file imports."""
    counter: Offered = Offered("typing.Counter[str]")
    shown: list[Offence] = _offering("import typing\n" + _USE, {"x": counter}, shown="Counter[str]")
    assert [(o.fix, o.edit.imports if o.edit else None) for o in shown] == [
        ("Counter[str]", ("from collections import Counter",)),
    ]
    thing: Offered = Offered("things.Thing[str]")
    spelled: list[Offence] = _offering("import things\n" + _USE, {"x": thing}, shown="Thing[str]")
    assert [o.fix for o in spelled] == ["things.Thing[str]"]
    assert [o.fix for o in _offering(_USE, {"x": thing}, shown="Thing[str]")] == [None]


def test_an_edit_writing_a_generic_under_another_name_is_no_fix() -> None:
    """A generic alias ty's edit writes as its class keeps the alias's arguments: not the class's."""
    numpy: str = "import numpy as np\n" + _USE
    array: Offered = Offered("np.ndarray[np.float64]")
    assert [o.fix for o in _offering(numpy, {"x": array}, shown="NDArray[float64]")] == [None]
    nested: Offered = Offered("list[np.ndarray[np.float64]]")
    assert [o.fix for o in _offering(numpy, {"x": nested}, shown="list[_Array1D[float64]]")] == [None]
    both: Offered = Offered("np.ndarray[tuple[int], np.dtype[np.float64]]")
    shown: str = "ndarray[tuple[int], dtype[float64]]"
    assert [o.fix for o in _offering(numpy, {"x": both}, shown=shown)] == [both.text]


def test_an_edit_writing_a_generic_by_the_files_name_for_it_is_a_fix() -> None:
    """A name the file, or the edit's own import, binds to the class shown is that class."""
    renamed: Offered = Offered("T[str]")
    source: str = "from things import Thing as T\n" + _USE
    assert [o.fix for o in _offering(source, {"x": renamed}, shown="Thing[str]")] == ["T[str]"]
    imported: Offered = Offered("S[str]", ("from shapes import Shape as S",))
    assert [o.fix for o in _offering(_USE, {"x": imported}, shown="Shape[str]")] == ["S[str]"]
    assert [o.fix for o in _offering(_USE, {"x": Offered("Thing[")}, shown="Thing[")] == [None]


def test_a_well_known_class_is_imported_to_run_unless_the_edit_says_another() -> None:
    """A standard-library class a checker prints bare is imported as ever; a namesake, as its edit says."""
    standard: Offered = Offered("Path", ("from pathlib import Path",))
    mine: Offered = Offered("Path", ("from mine import Path",))
    offences: list[Offence] = [
        *_offering(_USE, {"x": standard}, shown="Path"),
        *_offering(_USE, {"x": mine}, shown="Path"),
    ]
    assert [(o.edit.imports, o.edit.guarded) if o.edit else None for o in offences] == [
        (("from pathlib import Path",), ()),
        (("from typing import TYPE_CHECKING",), ("from mine import Path",)),
    ]


@pytest.mark.parametrize(
    ("shown", "imported", "fix"),
    [
        ("itemgetter[str]", "from operator import itemgetter", "itemgetter[str]"),
        ("itemgetter", "from operator import itemgetter", None),  # a generic class, bare
        ("dict[str, itemgetter]", "from operator import itemgetter", None),
        ("IPv4Address", "from ipaddress import IPv4Address", "IPv4Address"),
        ("dict_keys[str, int]", "from _collections_abc import dict_keys", None),  # a private module
        ("SupportsRead[str]", "from _typeshed import SupportsRead", None),  # the stubs' own
        ("path", "from os import path", None),  # a module
        ("getLogger", "from logging import getLogger", None),  # a function
        ("Thing", "from mine._impl import Thing", "Thing"),  # not the standard library's
    ],
)
def test_a_standard_library_class_an_edit_imports_must_be_one_the_file_can_write(
    shown: str,
    imported: str,
    fix: str | None,
) -> None:
    """A class its tables know, from a public module, and no generic one without its arguments."""
    offered: Offered = Offered(shown, (imported,))
    assert [o.fix for o in _offering(_USE, {"x": offered}, shown=shown)] == [fix]


def test_a_generic_class_a_hint_shows_bare_is_no_fix() -> None:
    """A checker prints a generic class bare when it doesn't know its arguments: nothing to write."""
    source: str = """
    from typing import Generic, TypeVar

    T = TypeVar("T")


    class Box(Generic[T]): ...


    def f(q) -> None:
        x = q.make()
        y = q.make()
    """
    assert _fixes(source, {"x": "Box", "y": "Box[int]"}) == [("x", None, False), ("y", "Box[int]", True)]


_ALIASES: Final = """
class Shape: ...


Json = dict[str, "Json"] | str
Pair = tuple[int, str]
Same = Shape


def f(q) -> None:
    Local = dict[str, int]
"""


@pytest.mark.parametrize(
    ("imports", "fix", "added"),
    [
        ("", "TypeAlias", ("from typing import TypeAlias",)),
        ("from typing import TypeAlias\n", "TypeAlias", ()),
        ("from typing_extensions import TypeAlias\n", "TypeAlias", ()),
        ("import typing as t\n", "t.TypeAlias", ()),
        (
            "import typing\nfrom typing_extensions import TypeAlias\n",
            "TypeAlias",
            (),
        ),  # the name itself first
        ("TypeAlias = 1\n", "typing.TypeAlias", ("import typing",)),
        ("TypeAlias = typing = 1\n", None, ()),  # no name is free to import it by
    ],
)
def test_a_composite_alias_is_declared_one(imports: str, fix: str | None, added: tuple[str, ...]) -> None:
    """`TypeAlias`, hinted for an alias's assignment, declares a module's alias made of other types.

    One written as a subscript or a union.

    Named as the module's imports can, else imported from `typing`. Never a bare class's alias, which
    declared one loses the class's type parameters, nor a function's local.
    """
    names: dict[str, str] = dict.fromkeys(("Json", "Pair", "Same", "Local"), "TypeAlias")
    offences: list[Offence] = [
        o for o in _checked(imports + _ALIASES, names, Checks(all_scopes=True)) if o.name in names
    ]
    assert [(o.name, o.fix) for o in offences] == [
        ("Json", fix),
        ("Pair", fix),
        ("Same", None),
        ("Local", None),
    ]
    assert {o.edit.imports for o in offences if o.edit is not None} <= {added}


def test_a_hint_declares_an_alias_fix_alone_cant_vouch_for() -> None:
    """A union of a class an unchecked package defines: only the checker says it's a type (a guess)."""
    source: str = "from typing import TypeAlias\nfrom other import Thing\nMaybe = Thing | None\n"
    offences: list[Offence] = _checked(source, {"Maybe": "TypeAlias"}, Checks(all_scopes=True))
    assert [(o.name, o.fix, o.unsafe) for o in offences] == [("Maybe", "TypeAlias", True)]
    assert [o.edit.kinds for o in offences if o.edit is not None] == [{"checker"}]


def test_an_alias_is_declared_only_where_typealias_is_bound_by_then() -> None:
    """A module body's annotation is evaluated: an import of `TypeAlias` further down doesn't name it."""
    source: str = "Pair = tuple[int, str]\nfrom typing import TypeAlias\nJson = dict[str, int]\n"
    names: dict[str, str] = {"Pair": "TypeAlias", "Json": "TypeAlias"}
    offences: list[Offence] = _checked(source, names, Checks(all_scopes=True))
    assert [(o.name, o.fix) for o in offences] == [("Pair", None), ("Json", "TypeAlias")]
    assert type_alias(Known({}, frozenset(), {}, {}), 1) is None  # a module not read for its imports
    spelled: list[Offence] = _offering(
        "import typing\ndef f(q) -> None:\n    x = q.kind\n",
        {"x": Offered("typing.TypeAlias")},
        shown="list[TypeAlias]",
    )
    assert [o.fix for o in spelled] == [None]  # nowhere else is it an annotation


def test_a_class_the_module_imports_for_type_checking_is_used_as_it_is() -> None:
    """A class the index finds among the module's `if TYPE_CHECKING:` imports: quoted in a module body."""
    source: str = """
    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from shapes import Late, Shape, sizes

    x = make()


    def g(Late) -> None: ...


    def f(q) -> None:
        a = q.make()
        b = q.make()
        c = q.make()
    """
    hinted: dict[str, str] = {"x": "Shape", "a": "dict[str, Shape]", "b": "sizes", "c": "Late"}
    offences: list[Offence] = _checked(source, hinted, Checks(all_scopes=True), ("Shape", "Late"))
    assert [(o.name, o.fix) for o in offences if o.name in hinted] == [
        ("x", '"Shape"'),
        ("a", "dict[str, Shape]"),
        ("b", None),  # not a class
        ("c", None),  # a parameter's name too
    ]
    assert all(o.edit is None or not (o.edit.imports or o.edit.guarded) for o in offences)


def test_the_first_checker_whose_hint_is_usable_wins() -> None:
    """With two checkers, the first named whose hint the file can use types the name."""
    source: str = "def f(q) -> None:\n    x = q.make()\n    y = q.make()\n"
    first: Hints = Hints("ty", {(2, 5): "Unknown", (3, 5): "int"})
    second: Hints = Hints(_CHECKER, {(2, 5): "str", (3, 5): "bytes"})
    offences: list[Offence] = check_source(source, outside=Outside(hints=(first, second)))
    assert [(o.name, o.fix, o.edit.reason if o.edit else None) for o in offences] == [
        ("x", "str", "basedpyright's inferred type"),
        ("y", "int", "ty's inferred type"),
    ]
