# SPDX-License-Identifier: MIT
"""Standard-library functions whose return depends on their arguments: each signature, for `--fix` to pick.

`Overloads.entry` reads a function's overloads (or its one signature, when a type variable or a
class inside a builtin generic puts its return beyond the fixed-return tables) as `--fix` matches
them against a call (`constricter.fix.overloads`): each parameter's kind, whether it has a default,
and which argument types it certainly takes or refuses; and the return, as a template.

Argument types are the builtin scalars in `SCALARS`, `LiteralString` standing for a `str` literal.
A parameter every overload declares the same way takes whatever a call passes it (a call matching
none is an error anyway), so only the parameters that tell the overloads apart are read. A return
template is an annotation with standard-library classes by their dotted paths (`re.Pattern[AnyStr]`)
and type variables by their bare names, which the call's arguments bind.
"""

import ast
import copy
from collections.abc import Iterable, Iterator, Sequence
from typing import Final, NamedTuple, TypeAlias

from constricter.fix.stdlib import Accepts, Constant, Parameter, Signature
from tests.typeshed.reading import ARITY, TYPING_GENERICS, ClassRef, Defs, Reading, readable, usable
from tests.typeshed.stubs import Alias, Binding, Found, Function, Klass, TypeVariable, decorator_name

SCALARS: Final = ("str", "LiteralString", "bytes", "bytearray", "int", "float", "complex", "bool", "None")
YES: Final = "y"
NO: Final = "n"
MAYBE: Final = "?"
POSITIONAL: Final = "p"  # positional only
EITHER: Final = "e"  # positional or keyword
KEYWORD: Final = "k"  # keyword only
STAR: Final = "a"  # `*args`
STARS: Final = "w"  # `**kwargs`
_BUILTINS: Final = "builtins"
_TYPING: Final = frozenset({"typing", "typing_extensions", "_typeshed"})
_STR: Final = "str"
_LITERAL_STRING: Final = "LiteralString"
_NONE: Final = "None"
_OBJECT: Final = "object"
_ANY: Final = frozenset({"Any", "Incomplete"})
_REFUSING: Final = frozenset({"Callable", "Type", "type"})  # no scalar is a callable or a class
_OPTIONAL: Final = "Optional"
_UNIONS: Final = frozenset({_OPTIONAL, "Union"})
_LITERAL: Final = "Literal"
_ANNOTATED: Final = "Annotated"
_GUARDS: Final = frozenset({"TypeGuard", "TypeIs"})
_CONTAINERS: Final = frozenset({*ARITY, "tuple"})  # the builtin generics a return may use
# A builtin scalar a parameter of another builtin type takes all the same (numbers widened).
_PROMOTED: Final = {
    ("int", "float"),
    ("int", "complex"),
    ("float", "complex"),
    ("bool", "float"),
    ("bool", "complex"),
}
# The class an argument of each type is an instance of (`None`'s, `object`, less what it doesn't have).
_CLASSES: Final = {"LiteralString": _STR, "None": _OBJECT}
_MAX_DEPTH: Final = 20
_DECLARING: Final = frozenset({"Generic", "Protocol"})  # a base that lists a class's type parameters
# Methods whose calls aren't an instance's plain ones: read as attributes, or on the class.
_NOT_METHODS: Final = frozenset({"property", "cached_property", "classmethod", "staticmethod"})
_UNWRITTEN: Final = frozenset({_OBJECT, "type", "function", "ellipsis"})  # vague, or internal
# What a protocol's body binds that isn't a member its instances need (`typing`'s own protocols'
# `__slots__ = ()`).
_MACHINERY: Final = frozenset({"__slots__", "__init__", "__new__", "__class_getitem__", "__init_subclass__"})
_ATOM_NONE: Final = "none"
_ATOM_LITERAL: Final = "literal"
_ATOM_FOUND: Final = "found"
_ATOM_UNKNOWN: Final = "unknown"


class Atom(NamedTuple):
    """One member of a parameter's union: `None`, a `Literal`'s values, a name found, or one unread."""

    kind: str
    found: Found | None = None
    subscripted: bool = False  # the name, with type arguments (`PathLike[str]`)
    literals: tuple[Constant, ...] = ()


class Param(NamedTuple):
    """One parameter of one signature: its name, kind (`POSITIONAL`...), default, and annotation."""

    name: str
    kind: str
    default: bool
    annotation: ast.expr | None


