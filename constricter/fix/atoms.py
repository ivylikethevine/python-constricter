# SPDX-License-Identifier: MIT
"""What an installed package's annotations are made of, and which arguments each part takes.

An annotation is read (by `constricter.fix.stubbed`) into its union's members (`Atom`s): `None`, a
`Literal`'s values, a type variable (with its bound's members), a `type[...]`, a class, or something
unread. Each takes a builtin scalar or container argument, or a class passed as one, by the verdicts
here: a standard-library class by the `scalars` table, an installed protocol by its members, and no
other installed class.
"""

import ast
from collections.abc import Iterator, Mapping, Sequence
from types import EllipsisType
from typing import Final, NamedTuple, TypeAlias

from constricter.fix import stdlib
from constricter.fix.declared import Alias, Declarations, Protocol, Variable
from constricter.fix.known import Origin
from constricter.fix.modules import Module
from constricter.fix.overloads import CONTAINERS, SCALARS
from constricter.fix.signatures import Constant

YES: Final = "y"
NO: Final = "n"
MAYBE: Final = "?"
NONE: Final = "None"
LITERAL_STRING: Final = "LiteralString"
VAR: Final = "var"
TYPE: Final = "type"
CLASS: Final = "class"
UNKNOWN_ATOM: Final = "unknown"
STR: Final = "str"  # `project.definition`'s kind for a function `Declarations` has
BUILTINS_MODULE: Final = "builtins"
TYPING: Final = frozenset({"typing", "typing_extensions"})
ANYTHING: Final = frozenset(
    {"typing.Any", "typing_extensions.Any", "_typeshed.Incomplete", "builtins.object"},
)
TYPES: Final = frozenset({"builtins.type", "typing.Type", "typing_extensions.Type"})
REFUSING: Final = frozenset({"Callable", "Type"})  # no scalar is a callable or a class
PARAM_SPEC: Final = "*"  # a `ParamSpec`'s or `TypeVarTuple`'s bound (see `declared`)
BUILTIN_TYPES: Final = (*SCALARS, *CONTAINERS)  # the `scalars` table's columns
ELEMENT_OF: Final = frozenset({"list", "set", "frozenset"})  # one type argument: their elements'
TUPLE: Final = "tuple"
HOMOGENEOUS: Final = 2  # `tuple[int, ...]`'s arguments


class Scope(NamedTuple):
    """Where an annotation is read: its module, and the type parameters in scope.

    Each parameter is its bound's text (`None`: unbounded; `"*"`: a `ParamSpec`'s), or an
    argument an alias was subscripted with: its annotation and the scope that's read in.
    """

    module: Module
    params: Mapping[str, "str | tuple[ast.expr, Scope] | None"]
    owner: str  # the module whose function is read: only its type variables are bound


class Atom(NamedTuple):
    """One member of an annotation's union.

    `kind`: `none`, `literal` (`values`), `any`, `var` (a type variable `name`, bounded by `bound`
    read in `scope`), `type` (a `type[...]`, whose own atoms are `inner`), `class` (`origin`, and
    the installed module defining it, if one does), or `unknown`.
    """

    kind: str
    values: tuple[Constant, ...] = ()
    name: str = ""
    bound: str | None = None
    scope: Scope | None = None
    inner: tuple["Atom", ...] = ()
    origin: Origin = ("", None)
    module: Module | None = None
    subscripted: bool = False
    args: tuple[ast.expr, ...] = ()  # a class's type arguments, read in `scope`
    constrained: bool = False  # a type variable's `bound` is its constraints: it binds none of them


UNKNOWN: Final = Atom(UNKNOWN_ATOM)


# Whether an atom takes a container argument, and what that container's elements must fit, if it says.
Taken: TypeAlias = tuple[str, tuple[Atom, ...] | None]


def atom_path(atom: Atom) -> str:
    """Name a class atom by its dotted path (`typing.SupportsIndex`).

    Returns:
      It.

    """
    return f"{atom.origin[0]}.{atom.origin[1]}"


def owned(atom: Atom, owner: str) -> bool:
    """Check that a type variable is the function's own: one of its type parameters, or its module's.

    Returns:
      Whether it is.

    """
    return atom.scope is not None and atom.scope.module.name == owner


def argument_of(atom: Atom) -> tuple[ast.expr, Scope]:
    """Read back the argument an alias's parameter was bound to (an `arg` atom).

    Returns:
      Its annotation, and the scope it's read in.

    """
    scope: Scope | None = atom.scope
    assert scope is not None  # an `arg` atom always has one  # ruff: ignore[assert]
    return parse_text(atom.name), scope


