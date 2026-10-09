# SPDX-License-Identifier: MIT
"""Standard-library functions and classes whose types `--fix` knows, and how a module names them.

The tables are generated from typeshed's stubs into `tables/` when the package is built, one JSON
file each (see `stdlib_tables/generate.py`): `RETURNS` holds functions returning the same builtin type
whatever their arguments; `OVERLOADS` those whose arguments decide it (`str` in, `str` out;
`bytes` in, `bytes` out), so they're typed only when those are known; `CLASSES` holds
non-generic classes, and functions returning one; `library_member` types those classes' methods
and attributes. A call is matched by the module and name it resolves to through the module's imports
(`origins`), not by how it's spelled, so `import os as o` then `o.getpid()`, or `from os import
getpid`, are the same call, and a `getpid` from anywhere else isn't.
"""

import ast
import builtins
import json
from collections.abc import Iterable, Mapping
from functools import cache, lru_cache
from pathlib import Path
from types import MappingProxyType
from typing import Final, NamedTuple, TypeAlias, cast

from constricter.fix.core.known import ImportPlan, Inference, Known
from constricter.fix.core.signatures import Variant
from constricter.rules.syntax import import_bindings
from constricter.rules.walked import classes


def _table(name: str) -> object:
    """Read one of the tables (`tables/<name>.json`), plain JSON as generated.

    Returns:
      Its entries.

    """
    # Not through `jsonc`: its comment stripping took 20 ms of every run's start, for nothing.
    return cast(
        "object",
        json.loads(Path(__file__).parents[1].joinpath("tables", f"{name}.json").read_bytes()),
    )


# `os.environ`'s own method with a fixed type: a variable's, which the tables' functions don't hold.
_ENVIRON: Final = {"os.environ.copy": "dict[str, str]"}
# `tarfile.open` is `TarFile.open` (typeshed's `open = TarFile.open`): an alias the tables don't follow.
_ALIASED: Final = {"tarfile.open": "tarfile.TarFile"}
RETURNS: Final = {**cast("dict[str, str]", _table("returns")), **_ENVIRON, **_ALIASED}
# Functions whose arguments decide their type: each signature, as each configuration reads them
# (see `constricter.fix.libraries.overloads`).
OVERLOADS: Final = cast("dict[str, list[Variant]]", _table("overloads"))
# Classes, and functions (constructors, classmethods) returning one: typed by that class's dotted
# path, spelled (and imported, if it must be) the way the module can.
CLASSES: Final = cast("dict[str, str]", _table("classes"))
# The builtin iterators no Python can subscript at run time.
_UNSUBSCRIPTABLE: Final = frozenset({"zip", "map", "reversed"})
# The `pathlib` classes: each one's `/` joins another part onto it.
_PATHS: Final = frozenset(
    f"pathlib.{name}"
    for name in ("Path", "PosixPath", "PurePath", "PurePosixPath", "PureWindowsPath", "WindowsPath")
)
_ALIASES: Final = cast("Mapping[str, str]", _table("aliases"))  # a class's other public paths, to its own
# Each class's methods' returns and attributes' types apart from its public ancestors' (`_BASES`),
# `None` where it hides one of theirs: `_member` resolves the rest through them.
_Own: TypeAlias = Mapping[str, Mapping[str, str | None]]
_METHODS: Final = cast("_Own", _table("methods"))
_ATTRIBUTES: Final = cast("_Own", _table("attributes"))
# What awaiting a call of each `async def` gives: a function's by its path, a method's by its
# class's path and its name (a class's own path: its instance).
_AWAITED: Final = cast("Mapping[str, str]", _table("awaited"))
# The `async def`s whose arguments decide what awaiting their call gives, as `OVERLOADS` holds a
# function's; `signatures.AWAIT` before a path names one's entry to `overloads.chosen`.
AWAITED_OVERLOADS: Final = cast("dict[str, list[Variant]]", _table("awaited_overloads"))
# The generic classes awaiting an instance of gives its last type argument.
_AWAITABLE: Final = frozenset({"asyncio.Future", "asyncio.Task"})
# Each class's public ancestors in the tables, nearest first, comma-separated.
_BASES: Final = cast("Mapping[str, str]", _table("bases"))
# Classes' methods whose arguments decide their type: each one's entry in `method_signatures` (its
# signatures without `self`, as `OVERLOADS`', under the class defining it: `module.Class.method`).
_METHOD_OVERLOADS: Final = cast("_Own", _table("method_overloads"))  # by name, as `_METHODS`
# Each generic class's type parameters, in order, comma-separated: an instance's type binds them.
# One ending `=` has a default (PEP 696): a class all of whose have one may be written bare.
_TYPE_PARAMETERS: Final = cast("Mapping[str, str]", _table("type_parameters"))
# The generic classes every Python can subscript at run time (`itertools.chain[str]`, not
# `itertools.count[int]`), as a module's own annotations are evaluated.
_SUBSCRIPTABLE: Final = cast("Mapping[str, str]", _table("subscriptable"))
# Each generic class's own attributes and properties, as templates naming its type parameters
# (`re.Match`'s `string`: `AnyStr`), which its instance's type arguments bind; and a non-generic
# class's own that `_ATTRIBUTES` can't hold (`ast.Module`'s `body`: `list[ast.stmt]`).
_GENERIC_ATTRIBUTES: Final = cast("_Own", _table("generic_attributes"))
# What iterating each class's instance gives, as such a template (`io.TextIOWrapper`'s `str`).
_ELEMENTS: Final = cast("Mapping[str, str]", _table("elements"))


