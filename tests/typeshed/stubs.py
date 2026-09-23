# SPDX-License-Identifier: MIT
"""Typeshed's standard-library stubs, read as one platform and Python version would see them.

A stub's `if sys.platform == ...` and `if sys.version_info >= ...` blocks are decided for each
configuration (`Config`); a name bound under any other condition is `UNKNOWN` there. What a module
binds (`Namespace`) follows the stub conventions: a plain `import x` or `from m import y` binds a name
for the stub's own use, `import x as x`, `from m import y as y` and `from m import *` also export it,
and `__all__`, where a stub sets it, is what `*` imports from it.
"""

import ast
import operator
from collections.abc import Callable, Iterator
from dataclasses import dataclass, field
from pathlib import Path
from typing import Final, NamedTuple, TypeAlias

# A platform (`sys.platform`) and a Python 3 minor version (`sys.version_info`).
Config: TypeAlias = tuple[str, int]
PLATFORMS: Final = ("linux", "darwin", "win32")
MINORS: Final = (11, 12, 13, 14)  # the Python versions constricter supports
CONFIGS: Final = tuple((platform, minor) for platform in PLATFORMS for minor in MINORS)
_TYPE_VARIABLES: Final = frozenset({"TypeVar", "ParamSpec", "TypeVarTuple"})
_ALL: Final = "__all__"
_STAR: Final = "*"
_DOT: Final = "."
_PACKAGE: Final = "__init__"
_OVERLOAD: Final = "overload"
_TYPE_ALIAS: Final = "TypeAlias"
_ACCESSORS: Final = frozenset({"setter", "deleter"})  # a property's, which bind nothing new
_MAX_HOPS: Final = 40  # re-exports followed before giving up (a cycle)
_VERSION_PARTS: Final = 2  # `(3, 12)`: a comparison with a patch level decides nothing here
_Version: TypeAlias = tuple[int, int]  # a Python version: 3 and its minor version
_Comparison: TypeAlias = Callable[[_Version, _Version], bool]
_Operator: TypeAlias = type[ast.cmpop]
_COMPARISONS: Final[dict[_Operator, _Comparison]] = {
    ast.GtE: operator.ge,
    ast.Gt: operator.gt,
    ast.Lt: operator.lt,
    ast.LtE: operator.le,
}


class Function(NamedTuple):
    """A function, or an overloaded one's `@overload`s, in order."""

    defs: tuple[ast.FunctionDef | ast.AsyncFunctionDef, ...]


class Klass(NamedTuple):
    """A class."""

    node: ast.ClassDef


class Imported(NamedTuple):
    """A name imported from another module (`from module import name`), still to be followed."""

    module: str
    name: str


class ModuleRef(NamedTuple):
    """A module (`import module`, or `from package import module`)."""

    module: str


class Alias(NamedTuple):
    """A type alias (`X: TypeAlias = ...`, `X = int | str`), or an assignment that may be one."""

    value: ast.expr


class Variable(NamedTuple):
    """A variable, or an attribute in a class body, declared with its annotation."""

    annotation: ast.expr


class TypeVariable(NamedTuple):
    """A `TypeVar` (and the types it's constrained to, if it is), `ParamSpec` or `TypeVarTuple`."""

    name: str
    constraints: tuple[ast.expr, ...] = ()


class Unknown(NamedTuple):
    """A name bound under a condition this reading can't decide, or in a way it doesn't follow."""


UNKNOWN: Final = Unknown()
Binding: TypeAlias = Function | Klass | Imported | ModuleRef | Alias | Variable | TypeVariable | Unknown


@dataclass
class Namespace:
    """What a module or class body binds, which of those names it exports, and its `__all__`, if set."""

    names: dict[str, Binding] = field(default_factory=dict[str, Binding])
    public: set[str] = field(default_factory=set[str])
    all: list[str] | None = None


class Found(NamedTuple):
    """A name followed through its re-exports to where it's defined: that module, its name there, and what."""

    module: str
    name: str
    binding: Binding


def private(name: str) -> bool:
    """Check whether a name (or any part of a dotted one) is private: starts with `_`.

    Returns:
      Whether it is.

    """
    return any(part.startswith("_") for part in name.split(_DOT))


