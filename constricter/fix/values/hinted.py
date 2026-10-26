"""`--infer-with`: a type checker's inferred type (an inlay hint) as a fix, when the file can use it.

Always a guess: a hint is the type the checker gave the value where the name is bound, so it can be
too narrow for a later binding, or too wide for what the code means. It's judged here as text, as
the checker printed it:

- a class object printed `<class 'Point'>` (ty's way) is `type[Point]`, a type variable printed with
  its scope (`Model@create_model`) the variable, and an intersection with a truthiness
  (`str & ~AlwaysFalsy`) its other member;
- an unpacked tuple (`tuple[str, *tuple[str, ...]]`, Python 3.11's syntax) is kept where the
  project's oldest Python parses it (`min-python`); else written with `Unpack` where the module
  imports it (one level deeper, to LVA006), and dropped where it doesn't;
- a `Literal` is widened to its values' types (`Literal[1, 2]` is `int`, `Literal[Color.RED]` is
  `Color`), and `LiteralString` to `str`, then a union's repeated members dropped;
- anything that isn't an annotation (`Module("os")`, a callable's signature, `Self@C`) is dropped,
  as is a vague one (`Any`, `list[Unknown]`), a bare `None`, one with `Never` or `NoReturn` in it
  (an empty display's `list[Never]`, or code the checker takes not to run), one nested as deep as
  LVA006 reports, or a tuple as long as LVA011 does;
- a special form alone (`type[Generic]`) is dropped, as is a union inside the hint
  (`dict[str, int | bytes]`), and a `Literal` in a class's own arguments, which may be bound to it
  (a union for a name its function doesn't narrow, a name it returns as `Self` and one bound again
  are `constricter.rules`' to drop);
- `TypeAlias`, hinted for an alias's assignment, declares a module's alias written as a subscript or
  a union (see `type_alias`), and is dropped anywhere else;
- a generator's, coroutine's or async generator's class as `types` has it at run time (ty's
  `GeneratorType[str, None, None]`) is `collections.abc`'s, as every checker types the expression
  that makes one (`Generator[str, None, None]`);
- every name in it must be one the file can use: a builtin, a name the module binds at its top
  level (before the binding, in a module body, where the annotation is evaluated), a class or
  alias it imports under `if TYPE_CHECKING:` or the hint's own edits import (`Offered`: imported
  for type checking alone, as the checker says from where; see `constricter.fix.index.offers` for which
  are taken), or a class the checker prints by its bare name from a module `ImportPlan.spell` can
  import (`Callable`, `Iterator`, `Path`, `deque`, ...). Anything else, it can't be sure what the
  name means. Nor where the file binds a name to another thing than the checker prints it for: one
  of those well-known classes bound to its own class or a module (`class Match`, `import datetime`),
  a builtin that takes no type arguments given some (numpy's `bool[bool]`, printed bare), a dotted
  name with a private part (`np._NBitIntP`), or a class a function defines (`Parser.read.Dialect`).

A hint with edits is judged as it shows first (`Thing[str]`), then as they'd write it
(`things.Thing[str]`, through a module the file imports).
"""

import ast
import builtins
import importlib
import operator
import re
import sys
from collections.abc import Mapping, Sequence
from functools import lru_cache
from types import ModuleType
from typing import Final, NamedTuple, TypeAlias

from constricter.fix.core.known import Hints, ImportPlan, Inference, Known, Offered
from constricter.fix.libraries import stdlib
from constricter.rules.annotations import ABSTRACT, depth, dotted, length, vague_fits

