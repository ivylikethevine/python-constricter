# SPDX-License-Identifier: MIT
"""The rules themselves (constricter.checker): what they report and what they exempt."""

import ast
import sys
import textwrap
from pathlib import Path
from typing import Final

import pytest

from constricter import (
    COMMENT_TYPED_TARGET,
    LEVELS,
    NESTED_TYPE,
    REDUNDANT_TYPE,
    UNANNOTATED,
    UNANNOTATED_MEMBER,
    UNTYPED_TARGET,
    VAGUE_TYPE,
    Checks,
    Coverage,
    Level,
    Offence,
    annotation_coverage,
    check_source,
    check_tree,
)

EXEMPT: Final = """
import os
from os import path as p

G = 0


class Holder:
    count: int = 0

    def method(self, items: list[int]) -> int:
        total: int = 0
        i: int
        for i in items:
            total += i
        return total


async def coroutine(items: list[str], *args: str, **kwargs: str) -> str:
    global G
    G = 1
    import re
    first: str
    rest: list[str]
    others: dict[str, str]
    whole: str
    match items:
        case [first, *rest] if first:
            pass
        case {**others}:
            pass
        case str() as whole:
            pass
        case _:
            pass
    try:
        raise ValueError
    except ValueError as e:
        pass
    try:
        raise TypeError
    except* TypeError as eg:
        pass
    _ = print()
    with open(os.devnull):
        pass
    joined: str = ",".join(x for x in items)
    n: int
    more: list[int]
    n, *more = 1, 2, 3
    item: str
    async for item in aiter(items):
        pass
    fh: typing.TextIO
    async with open(os.devnull) as fh:
        pass
    while (n := n - 1) > 0:
        pass
    m: re.Match[str] | None
    assert (m := re.match("x", joined)) or True
    square: Callable[[int], int] = lambda v: (w := v * v)
    total: int = 0
    total += 1

    def nested(value: int) -> int:
        inner: int = value + n
        return inner

    if joined:
        return joined
    else:
        return str(m)
"""

OFFENDING: Final = """
def broken(items: list[int]) -> None:
    plain = 1
    a: int
    a, b = 1, 2
    first, *rest = items
    if (count := len(items)) > 0:
        pass
    with open("x") as fh:
        pass
    plain = 2
    a = count
"""

MEMBER_MESSAGE: Final = "module or class variable 'x' is not annotated where it's first bound"
HALF: Final = 50.0
ALL: Final = 100.0
X_MESSAGE: Final = "local variable 'x' is not annotated where it's first bound"


def _check(source: str) -> list[Offence]:
    return check_source(textwrap.dedent(source))


def _codes(source: str) -> list[tuple[str, str]]:
    return [(o.name, o.code) for o in _check(source)]


def test_exempt_bindings_and_declared_locals_pass() -> None:
    """Exempt and declared bindings report nothing, at any level."""
    assert _check(EXEMPT) == []


def test_each_unannotated_first_binding_is_reported_once_at_its_name() -> None:
    """Each unannotated first binding is reported once, at its name."""
    assert _check(OFFENDING) == [
        Offence(3, 4, "plain"),
        Offence(5, 7, "b"),
        Offence(6, 4, "first"),
        Offence(6, 12, "rest"),
        Offence(7, 8, "count"),
        Offence(9, 22, "fh"),
    ]


def test_the_message_names_the_variable() -> None:
    """The message quotes the variable's name."""
    assert Offence(1, 0, "x").message == X_MESSAGE


