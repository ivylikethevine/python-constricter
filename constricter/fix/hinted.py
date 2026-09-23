# SPDX-License-Identifier: MIT
"""`--infer-with`: a type checker's inferred type (an inlay hint) as a fix, when the file can use it.

Always a guess: a hint is the type the checker gave the value where the name is bound, so it can be
too narrow for a later binding, or too wide for what the code means. It's judged here as text, as
the checker printed it:

- a class object printed `<class 'Point'>` (ty's way) is `type[Point]`;
- a `Literal` is widened to its values' types (`Literal[1, 2]` is `int`, `Literal[Color.RED]` is
  `Color`), and `LiteralString` to `str`, then a union's repeated members dropped;
- anything that isn't an annotation (`Module("os")`, a callable's signature, `Self@C`) is dropped,
  as is a vague one (`Any`, `list[Unknown]`), a bare `None`, one nested as deep as LVA006 reports,
  or a tuple as long as LVA011 does;
- every name in it must be one the file can use: a builtin, a name the module binds at its top
  level (before the binding, in a module body, where the annotation is evaluated), or a class the
  checker prints by its bare name from a module `ImportPlan.spell` can import (`Callable`,
  `Iterator`, `Path`, `deque`, ...). Anything else, it can't be sure what the name means.
"""

import ast
import builtins
import re
from typing import Final

from constricter.fix.known import ImportPlan, Inference, Known
from constricter.rules.annotations import ABSTRACT, depth, is_vague, length

KIND: Final = "checker"  # the fix kind, and what the guess rests on
_LITERAL: Final = "Literal"
_NONE: Final = "None"
_BUILTINS: Final = frozenset(dir(builtins))
# `collections.abc`'s classes, which a checker prints bare (not `Set`: that's `AbstractSet` to it).
_ABSTRACT: Final = sorted(ABSTRACT | {"Hashable", "MappingView", "Sized"})
# Classes a checker prints by their bare names, and where each is from.
WELL_KNOWN: Final = {
    **{name: f"collections.abc.{name}" for name in _ABSTRACT},
    **{
        name: f"collections.{name}" for name in ("ChainMap", "Counter", "OrderedDict", "defaultdict", "deque")
    },
    **{name: f"re.{name}" for name in ("Match", "Pattern")},
    **{name: f"pathlib.{name}" for name in ("Path", "PosixPath", "PurePath", "WindowsPath")},
    **{
        name: f"io.{name}"
        for name in ("BufferedRandom", "BufferedReader", "BufferedWriter", "BytesIO", "FileIO", "StringIO")
    },
    **{name: f"datetime.{name}" for name in ("date", "datetime", "time", "timedelta", "timezone")},
    **{name: f"subprocess.{name}" for name in ("CompletedProcess", "Popen")},
    "ArgumentParser": "argparse.ArgumentParser",
    "Decimal": "decimal.Decimal",
    "Fraction": "fractions.Fraction",
    "Logger": "logging.Logger",
    "Namespace": "argparse.Namespace",
    "UUID": "uuid.UUID",
    "stat_result": "os.stat_result",
}
# Nodes an annotation is made of: names, attributes, subscripts and their parts, and unions.
_ANNOTATION_NODES: Final = (
    ast.Name,
    ast.Attribute,
    ast.Subscript,
    ast.Tuple,
    ast.List,
    ast.Constant,
    ast.BinOp,
    ast.BitOr,
    ast.Load,
)
_WIDER: Final = {"LiteralString": "str"}
# ty prints a class object as `<class 'Point'>`: that's `type[Point]`.
_CLASS_OBJECT: Final = re.compile(r"<class '(\w+)'>")
_DISCARD: Final = "_"


def hinted(text: str, checker: str, known: Known, *, nesting: int, before: int | None) -> Inference | None:
    """Judge `checker`'s hint `text` as a fix for a binding (in a module body, on line `before`).

    Returns:
      The inference, spelled as the file can (an import added if it must be), or `None`.

    """
    plan: ImportPlan | None = known.names.plan
    try:
        parsed: ast.expr = ast.parse(_CLASS_OBJECT.sub(r"type[\1]", text), mode="eval").body
    except SyntaxError:
        return None
    root: ast.expr | None = _widened(parsed)
    if plan is None or root is None or not _annotation(root) or not _fits(root, nesting, known.max_length):
        return None
    names: set[str] = {node.id for node in ast.walk(root) if isinstance(node, ast.Name)}
    usable: set[str] = {name for name in names if _usable(name, plan, before)}
    if names - usable - WELL_KNOWN.keys():
        return None
    spelled: dict[str, str] = {}
    name: str
    for name in sorted(names - usable):
        found: str | None
        if (found := plan.spell(WELL_KNOWN[name])) is None:
            return None
        spelled[name] = found
    # The annotation holds no strings (its only constants are `None` and `...`): a name is a word
    # that isn't an attribute's.
    annotation: str = re.sub(
        r"(?<![\w.])(\w+)",
        lambda word: spelled.get(word[1], word[1]),
        ast.unparse(root),
    )
    return Inference(annotation, f"{checker}'s inferred type", frozenset({KIND}))


