# SPDX-License-Identifier: MIT
"""The rules: every local variable is typed where it's first bound (see README)."""

import ast
import re
from collections import deque
from collections.abc import Iterator, Sequence
from dataclasses import dataclass
from enum import IntEnum
from typing import Final

UNANNOTATED: Final = "LVA001"
UNTYPED_TARGET: Final = "LVA002"
COMMENT_TYPED_TARGET: Final = "LVA003"
UNANNOTATED_MEMBER: Final = "LVA004"
MESSAGES: dict[str, str] = {
  UNANNOTATED: "local variable {name} is not annotated where it's first bound",
  UNTYPED_TARGET: "for/match variable {name} is untyped; declare it before the statement",
  COMMENT_TYPED_TARGET: "for variable {name} is typed only by a type comment; declare it before the loop",
  UNANNOTATED_MEMBER: "module or class variable {name} is not annotated where it's first bound",
}

type _FunctionDef = ast.FunctionDef | ast.AsyncFunctionDef
_FUNCTION_DEFS: tuple[type[ast.FunctionDef], type[ast.AsyncFunctionDef]] = (
  ast.FunctionDef,
  ast.AsyncFunctionDef,
)
_FUTURE: Final = "__future__"
# `from __future__` features only code that also runs on Python 2 imports: its type comments count.
_PYTHON2_FUTURES: frozenset[str] = frozenset(
  {
    "nested_scopes",
    "generators",
    "division",
    "absolute_import",
    "with_statement",
    "print_function",
    "unicode_literals",
  }
)


class Level(IntEnum):
  """How strict: each level makes one more code an error rather than a warning."""

  RELAXED = 0
  STRICT = 1
  CONSTRICT = 2
  SUFFOCATE = 3


# Each level by name and by number, as the options take it.
LEVELS: dict[str, Level] = {key: level for level in Level for key in (level.name.lower(), str(level.value))}
_ERROR_FROM: dict[str, Level] = {
  UNANNOTATED: Level.STRICT,
  UNTYPED_TARGET: Level.CONSTRICT,
  COMMENT_TYPED_TARGET: Level.SUFFOCATE,
  UNANNOTATED_MEMBER: Level.STRICT,
}


@dataclass(frozen=True, order=True)
class Offence:
  """One untyped first binding; `col` is 0-based."""

  line: int
  col: int
  name: str
  code: str = UNANNOTATED

  @property
  def message(self) -> str:
    """The report text."""
    return MESSAGES[self.code].format(name=repr(self.name))

  def is_error(self, level: Level) -> bool:
    """Whether `level` makes this an error rather than a warning."""
    return level >= _ERROR_FROM[self.code]


def check_source(
  source: str | bytes, filename: str = "<unknown>", *, type_comments: bool = False, all_scopes: bool = False
) -> list[Offence]:
  """Return the offences in `source`, sorted. Raises `SyntaxError`.

  With `type_comments`, `x = 1  # type: int` counts as annotated; with `all_scopes`, module and
  class bodies are checked too (LVA004).
  """
  tree: ast.Module
  try:
    tree = ast.parse(source, filename, type_comments=True)
  except SyntaxError:  # a misplaced `# type:` comment, or a real error raised again here
    tree = ast.parse(source, filename)
  text: str = source.decode("utf-8") if isinstance(source, bytes) else source
  return check_tree(tree, type_comments=type_comments, all_scopes=all_scopes, lines=text.splitlines())


def check_tree(
  tree: ast.Module, *, type_comments: bool = False, all_scopes: bool = False, lines: Sequence[str] = ()
) -> list[Offence]:
  """Return the offences in a parsed module, sorted.

  `# type:` comments are seen only if it was parsed with `type_comments=True`; they count for `=`
  and `with` too in a module written to run on Python 2. With its source `lines`, a `**rest`
  capture is reported at its name rather than at its pattern's start.
  """
  type_comments = type_comments or _python2_compatible(tree)
  functions: list[_FunctionDef] = []
  _collect_functions(tree.body, functions)
  offences: list[Offence] = []
  while functions:
    offences += _check_function(functions.pop(), functions, type_comments=type_comments, lines=lines)
  if all_scopes:
    offences += _check_bodies(tree, type_comments=type_comments, lines=lines)
  return sorted(offences)


def _python2_compatible(tree: ast.Module) -> bool:
  """Whether a `from __future__` import only Python 2 needs marks the module as written for it."""
  return any(
    isinstance(stmt, ast.ImportFrom)
    and stmt.module == _FUTURE
    and any(alias.name in _PYTHON2_FUTURES for alias in stmt.names)
    for stmt in tree.body
  )


