# SPDX-License-Identifier: MIT
"""Typeshed's standard-library stubs, read as one platform and Python version would see them.

`typeshed-client` reads each stub (`stdlib_tables.shed`): it decides the `if sys.platform == ...` and
`if sys.version_info >= ...` blocks for a configuration (`Config`), and lists what a module or a
class body binds. What a module binds (`Namespace`) follows the stub conventions: a plain `import x`
or `from m import y` binds a name for the stub's own use, `import x as x`, `from m import y as y`
and `from m import *` also export it, and `__all__`, where a stub sets it, is what `*` imports from
it. Whether a module exists in a Python version is typeshed's `VERSIONS`, to the submodule.
"""

import ast
import importlib
from collections.abc import Callable
from dataclasses import dataclass, field
from functools import partial
from pathlib import Path
from typing import Final, NamedTuple, Protocol, TypeAlias, cast

# A platform (`sys.platform`) and a Python 3 minor version (`sys.version_info`).
Config: TypeAlias = tuple[str, int]
PLATFORMS: Final = ("linux", "darwin", "win32")
MINORS: Final = (11, 12, 13, 14)  # the Python versions constricter supports
CONFIGS: Final = tuple((platform, minor) for platform in PLATFORMS for minor in MINORS)
_TYPE_VARIABLES: Final = frozenset({"TypeVar", "ParamSpec", "TypeVarTuple"})
_DOT: Final = "."
_PACKAGE: Final = "__init__"
_OVERLOAD: Final = "overload"
_BOUND: Final = "bound"  # a `TypeVar`'s upper bound's keyword
_DEFAULT: Final = "default"
_ACCESSORS: Final = frozenset({"setter", "deleter"})  # a property's, which bind nothing new
_MAX_HOPS: Final = 40  # re-exports followed before giving up (a cycle)


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
    bound: ast.expr | None = None
    default: ast.expr | None = None  # its default (PEP 696): a class it parameterises may go without


class Unknown(NamedTuple):
    """A name bound in a way this reading doesn't follow: one of an assignment's several targets."""


UNKNOWN: Final = Unknown()
Binding: TypeAlias = Function | Klass | Imported | ModuleRef | Alias | Variable | TypeVariable | Unknown


@dataclass
class Namespace:
    """What a module or class body binds, which of those names it exports, and its `__all__`, if set."""

    names: dict[str, Binding] = field(default_factory=dict[str, Binding])
    public: set[str] = field(default_factory=set[str])
    all: list[str] | None = None


_Starred: TypeAlias = Callable[[str], list[str]]  # what `from m import *` imports from a module
_Versions: TypeAlias = dict[str, tuple[int, int | None]]  # each module's first and last minor version


class Read(NamedTuple):
    """A stub to read: its module, whether that's a package's `__init__`, its file, and for what."""

    module: str
    package: bool
    path: Path
    config: Config


class _Shed(Protocol):  # pylint: disable=too-few-public-methods  # a module's functions
    """What's used of `stdlib_tables.shed`: imported as a stub is first read, `typeshed-client` with it."""

    # A module's or a class's body, read: `Stubs.star` names what a `from m import __all__` gives it.
    read: Callable[[ast.Module, Read, Path, _Starred], Namespace]
    versions: Callable[[Path], _Versions]  # `VERSIONS`, under a `stdlib`


def _shed() -> _Shed:
    return _typed(importlib.import_module("stdlib_tables.shed"))


def _typed(module: object) -> _Shed:
    return cast("_Shed", module)


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


