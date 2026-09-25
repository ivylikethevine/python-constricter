# SPDX-License-Identifier: MIT
"""Installed packages' functions whose arguments decide their type: their signatures, read for a call.

A stub's overloads (see `constricter.fix.declared`) are resolved across the installed modules the
index holds, into the signatures the standard library's tables hold (see
`constricter.fix.overloads`), so a call is matched the same way: which argument types each
parameter certainly takes or refuses, the type variables they bind, and the return as a template
naming classes by their public dotted paths. What they take is worked out from the parameter's
annotation, through aliases (a generic one's parameters bound by its arguments), type variables'
bounds, unions and `Literal`s: a builtin scalar by the `scalars` table for a standard-library
class (`SupportsIndex`), by its members for an installed protocol, and never by any other
installed class; a class passed as an argument (`dtype=np.float64`) by `type[...]`, which binds
its type variable to it.
"""

import ast
import builtins
from collections.abc import Iterator, Mapping, Sequence
from dataclasses import dataclass, field
from pathlib import Path
from typing import Final, NamedTuple, TypeAlias, cast

from constricter.fix import project, stdlib
from constricter.fix.declared import Alias, Declarations, Protocol, Signature, Variable
from constricter.fix.known import Origin
from constricter.fix.modules import SUFFIX, Index, Module, module_name
from constricter.fix.overloads import SCALARS
from constricter.fix.signatures import Accepts, Constant, Parameter, ReadSignature

_YES: Final = "y"
_NO: Final = "n"
_MAYBE: Final = "?"
_NONE: Final = "None"
_LITERAL_STRING: Final = "LiteralString"
_KIND: Final = "signatures"
# What an atom is (see `_Atom`).
_NONE_ATOM: Final = "none"
_LITERAL_ATOM: Final = "literal"
_VAR: Final = "var"
_ARG: Final = "arg"
_TYPE: Final = "type"
_CLASS: Final = "class"
_UNKNOWN_ATOM: Final = "unknown"
_OPTIONAL: Final = "Optional"
_LITERAL: Final = "Literal"
_ANNOTATED: Final = "Annotated"
_STR: Final = "str"  # `project.definition`'s kind for a function `Declarations` has
_BUILTINS_MODULE: Final = "builtins"
_BUILTINS: Final = frozenset(dir(builtins))
_TYPING: Final = frozenset({"typing", "typing_extensions"})
_ANYTHING: Final = frozenset(
    {"typing.Any", "typing_extensions.Any", "_typeshed.Incomplete", "builtins.object"},
)
_TYPES: Final = frozenset({"builtins.type", "typing.Type", "typing_extensions.Type"})
_UNIONS: Final = frozenset({"Union", "Optional"})  # `_OPTIONAL` too
_REFUSING: Final = frozenset({"Callable", "Type"})  # no scalar is a callable or a class
_MAX_DEPTH: Final = 20  # aliases followed before giving up
_PARAM_SPEC: Final = "*"  # a `ParamSpec`'s or `TypeVarTuple`'s bound (see `declared`)
_TYPE_VARIABLE: Final = "t"  # `Accepts`' key for an unbounded type variable
_CLASS_VERDICT: Final = "k"  # `Accepts`' key for a class argument's verdict
_CLASS_BINDS: Final = "kv"  # `Accepts`' key for the type variable a class argument binds


class _Scope(NamedTuple):
    """Where an annotation is read: its module, and the type parameters in scope.

    Each parameter is its bound's text (`None`: unbounded; `"*"`: a `ParamSpec`'s), or an
    argument an alias was subscripted with: its annotation and the scope that's read in.
    """

    module: Module
    params: Mapping[str, "str | tuple[ast.expr, _Scope] | None"]
    owner: str  # the module whose function is read: only its type variables are bound


