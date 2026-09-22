# SPDX-License-Identifier: MIT
"""What an annotation says: vague parts (LVA005), nesting depth (LVA006), and inferable values (`--fix`)."""

import ast
from typing import TYPE_CHECKING, Final

if TYPE_CHECKING:
  from types import EllipsisType

_VAGUE: Final = frozenset({"Any", "object"})
# Generics that say little without their parameters.
_GENERICS: Final = frozenset(
  {
    "AbstractSet",
    "AsyncGenerator",
    "AsyncIterable",
    "AsyncIterator",
    "Awaitable",
    "Callable",
    "ChainMap",
    "Collection",
    "Container",
    "Coroutine",
    "Counter",
    "DefaultDict",
    "Deque",
    "Dict",
    "FrozenSet",
    "Generator",
    "ItemsView",
    "Iterable",
    "Iterator",
    "KeysView",
    "List",
    "Mapping",
    "Match",
    "MutableMapping",
    "MutableSequence",
    "MutableSet",
    "OrderedDict",
    "Pattern",
    "Reversible",
    "Sequence",
    "Set",
    "Tuple",
    "Type",
    "ValuesView",
    "defaultdict",
    "deque",
    "dict",
    "frozenset",
    "list",
    "set",
    "tuple",
    "type",
  }
)
# Calls that return a class or a special form, not an instance of what they're named.
_FACTORIES: Final = frozenset(
  {
    "Enum",
    "Flag",
    "IntEnum",
    "IntFlag",
    "NamedTuple",
    "NewType",
    "ParamSpec",
    "StrEnum",
    "TypeVar",
    "TypeVarTuple",
    "TypedDict",
  }
)
_NUMBERS: Final = (int, float, complex)


def _parsed(annotation: ast.expr) -> ast.expr:
  """Return a string annotation's expression, or the annotation itself."""
  if isinstance(annotation, ast.Constant) and isinstance(annotation.value, str):
    try:
      return ast.parse(annotation.value, mode="eval").body
    except SyntaxError:
      return annotation
  return annotation


def _name(node: ast.AST) -> str:
  name: str
  match node:
    case ast.Name(id=name) | ast.Attribute(attr=name):
      return name
    case _:
      return ""


def is_vague(annotation: ast.expr) -> bool:
  """Whether `annotation` has `Any`, `object` or a generic without its parameters in it."""
  root: ast.expr = _parsed(annotation)
  subscripted: set[int] = {id(node.value) for node in ast.walk(root) if isinstance(node, ast.Subscript)}
  node: ast.AST
  for node in ast.walk(root):
    name: str = _name(node)
    if name in _VAGUE or (name in _GENERICS and id(node) not in subscripted):
      return True
  return False


def depth(annotation: ast.expr) -> int:
  """How deeply `annotation`'s subscripts nest: `dict[str, list[int]]` is 2."""
  node: ast.expr = _parsed(annotation)
  inner: ast.expr
  parts: list[ast.expr]
  left: ast.expr
  right: ast.expr
  match node:
    case ast.Subscript(slice=inner):
      return 1 + depth(inner)
    case ast.Tuple(elts=parts) | ast.List(elts=parts):
      return max((depth(part) for part in parts), default=0)
    case ast.BinOp(left=left, right=right):
      return max(depth(left), depth(right))
    case _:
      return 0


def inferred(value: ast.expr) -> str | None:
  """Return the annotation `value` makes unambiguous: a literal's type, or a class it constructs."""
  constant: str | bytes | bool | int | float | complex | EllipsisType | None
  func: ast.expr
  match value:
    case ast.Constant(value=bool() | int() | float() | complex() | str() | bytes() as constant):
      return type(constant).__name__
    case ast.UnaryOp(op=ast.USub() | ast.UAdd(), operand=ast.Constant(value=constant)) if isinstance(
      constant, _NUMBERS
    ) and not isinstance(constant, bool):
      return type(constant).__name__
    case ast.JoinedStr():
      return "str"
    case ast.Call(func=ast.Name() | ast.Attribute() as func) if _constructs(_name(func)):
      return ast.unparse(func)
    case _:
      return None


def _constructs(name: str) -> bool:
  """Whether a call to `name` is, by its capitalised name, a class's constructor worth annotating."""
  return name[:1].isupper() and name not in _FACTORIES and name not in _GENERICS