@pytest.mark.parametrize(
    ("source", "expected"),
    [
        pytest.param(
            """
            def outer() -> None:
                class Local:
                    def method(self) -> None:
                        x = 1
            """,
            [Offence(5, 12, "x")],
            id="method-of-a-class-defined-in-a-function",
        ),
        pytest.param(
            """
            if True:
                def conditional() -> None:
                    x = 1
            try:
                import os
            except ImportError:
                def fallback() -> None:
                    y = 1
            """,
            [Offence(4, 8, "x"), Offence(9, 8, "y")],
            id="functions-inside-module-level-blocks",
        ),
        pytest.param(
            """
            class Outer:
                class Inner:
                    def method(self) -> None:
                        x = 1
            """,
            [Offence(5, 12, "x")],
            id="nested-classes",
        ),
        pytest.param(
            """
            def f(items: list[int]) -> None:
                values: list[int] = [y for x in items if (y := x)]
            """,
            [Offence(3, 46, "y")],
            id="walrus-in-a-comprehension-binds-the-function-local",
        ),
        pytest.param(
            """
            def f() -> None:
                def g() -> None:
                    x = 1
                x: int = 2
            """,
            [Offence(4, 8, "x")],
            id="nested-function-is-its-own-scope",
        ),
        pytest.param(
            """
            def f(flag: bool) -> None:
                if flag:
                    x = 1
                else:
                    x = 2
            """,
            [Offence(4, 8, "x")],
            id="first-binding-in-source-order",
        ),
        pytest.param(
            """
            def f(flag: bool) -> None:
                try:
                    pass
                except ValueError:
                    a = 1
                else:
                    b = 2
                finally:
                    c = 3
            """,
            [Offence(6, 8, "a"), Offence(8, 8, "b"), Offence(10, 8, "c")],
            id="every-try-block",
        ),
        pytest.param(
            """
            def f(obj: object) -> None:
                obj.attr = 1
                obj[0] = 2
            X = 1
            class C:
                y = 2
            """,
            [],
            id="attributes-subscripts-module-and-class-bodies",
        ),
    ],
)
def test_scopes(source: str, expected: list[Offence]) -> None:
    """Every function is its own scope, wherever it's defined."""
    assert _check(source) == expected


def test_its_own_source_follows_the_rule() -> None:
    """The package and its tests pass every code, module and class bodies included."""
    package: Path = Path(__file__).resolve().parents[1] / "src" / "constricter"
    sources: list[Path] = sorted(package.glob("*.py")) + sorted(Path(__file__).parent.glob("*.py"))
    assert package / "checker.py" in sources
    offences: list[str] = [
        f"{p}:{o.line}: {o.code} {o.name}"
        for p in sources
        for o in check_source(p.read_text(encoding="utf-8"), checks=Checks(all_scopes=True))
    ]
    assert offences == []


def test_type_comments_count_only_when_enabled() -> None:
    """`# type:` comments type `=` and `with` bindings only when enabled."""
    source: str = textwrap.dedent(
        """
        def f(path: str) -> None:
            a = 1  # type: int
            with open(path) as fh:  # type: object
                pass
        """,
    )
    assert [o.name for o in check_source(source)] == ["a", "fh"]
    assert not check_source(source, checks=Checks(type_comments=True))


def test_for_and_match_variables() -> None:
    """Untyped for/match variables are LVA002; comment-typed for variables are LVA003."""
    source: str = """
    def f(items: list[int], obj: object) -> None:
        for a in items:
            pass
        for b, c in []:  # type: int, int
            pass
        d: int
        for d in items:
            pass
        e = 0
        for e in items:
            pass
        for _ in items:
            pass
        for obj.attr in items:
            pass
        match obj:
            case [g, *h]:
                pass
            case {"k": 1, **i}:
                pass
        j: str
        match obj:
            case str() as j:
                pass
    """
    assert _codes(source) == [
        ("a", UNTYPED_TARGET),
        ("b", COMMENT_TYPED_TARGET),
        ("c", COMMENT_TYPED_TARGET),
        ("e", UNANNOTATED),
        ("g", UNTYPED_TARGET),
        ("h", UNTYPED_TARGET),
        ("i", UNTYPED_TARGET),
    ]


def test_messages() -> None:
    """Each code's message names the variable and the fix."""
    codes: tuple[str, ...] = (UNTYPED_TARGET, COMMENT_TYPED_TARGET, REDUNDANT_TYPE)
    assert [Offence(1, 0, "x", code).message for code in codes] == [
        "for/match variable 'x' is untyped; declare it before the statement",
        "for variable 'x' is typed only by a type comment; declare it before the loop",
        "'x' is annotated again with the type it already has, in the same block",
    ]