class _Atom(NamedTuple):
    """One member of an annotation's union.

    `kind`: `none`, `literal` (`values`), `any`, `var` (a type variable `name`, bounded by `bound`
    read in `scope`), `type` (a `type[...]`, whose own atoms are `inner`), `class` (`origin`, and
    the installed module defining it, if one does), or `unknown`.
    """

    kind: str
    values: tuple[Constant, ...] = ()
    name: str = ""
    bound: str | None = None
    scope: _Scope | None = None
    inner: tuple["_Atom", ...] = ()
    origin: Origin = ("", None)
    module: Module | None = None
    subscripted: bool = False
    constrained: bool = False  # a type variable's `bound` is its constraints: it binds none of them


_UNKNOWN: Final = _Atom(_UNKNOWN_ATOM)
_Resolved: TypeAlias = "_Atom | tuple[Alias, _Scope, Origin]"


@dataclass
class _Memo:
    """Each installed function's signatures, read, for the index they were read from."""

    modules: Mapping[str, Module] | None = None
    read: dict[tuple[str, str], tuple[ReadSignature, ...]] = field(
        default_factory=dict[tuple[str, str], "tuple[ReadSignature, ...]"],
    )

    def of(self, modules: Mapping[str, Module]) -> dict[tuple[str, str], tuple[ReadSignature, ...]]:
        """Keep what's read for `modules` alone.

        Returns:
          What's read so far.

        """
        if modules is not self.modules:
            self.modules = modules
            self.read = {}
        return self.read


_MEMO: Final = _Memo()


def overloaded(catalog: Index, path: Path) -> dict[str, tuple[ReadSignature, ...]]:
    """Find the installed functions the file at `path` calls whose arguments decide their type.

    Returns:
      Each one's signatures (one variant, see `overloads.chosen`), by the call's name as written
      (`np.empty`); none for a file `catalog` doesn't have.

    """
    modules: dict[str, Module] = catalog.modules
    target: Module | None
    if path.suffix != SUFFIX or (target := modules.get(module_name(path))) is None:
        return {}
    found: dict[str, tuple[ReadSignature, ...]] = {}
    memo: dict[tuple[str, str], tuple[ReadSignature, ...]] = _MEMO.of(modules)
    key: str
    for key in sorted(target.called):
        origin: Origin | None = _callee(modules, target, key)
        defined: tuple[Module, str] | None
        if origin is None or (defined := project.definition(modules, origin, _KIND)) is None:
            continue
        where: tuple[str, str]
        if (where := (defined[0].name, defined[1])) not in memo:
            memo[where] = _signatures(modules, *defined)
        found[key] = memo[where]
    return found


def classes(catalog: Index, path: Path) -> frozenset[str]:
    """Find the installed classes the file at `path` passes as arguments (`dtype=np.float64`).

    A class, or an alias of one (`np.int32 = signedinteger[_32Bit]`), through any re-exports.

    Returns:
      Each as the file writes it; none for a file `catalog` doesn't have.

    """
    modules: dict[str, Module] = catalog.modules
    target: Module | None
    if path.suffix != SUFFIX or (target := modules.get(module_name(path))) is None:
        return frozenset()
    reader: _Reader = _Reader(modules)
    return frozenset(name for name in target.passed if reader.is_class(target, name))


def _callee(modules: Mapping[str, Module], target: Module, callee: str) -> Origin | None:
    """Find what a call's name refers to: `f`, `np.empty`, `pkg.util.f` through the module's imports.

    A package's attribute, re-exported from anywhere (`numpy.empty`), not just what it defines.

    Returns:
      Its origin, or `None`.

    """
    head: str
    parts: list[str]
    head, *parts = callee.split(".")
    origin: Origin | None = target.names.get(head)
    part: str
    for part in parts:
        if origin is None or origin[1] is not None:
            return None
        submodule: str = f"{origin[0]}.{part}"
        origin = (submodule, None) if submodule in modules else (origin[0], part)
    return origin


