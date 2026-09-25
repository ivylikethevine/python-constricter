# SPDX-License-Identifier: MIT
"""Standard-library annotations spelled as the tables' templates, and generic classes' type parameters.

A template names builtins as themselves, classes by their dotted paths (`re.Pattern[AnyStr]`) and
type variables by their bare names, which a call's arguments or an instance's type arguments bind.
"""

import ast
from collections.abc import Iterator, Sequence
from typing import Final

from constricter.fix.signatures import Constant
from tests.typeshed.reading import ARITY, TYPING_GENERICS, ClassRef, Reading, usable
from tests.typeshed.stubs import Alias, Found, Klass, TypeVariable

BUILTINS: Final = "builtins"
TYPING: Final = frozenset({"typing", "typing_extensions", "_typeshed"})
STR: Final = "str"
LITERAL_STRING: Final = "LiteralString"
NONE: Final = "None"
OBJECT: Final = "object"
OPTIONAL: Final = "Optional"
UNIONS: Final = frozenset({OPTIONAL, "Union"})
LITERAL: Final = "Literal"
_GUARDS: Final = frozenset({"TypeGuard", "TypeIs"})
_CONTAINERS: Final = frozenset({*ARITY, "tuple"})  # the builtin generics a return may use
MAX_DEPTH: Final = 20
_DECLARING: Final = frozenset({"Generic", "Protocol"})  # a base that lists a class's type parameters
_UNWRITTEN: Final = frozenset({OBJECT, "type", "function", "ellipsis"})  # vague, or internal


class Templates:
    """Annotations spelled as templates, as one configuration sees the stubs."""

    def __init__(self, reading: Reading, canonical: dict[ClassRef, str]) -> None:
        """Read with `reading`; `canonical`: every public class's path, generic ones too."""
        self.reading: Reading = reading
        self.canonical: dict[ClassRef, str] = canonical

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
                and found.module in TYPING
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
            case _ if hops > MAX_DEPTH:
                pass
            case ast.Constant(value=None):
                found = NONE
            case ast.Constant(value=str() as text):
                found = self._spelled(parsed(text), module, hops + 1)
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
        if found.module in TYPING and found.name == LITERAL_STRING:
            return STR
        match found.binding:
            case TypeVariable():
                return found.name
            case Alias(value=value):
                return self._spelled(value, found.module, hops + 1)
            case Klass():
                klass: ClassRef = ClassRef(found.module, found.name)
                if self.reading.generic(klass) or klass.name in _UNWRITTEN:
                    return None
                return klass.name if klass.module == BUILTINS else self.canonical.get(klass)
            case _:
                return None

    def _spelled_subscript(self, expr: ast.Subscript, module: str, hops: int) -> str | None:
        found: Found | None = self.reading.ref(expr.value, module)
        args: list[ast.expr] = list(expr.slice.elts) if isinstance(expr.slice, ast.Tuple) else [expr.slice]
        if found is None:
            return None
        typing_class: bool = isinstance(found.binding, Klass) and found.name not in TYPING_GENERICS
        if found.module in TYPING and found.name not in TYPING_GENERICS and not typing_class:
            return self._special(found.name, args, module, hops)
        # `typing`'s own generic classes (`Iterator`) by their public path (`collections.abc.Iterator`).
        base: str | None = (
            TYPING_GENERICS.get(found.name)
            if found.module in TYPING and not typing_class
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
        if name in UNIONS:
            return self._union([*args, *([ast.Constant(None)] if name == OPTIONAL else [])], module, hops)
        if name == LITERAL:
            constants: list[Constant] = literal_values(args)
            return _joined([type_name(value) for value in constants]) if len(constants) == len(args) else None
        return "bool" if name in _GUARDS else None

    def _generic_base(self, found: Found) -> str | None:
        """Spell a generic class subscripted in a return: a builtin container, or a class's dotted path.

        Returns:
          It, or `None`.

        """
        if not isinstance(found.binding, Klass):
            return None
        klass: ClassRef = ClassRef(found.module, found.name)
        if klass.module == BUILTINS:
            return klass.name if klass.name in _CONTAINERS else None
        return self.canonical.get(klass) if self.reading.generic(klass) else None


def parsed(text: str) -> ast.expr:
    """Parse a string annotation (a forward reference); one that doesn't parse is `...`, naming nothing.

    Returns:
      Its expression.

    """
    try:
        return ast.parse(text, mode="eval").body
    except SyntaxError:
        return ast.Constant(...)


def literal_values(nodes: Sequence[ast.expr]) -> list[Constant]:
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


def type_name(value: Constant) -> str:
    """Name a literal's type (`None`'s, `None`).

    Returns:
      It.

    """
    return NONE if value is None else type(value).__name__


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