@pytest.mark.parametrize(
    ("level", "errors"),
    [
        (Level.RELAXED, set[str]()),
        (Level.STRICT, {UNANNOTATED, UNANNOTATED_MEMBER}),
        (Level.CONSTRICT, {UNANNOTATED, UNANNOTATED_MEMBER, UNTYPED_TARGET}),
        (
            Level.SUFFOCATE,
            {UNANNOTATED, UNANNOTATED_MEMBER, UNTYPED_TARGET, COMMENT_TYPED_TARGET, REDUNDANT_TYPE},
        ),
    ],
)
def test_levels(level: Level, errors: set[str]) -> None:
    """Each level makes one more code an error; the rest are warnings."""
    codes: tuple[str, ...] = (
        UNANNOTATED,
        UNANNOTATED_MEMBER,
        UNTYPED_TARGET,
        COMMENT_TYPED_TARGET,
        REDUNDANT_TYPE,
    )
    assert {code for code in codes if Offence(1, 0, "x", code).is_error(level)} == errors


def test_levels_by_name_and_number() -> None:
    """The options take a level's name or its number."""
    assert LEVELS == {
        "relaxed": Level.RELAXED,
        "0": Level.RELAXED,
        "strict": Level.STRICT,
        "1": Level.STRICT,
        "constrict": Level.CONSTRICT,
        "2": Level.CONSTRICT,
        "suffocate": Level.SUFFOCATE,
        "3": Level.SUFFOCATE,
    }


def test_walrus_in_defaults_and_decorators_binds_the_enclosing_function() -> None:
    """A `:=` in a nested def's default or decorator binds in the enclosing function."""
    source: str = """
    def f() -> None:
        @print if (a := 1) else print
        def g(x: int = (b := 2)) -> None:
            pass
    """
    assert _codes(source) == [("a", UNANNOTATED), ("b", UNANNOTATED)]


def test_a_misplaced_type_comment_is_not_a_syntax_error() -> None:
    """A `# type:` comment Python rejects there is ignored; real syntax errors still raise."""
    assert _codes("def f() -> None:\n    print(1)  # type: int\n    x = 1\n") == [("x", UNANNOTATED)]
    with pytest.raises(SyntaxError):
        _ = check_source("def (:\n")


def test_a_rest_capture_is_reported_at_its_name() -> None:
    """`**rest` is reported at its name, even on a later line; without source, at its pattern."""
    source: str = textwrap.dedent(
        """
    def f(obj: object) -> None:
      match obj:
        case {"k": 1, **rest}:
          pass
        case {
          "a": 1,
          **more,
        }:
          pass
    """,
    )
    assert [(o.line, o.col, o.name) for o in check_source(source)] == [(4, 20, "rest"), (8, 8, "more")]
    tree: ast.Module = ast.parse(source)
    assert [(o.line, o.col) for o in check_tree(tree)] == [(4, 9), (6, 9)]


def test_a_rest_capture_skips_an_earlier_non_matching_one_on_the_same_line() -> None:
    """A nested pattern's `**capture` before the outer one's, on the same line, isn't mistaken for it."""
    source: str = textwrap.dedent(
        """
    def f(obj: object) -> None:
      match obj:
        case {"a": {"b": 1, **inner}, **outer}:
          pass
    """,
    )
    assert [(o.line, o.col, o.name) for o in check_source(source)] == [
        (4, 26, "inner"),
        (4, 36, "outer"),
    ]


def test_python2_compatible_modules_count_type_comments() -> None:
    """A `from __future__` import only Python 2 needs turns type comments on; others don't."""
    body: str = "def f() -> None:\n  x = 1  # type: int\n"
    assert not _codes("from __future__ import print_function\n" + body)
    assert _codes("from __future__ import annotations\n" + body) == [("x", UNANNOTATED)]


