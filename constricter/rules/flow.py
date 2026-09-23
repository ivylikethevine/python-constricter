# SPDX-License-Identifier: MIT
"""Value flow: every type a name is bound to over its lifetime in a scope, against its declared type.

Three rules come of it (`check_tree` reports them): a declared type every value fits a strictly
narrower one of (LVA008), a value that doesn't fit the declared type at all (LVA009), and a declared
union member no value ever uses (LVA010).

It's flow-insensitive: the order and branches bindings happen in don't matter, only the set of
values a name is ever bound to. A binding whose value `--fix` can't infer with certainty is
*unknown*, and one unknown binding (or a write from a nested function) stops the narrowing claims
(LVA008, LVA010), since the name may hold something else; it never stops LVA009, which only needs
the one value it reports. The checker also stops them for every name in a module or class body,
which other code can rebind out of sight.

Types are compared through a `Hierarchy` of which named types are narrower than which: `bool` is
narrower than `int`, `int` than `float` and `float` than `complex` (the numeric tower), and a class
defined in the module is narrower than each base it names. Any other type is only as narrow as
itself; a parameterised generic (`list[int]`) is compared by its text.
"""

import ast
from collections.abc import Iterable, Mapping
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Final, TypeAlias

# Each named type's directly wider types.
Parents: TypeAlias = Mapping[str, frozenset[str]]
# One project-declared type and the types it's narrower than (`Checks.narrower`, `parse_narrower`).
Narrower: TypeAlias = tuple[str, tuple[str, ...]]
DEFAULT_PARENTS: Final[Parents] = {
    "bool": frozenset({"int"}),
    "int": frozenset({"float"}),
    "float": frozenset({"complex"}),
}
# Annotations every value fits: nothing is learnt from comparing a value with one (LVA005's domain).
_OBJECT: Final = "object"
_ANYTHING: Final = frozenset({"Any", _OBJECT})
_NONE: Final = "None"
_OPTIONAL: Final = "Optional"
_UNION: Final = "Union"
_COMPLEX: Final = "complex"
# `typing`'s capitalised aliases, compared as the builtins they stand for.
_ALIASES: Final = {
    "Dict": "dict",
    "FrozenSet": "frozenset",
    "List": "list",
    "Set": "set",
    "Tuple": "tuple",
    "Type": "type",
}
_TYPING_MODULES: Final = frozenset({"typing", "typing_extensions"})
# Qualifiers around the type that holds the values (`ClassVar[int]`, `Final[int]`); bare, they say
# nothing (`x: Final = 3`'s type is inferred).
_QUALIFIERS: Final = frozenset({"ClassVar", "Final"})
_ANNOTATED: Final = "Annotated"
# Types whose every narrower type is known: nothing outside this list subclasses one as far as the
# rules are concerned (a `bool` is the one narrower builtin, and the hierarchy knows it).
_CLOSED: Final = frozenset({"None", "bool", "bytearray", "bytes", "complex", "float", "int", "str"})
# Builtin generics, compared by the container alone: a display's element types follow its context
# (`flags: tuple[str, ...] = ("-q",)`, `rows: list[Base] = [child]`), so they decide nothing.
_CLOSED_GENERICS: Final = frozenset({"dict", "frozenset", "list", "set", "tuple", "type"})


class Kind(StrEnum):
    """What a `Finding` says, as the code that reports it."""

    NARROWABLE = "LVA008"  # every value fits a strictly narrower type than the declared one
    CONFLICT = "LVA009"  # a value doesn't fit the declared type
    UNUSED_MEMBER = "LVA010"  # a declared union member no value uses


@dataclass(frozen=True, order=True)
class Finding:
    """One value-flow result; `col` is 0-based, `detail` is the type it's about, as text."""

    line: int
    col: int
    name: str
    kind: Kind
    detail: str
    # LVA008's and LVA010's: the annotation it could be instead, and where the declared one is on
    # its line (start and end columns; `None` where it isn't all on the name's line).
    rewrite: str = field(default="", compare=False)
    span: tuple[int, int] | None = field(default=None, compare=False)


@dataclass(frozen=True)
class Binding:
    """One binding of a name: where, and its value's type as text (`None`: unknown).

    `guess`: when the type isn't certain, `--fix`'s guess at it, and what that rests on (`FIX_KINDS`).
    Value flow never compares a guess; `--fix` offers `T | None` from one, as a guess too.
    """

    at: tuple[int, int]
    value: str | None
    guess: tuple[str, frozenset[str]] | None = field(default=None, compare=False)