class Verdicts(NamedTuple):
    """What a parameter takes: a verdict per `SCALARS` type, and more for literals and type variables.

    `values`: for a variable argument; `constants`: for a literal argument not among `literals`
    (the values of its `Literal[...]` members), if they differ; `binds`: the type variable the
    parameter is, and what an argument of each type binds it to.
    """

    values: str
    constants: str | None = None
    literals: tuple[Constant, ...] | None = None
    binds: dict[str, tuple[str, str]] | None = None


def parameters(node: ast.FunctionDef | ast.AsyncFunctionDef) -> list[Param]:
    """List a signature's parameters in order, a `__name` (the stubs' old spelling) positional only.

    Returns:
      Them.

    """
    args: ast.arguments = node.args
    positional: list[ast.arg] = [*args.posonlyargs, *args.args]
    defaults: int = len(positional) - len(args.defaults)
    found: list[Param] = []
    index: int
    arg: ast.arg
    for index, arg in enumerate(positional):
        old: bool = arg.arg.startswith("__") and not arg.arg.endswith("__")
        kind: str = POSITIONAL if index < len(args.posonlyargs) or old else EITHER
        found.append(Param(arg.arg, kind, index >= defaults, arg.annotation))
    if args.vararg is not None:
        found.append(Param(args.vararg.arg, STAR, default=True, annotation=args.vararg.annotation))
    default: ast.expr | None
    for arg, default in zip(args.kwonlyargs, args.kw_defaults, strict=True):
        found.append(Param(arg.arg, KEYWORD, default is not None, arg.annotation))
    if args.kwarg is not None:
        found.append(Param(args.kwarg.arg, STARS, default=True, annotation=args.kwarg.annotation))
    return found


# A method's entry (`module.Class.name`) and signatures.
_Method: TypeAlias = tuple[str, list[Signature]]
# A parameter as every signature must have it to be shared: name, kind, default, annotation.
_Key: TypeAlias = tuple[str, str, bool, str]


def _binding(binds: dict[str, tuple[str, str]]) -> str | dict[str, list[str]]:
    """Write what a parameter's type variable binds to: each argument type's own, as a bare name, or each.

    Returns:
      The variable's name if every argument type binds it to itself (a `str` literal to `str`), else
      what each binds it to.

    """
    names: set[str] = {name for name, _ in binds.values()}
    own: bool = len(binds) == len(SCALARS) and all(
        text == (_STR if scalar == _LITERAL_STRING else scalar) for scalar, (_, text) in binds.items()
    )
    return names.pop() if own and len(names) == 1 else {kind: list(bound) for kind, bound in binds.items()}


def _self(node: ast.FunctionDef | ast.AsyncFunctionDef) -> ast.expr | None:
    """Find a method's `self` annotation.

    Returns:
      It, or `None`.

    """
    positional: list[ast.arg] = [*node.args.posonlyargs, *node.args.args]
    return positional[0].annotation if positional else None


def _unbound(node: ast.FunctionDef | ast.AsyncFunctionDef) -> ast.FunctionDef | ast.AsyncFunctionDef:
    """Copy a method's definition without its first parameter (`self`).

    Returns:
      The copy.

    """
    args: ast.arguments = copy.copy(node.args)
    if args.posonlyargs:
        args.posonlyargs = args.posonlyargs[1:]
    else:
        args.args = args.args[1:]
    unbound: ast.FunctionDef | ast.AsyncFunctionDef = copy.copy(node)
    unbound.args = args
    return unbound


def _shared(parameter: Param) -> str:
    """Write a parameter every signature has alike, which takes whatever a call passes it, compactly.

    Returns:
      Its name and kind, and `=` if it has a default: `bufsize e=`.

    """
    return f"{parameter.name} {parameter.kind}{'=' if parameter.default else ''}"


def _key(parameter: Param) -> _Key:
    annotation: str = "" if parameter.annotation is None else ast.dump(parameter.annotation)
    return parameter.name, parameter.kind, parameter.default, annotation