def test_all_scopes_checks_module_and_class_bodies() -> None:
    """With `all_scopes`, module and class bodies report LVA004; enums and dunders are exempt."""
    source: str = textwrap.dedent(
        """
    import enum
    __all__ = ["C"]
    LIMIT = 3
    TYPED: int = 4
    for item in []:
      pass


    class C:
      size = 1
      __slots__ = ()
      name: str = "c"


    class Colour(enum.Enum):
      RED = 1


    def f() -> None:
      class Local:
        inner = 2
    """,
    )
    assert _codes(source) == []
    assert [(o.name, o.code) for o in check_source(source, checks=Checks(all_scopes=True))] == [
        ("LIMIT", UNANNOTATED_MEMBER),
        ("item", UNTYPED_TARGET),
        ("size", UNANNOTATED_MEMBER),
        ("inner", UNANNOTATED_MEMBER),
    ]
    assert Offence(1, 0, "x", UNANNOTATED_MEMBER).message == MEMBER_MESSAGE


@pytest.mark.parametrize(
    ("annotation", "codes"),
    [
        ("Any", [VAGUE_TYPE]),
        ("typing.Any", [VAGUE_TYPE]),
        ("object", [VAGUE_TYPE]),
        ("list", [VAGUE_TYPE]),
        ("list[Any]", [VAGUE_TYPE]),
        ('"dict"', [VAGUE_TYPE]),
        ("Callable", [VAGUE_TYPE]),
        ("dict[str, int]", []),
        ("Callable[..., int]", []),
        ("tuple[int, ...]", []),
        ('"list[int]"', []),
        ('"not an expression ("', []),
        ("int | None", []),
    ],
)
def test_vague_annotations(annotation: str, codes: list[str]) -> None:
    """`Any`, `object` and generics without their parameters are LVA005."""
    source: str = f"def f() -> None:\n  x: {annotation}\n"
    assert [o.code for o in check_source(source)] == codes


@pytest.mark.parametrize(
    ("annotation", "nesting", "codes"),
    [
        ("dict[str, list[tuple[int, set[str]]]]", 5, []),
        ("dict[str, list[tuple[int, set[frozenset[str]]]]]", 5, [NESTED_TYPE]),
        ("list[int] | dict[str, list[int]]", 2, [NESTED_TYPE]),
        ('"list[list[int]]"', 2, [NESTED_TYPE]),
        ("Callable[[list[int]], int]", 3, []),
    ],
)
def test_nested_annotations(annotation: str, nesting: int, codes: list[str]) -> None:
    """An annotation whose subscripts nest `nesting` deep is LVA006."""
    source: str = f"def f() -> None:\n  x: {annotation} = []\n"
    assert [o.code for o in check_source(source, checks=Checks(nesting=nesting))] == codes


def test_vague_and_nested_are_reported_from_strict() -> None:
    """LVA005 and LVA006 aren't reported at `relaxed`, warn below `suffocate`, and error at it."""
    offence: Offence
    for offence in (Offence(1, 0, "x", VAGUE_TYPE), Offence(1, 0, "x", NESTED_TYPE)):
        assert [offence.is_reported(level) for level in Level] == [False, True, True, True]
        assert [offence.is_error(level) for level in Level] == [False, False, False, True]
    assert Offence(1, 0, "x").is_reported(Level.RELAXED)


@pytest.mark.parametrize(
    ("source", "expected"),
    [
        pytest.param(
            """
            def f() -> None:
                x: int = 1
                x: int = 2
            """,
            [Offence(4, 4, "x", REDUNDANT_TYPE)],
            id="same-annotation-repeated-in-the-same-block",
        ),
        pytest.param(
            """
            def f() -> None:
                x: int = 1
                y: int = 2
                x: int = 3
            """,
            [Offence(5, 4, "x", REDUNDANT_TYPE)],
            id="still-redundant-across-an-unrelated-binding",
        ),
        pytest.param(
            """
            def f() -> None:
                x: int = 1
                x: str = "a"
            """,
            [],
            id="a-different-annotation-is-not-redundant",
        ),
        pytest.param(
            """
            def f(flag: bool) -> None:
                if flag:
                    x: int = 1
                else:
                    x: int = 2
            """,
            [],
            id="branches-that-never-run-together-are-not-compared",
        ),
        pytest.param(
            """
            def f() -> None:
                try:
                    x: int = 1
                except ValueError:
                    x: int = 2
                finally:
                    x: int = 3
            """,
            [],
            id="try-body-except-and-finally-are-separate-blocks",
        ),
        pytest.param(
            """
            def f() -> None:
                for _ in range(2):
                    x: int = 1
                    x: int = 2
            """,
            [Offence(5, 8, "x", REDUNDANT_TYPE)],
            id="a-loop-body-is-one-block",
        ),
    ],
)
def test_redundant_typing(source: str, expected: list[Offence]) -> None:
    """LVA007: a name annotated again with the type it already has, in the same block."""
    assert _check(source) == expected