@cache
def method_signatures() -> dict[str, list[Variant]]:
    """Read the `method_signatures` table, the first time a call needs it.

    Returns:
      Each method's signatures (see `OVERLOADS`), by its entry.

    """
    return cast("dict[str, list[Variant]]", _table("method_signatures"))


@cache
def _scalars() -> Mapping[str, str]:
    return cast("Mapping[str, str]", _table("scalars"))


@cache
def _scalar_members() -> Mapping[str, frozenset[str]]:
    return {
        scalar: frozenset(names)
        for scalar, names in cast("Mapping[str, list[str]]", _table("scalar_members")).items()
    }


def scalar_verdicts(path: str) -> str | None:
    """Look up which builtin scalars a standard-library class or alias takes (`typing.SupportsIndex`).

    Read the first time an installed package's overloads need it (see `constricter.fix.index.stubbed`).

    Returns:
      Its verdict per `overloads.SCALARS` type, in order; or `None` if the tables don't have it.

    """
    return _scalars().get(path)


def scalar_members(scalar: str) -> frozenset[str] | None:
    """Name what an argument of builtin scalar type `scalar` has, for a protocol to be checked against.

    Returns:
      Its members, or `None` if the tables don't have them.

    """
    return _scalar_members().get(scalar)


# An environment lookup: `os.environ.get(k)` is `str | None`, with a `str` default it's `str`
# (`os.environ`'s generic `Mapping.get` decides it by the arguments).
ENVIRONMENT: Final = "os.environ.get"
_KIND: Final = "stdlib"  # the fix kind of what the tables type
_BUILTIN_NAMES: Final = frozenset({*dir(builtins), "None"})
_DOT: Final = "."
_ENTER: Final = "__enter__"
_SELF: Final = "Self"  # in a template: the receiver's own type
ANY: Final = "Any"  # a function's whole return in `RETURNS`, declared `typing.Any` (`json.loads`)
KNOWN: Final = frozenset({*RETURNS, *OVERLOADS, ENVIRONMENT, *CLASSES})  # every function the tables type
# Capitalised functions the tables don't type (`xml.etree.ElementTree.Comment`): no constructors.
FUNCTIONS: Final = frozenset(cast("Mapping[str, str]", _table("functions")))
# Module-level variables' types (`sys.path`: `list[str]`): builtin annotations, or classes' paths.
VARIABLES: Final = cast("dict[str, str]", _table("variables"))
_TABLE_MODULES: Final = frozenset(
    name.rsplit(".", count)[0]
    for name in (*KNOWN, *_ALIASES, *_METHODS, *_ATTRIBUTES, *_BASES, *VARIABLES)
    for count in range(1, name.count(".") + 1)
)


