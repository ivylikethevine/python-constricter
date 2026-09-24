# SPDX-License-Identifier: MIT
"""Standard-library functions and classes whose types `--fix` knows, and how a module names them.

The tables are generated from typeshed's stubs into `tables/`, one JSON file each (see
`tests/typeshed/stdlib_tables.py`): `RETURNS` holds functions returning the same builtin type
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
from typing import Final, NamedTuple, NotRequired, Required, TypeAlias, TypedDict, cast

from constricter.fix.known import ImportPlan, Inference, Known
from constricter.rules.syntax import import_bindings

Constant: TypeAlias = bool | int | float | complex | str | bytes | None  # a literal's value


class Accepts(TypedDict, total=False):
    """Which argument types a parameter takes (see `constricter.fix.overloads`).

    `v`: a verdict (`y`, `n`, `?`) per `overloads.SCALARS` type, for an argument that isn't a
    literal; `c`: for a literal not among `lit` (its `Literal[...]` values), where that differs;
    `var`: the type variable the parameter is, and its type, for an argument of each type; or just
    its name, where each binds it to its own type (a `str` literal's `str`). `t`: the type variable
    the parameter is, unbounded, so any argument binds it to its own type (`copy.copy(x)`). `e`, for
    a parameter that is a generic class of one type variable (`Iterable[_T]`): that variable, which
    an argument of a builtin container in `of` (`list[str]`) binds to its type argument at that index.
    `r`: the type variable a callable parameter returns (`Callable[..., _T]`), which a function
    argument binds to its declared return (`functools.partial(helper, 1)`).
    """

    v: Required[str]
    c: str
    lit: list[Constant]
    var: str | dict[str, list[str]]
    t: str
    e: str
    of: dict[str, int]
    r: str


# A parameter: its name, kind (`p` positional, `e` either, `k` keyword, `a` `*args`, `w` `**kwargs`),
# whether it has a default, and what it takes (`None`: whatever every signature takes there). The
# tables write one every signature has alike as `"name kind"`, `=` after it if it has a default.
Parameter: TypeAlias = tuple[str, str, bool, Accepts | None]


class Signature(TypedDict):
    """One signature of a function whose arguments decide its type: its parameters, and its return.

    The return is a template (see `constricter.fix.overloads`), or `None` if `--fix` can't write it.
    `self`: for a generic class's method declaring its instance's type (`self: Pattern[str]`), the
    type arguments that instance must have.
    """

    params: list[Parameter | str]
    returns: str | None
    self: NotRequired[list[str]]


Variant: TypeAlias = list[Signature]  # one configuration's signatures, in order


def _table(name: str) -> object:
    """Read one of the tables (`tables/<name>.json`), plain JSON as generated.

    Returns:
      Its entries.

    """
    # Not through `jsonc`: its comment stripping took 20 ms of every run's start, for nothing.
    return cast(
        "object",
        json.loads(Path(__file__).with_name("tables").joinpath(f"{name}.json").read_bytes()),
    )


RETURNS: Final = cast("dict[str, str]", _table("returns"))
# Functions whose arguments decide their type: each signature, as each configuration reads them
# (see `constricter.fix.overloads`).
OVERLOADS: Final = cast("dict[str, list[Variant]]", _table("overloads"))
# Classes, and functions (constructors, classmethods) returning one: typed by that class's dotted
# path, spelled (and imported, if it must be) the way the module can.
CLASSES: Final = cast("dict[str, str]", _table("classes"))
_ALIASES: Final = cast("Mapping[str, str]", _table("aliases"))  # a class's other public paths, to its own
# Each class's methods' returns and attributes' types apart from its public ancestors' (`_BASES`),
# `None` where it hides one of theirs: `_member` resolves the rest through them.
_Own: TypeAlias = Mapping[str, Mapping[str, str | None]]
_METHODS: Final = cast("_Own", _table("methods"))
_ATTRIBUTES: Final = cast("_Own", _table("attributes"))
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
# (`re.Match`'s `string`: `AnyStr`), which its instance's type arguments bind.
_GENERIC_ATTRIBUTES: Final = cast("_Own", _table("generic_attributes"))


@cache
def method_signatures() -> dict[str, list[Variant]]:
    """Read the `method_signatures` table, the first time a call needs it.

    Returns:
      Each method's signatures (see `OVERLOADS`), by its entry.

    """
    return cast("dict[str, list[Variant]]", _table("method_signatures"))


# An environment lookup: `os.environ.get(k)` is `str | None`, with a `str` default it's `str`
# (`os.environ`'s generic `Mapping.get` decides it by the arguments).
ENVIRONMENT: Final = "os.environ.get"
_KIND: Final = "stdlib"  # the fix kind of what the tables type
_BUILTIN_NAMES: Final = frozenset({*dir(builtins), "None"})
_DOT: Final = "."
KNOWN: Final = frozenset({*RETURNS, *OVERLOADS, ENVIRONMENT, *CLASSES})  # every function the tables type
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
    return _imported(tree.body)


def _imported(body: Iterable[ast.stmt]) -> dict[str, str]:
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


def library_member(receiver: str, name: str, call: ast.Call | None, known: Known) -> Inference | None:
    """Type a standard-library class's attribute or property, or (`call`) its method's return.

    `receiver` is the annotation of what it's looked up on, as the module spells it
    (`ArgumentParser`, `argparse.ArgumentParser`), resolved through its imports and the ones `--fix`
    is adding to it; a class the member gives is spelled (and imported, if it must be) as the
    module can. The arguments of a call don't matter: the tables hold only what they can't change.

    Returns:
      Its inference, or `None` if the class or its member isn't in the tables, or a class it gives
      can't be named.

    """
    path: str | None = _class_path(receiver, known)
    found: str | None = (
        None if path is None else _member(_ATTRIBUTES if call is None else _METHODS, path, name)
    )
    plan: ImportPlan | None = known.names.plan
    if found is not None and is_class(found):
        found = None if plan is None else plan.spell(found)
    what: str = "annotation" if call is None else "return type"
    return (
        None
        if found is None
        else Inference(found, f"`{path}.{name}`'s {what} in typeshed", frozenset({_KIND}))
    )


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
    parameters, bound to the receiver's type arguments as the module spells them.
    """

    entry: str
    instance: list[str] | None
    types: dict[str, str]


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
    return Method(entry, texts if args and builtin else None, _bound(path, texts))


def generic_attribute(receiver: str, name: str, known: Known) -> tuple[str, str, dict[str, str]] | None:
    """Find a generic class's own attribute or property on a receiver of a known type (`re.Match[str]`).

    Returns:
      Its class's path, its template (see `_GENERIC_ATTRIBUTES`), and the class's type parameters
      bound to the receiver's type arguments as the module spells them; or `None`.

    """
    path: str | None
    args: list[ast.expr]
    path, args = _receiver(receiver, known)
    template: str | None = None if path is None else _GENERIC_ATTRIBUTES.get(path, {}).get(name)
    if path is None or template is None:
        return None
    return path, template, _bound(path, [ast.unparse(arg) for arg in args])


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


def _bound(path: str, texts: list[str]) -> dict[str, str]:
    """Bind a generic class's type parameters to an instance's type arguments, if it gives them all.

    Returns:
      Each parameter's argument, by name; none if they don't match.

    """
    params: list[str] = [param.rstrip("=") for param in _TYPE_PARAMETERS.get(path, "").split(",") if param]
    return dict(zip(params, texts, strict=True)) if texts and len(params) == len(texts) else {}


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

    Returns:
      Whether it can be evaluated (as a module's annotations are) without that `TypeError`.

    """
    node: ast.AST
    for node in ast.walk(_parsed(annotation)):
        path: str | None = _path(node.value, known) if isinstance(node, ast.Subscript) else None
        if path in _TYPE_PARAMETERS and path not in _SUBSCRIPTABLE:
            return False
    return True


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
        path = resolved(root, _imported(ast.parse("\n".join(plan.added.values())).body))
    return None if path is None else _ALIASES.get(path, path)


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
