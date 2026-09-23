# SPDX-License-Identifier: MIT
"""Standard-library functions and classes whose types `--fix` knows, and how a module names them.

The tables are generated from typeshed's stubs into `stdlib.json` (see
`tests/typeshed/stdlib_tables.py`): `RETURNS` holds functions returning the same builtin type
whatever their arguments; `ANY_STR` functions return the type of their arguments (`str` in, `str`
out; `bytes` in, `bytes` out), so they're typed only when those are known; `CLASSES` holds
non-generic classes, and functions returning one; `library_member` types those classes' methods
and attributes. A call is matched by the module and name it resolves to through the module's imports
(`origins`), not by how it's spelled, so `import os as o` then `o.getpid()`, or `from os import
getpid`, are the same call, and a `getpid` from anywhere else isn't.
"""

import ast
from collections.abc import Iterable, Mapping
from functools import lru_cache
from pathlib import Path
from typing import Final, TypeAlias, TypedDict, cast

from constricter.fix.known import ImportPlan, Inference, Known
from constricter.jsonc import loads

_Members: TypeAlias = Mapping[str, Mapping[str, str]]  # each class's members' annotations, by name


class _Tables(TypedDict):
    """`stdlib.json`'s tables (see `tests/typeshed/stdlib_tables.py`)."""

    returns: dict[str, str]
    any_str: list[str]
    classes: dict[str, str]
    aliases: dict[str, str]
    methods: dict[str, dict[str, str]]
    attributes: dict[str, dict[str, str]]


_TABLES: Final = cast("_Tables", loads(Path(__file__).with_name("stdlib.json").read_bytes()))
RETURNS: Final = _TABLES["returns"]
ANY_STR: Final = frozenset(_TABLES["any_str"])
# Classes, and functions (constructors, classmethods) returning one: typed by that class's dotted
# path, spelled (and imported, if it must be) the way the module can.
CLASSES: Final = _TABLES["classes"]
_ALIASES: Final[Mapping[str, str]] = _TABLES["aliases"]  # a class's other public paths, to its own
_METHODS: Final[_Members] = _TABLES["methods"]
_ATTRIBUTES: Final[_Members] = _TABLES["attributes"]
# An environment lookup: `os.environ.get(k)` or `os.getenv(k)` is `str | None`, with a `str` default
# it's `str` (`os.getenv`'s overloads, and `os.environ`'s generic `Mapping.get`, decide it by the
# arguments, which the tables leave out).
ENVIRONMENT: Final = frozenset({"os.environ.get", "os.getenv"})
BY_ARGUMENTS: Final = ANY_STR | ENVIRONMENT  # the functions typed by their arguments' types
_KIND: Final = "stdlib"  # the fix kind of what the tables type
_DOT: Final = "."
KNOWN: Final = frozenset({*RETURNS, *ANY_STR, *ENVIRONMENT, *CLASSES})  # every function the tables type
_TABLE_MODULES: Final = frozenset(
    name.rsplit(".", count)[0]
    for name in (*KNOWN, *_ALIASES, *_METHODS, *_ATTRIBUTES)
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
    found: dict[str, str] = {}
    stmt: ast.stmt
    module: str
    alias: ast.alias
    for stmt in body:
        match stmt:
            case ast.Import():
                for alias in stmt.names:
                    if alias.name.split(".", 1)[0] in _TABLE_MODULES:
                        found[alias.asname or alias.name.split(".", 1)[0]] = (
                            alias.name if alias.asname else alias.name.split(".", 1)[0]
                        )
            case ast.ImportFrom(module=str() as module, level=0) if module in _TABLE_MODULES:
                for alias in stmt.names:
                    found[alias.asname or alias.name] = f"{module}.{alias.name}"
            case _:
                pass
    return found


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
    table: _Members = _ATTRIBUTES if call is None else _METHODS
    found: str | None = None if path is None else table.get(path, {}).get(name)
    plan: ImportPlan | None = known.names.plan
    if found is not None and _is_class(found):
        found = None if plan is None else plan.spell(found)
    what: str = "annotation" if call is None else "return type"
    return (
        None
        if found is None
        else Inference(found, f"`{path}.{name}`'s {what} in typeshed", frozenset({_KIND}))
    )


def _class_path(receiver: str, known: Known) -> str | None:
    """Resolve a receiver's annotation to a class's path in the tables (its own, not an alias).

    Returns:
      The path, or `None` if the annotation doesn't name a standard-library class the module imports
      (or `--fix` is importing).

    """
    root: ast.expr = _parsed(receiver)
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


def _is_class(annotation: str) -> bool:
    """Check whether a table's annotation is a class's dotted path (`io.BytesIO`), not a builtin one.

    Returns:
      Whether it is.

    """
    return _DOT in annotation and all(part.isidentifier() for part in annotation.split(_DOT))
