# SPDX-License-Identifier: MIT
"""`--infer-from`: the types a traced run saw (`python -m constricter.trace`), as a type checker's hints are.

A trace holds, for each file by its SHA-256, the types each binding of its functions' locals held
(see `constricter.recording`). `hints` turns a file's into `Hints`, which `--fix` judges as it does a
checker's (`constricter.fix.values.hinted`): each a guess, of kind `traced`. Only for a local no
annotation types: one an assignment or a `for` loop binds to a value rooted at a parameter no
checker types (`row = rows[0].load()`, `for row in rows:`; see `_unannotated`), or at an attribute
of `self` its class stores nothing else in (see `_undeclared`). Anything else a type
checker may type wider than the run saw (an `X | None` that was never `None`, a base class, a
`TypedDict`), which the narrower annotation would make an error. A name bound more than once has
what all its bindings held, where each is such a binding the run reached. Up to three types seen
are their union, `None` last.

A class is shown bare (one defined in another as `Outer.Inner`), with the import that names it for
type checking alone (`Offered`), unless the file defines it: `constricter.fix.index.offers` then
takes only a class the index knows. One of a private module of the standard library has no hint.
"""

import ast
import hashlib
import json
import re
import sys
from collections.abc import Iterable, Iterator, Mapping, Sequence
from functools import cache
from pathlib import Path
from typing import Final, NamedTuple, TypeAlias, cast

from constricter import recording
from constricter.fix.core.known import Hints, Offered
from constricter.fix.values.hinted import TRACED

_LABEL: Final = "a traced run"
_SUFFIX: Final = ".py"
_MEMBERS: Final = 3  # how many types seen make a union
_CLASS: Final = re.compile(rf"([\w.]+){recording.SEPARATOR}([\w.]+)")
_STDLIB: Final = sys.stdlib_module_names
_SELF: Final = "self"
_TYPED: Final = frozenset({_SELF, "cls"})  # the parameters a class types, unannotated
_Function: TypeAlias = ast.FunctionDef | ast.AsyncFunctionDef
# Each binding's spellings, by its name, by its line.
_Bindings: TypeAlias = Mapping[int, Mapping[str, tuple[str, ...]]]