def _annotation(root: ast.expr) -> bool:
    """Check that an expression is an annotation, and says something: not a bare `None`.

    Names, attributes, subscripts and unions, whose only constants are `None` and `...`: not a call
    (`Module("os")`), a signature, or a string.

    Returns:
      Whether it is.

    """
    return (
        all(isinstance(node, _ANNOTATION_NODES) for node in ast.walk(root))
        and all(node.value in {None, Ellipsis} for node in ast.walk(root) if isinstance(node, ast.Constant))
        and not (isinstance(root, ast.Constant) and root.value is None)
    )


def _fits(root: ast.expr, nesting: int, max_length: int) -> bool:
    """Check the rules accept an annotation: not vague (LVA005), too deep (LVA006) or long (LVA011).

    Returns:
      Whether it is.

    """
    return not is_vague(root) and depth(root) < nesting and length(root) <= max_length


def _usable(name: str, plan: ImportPlan, before: int | None) -> bool:
    """Check whether the annotation can use `name` as it is: the module binds it, or it's a builtin.

    In a module body (`before`, the binding's line), the module must bind it earlier: the
    annotation is evaluated there.

    Returns:
      Whether it can.

    """
    if name == _DISCARD:  # gettext's, or a throwaway: never a class the checker means
        return False
    if name in plan.defined:
        return before is None or plan.defined[name] < before
    return name in _BUILTINS


def _widened(node: ast.expr) -> ast.expr | None:
    """Widen every `Literal` in an annotation to its values' types, and a union's repeats away.

    Returns:
      The annotation, or `None` if a `Literal` holds something that isn't a plain value.

    """
    name: str
    value: ast.expr
    inner: ast.expr
    elements: list[ast.expr]
    match node:
        case ast.Subscript(value=ast.Name(id=name), slice=inner) if name == _LITERAL:
            members: list[ast.expr] = inner.elts if isinstance(inner, ast.Tuple) else [inner]
            return _union([_literal_type(member) for member in members])
        case ast.BinOp(op=ast.BitOr()):
            return _union([_widened(member) for member in _members(node)])
        case ast.Subscript(value=value, slice=inner):
            widened: ast.expr | None = _widened(inner)
            return None if widened is None else ast.Subscript(value, widened)
        case ast.Tuple(elts=elements) | ast.List(elts=elements):
            parts: list[ast.expr | None] = [_widened(element) for element in elements]
            kept: list[ast.expr] = [part for part in parts if part is not None]
            rebuilt: ast.expr = ast.Tuple(kept) if isinstance(node, ast.Tuple) else ast.List(kept)
            return rebuilt if len(kept) == len(parts) else None
        case ast.Name(id=name):
            return ast.Name(_WIDER.get(name, name))
        case _:
            return node


def _literal_type(member: ast.expr) -> ast.expr | None:
    """Type one `Literal` value: `1` is `int`, `-1` too, `"a"` is `str`, `Color.RED` is `Color`.

    Returns:
      Its type, or `None` for anything else.

    """
    owner: ast.expr
    value: bool | int | str | bytes
    match member:
        case ast.Constant(value=None):
            return member
        case ast.Constant(value=bool() | int() | str() | bytes() as value):
            return ast.Name(type(value).__name__)
        case ast.UnaryOp(op=ast.USub(), operand=ast.Constant(value=int())):
            return ast.Name("int")
        case ast.Attribute(value=owner):
            return owner
        case _:
            return None


def _members(node: ast.expr) -> list[ast.expr]:
    """Flatten a union (`A | B | C`) into its members.

    Returns:
      Them, in order.

    """
    left: ast.expr
    right: ast.expr
    match node:
        case ast.BinOp(left=left, op=ast.BitOr(), right=right):
            return [*_members(left), *_members(right)]
        case _:
            return [node]


def _union(members: list[ast.expr | None]) -> ast.expr | None:
    """Join members into a union, each once, in order (`None` last, as it's conventionally written).

    Returns:
      The union (a single member alone), or `None` if any member is.

    """
    seen: dict[str, ast.expr] = {}
    member: ast.expr | None
    for member in members:
        if member is None:
            return None
        part: ast.expr
        for part in _members(member):
            _ = seen.setdefault(ast.unparse(part), part)
    ordered: list[ast.expr] = sorted(seen.values(), key=lambda part: ast.unparse(part) == _NONE)
    union: ast.expr = ordered[0]
    for member in ordered[1:]:
        union = ast.BinOp(union, ast.BitOr(), member)
    return union