def _signatures(modules: Mapping[str, Module], module: Module, name: str) -> tuple[ReadSignature, ...]:
    """Read an installed function's signatures as the tables hold theirs.

    Returns:
      Them.

    """
    # Found by its declared signatures (`project.definition`): only an installed module has them.
    declared: Declarations = cast("Declarations", module.declared)
    written: tuple[Signature, ...] = declared.signatures[name]
    shared: set[tuple[str, str, bool, str | None]] = set(written[0].params)
    signature: Signature
    for signature in written[1:]:
        shared &= set(signature.params)
    variables: frozenset[str] = frozenset(
        {
            *declared.variables,
            *module.type_vars,
            *(param for each in written for param, _ in each.type_params),
        },
    )
    shared = {param for param in shared if not _names_any(param[3], variables)}
    reader: _Reader = _Reader(modules)
    return tuple(reader.signature(module, signature, shared) for signature in written)


def _names_any(annotation: str | None, names: frozenset[str]) -> bool:
    """Check whether an annotation names any of `names`.

    Returns:
      Whether it does.

    """
    if annotation is None:
        return False
    node: ast.AST
    for node in ast.walk(_parsed(annotation)):
        if isinstance(node, ast.Name) and node.id in names:
            return True
        if isinstance(node, ast.Constant) and isinstance(node.value, str) and _names_any(node.value, names):
            return True  # a forward reference
    return False


