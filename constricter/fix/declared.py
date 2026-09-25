# SPDX-License-Identifier: MIT
"""What an installed package's stub declares that a call's arguments may decide the type of.

`declarations` reads, from a module's top level: each function whose arguments decide its return
(`@overload`s, or a return naming a type variable) with its signatures as written; type aliases
(`X: TypeAlias = ...`, `type X[T] = ...`, `X = A | B`); type variables' bounds and constraints; and
protocols' members. All as source text, for `constricter.fix.stubbed` to resolve across modules
when a call needs them (`Module` keeps them, pickled into the installed modules' cache).
"""

import ast
from collections.abc import Iterator, Mapping
from typing import Final, NamedTuple, TypeAlias, cast

from constricter.rules.annotations import defined_type_vars, node_name

# A parameter: its name, kind (`p` positional only, `e` either, `k` keyword only, `a` `*args`,
# `w` `**kwargs`), whether it has a default, and its annotation's text (`None`: unannotated).
Param: TypeAlias = tuple[str, str, bool, str | None]
_OVERLOAD: Final = "overload"
_TYPE_VARIABLES: Final = frozenset({"TypeVar", "ParamSpec", "TypeVarTuple"})
_TYPE_VAR: Final = "TypeVar"
_TYPE_ALIAS: Final = "TypeAlias"
_PROTOCOL: Final = "Protocol"
_PROPERTIES: Final = frozenset({"property", "cached_property"})
_BOUND: Final = "bound"
_STAR: Final = "*"
_SELF: Final = "Self"  # a method returning its instance's own type


class Signature(NamedTuple):
    """One signature: its parameters, its return's text (`None`: unannotated), and its type parameters.

    `type_params`: its own (`def f[T: int]`), each with its bound's text, or `None`; a `ParamSpec`
    or `TypeVarTuple` has `"*"` for one.
    """

    params: tuple[Param, ...]
    returns: str | None
    type_params: tuple[tuple[str, str | None], ...] = ()
    self_typed: bool = False  # a method whose `self` is annotated: only some instances have it


class Class(NamedTuple):
    """A class: its type parameters (each with its bound's text, or `None`), and its methods' signatures.

    `bases`: its bases as written. `methods`: those whose arguments or instance decide their return:
    overloaded, naming a type variable, or any at all for a generic class (its parameters bind them);
    each signature without `self`.
    """

    params: tuple[tuple[str, str | None], ...]
    bases: tuple[str, ...]
    methods: Mapping[str, tuple[Signature, ...]]


class Alias(NamedTuple):
    """A type alias: its value's text, and its own type parameters (`type X[T] = ...`'s; else none)."""

    value: str
    params: tuple[str, ...] = ()


class Variable(NamedTuple):
    """A type variable: its bound's text, or its constraints joined with `|`; `constrained` says which."""

    bound: str | None
    constrained: bool = False


class Protocol(NamedTuple):
    """A protocol class: the members an instance needs, and whether one is a property."""

    members: frozenset[str]
    properties: bool


class Declarations(NamedTuple):
    """What `declarations` reads from a module (see the module docstring)."""

    signatures: Mapping[str, tuple[Signature, ...]]
    aliases: Mapping[str, Alias]
    variables: Mapping[str, Variable]
    protocols: Mapping[str, Protocol]
    # What another module may import from it, as type checkers read a typed package's interface:
    # its `__all__`, else its public definitions and redundant-alias imports (`from m import x as x`);
    # `None` where a `*` import leaves that open.
    exports: frozenset[str] | None = None
    # Classes generic only through a subscripted base (`class float64(floating[_64Bit])`), each with
    # the names in its bases' subscripts: generic if one is a type variable (see `installed`).
    bases: Mapping[str, frozenset[str]] = {}
    classes: Mapping[str, Class] = {}  # every class, for its methods