def truth(test: ast.expr, config: Config) -> bool | None:
    """Decide a stub's `if` condition on `sys.platform` and `sys.version_info` for `config`.

    Returns:
      Whether it holds, or `None` if it's any other condition.

    """
    text: str
    values: list[ast.expr]
    op: ast.cmpop
    boolean: ast.boolop
    operand: ast.expr
    match test:
        case ast.Compare(
            left=ast.Attribute(value=ast.Name(id="sys"), attr="platform"),
            ops=[ast.Eq() | ast.NotEq() as op],
            comparators=[ast.Constant(value=str() as text)],
        ):
            return (config[0] == text) == isinstance(op, ast.Eq)
        case ast.Compare(
            left=ast.Attribute(value=ast.Name(id="sys"), attr="version_info"),
            ops=[op],
            comparators=[ast.Tuple(elts=values)],
        ):
            return _version(op, values, config[1])
        case ast.Call(
            func=ast.Attribute(
                value=ast.Attribute(value=ast.Name(id="sys"), attr="platform"),
                attr="startswith",
            ),
            args=[ast.Constant(value=str() as text)],
        ):
            return config[0].startswith(text)
        case ast.UnaryOp(op=ast.Not(), operand=operand):
            decided: bool | None = truth(operand, config)
            return None if decided is None else not decided
        case ast.BoolOp(op=boolean, values=values):
            return _combined(
                [truth(value, config) for value in values],
                conjunction=isinstance(boolean, ast.And),
            )
        case _:
            return None


def _version(op: ast.cmpop, values: list[ast.expr], minor: int) -> bool | None:
    """Compare Python `3.minor` with a `sys.version_info` tuple of two whole numbers.

    Returns:
      The comparison, or `None` for any other tuple or operator.

    """
    parts: list[int] = [
        value.value
        for value in values
        if isinstance(value, ast.Constant)
        and isinstance(value.value, int)
        and not isinstance(value.value, bool)
    ]
    compare: _Comparison | None = _COMPARISONS.get(type(op))
    if compare is None or len(parts) != len(values) or len(parts) != _VERSION_PARTS:
        return None
    return compare((3, minor), (parts[0], parts[1]))


def _combined(parts: list[bool | None], *, conjunction: bool) -> bool | None:
    """Combine three-valued truths with `and` (`conjunction`) or `or`.

    Returns:
      The result, `None` when the unknown parts decide it.

    """
    decisive: bool  # what one part alone decides it to
    if (decisive := not conjunction) in parts:
        return decisive
    return None if None in parts else not decisive


def _bound(body: list[ast.stmt]) -> Iterator[str]:
    """Name everything a block of stub statements may bind, nested `if` blocks included.

    Yields:
      Each name.

    """
    stmt: ast.stmt
    name: str
    targets: list[ast.expr]
    for stmt in body:
        match stmt:
            case ast.If():
                yield from _bound(stmt.body + stmt.orelse)
            case ast.FunctionDef() | ast.AsyncFunctionDef() | ast.ClassDef():
                yield stmt.name
            case ast.Import() | ast.ImportFrom():
                yield from (alias.asname or alias.name.split(_DOT, 1)[0] for alias in stmt.names)
            case ast.AnnAssign(target=ast.Name(id=name)):
                yield name
            case ast.Assign(targets=targets):
                yield from (target.id for target in targets if isinstance(target, ast.Name))
            case _:
                pass


def _overload(node: ast.FunctionDef | ast.AsyncFunctionDef) -> bool:
    return any(decorator_name(decorator) == _OVERLOAD for decorator in node.decorator_list)


def decorator_name(decorator: ast.expr) -> str:
    """Name a decorator (or a call's function) by its last part: `overload`, `deprecated`, `setter`.

    Returns:
      The name, or `""` for any other expression.

    """
    name: str
    func: ast.expr
    match decorator:
        case ast.Name(id=name) | ast.Attribute(attr=name):
            return name
        case ast.Call(func=func):
            return decorator_name(func)
        case _:
            return ""


def _bind(space: Namespace, name: str, binding: Binding, *, export: bool | None = None) -> None:
    """Bind `name`, exported if `export` says (by default: if it isn't private)."""
    space.names[name] = binding
    if not private(name) if export is None else export:
        space.public.add(name)
    else:
        space.public.discard(name)