def _check_bodies(tree: ast.Module, *, type_comments: bool, lines: Sequence[str]) -> list[Offence]:
  """Return the offences in the module body and every class body but an enum's (LVA004).

  Dunder names (`__all__`, `__slots__`) are exempt: annotating one can change what it means.
  """
  bodies: list[list[ast.stmt]] = [tree.body]
  bodies += [node.body for node in ast.walk(tree) if isinstance(node, ast.ClassDef) and not _is_enum(node)]
  offences: list[Offence] = []
  body: list[ast.stmt]
  for body in bodies:
    scope: _Scope = _Scope(
      {"_"}, [], type_comments=type_comments, lines=lines, unannotated=UNANNOTATED_MEMBER
    )
    stmt: ast.stmt
    for stmt in body:
      _visit(scope, stmt)
    offences += [o for o in scope.offences if not (o.name.startswith("__") and o.name.endswith("__"))]
  return offences


def _is_enum(node: ast.ClassDef) -> bool:
  """Whether a base's name ends in `Enum` or `Flag`: enum members mustn't be annotated."""
  base: ast.expr
  name: str
  for base in node.bases:
    match base:
      case ast.Name(id=name) | ast.Attribute(attr=name) if name.endswith(("Enum", "Flag")):
        return True
      case _:
        pass
  return False


def _collect_functions(body: list[ast.stmt], into: list[_FunctionDef]) -> None:
  """Collect functions in a module or class body, through compound statements and classes."""
  stmt: ast.stmt
  for stmt in body:
    if isinstance(stmt, _FUNCTION_DEFS):
      into.append(stmt)
    elif isinstance(stmt, ast.ClassDef):
      _collect_functions(stmt.body, into)
    else:
      _collect_functions(_child_statements(stmt), into)


def _child_statements(stmt: ast.stmt) -> list[ast.stmt]:
  """Return the statements nested directly in `stmt`, in source order."""
  children: list[ast.stmt] = []
  handler: ast.ExceptHandler
  case: ast.match_case
  match stmt:
    case ast.If() | ast.For() | ast.AsyncFor() | ast.While():
      children += stmt.body + stmt.orelse
    case ast.With() | ast.AsyncWith():
      children += stmt.body
    case ast.Try() | ast.TryStar():
      children += stmt.body
      for handler in stmt.handlers:
        children += handler.body
      children += stmt.orelse + stmt.finalbody
    case ast.Match():
      for case in stmt.cases:
        children += case.body
    case _:
      pass
  return children


def _expressions(stmt: ast.stmt) -> Iterator[ast.AST]:
  """Yield the parts of `stmt` that aren't statements: where a `:=` can bind."""
  child: ast.AST
  for child in ast.iter_child_nodes(stmt):
    if isinstance(child, ast.match_case | ast.ExceptHandler):
      yield from (part for part in ast.iter_child_nodes(child) if not isinstance(part, ast.stmt))
    elif not isinstance(child, ast.stmt):
      yield child


def _names(target: ast.expr) -> Iterator[ast.Name]:
  """Yield the plain names an assignment target binds."""
  elements: list[ast.expr]
  element: ast.expr
  value: ast.expr
  match target:
    case ast.Name():
      yield target
    case ast.Tuple(elts=elements) | ast.List(elts=elements):
      for element in elements:
        yield from _names(element)
    case ast.Starred(value=value):
      yield from _names(value)
    case _:
      return


def _captures(pattern: ast.pattern, lines: Sequence[str]) -> Iterator[tuple[str, tuple[int, int]]]:
  """Yield each name a `case` pattern captures, with where it's bound."""
  node: ast.AST
  name: str
  for node in ast.walk(pattern):
    match node:
      case ast.MatchAs(name=str() as name) | ast.MatchStar(name=str() as name):
        yield name, _at(node)
      case ast.MatchMapping(rest=str() as name):
        yield name, _rest_at(node, name, lines)
      case _:
        pass


def _at(node: ast.expr | ast.pattern) -> tuple[int, int]:
  return node.lineno, node.col_offset


def _rest_at(node: ast.MatchMapping, name: str, lines: Sequence[str]) -> tuple[int, int]:
  """Find `**name` in a mapping pattern's source (as `ast`, a byte column); else its start."""
  rest: re.Pattern[bytes] = re.compile(rb"\*\*\s*(" + re.escape(name.encode()) + rb")\b")
  number: int
  found: re.Match[bytes] | None
  for number in range(node.lineno, min(node.end_lineno or node.lineno, len(lines)) + 1):
    if found := rest.search(lines[number - 1].encode(), node.col_offset if number == node.lineno else 0):
      return number, found.start(1)
  return _at(node)


