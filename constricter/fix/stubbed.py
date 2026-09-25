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

from constricter.fix import classnames, project
from constricter.fix.atoms import (
    ANYTHING,
    BUILTINS_MODULE,
    CLASS,
    MAYBE,
    NO,
    NONE,
    PARAM_SPEC,
    TYPE,
    TYPES,
    TYPING,
    UNKNOWN,
    VAR,
    YES,
    Atom,
    Scope,
    Taken,
    argument_of,
    atom_path,
    bound_alias,
    class_binds,
    class_verdict,
    combined,
    element_of,
    free_variables,
    joined,
    literal_values,
    owned,
    parse_text,
    private_name,
    scalar_binds,
    scalar_verdict,
    verdict_of,
)
from constricter.fix.classnames import Packaged
from constricter.fix.declared import Alias, Class, Declarations, Signature, Variable
from constricter.fix.known import Guarded, Origin
from constricter.fix.modules import SUFFIX, Index, Module, module_name
from constricter.fix.overloads import CONTAINERS, SCALARS, substituted
from constricter.fix.signatures import (
    CLASS_BINDS,
    CLASS_VERDICT,
    CONTAINER_BINDS,
    CONTAINER_VERDICTS,
    ELEMENT_VERDICTS,
    Accepts,
    Constant,
    Expansion,
    Parameter,
    ReadSignature,
)

_KIND: Final = "signatures"
# What an atom is (see `Atom`).
_NONE_ATOM: Final = "none"
_LITERAL_ATOM: Final = "literal"
_ARG: Final = "arg"
_OPTIONAL: Final = "Optional"
_LITERAL: Final = "Literal"
_ANNOTATED: Final = "Annotated"
_BUILTINS: Final = frozenset(dir(builtins))
_UNIONS: Final = frozenset({"Union", "Optional"})  # `_OPTIONAL` too
_MAX_DEPTH: Final = 20  # aliases followed before giving up
_TYPE_VARIABLE: Final = "t"  # `Accepts`' key for an unbounded type variable
_SELF: Final = "Self"
_ANY: Final = "typing.Any"  # a pattern's anything
_UNFOLLOWED: Final = "?"  # a lineage's base that can't be followed
_RENAMED: Final = "_alias"  # an alias's type parameter, renamed apart (see `Expansion`)


_Resolved: TypeAlias = Atom | tuple[Alias, Scope, Origin]


# An alias of an installed generic class: the class, the alias's expansion, and each installed class
# its pattern names, by its path there and where it's defined.
_Expanded: TypeAlias = tuple[Origin, Expansion, tuple[tuple[str, Origin], ...]]


@dataclass
class _Memo:
    """What's read of the installed modules, for as long as the index has the same ones.

    Each installed function's signatures, each package's classes and aliases (see
    `classnames.classes`), each class's lineage and methods (see `Methods`), each class's methods by
    name, the names of those it has, its bases' included, and each alias's expansion. The index
    changes as files are checked, the installed modules in it don't.
    """

    installed: frozenset[int] = frozenset()  # the installed modules read, by identity
    read: dict[tuple[str, str], tuple[ReadSignature, ...]] = field(
        default_factory=dict[tuple[str, str], "tuple[ReadSignature, ...]"],
    )
    packages: dict[tuple[str, bool], Packaged] = field(
        default_factory=dict[tuple[str, bool], "Packaged"],
    )
    lines: dict[Origin, tuple[str, ...]] = field(default_factory=dict[Origin, "tuple[str, ...]"])
    methods: dict[tuple[Origin, str], tuple[ReadSignature, ...]] = field(
        default_factory=dict[tuple[Origin, str], "tuple[ReadSignature, ...]"],
    )
    names: dict[Origin, frozenset[str]] = field(default_factory=dict[Origin, frozenset[str]])
    expansions: dict[Origin, _Expanded | None] = field(default_factory=dict[Origin, "_Expanded | None"])

    def of(self, modules: Mapping[str, Module]) -> "_Memo":
        """Keep what's read for as long as `modules` has the same installed ones.

        Returns:
          This memo, emptied if they've changed.

        """
        installed: frozenset[int] = frozenset(id(module) for module in modules.values() if module.installed)
        if installed != self.installed:
            self.installed = installed
            self.read = {}
            self.packages = {}
            self.lines = {}
            self.methods = {}
            self.names = {}
            self.expansions = {}
        return self


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
    memo: dict[tuple[str, str], tuple[ReadSignature, ...]] = _MEMO.of(modules).read
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