def bound_alias(alias: Alias, where: Scope, args: Sequence[ast.expr], caller: Scope) -> Scope:
    """Scope an alias's value: its type parameters bound to the arguments it's subscripted with.

    Its own (`type X[T] = ...`), or else the type variables its value names, in order; one without
    an argument stays unbound (any type).

    Returns:
      The scope.

    """
    params: tuple[str, ...] = alias.params or free_variables(alias.value, where)
    bound: dict[str, str | tuple[ast.expr, Scope] | None] = dict.fromkeys(params)
    name: str
    arg: ast.expr
    for name, arg in zip(params, args, strict=False):
        bound[name] = (arg, caller)
    return Scope(where.module, bound, caller.owner)


def free_variables(value: str, scope: Scope) -> tuple[str, ...]:
    """Name the type variables an old-style alias's value names (its parameters), in order.

    Returns:
      Them.

    """
    declared: Declarations | None = scope.module.declared
    variables: Mapping[str, Variable] = {} if declared is None else declared.variables
    return tuple(
        dict.fromkeys(
            node.id
            for node in ast.walk(parse_text(value))
            if isinstance(node, ast.Name) and (node.id in variables or node.id in scope.module.type_vars)
        ),
    )


def verdict_of(atoms: Sequence[Atom], scalar: str, *, constant: bool) -> str:
    """Decide whether an annotation's atoms take an argument of type `scalar` (a literal one if `constant`).

    Returns:
      `y` if one certainly does, `n` if none does, else `?`.

    """
    return combined({scalar_verdict(atom, scalar, constant=constant) for atom in atoms})


def combined(verdicts: set[str]) -> str:
    """Combine the verdicts of a union's members: `y` if one takes it, `n` if none does, else `?`.

    Returns:
      The verdict.

    """
    if YES in verdicts:
        return YES
    return NO if verdicts == {NO} else MAYBE


def scalar_verdict(atom: Atom, scalar: str, *, constant: bool) -> str:
    """Decide whether one atom takes an argument of type `scalar`.

    Returns:
      The verdict.

    """
    match atom.kind:
        case "none":
            return YES if scalar == NONE else NO
        case "literal":
            types: set[str] = {type(value).__name__ if value is not None else NONE for value in atom.values}
            matches: bool = scalar in types or (scalar == LITERAL_STRING and STR in types)
            return NO if constant or not matches else MAYBE
        case "var":
            return bound_verdict(atom, scalar)
        case "type":
            return NO
        case "class":
            return class_takes(atom, scalar)
        case _:
            return MAYBE


def bound_verdict(atom: Atom, scalar: str) -> str:
    """Decide whether a type variable takes an argument of type `scalar`, by its bound (its `inner` atoms).

    Returns:
      The verdict (`y` without one).

    """
    if atom.bound is None:
        return YES
    return MAYBE if atom.bound == PARAM_SPEC else verdict_of(atom.inner, scalar, constant=False)


def class_takes(atom: Atom, scalar: str) -> str:
    """Decide whether a class takes an argument of type `scalar`.

    A standard-library one by the `scalars` table; an installed protocol by its members (a generic
    one's parameters unread); no other installed class.

    Returns:
      The verdict.

    """
    path: str = atom_path(atom)
    if atom.module is None:
        return external_takes(path, scalar)
    declared: Declarations | None = atom.module.declared
    protocol: Protocol | None = None if declared is None else declared.protocols.get(path.rpartition(".")[2])
    members: frozenset[str] | None = stdlib.scalar_members(scalar)
    if protocol is None or (members is not None and not protocol.members <= members):
        return NO
    return (
        MAYBE
        if members is None or atom.subscripted or path.rpartition(".")[2] in atom.module.generics
        else YES
    )


def element_of(container: str, args: Sequence[ast.expr]) -> ast.expr | None:
    """Find what a builtin container's type arguments say its elements are (`list[int]`, `tuple[int, ...]`).

    Returns:
      Their annotation, or `None` for any other (`tuple[int, str]`, a `dict`'s, none at all).

    """
    if container in ELEMENT_OF and len(args) == 1:
        return args[0]
    ellipsis: bool = (
        len(args) == HOMOGENEOUS
        and isinstance(args[1], ast.Constant)
        and isinstance(args[1].value, EllipsisType)
    )
    return args[0] if container == TUPLE and ellipsis else None


def external_takes(path: str, scalar: str) -> str:
    """Decide whether a class outside the installed packages (`typing.SupportsIndex`) takes a `scalar`.

    Returns:
      The verdict: the `scalars` table's, or `?` where it hasn't one.

    """
    module: str
    name: str
    module, _, name = path.rpartition(".")
    verdicts: str | None = stdlib.scalar_verdicts(path)
    if path in ANYTHING:
        verdicts = YES * len(BUILTIN_TYPES)
    elif module in TYPING and name == LITERAL_STRING:
        verdicts = "".join(YES if each == LITERAL_STRING else NO for each in BUILTIN_TYPES)
    elif module in TYPING and name in REFUSING:
        verdicts = NO * len(BUILTIN_TYPES)
    return MAYBE if verdicts is None else verdicts[BUILTIN_TYPES.index(scalar)]