class _Scope:
  """One function body: names bound so far and offences found."""

  def __init__(
    self,
    declared: set[str],
    nested: list[_FunctionDef],
    *,
    type_comments: bool,
    lines: Sequence[str],
    unannotated: str = UNANNOTATED,
  ) -> None:
    self.declared: set[str] = declared
    self.unannotated_code: str = unannotated
    self.nested: list[_FunctionDef] = nested
    self.type_comments: bool = type_comments
    self.lines: Sequence[str] = lines
    self.offences: list[Offence] = []

  def bind(self, name: str, at: tuple[int, int], code: str | None) -> None:
    """Bind `name`; unless it's already bound, report `code` at `(line, col)` (`None`: typed)."""
    if name not in self.declared:
      self.declared.add(name)
      if code is not None:
        self.offences.append(Offence(*at, name, code))

  def walrus(self, node: ast.AST) -> None:
    """Bind `:=` targets in an expression, comprehensions included, lambdas excluded."""
    pending: deque[ast.AST] = deque([node])
    current: ast.AST
    while pending:
      current = pending.popleft()
      if isinstance(current, ast.Lambda):
        continue
      if isinstance(current, ast.NamedExpr):
        self.bind(current.target.id, _at(current.target), self.unannotated_code)
      pending.extend(ast.iter_child_nodes(current))

  def unannotated(self, type_comment: str | None) -> str | None:
    """Return the code for an `=` or `with` binding: `None` if a counted type comment types it."""
    return None if type_comment is not None and self.type_comments else self.unannotated_code


def _check_function(
  func: _FunctionDef, functions: list[_FunctionDef], *, type_comments: bool, lines: Sequence[str]
) -> list[Offence]:
  """Return one function's offences; nested functions are queued onto `functions`."""
  args: ast.arguments = func.args
  params: set[str] = {a.arg for a in (*args.posonlyargs, *args.args, *args.kwonlyargs)}
  params.update(extra.arg for extra in (args.vararg, args.kwarg) if extra is not None)
  # `_` is a discard.
  scope: _Scope = _Scope(params | {"_"}, functions, type_comments=type_comments, lines=lines)
  stmt: ast.stmt
  for stmt in func.body:
    _visit(scope, stmt)
  return scope.offences


def _visit(scope: _Scope, stmt: ast.stmt) -> None:
  """Bind the names `stmt` binds, as Python would, then visit its nested statements."""
  part: ast.AST
  for part in _expressions(stmt):
    scope.walrus(part)
  _declare(scope, stmt)
  _bind(scope, stmt)
  child: ast.stmt
  for child in _child_statements(stmt):
    _visit(scope, child)


def _declare(scope: _Scope, stmt: ast.stmt) -> None:
  """Bind the names `stmt` binds that need no annotation, or carry their own."""
  aliases: list[ast.alias]
  names: list[str]
  name: str
  handlers: list[ast.ExceptHandler]
  match stmt:
    case ast.FunctionDef() | ast.AsyncFunctionDef():
      scope.declared.add(stmt.name)
      scope.nested.append(stmt)  # its body is its own scope
    case ast.ClassDef():
      scope.declared.add(stmt.name)
      _collect_functions(stmt.body, scope.nested)  # methods of a class defined in a function
    case ast.Import(names=aliases) | ast.ImportFrom(names=aliases):
      scope.declared.update((alias.asname or alias.name).split(".")[0] for alias in aliases)
    case ast.Global(names=names) | ast.Nonlocal(names=names):
      scope.declared.update(names)
    case ast.AnnAssign(target=ast.Name(id=name)) | ast.TypeAlias(name=ast.Name(id=name)):
      scope.declared.add(name)
    case ast.Try(handlers=handlers) | ast.TryStar(handlers=handlers):
      scope.declared.update(handler.name for handler in handlers if handler.name)
    case _:
      pass


def _bind(scope: _Scope, stmt: ast.stmt) -> None:
  """Bind the names `stmt` binds that need typing, reporting the untyped ones."""
  targets: list[ast.expr]
  target: ast.expr
  items: list[ast.withitem]
  comment: str | None
  cases: list[ast.match_case]
  match stmt:
    case ast.Assign(targets=targets, type_comment=comment):
      _bind_targets(scope, targets, scope.unannotated(comment))
    case ast.With(items=items, type_comment=comment) | ast.AsyncWith(items=items, type_comment=comment):
      _bind_targets(scope, [i.optional_vars for i in items if i.optional_vars], scope.unannotated(comment))
    case ast.For(target=target, type_comment=comment) | ast.AsyncFor(target=target, type_comment=comment):
      _bind_targets(scope, [target], UNTYPED_TARGET if comment is None else COMMENT_TYPED_TARGET)
    case ast.Match(cases=cases):
      _bind_captures(scope, cases)
    case _:
      pass


def _bind_targets(scope: _Scope, targets: list[ast.expr], code: str | None) -> None:
  """Bind every name in `targets`, reporting `code` for each first binding."""
  target: ast.expr
  name: ast.Name
  for target in targets:
    for name in _names(target):
      scope.bind(name.id, _at(name), code)


def _bind_captures(scope: _Scope, cases: list[ast.match_case]) -> None:
  """Bind every name the `case` patterns capture: LVA002 unless declared first."""
  case: ast.match_case
  name: str
  at: tuple[int, int]
  for case in cases:
    for name, at in _captures(case.pattern, scope.lines):
      scope.bind(name, at, UNTYPED_TARGET)
