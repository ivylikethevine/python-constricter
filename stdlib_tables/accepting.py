# SPDX-License-Identifier: MIT
"""Which argument types a standard-library parameter's annotation certainly takes or refuses.

`Accepting.accepts` reads an annotation into its union's members (`Atom`s) and gives a verdict,
`YES`, `NO` or `MAYBE`, for each builtin scalar in `SCALARS` (`LiteralString` standing for a `str`
literal): by its class, nominally, or by a protocol's members, structurally; and, where a type
variable is bound by the argument, the type it binds. For `stdlib_tables.overloads`, whose
`Overloads` reads the signatures these verdicts are part of.
"""

import ast
from collections.abc import Iterator, Sequence
from typing import Final, NamedTuple

from constricter.fix.core.signatures import (
    Constant,
)
from stdlib_tables.forms import ClassRef, substituted
from stdlib_tables.reading import Reading
from stdlib_tables.stubs import (
    Alias,
    Binding,
    Found,
    Function,
    Klass,
    TypeVariable,
)
from stdlib_tables.templates import (
    BUILTINS,
    LITERAL,
    LITERAL_STRING,
    MAX_DEPTH,
    NONE,
    OBJECT,
    OPTIONAL,
    STR,
    TYPING,
    UNIONS,
    Templates,
    literal_values,
    parsed,
    type_name,
)

SCALARS: Final = ("str", "LiteralString", "bytes", "bytearray", "int", "float", "complex", "bool", "None")
YES: Final = "y"
NO: Final = "n"
MAYBE: Final = "?"


ANY: Final = frozenset({"Any", "Incomplete"})
REFUSING: Final = frozenset({"Callable", "Type", "type"})  # no scalar is a callable or a class
ANNOTATED: Final = "Annotated"
# A builtin scalar a parameter of another builtin type takes all the same (numbers widened).
PROMOTED: Final = {
    ("int", "float"),
    ("int", "complex"),
    ("float", "complex"),
    ("bool", "float"),
    ("bool", "complex"),
}
# The class an argument of each type is an instance of (`None`'s, `object`, less what it doesn't have).
CLASSES: Final = {"LiteralString": STR, "None": OBJECT}


# What a protocol's body binds that isn't a member its instances need (`typing`'s own protocols'
# `__slots__ = ()`).
MACHINERY: Final = frozenset({"__slots__", "__init__", "__new__", "__class_getitem__", "__init_subclass__"})
ATOM_NONE: Final = "none"
ATOM_LITERAL: Final = "literal"
ATOM_FOUND: Final = "found"
ATOM_UNKNOWN: Final = "unknown"


CALLABLE: Final = "Callable"


AWAITABLES: Final = frozenset({"Awaitable", "Coroutine", "Future", "Task"})


# The builtin containers whose element an argument of the type binds a parameter's type variable to.
CONTAINERS: Final = ("list", "tuple", "set", "frozenset", "dict")


class Atom(NamedTuple):
    """One member of a parameter's union: `None`, a `Literal`'s values, a name found, or one unread."""

    kind: str
    found: Found | None = None
    subscripted: bool = False  # the name, with type arguments (`PathLike[str]`)
    literals: tuple[Constant, ...] = ()


class Verdicts(NamedTuple):
    """What a parameter takes: a verdict per `SCALARS` type, and more for literals and type variables.

    `values`: for a variable argument; `constants`: for a literal argument not among `literals`
    (the values of its `Literal[...]` members), if they differ; `binds`: the type variable the
    parameter is, and what an argument of each type binds it to. `anything`: the type variable the
    parameter is, if it's unbounded, which any argument binds to its own type; `elements`: for a
    parameter that is a generic class of one type variable (`Iterable[_T]`), that variable, and which
    type argument of each builtin container in `CONTAINERS` taking it binds it (`dict`'s keys: 0);
    `returned`: for a callable returning an unbounded type variable (`Callable[..., _T]`), that
    variable, which a function argument binds to its declared return.
    """

    values: str
    constants: str | None = None
    literals: tuple[Constant, ...] | None = None
    binds: dict[str, tuple[str, str]] | None = None
    anything: str | None = None
    elements: tuple[str, dict[str, int]] | None = None
    returned: str | None = None
    awaited: str | None = None  # for an awaitable, the unbounded type variable awaiting it gives
    bounded: str | None = None  # the type variable the parameter is, if a bound is all that limits it


def unbounded(atoms: Sequence[Atom], *, bounded: bool = False) -> str | None:
    """Name the type variable a parameter is, if it's all it is, with no limit (`bounded`: but a bound).

    Returns:
      Its name, or `None`.

    """
    found: Found | None = atoms[0].found if len(atoms) == 1 else None
    variable: Binding | None = None if found is None else found.binding
    if not isinstance(variable, TypeVariable) or variable.constraints:
        return None
    return None if variable.bound is not None and not bounded else variable.name