class _Reader:
    """Reads one function's signatures (see the module docstring)."""

    def __init__(self, modules: Mapping[str, Module]) -> None:
        """Read in `modules`."""
        self.modules: Mapping[str, Module] = modules

    def signature(
        self,
        module: Module,
        signature: Signature,
        shared: set[tuple[str, str, bool, str | None]],
    ) -> ReadSignature:
        """Read one signature: what each parameter takes, and its return as a template.

        A parameter every signature declares the same way, naming no type variable, takes whatever a
        call passes it (as the tables' do): only those that tell the signatures apart, or bind a
        type variable, are read.

        Returns:
          It.

        """
        scope: _Scope = _Scope(module, dict(signature.type_params), module.name)
        params: tuple[Parameter, ...] = tuple(
            (
                param[0],
                param[1],
                param[2],
                None
                if param in shared or param[3] is None
                else self._accepts(ast.parse(param[3], mode="eval").body, scope),
            )
            for param in signature.params
        )
        returns: str | None = (
            None
            if signature.returns is None
            else self._template(ast.parse(signature.returns, mode="eval").body, scope, 0)
        )
        return ReadSignature(params, returns, None)

    def _accepts(self, annotation: ast.expr, scope: _Scope) -> Accepts:
        """Work out what a parameter takes (see `stdlib.Accepts`).

        Returns:
          It.

        """
        atoms: list[_Atom] = list(self._atoms(annotation, scope, 0))
        literals: list[Constant] = [value for atom in atoms for value in atom.values]
        values: str = "".join(_verdict(atoms, scalar, constant=False) for scalar in SCALARS)
        found: Accepts = {"v": values, _CLASS_VERDICT: _combined({_class_verdict(atom) for atom in atoms})}
        if literals:
            found["lit"] = literals
            constants: str = "".join(_verdict(atoms, scalar, constant=True) for scalar in SCALARS)
            if constants != values:
                found["c"] = constants
        binds: dict[str, list[str]] = {}
        scalar: str
        for scalar in SCALARS:
            bound: tuple[str, str] | None
            if (bound := _binds(atoms, scalar, scope.owner)) is not None:
                binds[scalar] = [bound[0], bound[1]]
        if binds:
            found["var"] = binds
        if (
            len(atoms) == 1
            and atoms[0].kind == _VAR
            and atoms[0].bound is None
            and _own(atoms[0], scope.owner)
        ):
            found[_TYPE_VARIABLE] = atoms[0].name
        variable: str | None
        if (variable := _class_binds(atoms, scope.owner)) is not None:
            found[_CLASS_BINDS] = variable
        return found

    def _atoms(self, expr: ast.expr, scope: _Scope, hops: int) -> Iterator[_Atom]:
        """Split an annotation into its union's members, through aliases, `Optional`, `Union`, strings.

        Yields:
          Each member.

        """
        text: str
        left: ast.expr
        right: ast.expr
        if hops > _MAX_DEPTH:
            yield _UNKNOWN
            return
        match expr:
            case ast.Constant(value=None):
                yield _Atom(_NONE_ATOM)
            case ast.Constant(value=str() as text):
                yield from self._atoms(_parsed(text), scope, hops + 1)
            case ast.BinOp(left=left, op=ast.BitOr(), right=right):
                yield from self._atoms(left, scope, hops + 1)
                yield from self._atoms(right, scope, hops + 1)
            case ast.Subscript():
                yield from self._subscript_atoms(expr, scope, hops)
            case ast.Name() | ast.Attribute():
                yield from self._named_atoms(expr, scope, hops, ())
            case _:
                yield _UNKNOWN

    def _named_atoms(
        self,
        expr: ast.Name | ast.Attribute,
        scope: _Scope,
        hops: int,
        args: Sequence[ast.expr],
    ) -> Iterator[_Atom]:
        """Read a name an annotation uses, subscripted with `args` (none if it isn't).

        Yields:
          Its atoms: an alias's, bound by `args`; else the one it is.

        """
        resolved: _Resolved | None
        if (resolved := self.resolve(expr, scope)) is None:
            yield _UNKNOWN
        elif not isinstance(resolved, _Atom):
            alias: Alias
            where: _Scope
            alias, where, _ = resolved
            yield from self._atoms(_parsed(alias.value), _bound_alias(alias, where, args, scope), hops + 1)
        elif resolved.kind == _ARG:
            yield from self._atoms(*_argument(resolved), hops + 1)
        elif (
            resolved.kind == _VAR and resolved.scope is not None and resolved.bound not in {None, _PARAM_SPEC}
        ):
            bound: ast.expr = _parsed(resolved.bound or "")
            yield resolved._replace(inner=tuple(self._atoms(bound, resolved.scope, hops + 1)))
        else:
            yield resolved._replace(subscripted=bool(args))

    def _subscript_atoms(self, expr: ast.Subscript, scope: _Scope, hops: int) -> Iterator[_Atom]:
        args: list[ast.expr] = list(expr.slice.elts) if isinstance(expr.slice, ast.Tuple) else [expr.slice]
        base: ast.expr = expr.value
        if not isinstance(base, ast.Name | ast.Attribute):
            yield _UNKNOWN
            return
        path: str | None = self._external(base, scope)
        if path is not None and path.rpartition(".")[0] in _TYPING:
            name: str = path.rpartition(".")[2]
            if name in _UNIONS:
                members: list[ast.expr] = [*args, *([ast.Constant(None)] if name == _OPTIONAL else [])]
                yield from (atom for member in members for atom in self._atoms(member, scope, hops + 1))
                return
            if name == _LITERAL:
                yield _Atom(_LITERAL_ATOM, tuple(_literal_values(args)))
                return
            if name == _ANNOTATED:
                yield from self._atoms(args[0], scope, hops + 1)
                return
        if path in _TYPES:
            yield _Atom(_TYPE, inner=tuple(self._atoms(args[0], scope, hops + 1)))
            return
        yield from self._named_atoms(base, scope, hops, args)

    def _external(self, expr: ast.Name | ast.Attribute, scope: _Scope) -> str | None:
        """Name what an annotation's name refers to outside the installed modules (`typing.Union`).

        Returns:
          Its dotted path, or `None` if it's an installed module's, or unknown.

        """
        resolved: _Resolved | None = self.resolve(expr, scope)
        if not isinstance(resolved, _Atom) or resolved.kind != _CLASS or resolved.module is not None:
            return None
        return _path(resolved)

    def resolve(self, expr: ast.Name | ast.Attribute, scope: _Scope) -> _Resolved | None:
        """Resolve a name an annotation uses: a type parameter, a class, an alias, a type variable.

        Returns:
          It as an atom (`arg`: a parameter an alias's argument binds), or an alias with the scope
          its value is read in; or `None` if it's none of them.

        """
        origin: Origin | None
        if isinstance(expr, ast.Name) and expr.id in scope.params:
            param: str | tuple[ast.expr, _Scope] | None = scope.params[expr.id]
            if isinstance(param, tuple):
                return _Atom(_ARG, name=ast.unparse(param[0]), scope=param[1])
            return _Atom(_VAR, name=expr.id, bound=param, scope=scope)
        if (origin := self._origin(expr, scope.module)) is None or origin[1] is None:
            return None
        origin = project.canonical_origin(self.modules, origin)
        defining: Module | None = self.modules.get(origin[0])
        if defining is None or not defining.installed:
            return _Atom(_CLASS, origin=origin)
        return self._declared(defining, origin)

    def is_class(self, target: Module, name: str) -> bool:
        """Check whether a dotted name the module writes (`np.float64`) is an installed class or its alias.

        Returns:
          Whether it is.

        """
        origin: Origin | None = _callee(self.modules, target, name)
        resolved: _Resolved | None = (
            None
            if origin is None or origin[1] is None
            else self._declared_of(project.canonical_origin(self.modules, origin))
        )
        if resolved is not None and not isinstance(resolved, _Atom):  # an alias: of a class?
            value: ast.expr = _parsed(resolved[0].value)
            base: ast.expr = value.value if isinstance(value, ast.Subscript) else value
            resolved = self.resolve(base, resolved[1]) if isinstance(base, ast.Name | ast.Attribute) else None
        return isinstance(resolved, _Atom) and resolved.kind == _CLASS and resolved.module is not None

    def _declared_of(self, origin: Origin) -> _Resolved | None:
        defining: Module | None = self.modules.get(origin[0])
        return None if defining is None or not defining.installed else self._declared(defining, origin)

    @staticmethod
    def _declared(module: Module, origin: Origin) -> _Resolved | None:
        """Read what an installed module defines under `origin`'s name: an alias, a type variable, a class.

        Returns:
          It, or `None` for anything else (a function, a variable).

        """
        name: str = origin[1] or ""
        declared: Declarations | None = module.declared
        own: _Scope = _Scope(module, {}, module.name)
        if declared is not None and name in declared.aliases:
            return declared.aliases[name], own, origin
        variable: Variable | None
        if (variable := None if declared is None else declared.variables.get(name)) is not None:
            return _Atom(_VAR, name=name, bound=variable.bound, scope=own, constrained=variable.constrained)
        if (
            name in module.classes
            or name in module.generics
            or (declared is not None and name in declared.protocols)
        ):
            return _Atom(_CLASS, origin=origin, module=module)
        return None

    def _origin(self, expr: ast.Name | ast.Attribute, module: Module) -> Origin | None:
        """Find what a (dotted) name refers to in `module`: an import, its own, or a builtin.

        Returns:
          Its origin (a module's: `(name, None)`), or `None`.

        """
        if isinstance(expr, ast.Name):
            declared: Declarations | None = module.declared
            return (
                ((module.name, expr.id) if declared is not None and expr.id in declared.aliases else None)
                or module.names.get(expr.id)
                or module.guarded.get(expr.id)
                or ((_BUILTINS_MODULE, expr.id) if expr.id in _BUILTINS else None)
            )
        if not isinstance(expr.value, ast.Name | ast.Attribute):
            return None
        base: Origin | None
        if (base := self._origin(expr.value, module)) is None:
            return None
        if base[1] is None:  # a module's attribute, or its submodule
            submodule: str = f"{base[0]}.{expr.attr}"
            return (submodule, None) if submodule in self.modules else (base[0], expr.attr)
        return None

    def _template(self, expr: ast.expr, scope: _Scope, hops: int) -> str | None:
        """Write an annotation as a template: classes by their public dotted paths, type variables bare.

        A private alias is written as what it stands for, its parameters bound by its arguments.

        Returns:
          The template, or `None` if it names something `--fix` can't write (`Any`, a `Literal`, a
          class with no public path, a type variable from elsewhere).

        """
        text: str
        left: ast.expr
        right: ast.expr
        base: ast.Name | ast.Attribute
        found: str | None = None
        match expr:
            case _ if hops > _MAX_DEPTH:
                pass
            case ast.Constant(value=None):
                found = _NONE
            case ast.Constant(value=builtins.Ellipsis):
                found = "..."
            case ast.Constant(value=str() as text):
                found = self._template(_parsed(text), scope, hops + 1)
            case ast.BinOp(left=left, op=ast.BitOr(), right=right):
                found = _joined(" | ", [self._template(side, scope, hops + 1) for side in (left, right)])
            case ast.Subscript(value=ast.Name() | ast.Attribute() as base):
                args: list[ast.expr] = (
                    list(expr.slice.elts) if isinstance(expr.slice, ast.Tuple) else [expr.slice]
                )
                found = self._named_template(base, scope, hops, args)
            case ast.Name() | ast.Attribute():
                found = self._named_template(expr, scope, hops, [])
            case _:
                pass
        return found

    def _named_template(
        self,
        expr: ast.Name | ast.Attribute,
        scope: _Scope,
        hops: int,
        args: Sequence[ast.expr],
    ) -> str | None:
        """Write a name, subscripted with `args` (none if it isn't), as a template.

        Returns:
          It, or `None`.

        """
        resolved: _Resolved | None = self.resolve(expr, scope)
        written: str | None
        if resolved is None:
            return None
        if not isinstance(resolved, _Atom):
            alias: Alias
            where: _Scope
            origin: Origin
            alias, where, origin = resolved
            public: Origin = project.public_origin(self.modules, origin)
            if not _private(public[0]) and not _private(public[1]):
                written = f"{public[0]}.{public[1]}"
            else:
                return self._template(_parsed(alias.value), _bound_alias(alias, where, args, scope), hops + 1)
        elif resolved.kind == _ARG:
            return self._template(*_argument(resolved), hops + 1)
        elif resolved.kind == _VAR:
            written = resolved.name if _own(resolved, scope.owner) else None
        else:
            written = self._class_path(resolved)
        if written is None or not args:
            return written
        texts: list[str | None] = [self._template(arg, scope, hops + 1) for arg in args]
        return None if None in texts else f"{written}[{', '.join(t for t in texts if t is not None)}]"

    def _class_path(self, atom: _Atom) -> str | None:
        """Write a class as a template names it: a builtin bare, any other by its public dotted path.

        Returns:
          It, or `None` for `typing`'s forms, `object`, `type`, or a class with no public path.

        """
        origin: Origin = atom.origin
        if atom.module is not None:
            origin = project.public_origin(self.modules, origin)
        elif origin[0] == _BUILTINS_MODULE:
            return origin[1] if origin[1] not in {"object", "type"} else None
        elif origin[0] in _TYPING:
            return None
        return None if _private(origin[0]) or _private(origin[1]) else f"{origin[0]}.{origin[1]}"