@dataclass
class Lifetime:
    """Every binding of one name in one scope, and its declared type (its first annotation)."""

    declared: str | None = None
    declared_at: tuple[int, int] = (0, 0)
    declared_span: tuple[int, int] | None = None  # the annotation's columns, if it's all on one line
    bindings: list[Binding] = field(default_factory=list[Binding])
    escaped: bool = False  # written somewhere this scope can't see (`global`, `nonlocal`, ...)

    def declare(self, annotation: str, at: tuple[int, int], span: tuple[int, int] | None = None) -> None:
        """Record an annotation, and its columns if it's all on the name's line; only the first counts."""
        if self.declared is None:
            self.declared = annotation
            self.declared_at = at
            self.declared_span = span

    def bind(
        self,
        at: tuple[int, int],
        value: str | None,
        guess: tuple[str, frozenset[str]] | None = None,
    ) -> None:
        """Record a binding, with its value's type if known (or `--fix`'s guess at it, if not)."""
        self.bindings.append(Binding(at, value, guess))


class Hierarchy:
    """Which named types are narrower than which; see the module docstring."""

    def __init__(self, parents: Mapping[str, Iterable[str]], classes: Iterable[str] = ()) -> None:
        """Take each named type's directly wider types (`DEFAULT_PARENTS`' shape).

        `classes` are the other types whose whole ancestry `parents` holds (see `closed`).
        """
        self.parents: dict[str, frozenset[str]] = {name: frozenset(wider) for name, wider in parents.items()}
        self.classes: frozenset[str] = frozenset(classes)

    @classmethod
    def for_module(cls, tree: ast.Module, narrower: Parents | None = None) -> "Hierarchy":
        """Build the default hierarchy, plus each class the module defines under the bases it names.

        A project's own `narrower` entries (each type's wider types) replace whatever the defaults
        or the module say for that type (`int = []` stops `int` fitting `float`); every type they
        name counts as `closed`, since the project vouches for its ancestry.

        Returns:
          The hierarchy.

        """
        own: Parents = narrower or {}
        parents: dict[str, frozenset[str]] = dict(DEFAULT_PARENTS)
        defined: dict[str, list[ast.expr]] = {}
        node: ast.AST
        bases: frozenset[str]
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                defined[node.name] = node.bases
                if bases := frozenset(b.id for b in node.bases if isinstance(b, ast.Name)):
                    parents[node.name] = bases
        parents.update(own)
        vouched: frozenset[str] = frozenset(own).union(*own.values())
        return cls(parents, vouched | {name for name in defined if _visible(name, defined, frozenset())})

    def wider(self, atom: str) -> frozenset[str]:
        """Find every type `atom` is narrower than, directly or not.

        Returns:
          Them, not including `atom` itself.

        """
        return self._wider(atom, frozenset({atom}))

    def _wider(self, atom: str, seen: frozenset[str]) -> frozenset[str]:
        """Find the types `atom` is narrower than that aren't in `seen` (which a cycle leads back to).

        Returns:
          Them.

        """
        direct: frozenset[str] = self.parents.get(atom, frozenset()) - seen
        return direct.union(*(self._wider(parent, seen | direct) for parent in direct))

    def closed(self, atom: str) -> bool:
        """Check whether every type narrower than `atom`, and every wider one, is known.

        A builtin scalar, a builtin generic (by its text), or a class the module defines whose bases
        are all such classes; not an imported class (its bases, and subclasses, are out of sight), a
        protocol's structural matches, or an alias. Only a closed type's mismatch is certain.

        Returns:
          Whether it's closed.

        """
        return atom in _CLOSED or atom in self.classes or _container(atom) in _CLOSED_GENERICS

    def fits(self, atom: str, other: str) -> bool:
        """Check whether a value of type `atom` fits `other`.

        Returns:
          Whether they're the same type, or `atom` is narrower.

        """
        return (
            atom == other
            or other in _ANYTHING
            or other in self.wider(atom)
            or (_container(atom) in _CLOSED_GENERICS and _container(atom) == _container(other))
        )

    def fits_all(self, value: frozenset[str], declared: frozenset[str]) -> bool:
        """Check whether a value of the union `value` fits the union `declared`.

        Returns:
          Whether every member of `value` fits some member of `declared`.

        """
        return all(any(self.fits(atom, member) for member in declared) for atom in value)

    def simplified(self, atoms: Iterable[str]) -> frozenset[str]:
        """Drop every member of a union that's narrower than another member of it.

        Returns:
          The union's widest members: `int | bool | str` is `int | str`.

        """
        pool: frozenset[str] = frozenset(atoms)
        return frozenset(a for a in pool if not any(self.fits(a, b) and not self.fits(b, a) for b in pool))