def declarations(tree: ast.Module) -> Declarations:
    """Read a stub's declarations (see the module docstring).

    Returns:
      Them.

    """
    type_vars: frozenset[str] = defined_type_vars(tree)
    signatures: dict[str, list[Signature]] = {}
    overloaded: set[str] = set()
    aliases: dict[str, Alias] = {}
    variables: dict[str, Variable] = {}
    protocols: dict[str, Protocol] = {}
    bases: dict[str, frozenset[str]] = {}
    classes: dict[str, Class] = {}
    names: frozenset[str] | None
    stmt: ast.stmt
    for stmt in tree.body:
        match stmt:
            case ast.FunctionDef():
                _signature(stmt, signatures, overloaded, type_vars)
            case ast.ClassDef():
                if any(node_name(base) == _PROTOCOL for base in _bases(stmt)):
                    protocols[stmt.name] = _protocol(stmt)
                if (names := _subscripted(stmt)) is not None:
                    bases[stmt.name] = names
                classes[stmt.name] = _class(stmt, type_vars, variables)
            case _:
                _assignment(stmt, aliases, variables)
    return Declarations(
        {name: tuple(found) for name, found in signatures.items() if found},
        aliases,
        variables,
        protocols,
        _exports(tree),
        bases,
        classes,
    )


def _class(node: ast.ClassDef, type_vars: frozenset[str], variables: Mapping[str, Variable]) -> Class:
    """Read a class's type parameters and its methods (see `Class`).

    Its own (`class C[T]`), else a `Generic[...]` or `Protocol[...]` base's, else the type variables
    its bases' subscripts name, in order.

    Returns:
      It.

    """
    own: tuple[tuple[str, str | None], ...] = tuple(_type_params(node))
    subscripts: list[ast.Subscript] = [base for base in node.bases if isinstance(base, ast.Subscript)]
    generic: list[ast.Subscript] = [
        base for base in subscripts if node_name(base.value) in {"Generic", _PROTOCOL}
    ]
    known: frozenset[str] = type_vars | variables.keys()
    names: list[str] = list(
        dict.fromkeys(
            found.id
            for base in (generic or subscripts)
            for found in ast.walk(base.slice)
            if isinstance(found, ast.Name) and (generic or found.id in known)
        ),
    )
    params: tuple[tuple[str, str | None], ...] = own or tuple(
        (name, None if name not in variables or variables[name].constrained else variables[name].bound)
        for name in names
    )
    signatures: dict[str, list[Signature]] = {}
    overloaded: set[str] = set()
    stmt: ast.stmt
    for stmt in node.body:
        if isinstance(stmt, ast.FunctionDef) and (stmt.args.posonlyargs or stmt.args.args):
            _signature(
                stmt,
                signatures,
                overloaded,
                known | {_SELF, *(name for name, _ in params)},
                every=bool(params),
            )
    return Class(
        params,
        tuple(ast.unparse(base) for base in node.bases),
        {name: tuple(_unbound(each) for each in found) for name, found in signatures.items() if found},
    )


def _unbound(signature: Signature) -> Signature:
    """Drop a method's `self` from its signature, noting whether it's annotated (not as `Self`).

    Returns:
      The signature.

    """
    annotation: str | None = signature.params[0][3]
    return signature._replace(
        params=signature.params[1:],
        self_typed=annotation is not None and annotation.rpartition(".")[2] != _SELF,
    )


def _subscripted(node: ast.ClassDef) -> frozenset[str] | None:
    """Name what a class's subscripted bases pass their type parameters, where that alone makes it generic.

    Returns:
      Those names; `None` for a class with type parameters of its own, a `Generic[...]` or
      `Protocol[...]` base, or no subscripted base.

    """
    subscripts: list[ast.Subscript] = [base for base in node.bases if isinstance(base, ast.Subscript)]
    if (
        not subscripts
        or cast("object", getattr(node, "type_params", ()))
        or any(node_name(base.value) in {"Generic", _PROTOCOL} for base in subscripts)
    ):
        return None
    return frozenset(
        found.id for base in subscripts for found in ast.walk(base.slice) if isinstance(found, ast.Name)
    )


