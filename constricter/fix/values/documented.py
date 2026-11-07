"""`--fix` for calls to unannotated functions whose docstrings name their return type (a guess).

A numpydoc `Returns` section, a Google-style `Returns:` whose first line names the type
(`bool: Whether ...`) or a Sphinx `:rtype:` field. What it names: a builtin scalar (`int`,
`float`, `bool`, `str`, `bytes`, `complex`, or `integer`, `boolean`, `string`); a class the module
binds by that name, its own or one it imports (`DataFrame`, `pd.DataFrame`), not a generic one,
whose arguments a docstring doesn't give; a `list`, `set`, `frozenset` or `tuple` of one of those
(`list of int`, `tuple of str`); an annotation of those (`list[str]`, `dict[str, Graph]`); or
several of those, `or` or `|` between (`int or float`, `Graph or None`), but no class among other
types than `None`: `Series or DataFrame` is the receiver's own kind, which a checker given the
union holds against each caller using one's members. A numpydoc section of
several entries is a tuple of their types, where every `return` is a tuple display of as many.
Only where every `return` the function has gives a value of no known type or one the named type
takes (`int` for a `float`), none without `None` named where one gives `None`, no `int` or `bool`
where one is a true division (`a / b`), and no number in a module importing numpy, whose scalars
no checker takes for one: a docstring may be stale, so its type is a guess (`documented`).
"""

import ast
import re
from collections.abc import Callable, Iterable
from functools import partial
from typing import Final

from constricter.fix.values.shapes import is_none
from constricter.source.flow import members
from constricter.source.syntax import FunctionDef, own_returns

KIND: Final = "documented"  # the guessing mechanism (`FIX_KINDS`)
_SCALARS: Final = {
    "int": "int",
    "integer": "int",
    "float": "float",
    "bool": "bool",
    "boolean": "bool",
    "str": "str",
    "string": "str",
    "bytes": "bytes",
    "complex": "complex",
}
# What a value of each type may be where that's the type named: a `bool` is an `int`, an `int` a `float`.
_TAKES: Final = {
    "int": frozenset({"int", "bool"}),
    "float": frozenset({"float", "int", "bool"}),
    "complex": frozenset({"complex", "float", "int", "bool"}),
}
_NONE: Final = "None"
_INTEGERS: Final = frozenset({"int", "bool"})  # what a true division (`/`) never gives
_NUMBERS: Final = frozenset({"int", "float", "complex", "bool"})  # what a docstring names numpy's scalars
_NUMPY: Final = "numpy"
_ELLIPSIS: Final = "..."
_TUPLE: Final = "tuple"
_OPEN: Final = "["  # a subscript's, outside of which `or`, `,` and `|` split alternatives
_CLOSE: Final = "]"
# A builtin container named with its elements (`list of int`), and how many type arguments each takes.
_OF: Final = re.compile(r"(?P<container>list|set|frozenset|tuple)\s+of\s+(?P<element>[A-Za-z_][\w.]*)")
_CONTAINERS: Final = {"list": 1, "set": 1, "frozenset": 1, "tuple": 0, "dict": 2, "type": 1}  # 0: any
_HOMOGENEOUS: Final = 2  # `tuple[T, ...]`'s arguments
_ALTERNATIVES: Final = re.compile(r"\s*,\s*or\s+|\s*,\s*|\s+or\s+|\s*\|\s*")
_DOTTED: Final = re.compile(r"[A-Za-z_]\w*(?:\.[A-Za-z_]\w*)*")
_NUMPYDOC: Final = re.compile(
    r"^(?P<indent>[ \t]*)Returns[ \t]*\n[ \t]*-{3,}[ \t]*\n(?P<body>(?:.*\n?)*)",
    re.MULTILINE,
)
_GOOGLE: Final = re.compile(r"^[ \t]*Returns?:[ \t]*\n[ \t]+(?P<type>[\w .,|\[\]]+?)[ \t]*:", re.MULTILINE)
_SPHINX: Final = re.compile(r"^[ \t]*:rtype:[ \t]*(?P<type>[^\n]+?)[ \t]*$", re.MULTILINE)
_ENTRY: Final = re.compile(r"(?:\w+[ \t]*:[ \t]*)?(?P<type>[^\n:]+?)[ \t]*")