def origins(tree: ast.Module) -> dict[str, str]:
    """Map each top-level name the module imports from the standard library to what it is.

    `import os` binds `os` to `os` (and `import os.path` binds `os` too); `import os.path as p`
    binds `p` to `os.path`; `from os import getpid as pid` binds `pid` to `os.getpid`. Only the
    modules the tables name are kept, and a relative import names no module here.

    Returns:
      Each bound name, mapped to its dotted origin.

    """
    return imported(tree.body)


def imported(body: Iterable[ast.stmt]) -> dict[str, str]:
    """Map the names the imports among `body` bind to what they are (see `origins`).

    Returns:
      Each bound name, mapped to its dotted origin.

    """
    return {name: origin for name, origin, module in import_bindings(body) if module in _TABLE_MODULES}


def resolved(func: ast.expr, bound: Mapping[str, str]) -> str | None:
    """Resolve a callee (`o.path.join`, `getpid`) through the module's imports (`bound`, see `origins`).

    Returns:
      Its dotted origin (`os.path.join`), or `None` if its first name isn't one the module imports.

    """
    name: str
    owner: ast.expr
    attr: str
    match func:
        case ast.Name(id=name) if name in bound:
            return bound[name]
        case ast.Attribute(value=owner, attr=attr):
            found: str | None = resolved(owner, bound)
            return None if found is None else f"{found}.{attr}"
        case _:
            return None


def library_member(
    receiver: str,
    name: str,
    call: ast.Call | None,
    known: Known,
    *,
    inherited: bool = False,
) -> Inference | None:
    """Type a standard-library class's attribute or property, or (`call`) its method's return.

    `receiver` is the annotation of what it's looked up on, as the module spells it
    (`ArgumentParser`, `argparse.ArgumentParser`), resolved through its imports and the ones `--fix`
    is adding to it; a class the member gives is spelled (and imported, if it must be) as the
    module can. The arguments of a call don't matter: the tables hold only what they can't change.
    `inherited`: whether it's looked up for a class under `receiver`, where a member that is
    `receiver` itself may be its `Self` (`Path.resolve()`), the inheriting class.

    Returns:
      Its inference, or `None` if the class or its member isn't in the tables, or a class it gives
      can't be named.

    """
    path: str | None = _class_path(receiver, known)
    found: str | None = (
        None if path is None else _member(_ATTRIBUTES if call is None else _METHODS, path, name)
    )
    if found is not None and inherited and found == path:
        return None
    plan: ImportPlan | None = known.names.plan
    if found is not None and is_class(found):
        found = None if plan is None else plan.spell(found)
    what: str = "annotation" if call is None else "return type"
    return (
        None
        if found is None
        else Inference(found, f"`{path}.{name}`'s {what} in typeshed", frozenset({_KIND}))
    )


def awaited_call(func: ast.expr, known: Known) -> Inference | None:
    """Type what awaiting a call of a standard-library `async def` gives (`await asyncio.start_server(...)`).

    Returns:
      Its inference, or `None` if `func` isn't one the tables hold, or its class can't be named.

    """
    path: str | None = resolved(func, known.names.stdlib)
    return None if path is None else _awaited(path, path, known)


def awaited_member(receiver: str, name: str, known: Known) -> Inference | None:
    """Type what awaiting a call of a standard-library class's `async def` method gives.

    `await reader.readline()`, on a receiver typed `asyncio.StreamReader`; and what `async with`
    binds, by `__aenter__`: the receiver's own type, where that returns `Self`.

    Returns:
      Its inference, or `None` if the class or its method isn't in the tables, or a class it gives
      can't be named.

    """
    path: str | None = _class_path(receiver, known)
    return None if path is None else _awaited(f"{path}.{name}", path, known, receiver)