def _path(atom: _Atom) -> str:
    """Name a class atom by its dotted path (`typing.SupportsIndex`).

    Returns:
      It.

    """
    return f"{atom.origin[0]}.{atom.origin[1]}"


def _own(atom: _Atom, owner: str) -> bool:
    """Check that a type variable is the function's own: one of its type parameters, or its module's.

    Returns:
      Whether it is.

    """
    return atom.scope is not None and atom.scope.module.name == owner


def _argument(atom: _Atom) -> tuple[ast.expr, _Scope]:
    """Read back the argument an alias's parameter was bound to (an `arg` atom).

    Returns:
      Its annotation, and the scope it's read in.

    """
    scope: _Scope | None = atom.scope
    assert scope is not None  # an `arg` atom always has one  # ruff: ignore[assert]
    return _parsed(atom.name), scope


def _bound_alias(alias: Alias, where: _Scope, args: Sequence[ast.expr], caller: _Scope) -> _Scope:
    """Scope an alias's value: its type parameters bound to the arguments it's subscripted with.

    Its own (`type X[T] = ...`), or else the type variables its value names, in order; one without
    an argument stays unbound (any type).

    Returns:
      The scope.

    """
    params: tuple[str, ...] = alias.params or _free_variables(alias.value, where)
    bound: dict[str, str | tuple[ast.expr, _Scope] | None] = dict.fromkeys(params)
    name: str
    arg: ast.expr
    for name, arg in zip(params, args, strict=False):
        bound[name] = (arg, caller)
    return _Scope(where.module, bound, caller.owner)