def _no_class(_: str) -> bool:
    """Tell of no class: a docstring's names left unread.

    Returns:
      `False`.

    """
    return False


def documented(
    func: FunctionDef,
    returned: Iterable[str | None],
    *,
    numpy: bool = False,
    classes: Callable[[str], bool] = _no_class,
) -> str | None:
    """Type a function by its docstring's named return, where its `return`s allow it.

    `returned`: each `return`'s type, `None` where it isn't known; `numpy`: its module imports numpy
    (see `imports_numpy`), so a number it names may be numpy's (`np.int64`); `classes`: whether the
    module may write a name as a class (see `writable`).

    Returns:
      The type (`int`, `str | None`, `DataFrame`), or `None`: no docstring, no return named, one
      that isn't a type read here, a number where `numpy`, or a `return` of a value it doesn't take.

    """
    docstring: str | None = ast.get_docstring(func)
    named: str | None
    if docstring is None or (named := _named(docstring, classes, func)) is None:
        return None
    parts: frozenset[str] = members(named) or frozenset({named})
    if (_INTEGERS & parts and _divides(func)) or (numpy and _NUMBERS & _names(named)):
        return None
    if len(parts - {_NONE}) > 1 and any(classes(part) for part in parts):  # which is the receiver's to decide
        return None
    if _NONE not in parts and _gives_none(func):
        return None
    return named if all(each is None or _takes(parts, each) for each in returned) else None


def writable(
    module: ast.Module,
    named: tuple[Callable[[str], bool], ...] = (),
    generic: tuple[Callable[[str], bool], ...] = (),
) -> Callable[[str], bool]:
    """Tell what the module may write as a class: its own top-level classes, defined once, or `named`'s.

    `named`: whether it names another class so (`Known.classes`, `LibraryNames.written`); `generic`:
    whether one is generic, whose arguments a docstring doesn't give, as its own are that have a
    subscripted base or type parameters.

    Returns:
      Whether a name is one.

    """
    counted: dict[str, int] = {}
    unwritten: set[str] = set()
    node: ast.stmt
    for node in module.body:
        if isinstance(node, ast.ClassDef):
            counted[node.name] = counted.get(node.name, 0) + 1
            if getattr(node, "type_params", None) or any(
                isinstance(base, ast.Subscript) for base in node.bases
            ):
                unwritten.add(node.name)
    own: frozenset[str] = frozenset(name for name, count in counted.items() if count == 1)
    return partial(_writes, (own.__contains__, *named), (frozenset(unwritten).__contains__, *generic))


def _writes(
    named: tuple[Callable[[str], bool], ...],
    generic: tuple[Callable[[str], bool], ...],
    name: str,
) -> bool:
    """Check that `name` is a class `named` tells of, and none `generic` does (see `writable`).

    Returns:
      Whether it is.

    """
    return any(each(name) for each in named) and not any(each(name) for each in generic)


def imports_numpy(module: ast.Module) -> bool:
    """Check whether a module imports numpy or a submodule, at its top level or in a top-level `if` or `try`.

    Returns:
      Whether it does.

    """
    statements: list[ast.stmt] = [*module.body]
    statement: ast.stmt
    for statement in module.body:
        if isinstance(statement, ast.If | ast.Try):
            statements.extend((*statement.body, *statement.orelse))
    return any(
        (isinstance(each, ast.Import) and any(alias.name.partition(".")[0] == _NUMPY for alias in each.names))
        or (
            isinstance(each, ast.ImportFrom)
            and not each.level
            and (each.module or "").partition(".")[0] == _NUMPY
        )
        for each in statements
    )


def _takes(parts: frozenset[str], given: str) -> bool:
    """Check that a type of `parts` (its union's members) takes a `return`'s known type, each of its members.

    Returns:
      Whether it does: each member named, or one a named scalar takes (`int` for a `float`).

    """
    return all(
        each in parts or any(each in _TAKES.get(part, ()) for part in parts)
        for each in members(given) or frozenset({given})
    )