def _awaited(entry: str, path: str, known: Known, receiver: str | None = None) -> Inference | None:
    found: str | None = _AWAITED.get(entry)
    plan: ImportPlan | None = known.names.plan
    if found is not None and found == path and receiver is not None:
        found = receiver  # its `Self`: the instance, as the module wrote its type
    elif found is not None and is_class(found):
        found = None if plan is None else plan.spell(found)
    return (
        None if found is None else Inference(found, f"`{entry}`'s return type, awaited", frozenset({_KIND}))
    )


def awaited_value(annotation: str, known: Known) -> str | None:
    """Find what awaiting a value typed `annotation` gives: `T`, of an `asyncio.Future[T]` or a `Task[T]`.

    Returns:
      It, as the annotation writes it; `None` for any other type.

    """
    path: str | None
    args: list[ast.expr]
    path, args = _receiver(annotation, known)
    return ast.unparse(args[-1]) if path in _AWAITABLE and args else None


def bases(tree: ast.Module, bound: Mapping[str, str]) -> dict[str, str]:
    """Spell the standard-library classes the module's classes inherit from (`unittest.TestCase`).

    Those the tables hold whole; and a generic one given all its arguments
    (`collections.OrderedDict[str, int]`), which decide its members' types: written with builtin
    types, dotted names and the module's own classes alone, not a type variable, which means
    nothing outside its class.

    Returns:
      Each, as the module's imports (`bound`, see `origins`) name it where it's a base, with its
      path in the tables (`""`: a generic one's, whose members its arguments type).

    """
    found: dict[str, str] = {}
    plain: frozenset[str] = _BUILTIN_NAMES | {node.name for node in classes(tree)}
    base: ast.expr
    for base in (base for node in classes(tree) for base in node.bases):
        head: ast.expr = base.value if isinstance(base, ast.Subscript) else base
        path: str = resolved(head, bound) or ""
        path = _ALIASES.get(path, path)
        given: int = 0
        if isinstance(base, ast.Subscript) and all(
            part.id in plain for part in ast.walk(base.slice) if isinstance(part, ast.Name)
        ):
            given = len(base.slice.elts) if isinstance(base.slice, ast.Tuple) else 1
        if given and len(_TYPE_PARAMETERS.get(path, "").split(",")) == given and path in _TYPE_PARAMETERS:
            found[ast.unparse(base)] = ""
        if not given and CLASSES.get(path) == path:
            found[ast.unparse(base)] = path
    return found


def members(path: str) -> frozenset[str]:
    """Name every member the tables hold of the class at `path`, its public ancestors' included.

    Returns:
      Them.

    """
    own: set[str] = set()
    table: _Own
    for table in (_METHODS, _ATTRIBUTES, _METHOD_OVERLOADS, _GENERIC_ATTRIBUTES):
        own.update(table.get(path, {}))
    return frozenset(own).union(*(members(ancestor) for ancestor in _ancestors(path)))


def lines(path: str) -> frozenset[str]:
    """Name the class at `path` and every public ancestor the tables give it.

    Returns:
      Their paths: two classes sharing one have an order between them the tables don't say.

    """
    return frozenset({path}).union(*(lines(ancestor) for ancestor in _ancestors(path)))


def enters_itself(receiver: str, known: Known) -> bool:
    """Check whether `receiver` is a standard-library class whose `__enter__` returns the instance itself.

    `receiver` is an annotation as the module spells it; its type arguments (`Popen[bytes]`) are the
    instance's, which `with` then gives as it is.

    Returns:
      Whether it is.

    """
    path: str | None = _receiver(receiver, known)[0]
    return path is not None and _member(_METHODS, path, _ENTER) == path


def _member(table: "_Own", path: str, name: str) -> str | None:
    """Look up a class's member in a table: its own entry, else its nearest public ancestor's.

    Returns:
      Its entry (an attribute's type, a method's return, a `method_signatures` entry), or `None`.

    """
    own: Mapping[str, str | None] = table.get(path, {})
    if name in own:
        return own[name]
    ancestor: str
    for ancestor in _ancestors(path):
        found: str | None
        if (found := _member(table, ancestor, name)) is not None:
            return found
    return None