def class_verdict(atom: Atom) -> str:
    """Decide whether one atom takes a class passed as an argument (`dtype=np.float64`).

    A class is an instance of `type` alone: `type[...]`, `type` and `object` take it; `None`, a
    literal, any other class, or a protocol with an attribute or property (which a class has as a
    descriptor, not a value) don't.

    Returns:
      The verdict.

    """
    found: str = MAYBE
    match atom.kind:
        case "none" | "literal":
            found = NO
        case "type":  # a `type[T]` takes any class (bounds unchecked: a call outside one is an error)
            found = YES if all(inner.kind == VAR or is_anything(inner) for inner in atom.inner) else MAYBE
        case "var" if atom.bound is None:
            found = YES
        case "var" if atom.bound != PARAM_SPEC:
            found = combined({class_verdict(inner) for inner in atom.inner})
        case "class":
            found = class_takes_class(atom)
        case _:
            pass
    return found


def is_anything(atom: Atom) -> bool:
    """Check whether an atom is `Any`, `object` or `typeshed`'s `Incomplete`.

    Returns:
      Whether it is.

    """
    return atom.kind == CLASS and atom_path(atom) in ANYTHING


def class_takes_class(atom: Atom) -> str:
    """Decide whether a class atom takes a class passed as an argument (see `class_verdict`).

    Returns:
      The verdict.

    """
    origin: Origin = atom.origin
    if atom_path(atom) in ANYTHING | TYPES:
        return YES
    if atom.module is None:
        return NO if origin[0] == BUILTINS_MODULE else MAYBE
    declared: Declarations | None = atom.module.declared
    protocol: Protocol | None = None if declared is None else declared.protocols.get(origin[1] or "")
    return NO if protocol is None or protocol.properties else MAYBE


def scalar_binds(atoms: Sequence[Atom], scalar: str, owner: str) -> tuple[str, str] | None:
    """Find the type variable an argument of type `scalar` binds: the one member that takes it.

    Returns:
      Its name, and the argument's type (a literal's widened to `str`); or `None`.

    """
    taking: list[Atom] = [atom for atom in atoms if scalar_verdict(atom, scalar, constant=False) != NO]
    if len(taking) != 1 or taking[0].kind != VAR or taking[0].constrained or not owned(taking[0], owner):
        return None
    if scalar_verdict(taking[0], scalar, constant=False) != YES:
        return None
    return taking[0].name, STR if scalar == LITERAL_STRING else scalar


def class_binds(atoms: Sequence[Atom], owner: str) -> str | None:
    """Find the type variable a class argument binds: a `type[T]`, all else refusing a class.

    Returns:
      Its name, or `None`.

    """
    types: list[Atom] = [atom for atom in atoms if atom.kind == TYPE]
    if len(types) != 1 or any(class_verdict(atom) != NO for atom in atoms if atom.kind != TYPE):
        return None
    inner: tuple[Atom, ...] = types[0].inner
    variable: Atom | None = inner[0] if len(inner) == 1 and inner[0].kind == VAR else None
    return None if variable is None or variable.constrained or not owned(variable, owner) else variable.name


def literal_values(args: Sequence[ast.expr]) -> Iterator[Constant]:
    """Read a `Literal[...]`'s values (a name, which isn't one, left out).

    Yields:
      Each.

    """
    arg: ast.expr
    for arg in args:
        if isinstance(arg, ast.Constant) and isinstance(
            arg.value,
            bool | int | float | complex | str | bytes | None,
        ):
            yield arg.value


def joined(separator: str, parts: Sequence[str | None]) -> str | None:
    """Join a template's parts, none of which may be missing.

    Returns:
      The text, or `None` if a part is.

    """
    return None if None in parts else separator.join(part for part in parts if part is not None)


def parse_text(text: str) -> ast.expr:
    """Parse an annotation's text; one that doesn't parse (`"int["`) names nothing.

    Returns:
      Its tree.

    """
    try:
        return ast.parse(text, mode="eval").body
    except SyntaxError:
        return ast.Constant(value=...)  # read as nothing it names


def private_name(name: str | None) -> bool:
    """Check whether a dotted name (`numpy._typing`) has a private part, or is missing.

    Returns:
      Whether it has, or is.

    """
    return name is None or any(part.startswith("_") for part in name.split("."))