def _names(annotation: str) -> frozenset[str]:
    """Name the names an annotation is written with, at any depth (`int` in `tuple[int, str]`).

    Returns:
      Them.

    """
    return frozenset(
        node.id for node in ast.walk(ast.parse(annotation, mode="eval")) if isinstance(node, ast.Name)
    )


def _gives_none(func: FunctionDef) -> bool:
    """Check whether a `return` of the function's gives `None`: `return None`, or a bare `return`.

    A recorded `return`'s type is unknown for `None` (no binding's fix is one), so it's read here.

    Returns:
      Whether one does.

    """
    return any(each.value is None or is_none(each.value) for each in own_returns(func.body))


def _divides(func: FunctionDef) -> bool:
    """Check whether a `return` of the function's gives a true division, which no `int` or `bool` is.

    Returns:
      Whether one does.

    """
    returned: list[ast.expr | None] = [each.value for each in own_returns(func.body)]
    return any(isinstance(value, ast.BinOp) and isinstance(value.op, ast.Div) for value in returned)


def _named(docstring: str, classes: Callable[[str], bool], func: FunctionDef) -> str | None:
    """Read the type a docstring names its return as (see the module's docstring).

    Returns:
      It, as an annotation; `None` for none, or a kind of type not read here.

    """
    found: re.Match[str] | None
    if (found := _NUMPYDOC.search(docstring)) is not None:
        entries: list[str] | None = _numpydoc(found.group("body"), found.group("indent"))
        types: list[str | None] = [_annotation(each, classes) for each in entries or ()]
        if not types or None in types:
            return None
        written: list[str] = [each for each in types if each is not None]
        return written[0] if len(written) == 1 else _tuple(written, func)
    if (found := _GOOGLE.search(docstring)) is not None or (found := _SPHINX.search(docstring)) is not None:
        return _annotation(found.group("type"), classes)
    return None


def _tuple(types: list[str], func: FunctionDef) -> str | None:
    """Write a numpydoc section's several entries as a tuple, where every `return` is a display of as many.

    numpydoc lists a tuple's parts as entries, but a docstring may list alternatives so too.

    Returns:
      `tuple[A, B]`, or `None`.

    """
    returned: list[ast.Return] = own_returns(func.body)
    if not returned or not all(
        isinstance(each.value, ast.Tuple)
        and len(each.value.elts) == len(types)
        and not any(isinstance(elt, ast.Starred) for elt in each.value.elts)
        for each in returned
    ):
        return None
    return f"{_TUPLE}[{', '.join(types)}]"


def _numpydoc(body: str, indent: str) -> list[str] | None:
    """Read a numpydoc `Returns` section's entries' types (each one's description indented under it).

    Returns:
      Their texts; `None` where an entry can't be read.

    """
    entries: list[str] = []
    line: str
    for line in body.splitlines():
        if not line.strip():
            continue
        if not line.startswith(indent) or line[len(indent) :].startswith((" ", "\t")):
            if not line.startswith(indent):
                break
            continue  # a description line
        if set(line.strip()) <= {"-"}:  # the next section's underline: its heading was the last entry
            _ = entries.pop()
            break
        entries.append(line[len(indent) :])
    found: list[re.Match[str] | None] = [_ENTRY.fullmatch(each) for each in entries]
    return None if None in found else [each.group("type") for each in found if each is not None]


def _annotation(text: str, classes: Callable[[str], bool]) -> str | None:
    """Write a docstring's type as an annotation (see the module's docstring).

    Returns:
      It, or `None`: a type not read here, or `None` alone.

    """
    words: str = " ".join(text.strip().strip("`").split())
    written: list[str] = []
    alternative: str
    for alternative in _alternatives(words):
        atom: str | None = (
            _subscripted(alternative, classes)
            if _OPEN in alternative
            else _atom(alternative.strip("`"), classes)
        )
        if atom is None:
            return None
        if atom not in written:
            written.append(atom)
    if _NONE in written:  # last, as a checker writes it
        written.remove(_NONE)
        written.append(_NONE)
    return None if not written or written == [_NONE] else " | ".join(written)