KIND: Final = "checker"  # the fix kind, and what the guess rests on
TRACED: Final = "traced"  # the same, for a traced run's types (`--infer-from`)
KINDS: Final = frozenset({KIND, TRACED})
AGREED: Final = "agreed"  # beside `KIND`: another checker hints the same type there (a set of its own)
_LITERAL: Final = "Literal"
_NONE: Final = "None"
_BUILTINS: Final = frozenset(dir(builtins))
ALIAS: Final = "TypeAlias"  # what a checker hints an alias's assignment as
_ALIAS_ORIGINS: Final = ("typing.TypeAlias", "typing_extensions.TypeAlias")
_CLASS: Final = "type["
_UNPACK: Final = "Unpack"  # what an unpacked tuple (`*tuple[str, ...]`) is written with
_UNPACK_ORIGINS: Final = frozenset({"typing.Unpack", "typing_extensions.Unpack"})
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
# Standard-library modules never imported to ask what they bind: importing one does something.
_UNIMPORTED: Final = frozenset({"antigravity", "this", "__hello__", "__phello__", "idlelib", "turtle"})
_RELATIVE: Final = "."
_DOT: Final = "."
# How one unbound name of a hint can be written: through a guarded import, or `ImportPlan.spell`.
_OWN: Final = "own"  # the module imports it under `if TYPE_CHECKING:`
_OFFERED: Final = "offered"  # the hint's edits import it
_KNOWN: Final = "known"  # `WELL_KNOWN` says where it's from
# The builtins that take type arguments: another of a builtin's names given some is another class.
_GENERIC_BUILTINS: Final = frozenset(
    {
        "BaseExceptionGroup",
        "ExceptionGroup",
        "classmethod",
        "dict",
        "enumerate",
        "filter",
        "frozenset",
        "list",
        "map",
        "memoryview",
        "reversed",
        "set",
        "slice",
        "staticmethod",
        "tuple",
        "type",
        "zip",
    },
)
# `types`' classes for what a generator, a coroutine and an async generator make, and how checkers
# type those: as `collections.abc`'s classes.
_RUNTIME: Final = {
    "GeneratorType": "Generator",
    "CoroutineType": "Coroutine",
    "AsyncGeneratorType": "AsyncGenerator",
}
_TYPES: Final = "types"
_BOTTOM: Final = frozenset({"Never", "NoReturn"})  # the type of no value: never a variable's


class Site(NamedTuple):
    """Where a hint's name is bound.

    How deep an annotation may nest there (LVA006), on which line of a module body (`None` in a
    function), and whether to an operation on tuples (`a + (b,)`), whose precise type mypy doesn't
    read (see `_homogeneous`).
    """

    nesting: int
    before: int | None = None
    concatenated: bool = False


def hinted(text: str, known: Known, site: Site, offered: Offered | None = None) -> str | None:
    """Judge a checker's hint `text` as a fix for the binding at `site`.

    `offered`: what the hint's edits would write, judged if `text` is no fix.

    Returns:
      The annotation, spelled as the file can (an import added if it must be), or `None`.

    """
    imports: tuple[str, ...] = () if offered is None else offered.imports
    candidates: list[str] = [text]
    if offered is not None and not _renamed(text, offered.text, known.names.plan, _origins(imports)):
        candidates.append(offered.text)
    candidate: str
    for candidate in dict.fromkeys(candidates):
        annotation: str | None
        if (annotation := _spelled(candidate, known, imports, site)) is not None:
            return annotation
    return None


def inference(annotation: str, found: Hints, agreeing: int = 1) -> Inference:
    """Make the fix a hint of `found` gives, as `hinted` wrote it.

    `agreeing`: the checkers whose hints give it, `found`'s included; two or more, it rests on their
    agreement too (`AGREED`).

    Returns:
      It.

    """
    if found.kind == TRACED:
        return Inference(annotation, "what a traced run bound it to", frozenset({TRACED}))
    if agreeing > 1:
        reason: str = f"{found.checker}'s inferred type, which {agreeing} type checkers agree on"
        return Inference(annotation, reason, frozenset({found.kind, AGREED}))
    return Inference(annotation, f"{found.checker}'s inferred type", frozenset({found.kind}))


def resting(found: Inference) -> frozenset[str]:
    """Name what a hint's guess rests on, to trust (`unsafe-fix-select`): its checker, not their agreement.

    Returns:
      Its kinds less `AGREED`: `--unsafe-fix-select checker` trusts an agreed hint as it does any.

    """
    return found.kinds - {AGREED}