@lru_cache(maxsize=1024)
def _ancestors(path: str) -> tuple[str, ...]:
    return tuple(_BASES[path].split(",")) if path in _BASES else ()


class Method(NamedTuple):
    """A standard-library method whose arguments decide its type, on a receiver of a known type.

    `entry`: its `method_signatures` entry; `instance`: the receiver's type arguments, if they're
    builtins (`Pattern[str]`'s `str`), for a signature declaring `self`'s; `types`: its class's type
    parameters, bound to the receiver's type arguments as the module spells them. For a receiver
    typed through an installed class's alias (`npt.NDArray[np.float64]`): `templates`, the class's
    type parameters as templates naming the alias's, and `matched`, the receiver's type as the class
    it stands for, which a method's `self` is matched against (see `signatures.Expansion`).
    """

    entry: str
    instance: list[str] | None
    types: dict[str, str]
    templates: Mapping[str, str] = MappingProxyType({})
    matched: str | None = None


def for_receiver(method: Method, receiver: str) -> Method:
    """Bind a method's `Self` to `receiver`: a class under the one it was found on has it as its own.

    Returns:
      The method, its `Self` (if it binds one) the receiver's type.

    """
    return method._replace(types={**method.types, _SELF: receiver}) if _SELF in method.types else method


def overloaded_method(receiver: str, name: str, known: Known) -> Method | None:
    """Find a standard-library class's method whose arguments decide its type (see `method_signatures`).

    Returns:
      It, or `None` if the receiver isn't such a class or the method isn't such a method.

    """
    path: str | None
    args: list[ast.expr]
    path, args = _receiver(receiver, known)
    entry: str | None = None if path is None else _member(_METHOD_OVERLOADS, path, name)
    if path is None or entry is None:
        return None
    texts: list[str] = [ast.unparse(arg) for arg in args]
    builtin: bool = all(
        isinstance(node, ast.Name) and node.id in _BUILTIN_NAMES and known.is_builtin(node.id)
        for arg in args
        for node in ast.walk(arg)
        if isinstance(node, ast.Name | ast.Attribute)
    )
    return Method(entry, texts if args and builtin else None, _bound(path, texts, receiver))


def operand(annotation: str, known: Known) -> str | None:
    """Name an operand's type as an operator's `takes` does: a builtin's name, or a class's path.

    Returns:
      It, or `None` for any other type: a union, a subscript, a class the tables don't have.

    """
    root: ast.expr = _parsed(annotation)
    if isinstance(root, ast.Name) and root.id in _BUILTIN_NAMES:
        return root.id if known.is_builtin(root.id) else None
    return _path(root, known) if isinstance(root, ast.Name | ast.Attribute) else None


def inherits(path: str, ancestor: str) -> bool:
    """Check whether the class at `path` is under `ancestor`, as far as the tables know its bases.

    Returns:
      Whether it is.

    """
    return any(base == ancestor or inherits(base, ancestor) for base in _ancestors(path))


def generic_attribute(receiver: str, name: str, known: Known) -> tuple[str, str, dict[str, str]] | None:
    """Find a class's attribute or property held as a template, on a receiver of a known type.

    A generic class's own (`string`, on an `re.Match[str]`), or one a class with no type parameters
    has or inherits (`parameters`, on an `inspect.Signature`).

    Returns:
      Its class's path, its template (see `_GENERIC_ATTRIBUTES`), and the class's type parameters
      bound to the receiver's type arguments as the module spells them; or `None`.

    """
    path: str | None
    args: list[ast.expr]
    path, args = _receiver(receiver, known)
    template: str | None = None
    if path is not None:
        template = (
            _GENERIC_ATTRIBUTES.get(path, {}).get(name)
            if path in _TYPE_PARAMETERS
            else _member(_GENERIC_ATTRIBUTES, path, name)
        )
    if path is None or template is None:
        return None
    return path, template, _bound(path, [ast.unparse(arg) for arg in args], receiver)