def bind(space: Namespace, name: str, binding: Binding, *, export: bool | None = None) -> None:
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
        self._stdlib: Path = stdlib
        self._modules: dict[str, tuple[ast.Module, bool, Path]] = {}
        path: Path
        for path in sorted(stdlib.rglob("*.pyi")):
            parts: list[str] = list(path.relative_to(stdlib).with_suffix("").parts)
            package: bool = parts[-1] == _PACKAGE
            module: str = _DOT.join(parts[:-1] if package else parts)
            self._modules[module] = (ast.parse(path.read_text(encoding="utf-8")), package, path)
        self._versions: dict[str, tuple[int, int | None]] = _shed().versions(stdlib)
        self._spaces: dict[tuple[str, Config], Namespace | None] = {}
        self._class_spaces: dict[tuple[str, str, Config], Namespace] = {}
        self._found: dict[tuple[str, str, Config], Found | None] = {}

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
                self._spaces[key] = self._read(self._modules[module][0], module, config)
        return self._spaces[key]

    def class_namespace(self, module: str, node: ast.ClassDef, config: Config) -> Namespace:
        """Read what a class body (of a class defined at `module`'s top level) binds in `config`.

        Returns:
          Its namespace.

        """
        key: tuple[str, str, Config]
        if (key := (module, node.name, config)) not in self._class_spaces:
            body: ast.Module = ast.Module(body=node.body, type_ignores=[])
            self._class_spaces[key] = self._read(body, module, config)
        return self._class_spaces[key]

    def lookup(self, module: str, name: str, config: Config) -> Found | None:
        """Follow `module.name` through re-exports to its definition, in `config`.

        Returns:
          Where it's defined and what it is (a submodule `ModuleRef`), or `None` if it isn't there.

        """
        key: tuple[str, str, Config]
        if (key := (module, name, config)) not in self._found:
            self._found[key] = self._followed(module, name, config, 0)
        return self._found[key]

    def _followed(self, module: str, name: str, config: Config, hops: int) -> Found | None:
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
                return self._followed(origin, imported, config, hops + 1)
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

    def _read(self, body: ast.Module, module: str, config: Config) -> Namespace:
        """Read what `body` binds in `config`: `module`'s stub's, or that of a class of it.

        Returns:
          Its namespace.

        """
        package: bool
        path: Path
        _, package, path = self._modules[module]
        starred: Callable[[str], list[str]] = partial(self.star, config=config)
        return _shed().read(body, Read(module, package, path, config), self._stdlib, starred)


def define(node: ast.FunctionDef | ast.AsyncFunctionDef, space: Namespace) -> None:
    """Bind a function, adding an `@overload` to the ones before it; a property's setter changes nothing."""
    if any(decorator_name(d) in _ACCESSORS for d in node.decorator_list):
        return
    prior: Binding | None = space.names.get(node.name)
    if _overload(node) and isinstance(prior, Function) and all(_overload(d) for d in prior.defs):
        bind(space, node.name, Function((*prior.defs, node)))
    else:
        bind(space, node.name, Function((node,)))


def assign(stmt: ast.stmt, space: Namespace) -> None:
    """Bind what an assignment, annotated or not, binds."""
    name: str
    value: ast.expr
    annotation: ast.expr
    func: ast.expr
    args: list[ast.expr]
    keywords: list[ast.keyword]
    targets: list[ast.expr]
    match stmt:
        case ast.Assign(targets=[ast.Name(id="__all__")], value=value):
            space.all = _strings(value)
        case ast.AugAssign(target=ast.Name(id="__all__"), op=ast.Add(), value=value):
            space.all = [*(space.all or []), *_strings(value)]
        case ast.Assign(
            targets=[ast.Name(id=name)],
            value=ast.Call(func=func, args=args, keywords=keywords),
        ) if decorator_name(func).removeprefix("_") in _TYPE_VARIABLES:  # `TypeVar as _TypeVar` too
            bound: ast.expr | None = next((k.value for k in keywords if k.arg == _BOUND), None)
            default: ast.expr | None = next((k.value for k in keywords if k.arg == _DEFAULT), None)
            bind(space, name, TypeVariable(name, tuple(args[1:]), bound, default))
        case (
            ast.Assign(targets=[ast.Name(id=name)], value=value)
            | ast.AnnAssign(
                target=ast.Name(id=name),
                annotation=ast.Name(id="TypeAlias") | ast.Attribute(attr="TypeAlias"),
                value=ast.expr() as value,
            )
        ):
            bind(space, name, Alias(value))
        case ast.AnnAssign(target=ast.Name(id=name), annotation=annotation):
            bind(space, name, Variable(annotation))
        case ast.Assign(targets=targets):
            space.names.update(dict.fromkeys((t.id for t in targets if isinstance(t, ast.Name)), UNKNOWN))
        case _:
            pass


def _strings(value: ast.expr) -> list[str]:
    """Read the strings a list or tuple display holds (an `__all__`).

    Returns:
      Them, in order.

    """
    elements: list[ast.expr] = value.elts if isinstance(value, ast.List | ast.Tuple) else []
    return [e.value for e in elements if isinstance(e, ast.Constant) and isinstance(e.value, str)]