def _alternatives(words: str) -> list[str]:
    """Split a docstring's type at each `or`, `,` or `|` outside brackets (`dict[str, int] or None`).

    Returns:
      The alternatives' texts.

    """
    depth: list[int] = []
    level: int = 0
    char: str
    for char in words:
        level -= char == _CLOSE
        depth.append(level)
        level += char == _OPEN
    found: list[str] = []
    start: int = 0
    cut: re.Match[str]
    for cut in _ALTERNATIVES.finditer(words):
        if not depth[cut.start()]:
            found.append(words[start : cut.start()])
            start = cut.end()
    return [*found, words[start:]]


def _atom(text: str, classes: Callable[[str], bool]) -> str | None:
    """Write one alternative of a docstring's type: a scalar, `None`, a class, or a container of one.

    Returns:
      It, or `None`.

    """
    if text.lower() in _SCALARS:
        return _SCALARS[text.lower()]
    if text.lower() == _NONE.lower():
        return _NONE
    if _DOTTED.fullmatch(text):
        return text if classes(text) else None
    found: re.Match[str] | None
    if (found := _OF.fullmatch(text)) is None:
        return None
    element: str = found.group("element")
    written: str | None = _element(element, classes) or (
        _element(element[:-1], classes) if element.endswith("s") else None
    )
    if written is None:
        return None
    container: str = found.group("container")
    return f"{_TUPLE}[{written}, {_ELLIPSIS}]" if container == _TUPLE else f"{container}[{written}]"


def _element(text: str, classes: Callable[[str], bool]) -> str | None:
    """Write a container's element type: a scalar or a class.

    Returns:
      It, or `None`.

    """
    if text.lower() in _SCALARS:
        return _SCALARS[text.lower()]
    return text if _DOTTED.fullmatch(text) and classes(text) else None


def _subscripted(text: str, classes: Callable[[str], bool]) -> str | None:
    """Write a docstring's type given as an annotation (`list[str]`), where each name in it is one read here.

    A builtin container with its arguments, a scalar, `None` or a class; `|` between them.

    Returns:
      It, as `ast` writes it, or `None`.

    """
    try:
        tree: ast.expr = ast.parse(text, mode="eval").body
    except SyntaxError:
        return None
    return ast.unparse(tree) if _readable(tree, classes) else None


def _readable(node: ast.expr, classes: Callable[[str], bool]) -> bool:
    """Check that an annotation's every part is one `_subscripted` reads.

    Returns:
      Whether it is.

    """
    head: str
    inner: ast.expr
    left: ast.expr
    right: ast.expr
    match node:
        case ast.Subscript(value=ast.Name(id=head), slice=inner) if head in _CONTAINERS:
            return _arguments_readable(head, inner.elts if isinstance(inner, ast.Tuple) else [inner], classes)
        case ast.BinOp(left=left, op=ast.BitOr(), right=right):
            return _readable(left, classes) and _readable(right, classes)
        case ast.Constant(value=None):
            return True
        case ast.Name(id=head):
            return head in _SCALARS.values() or classes(head)
        case ast.Attribute():
            return classes(ast.unparse(node))
        case _:
            return False


def _arguments_readable(container: str, arguments: list[ast.expr], classes: Callable[[str], bool]) -> bool:
    """Check a builtin container's type arguments: as many as it takes, each readable (`tuple[T, ...]` too).

    Returns:
      Whether they are.

    """
    if container == _TUPLE and len(arguments) == _HOMOGENEOUS and _is_ellipsis(arguments[1]):
        return _readable(arguments[0], classes)
    wanted: int = _CONTAINERS[container]
    return (not wanted or len(arguments) == wanted) and all(_readable(each, classes) for each in arguments)


def _is_ellipsis(node: ast.expr) -> bool:
    """Check that a node is `...`.

    Returns:
      Whether it is.

    """
    return isinstance(node, ast.Constant) and node.value is Ellipsis