def _exports(tree: ast.Module) -> frozenset[str] | None:
    """Name what a typed package's module exports (see `Declarations.exports`).

    Returns:
      Them, or `None` if a `*` import (without an `__all__`) makes that open.

    """
    listed: list[str] | None = None
    names: set[str] = set()
    starred: bool = False
    stmt: ast.stmt
    value: ast.expr
    for stmt in tree.body:
        match stmt:
            case ast.Assign(targets=[ast.Name(id="__all__")], value=value):
                listed = _strings(value)
            case ast.AugAssign(target=ast.Name(id="__all__"), op=ast.Add(), value=value):
                listed = [*(listed or []), *_strings(value)]
            case ast.Import() | ast.ImportFrom():
                starred |= any(alias.name == _STAR for alias in stmt.names)
                names.update(alias.name for alias in stmt.names if alias.asname == alias.name)
            case ast.FunctionDef() | ast.AsyncFunctionDef() | ast.ClassDef():
                names.add(stmt.name)
            case ast.Assign() | ast.AnnAssign():
                targets: list[ast.expr] = stmt.targets if isinstance(stmt, ast.Assign) else [stmt.target]
                names.update(target.id for target in targets if isinstance(target, ast.Name))
            case _ if type(stmt).__name__ == _TYPE_ALIAS:
                names.add(_type_alias(stmt)[0])
            case _:
                pass
    if listed is not None:
        return frozenset(listed)
    return None if starred else frozenset(name for name in names if not name.startswith("_"))


def _strings(value: ast.expr) -> list[str]:
    elements: list[ast.expr] = value.elts if isinstance(value, ast.List | ast.Tuple) else []
    return [e.value for e in elements if isinstance(e, ast.Constant) and isinstance(e.value, str)]


def _signature(
    node: ast.FunctionDef,
    signatures: dict[str, list[Signature]],
    overloaded: set[str],
    type_vars: frozenset[str],
    *,
    every: bool = False,
) -> None:
    """Add a function's signature: an `@overload` to those before it; a generic one as its only one.

    With `every` (a generic class's methods), any undecorated one with a return annotation too.
    """
    overload: bool = any(node_name(decorator) == _OVERLOAD for decorator in node.decorator_list)
    if node.name in overloaded:
        if overload:
            signatures[node.name].append(_read(node))
        return  # the implementation after the overloads, which callers don't see
    signature: Signature = _read(node)
    if overload:
        overloaded.add(node.name)
        signatures[node.name] = [signature]
    elif not node.decorator_list and (
        signature.type_params or _mentions(node.returns, type_vars) or (every and node.returns is not None)
    ):
        signatures[node.name] = [signature]
    else:
        signatures[node.name] = []  # defined again later: whichever is last is the one


def _read(node: ast.FunctionDef) -> Signature:
    """Read one signature as written.

    Returns:
      It.

    """
    args: ast.arguments = node.args
    positional: list[ast.arg] = [*args.posonlyargs, *args.args]
    first_default: int = len(positional) - len(args.defaults)
    params: list[Param] = [
        (arg.arg, "p" if at < len(args.posonlyargs) else "e", at >= first_default, _text(arg.annotation))
        for at, arg in enumerate(positional)
    ]
    if args.vararg is not None:
        params.append((args.vararg.arg, "a", True, _text(args.vararg.annotation)))
    params.extend(
        (arg.arg, "k", default is not None, _text(arg.annotation))
        for arg, default in zip(args.kwonlyargs, args.kw_defaults, strict=True)
    )
    if args.kwarg is not None:
        params.append((args.kwarg.arg, "w", True, _text(args.kwarg.annotation)))
    return Signature(tuple(params), _text(node.returns), tuple(_type_params(node)))


def _type_params(node: ast.AST) -> Iterator[tuple[str, str | None]]:
    """Read a definition's own type parameters (Python 3.12+'s `def f[T: int]`, `type X[T] = ...`).

    Yields:
      Each one's name and bound (`"*"` for a `ParamSpec` or `TypeVarTuple`).

    """
    param: ast.AST
    for param in cast("list[ast.AST]", getattr(node, "type_params", [])):
        name: str = cast("str", getattr(param, "name", ""))
        if type(param).__name__ == _TYPE_VAR:
            yield name, _text(cast("ast.expr | None", getattr(param, _BOUND, None)))
        else:
            yield name, "*"