def test_redundant_typing_is_reported_from_relaxed_and_errors_at_suffocate() -> None:
    """LVA007 warns at every level and only errors at `suffocate`, like LVA003."""
    offence: Offence = Offence(1, 0, "x", REDUNDANT_TYPE)
    assert [offence.is_reported(level) for level in Level] == [True, True, True, True]
    assert [offence.is_error(level) for level in Level] == [False, False, False, True]


@pytest.mark.parametrize(
    ("value", "fix"),
    [
        ("0", "int"),
        ("-1.5", "float"),
        ("+2", "int"),
        ("True", "bool"),
        ("-True", None),
        ("not y", "bool"),
        ("1j", "complex"),
        ("'text'", "str"),
        ("b'raw'", "bytes"),
        ("f'{0}'", "str"),
        ("Path('x')", "Path"),
        ("ast.Name('x')", "ast.Name"),
        ("len([1])", "int"),
        ("isinstance(1, int)", "bool"),
        ("TypeVar('T')", None),
        ("Counter()", None),
        ("path()", None),
        ("None", None),
        ("[1]", "list[int]"),
        ("[]", None),
        ("[1, 'a']", None),
        ("[[1], [2]]", "list[list[int]]"),
        ("{1, 2}", "set[int]"),
        ("(1, 'a', b'')", "tuple[int, str, bytes]"),
        ("(1, *[])", None),
        ("{'a': 1}", "dict[str, int]"),
        ("{'a': 1, 'b': 'c'}", None),
        ("{**{}}", None),
        ("{}", None),
    ],
)
def test_fixes_are_offered_only_where_the_value_decides_the_type(value: str, fix: str | None) -> None:
    """A literal or a capitalised constructor call offers its annotation; anything else doesn't."""
    offences: list[Offence] = check_source(f"def f() -> None:\n  x = {value}\n")
    assert [(o.name, o.fix) for o in offences] == [("x", fix)]


def test_fixes_are_offered_only_for_a_single_plain_name() -> None:
    """Unpacking, chained `=`, `:=`, `with` and class bodies are never fixed; module bodies are."""
    source: str = textwrap.dedent(
        """
    LIMIT = 3


    def f() -> None:
      a, b = 1, 2
      c = d = 3
      if (e := 4):
        pass


    class C:
      size = 1
    """,
    )
    assert [(o.name, o.fix) for o in check_source(source, checks=Checks(all_scopes=True))] == [
        ("LIMIT", "int"),
        ("a", None),
        ("b", None),
        ("c", None),
        ("d", None),
        ("e", None),
        ("size", None),
    ]


@pytest.mark.skipif(sys.version_info < (3, 12), reason="`type` statements are Python 3.12+")
def test_a_type_alias_statement_binds_its_name() -> None:
    """`type X = ...` binds `X` with no annotation needed."""
    assert not _codes("def f() -> None:\n  type Alias = list[int]\n  Alias = 1\n")


