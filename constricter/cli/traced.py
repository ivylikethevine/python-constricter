# SPDX-License-Identifier: MIT
"""`--infer-from`: the types a traced run saw (`python -m constricter.trace`), as a type checker's hints are.

A trace holds, for each file by its SHA-256, the types each function's locals held when it returned
(see `constricter.trace`). `hints` turns a file's into `Hints`, which `--fix` judges as it does a
checker's (`constricter.fix.values.hinted`): each a guess, of kind `traced`. Only for a local no
annotation types: one assigned a value rooted at a parameter its function leaves unannotated
(`row = rows[0].load()`; not `self` or `cls`). Anything else a type checker may
type wider than the run saw (an `X | None` that was never `None`, a base class, a `TypedDict`),
which the narrower annotation would make an error. And only one its function binds once, outside any
loop: the trace says what it held last, not where. Up to three types seen are their union, `None`
last.

A class is shown bare, with the import that names it for type checking alone (`Offered`), unless
the file defines it: `constricter.fix.index.offers` then takes only a class the index knows. One of
a private module of the standard library has no hint.
"""

import ast
import hashlib
import json
import re
import sys
from collections import Counter
from collections.abc import Iterable, Iterator, Mapping, Sequence
from functools import cache
from pathlib import Path
from typing import Final, NamedTuple, TypeAlias, cast

from constricter import trace
from constricter.fix.core.known import Hints, Offered
from constricter.fix.values.hinted import TRACED

_LABEL: Final = "a traced run"
_SUFFIX: Final = ".py"
_MEMBERS: Final = 3  # how many types seen make a union
_CLASS: Final = re.compile(rf"([\w.]+){trace.SEPARATOR}(\w+)")
_STDLIB: Final = sys.stdlib_module_names
_TYPED: Final = frozenset({"self", "cls"})  # the parameters a class types, unannotated
_SCOPES: Final = (
    ast.FunctionDef,
    ast.AsyncFunctionDef,
    ast.ClassDef,
    ast.Lambda,
    ast.ListComp,
    ast.SetComp,
    ast.DictComp,
    ast.GeneratorExp,
)
_Function: TypeAlias = ast.FunctionDef | ast.AsyncFunctionDef
# Each function's locals' spellings, by name, by the function's first line.
_Functions: TypeAlias = Mapping[int, Mapping[str, tuple[str, ...]]]


class Trace(NamedTuple):
    """A trace file: each file's functions by its SHA-256, and the file each module named in it is."""

    files: Mapping[str, _Functions]
    modules: Mapping[str, str]


@cache
def load(path: Path) -> Trace:
    """Read the trace file at `path`, once.

    Returns:
      It.

    Raises:
      ValueError: It can't be read, or isn't a trace this version reads.

    """
    try:
        return _read(_table(cast("object", json.loads(path.read_text(encoding="utf-8")))))
    except (OSError, ValueError) as error:
        message: str = f"{path}: {error}"
        raise ValueError(message) from error


def _read(found: Mapping[str, object]) -> Trace:
    """Read a trace file's contents.

    Returns:
      The trace, without what isn't as the recorder writes it.

    Raises:
      ValueError: It isn't a trace this version reads.

    """
    if found.get("version") != trace.VERSION:
        message: str = f"not a trace `python -m constricter.trace` version {trace.VERSION} wrote"
        raise ValueError(message)
    return Trace(
        {
            digest: {
                int(line): {
                    name: tuple(cast("list[str]", types))
                    for name, types in _table(held).items()
                    if isinstance(types, list)
                }
                for line, held in _table(_table(entry).get("functions")).items()
                if line.isdecimal()
            }
            for digest, entry in _table(found.get("files")).items()
        },
        {name: digest for name, digest in _table(found.get("modules")).items() if isinstance(digest, str)},
    )


def _table(value: object) -> dict[str, object]:
    return cast("dict[str, object]", value) if isinstance(value, dict) else {}


def merged(
    hinted: Mapping[Path, tuple[Hints, ...]],
    found: Trace,
    paths: Iterable[Path],
) -> dict[Path, tuple[Hints, ...]]:
    """Add the trace's hints for each of `paths` after the type checkers' (`hinted`).

    Returns:
      Each file's hints.

    """
    every: dict[Path, tuple[Hints, ...]] = dict(hinted)
    path: Path
    for path in paths:
        try:
            traced: Hints | None = hints(found, path.read_bytes()) if path.suffix == _SUFFIX else None
        except OSError:  # checking it reports that
            continue
        if traced is not None:
            every[path] = (*every.get(path, ()), traced)
    return every


