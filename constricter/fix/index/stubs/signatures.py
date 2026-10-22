"""An installed function's signatures, read from its stub as the standard library's tables hold theirs.

A stub's overloads (see `constricter.fix.index.stubs.declared`) are resolved across the installed modules the
index holds, into the signatures of `constricter.fix.libraries.overloads`: which argument types each
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
from typing import Final, cast

from constricter.fix.core.known import Origin
from constricter.fix.core.signatures import (
    CLASS_BINDS,
    CLASS_BOUNDED,
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
from constricter.fix.index import own_types, project
from constricter.fix.index.modules import Module
from constricter.fix.index.stubs import classnames
from constricter.fix.index.stubs.atoms import (
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
    class_bounded,
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
from constricter.fix.index.stubs.declared import Alias, Class, Declarations, Signature, Variable
from constricter.fix.index.stubs.names import ALIAS_DEPTH, ARG, Resolved, Resolver
from constricter.fix.index.stubs.read import MEMO, Asked, Expanded
from constricter.fix.libraries.overloads import CONTAINERS, SCALARS, substituted

# What an atom is (see `Atom`).
_NONE_ATOM: Final = "none"
_LITERAL_ATOM: Final = "literal"
_OPTIONAL: Final = "Optional"
_LITERAL: Final = "Literal"
_ANNOTATED: Final = "Annotated"
_UNIONS: Final = frozenset({"Union", "Optional"})  # `_OPTIONAL` too
_TYPE_VARIABLE: Final = "t"  # `Accepts`' key for an unbounded type variable
_SELF: Final = "Self"
_ANY: Final = "typing.Any"  # a pattern's anything
_RENAMED: Final = "_alias"  # an alias's type parameter, renamed apart (see `Expansion`)


def read_all(
    reader: "Reader",
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
    declared: Declarations | None = module.declared  # none: a checked file's (see `read_signatures`)
    shared: set[tuple[str, str, bool, str | None]] = set(written[0].params)
    signature: Signature
    for signature in written[1:]:
        shared &= set(signature.params)
    named: frozenset[str] = frozenset(
        {
            *(() if declared is None else declared.variables),
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


class Reader(Resolver):
    """Reads one function's signatures (see the module docstring)."""

    def __init__(self, modules: Mapping[str, Module]) -> None:
        """Read in `modules`."""
        super().__init__(modules)
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
                None if param in shared or param[3] is None else self._accepted(param[3], scope),
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

    def _accepted(self, text: str, scope: Scope) -> Accepts:
        """Work out what a parameter annotated `text` takes, once for each module and scope it's read in.

        A package's signatures write the same few hundred annotations over and over (`Axis`,
        `bool`, `str | None`).

        Returns:
          It (see `_accepts`), shared by every parameter written alike: to read, never to change.

        """
        # A signature's scope holds bounds' texts alone (see `signature`): no alias's argument.
        bounds: Mapping[str, str | None] = cast("Mapping[str, str | None]", scope.params)
        if not scope.module.installed:  # a checked file's: by the index's classes, which the memo outlives
            return self._accepts(parse_text(text), scope)
        memo: dict[Asked, Accepts] = MEMO.of(self.modules).accepts
        key: Asked
        if (key := (scope.module.name, scope.owner, text, tuple(sorted(bounds.items())))) not in memo:
            memo[key] = self._accepts(parse_text(text), scope)
        return memo[key]

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
            if class_bounded(atoms):
                found[CLASS_BOUNDED] = True
        self._containers(atoms, scope, found)
        if not scope.module.installed:  # a checked file's: by the checked files' classes it names
            own_types.accept(self.modules, atoms, lambda arg, where: self._atoms(arg, where, 1), found)
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
        if atom.kind == VAR and atom.bound not in {None, PARAM_SPEC} and hops < ALIAS_DEPTH:
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
        if hops > ALIAS_DEPTH:
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
        resolved: Resolved | None
        if (resolved := self.resolve(expr, scope)) is None:
            yield UNKNOWN
        elif not isinstance(resolved, Atom):
            alias: Alias
            where: Scope
            alias, where, _ = resolved
            yield from self._atoms(parse_text(alias.value), bound_alias(alias, where, args, scope), hops + 1)
        elif resolved.kind == ARG:
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
        resolved: Resolved | None = self.resolve(expr, scope)
        if not isinstance(resolved, Atom) or resolved.kind != CLASS or resolved.module is not None:
            return None
        return atom_path(resolved)

    def method(self, module: Module, klass: Class, name: str, hops: int) -> tuple[ReadSignature, ...] | None:
        """Read a class's method (its own, else its nearest base's that has it) as a function's are.

        Returns:
          Its signatures, or `None` if neither it nor a base it can follow declares it.

        """
        written: tuple[Signature, ...] | None
        if (written := klass.methods.get(name)) is not None:
            return read_all(
                self,
                module,
                written,
                frozenset(name for name, _ in klass.params),
                dict(klass.params),
            )
        base: str
        for base in klass.bases if hops < ALIAS_DEPTH else ():
            resolved: Resolved | None = self.resolved_base(base, module)
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

    def expansion(self, origin: Origin) -> Expanded | None:
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
        head: Resolved | None = self.resolve(base, own)
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
            case _ if hops > ALIAS_DEPTH:
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
        resolved: Resolved | None = self.resolve(expr, scope)
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
        elif resolved.kind == ARG:
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