def _free_variables(value: str, scope: _Scope) -> tuple[str, ...]:
    """Name the type variables an old-style alias's value names (its parameters), in order.

    Returns:
      Them.

    """
    declared: Declarations | None = scope.module.declared
    variables: Mapping[str, Variable] = {} if declared is None else declared.variables
    return tuple(
        dict.fromkeys(
            node.id
            for node in ast.walk(_parsed(value))
            if isinstance(node, ast.Name) and (node.id in variables or node.id in scope.module.type_vars)
        ),
    )


def _verdict(atoms: Sequence[_Atom], scalar: str, *, constant: bool) -> str:
    """Decide whether an annotation's atoms take an argument of type `scalar` (a literal one if `constant`).

    Returns:
      `y` if one certainly does, `n` if none does, else `?`.

    """
    return _combined({_scalar_verdict(atom, scalar, constant=constant) for atom in atoms})


def _combined(verdicts: set[str]) -> str:
    if _YES in verdicts:
        return _YES
    return _NO if verdicts == {_NO} else _MAYBE


def _scalar_verdict(atom: _Atom, scalar: str, *, constant: bool) -> str:
    """Decide whether one atom takes an argument of type `scalar`.

    Returns:
      The verdict.

    """
    match atom.kind:
        case "none":
            return _YES if scalar == _NONE else _NO
        case "literal":
            types: set[str] = {type(value).__name__ if value is not None else _NONE for value in atom.values}
            matches: bool = scalar in types or (scalar == _LITERAL_STRING and _STR in types)
            return _NO if constant or not matches else _MAYBE
        case "var":
            return _bound_verdict(atom, scalar)
        case "type":
            return _NO
        case "class":
            return _class_takes(atom, scalar)
        case _:
            return _MAYBE