class Accepting(Templates):
    """What a configuration's parameters take of each argument type (see the module docstring)."""

    def __init__(self, reading: Reading, canonical: dict[ClassRef, str]) -> None:
        """Read with `reading`; `canonical`: every public class's path, generic ones too."""
        super().__init__(reading, canonical)
        self._names: dict[str, frozenset[str] | None] = {}
        self._taken: dict[tuple[ClassRef, str, bool], str] = {}  # `_klass`'s verdicts

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
        # A scalar that is one (`str`, an `Iterable[str]`; `float`, a `_SupportsFloor[int]`) binds it.
        of: tuple[ClassRef, str] | None
        if (of := self._of_one(annotation, module)) is not None:
            taken: list[bool] = []
            for scalar in SCALARS:
                element: str | None = self._scalar_element(scalar, of[0])
                taken.append(element is not None)
                if element is not None:
                    binds[scalar] = (of[1], element)
            values = "".join(YES if yes else verdict for yes, verdict in zip(taken, values, strict=True))
            constants = "".join(
                YES if yes else verdict for yes, verdict in zip(taken, constants, strict=True)
            )
        return Verdicts(
            values,
            constants if literals and constants != values else None,
            tuple(literals) if literals else None,
            binds or None,
            unbounded(atoms),
            None if of is None else self._container_elements(*of),
            self._callable_return(annotation, module),
            self._awaited(annotation, module, 0),
            unbounded(atoms, bounded=True),
        )

    def _awaited(self, annotation: ast.expr, module: str, hops: int) -> str | None:
        """Name the unbounded type variable awaiting a parameter gives (`Coroutine[Any, Any, _T]`'s `_T`).

        Of an `Awaitable`, a `Coroutine`, a `Future` or a `Task`, alone or in a union, or an alias of
        one written with the variable (`_CoroutineLike[_T]`).

        Returns:
          Its name, or `None` for any other parameter.

        """
        head: ast.expr
        last: ast.expr
        match annotation:
            case ast.BinOp(left=head, op=ast.BitOr(), right=last):
                return self._awaited(head, module, hops) or self._awaited(last, module, hops)
            case ast.Subscript(value=head, slice=ast.Tuple(elts=[*_, last]) | last):
                pass
            case _:
                return None
        found: Found | None = self.reading.ref(head, module)
        awaitable: bool = found is not None and found.name in AWAITABLES
        if found is not None and isinstance(found.binding, Alias) and hops < MAX_DEPTH:
            # An alias of one, written with its own variable: the one it's subscripted with here.
            awaitable = self._awaited(found.binding.value, found.module, hops + 1) is not None
        return unbounded(list(self._atoms(last, module, 1))) if awaitable else None

    def _callable_return(self, annotation: ast.expr, module: str) -> str | None:
        """Name the unbounded type variable a callable parameter returns (`Callable[..., _T]`'s `_T`).

        Returns:
          Its name, or `None` for any other parameter.

        """
        callee: ast.expr
        returned: ast.expr
        match annotation:
            case ast.Subscript(value=callee, slice=ast.Tuple(elts=[_, returned])):
                pass
            case _:
                return None
        found: Found | None = self.reading.ref(callee, module)
        if found is None or found.name != CALLABLE:
            return None
        return unbounded(list(self._atoms(returned, module, 1)))

    def _of_one(self, annotation: ast.expr, module: str) -> tuple[ClassRef, str] | None:
        """Read a parameter that is a generic class of one unbounded type variable (`Iterable[_T]`).

        Returns:
          The class, and the variable's name; or `None`.

        """
        if not isinstance(annotation, ast.Subscript) or isinstance(annotation.slice, ast.Tuple):
            return None
        found: Found | None = self.reading.ref(annotation.value, module)
        inner: list[Atom] = list(self._atoms(annotation.slice, module, 1))
        name: str | None = unbounded(inner)
        if found is None or not isinstance(found.binding, Klass) or name is None:
            return None
        return ClassRef(found.module, found.name), name

    def _scalar_element(self, scalar: str, generic: ClassRef) -> str | None:
        """Find what a builtin scalar that is a `generic` (`str`, an `Iterable[str]`) binds its variable to.

        Returns:
          That type, if it's a builtin scalar (`bytes`' `int`); or `None`.

        """
        builtin: ClassRef = ClassRef(BUILTINS, CLASSES.get(scalar, scalar))
        found: list[str] | None = self.base_arguments(builtin, generic)
        protocol: str | None = None if found is not None else self._protocol_element(scalar, generic)
        found = found if protocol is None else [protocol]
        return found[0] if found is not None and len(found) == 1 and found[0] in SCALARS else None

    def _protocol_element(self, scalar: str, protocol: ClassRef) -> str | None:
        """Find what a scalar that has a generic protocol's members binds its one type parameter to.

        By the methods returning it (`_SupportsFloor[_T]`'s `__floor__`), as the scalar's class
        declares them (`float.__floor__` returns an `int`).

        Returns:
          That type, if every such method returns the same; or `None`.

        """
        node: ast.ClassDef | None = self.reading.class_node(protocol)
        params: list[str] = [param.rstrip("=") for param in self.type_parameters(protocol) or []]
        if (
            node is None
            or len(params) != 1
            or not self.reading.is_protocol(node, protocol.module)
            or self._structural(protocol, scalar) != YES
        ):
            return None
        owners: list[ClassRef] = self.reading.trusted(ClassRef(BUILTINS, CLASSES.get(scalar, scalar)))[0]
        found: set[str | None] = set()
        name: str
        binding: Binding
        for name, binding in self.reading.body(protocol).items():
            returns: ast.expr | None = binding.defs[0].returns if isinstance(binding, Function) else None
            if returns is None or self._spelled(returns, protocol.module, 0) != params[0]:
                continue
            method: Binding | None = next(
                (body[name] for body in (self.reading.body(owner) for owner in owners) if name in body),
                None,
            )
            found.update(
                {self.template(d.returns, BUILTINS) for d in method.defs}
                if isinstance(method, Function)
                else {None},
            )
        return found.pop() if len(found) == 1 else None

    def _container_elements(self, generic: ClassRef, variable: str) -> tuple[str, dict[str, int]] | None:
        """Find which type argument of each builtin container that is a `generic` binds its variable.

        Returns:
          The variable, and each such container's index (`list`'s 0, `dict`'s keys' 0); or `None` if
          none is.

        """
        found: dict[str, int] = {}
        container: str
        for container in CONTAINERS:
            klass: ClassRef = ClassRef(BUILTINS, container)
            params: list[str] = [param.rstrip("=") for param in self.type_parameters(klass) or []]
            arguments: list[str] | None = self.base_arguments(klass, generic)
            if arguments is not None and len(arguments) == 1 and arguments[0] in params:
                found[container] = params.index(arguments[0])
        return (variable, found) if found else None

    def base_arguments(self, klass: ClassRef, base: ClassRef, hops: int = 0) -> list[str] | None:
        """Spell the type arguments `klass` gives an ancestor (`list` gives `Iterable` its own `_T`).

        Through its bases' arguments, each class's type parameters replaced by what its subclass
        passes them.

        Returns:
          Them, in terms of `klass`'s own type parameters; or `None` if it isn't an ancestor, or an
          argument can't be spelled.

        """
        node: ast.ClassDef | None = self.reading.class_node(klass)
        if node is None or hops > MAX_DEPTH:
            return None
        written: ast.expr
        for written in node.bases:
            value: ast.expr = written.value if isinstance(written, ast.Subscript) else written
            found: Found | None = self.reading.ref(value, klass.module)
            if found is None or not isinstance(found.binding, Klass):
                continue
            parent: ClassRef = ClassRef(found.module, found.name)
            args: list[ast.expr] = []
            if isinstance(written, ast.Subscript):
                index: ast.expr = written.slice
                args = list(index.elts) if isinstance(index, ast.Tuple) else [index]
            texts: list[str | None] = [self._spelled(arg, klass.module, 0) for arg in args]
            if None in texts:
                continue
            spelled: list[str] = [text for text in texts if text is not None]
            if parent == base:
                return spelled
            above: list[str] | None
            if (above := self.base_arguments(parent, base, hops + 1)) is not None:
                params: list[str] = [param.rstrip("=") for param in self.type_parameters(parent) or []]
                return [substituted(text, dict(zip(params, spelled, strict=False))) for text in above]
        return None

    def _atoms(self, expr: ast.expr, module: str, hops: int) -> Iterator[Atom]:
        """Split an annotation into its union's members, through aliases, `Optional`, `Union`, strings.

        Yields:
          Each member: `None`, a `Literal`'s values, a name found (and its subscript, if any), or
          one that can't be read.

        """
        left: ast.expr
        right: ast.expr
        text: str
        if hops > MAX_DEPTH:
            yield Atom(ATOM_UNKNOWN)
            return
        match expr:
            case ast.Constant(value=None):
                yield Atom(ATOM_NONE)
            case ast.Constant(value=str() as text):
                yield from self._atoms(parsed(text), module, hops + 1)
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
                    yield Atom(ATOM_UNKNOWN) if found is None else Atom(ATOM_FOUND, found)
            case _:
                yield Atom(ATOM_UNKNOWN)

    def _subscript_atoms(self, expr: ast.Subscript, module: str, hops: int) -> Iterator[Atom]:
        found: Found | None = self.reading.ref(expr.value, module)
        args: list[ast.expr] = list(expr.slice.elts) if isinstance(expr.slice, ast.Tuple) else [expr.slice]
        if found is None:
            yield Atom(ATOM_UNKNOWN)
        elif found.module in TYPING and found.name in UNIONS:
            members: list[ast.expr] = [*args, *([ast.Constant(None)] if found.name == OPTIONAL else [])]
            yield from (atom for member in members for atom in self._atoms(member, module, hops + 1))
        elif found.module in TYPING and found.name == LITERAL:
            constants: list[Constant] = literal_values(args)
            yield Atom(ATOM_LITERAL, literals=tuple(constants))
        elif found.module in TYPING and found.name == ANNOTATED:
            yield from self._atoms(args[0], module, hops + 1)
        elif isinstance(found.binding, Alias):  # a generic alias: taken whole, its parameters unread
            yield from (
                inner._replace(subscripted=True)
                for inner in self._atoms(found.binding.value, found.module, hops + 1)
            )
        else:
            yield Atom(ATOM_FOUND, found, subscripted=True)

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
        if atom.kind == ATOM_NONE:
            return YES if scalar == NONE else NO
        if atom.kind == ATOM_LITERAL:
            types: set[str] = {type_name(value) for value in atom.literals}
            matches: bool = scalar in types or (scalar == LITERAL_STRING and STR in types)
            return NO if constant or not matches else MAYBE  # a literal among them is matched apart
        if atom.found is not None:
            return self._found(atom.found, scalar, subscripted=atom.subscripted)
        return MAYBE

    def _found(self, found: Found, scalar: str, *, subscripted: bool) -> str:
        """Decide whether a name a parameter's annotation uses takes an argument of type `scalar`.

        Returns:
          The verdict.

        """
        if found.module in TYPING and found.name in ANY:
            return YES
        if found.module in TYPING and found.name == LITERAL_STRING:
            return YES if scalar == LITERAL_STRING else NO
        if found.module in TYPING and found.name in REFUSING:
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
        key: tuple[ClassRef, str, bool]
        if (key := (ClassRef(found.module, found.name), scalar, subscripted)) not in self._taken:
            self._taken[key] = self._takes_scalar(key[0], scalar, subscripted=subscripted)
        return self._taken[key]

    def _takes_scalar(self, klass: ClassRef, scalar: str, *, subscripted: bool) -> str:
        node: ast.ClassDef | None = self.reading.class_node(klass)
        if klass == ClassRef(BUILTINS, OBJECT) or (
            klass.module == BUILTINS and (scalar, klass.name) in PROMOTED
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
        widened: str = STR if scalar == LITERAL_STRING else scalar
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
        if scalar == NONE:
            return NO
        order: list[ClassRef] | None
        if (order := self.reading.mro(ClassRef(BUILTINS, CLASSES.get(scalar, scalar)))) is None:
            return MAYBE
        return YES if klass in order else NO

    def _structural(self, protocol: ClassRef, scalar: str) -> str:
        """Decide by its members' names whether an argument of type `scalar` has a protocol's members.

        Returns:
          `YES` if it has them all, `NO` if it lacks one, `MAYBE` if either can't be told.

        """
        needed: frozenset[str] | None = self._protocol_names(protocol)
        has: frozenset[str] | None = self._class_names(CLASSES.get(scalar, scalar))
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
            - MACHINERY
        )

    def _is_protocol(self, klass: ClassRef) -> bool:
        node: ast.ClassDef | None = self.reading.class_node(klass)
        return node is not None and self.reading.is_protocol(node, klass.module)

    def takes(self, annotation: ast.expr, module: str, types: Sequence[str]) -> str:
        """Work out whether a parameter's annotation takes an argument of each builtin type in `types`.

        Returns:
          A verdict (`YES`, `NO`, `MAYBE`) per type, in order.

        """
        atoms: list[Atom] = list(self._atoms(annotation, module, 0))
        return "".join(self._verdict(atoms, name, constant=False) for name in types)

    def scalar_members(self, scalar: str) -> frozenset[str] | None:
        """Name what an argument of type `scalar` has (`None`'s: `object`'s), for protocols to be checked by.

        Returns:
          Them, or `None` if its class's bases can't all be followed.

        """
        return self._class_names(CLASSES.get(scalar, scalar))

    def _class_names(self, name: str) -> frozenset[str] | None:
        """Name what a builtin class's instances have: its members, its bases', `object`'s.

        Returns:
          Them, or `None` if its bases can't all be followed.

        """
        if name not in self._names:
            classes: list[ClassRef]
            whole: bool
            classes, whole = self.reading.trusted(ClassRef(BUILTINS, name))
            self._names[name] = (
                frozenset(
                    member
                    for owner in (*classes, ClassRef(BUILTINS, OBJECT))
                    for member in self.reading.body(owner)
                )
                if whole
                else None
            )
        return self._names[name]