class Stubs:
    """The standard library's stubs in one typeshed checkout, read per configuration."""

    def __init__(self, typeshed: Path) -> None:
        """Parse every standard-library stub under `typeshed`, and its `VERSIONS` file."""
        stdlib: Path = typeshed / "stdlib"
        self._modules: dict[str, tuple[ast.Module, bool]] = {}
        path: Path
        for path in sorted(stdlib.rglob("*.pyi")):
            parts: list[str] = list(path.relative_to(stdlib).with_suffix("").parts)
            package: bool = parts[-1] == _PACKAGE
            module: str = _DOT.join(parts[:-1] if package else parts)
            self._modules[module] = (ast.parse(path.read_text(encoding="utf-8")), package)
        self._versions: dict[str, tuple[int, int | None]] = _read_versions(stdlib / "VERSIONS")
        self._spaces: dict[tuple[str, Config], Namespace | None] = {}
        self._class_spaces: dict[tuple[str, str, Config], Namespace] = {}

    def modules(self) -> list[str]:
        """List every module the stubs describe.

        Returns:
          Their dotted names, sorted.

        """
        return sorted(self._modules)

    def available(self, module: str, config: Config) -> bool:
        """Check whether `module` exists in `config`'s Python version, by `VERSIONS` (or its parent's).

        Returns:
          Whether it does.

        """
        parts: list[str] = module.split(_DOT)
        prefixes: list[str] = [_DOT.join(parts[:count]) for count in range(len(parts), 0, -1)]
        listed: str | None = next((prefix for prefix in prefixes if prefix in self._versions), None)
        if module not in self._modules or listed is None:
            return False
        first: int
        last: int | None
        first, last = self._versions[listed]
        return first <= config[1] and (last is None or config[1] <= last)

    def namespace(self, module: str, config: Config) -> Namespace | None:
        """Read what `module` binds and exports in `config`.

        Returns:
          Its namespace, or `None` if the module doesn't exist there.

        """
        key: tuple[str, Config]
        if (key := (module, config)) not in self._spaces:
            self._spaces[key] = None  # a cycle of star imports sees it as missing, not recursing
            if self.available(module, config):
                tree: ast.Module
                package: bool
                tree, package = self._modules[module]
                space: Namespace = Namespace()
                self._walk(tree.body, module if package else module.rpartition(_DOT)[0], config, space)
                self._spaces[key] = space
        return self._spaces[key]

    def class_namespace(self, module: str, node: ast.ClassDef, config: Config) -> Namespace:
        """Read what a class body (of a class defined at `module`'s top level) binds in `config`.

        Returns:
          Its namespace.

        """
        key: tuple[str, str, Config]
        if (key := (module, node.name, config)) not in self._class_spaces:
            space: Namespace = Namespace()
            self._walk(node.body, module, config, space)
            self._class_spaces[key] = space
        return self._class_spaces[key]

    def lookup(self, module: str, name: str, config: Config, hops: int = 0) -> Found | None:
        """Follow `module.name` through re-exports to its definition, in `config`.

        Returns:
          Where it's defined and what it is (a submodule `ModuleRef`), or `None` if it isn't there.

        """
        space: Namespace | None
        if (space := self.namespace(module, config)) is None or hops > _MAX_HOPS:
            return None
        submodule: str = f"{module}.{name}"
        origin: str
        imported: str
        binding: Binding | None = space.names.get(name)
        match binding:
            case None if self.available(submodule, config):
                return Found(module, name, ModuleRef(submodule))
            case None:
                return None
            case Imported(module=origin, name=imported):
                return self.lookup(origin, imported, config, hops + 1)
            case _:
                return Found(module, name, binding)

    def star(self, module: str, config: Config) -> list[str]:
        """Name what `from module import *` imports in `config`: its `__all__`, else its public names.

        Returns:
          The names.

        """
        space: Namespace | None
        if (space := self.namespace(module, config)) is None:
            return []
        return list(space.all) if space.all is not None else sorted(n for n in space.public if not private(n))

    def _walk(self, body: list[ast.stmt], package: str, config: Config, space: Namespace) -> None:
        """Bind what each statement of `body` binds in `config` into `space`."""
        stmt: ast.stmt
        test: ast.expr
        name: str
        decided: bool | None
        for stmt in body:
            match stmt:
                case ast.If(test=test):
                    if (decided := truth(test, config)) is None:
                        space.names.update(dict.fromkeys(_bound([stmt]), UNKNOWN))
                    else:
                        self._walk(stmt.body if decided else stmt.orelse, package, config, space)
                case ast.FunctionDef() | ast.AsyncFunctionDef():
                    _define(stmt, space)
                case ast.ClassDef(name=name):
                    _bind(space, name, Klass(stmt))
                case ast.Import() | ast.ImportFrom():
                    self._import(stmt, package, config, space)
                case _:
                    _assign(stmt, space)

    def _import(
        self,
        stmt: ast.Import | ast.ImportFrom,
        package: str,
        config: Config,
        space: Namespace,
    ) -> None:
        """Bind an import's names, exporting those it re-exports (`as` the same name, or `*`)."""
        alias: ast.alias
        if isinstance(stmt, ast.Import):
            for alias in stmt.names:
                top: str = alias.name.split(_DOT, 1)[0]
                if alias.asname:
                    _bind(space, alias.asname, ModuleRef(alias.name), export=alias.asname == alias.name)
                else:
                    _bind(space, top, ModuleRef(top), export=False)
            return
        origin: str = _absolute(stmt, package)
        for alias in stmt.names:
            if alias.name == _STAR:
                name: str
                for name in self.star(origin, config):
                    _bind(space, name, Imported(origin, name), export=True)
            elif alias.name == _ALL:
                space.all = self.star(origin, config)
            else:
                _bind(
                    space,
                    alias.asname or alias.name,
                    Imported(origin, alias.name),
                    export=alias.asname == alias.name,
                )