def test_fixes_use_same_module_return_types() -> None:
    """A call to a plain module function offers its declared return type; unsafe ones don't."""
    source: str = textwrap.dedent(
        """
    from typing import Any, TypeVar
    T = TypeVar("T")


    def count() -> int: ...
    def rows() -> list[tuple[int, str]]: ...
    def nothing() -> None: ...
    def vague() -> Any: ...
    def same(value: T) -> T: ...
    def untyped(): ...
    async def later() -> int: ...
    @cache
    def cached() -> int: ...
    def twice() -> int: ...
    def twice() -> str: ...


    def f() -> None:
      a = count()
      b = [rows(), rows()]
      c = nothing()
      d = vague()
      e = same(1)
      g = untyped()
      h = later()
      i = cached()
      j = twice()
    """,
    )
    assert [(o.name, o.fix) for o in check_source(source)] == [
        ("a", "int"),
        ("b", "list[list[tuple[int, str]]]"),
        ("c", None),
        ("d", None),
        ("e", None),
        ("g", None),
        ("h", None),
        ("i", None),
        ("j", None),
    ]


def test_fixes_copy_an_already_typed_locals_type() -> None:
    """A plain `x = y` offers `y`'s type: its annotation, an earlier fix, or its parameter's."""
    source: str = textwrap.dedent(
        """
    def f(n: int) -> None:
      a: int = 1
      b = a
      c = 2
      d = c
      e = n
      g = h
    """,
    )
    assert [(o.name, o.fix, o.unsafe) for o in check_source(source)] == [
        ("b", "int", False),
        ("c", "int", False),
        ("d", "int", False),
        ("e", "int", False),
        ("g", None, False),
    ]


def test_a_copy_of_a_guessed_fix_is_guessed_too() -> None:
    """A copy of an unsafely-fixed local is offered too, but it's no more certain than its source."""
    source: str = "def f() -> None:\n  a = Box(1)\n  b = a\n"
    assert [(o.name, o.fix, o.unsafe) for o in check_source(source)] == [
        ("a", "Box", True),
        ("b", "Box", True),
    ]


@pytest.mark.parametrize(
    ("param", "subscript", "fix"),
    [
        ("nums: list[int]", "nums[0]", "int"),
        ("nums: list[int]", "nums[1:2]", "list[int]"),
        ("pairs: dict[str, int]", "pairs['x']", "int"),
        ("row: tuple[int, ...]", "row[0]", "int"),
        ("row: tuple[int, str]", "row[0]", None),  # which element varies with the index
        ("text: str", "text[0]", "str"),
        ("text: str", "text[1:3]", "str"),
        ("data: bytes", "data[0:1]", "bytes"),
        ("items: set[int]", "items.pop()", None),  # a `set` isn't subscriptable
        ("nums: list[int]", "nums[i]", "int"),  # a non-literal index still gets the element type
    ],
)
def test_fixes_infer_a_typed_locals_subscript(param: str, subscript: str, fix: str | None) -> None:
    """A subscript of an already-typed local offers its element type, a slice its own type."""
    source: str = f"def f({param}, i: int) -> None:\n  x = {subscript}\n"
    assert [(o.name, o.fix) for o in check_source(source)] == [("x", fix)]


def test_a_subscript_of_a_guessed_fix_is_not_offered() -> None:
    """A subscript of an unsafely-fixed local (`Box` isn't a known container) offers nothing."""
    source: str = "def f() -> None:\n  a = Box([1])\n  b = a[0]\n"
    assert [(o.name, o.fix) for o in check_source(source)] == [("a", "Box"), ("b", None)]


def test_fixes_infer_a_typed_locals_attribute() -> None:
    """A class-level annotated attribute of a locally-constructed instance offers its type."""
    source: str = textwrap.dedent(
        """
    class Point:
      x: int
      y: int
      label = "origin"  # not class-level annotated: not offered

    def f() -> None:
      p = Point()
      a = p.x
      b = p.y
      c = p.z
      d = p.label
    """,
    )
    assert [(o.name, o.fix) for o in check_source(source)] == [
        ("p", "Point"),
        ("a", "int"),
        ("b", "int"),
        ("c", None),
        ("d", None),
    ]