def type_alias(known: Known, before: int) -> str | None:
    """Name `TypeAlias`, to declare the alias a module body binds on line `before`.

    As an import the module has names it (`typing`'s, or `typing_extensions`'s), if it runs by then,
    the name itself before one through its module (`TypeAlias`, then `typing.TypeAlias`); else by a
    new import from `typing`, where every Python the module runs on has it there (`aliased`).

    Returns:
      The name, or `None` if the module can't name it there.

    """
    plan: ImportPlan | None
    if (plan := known.names.plan) is None:
        return None
    name: str | None
    named: list[str]
    if not (named := [name for origin in _ALIAS_ORIGINS if (name := plan.named(origin)) is not None]):
        return plan.spell(_ALIAS_ORIGINS[0]) if known.names.aliased else None
    bound: list[str] = [each for each in named if plan.defined.get(each.partition(".")[0], before) < before]
    return min(bound, key=lambda each: _DOT in each) if bound else None


def renames(name: str, annotation: str, *, local: bool) -> bool:
    """Check whether `annotation`, a hint's, says `name` is another name for a class: a `type[C]`.

    An alias annotations are written with, which declared (a variable) it would no longer be. A
    module's name is taken for one, and a function's (`local`) if it's written as a class's is
    (`Pair = tuple[int, str]`, not `cls = type(self)`).

    Returns:
      Whether it does.

    """
    return annotation.startswith(_CLASS) and not (local and name[:1].islower())


def _renamed(shown: str, written: str, plan: ImportPlan | None, origins: _Origins) -> bool:
    """Check whether a hint's edit writes a generic `shown` under one name under another.

    ty shows a generic alias (`NDArray[bool]`) and writes the class it stands for with the alias's
    own arguments (`np.ndarray[np.bool]`), which aren't the class's. A name the file or the edit's
    imports bind to the one shown (`from shapes import Shape as S`) is the same one.

    Returns:
      Whether it does.

    """
    try:
        pairs: list[tuple[ast.expr, ast.expr]] = list(zip(_heads(shown), _heads(written), strict=False))
    except SyntaxError:
        return False
    was: ast.expr
    now: ast.expr
    for was, now in pairs:
        name: str = now.attr if isinstance(now, ast.Attribute) else ast.unparse(now)
        if name in origins and isinstance(now, ast.Name):
            name = origins[name][2]
        elif isinstance(now, ast.Name):
            name = (name if plan is None else plan.bound.get(name, name)).rpartition(_DOT)[2]
        if name != (was.attr if isinstance(was, ast.Attribute) else ast.unparse(was)):
            return True
    return False


def _heads(text: str) -> list[ast.expr]:
    """List what a hint's `text` subscripts (`dict` and `list` in `dict[str, list[int]]`), outermost first.

    Returns:
      Them.

    """
    root: ast.expr = ast.parse(_plain(text), mode="eval").body
    return [node.value for node in ast.walk(root) if isinstance(node, ast.Subscript)]


