# SPDX-License-Identifier: MIT
"""`--infer-with`: a type checker's inferred type (an inlay hint) as a fix, when the file can use it.

Always a guess: a hint is the type the checker gave the value where the name is bound, so it can be
too narrow for a later binding, or too wide for what the code means. It's judged here as text, as
the checker printed it:

- a class object printed `<class 'Point'>` (ty's way) is `type[Point]`, a type variable printed with
  its scope (`Model@create_model`) the variable, and an intersection with a truthiness
  (`str & ~AlwaysFalsy`) its other member;
- a `Literal` is widened to its values' types (`Literal[1, 2]` is `int`, `Literal[Color.RED]` is
  `Color`), and `LiteralString` to `str`, then a union's repeated members dropped;
- anything that isn't an annotation (`Module("os")`, a callable's signature, `Self@C`) is dropped,
  as is a vague one (`Any`, `list[Unknown]`), a bare `None`, one nested as deep as LVA006 reports,
  or a tuple as long as LVA011 does;
- a special form alone (`type[Generic]`) is dropped;
- `TypeAlias`, hinted for an alias's assignment, declares a module's alias written as a subscript or
  a union (see `type_alias`), and is dropped anywhere else;
- every name in it must be one the file can use: a builtin, a name the module binds at its top
  level (before the binding, in a module body, where the annotation is evaluated), a class or
  alias it imports under `if TYPE_CHECKING:` or the hint's own edits import (`Offered`: imported
  for type checking alone, as the checker says from where; see `constricter.fix.offers` for which
  are taken), or a class the checker prints by its bare name from a module `ImportPlan.spell` can
  import (`Callable`, `Iterator`, `Path`, `deque`, ...). Anything else, it can't be sure what the
  name means.

A hint with edits is judged as it shows first (`Thing[str]`), then as they'd write it
(`things.Thing[str]`, through a module the file imports).
"""

import ast
import builtins
import re
import sys
from functools import lru_cache
from typing import Final, TypeAlias

from constricter.fix import stdlib
from constricter.fix.known import ImportPlan, Inference, Known, Offered
from constricter.rules.annotations import ABSTRACT, depth, is_vague, length

KIND: Final = "checker"  # the fix kind, and what the guess rests on
_LITERAL: Final = "Literal"
_NONE: Final = "None"
_BUILTINS: Final = frozenset(dir(builtins))
ALIAS: Final = "TypeAlias"  # what a checker hints an alias's assignment as
_ALIAS_ORIGINS: Final = ("typing.TypeAlias", "typing_extensions.TypeAlias")
_CLASS: Final = "type["
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
    ast.Starred,  # `tuple[str, *tuple[str, ...]]`
)
_WIDER: Final = {"LiteralString": "str"}
# `typing`'s special forms, which a checker prints for the form itself (`type[Generic]`, `Annotated`).
_FORMS: Final = frozenset(
    {
        "Annotated",
        "ClassVar",
        "Concatenate",
        "Final",
        "Generic",
        "Literal",
        "NotRequired",
        "Optional",
        "Protocol",
        "ReadOnly",
        "Required",
        "TypeGuard",
        "TypeIs",
        "Union",
        "Unpack",
    },
)
# ty prints a class object as `<class 'Point'>`: that's `type[Point]`.
_CLASS_OBJECT: Final = re.compile(r"<class '(\w+)'>")
# ty prints a type variable with the function or class that declares it: `Model@create_model`.
_SCOPED: Final = re.compile(r"\b(?!Self@)(\w+)@\w+")
# What ty intersects a type with where a truth test narrowed it: `str & ~AlwaysFalsy`.
_TRUTHINESS: Final = frozenset({"AlwaysFalsy", "AlwaysTruthy"})
_DISCARD: Final = "_"
# Each name a hint's edits import: its statement, module and name there (see `_origins`).
_Origins: TypeAlias = dict[str, tuple[str, str, str]]
_STDLIB: Final = sys.stdlib_module_names | {"_typeshed"}  # and the module its stubs alone have
_RELATIVE: Final = "."
_DOT: Final = "."
# How one unbound name of a hint can be written: through a guarded import, or `ImportPlan.spell`.
_OWN: Final = "own"  # the module imports it under `if TYPE_CHECKING:`
_OFFERED: Final = "offered"  # the hint's edits import it
_KNOWN: Final = "known"  # `WELL_KNOWN` says where it's from