def test_an_attribute_of_a_guessed_fix_is_guessed_too() -> None:
    """A class attribute of an unsafely-fixed local is no more certain than its source."""
    source: str = textwrap.dedent(
        """
    class Point:
      x: int

    def f() -> None:
      p = Point()
      a = p.x
    """,
    )
    assert [(o.name, o.fix, o.unsafe) for o in check_source(source)] == [
        ("p", "Point", True),
        ("a", "int", True),
    ]


def test_fixes_infer_a_methods_self_attribute() -> None:
    """`self.attr` in a method offers its type: class-level, or `self.attr: T = ...` in any method."""
    source: str = textwrap.dedent(
        """
    class Counter:
      total: int

      def __init__(self) -> None:
        self.name: str = "x"

      def read(self) -> None:
        a = self.total
        b = self.name
        c = self.missing
    """,
    )
    assert [(o.name, o.fix, o.unsafe) for o in check_source(source, checks=Checks(all_scopes=True))] == [
        ("a", "int", False),
        ("b", "str", False),
        ("c", None, False),
    ]


def test_a_nested_functions_self_is_not_typed() -> None:
    """A function nested in a method isn't itself a method: its closed-over `self` isn't typed."""
    source: str = textwrap.dedent(
        """
    class C:
      x: int

      def method(self) -> None:
        def helper() -> None:
          a = self.x
        helper()
    """,
    )
    assert [(o.name, o.fix) for o in check_source(source)] == [("a", None)]


def test_a_classmethods_cls_is_not_typed_as_self() -> None:
    """Only a `self`-named first parameter is typed as the class; `cls` (classmethods) isn't."""
    source: str = textwrap.dedent(
        """
    class C:
      x: int

      @classmethod
      def make(cls) -> "C":
        return cls()

      @classmethod
      def read(cls) -> None:
        a = cls.x
    """,
    )
    assert [(o.name, o.fix) for o in check_source(source)] == [("a", None)]


@pytest.mark.parametrize(
    ("param", "call", "fix"),
    [
        ("s: str", "s.strip()", "str"),
        ("s: str", "s.split(',')", "list[str]"),
        ("s: str", "s.startswith('x')", "bool"),
        ("s: str", "s.count('x')", "int"),
        ("s: str", "s.encode()", "bytes"),
        ("b: bytes", "b.decode()", "str"),
        ("b: bytes", "b.hex()", "str"),
        ("b: bytes", "b.strip()", "bytes"),
        ("s: str", "s.unknown_method()", None),
        ("n: int", "n.bit_length()", None),  # `int` isn't in `_METHOD_RETURNS`
    ],
)
def test_fixes_infer_a_typed_locals_method_call(param: str, call: str, fix: str | None) -> None:
    """A `str`/`bytes` method with a fixed return type, called on an already-typed local, offers it."""
    source: str = f"def f({param}) -> None:\n  x = {call}\n"
    assert [(o.name, o.fix) for o in check_source(source)] == [("x", fix)]


def test_a_method_call_on_a_guessed_fix_is_not_offered() -> None:
    """A method call on an unsafely-fixed local (`Box` isn't `str`/`bytes`) offers nothing."""
    source: str = "def f() -> None:\n  a = Box('x')\n  b = a.strip()\n"
    assert [(o.name, o.fix) for o in check_source(source)] == [("a", "Box"), ("b", None)]


def test_annotation_coverage_counts_first_bindings() -> None:
    """Coverage counts the first bindings the rules cover; typed ones, type comments included."""
    source: str = textwrap.dedent(
        """
    import os
    LIMIT = 1
    __all__ = ["f"]


    def f(items: list[int]) -> None:
      a: int = 1
      b = 2
      b = 3
      b: int = 4  # a later annotation doesn't count it again
      c: str
      for c in []:
        pass
      for d in items:  # type: int
        pass
      for e in items:
        pass
      _ = 4
    """,
    )
    assert annotation_coverage(source) == Coverage(3, 5)  # a, c, d typed; b, e not
    assert annotation_coverage(source, Checks(all_scopes=True)) == Coverage(3, 6)  # LIMIT; not __all__
    assert Coverage(3, 6).percent == HALF
    assert Coverage(0, 0).percent == ALL