def _define(node: ast.FunctionDef | ast.AsyncFunctionDef, space: Namespace) -> None:
    """Bind a function, adding an `@overload` to the ones before it; a property's setter changes nothing."""
    if any(decorator_name(d) in _ACCESSORS for d in node.decorator_list):
        return
    prior: Binding | None = space.names.get(node.name)
    if _overload(node) and isinstance(prior, Function) and all(_overload(d) for d in prior.defs):
        _bind(space, node.name, Function((*prior.defs, node)))
    else:
        _bind(space, node.name, Function((node,)))


def _assign(stmt: ast.stmt, space: Namespace) -> None:
    """Bind what an assignment, annotated or not, binds."""
    name: str
    value: ast.expr
    annotation: ast.expr
    func: ast.expr
    args: list[ast.expr]
    match stmt:
        case ast.Assign(targets=[ast.Name(id="__all__")], value=value):
            space.all = _strings(value)
        case ast.AugAssign(target=ast.Name(id="__all__"), op=ast.Add(), value=value):
            space.all = [*(space.all or []), *_strings(value)]
        case ast.Assign(targets=[ast.Name(id=name)], value=ast.Call(func=func, args=args)) if (
            decorator_name(func) in _TYPE_VARIABLES
        ):
            _bind(space, name, TypeVariable(name, tuple(args[1:])))
        case (
            ast.Assign(targets=[ast.Name(id=name)], value=value)
            | ast.AnnAssign(
                target=ast.Name(id=name),
                annotation=ast.Name(id="TypeAlias") | ast.Attribute(attr="TypeAlias"),
                value=ast.expr() as value,
            )
        ):
            _bind(space, name, Alias(value))
        case ast.AnnAssign(target=ast.Name(id=name), annotation=annotation):
            _bind(space, name, Variable(annotation))
        case _:
            space.names.update(dict.fromkeys(_bound([stmt]), UNKNOWN))


def _strings(value: ast.expr) -> list[str]:
    """Read the strings a list or tuple display holds (an `__all__`).

    Returns:
      Them, in order.

    """
    elements: list[ast.expr] = value.elts if isinstance(value, ast.List | ast.Tuple) else []
    return [e.value for e in elements if isinstance(e, ast.Constant) and isinstance(e.value, str)]


def _absolute(stmt: ast.ImportFrom, package: str) -> str:
    """Resolve a `from` import's module, relative to `package` if it's a relative import.

    Returns:
      The module's dotted name.

    """
    if not stmt.level:
        return stmt.module or ""
    parts: list[str] = package.split(_DOT)
    base: str = _DOT.join(parts[: len(parts) - stmt.level + 1])
    return f"{base}.{stmt.module}" if stmt.module else base


def _read_versions(path: Path) -> dict[str, tuple[int, int | None]]:
    """Read typeshed's `VERSIONS`: each module's first and last Python 3 minor version (`None`: still there).

    Returns:
      Them, by module.

    """
    found: dict[str, tuple[int, int | None]] = {}
    line: str
    text: str
    for line in path.read_text(encoding="utf-8").splitlines():
        if not (text := line.partition("#")[0].strip()):
            continue
        module: str
        span: str
        module, _, span = text.partition(":")
        first: str
        last: str
        first, _, last = span.strip().partition("-")
        found[module.strip()] = (_minor(first), _minor(last) if last else None)
    return found


def _minor(version: str) -> int:
    return int(version.split(_DOT)[1])