def hinted(
    text: str,
    known: Known,
    *,
    nesting: int,
    before: int | None,
    offered: Offered | None = None,
) -> str | None:
    """Judge a checker's hint `text` as a fix for a binding (in a module body, on line `before`).

    `offered`: what the hint's edits would write, judged if `text` is no fix.

    Returns:
      The annotation, spelled as the file can (an import added if it must be), or `None`.

    """
    imports: tuple[str, ...] = () if offered is None else offered.imports
    candidate: str
    for candidate in dict.fromkeys([text] if offered is None else [text, offered.text]):
        annotation: str | None
        if (annotation := _spelled(candidate, known, imports, nesting=nesting, before=before)) is not None:
            return annotation
    return None


def inference(annotation: str, checker: str) -> Inference:
    """Make the fix `checker`'s hint gives, as `hinted` wrote it.

    Returns:
      It.

    """
    return Inference(annotation, f"{checker}'s inferred type", frozenset({KIND}))


def type_alias(known: Known, before: int) -> str | None:
    """Name `TypeAlias`, to declare the alias a module body binds on line `before`.

    As an import the module has names it (`typing`'s, or `typing_extensions`'s), if it runs by then,
    the name itself before one through its module (`TypeAlias`, then `typing.TypeAlias`); else by a
    new import from `typing`.

    Returns:
      The name, or `None` if the module can't name it there.

    """
    plan: ImportPlan | None
    if (plan := known.names.plan) is None:
        return None
    name: str | None
    named: list[str]
    if not (named := [name for origin in _ALIAS_ORIGINS if (name := plan.named(origin)) is not None]):
        return plan.spell(_ALIAS_ORIGINS[0])
    bound: list[str] = [each for each in named if plan.defined.get(each.partition(".")[0], before) < before]
    return min(bound, key=lambda each: _DOT in each, default=None)


def renames(name: str, annotation: str, *, local: bool) -> bool:
    """Check whether `annotation`, a hint's, says `name` is another name for a class: a `type[C]`.

    An alias annotations are written with, which declared (a variable) it would no longer be. A
    module's name is taken for one, and a function's (`local`) if it's written as a class's is
    (`Pair = tuple[int, str]`, not `cls = type(self)`).

    Returns:
      Whether it does.

    """
    return annotation.startswith(_CLASS) and not (local and name[:1].islower())


def _spelled(
    text: str,
    known: Known,
    imports: tuple[str, ...],
    *,
    nesting: int,
    before: int | None,
) -> str | None:
    """Write a hint's `text` as an annotation the file can hold, with `imports` for its names.

    Returns:
      The annotation, or `None` if it isn't one, says too little, or names what the file can't.

    """
    plan: ImportPlan | None = known.names.plan
    try:
        parsed: ast.expr = ast.parse(_plain(text), mode="eval").body
    except SyntaxError:
        return None
    root: ast.expr | None = _widened(parsed)
    if plan is None or root is None or not _annotation(root) or not _fits(root, nesting, known.max_length):
        return None
    lone: set[str] = _lone(root)
    # `TypeAlias` is `type_alias`'s to write. A special form alone isn't a type.
    if _aliases(root) or lone & _FORMS:
        return None
    origins: _Origins = _origins(imports)
    names: list[str] = sorted(
        {
            node.id
            for node in ast.walk(root)
            if isinstance(node, ast.Name) and not _usable(node.id, plan, before)
        },
    )
    ways: dict[str, str | None] = {name: _way(name, plan, origins, lone=name in lone) for name in names}
    if None in ways.values():
        return None
    spelled: dict[str, str] = {}
    name: str
    for name in names:
        found: str | None
        if (found := _named(name, ways[name], plan, origins)) is None:
            return None
        spelled[name] = found
    # The annotation holds no strings (its only constants are `None` and `...`): a name is a word
    # that isn't an attribute's.
    return re.sub(
        r"(?<![\w.])(\w+)",
        lambda word: spelled.get(word[1], word[1]),
        ast.unparse(root),
    )


def _plain(text: str) -> str:
    """Write a hint's text as Python reads it: ty's class objects and scoped type variables as names.

    Returns:
      It: `<class 'Point'>` as `type[Point]`, `Model@create_model` as `Model`.

    """
    return _SCOPED.sub(r"\1", _CLASS_OBJECT.sub(r"type[\1]", text))


def _lone(root: ast.expr) -> set[str]:
    """Name the names an annotation writes without type arguments (`Box` in `list[Box]`, not `list`).

    Returns:
      Them.

    """
    subscripted: set[int] = {id(node.value) for node in ast.walk(root) if isinstance(node, ast.Subscript)}
    return {node.id for node in ast.walk(root) if isinstance(node, ast.Name) and id(node) not in subscripted}