class Methods(NamedTuple):
    """Installed classes' methods a file may call whose arguments or instance decide their type.

    `signatures`: each one's, by the class as the file writes it and the method (`np.ndarray.astype`);
    `parameters`: each such class's type parameters, in order, which a receiver's type binds;
    `lineage`: each installed class the file names, as it writes it, with where it's defined and its
    ancestors' (`numpy.float64`, `numpy.floating`, ...), `?` last where a base can't be followed: a
    receiver's type is matched against a method's `self` by them. `aliases`: each public alias of an
    installed generic class the file names (`npt.NDArray`), whose methods are its class's; the
    classes its expansion names are in `lineage` by their paths (`numpy.dtype`).
    """

    signatures: dict[str, tuple[ReadSignature, ...]]
    parameters: dict[str, tuple[str, ...]]
    lineage: dict[str, tuple[str, ...]]
    aliases: dict[str, Expansion]


def methods(catalog: Index, path: Path, guarded: Mapping[str, Guarded] | None = None) -> Methods:
    """Find the methods the file at `path` calls that an installed class it names declares (see `Methods`).

    Named through its imports, those under `if TYPE_CHECKING:` included, and those its fixes will add
    there (`guarded`, see `project.Imported`): a return type spelled through one is a receiver's.

    Returns:
      Them; none for a file `catalog` doesn't have.

    """
    modules: dict[str, Module] = catalog.modules
    found: Methods = Methods({}, {}, {}, {})
    target: Module | None
    if path.suffix != SUFFIX or (target := modules.get(module_name(path))) is None or not target.method_calls:
        return found
    reader: _Reader = _Reader(modules)
    memo: _Memo = _MEMO.of(modules)
    spelled: str
    origin: Origin
    names: dict[str, Origin] = {
        **{name: found.origin for name, found in (guarded or {}).items()},
        **target.guarded,
        **target.names,
    }
    for spelled, origin in classnames.classes(modules, names, memo.packages):
        _class_methods(found, reader, target, spelled, origin)
    alias: Origin
    for spelled, alias in classnames.classes(modules, names, memo.packages, aliases=True):
        if alias not in memo.expansions:
            memo.expansions[alias] = reader.expansion(alias)
        expanded: _Expanded | None
        if (expanded := memo.expansions[alias]) is None:
            continue
        paths: tuple[tuple[str, Origin], ...]
        origin, found.aliases[spelled], paths = expanded
        _class_methods(found, reader, target, spelled, origin)
        path_named: str
        for path_named, origin in paths:
            found.lineage[path_named] = _lineage(reader, origin)
    return found


def _lineage(reader: "_Reader", origin: Origin) -> tuple[str, ...]:
    """Find an installed class's lineage (see `Methods.lineage`), and the methods it has, once.

    Returns:
      It.

    """
    memo: _Memo = _MEMO.of(reader.modules)
    if origin not in memo.lines:
        memo.lines[origin] = tuple(dict.fromkeys(reader.lineage(origin, 0)))
        memo.names[origin] = classnames.method_names(reader.modules, memo.lines[origin])
    return memo.lines[origin]


def _class_methods(found: Methods, reader: "_Reader", target: Module, spelled: str, origin: Origin) -> None:
    """Add an installed class's methods `target` calls, as it writes the class (`spelled`), to `found`."""
    found.lineage[spelled] = _lineage(reader, origin)
    memo: _Memo = _MEMO.of(reader.modules)
    module: Module = reader.modules[origin[0]]
    klass: Class = cast("Declarations", module.declared).classes[origin[1] or ""]
    name: str
    for name in sorted(memo.names[origin] & target.method_calls):
        if (origin, name) not in memo.methods:
            # Its lineage has the method: the class or a base declares it.
            memo.methods[origin, name] = cast(
                "tuple[ReadSignature, ...]",
                reader.method(module, klass, name, 0),
            )
        found.signatures[f"{spelled}.{name}"] = memo.methods[origin, name]
        found.parameters[spelled] = tuple(param for param, _ in klass.params)


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
    return _read_all(_Reader(modules), module, declared.signatures[name], frozenset(), {})