class Overloads:
    """Signatures read for `--fix` to pick among, as one configuration sees the stubs."""

    def __init__(self, reading: Reading, canonical: dict[ClassRef, str]) -> None:
        """Read with `reading`; `canonical`: every public class's path, generic ones too."""
        self.reading: Reading = reading
        self.canonical: dict[ClassRef, str] = canonical
        self._names: dict[str, frozenset[str] | None] = {}

    def entry(
        self,
        defs: Defs,
        module: str,
        selves: Sequence[ast.expr | None] = (),
    ) -> list[Signature] | None:
        """Read a function's signatures, in order, as the `overloads` table holds them.

        `selves`: a method's (read without `self`) each signature's `self` annotation, if any.

        Returns:
          Each one's parameters (`[name, kind, default, accepts]`, or `"name kind="` where every
          signature has the parameter alike: see `_shared`) and return template (null if it can't
          be written);
          or `None` if a signature can't be read, or none's return can be written.

        """
        if any(not readable(node) for node in defs):
            return None
        each: list[list[Param]] = [parameters(node) for node in defs]
        keys: list[set[_Key]] = [{_key(p) for p in one} for one in each]
        shared: set[_Key] = keys[0].intersection(*keys[1:])
        found: list[Signature] = []
        node: ast.FunctionDef | ast.AsyncFunctionDef
        one: list[Param]
        index: int
        for index, (node, one) in enumerate(zip(defs, each, strict=True)):
            params: list[Parameter | str] = [
                _shared(p) if _key(p) in shared else (p.name, p.kind, p.default, self._accepted(p, module))
                for p in one
            ]
            signature: Signature = Signature(params=params, returns=self.template(node.returns, module))
            instance: list[str] | None
            if index < len(selves) and (instance := self._instance(selves[index], module)) is not None:
                signature["self"] = instance
            found.append(signature)
        return found if any(signature["returns"] is not None for signature in found) else None

    def methods(
        self,
        klass: ClassRef,
        fixed: Iterable[str],
        *,
        inherited: bool = True,
    ) -> dict[str, "_Method"]:
        """Read a class's plain methods whose arguments decide their return: not `fixed` (typed alike always).

        A method's signatures are read without its `self`, as a call on an instance passes it; with
        `inherited` false, only the class's own (a generic base's type variables aren't its own).

        Returns:
          Each one's defining class and method (`module.Class.name`: one entry for all the classes
          inheriting it) and signatures (see `entry`), by name.

        """
        found: dict[str, _Method] = {}
        known: frozenset[str] = frozenset(fixed)
        name: str
        function: Function
        owner: ClassRef
        for name, (function, owner) in self.reading.functions(klass).items():
            decorators: set[str] = {decorator_name(d) for d in function.defs[0].decorator_list}
            signatures: list[Signature] | None
            if name in known or decorators & _NOT_METHODS or (not inherited and owner != klass):
                continue
            if (
                signatures := self.entry(
                    tuple(_unbound(node) for node in function.defs),
                    owner.module,
                    [_self(node) for node in function.defs],
                )
            ) is not None:
                found[name] = (f"{owner.module}.{owner.name}.{name}", signatures)
        return found

    def _instance(self, annotation: ast.expr | None, module: str) -> list[str] | None:
        """Read the type arguments a method's `self` annotation gives its class (`Pattern[str]`'s `str`).

        Returns:
          Them, or `None` if it gives none, or one names a type variable or can't be written.

        """
        if not isinstance(annotation, ast.Subscript):
            return None
        index: ast.expr = annotation.slice
        args: list[ast.expr] = list(index.elts) if isinstance(index, ast.Tuple) else [index]
        texts: list[str | None] = [self.template(arg, module) for arg in args]
        if None in texts or self._variables(annotation.slice, module):
            return None
        return [text for text in texts if text is not None]

    def type_parameters(self, klass: ClassRef) -> list[str] | None:
        """Name a generic class's type parameters, in order.

        Its `Generic[...]`'s (or `Protocol[...]`'s), else the type variables its bases' arguments
        name, as they first appear.

        Returns:
          Their names, or `None` if it isn't a class here.

        """
        node: ast.ClassDef | None
        if (node := self.reading.class_node(klass)) is None:
            return None
        base: ast.expr
        for base in node.bases:
            found: Found | None
            if (
                isinstance(base, ast.Subscript)
                and (found := self.reading.ref(base.value, klass.module)) is not None
                and found.module in _TYPING
                and found.name in _DECLARING
            ):
                return self._variables(base.slice, klass.module)
        return list(
            dict.fromkeys(name for base in node.bases for name in self._variables(base, klass.module)),
        )

    def _variables(self, expr: ast.expr, module: str) -> list[str]:
        """Name the type variables an expression names, in order, one with a default marked `=` (`_T=`).

        Returns:
          Them.

        """
        names: list[ast.Name] = [node for node in ast.walk(expr) if isinstance(node, ast.Name)]
        found: list[Found | None] = [self.reading.ref(node, module) for node in names]
        return [
            node.id + ("=" if target.binding.default else "")
            for node, target in zip(names, found, strict=True)
            if target is not None and isinstance(target.binding, TypeVariable)
        ]

    def _accepted(self, parameter: Param, module: str) -> Accepts:
        """Write what a parameter takes as the tables hold it.

        Returns:
          Its verdicts.

        """
        verdicts: Verdicts = (
            Verdicts(MAYBE * len(SCALARS))
            if parameter.annotation is None
            else self.accepts(parameter.annotation, module)
        )
        found: Accepts = Accepts(v=verdicts.values)
        if verdicts.constants is not None:
            found["c"] = verdicts.constants
        if verdicts.literals is not None:
            found["lit"] = list(verdicts.literals)
        if verdicts.binds:
            found["var"] = _binding(verdicts.binds)
        return found

    def accepts(self, annotation: ast.expr, module: str) -> Verdicts:
        """Work out which `SCALARS` types a parameter's annotation takes.

        Returns:
          Its verdicts (see `Verdicts`).

        """
        atoms: list[Atom] = list(self._atoms(annotation, module, 0))
        literals: list[Constant] = [value for atom in atoms for value in atom.literals]
        values: str = "".join(self._verdict(atoms, scalar, constant=False) for scalar in SCALARS)
        constants: str = "".join(self._verdict(atoms, scalar, constant=True) for scalar in SCALARS)
        binds: dict[str, tuple[str, str]] = {}
        scalar: str
        for scalar in SCALARS:
            bound: tuple[str, str] | None
            if (bound := self._binds(atoms, scalar)) is not None:
                binds[scalar] = bound
        return Verdicts(
            values,
            constants if literals and constants != values else None,
            tuple(literals) if literals else None,
            binds or None,
        )

    def _atoms(self, expr: ast.expr, module: str, hops: int) -> Iterator[Atom]:
        """Split an annotation into its union's members, through aliases, `Optional`, `Union`, strings.

        Yields:
          Each member: `None`, a `Literal`'s values, a name found (and its subscript, if any), or
          one that can't be read.

        """
        left: ast.expr
        right: ast.expr
        text: str
        if hops > _MAX_DEPTH:
            yield Atom(_ATOM_UNKNOWN)
            return
        match expr:
            case ast.Constant(value=None):
                yield Atom(_ATOM_NONE)
            case ast.Constant(value=str() as text):
                yield from self._atoms(_parsed(text), module, hops + 1)
            case ast.BinOp(left=left, op=ast.BitOr(), right=right):
                yield from self._atoms(left, module, hops + 1)
                yield from self._atoms(right, module, hops + 1)
            case ast.Subscript():
                yield from self._subscript_atoms(expr, module, hops)
            case ast.Name() | ast.Attribute():
                found: Found | None = self.reading.ref(expr, module)
                if found is not None and isinstance(found.binding, Alias):
                    yield from self._atoms(found.binding.value, found.module, hops + 1)
                else:
                    yield Atom(_ATOM_UNKNOWN) if found is None else Atom(_ATOM_FOUND, found)
            case _:
                yield Atom(_ATOM_UNKNOWN)

    def _subscript_atoms(self, expr: ast.Subscript, module: str, hops: int) -> Iterator[Atom]:
        found: Found | None = self.reading.ref(expr.value, module)
        args: list[ast.expr] = list(expr.slice.elts) if isinstance(expr.slice, ast.Tuple) else [expr.slice]
        if found is None:
            yield Atom(_ATOM_UNKNOWN)
        elif found.module in _TYPING and found.name in _UNIONS:
            members: list[ast.expr] = [*args, *([ast.Constant(None)] if found.name == _OPTIONAL else [])]
            yield from (atom for member in members for atom in self._atoms(member, module, hops + 1))
        elif found.module in _TYPING and found.name == _LITERAL:
            constants: list[Constant] = _constants(args)
            yield Atom(_ATOM_LITERAL, literals=tuple(constants))
        elif found.module in _TYPING and found.name == _ANNOTATED:
            yield from self._atoms(args[0], module, hops + 1)
        elif isinstance(found.binding, Alias):  # a generic alias: taken whole, its parameters unread
            yield from (
                inner._replace(subscripted=True)
                for inner in self._atoms(found.binding.value, found.module, hops + 1)
            )
        else:
            yield Atom(_ATOM_FOUND, found, subscripted=True)

    def _verdict(self, atoms: Sequence[Atom], scalar: str, *, constant: bool) -> str:
        """Decide whether a parameter takes an argument of type `scalar` (a literal one if `constant`).

        Returns:
          `YES` if a member certainly does, `NO` if every member certainly doesn't, else `MAYBE`.

        """
        verdicts: set[str] = {self._atom(atom, scalar, constant=constant) for atom in atoms}
        if YES in verdicts:
            return YES
        return NO if verdicts == {NO} else MAYBE

    def _atom(self, atom: Atom, scalar: str, *, constant: bool) -> str:
        if atom.kind == _ATOM_NONE:
            return YES if scalar == _NONE else NO
        if atom.kind == _ATOM_LITERAL:
            types: set[str] = {_type_name(value) for value in atom.literals}
            matches: bool = scalar in types or (scalar == _LITERAL_STRING and _STR in types)
            return NO if constant or not matches else MAYBE  # a literal among them is matched apart
        if atom.found is not None:
            return self._found(atom.found, scalar, subscripted=atom.subscripted)
        return MAYBE

    def _found(self, found: Found, scalar: str, *, subscripted: bool) -> str:
        """Decide whether a name a parameter's annotation uses takes an argument of type `scalar`.

        Returns:
          The verdict.

        """
        if found.module in _TYPING and found.name in _ANY:
            return YES
        if found.module in _TYPING and found.name == _LITERAL_STRING:
            return YES if scalar == _LITERAL_STRING else NO
        if found.module in _TYPING and found.name in _REFUSING:
            return NO
        if isinstance(found.binding, TypeVariable):
            return self._type_variable(found.binding, found.module, scalar)
        return (
            self._klass(found, scalar, subscripted=subscripted) if isinstance(found.binding, Klass) else MAYBE
        )

    def _klass(self, found: Found, scalar: str, *, subscripted: bool = False) -> str:
        """Decide whether a class a parameter's annotation names takes an argument of type `scalar`.

        By inheritance, or for a protocol by its members' names; a builtin number takes a narrower
        one (`int` for `float`).

        Returns:
          The verdict.

        """
        klass: ClassRef = ClassRef(found.module, found.name)
        node: ast.ClassDef | None = self.reading.class_node(klass)
        if klass == ClassRef(_BUILTINS, _OBJECT) or (
            klass.module == _BUILTINS and (scalar, klass.name) in _PROMOTED
        ):
            return YES
        verdict: str = (
            self._structural(klass, scalar)
            if node is not None and self.reading.is_protocol(node, klass.module)
            else self._nominal(klass, scalar)
        )
        # A generic class's parameters aren't read: the class taking it isn't enough.
        return MAYBE if verdict == YES and (subscripted or self.reading.generic(klass)) else verdict

    def _type_variable(self, variable: TypeVariable, module: str, scalar: str) -> str:
        if variable.constraints:
            return self._verdict(
                [atom for constraint in variable.constraints for atom in self._atoms(constraint, module, 1)],
                scalar,
                constant=False,
            )
        if variable.bound is not None:
            return self._verdict(list(self._atoms(variable.bound, module, 1)), scalar, constant=False)
        return YES

    def _binds(self, atoms: Sequence[Atom], scalar: str) -> tuple[str, str] | None:
        """Find the type variable an argument of type `scalar` binds, if one member alone takes it.

        Returns:
          Its name, and what it's bound to: a constraint's type, or the argument's own (a literal's
          widened to `str`); or `None`.

        """
        taking: list[Atom] = [atom for atom in atoms if self._atom(atom, scalar, constant=False) != NO]
        found: Found | None
        if len(taking) != 1 or (found := taking[0].found) is None:
            return None
        variable: Binding = found.binding
        if not isinstance(variable, TypeVariable) or self._atom(taking[0], scalar, constant=False) != YES:
            return None
        widened: str = _STR if scalar == _LITERAL_STRING else scalar
        if not variable.constraints:
            return found.name, widened
        texts: set[str | None] = {
            self.template(constraint, found.module)
            for constraint in variable.constraints
            if self._verdict(list(self._atoms(constraint, found.module, 1)), scalar, constant=False) == YES
        }
        text: str | None = texts.pop() if len(texts) == 1 else None
        return None if text is None else (found.name, text)

    def _nominal(self, klass: ClassRef, scalar: str) -> str:
        """Decide by inheritance whether an argument of type `scalar` is an instance of `klass`.

        Returns:
          The verdict (`MAYBE` if the scalar's class's order can't be worked out).

        """
        if scalar == _NONE:
            return NO
        order: list[ClassRef] | None
        if (order := self.reading.mro(ClassRef(_BUILTINS, _CLASSES.get(scalar, scalar)))) is None:
            return MAYBE
        return YES if klass in order else NO

    def _structural(self, protocol: ClassRef, scalar: str) -> str:
        """Decide by its members' names whether an argument of type `scalar` has a protocol's members.

        Returns:
          `YES` if it has them all, `NO` if it lacks one, `MAYBE` if either can't be told.

        """
        needed: frozenset[str] | None = self._protocol_names(protocol)
        has: frozenset[str] | None = self._class_names(_CLASSES.get(scalar, scalar))
        if needed is None or has is None:
            return MAYBE
        return YES if needed <= has else NO

    def _protocol_names(self, protocol: ClassRef) -> frozenset[str] | None:
        classes: list[ClassRef]
        whole: bool
        classes, whole = self.reading.trusted(protocol)
        if not whole:
            return None
        return (
            frozenset(
                name for owner in classes if self._is_protocol(owner) for name in self.reading.body(owner)
            )
            - _MACHINERY
        )

    def _is_protocol(self, klass: ClassRef) -> bool:
        node: ast.ClassDef | None = self.reading.class_node(klass)
        return node is not None and self.reading.is_protocol(node, klass.module)

    def _class_names(self, name: str) -> frozenset[str] | None:
        """Name what a builtin class's instances have: its members, its bases', `object`'s.

        Returns:
          Them, or `None` if its bases can't all be followed.

        """
        if name not in self._names:
            classes: list[ClassRef]
            whole: bool
            classes, whole = self.reading.trusted(ClassRef(_BUILTINS, name))
            self._names[name] = (
                frozenset(
                    member
                    for owner in (*classes, ClassRef(_BUILTINS, _OBJECT))
                    for member in self.reading.body(owner)
                )
                if whole
                else None
            )
        return self._names[name]

    def template(self, expr: ast.expr | None, module: str, hops: int = 0) -> str | None:
        """Spell a return annotation as a template: builtins, classes' dotted paths, type variables' names.

        Returns:
          It, or `None` if it can't be written (`Any`, `Self`, a class with no public path) or
          `--fix` shouldn't write it (vague, too deep, `None` alone).

        """
        found: str | None = None if expr is None else self._spelled(expr, module, hops)
        return found if found is not None and usable(found) else None

    def _spelled(self, expr: ast.expr, module: str, hops: int) -> str | None:
        left: ast.expr
        right: ast.expr
        text: str
        found: str | None = None
        match expr:
            case _ if hops > _MAX_DEPTH:
                pass
            case ast.Constant(value=None):
                found = _NONE
            case ast.Constant(value=str() as text):
                found = self._spelled(_parsed(text), module, hops + 1)
            case ast.BinOp(left=left, op=ast.BitOr(), right=right):
                found = self._union([left, right], module, hops)
            case ast.Subscript():
                found = self._spelled_subscript(expr, module, hops)
            case ast.Name() | ast.Attribute():
                target: Found | None = self.reading.ref(expr, module)
                found = None if target is None else self._spelled_name(target, hops)
            case _:
                pass
        return found

    def _union(self, parts: Sequence[ast.expr], module: str, hops: int) -> str | None:
        spelled: list[str | None] = [self._spelled(part, module, hops + 1) for part in parts]
        return None if None in spelled else _joined([part for part in spelled if part is not None])

    def _spelled_name(self, found: Found, hops: int) -> str | None:
        value: ast.expr
        if found.module in _TYPING and found.name == _LITERAL_STRING:
            return _STR
        match found.binding:
            case TypeVariable():
                return found.name
            case Alias(value=value):
                return self._spelled(value, found.module, hops + 1)
            case Klass():
                klass: ClassRef = ClassRef(found.module, found.name)
                if self.reading.generic(klass) or klass.name in _UNWRITTEN:
                    return None
                return klass.name if klass.module == _BUILTINS else self.canonical.get(klass)
            case _:
                return None

    def _spelled_subscript(self, expr: ast.Subscript, module: str, hops: int) -> str | None:
        found: Found | None = self.reading.ref(expr.value, module)
        args: list[ast.expr] = list(expr.slice.elts) if isinstance(expr.slice, ast.Tuple) else [expr.slice]
        if found is None:
            return None
        typing_class: bool = isinstance(found.binding, Klass) and found.name not in TYPING_GENERICS
        if found.module in _TYPING and found.name not in TYPING_GENERICS and not typing_class:
            return self._special(found.name, args, module, hops)
        # `typing`'s own generic classes (`Iterator`) by their public path (`collections.abc.Iterator`).
        base: str | None = (
            TYPING_GENERICS.get(found.name)
            if found.module in _TYPING and not typing_class
            else self._generic_base(found)
        )
        inner: list[str | None] = [
            "..."
            if isinstance(arg, ast.Constant) and arg.value is Ellipsis
            else self._spelled(arg, module, hops + 1)
            for arg in args
        ]
        arity: int | None = ARITY.get(base or "")
        if base is None or not inner or None in inner or (arity is not None and arity != len(inner)):
            return None
        return f"{base}[{', '.join(part for part in inner if part is not None)}]"

    def _special(self, name: str, args: list[ast.expr], module: str, hops: int) -> str | None:
        """Spell one of `typing`'s subscripted forms in a return: `Optional`, `Union`, `Literal`, a guard.

        Returns:
          It, or `None` for any other.

        """
        if name in _UNIONS:
            return self._union([*args, *([ast.Constant(None)] if name == _OPTIONAL else [])], module, hops)
        if name == _LITERAL:
            constants: list[Constant] = _constants(args)
            return (
                _joined([_type_name(value) for value in constants]) if len(constants) == len(args) else None
            )
        return "bool" if name in _GUARDS else None

    def _generic_base(self, found: Found) -> str | None:
        """Spell a generic class subscripted in a return: a builtin container, or a class's dotted path.

        Returns:
          It, or `None`.

        """
        if not isinstance(found.binding, Klass):
            return None
        klass: ClassRef = ClassRef(found.module, found.name)
        if klass.module == _BUILTINS:
            return klass.name if klass.name in _CONTAINERS else None
        return self.canonical.get(klass) if self.reading.generic(klass) else None