def element(receiver: str, known: Known) -> tuple[str, str, dict[str, str]] | None:
    """Find what iterating a standard-library class's instance gives (a `for` loop over a file: its lines).

    Returns:
      Its class's path, the element's template (see `_ELEMENTS`), and the class's type parameters
      bound to the receiver's type arguments as the module spells them; or `None`.

    """
    path: str | None
    args: list[ast.expr]
    path, args = _receiver(receiver, known)
    template: str | None = None if path is None else _ELEMENTS.get(path)
    if path is None or template is None:
        return None
    return path, template, _bound(path, [ast.unparse(arg) for arg in args], receiver)


def _receiver(receiver: str, known: Known) -> tuple[str | None, list[ast.expr]]:
    """Resolve a receiver's annotation to its class's path, and its type arguments (`re.Match[str]`'s `str`).

    Returns:
      The path (`None` if it's no standard-library class the module can name), and the arguments.

    """
    root: ast.expr = _parsed(receiver)
    args: list[ast.expr] = []
    if isinstance(root, ast.Subscript):
        args = list(root.slice.elts) if isinstance(root.slice, ast.Tuple) else [root.slice]
        root = root.value
    return _path(root, known), args


def _bound(path: str, texts: list[str], receiver: str) -> dict[str, str]:
    """Bind a generic class's type parameters to an instance's type arguments, if it gives them all.

    And `Self` to `receiver`, the instance's type as the module spells it: not a generic class
    named without its arguments.

    Returns:
      Each parameter's argument, by name; none if they don't match.

    """
    params: list[str] = [param.rstrip("=") for param in _TYPE_PARAMETERS.get(path, "").split(",") if param]
    if len(params) != len(texts):
        return {}
    return {**dict(zip(params, texts, strict=True)), _SELF: receiver}


def generics(bound: Mapping[str, str]) -> frozenset[str]:
    """Spell the standard library's generic classes as a module's imports (`bound`, see `origins`) name them.

    Returns:
      Each spelling (`StreamHandler`, `logging.StreamHandler`): written bare, one is missing its
      type arguments.

    """
    return frozenset(
        f"{name}{path.removeprefix(origin)}"
        for name, origin in bound.items()
        for path in _generic_paths(origin)
    )


def held_whole(path: str) -> str | None:
    """Find the class at `path` (or the one `path` is another name of), if the tables hold it whole.

    Returns:
      Its own path; `None` for anything else, a generic class included (see `bases`).

    """
    own: str = _ALIASES.get(path, path)
    return own if CLASSES.get(own) == own else None


def defines_class(path: str) -> bool:
    """Check whether `path` is a class the tables know: a plain one, or a generic one.

    Returns:
      Whether it is (`decimal.Decimal`, `operator.itemgetter`; not `os.path`, nor `logging.getLogger`).

    """
    return CLASSES.get(path) == path or path in _TYPE_PARAMETERS


def needs_arguments(path: str) -> bool:
    """Check whether `path` is a generic class of the standard library's that is missing arguments, bare.

    Returns:
      Whether it is (`operator.itemgetter`; not `io.BufferedReader`, whose parameter has a default).

    """
    return path in _generic_paths(path)


@lru_cache(maxsize=1024)
def _generic_paths(origin: str) -> tuple[str, ...]:
    """Find the generic classes an import's origin names (itself, or those in its module) that need arguments.

    Returns:
      Their paths.

    """
    return tuple(
        path
        for path, params in _TYPE_PARAMETERS.items()
        if (path == origin or path.startswith(f"{origin}."))
        and not all(param.endswith("=") for param in params.split(","))
    )