def hints(found: Trace, source: bytes) -> Hints | None:
    """Make the hints a trace has for a file's `source`.

    Returns:
      Them; `None` for a file the trace doesn't have as it is, or has nothing for.

    """
    digest: str = hashlib.sha256(source).hexdigest()
    functions: _Functions = found.files.get(digest, {})
    try:
        tree: ast.Module | None = ast.parse(source) if functions else None
    except (SyntaxError, ValueError):
        tree = None
    types: dict[tuple[int, int], str] = {}
    offered: dict[tuple[int, int], Offered] = {}
    node: ast.AST
    for node in ast.walk(tree) if tree is not None else ():
        if not isinstance(node, _Function):
            continue
        held: Mapping[str, tuple[str, ...]] = functions.get(
            min([node.lineno, *(decorator.lineno for decorator in node.decorator_list)]),
            {},
        )
        target: ast.Name
        for target in _untyped(node) if held else ():
            typed: Offered | None
            if (typed := _typed(held.get(target.id, ()), found.modules, digest)) is not None:
                where: tuple[int, int] = (target.lineno, target.end_col_offset or 0)
                types[where] = typed.text
                if typed.imports:
                    offered[where] = typed
    return Hints(_LABEL, types, offered, TRACED) if types else None


def _typed(spellings: Sequence[str], modules: Mapping[str, str], digest: str) -> Offered | None:
    """Join a local's `spellings` into the annotation they make, with the imports its classes need.

    `modules`, `digest`: see `Trace.modules`, and the file's own SHA-256, whose classes need none.

    Returns:
      It, or `None`: nothing seen, something that couldn't be spelled, more than `_MEMBERS` types,
      two classes of one name, or one of a private module of the standard library.

    """
    if not spellings or trace.UNKNOWN in spellings or len(spellings) > _MEMBERS:
        return None
    origins: dict[str, str] = {}
    spelling: str
    for spelling in spellings:
        module: str
        name: str
        for module, name in cast("list[tuple[str, str]]", _CLASS.findall(spelling)):
            private: bool = module.partition(".")[0] in _STDLIB and any(
                part.startswith("_") for part in module.split(".")
            )
            if private or origins.setdefault(name, module) != module:
                return None
    return Offered(
        " | ".join(
            _CLASS.sub(r"\2", spelling)
            for spelling in sorted(spellings, key=lambda text: (text == trace.NONE, text))
        ),
        tuple(
            f"from {module} import {name}"
            for name, module in sorted(origins.items())
            if modules.get(module) != digest
        ),
    )


def _untyped(function: _Function) -> list[ast.Name]:
    """Find the locals `function` binds once, outside any loop, to a value no annotation types.

    One rooted at a parameter it leaves unannotated (`rows[0].load()`, `make(n)`; not `self` or
    `cls`, which its class types): a type checker has no type for it either, so none to set against
    what the run saw. Not one rooted at such a local, which a checker types by its new annotation.

    Returns:
      Each such name's binding.

    """
    args: ast.arguments = function.args
    params: list[ast.arg] = [
        arg
        for arg in (*args.posonlyargs, *args.args, *args.kwonlyargs, args.vararg, args.kwarg)
        if arg is not None
    ]
    others: set[str] = {arg.arg for arg in params}
    rooted: set[str | None] = {arg.arg for arg in params if arg.annotation is None and arg.arg not in _TYPED}
    stores: list[ast.Name] = []
    looped: set[int] = set()  # the nodes a loop runs again
    node: ast.AST
    for node in _own(function):
        if isinstance(node, ast.For | ast.AsyncFor | ast.While):
            looped.update(id(inside) for inside in _own(node))
        if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Store):
            stores.append(node)
        elif isinstance(node, ast.Global | ast.Nonlocal):
            others.update(node.names)
        elif isinstance(node, ast.alias):
            others.add((node.asname or node.name).partition(".")[0])
        elif isinstance(node, ast.ExceptHandler | ast.MatchAs | ast.MatchStar) and node.name is not None:
            others.add(node.name)
        elif isinstance(node, ast.MatchMapping) and node.rest is not None:
            others.add(node.rest)
    counts: Counter[str] = Counter(store.id for store in stores)
    others.update(store.id for store in stores if id(store) in looped or counts[store.id] > 1)
    return [
        target for target, value in _assigned(function) if target.id not in others and _root(value) in rooted
    ]


def _assigned(function: _Function) -> Iterator[tuple[ast.Name, ast.expr]]:
    """Find the plain assignments of one name in a function's own scope, in order.

    Yields:
      Each one's name and value.

    """
    node: ast.AST
    for node in _own(function):
        if isinstance(node, ast.Assign) and len(node.targets) == 1:
            target: ast.expr = node.targets[0]
            if isinstance(target, ast.Name):
                yield target, node.value


def _root(value: ast.expr) -> str | None:
    """Find the name a value is taken from: `rows` in `rows[0].load()`, `make` in `make(n)`.

    Returns:
      It, or `None` for a value that's computed some other way.

    """
    if isinstance(value, ast.Attribute | ast.Subscript | ast.Await):
        return _root(value.value)
    if isinstance(value, ast.Call):
        return _root(value.func)
    return value.id if isinstance(value, ast.Name) else None


def _own(node: ast.AST) -> Iterator[ast.AST]:
    """Walk what a function's own scope holds: not what a function, class or comprehension inside it does.

    Yields:
      Each node under `node`, a nested scope's own node included.

    """
    child: ast.AST
    for child in ast.iter_child_nodes(node):
        yield child
        if not isinstance(child, _SCOPES):
            yield from _own(child)