def _parsed(text: str) -> ast.expr:
    """Parse a string annotation (a forward reference); one that doesn't parse is `...`, naming nothing.

    Returns:
      Its expression.

    """
    try:
        return ast.parse(text, mode="eval").body
    except SyntaxError:
        return ast.Constant(...)


def _constants(nodes: Sequence[ast.expr]) -> list[Constant]:
    """Read a `Literal[...]`'s builtin constants (another member, an enum's, is left out).

    Returns:
      Them.

    """
    value: Constant
    found: list[Constant] = []
    node: ast.expr
    for node in nodes:
        match node:
            case ast.Constant(value=bool() | int() | float() | str() | bytes() | None as value):
                found.append(value)
            case _:
                pass
    return found


def _type_name(value: Constant) -> str:
    return _NONE if value is None else type(value).__name__


def _joined(parts: Sequence[str]) -> str:
    """Join annotations with `|`, each member once, in order.

    Returns:
      The union.

    """
    members: list[str] = []
    part: str
    for part in parts:
        member: str
        for member in _members(ast.parse(part, mode="eval").body):
            if member not in members:
                members.append(member)
    return " | ".join(members)


def _members(expr: ast.expr) -> Iterator[str]:
    """Walk a union's members (`a | b | c`), not into brackets.

    Yields:
      Each one's text.

    """
    if isinstance(expr, ast.BinOp) and isinstance(expr.op, ast.BitOr):
        yield from _members(expr.left)
        yield from _members(expr.right)
    else:
        yield ast.unparse(expr)