def evaluable(annotation: str, known: Known) -> bool:
    """Check that an annotation subscripts no standard-library class that can't be at run time.

    Nor a builtin iterator that can't (`zip[tuple[int, str]]`).

    Returns:
      Whether it can be evaluated (as a module's annotations are) without that `TypeError`.

    """
    node: ast.AST
    for node in ast.walk(_parsed(annotation)):
        if not isinstance(node, ast.Subscript):
            continue
        if isinstance(node.value, ast.Name) and node.value.id in _UNSUBSCRIPTABLE:
            return False
        path: str | None = _path(node.value, known)
        if path in _TYPE_PARAMETERS and path not in _SUBSCRIPTABLE:
            return False
    return True


def joins_path(left: str, right: str | None, known: Known) -> bool:
    """Check whether `left / right` joins a path: a `pathlib` class's `/` gives its own class back.

    Returns:
      Whether `left` is a `pathlib` path class's annotation, and `right` a `str`'s or the same.

    """
    return right in {"str", left} and is_path(left, known)


def is_path(receiver: str, known: Known) -> bool:
    """Check whether `receiver` is a `pathlib` path class's annotation.

    Returns:
      Whether it is.

    """
    return _class_path(receiver, known) in _PATHS


def _class_path(receiver: str, known: Known) -> str | None:
    """Resolve a receiver's annotation to a class's path in the tables (its own, not an alias).

    Returns:
      The path, or `None` if the annotation doesn't name a standard-library class the module imports
      (or `--fix` is importing).

    """
    return _path(_parsed(receiver), known)


def _path(root: ast.expr, known: Known) -> str | None:
    """Resolve a class's name or dotted path to its path in the tables (see `_class_path`).

    Returns:
      The path, or `None`.

    """
    path: str | None = resolved(root, known.names.stdlib)
    plan: ImportPlan | None = known.names.plan
    if path is None and plan is not None and plan.added:
        path = resolved(root, _added(tuple(plan.added.values())))
    if path is None and plan is not None and plan.guarded:
        path = _guarded(root, plan)
    if path is None and plan is not None and plan.checking.bound:
        path = resolved(root, plan.checking.bound)
    # A class's own path, where the module binds no name it starts with: a library base out of its
    # sight, as the index names it (see `constricter.fix.index.beyond`).
    if path is None and isinstance(root, ast.Attribute):  # a dotted path alone can be a class's own
        written: str = ast.unparse(root)
        if held_whole(written) and (plan is None or written.partition(".")[0] not in plan.taken):
            path = written
    return None if path is None else _ALIASES.get(path, path)


def _guarded(root: ast.expr, plan: ImportPlan) -> str | None:
    """Resolve a class's name or dotted path through an import for type checking (`ImportPlan.guarded`).

    One the module has, or `--fix` is adding for another file's type: the next run would resolve it
    by the import, so this one does.

    Returns:
      Its dotted origin, or `None` if its first name isn't such an import's.

    """
    first: str | None = next(
        (node.id for node in ast.walk(root) if isinstance(node, ast.Name) and node.id in plan.guarded),
        None,
    )
    if first is None:
        return None
    return resolved(root, {first: ".".join(part for part in plan.guarded[first].origin if part)})


@lru_cache(maxsize=256)
def _added(statements: tuple[str, ...]) -> Mapping[str, str]:
    """Map the names the imports `--fix` is adding bind (see `imported`), read once for all its lookups.

    Returns:
      Each bound name, mapped to its dotted origin: shared, so only read it.

    """
    return imported(ast.parse("\n".join(statements)).body)


@lru_cache(maxsize=4096)
def _parsed(annotation: str) -> ast.expr:
    """Parse an annotation, once for all its lookups.

    `annotation` is always `ast.unparse`'s own output, so it's always valid Python. The tree is
    shared: only read it.

    Returns:
      Its expression.

    """
    return ast.parse(annotation, mode="eval").body


def is_class(annotation: str) -> bool:
    """Check whether a table's annotation is a class's dotted path (`io.BytesIO`), not a builtin one.

    Returns:
      Whether it is.

    """
    return _DOT in annotation and all(part.isidentifier() for part in annotation.split(_DOT))