def parse_narrower(text: str) -> tuple[Narrower, ...]:
    """Read a type hierarchy as the plugins' option takes it: `B=A, C=A, C=D, int=`.

    Each `narrower=wider` entry adds a wider type; `narrower=` alone says it has none.

    Returns:
      Each narrower type and its wider types, in the order first named.

    """
    parents: dict[str, list[str]] = {}
    entry: str
    narrower: str
    wider: str
    for entry in text.replace(",", " ").split():
        narrower, _, wider = entry.partition("=")
        parents.setdefault(narrower, []).extend([wider] if wider else [])
    return tuple((name, tuple(wider)) for name, wider in parents.items())


def _container(atom: str) -> str:
    """Name a generic's container (`list` for `list[int]`), or return a plain type as it is.

    Returns:
      The name.

    """
    return atom.partition("[")[0]


def _visible(name: str, defined: Mapping[str, list[ast.expr]], seen: frozenset[str]) -> bool:
    """Check whether a module class's whole ancestry is in the module (or `object`).

    Returns:
      Whether each base is a plain name of `object` or of such a class; `seen` ends a cycle.

    """
    return name not in seen and all(
        isinstance(base, ast.Name)
        and (base.id == _OBJECT or (base.id in defined and _visible(base.id, defined, seen | {name})))
        for base in defined[name]
    )


def members(annotation: str) -> frozenset[str] | None:
    """Split an annotation into its union's members, normalised as text.

    `X | Y`, `Optional[X]` and `Union[X, Y]` all split; `None` is `"None"`; `typing`'s capitalised
    aliases (`List[int]`) read as the builtins (`list[int]`); a string annotation is parsed first;
    `ClassVar[X]`, `Final[X]` and `Annotated[X, ...]` are `X`'s.

    Returns:
      The members, or `None` if the annotation can't be read (or is a bare `Final` or `ClassVar`).

    """
    try:
        root: ast.expr | None = _unwrapped(ast.parse(annotation, mode="eval").body)
    except SyntaxError:
        return None
    return None if root is None else _members(root)


def _unwrapped(node: ast.expr) -> ast.expr | None:
    """Strip the qualifiers around an annotation's type.

    Returns:
      The type, or `None` for a bare qualifier, which names none.

    """
    head: ast.expr
    inner: ast.expr
    match node:
        case ast.Subscript(value=head, slice=inner) if _head(head) in _QUALIFIERS:
            return _unwrapped(inner)
        case ast.Subscript(value=head, slice=ast.Tuple(elts=[inner, *_])) if _head(head) == _ANNOTATED:
            return _unwrapped(inner)
        case _ if _head(node) in _QUALIFIERS:
            return None
        case _:
            return node


def _members(node: ast.expr) -> frozenset[str] | None:
    left: ast.expr
    right: ast.expr
    head: ast.expr
    inner: ast.expr
    parts: list[ast.expr]
    text: str
    match node:
        case ast.BinOp(left=left, op=ast.BitOr(), right=right):
            return _union(_members(left), _members(right))
        case ast.Subscript(value=head, slice=inner) if _head(head) == _OPTIONAL:
            return _union(_members(inner), frozenset({_NONE}))
        case ast.Subscript(value=head, slice=inner) if _head(head) == _UNION:
            parts = inner.elts if isinstance(inner, ast.Tuple) else [inner]
            found: frozenset[str] | None = frozenset()
            for inner in parts:
                found = _union(found, _members(inner))
            return found
        case ast.Constant(value=None):
            return frozenset({_NONE})
        case ast.Constant(value=str() as text):
            return members(text)
        case _:
            return frozenset({_atom(node)})


def _union(left: frozenset[str] | None, right: frozenset[str] | None) -> frozenset[str] | None:
    return None if left is None or right is None else left | right


def _head(node: ast.expr) -> str:
    """Name a subscript's head, as `typing`'s name for it if it's one (`typing.Optional`, `Optional`).

    Returns:
      Its name, or `""` if it's neither a name nor a `typing` attribute.

    """
    name: str
    module: str
    match node:
        case ast.Name(id=name):
            return name
        case ast.Attribute(value=ast.Name(id=module), attr=name) if module in _TYPING_MODULES:
            return name
        case _:
            return ""