class Trace(NamedTuple):
    """A trace file: each file's bindings by its SHA-256, and the file each module named in it is."""

    files: Mapping[str, _Bindings]
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
    if found.get("version") != recording.VERSION:
        message: str = f"not a trace `python -m constricter.trace` version {recording.VERSION} wrote"
        raise ValueError(message)
    return Trace(
        {
            digest: {
                int(line): {
                    name: tuple(cast("list[str]", types))
                    for name, types in _table(held).items()
                    if isinstance(types, list)
                }
                for line, held in _table(_table(entry).get("bindings")).items()
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
    bindings: _Bindings = found.files.get(digest, {})
    try:
        tree: ast.Module | None = ast.parse(source) if bindings else None
    except (SyntaxError, ValueError):
        tree = None
    types: dict[tuple[int, int], str] = {}
    offered: dict[tuple[int, int], Offered] = {}
    stored: dict[int, frozenset[str]] = {} if tree is None else _undeclared(tree)
    node: ast.AST
    for node in ast.walk(tree) if tree is not None else ():
        targets: list[ast.Name]
        for targets in (
            _untyped(node, stored.get(id(node), frozenset())).values() if isinstance(node, _Function) else ()
        ):
            # A binding the run never reached may hold anything.
            seen: list[tuple[str, ...]] = [
                bindings.get(target.lineno, {}).get(target.id, ()) for target in targets
            ]
            typed: Offered | None = (
                _typed(sorted({spelling for each in seen for spelling in each}), found.modules, digest)
                if all(seen)
                else None
            )
            if typed is not None:
                types.update({(target.lineno, target.end_col_offset or 0): typed.text for target in targets})
            if typed is not None and typed.imports:
                offered.update({(target.lineno, target.end_col_offset or 0): typed for target in targets})
    return Hints(_LABEL, types, offered, TRACED) if types else None


def _typed(spellings: Sequence[str], modules: Mapping[str, str], digest: str) -> Offered | None:
    """Join a local's `spellings` into the annotation they make, with the imports its classes need.

    `modules`, `digest`: see `Trace.modules`, and the file's own SHA-256, whose classes need none.

    Returns:
      It, or `None`: nothing seen, something that couldn't be spelled, more than `_MEMBERS` types,
      two classes of one name, or one of a private module of the standard library.

    """
    if not spellings or recording.UNKNOWN in spellings or len(spellings) > _MEMBERS:
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
            # A class defined in another is imported by the outer one's name.
            if private or origins.setdefault(name.partition(".")[0], module) != module:
                return None
    return Offered(
        " | ".join(
            _CLASS.sub(r"\2", spelling)
            for spelling in sorted(spellings, key=lambda text: (text == recording.NONE, text))
        ),
        tuple(
            f"from {module} import {name}"
            for name, module in sorted(origins.items())
            if modules.get(module) != digest
        ),
    )


def _undeclared(tree: ast.Module) -> dict[int, frozenset[str]]:
    """Find the attributes of `self` no type checker types, in each method of a class with no base.

    Those the class's methods store only by a plain `self.x = value`, each value rooted at a
    parameter its method leaves unannotated, and the class's body doesn't bind: a checker types
    one by what's stored in it, so has no type for it.

    Returns:
      Them, by each such method's identity.

    """
    found: dict[int, frozenset[str]] = {}
    node: ast.AST
    for node in ast.walk(tree):
        if not isinstance(node, ast.ClassDef) or node.bases or node.keywords:
            continue
        methods: list[_Function] = [
            method
            for method in node.body
            if isinstance(method, _Function) and [arg.arg for arg in _params(method)][:1] == [_SELF]
        ]
        bound: set[str] = {
            each.name if isinstance(each, ast.ClassDef | _Function) else each.id
            for statement in node.body
            for each in (statement, *_own(statement))
            if isinstance(each, ast.ClassDef | _Function)
            or (isinstance(each, ast.Name) and isinstance(each.ctx, ast.Store))
        }
        plain: dict[str, bool] = {}  # whether each attribute stored is only ever stored so
        method: _Function
        for method in methods:
            rooted: set[str | None] = _unannotated(method)
            taken: set[int] = {
                id(statement.targets[0])
                for statement in ast.walk(method)
                if isinstance(statement, ast.Assign)
                and len(statement.targets) == 1
                and _root(statement.value)[0] in rooted
            }
            plain.update(
                {
                    store.attr: plain.get(store.attr, True) and id(store) in taken
                    for store in ast.walk(method)
                    if isinstance(store, ast.Attribute)
                    and isinstance(store.ctx, ast.Store | ast.Del)
                    and isinstance(store.value, ast.Name)
                    and store.value.id == _SELF
                },
            )
        attributes: frozenset[str] = frozenset(attr for attr, only in plain.items() if only) - bound
        found.update({id(method): attributes for method in methods})
    return found


def _params(function: _Function) -> list[ast.arg]:
    """List a function's parameters, in order.

    Returns:
      Them.

    """
    args: ast.arguments = function.args
    return [
        arg
        for arg in (*args.posonlyargs, *args.args, args.vararg, *args.kwonlyargs, args.kwarg)
        if arg is not None
    ]


def _unannotated(function: _Function) -> set[str | None]:
    """Name the parameters of a function no type checker has a type for.

    The unannotated ones (not `self` or `cls`, which its class types) it gives no default but
    `None` (a checker types one by its default), doesn't bind again, and doesn't test by a call
    (`isinstance(rows, list)`, a `TypeGuard`'s) or match, which narrows one.

    Returns:
      Them.

    """
    args: ast.arguments = function.args
    last: list[ast.arg] = [*args.posonlyargs, *args.args][::-1][: len(args.defaults)][::-1]
    defaults: list[tuple[ast.arg, ast.expr | None]] = [
        *zip(last, args.defaults, strict=True),
        *zip(args.kwonlyargs, args.kw_defaults, strict=True),
    ]
    typed: set[str] = {
        arg.arg
        for arg, default in defaults
        if default is not None and not (isinstance(default, ast.Constant) and default.value is None)
    }
    node: ast.AST
    for node in _own(function):
        if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Store):
            typed.add(node.id)
        elif isinstance(node, ast.Match) and isinstance(node.subject, ast.Name):
            typed.add(node.subject.id)
        elif isinstance(node, ast.If | ast.While | ast.IfExp | ast.Assert):
            typed.update(
                passed.id
                for call in ast.walk(node.test)
                if isinstance(call, ast.Call)
                for passed in (*call.args, *(keyword.value for keyword in call.keywords))
                if isinstance(passed, ast.Name)
            )
    return {arg.arg for arg in _params(function) if arg.annotation is None and arg.arg not in _TYPED | typed}


def _untyped(function: _Function, stored: frozenset[str]) -> dict[str, list[ast.Name]]:
    """Find the locals `function` binds only to values no annotation types.

    Each by a plain assignment or as a `for` loop's target, to a value rooted at a parameter it
    leaves unannotated (`rows[0].load()`, `make(n)`; not `self` or `cls`, which its class types),
    or at one of the attributes of `self` its class has `stored` so (`self.rows[0]`): a type checker
    has no type for it either, so none to set against what the run saw. Not one rooted at such a
    local, which a checker types by its new annotation.

    Returns:
      Each such name's bindings.

    """
    others: set[str] = {arg.arg for arg in _params(function)}
    rooted: set[str | None] = _unannotated(function)
    stores: list[ast.Name] = []
    node: ast.AST
    for node in _own(function):
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
    targets: list[ast.Name] = [
        target
        for target, value in _assigned(function)
        if _root(value)[0] in rooted or (_root(value)[0] == _SELF and _root(value)[1] in stored)
    ]
    others.update(store.id for store in stores if all(store is not target for target in targets))
    found: dict[str, list[ast.Name]] = {}
    target: ast.Name
    for target in targets:
        if target.id not in others:
            found.setdefault(target.id, []).append(target)
    return found


def _assigned(function: _Function) -> Iterator[tuple[ast.Name, ast.expr]]:
    """Find what binds one name to one value in a function's own scope, in order.

    Yields:
      Each plain assignment's name and value, and each `for` loop's target and what it loops over.

    """
    node: ast.AST
    for node in _own(function):
        target: ast.expr | None = None
        if isinstance(node, ast.Assign) and len(node.targets) == 1:
            target = node.targets[0]
        elif isinstance(node, ast.For | ast.AsyncFor):
            target = node.target
        if isinstance(node, ast.Assign | ast.For | ast.AsyncFor) and isinstance(target, ast.Name):
            yield target, node.value if isinstance(node, ast.Assign) else node.iter


def _root(value: ast.expr, attr: str | None = None) -> tuple[str | None, str | None]:
    """Find the name a value is taken from: `rows` in `rows[0].load()`, `make` in `make(n)`.

    `attr`: the attribute `value` is read for.

    Returns:
      It (`None` for a value that's computed some other way), and the attribute read of the name
      itself, if one is: `rows` in `self.rows[0].load()`.

    """
    if isinstance(value, ast.Attribute):
        return _root(value.value, value.attr)
    if isinstance(value, ast.Subscript | ast.Await):
        return _root(value.value)
    if isinstance(value, ast.Call):
        return _root(value.func)
    return (value.id if isinstance(value, ast.Name) else None, attr)


def _own(node: ast.AST) -> Iterator[ast.AST]:
    """Walk what a function's own scope holds: not what a function, class or comprehension inside it does.

    Yields:
      Each node under `node`, a nested scope's own node included.

    """
    child: ast.AST
    for child in ast.iter_child_nodes(node):
        yield child
        if not isinstance(child, recording.SCOPES):
            yield from _own(child)