def _aliases(root: ast.expr) -> bool:
    """Check whether an annotation is (or has in it) `TypeAlias`, however it's spelled.

    Returns:
      Whether it does.

    """
    return any(
        (isinstance(node, ast.Name) and node.id == ALIAS)
        or (isinstance(node, ast.Attribute) and node.attr == ALIAS)
        for node in ast.walk(root)
    )


@lru_cache(maxsize=1024)
def _origins(imports: tuple[str, ...]) -> _Origins:
    """Read the `from` imports a hint's edits add (see `Offered`), each a statement binding one name.

    An `import m` is passed over: it names no class.

    Returns:
      Each name bound, with its statement, the module (a relative one with its dots) and its name there.

    """
    found: _Origins = {}
    statement: str
    for statement in imports:
        node: ast.stmt = ast.parse(statement).body[0]
        if isinstance(node, ast.ImportFrom):
            alias: ast.alias = node.names[0]
            module: str = _RELATIVE * node.level + (node.module or "")
            found[alias.asname or alias.name] = (statement, module, alias.name)
    return found


def _way(name: str, plan: ImportPlan, origins: _Origins, *, lone: bool) -> str | None:
    """Choose how a name the module doesn't bind where annotations run can be written.

    `lone`: whether the annotation writes it without type arguments somewhere.

    Returns:
      `_OWN`, `_OFFERED` or `_KNOWN`; `None` if nothing says what the name means. From the standard
      library, a hint's edits must import a class its tables know, from a public module, and never a
      generic one written bare (a checker prints one so when it doesn't know its arguments).

    """
    if name == _DISCARD:
        return None
    if name in plan.guarded and plan.guarded[name].statement is None and name not in plan.values:
        return _OWN
    module: str
    attribute: str
    _, module, attribute = origins.get(name, ("", "", ""))
    # A standard-library class a checker prints bare is imported to run, as `--fix`'s own are.
    standard: bool = name not in origins or module.partition(_RELATIVE)[0] in _STDLIB
    if name in WELL_KNOWN and standard:
        return _KNOWN
    if name not in origins:
        return None
    path: str = f"{module}.{attribute}"
    writable: bool = (
        not any(part.startswith("_") for part in module.split(_RELATIVE))
        and stdlib.defines_class(path)
        and not (lone and stdlib.needs_arguments(path))
    )
    return _OFFERED if writable or not standard else None


def _named(name: str, way: str | None, plan: ImportPlan, origins: _Origins) -> str | None:
    """Write `name` the `way` chosen for it, adding the import it takes.

    Returns:
      The name as the file is to write it, or `None` if the import can't bind it.

    """
    if way == _KNOWN:
        return plan.spell(WELL_KNOWN[name])
    if way == _OWN:
        return name
    statement: str
    module: str
    attribute: str
    statement, module, attribute = origins[name]
    # Through an import that runs, if the module has one of what the hint's would bind.
    found: str | None
    if not module.startswith(_RELATIVE) and (found := plan.named(f"{module}.{attribute}")) is not None:
        return found
    return name if plan.guard(name, (module, attribute), statement) else None


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
        case ast.BinOp(op=ast.BitOr() | ast.BitAnd()):
            return _joined(node)
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


def _joined(node: ast.BinOp) -> ast.expr | None:
    """Widen a union's members; or read an intersection with a truthiness as its one other member.

    Returns:
      The annotation, or `None` for a member that widens to none, or any other intersection.

    """
    if isinstance(node.op, ast.BitOr):
        return _union([_widened(member) for member in _members(node)])
    types: list[ast.expr] = [part for part in _members(node, ast.BitAnd) if not _truthiness(part)]
    return _widened(types[0]) if len(types) == 1 else None


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


def _members(node: ast.expr, joined: type[ast.operator] = ast.BitOr) -> list[ast.expr]:
    """Flatten a union (`A | B | C`) into its members; or, `joined` by `&`, an intersection.

    Returns:
      Them, in order.

    """
    if isinstance(node, ast.BinOp) and isinstance(node.op, joined):
        return [*_members(node.left, joined), *_members(node.right, joined)]
    return [node]


def _truthiness(node: ast.expr) -> bool:
    """Check whether an intersection's member only says its value is true, or false (`~AlwaysFalsy`).

    Returns:
      Whether it does.

    """
    name: str
    match node:
        case ast.UnaryOp(op=ast.Invert(), operand=ast.Name(id=name)):
            return name in _TRUTHINESS
        case _:
            return False


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