def _read_all(
    reader: "_Reader",
    module: Module,
    written: tuple[Signature, ...],
    variables: frozenset[str],
    params: Mapping[str, str | None],
) -> tuple[ReadSignature, ...]:
    """Read a function's (or method's) signatures, `params` its class's type parameters.

    A parameter every signature declares the same way takes whatever a call passes it, unless it
    names a type variable (the module's, the class's in `variables`, or the signature's own).

    Returns:
      Them.

    """
    declared: Declarations = cast("Declarations", module.declared)
    shared: set[tuple[str, str, bool, str | None]] = set(written[0].params)
    signature: Signature
    for signature in written[1:]:
        shared &= set(signature.params)
    named: frozenset[str] = frozenset(
        {
            *declared.variables,
            *module.type_vars,
            *variables,
            *(param for each in written for param, _ in each.type_params),
        },
    )
    shared = {param for param in shared if not _names_any(param[3], named)}
    return tuple(reader.signature(module, signature, shared, params) for signature in written)


def _names(text: str) -> frozenset[str]:
    """Name the bare names a template or pattern uses (its type variables').

    Returns:
      Them.

    """
    return frozenset(node.id for node in ast.walk(parse_text(text)) if isinstance(node, ast.Name))


def _names_any(annotation: str | None, names: frozenset[str]) -> bool:
    """Check whether an annotation names any of `names`.

    Returns:
      Whether it does.

    """
    if annotation is None:
        return False
    node: ast.AST
    for node in ast.walk(parse_text(annotation)):
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
        self.matching: bool = False  # writing a pattern to match a receiver against (see `pattern`)

    def signature(
        self,
        module: Module,
        signature: Signature,
        shared: set[tuple[str, str, bool, str | None]],
        types: Mapping[str, str | None],
    ) -> ReadSignature:
        """Read one signature: what each parameter takes, and its return as a template.

        A parameter every signature declares the same way, naming no type variable, takes whatever a
        call passes it (as the tables' do): only those that tell the signatures apart, or bind a
        type variable, are read.

        Returns:
          It.

        """
        scope: Scope = Scope(module, {**types, **dict(signature.type_params)}, module.name)
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
        if signature.self_type is None:
            return ReadSignature(params, returns, None)
        # A method declaring its `self` (`self: NDArray[ScalarT]`) is for such instances alone.
        receiver: str | None = self.pattern(parse_text(signature.self_type), scope)
        # Each type variable `self`'s pattern names, bounded (its constraints, for a constrained one).
        variables: Mapping[str, Variable] = cast("Declarations", module.declared).variables
        bounds: list[tuple[str, str]] = []
        name: str
        for name in sorted(_names(receiver or "")):
            bound: str | tuple[ast.expr, Scope] | None = (
                scope.params[name]
                if name in scope.params
                else variables[name].bound
                if name in variables
                else None
            )
            pattern: str | None = (
                self.pattern(parse_text(bound), scope)
                if isinstance(bound, str) and bound != PARAM_SPEC
                else None
            )
            if pattern is not None:
                bounds.append((name, pattern))
        return ReadSignature(
            params,
            returns,
            None if receiver is not None else [MAYBE],
            receiver,
            tuple(bounds),
        )

    def pattern(self, expr: ast.expr, scope: Scope) -> str | None:
        """Write an annotation as a pattern for a receiver's type to match (see `ReadSignature.receiver`).

        As a template, but every class by where it's defined (`builtins.tuple`), aliases written out,
        and anything (`Any`, `object`, a type variable from elsewhere) as `typing.Any`.

        Returns:
          It, or `None` if it names something that can't be matched (a `Literal`).

        """
        self.matching = True
        try:
            return self._template(expr, scope, 0)
        finally:
            self.matching = False

    def _accepts(self, annotation: ast.expr, scope: Scope) -> Accepts:
        """Work out what a parameter takes (see `stdlib.Accepts`).

        Returns:
          It.

        """
        atoms: list[Atom] = list(self._atoms(annotation, scope, 0))
        literals: list[Constant] = [value for atom in atoms for value in atom.values]
        values: str = "".join(verdict_of(atoms, scalar, constant=False) for scalar in SCALARS)
        found: Accepts = {"v": values, CLASS_VERDICT: combined({class_verdict(atom) for atom in atoms})}
        if literals:
            found["lit"] = literals
            constants: str = "".join(verdict_of(atoms, scalar, constant=True) for scalar in SCALARS)
            if constants != values:
                found["c"] = constants
        binds: dict[str, list[str]] = {}
        scalar: str
        for scalar in SCALARS:
            bound: tuple[str, str] | None
            if (bound := scalar_binds(atoms, scalar, scope.owner)) is not None:
                binds[scalar] = [bound[0], bound[1]]
        if binds:
            found["var"] = binds
        if (
            len(atoms) == 1
            and atoms[0].kind == VAR
            and atoms[0].bound is None
            and owned(atoms[0], scope.owner)
        ):
            found[_TYPE_VARIABLE] = atoms[0].name
        variable: str | None
        if (variable := class_binds(atoms, scope.owner)) is not None:
            found[CLASS_BINDS] = variable
        self._containers(atoms, scope, found)
        return found

    def _containers(self, atoms: Sequence[Atom], scope: Scope, found: Accepts) -> None:
        """Add what a parameter takes of each builtin container argument to `found` (see `Accepts`).

        A container every member refuses, or one member takes (its elements' types too, where that
        member says: `tuple[int, ...]`); and the bounded type variable it binds, where the parameter
        is only that (`ShapeT`, bound to `tuple[int, ...]`).
        """
        verdicts: dict[str, str] = {}
        elements: dict[str, str] = {}
        container: str
        for container in CONTAINERS:
            each: list[Taken] = [self._container(atom, container, 0) for atom in atoms]
            verdict: str
            if (verdict := combined({taken for taken, _ in each})) != MAYBE:
                verdicts[container] = verdict
            taking: list[tuple[Atom, ...] | None] = [inner for taken, inner in each if taken != NO]
            if verdict == YES and len(taking) == 1 and taking[0] is not None:
                elements[container] = "".join(
                    verdict_of(taking[0], scalar, constant=False) for scalar in SCALARS
                )
        if verdicts:
            found[CONTAINER_VERDICTS] = verdicts
        if elements:
            found[ELEMENT_VERDICTS] = elements
        only: Atom | None = atoms[0] if len(atoms) == 1 and atoms[0].kind == VAR else None
        if (
            only is not None
            and only.bound not in {None, PARAM_SPEC}
            and not only.constrained
            and owned(only, scope.owner)
        ):
            found[CONTAINER_BINDS] = only.name

    def _container(self, atom: Atom, container: str, hops: int) -> Taken:
        """Decide whether one atom takes a builtin `container` argument, and what its elements must be.

        Returns:
          The verdict, and the atoms its elements' type must fit where the atom says (`list[int]`,
          `tuple[int, ...]`); `None` where it doesn't.

        """
        verdict: str = scalar_verdict(atom, container, constant=False)
        elements: tuple[Atom, ...] | None = None
        if atom.kind == VAR and atom.bound not in {None, PARAM_SPEC} and hops < _MAX_DEPTH:
            each: list[Taken] = [self._container(inner, container, hops + 1) for inner in atom.inner]
            taking: list[tuple[Atom, ...] | None] = [inner for taken, inner in each if taken != NO]
            verdict = combined({taken for taken, _ in each})
            elements = taking[0] if len(taking) == 1 else None
        elif atom.kind == CLASS and atom.module is None and atom_path(atom) == f"builtins.{container}":
            verdict = YES
            of: ast.expr | None = element_of(container, atom.args)
            if atom.args and (of is None or atom.scope is None):
                verdict = MAYBE  # `tuple[int, str]`, `dict[str, int]`: their elements aren't read
            elif of is not None and atom.scope is not None:
                elements = tuple(self._atoms(of, atom.scope, hops + 1))
        return verdict, elements

    def _atoms(self, expr: ast.expr, scope: Scope, hops: int) -> Iterator[Atom]:
        """Split an annotation into its union's members, through aliases, `Optional`, `Union`, strings.

        Yields:
          Each member.

        """
        text: str
        left: ast.expr
        right: ast.expr
        if hops > _MAX_DEPTH:
            yield UNKNOWN
            return
        match expr:
            case ast.Constant(value=None):
                yield Atom(_NONE_ATOM)
            case ast.Constant(value=str() as text):
                yield from self._atoms(parse_text(text), scope, hops + 1)
            case ast.BinOp(left=left, op=ast.BitOr(), right=right):
                yield from self._atoms(left, scope, hops + 1)
                yield from self._atoms(right, scope, hops + 1)
            case ast.Subscript():
                yield from self._subscript_atoms(expr, scope, hops)
            case ast.Name() | ast.Attribute():
                yield from self._named_atoms(expr, scope, hops, ())
            case _:
                yield UNKNOWN

    def _named_atoms(
        self,
        expr: ast.Name | ast.Attribute,
        scope: Scope,
        hops: int,
        args: Sequence[ast.expr],
    ) -> Iterator[Atom]:
        """Read a name an annotation uses, subscripted with `args` (none if it isn't).

        Yields:
          Its atoms: an alias's, bound by `args`; else the one it is.

        """
        resolved: _Resolved | None
        if (resolved := self.resolve(expr, scope)) is None:
            yield UNKNOWN
        elif not isinstance(resolved, Atom):
            alias: Alias
            where: Scope
            alias, where, _ = resolved
            yield from self._atoms(parse_text(alias.value), bound_alias(alias, where, args, scope), hops + 1)
        elif resolved.kind == _ARG:
            yield from self._atoms(*argument_of(resolved), hops + 1)
        elif resolved.kind == VAR and resolved.scope is not None and resolved.bound not in {None, PARAM_SPEC}:
            bound: ast.expr = parse_text(resolved.bound or "")
            yield resolved._replace(inner=tuple(self._atoms(bound, resolved.scope, hops + 1)))
        else:
            yield resolved._replace(subscripted=bool(args), args=tuple(args), scope=scope)

    def _subscript_atoms(self, expr: ast.Subscript, scope: Scope, hops: int) -> Iterator[Atom]:
        args: list[ast.expr] = list(expr.slice.elts) if isinstance(expr.slice, ast.Tuple) else [expr.slice]
        base: ast.expr = expr.value
        if not isinstance(base, ast.Name | ast.Attribute):
            yield UNKNOWN
            return
        path: str | None = self._external(base, scope)
        if path is not None and path.rpartition(".")[0] in TYPING:
            name: str = path.rpartition(".")[2]
            if name in _UNIONS:
                members: list[ast.expr] = [*args, *([ast.Constant(None)] if name == _OPTIONAL else [])]
                yield from (atom for member in members for atom in self._atoms(member, scope, hops + 1))
                return
            if name == _LITERAL:
                yield Atom(_LITERAL_ATOM, tuple(literal_values(args)))
                return
            if name == _ANNOTATED:
                yield from self._atoms(args[0], scope, hops + 1)
                return
        if path in TYPES:
            yield Atom(TYPE, inner=tuple(self._atoms(args[0], scope, hops + 1)))
            return
        yield from self._named_atoms(base, scope, hops, args)

    def _external(self, expr: ast.Name | ast.Attribute, scope: Scope) -> str | None:
        """Name what an annotation's name refers to outside the installed modules (`typing.Union`).

        Returns:
          Its dotted path, or `None` if it's an installed module's, or unknown.

        """
        resolved: _Resolved | None = self.resolve(expr, scope)
        if not isinstance(resolved, Atom) or resolved.kind != CLASS or resolved.module is not None:
            return None
        return atom_path(resolved)

    def resolve(self, expr: ast.Name | ast.Attribute, scope: Scope) -> _Resolved | None:
        """Resolve a name an annotation uses: a type parameter, a class, an alias, a type variable.

        Returns:
          It as an atom (`arg`: a parameter an alias's argument binds), or an alias with the scope
          its value is read in; or `None` if it's none of them.

        """
        origin: Origin | None
        if isinstance(expr, ast.Name) and expr.id in scope.params:
            param: str | tuple[ast.expr, Scope] | None = scope.params[expr.id]
            if isinstance(param, tuple):
                return Atom(_ARG, name=ast.unparse(param[0]), scope=param[1])
            return Atom(VAR, name=expr.id, bound=param, scope=scope)
        if (origin := self._origin(expr, scope.module)) is None or origin[1] is None:
            return None
        origin = project.canonical_origin(self.modules, origin)
        defining: Module | None = self.modules.get(origin[0])
        if defining is None or not defining.installed:
            return Atom(CLASS, origin=origin)
        return self._declared(defining, origin)

    def method(self, module: Module, klass: Class, name: str, hops: int) -> tuple[ReadSignature, ...] | None:
        """Read a class's method (its own, else its nearest base's that has it) as a function's are.

        Returns:
          Its signatures, or `None` if neither it nor a base it can follow declares it.

        """
        written: tuple[Signature, ...] | None
        if (written := klass.methods.get(name)) is not None:
            return _read_all(
                self,
                module,
                written,
                frozenset(name for name, _ in klass.params),
                dict(klass.params),
            )
        base: str
        for base in klass.bases if hops < _MAX_DEPTH else ():
            parsed: ast.expr = parse_text(base)
            parsed = parsed.value if isinstance(parsed, ast.Subscript) else parsed
            resolved: _Resolved | None = (
                self.resolve(parsed, Scope(module, {}, module.name))
                if isinstance(parsed, ast.Name | ast.Attribute)
                else None
            )
            if (
                isinstance(resolved, Atom)
                and resolved.module is not None
                and resolved.module.declared is not None
            ):
                inherited: Class | None = resolved.module.declared.classes.get(resolved.origin[1] or "")
                read: tuple[ReadSignature, ...] | None = (
                    None if inherited is None else self.method(resolved.module, inherited, name, hops + 1)
                )
                if read is not None:
                    return read
        return None

    def expansion(self, origin: Origin) -> _Expanded | None:
        """Expand an installed alias of a generic class (`NDArray`), as a receiver's type (see `Expansion`).

        Returns:
          The class, the expansion, and the installed classes its pattern names; or `None` for an
          alias of anything else (a union, a protocol, another alias).

        """
        module: Module = self.modules[origin[0]]
        alias: Alias = cast("Declarations", module.declared).aliases[origin[1] or ""]
        value: ast.expr = parse_text(alias.value)
        own: Scope = Scope(module, {}, module.name)
        base: ast.Name | ast.Attribute
        index: ast.expr
        match value:
            case ast.Subscript(value=ast.Name() | ast.Attribute() as base, slice=index):
                pass
            case _:
                return None
        head: _Resolved | None = self.resolve(base, own)
        if not isinstance(head, Atom) or head.kind != CLASS or head.module is None:
            return None
        klass: Class | None = cast("Declarations", head.module.declared).classes.get(head.origin[1] or "")
        params: tuple[str, ...] = alias.params or free_variables(alias.value, own)
        scope: Scope = Scope(module, dict.fromkeys(params), module.name)
        receiver: str | None = self.pattern(value, scope)
        if klass is None or receiver is None:
            return None
        renamed: dict[str, str] = {param: f"{_RENAMED}{place}" for place, param in enumerate(params)}
        args: list[ast.expr] = list(index.elts) if isinstance(index, ast.Tuple) else [index]
        return (
            head.origin,
            Expansion(
                tuple(renamed.values()),
                substituted(receiver, renamed),
                self._templates(klass, args, scope, renamed),
            ),
            self._named(receiver),
        )

    def _templates(
        self,
        klass: Class,
        args: Sequence[ast.expr],
        scope: Scope,
        renamed: Mapping[str, str],
    ) -> tuple[tuple[str, str], ...]:
        """Write what an alias passes each of its class's type parameters, where it can be written.

        Returns:
          Each parameter with its template, the alias's own parameters `renamed`.

        """
        found: list[tuple[str, str]] = []
        param: str
        arg: ast.expr
        for (param, _), arg in zip(klass.params, args, strict=False):  # a class's own subscript fits
            template: str | None
            if (template := self._template(arg, scope, 0)) is not None:
                found.append((param, substituted(template, renamed)))
        return tuple(found)

    def _named(self, pattern: str) -> tuple[tuple[str, Origin], ...]:
        """Find the installed classes a pattern names.

        Returns:
          Each by its path there, and where it's defined.

        """
        found: dict[str, Origin] = {}
        node: ast.AST
        for node in ast.walk(parse_text(pattern)):
            path: str = ast.unparse(node) if isinstance(node, ast.Attribute) else ""
            where: Origin = (path.rpartition(".")[0], path.rpartition(".")[2])
            if path and classnames.declares(self.modules, where):
                found[path] = where
        return tuple(found.items())

    def lineage(self, origin: Origin, hops: int) -> Iterator[str]:
        """Walk an installed class and its ancestors, depth first (see `Methods.lineage`).

        Yields:
          Where each is defined (`numpy.float64`), then `?` if a base can't be followed.

        """
        yield f"{origin[0]}.{origin[1]}"
        module: Module = self.modules[origin[0]]
        klass: Class = cast("Declarations", module.declared).classes[origin[1] or ""]
        base: str
        for base in klass.bases:
            parsed: ast.expr = parse_text(base)
            parsed = parsed.value if isinstance(parsed, ast.Subscript) else parsed
            resolved: _Resolved | None = (
                self.resolve(parsed, Scope(module, {}, module.name))
                if isinstance(parsed, ast.Name | ast.Attribute)
                else None
            )
            if not isinstance(resolved, Atom) or resolved.kind != CLASS:
                yield _UNFOLLOWED
            elif resolved.module is None:
                yield atom_path(resolved)
            elif hops < _MAX_DEPTH:
                yield from self.lineage(resolved.origin, hops + 1)
            else:  # a cycle of bases
                yield _UNFOLLOWED

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
        if resolved is not None and not isinstance(resolved, Atom):  # an alias: of a class?
            value: ast.expr = parse_text(resolved[0].value)
            base: ast.expr = value.value if isinstance(value, ast.Subscript) else value
            resolved = self.resolve(base, resolved[1]) if isinstance(base, ast.Name | ast.Attribute) else None
        return isinstance(resolved, Atom) and resolved.kind == CLASS and resolved.module is not None

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
        own: Scope = Scope(module, {}, module.name)
        if declared is not None and name in declared.aliases:
            return declared.aliases[name], own, origin
        variable: Variable | None
        if (variable := None if declared is None else declared.variables.get(name)) is not None:
            return Atom(VAR, name=name, bound=variable.bound, scope=own, constrained=variable.constrained)
        if (
            name in module.classes
            or name in module.generics
            or (declared is not None and name in declared.protocols)
        ):
            return Atom(CLASS, origin=origin, module=module)
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
                or ((BUILTINS_MODULE, expr.id) if expr.id in _BUILTINS else None)
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

    def _template(self, expr: ast.expr, scope: Scope, hops: int) -> str | None:
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
                found = NONE
            case ast.Constant(value=builtins.Ellipsis):
                found = "..."
            case ast.Constant(value=str() as text):
                found = self._template(parse_text(text), scope, hops + 1)
            case ast.BinOp(left=left, op=ast.BitOr(), right=right):
                found = joined(" | ", [self._template(side, scope, hops + 1) for side in (left, right)])
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
        scope: Scope,
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
        if not isinstance(resolved, Atom):
            alias: Alias
            where: Scope
            origin: Origin
            alias, where, origin = resolved
            public: Origin = project.public_origin(self.modules, origin)
            if not self.matching and not private_name(public[0]) and not private_name(public[1]):
                written = f"{public[0]}.{public[1]}"
            elif alias.params or free_variables(alias.value, where) or not args:
                return self._template(
                    parse_text(alias.value),
                    bound_alias(alias, where, args, scope),
                    hops + 1,
                )
            else:  # another name for a generic class (`_dtype = dtype`): its arguments are the class's
                written = self._template(parse_text(alias.value), where, hops + 1)
        elif resolved.kind == _ARG:
            return self._template(*argument_of(resolved), hops + 1)
        elif resolved.kind == VAR:
            written = resolved.name if owned(resolved, scope.owner) else _ANY if self.matching else None
        else:
            written = self._class_path(resolved)
        if written is None or not args:
            return written
        texts: list[str | None] = [self._template(arg, scope, hops + 1) for arg in args]
        return None if None in texts else f"{written}[{', '.join(t for t in texts if t is not None)}]"

    def _class_path(self, atom: Atom) -> str | None:
        """Write a class as a template names it: a builtin bare, any other by its public dotted path.

        Returns:
          It, or `None` for `typing`'s forms, `object`, `type`, or a class with no public path.

        """
        origin: Origin = atom.origin
        if self.matching:
            return _ANY if atom_path(atom) in ANYTHING else None if origin[0] in TYPING else atom_path(atom)
        if atom.module is not None:
            origin = project.public_origin(self.modules, origin)
        elif origin[0] == BUILTINS_MODULE:
            return origin[1] if origin[1] not in {"object", "type"} else None
        elif origin[0] in TYPING:
            return _SELF if origin[1] == _SELF else None  # a method's `Self`: the receiver's type
        return None if private_name(origin[0]) or private_name(origin[1]) else f"{origin[0]}.{origin[1]}"