def _atom(node: ast.expr) -> str:
    """Normalise one union member as text: a `typing` alias reads as its builtin.

    Returns:
      The text.

    """
    inner: ast.expr
    head: ast.expr
    match node:
        case ast.Subscript(value=head, slice=inner) if _head(head) in _ALIASES:
            return ast.unparse(ast.Subscript(ast.Name(_ALIASES[_head(head)]), inner))
        case _ if _head(node) in _ALIASES:
            return _ALIASES[_head(node)]
        case ast.Attribute() if _head(node):
            return _head(node)
        case _:
            return ast.unparse(node)


def augmented(op: ast.operator, operand: str | None) -> str | None:
    """Infer the type an augmented assignment (`x op= operand`) can bind, besides `x`'s own.

    `/` gives a `float` for real numbers (a `complex` for one); `+`, `-`, `*`, `//` and `%` give a
    type both sides fit in, which the operand's own type stands for, since `x`'s is already among
    its values. Any other operator (`**` can turn an `int` into a `float`; bit operators, `@`, ...)
    is unknown.

    Returns:
      The type as text, or `None` if unknown.

    """
    match op:
        case ast.Div():
            if operand == _COMPLEX:
                return operand
            return "float" if operand in DEFAULT_PARENTS else None
        case ast.Add() | ast.Sub() | ast.Mult() | ast.FloorDiv() | ast.Mod():
            return operand
        case _:
            return None


def findings(name: str, lifetime: Lifetime, hierarchy: Hierarchy) -> list[Finding]:
    """Compare every value `name` is bound to with its declared type.

    Only types whose whole ancestry is known (`Hierarchy.closed`) are compared: an imported class
    may be a subclass of anything, so neither its values nor its annotation decide a finding.

    Returns:
      A `CONFLICT` for each value that doesn't fit; else, only if every value is known and nothing
      outside the scope writes it, an `UNUSED_MEMBER` for each declared union member no value fits
      and a `NARROWABLE` if every value fits a strictly narrower type than what's left.

    """
    declared: frozenset[str] | None = members(lifetime.declared) if lifetime.declared else None
    if not declared or declared & _ANYTHING:
        return []
    found: list[Finding] = []
    values: list[frozenset[str]] = []
    binding: Binding
    value: frozenset[str] | None
    certain: bool = all(hierarchy.closed(member) for member in declared)
    for binding in lifetime.bindings:
        if (value := members(binding.value) if binding.value else None) is None:
            continue
        values.append(value)
        if (
            certain
            and all(hierarchy.closed(atom) for atom in value)
            and not hierarchy.fits_all(value, declared)
        ):
            found.append(Finding(*binding.at, name, Kind.CONFLICT, binding.value or ""))
    # Every value known, nothing outside the scope writes the name, and every type compared closed.
    complete: bool = bool(values) and len(values) == len(lifetime.bindings) and not lifetime.escaped
    if found or not complete or not certain or not all(hierarchy.closed(a) for v in values for a in v):
        return found
    return found + _narrowing(
        name,
        lifetime,
        declared,
        frozenset[str]().union(*values),
        hierarchy,
    )


def _narrowing(
    name: str,
    lifetime: Lifetime,
    declared: frozenset[str],
    values: frozenset[str],
    hierarchy: Hierarchy,
) -> list[Finding]:
    """Find the declared union members no value uses, then whether what's left could narrow.

    Returns:
      The `UNUSED_MEMBER` and `NARROWABLE` findings.

    """
    at: tuple[int, int] = lifetime.declared_at
    span: tuple[int, int] | None = lifetime.declared_span
    used: frozenset[str] = frozenset(m for m in declared if any(hierarchy.fits(v, m) for v in values))
    found: list[Finding] = [
        Finding(*at, name, Kind.UNUSED_MEMBER, member, _render(used), span)
        for member in sorted(declared - used)
    ]
    narrowest: frozenset[str] = hierarchy.simplified(values)
    if not hierarchy.fits_all(used, narrowest):  # every value fits `used`: no `CONFLICT` got here
        rendered: str = _render(narrowest)
        found.append(Finding(*at, name, Kind.NARROWABLE, rendered, rendered, span))
    return found


def _render(atoms: frozenset[str]) -> str:
    """Write a union as annotation text: its members sorted, `None` last.

    Returns:
      The text.

    """
    return " | ".join(sorted(atoms, key=lambda atom: (atom == _NONE, atom)))