def _spelled(text: str, known: Known, imports: tuple[str, ...], site: Site) -> str | None:
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
    if root is not None and site.concatenated:
        root = _homogeneous(root)
    if plan is not None and root is not None and not known.names.starred:
        root = _unstarred(root, plan)
    if (
        plan is None
        or root is None
        or not _annotation(root, known.indirect.unions)
        or not _fits(root, site.nesting, known)
    ):
        return None
    origins: _Origins = _origins(imports)
    root = _abstract(root, plan, origins)
    lone: set[str] = _lone(root)
    # `TypeAlias` is `type_alias`'s to write. A special form alone isn't a type.
    if _aliases(root) or lone & _FORMS or _misnamed(root, plan) or _bottom(root):
        return None
    names: list[str] = sorted(
        {
            node.id
            for node in ast.walk(root)
            if isinstance(node, ast.Name) and not _usable(node.id, plan, site.before)
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


def _unstarred(root: ast.expr, plan: ImportPlan) -> ast.expr | None:
    """Write an annotation's unpacked tuples as every Python 3 parses them: `Unpack[tuple[str, ...]]`.

    `*tuple[str, ...]` in a subscript is Python 3.11's syntax: for a module that may run on an
    older one (see `LibraryNames.starred`).

    Returns:
      The annotation; `None` for one that unpacks, where the module doesn't import `Unpack`.

    """
    nodes: list[ast.AST] = list(ast.walk(root))
    if not any(isinstance(node, ast.Starred) for node in nodes):
        return root
    if plan.bound.get(_UNPACK) not in _UNPACK_ORIGINS:
        return None
    lone: list[ast.expr] = []  # each tuple of one unpacked element: `tuple[*Ts]`'s, its one argument
    node: ast.AST
    for node in nodes:
        if isinstance(node, ast.Tuple | ast.List):
            if isinstance(node, ast.Tuple) and len(node.elts) == 1 and isinstance(node.elts[0], ast.Starred):
                lone.append(node)
            node.elts = [
                ast.Subscript(ast.Name(_UNPACK), each.value) if isinstance(each, ast.Starred) else each
                for each in node.elts
            ]
    for node in nodes:
        if isinstance(node, ast.Subscript) and isinstance(node.slice, ast.Tuple) and node.slice in lone:
            node.slice = node.slice.elts[0]
    return root


def _abstract(root: ast.expr, plan: ImportPlan, origins: _Origins) -> ast.expr:
    """Write `types`' generator, coroutine and async generator classes as `collections.abc`'s.

    Where the name is `types`' (`GeneratorType` that the module or the hint's edits import from it,
    `types.GeneratorType` through the module): see `_RUNTIME`.

    Returns:
      The annotation.

    """
    node: ast.AST
    abstract: str | None
    for node in ast.walk(root):
        if isinstance(node, ast.Subscript) and (abstract := _runtime(node.value, plan, origins)) is not None:
            node.value = ast.Name(abstract)
    return root if (abstract := _runtime(root, plan, origins)) is None else ast.Name(abstract)


def _runtime(node: ast.expr, plan: ImportPlan, origins: _Origins) -> str | None:
    """Name the `collections.abc` class for `types`' class `node` names, if it names one of `_RUNTIME`'s.

    Returns:
      It, or `None`.

    """
    name: str
    module: str
    match node:
        case ast.Name(id=name) if name in _RUNTIME and _origin(name, plan, origins) == f"{_TYPES}.{name}":
            return _RUNTIME[name]
        case ast.Attribute(value=ast.Name(id=module), attr=name) if (
            name in _RUNTIME and plan.bound.get(module) == _TYPES
        ):
            return _RUNTIME[name]
        case _:
            return None


def _bottom(root: ast.expr) -> bool:
    """Check whether an annotation has `Never` or `NoReturn` in it, however it's spelled.

    Returns:
      Whether it does.

    """
    return any(
        (isinstance(node, ast.Name) and node.id in _BOTTOM)
        or (isinstance(node, ast.Attribute) and node.attr in _BOTTOM)
        for node in ast.walk(root)
    )


def _misnamed(root: ast.expr, plan: ImportPlan) -> bool:
    """Check whether an annotation names what the file binds to another thing than the checker means.

    A module, written bare (`import socket`, then `socket`: the checker's is a class), a well-known
    class's name (`Match`) the module binds to its own class, a builtin it doesn't rebind given type
    arguments it takes none of (numpy's `bool`, printed bare), a private part of a dotted name
    (`np._NBitIntP`), or a class a function defines, named through it (`Parser.read.Dialect`).

    Returns:
      Whether it does.

    """
    node: ast.AST
    name: str
    # A dotted name's root (`datetime` in `datetime.date`) is a module's, rightly.
    roots: set[int] = {id(node.value) for node in ast.walk(root) if isinstance(node, ast.Attribute)}
    for node in ast.walk(root):
        match node:
            case ast.Name(id=name) if id(node) not in roots and (
                plan.bound.get(name) == name
                or (name in WELL_KNOWN and name in plan.defined and not _imported(name, plan))
            ):
                return True
            case ast.Subscript(value=ast.Name(id=name)) if (
                name in _BUILTINS and name not in plan.defined and name not in _GENERIC_BUILTINS
            ):
                return True
            case ast.Attribute() if id(node) not in roots:
                parts: list[str] = _dotted(node)
                if parts and (
                    any(part.startswith("_") for part in parts[1:])
                    or (parts[0] not in plan.bound and any(part[:1].islower() for part in parts[1:-1]))
                    or _unbound_attribute(parts, plan)
                ):
                    return True
            case _:
                pass
    return False


def _unbound_attribute(parts: list[str], plan: ImportPlan) -> bool:
    """Check whether a dotted name through a standard-library module names what the module hasn't.

    A checker prints what its stubs have: `sys.OptExcInfo`, typeshed's alias of `sys.exc_info()`'s
    return, which `sys` doesn't bind, or `importlib.metadata.SelectableGroups`, gone since 3.12.
    Asked of the module as this Python has it (imported here if it isn't yet); a module that can't
    be imported says nothing.

    Returns:
      Whether the module lacks the attribute.

    """
    origin: str | None = plan.bound.get(parts[0])
    if origin is None or origin.partition(_DOT)[0] not in _STDLIB:
        return False
    found: ModuleType | None
    names: list[str] = [*origin.split(_DOT), *parts[1:]]
    # The longest prefix that's a module, then the rest as its attributes.
    count: int
    for count in range(len(names), 0, -1):
        if (found := _module(_DOT.join(names[:count]))) is not None:
            return not _has_attributes(found, names[count:])
    return False


def _module(name: str) -> ModuleType | None:
    """Find a standard-library module by its dotted `name`: imported already, or imported here.

    Returns:
      It, or `None` if it can't be imported, or isn't one (a package's submodule it hasn't).

    """
    if name.partition(_DOT)[0] in _UNIMPORTED or any(part.startswith("_") for part in name.split(_DOT)):
        return None
    try:
        return importlib.import_module(name)
    except (ImportError, OSError, ValueError, AttributeError, RuntimeError):  # one this platform lacks
        return None


def _has_attributes(module: ModuleType, names: Sequence[str]) -> bool:
    """Check whether `module` has `names`, each an attribute of the one before.

    Returns:
      Whether it does.

    """
    try:
        _ = operator.attrgetter(_DOT.join(names))(module) if names else module
    except AttributeError:
        return False
    return True


def _origin(name: str, plan: ImportPlan, origins: _Origins) -> str | None:
    """Find what a hint's bare `name` is: what the module's import binds, else the hint's edits'.

    Returns:
      Its qualified name; `None` where the module binds it otherwise, or nothing says.

    """
    if name in plan.bound:
        return plan.bound[name]
    if name in plan.defined or name not in origins:
        return None
    return f"{origins[name][1]}.{origins[name][2]}"


def _imported(name: str, plan: ImportPlan) -> bool:
    """Check whether the module binds `name` by importing a class of that name (`from re import Match`).

    Returns:
      Whether it does: not by `import name` (a module), nor under another name, nor otherwise.

    """
    bound: str | None = plan.bound.get(name)
    return bound is not None and _DOT in bound and bound.rpartition(_DOT)[2] == name


def _dotted(node: ast.expr) -> list[str]:
    """Split a dotted name into its parts: `np.ma.MaskedArray`'s `np`, `ma` and `MaskedArray`.

    Returns:
      Them, the root first; empty for an attribute of anything but a name.

    """
    spelled: str | None = dotted(node)
    return [] if spelled is None else spelled.split(_DOT)


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


def _annotation(root: ast.expr, unions: Mapping[str, str]) -> bool:
    """Check that an expression is an annotation, and says something: not a bare `None`.

    Names, attributes, subscripts and unions, whose only constants are `None` and `...`: not a call
    (`Module("os")`), a signature, or a string. `unions`: the module's type aliases of a union, as
    it spells them (see `Indirect.unions`).

    Returns:
      Whether it is.

    """
    return (
        all(isinstance(node, _ANNOTATION_NODES) for node in ast.walk(root))
        and all(node.value in {None, Ellipsis} for node in ast.walk(root) if isinstance(node, ast.Constant))
        and not (isinstance(root, ast.Constant) and root.value is None)
        and not _mixes(root, unions)
    )


def _mixes(root: ast.expr, unions: Mapping[str, str]) -> bool:
    """Check whether an annotation has a union inside it (`dict[str, int | bytes]`): a mixed container's.

    Its elements are read as one member or another, which no test of the name narrows. An alias of
    a union (`list[Scalar]`, pandas's `Scalar = Union[str, int, ...]`) is one too.

    Returns:
      Whether it does.

    """
    chain: set[int] = _chain(root)
    inner: set[int] = {
        id(name)
        for node in ast.walk(root)
        if isinstance(node, ast.Subscript)
        for name in ast.walk(node.slice)
        if isinstance(name, ast.Name)
    }
    return any(
        (isinstance(node, ast.BinOp) and id(node) not in chain)
        or (isinstance(node, ast.Name) and id(node) in inner and node.id in unions)
        for node in ast.walk(root)
    )


def _homogeneous(root: ast.expr) -> ast.expr | None:
    """Widen a tuple with an unpacked variadic part beside other elements to the variadic tuple alone.

    For a concatenation, which basedpyright types precisely (`tuple[str, ...] + (name,)` is
    `tuple[*tuple[str, ...], str]`) where mypy reads typeshed's `tuple[str, ...]` and rejects the
    precise type declared; a display (`(name, *names)`) every checker types precisely. Every other
    element of the variadic part's type widens to it.

    Returns:
      The annotation; `None` where an element is of another type, which no plain tuple holds.

    """
    node: ast.AST
    for node in ast.walk(root):
        if not (isinstance(node, ast.Subscript) and isinstance(node.slice, ast.Tuple)):
            continue
        starred: list[ast.Starred] = [part for part in node.slice.elts if isinstance(part, ast.Starred)]
        element: ast.expr | None
        if len(starred) != 1 or len(node.slice.elts) == 1 or (element := _variadic(starred[0].value)) is None:
            continue
        kept: str = ast.unparse(element)
        if any(ast.unparse(part) != kept for part in node.slice.elts if not isinstance(part, ast.Starred)):
            return None
        node.slice = ast.Tuple([element, ast.Constant(Ellipsis)])
    return root


def _variadic(node: ast.expr) -> ast.expr | None:
    """Read the element type of a variadic tuple, `tuple[T, ...]`.

    Returns:
      `T`, or `None` for anything else (`Ts`, a type variable tuple).

    """
    element: ast.expr
    match node:
        case ast.Subscript(
            value=ast.Name(id="tuple"),
            slice=ast.Tuple(elts=[element, ast.Constant(value=builtins.Ellipsis)]),
        ):
            return element
        case _:
            return None


def _chain(root: ast.expr) -> set[int]:
    """Find the nodes joining an annotation's outermost union: `A | B` in `A | B | C`.

    Returns:
      Their identities.

    """
    return {id(root)} | _chain(root.left) if isinstance(root, ast.BinOp) else set()


def _fits(root: ast.expr, nesting: int, known: Known) -> bool:
    """Check the rules accept an annotation: not vague (LVA005), too deep (LVA006) or long (LVA011).

    Returns:
      Whether it is.

    """
    return (
        vague_fits(root, known.limits.vague)
        and depth(root) < nesting
        and length(root) <= known.limits.max_length
    )


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
            # A class's own argument may be bound to the literals (`Reader[Literal["frame"]]`).
            # Compared as written: a node built here has no `ctx` before Python 3.13, so its dump differs.
            same: bool = widened is not None and (_holds(value) or ast.unparse(widened) == ast.unparse(inner))
            return ast.Subscript(value, widened) if widened is not None and same else None
        case ast.Tuple(elts=elements) | ast.List(elts=elements):
            parts: list[ast.expr | None] = [_widened(element) for element in elements]
            kept: list[ast.expr] = [part for part in parts if part is not None]
            rebuilt: ast.expr = ast.Tuple(kept) if isinstance(node, ast.Tuple) else ast.List(kept)
            return rebuilt if len(kept) == len(parts) else None
        case ast.Name(id=name):
            return ast.Name(_WIDER.get(name, name))
        case _:
            return node


def _holds(head: ast.expr) -> bool:
    """Check whether a subscript's head is a container of any type: a builtin, or `collections.abc`'s.

    Returns:
      Whether it is.

    """
    return isinstance(head, ast.Name) and (head.id in _BUILTINS or head.id in WELL_KNOWN)


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