def _mentions(annotation: ast.expr | None, type_vars: frozenset[str]) -> bool:
    return annotation is not None and any(
        isinstance(node, ast.Name) and node.id in type_vars for node in ast.walk(annotation)
    )


def _text(annotation: ast.expr | None) -> str | None:
    return None if annotation is None else ast.unparse(annotation)


def _bases(node: ast.ClassDef) -> Iterator[ast.expr]:
    base: ast.expr
    for base in node.bases:
        yield base.value if isinstance(base, ast.Subscript) else base


def _protocol(node: ast.ClassDef) -> Protocol:
    """Read a protocol's members: what its body defines or declares.

    Returns:
      It.

    """
    members: set[str] = set()
    properties: bool = False
    stmt: ast.stmt
    name: str
    for stmt in node.body:
        match stmt:
            case ast.FunctionDef() | ast.AsyncFunctionDef():
                members.add(stmt.name)
                properties |= any(node_name(d) in _PROPERTIES for d in stmt.decorator_list)
            case ast.AnnAssign(target=ast.Name(id=name)):
                members.add(name)
                properties = True  # an instance attribute: a class object's is its own
            case _:
                pass
    return Protocol(
        frozenset(members - {"__init__", "__new__", "__slots__", "__class_getitem__"}),
        properties,
    )


def _assignment(stmt: ast.stmt, aliases: dict[str, Alias], variables: dict[str, Variable]) -> None:
    """Read a type alias or a type variable a top-level statement declares, if it declares one."""
    func: ast.expr
    args: list[ast.expr]
    keywords: list[ast.keyword]
    annotation: ast.expr
    name: str
    value: ast.expr
    found: Alias
    match stmt:
        case ast.Assign(
            targets=[ast.Name(id=name)],
            value=ast.Call(func=func, args=args, keywords=keywords),
        ) if node_name(func).removeprefix("_") in _TYPE_VARIABLES:
            bound: ast.expr | None = next((k.value for k in keywords if k.arg == _BOUND), None)
            constraints: list[str] = [ast.unparse(arg) for arg in args[1:]]
            variables[name] = (
                Variable(" | ".join(constraints), constrained=True)
                if constraints
                else Variable(_text(bound) if node_name(func).removeprefix("_") == _TYPE_VAR else "*")
            )
        case ast.AnnAssign(target=ast.Name(id=name), annotation=annotation, value=ast.expr() as value) if (
            node_name(annotation) == _TYPE_ALIAS
        ):
            aliases[name] = Alias(ast.unparse(value))
        case ast.Assign(targets=[ast.Name(id=name)], value=value) if _type_expression(value):
            aliases[name] = Alias(ast.unparse(value))
        case _ if type(stmt).__name__ == _TYPE_ALIAS:  # `type X[T] = ...` (3.12+)
            name, found = _type_alias(stmt)
            aliases[name] = found
        case _:
            pass


def _type_alias(stmt: ast.stmt) -> tuple[str, Alias]:
    """Read Python 3.12+'s `type X[T] = ...` (an `ast.TypeAlias`, which 3.11's `ast` doesn't have).

    Returns:
      Its name, and it.

    """
    named: ast.Name = cast("ast.Name", getattr(stmt, "name", None))
    value: ast.expr = cast("ast.expr", getattr(stmt, "value", None))
    return named.id, Alias(ast.unparse(value), tuple(param for param, _ in _type_params(stmt)))


def _type_expression(value: ast.expr) -> bool:
    """Check whether an assignment's value may be a type (`A | B`, `list[int]`, `pkg.Class`), not a value.

    Returns:
      Whether it may.

    """
    match value:
        case ast.BinOp(op=ast.BitOr()) | ast.Subscript() | ast.Name() | ast.Attribute():
            return True
        case _:
            return False