def _bound_verdict(atom: _Atom, scalar: str) -> str:
    """Decide whether a type variable takes an argument of type `scalar`, by its bound (its `inner` atoms).

    Returns:
      The verdict (`y` without one).

    """
    if atom.bound is None:
        return _YES
    return _MAYBE if atom.bound == _PARAM_SPEC else _verdict(atom.inner, scalar, constant=False)


def _class_takes(atom: _Atom, scalar: str) -> str:
    """Decide whether a class takes an argument of type `scalar`.

    A standard-library one by the `scalars` table; an installed protocol by its members (a generic
    one's parameters unread); no other installed class.

    Returns:
      The verdict.

    """
    path: str = _path(atom)
    if atom.module is None:
        return _external_takes(path, scalar)
    declared: Declarations | None = atom.module.declared
    protocol: Protocol | None = None if declared is None else declared.protocols.get(path.rpartition(".")[2])
    members: frozenset[str] | None = stdlib.scalar_members(scalar)
    if protocol is None or (members is not None and not protocol.members <= members):
        return _NO
    return (
        _MAYBE
        if members is None or atom.subscripted or path.rpartition(".")[2] in atom.module.generics
        else _YES
    )


def _external_takes(path: str, scalar: str) -> str:
    """Decide whether a class outside the installed packages (`typing.SupportsIndex`) takes a `scalar`.

    Returns:
      The verdict: the `scalars` table's, or `?` where it hasn't one.

    """
    module: str
    name: str
    module, _, name = path.rpartition(".")
    verdicts: str | None = stdlib.scalar_verdicts(path)
    if path in _ANYTHING:
        verdicts = _YES * len(SCALARS)
    elif module in _TYPING and name == _LITERAL_STRING:
        verdicts = "".join(_YES if each == _LITERAL_STRING else _NO for each in SCALARS)
    elif module in _TYPING and name in _REFUSING:
        verdicts = _NO * len(SCALARS)
    return _MAYBE if verdicts is None else verdicts[SCALARS.index(scalar)]


