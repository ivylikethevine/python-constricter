# SPDX-License-Identifier: MIT
"""The rules themselves (constricter.checker): what they report and what they exempt."""

import ast
import textwrap
from pathlib import Path

import pytest

from constricter import (
  COMMENT_TYPED_TARGET,
  LEVELS,
  UNANNOTATED,
  UNTYPED_TARGET,
  Level,
  Offence,
  check_source,
  check_tree,
)

EXEMPT = """
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
    fh: object
    async with open(os.devnull) as fh:
        pass
    while (n := n - 1) > 0:
        pass
    m: re.Match[str] | None
    assert (m := re.match("x", joined)) or True
    type Alias = list[int]
    square: object = lambda v: (w := v * v)
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

OFFENDING = """
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

X_MESSAGE = "local variable 'x' is not annotated where it's first bound"


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
  """The package and its tests pass every code."""
  package: Path = Path(__file__).resolve().parents[1] / "src" / "constricter"
  sources: list[Path] = sorted(package.glob("*.py")) + sorted(Path(__file__).parent.glob("*.py"))
  assert package / "checker.py" in sources
  offences: list[str] = [
    f"{p}:{o.line}: {o.code} {o.name}" for p in sources for o in check_source(p.read_text(encoding="utf-8"))
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
        """
  )
  assert [o.name for o in check_source(source)] == ["a", "fh"]
  assert not check_source(source, type_comments=True)


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
  assert [Offence(1, 0, "x", code).message for code in (UNTYPED_TARGET, COMMENT_TYPED_TARGET)] == [
    "for/match variable 'x' is untyped; declare it before the statement",
    "for variable 'x' is typed only by a type comment; declare it before the loop",
  ]


@pytest.mark.parametrize(
  ("level", "errors"),
  [
    (Level.RELAXED, set[str]()),
    (Level.STRICT, {UNANNOTATED}),
    (Level.CONSTRICT, {UNANNOTATED, UNTYPED_TARGET}),
    (Level.SUFFOCATE, {UNANNOTATED, UNTYPED_TARGET, COMMENT_TYPED_TARGET}),
  ],
)
def test_levels(level: Level, errors: set[str]) -> None:
  """Each level makes one more code an error; the rest are warnings."""
  codes: tuple[str, ...] = (UNANNOTATED, UNTYPED_TARGET, COMMENT_TYPED_TARGET)
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
    """
  )
  assert [(o.line, o.col, o.name) for o in check_source(source)] == [(4, 20, "rest"), (8, 8, "more")]
  tree: ast.Module = ast.parse(source)
  assert [(o.line, o.col) for o in check_tree(tree)] == [(4, 9), (6, 9)]