def _class_verdict(atom: _Atom) -> str:
    """Decide whether one atom takes a class passed as an argument (`dtype=np.float64`).

    A class is an instance of `type` alone: `type[...]`, `type` and `object` take it; `None`, a
    literal, any other class, or a protocol with an attribute or property (which a class has as a
    descriptor, not a value) don't.

    Returns:
      The verdict.

    """
    found: str = _MAYBE
    match atom.kind:
        case "none" | "literal":
            found = _NO
        case "type":  # a `type[T]` takes any class (bounds unchecked: a call outside one is an error)
            found = _YES if all(inner.kind == _VAR or _anything(inner) for inner in atom.inner) else _MAYBE
        case "var" if atom.bound is None:
            found = _YES
        case "var" if atom.bound != _PARAM_SPEC:
            found = _combined({_class_verdict(inner) for inner in atom.inner})
        case "class":
            found = _class_takes_class(atom)
        case _:
            pass
    return found


def _anything(atom: _Atom) -> bool:
    """Check whether an atom is `Any`, `object` or `typeshed`'s `Incomplete`.

    Returns:
      Whether it is.

    """
    return atom.kind == _CLASS and _path(atom) in _ANYTHING


def _class_takes_class(atom: _Atom) -> str:
    """Decide whether a class atom takes a class passed as an argument (see `_class_verdict`).

    Returns:
      The verdict.

    """
    origin: Origin = atom.origin
    if _path(atom) in _ANYTHING | _TYPES:
        return _YES
    if atom.module is None:
        return _NO if origin[0] == _BUILTINS_MODULE else _MAYBE
    declared: Declarations | None = atom.module.declared
    protocol: Protocol | None = None if declared is None else declared.protocols.get(origin[1] or "")
    return _NO if protocol is None or protocol.properties else _MAYBE


def _binds(atoms: Sequence[_Atom], scalar: str, owner: str) -> tuple[str, str] | None:
    """Find the type variable an argument of type `scalar` binds: the one member that takes it.

    Returns:
      Its name, and the argument's type (a literal's widened to `str`); or `None`.

    """
    taking: list[_Atom] = [atom for atom in atoms if _scalar_verdict(atom, scalar, constant=False) != _NO]
    if len(taking) != 1 or taking[0].kind != _VAR or taking[0].constrained or not _own(taking[0], owner):
        return None
    if _scalar_verdict(taking[0], scalar, constant=False) != _YES:
        return None
    return taking[0].name, _STR if scalar == _LITERAL_STRING else scalar


def _class_binds(atoms: Sequence[_Atom], owner: str) -> str | None:
    """Find the type variable a class argument binds: a `type[T]`, all else refusing a class.

    Returns:
      Its name, or `None`.

    """
    types: list[_Atom] = [atom for atom in atoms if atom.kind == _TYPE]
    if len(types) != 1 or any(_class_verdict(atom) != _NO for atom in atoms if atom.kind != _TYPE):
        return None
    inner: tuple[_Atom, ...] = types[0].inner
    variable: _Atom | None = inner[0] if len(inner) == 1 and inner[0].kind == _VAR else None
    return None if variable is None or variable.constrained or not _own(variable, owner) else variable.name


def _literal_values(args: Sequence[ast.expr]) -> Iterator[Constant]:
    arg: ast.expr
    for arg in args:
        if isinstance(arg, ast.Constant) and isinstance(
            arg.value,
            bool | int | float | complex | str | bytes | None,
        ):
            yield arg.value


def _joined(separator: str, parts: Sequence[str | None]) -> str | None:
    return None if None in parts else separator.join(part for part in parts if part is not None)


def _parsed(text: str) -> ast.expr:
    try:
        return ast.parse(text, mode="eval").body
    except SyntaxError:
        return ast.Constant(value=...)  # read as nothing it names


def _private(name: str | None) -> bool:
    return name is None or any(part.startswith("_") for part in name.split("."))
