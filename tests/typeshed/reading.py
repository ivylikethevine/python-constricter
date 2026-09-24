# SPDX-License-Identifier: MIT
"""Types read from typeshed's standard-library stubs, as one configuration sees them (see `Reading`).

What `stdlib_tables` builds its tables from: an annotation as a `Form` (a builtin annotation, a
class, or `AnyStr`), a function's return, a class's members in its method resolution order.
"""

import ast
import re
from collections.abc import Iterable, Sequence
from typing import Final, NamedTuple, TypeAlias

from constricter.offences import MAX_LENGTH, NESTING
from constricter.rules.annotations import depth, is_vague
from tests.typeshed.stubs import (
    Alias,
    Binding,
    Config,
    Found,
    Function,
    Klass,
    ModuleRef,
    Stubs,
    TypeVariable,
    Variable,
    decorator_name,
    private,
)

# Their classes, called, may build a class (`Enum("Color", "RED")`), not an instance.
_NO_CONSTRUCTORS: Final = frozenset({"enum"})
_DECORATORS: Final = frozenset(
    {"overload", "deprecated", "final", "abstractmethod", "classmethod", "staticmethod", "override"},
)
_PROPERTIES: Final = frozenset({"property", "cached_property"})
_CLASS_SIDE: Final = frozenset({"classmethod", "staticmethod"})
ATTRIBUTE: Final = "attribute"
CLASSMETHOD: Final = "classmethod"
_METHOD: Final = "method"
_BUILTINS: Final = "builtins"
_TUPLE: Final = "tuple"
_STR: Final = "str"
_BYTES: Final = "bytes"
_NONE: Final = "None"
_NEW: Final = "__new__"
_CLASS_GETITEM: Final = "__class_getitem__"
_TYPING: Final = frozenset({"typing", "typing_extensions"})
# Builtins spelled as themselves; `object` and `type` are vague, `function` and `ellipsis` internal.
_BUILTIN_SKIPPED: Final = frozenset({"object", "type", "function", "ellipsis"})
# The builtin containers, however spelled, and how many type parameters each takes (`None`: any).
_GENERICS: Final = {"list": "list", "set": "set", "frozenset": "frozenset", "dict": "dict", _TUPLE: _TUPLE}
TYPING_GENERICS: Final = {
    "List": "list",
    "Set": "set",
    "FrozenSet": "frozenset",
    "Dict": "dict",
    "Tuple": _TUPLE,
}
ARITY: Final = {"list": 1, "set": 1, "frozenset": 1, "dict": 2}
_WRAPPERS: Final = frozenset({"ClassVar", "Final"})  # `typing`'s, around an attribute's type
_GUARDS: Final = frozenset({"TypeGuard", "TypeIs"})  # a function returning one returns a `bool`
_SPECIAL_BASES: Final = frozenset({"Generic", "Protocol"})  # bases that add nothing to an instance
_PROTOCOL: Final = "Protocol"
_LITERAL: Final = "Literal"
_OPTIONAL: Final = "Optional"
_UNIONS: Final = frozenset({_OPTIONAL, "Union"})
_TYPED_DICT: Final = "TypedDict"
_TEXT_WORDS: Final = re.compile(r"[A-Za-z_]+")
_EITHER: Final = frozenset({"AnyStr", "Any", "object", "Incomplete"})  # a parameter taking both
_BUFFER: Final = "buffer"  # a `bytes` overload's parameter may take any buffer
_SEQUENCE: Final = 2  # `tuple[T, ...]`'s two parts
_MAX_DEPTH: Final = 20  # aliases followed before giving up


class Text(NamedTuple):
    """An annotation spelled with builtins alone (`int`, `list[str]`, `str | None`)."""

    text: str


class ClassRef(NamedTuple):
    """A class, by the module that defines it and its name there."""

    module: str
    name: str


class Special(NamedTuple):
    """`AnyStr`: whichever of `str` and `bytes` the arguments are."""


ANY_STR: Final = Special()
Form: TypeAlias = Text | ClassRef | Special
_TEXTS: Final[frozenset[Form | None]] = frozenset({Text(_STR), Text(_BYTES)})
_STR_ONLY: Final[frozenset[Form | None]] = frozenset({Text(_STR)})
_SELF: Final = "Self"
# `typing`'s names an annotation may use: a `LiteralString` is a `str`; `Self` is the class it's on.
_TYPING_FORMS: Final[dict[str, Form | None]] = {"LiteralString": Text(_STR), "AnyStr": ANY_STR, _SELF: None}
Table: TypeAlias = dict[str, str]  # each entry's annotation, or a class's dotted path, by name
Defs: TypeAlias = Sequence[ast.FunctionDef | ast.AsyncFunctionDef]  # a function's overloads


class Member(NamedTuple):
    """A class's member: what it is (`method`, `classmethod`, `attribute`), its form, its class's module."""

    kind: str
    form: Form
    module: str


def _typing(found: Found, *names: str) -> bool:
    """Check whether a name is one of `typing`'s (or `typing_extensions`'), one of `names`.

    Returns:
      Whether it is.

    """
    return found.module in _TYPING and found.name in names


class Reading:
    """Types read from the stubs for one configuration."""

    def __init__(self, stubs: Stubs, config: Config) -> None:
        """Read `stubs` as `config` sees them."""
        self.stubs: Stubs = stubs
        self.config: Config = config
        self._generic: dict[ClassRef, bool] = {}
        self._mro: dict[ClassRef, list[ClassRef] | None] = {}

    def ref(self, expr: ast.AST, module: str) -> Found | None:
        """Resolve a name or dotted name as `module` spells it (a builtin, if it binds no such name).

        Returns:
          What it names, or `None`.

        """
        name: str
        value: ast.expr
        found: Found | None = None
        match expr:
            case ast.Name(id=name):
                found = self.stubs.lookup(module, name, self.config) or self.stubs.lookup(
                    _BUILTINS,
                    name,
                    self.config,
                )
            case ast.Attribute(value=value, attr=name):
                base: Found | None = self.ref(value, module)
                if base is not None and isinstance(base.binding, ModuleRef):
                    found = self.stubs.lookup(base.binding.module, name, self.config)
            case _:
                pass
        return found

    def form(self, expr: ast.expr, module: str, owner: ClassRef | None, hops: int = 0) -> Form | None:
        """Read an annotation in `module` as a `Form`; `Self` is `owner`.

        Returns:
          The form, or `None` if it isn't one the tables can hold.

        """
        text: str
        left: ast.expr
        right: ast.expr
        base: ast.expr
        index: ast.expr
        found: Form | None = None
        match expr:
            case _ if hops > _MAX_DEPTH:
                pass
            case ast.Constant(value=None):
                found = Text(_NONE)
            case ast.Constant(value=str() as text):
                found = self._forward(text, module, owner, hops)
            case ast.BinOp(left=left, op=ast.BitOr(), right=right):
                found = _union([self.form(side, module, owner, hops + 1) for side in (left, right)])
            case ast.Subscript(value=base, slice=index):
                found = self._subscript(base, index, module, owner, hops)
            case ast.Name() | ast.Attribute():
                target: Found | None = self.ref(expr, module)
                found = None if target is None else self._named(target, owner, hops)
            case _:
                pass
        return found

    def _forward(self, text: str, module: str, owner: ClassRef | None, hops: int) -> Form | None:
        """Read a string annotation (a forward reference) as the annotation it holds.

        Returns:
          Its form, or `None`.

        """
        try:
            parsed: ast.expr = ast.parse(text, mode="eval").body
        except SyntaxError:
            return None
        return self.form(parsed, module, owner, hops + 1)

    def _named(self, found: Found, owner: ClassRef | None, hops: int) -> Form | None:
        """Read a name an annotation uses: a class, an alias, `Self`, `LiteralString`, `AnyStr`.

        Returns:
          Its form, or `None`.

        """
        value: ast.expr
        constraints: tuple[ast.expr, ...]
        if found.module in _TYPING and found.name in _TYPING_FORMS:
            return owner if found.name == _SELF else _TYPING_FORMS[found.name]
        match found.binding:
            case TypeVariable(constraints=constraints):
                return _constrained([self.form(c, found.module, owner, hops + 1) for c in constraints])
            case Klass():
                return self._class(ClassRef(found.module, found.name))
            case Alias(value=value):
                return self.form(value, found.module, owner, hops + 1)
            case _:
                return None

    def _class(self, klass: ClassRef) -> Form | None:
        """Read a class as a form: a builtin by its name, any other by where it's defined; not a generic.

        Returns:
          Its form, or `None`.

        """
        if self.generic(klass):
            return None
        if klass.module != _BUILTINS:
            return klass
        return None if klass.name in _BUILTIN_SKIPPED or private(klass.name) else Text(klass.name)

    def _subscript(
        self,
        base: ast.expr,
        index: ast.expr,
        module: str,
        owner: ClassRef | None,
        hops: int,
    ) -> Form | None:
        """Read a subscripted annotation: a builtin container of builtins, or one of `typing`'s forms.

        Returns:
          Its form, or `None`.

        """
        found: Found | None
        if (found := self.ref(base, module)) is None:
            return None
        args: list[ast.expr] = list(index.elts) if isinstance(index, ast.Tuple) else [index]
        if found.module in _TYPING and found.name not in TYPING_GENERICS:
            return self._special(found.name, args, module, owner, hops)
        name: str | None = (TYPING_GENERICS if found.module in _TYPING else _GENERICS).get(found.name)
        if name is None or (found.module != _BUILTINS and found.module not in _TYPING):
            return None
        if name == _TUPLE and len(args) == _SEQUENCE and _is_ellipsis(args[1]):
            element: Form | None = self.form(args[0], module, owner, hops + 1)
            return Text(f"tuple[{element.text}, ...]") if isinstance(element, Text) else None
        parts: list[Form | None] = [self.form(arg, module, owner, hops + 1) for arg in args]
        texts: list[str] = [part.text for part in parts if isinstance(part, Text)]
        if not texts or len(texts) != len(parts) or ARITY.get(name, len(parts)) != len(parts):
            return None
        return Text(f"{name}[{', '.join(texts)}]")

    def _special(
        self,
        name: str,
        args: list[ast.expr],
        module: str,
        owner: ClassRef | None,
        hops: int,
    ) -> Form | None:
        """Read one of `typing`'s subscripted forms: `Optional`, `Union`, `Literal`, a guard, a wrapper.

        Returns:
          Its form, or `None`.

        """
        parts: list[Form | None] = [self.form(arg, module, owner, hops + 1) for arg in args]
        if name in _GUARDS:
            return Text("bool")
        if name == _LITERAL:
            return _union([_literal(arg) for arg in args])
        if name == _OPTIONAL:
            parts.append(Text(_NONE))
        if name in _UNIONS or (name in _WRAPPERS and len(parts) == 1):
            return _union(parts)
        return None

    def generic(self, klass: ClassRef) -> bool:
        """Check whether a class takes type parameters, through a base's (`Base[T]`, `Generic[T]`).

        Returns:
          Whether it does (or isn't a class here).

        """
        if klass not in self._generic:
            node: ast.ClassDef | None = self.class_node(klass)
            self._generic[klass] = node is None or any(
                self._type_variable(inner, klass.module)
                for base in node.bases
                for sub in ast.walk(base)
                if isinstance(sub, ast.Subscript)
                for inner in ast.walk(sub.slice)
            )
        return self._generic[klass]

    def _type_variable(self, node: ast.AST, module: str) -> bool:
        found: Found | None = self.ref(node, module)
        return found is not None and isinstance(found.binding, TypeVariable)

    def class_node(self, klass: ClassRef) -> ast.ClassDef | None:
        """Find a class's definition.

        Returns:
          It, or `None` if it isn't a class here.

        """
        found: Found | None = self.stubs.lookup(klass.module, klass.name, self.config)
        return found.binding.node if found is not None and isinstance(found.binding, Klass) else None

    def mro(self, klass: ClassRef) -> list[ClassRef] | None:
        """Work out a class's method resolution order (C3), `object` left out.

        Returns:
          It, or `None` if any base anywhere above it can't be followed.

        """
        if klass not in self._mro:
            self._mro[klass] = None  # a cycle can't be followed
            bases: list[ClassRef] | None = self._bases(klass)
            lines: list[list[ClassRef] | None] = [] if bases is None else [self.mro(base) for base in bases]
            known: list[list[ClassRef]] = [line for line in lines if line is not None]
            if bases is not None and len(known) == len(lines):
                self._mro[klass] = _c3(klass, [*known, bases])
        return self._mro[klass]

    def trusted(self, klass: ClassRef) -> tuple[list[ClassRef], bool]:
        """Find the classes whose members a class certainly has, in order, where a base can't be followed.

        Its whole method resolution order if it can be worked out; else it and, with a single base,
        that base's own trusted classes (single inheritance keeps their order), else just it.

        Returns:
          Those classes, and whether they're its whole order.

        """
        whole: list[ClassRef] | None
        if (whole := self.mro(klass)) is not None:
            return whole, True
        bases: list[ClassRef] | None = self._bases(klass)
        if bases is not None and len(bases) == 1:
            return [klass, *self.trusted(bases[0])[0]], False
        return [klass], False

    def _bases(self, klass: ClassRef) -> list[ClassRef] | None:
        """List a class's bases, `object`, `Generic` and `Protocol` left out; a generic base by its class.

        Returns:
          Them, or `None` if one isn't a plain class here (a `TypedDict`, a special form).

        """
        node: ast.ClassDef | None
        if (node := self.class_node(klass)) is None:
            return None
        found: list[ClassRef] = []
        base: ast.expr
        for base in node.bases:
            # A generic base is still a class in the order; its members naming its type parameters
            # aren't read (they aren't forms the tables hold).
            target: Found | None = self.ref(
                base.value if isinstance(base, ast.Subscript) else base,
                klass.module,
            )
            if target is None or _typing(target, _TYPED_DICT):
                return None
            if _typing(target, *_SPECIAL_BASES) or (target.module, target.name) == (_BUILTINS, "object"):
                continue
            if not isinstance(target.binding, Klass):
                return None
            found.append(ClassRef(target.module, target.name))
        return found

    def is_protocol(self, node: ast.ClassDef, module: str) -> bool:
        """Check whether a class is a protocol (`Protocol` among its own bases), which can't be instantiated.

        Returns:
          Whether it is.

        """
        targets: list[Found | None] = [
            self.ref(base.value if isinstance(base, ast.Subscript) else base, module) for base in node.bases
        ]
        return any(target is not None and _typing(target, _PROTOCOL) for target in targets)

    def typed_dict(self, klass: ClassRef) -> bool:
        """Check whether a class is a `TypedDict`, whose body declares keys, not attributes.

        Returns:
          Whether it is (directly or through a base).

        """
        node: ast.ClassDef | None
        if (node := self.class_node(klass)) is None:
            return False
        targets: list[Found | None] = [self.ref(base, klass.module) for base in node.bases]
        return any(
            target is not None
            and (
                _typing(target, _TYPED_DICT)
                or (
                    isinstance(target.binding, Klass)
                    and self.typed_dict(ClassRef(target.module, target.name))
                )
            )
            for target in targets
        )

    def bound_method(self, value: ast.expr, module: str) -> Form | None:
        """Read a module-level alias of a method bound to a module-level instance (`random = _inst.random`).

        Returns:
          What the method returns, or `None` if `value` isn't such a method.

        """
        instance: str
        name: str
        match value:
            case ast.Attribute(value=ast.Name(id=instance), attr=name):
                pass
            case _:
                return None
        found: Found | None = self.stubs.lookup(module, instance, self.config)
        klass: Form | None = (
            self.form(found.binding.annotation, found.module, None)
            if found is not None and isinstance(found.binding, Variable)
            else None
        )
        member: Member | None = self.members(klass).get(name) if isinstance(klass, ClassRef) else None
        return member.form if member is not None and member.kind != ATTRIBUTE else None

    def returns(self, defs: Defs, module: str, owner: ClassRef | None) -> Form | None:
        """Read what a function (each of its overloads) returns.

        Returns:
          The form every overload agrees on, `ANY_STR` for `str`/`bytes` overloads, or `None`.

        """
        if any(not readable(node) for node in defs):
            return None
        forms: list[Form | None] = [
            None if node.returns is None else self.form(node.returns, module, owner) for node in defs
        ]
        if owner is None and _any_str_overloads(defs, forms):
            return ANY_STR
        first: Form | None = forms[0]
        if first is None or any(form != first for form in forms):
            return None
        return None if first == ANY_STR and not _mentions(defs, "AnyStr") else first

    def members(self, klass: ClassRef) -> dict[str, Member]:
        """Read a class's public members, inherited ones included, as the class resolves them.

        Returns:
          Each member, by name.

        """
        found: dict[str, Member] = {}
        if self.typed_dict(klass):
            return found
        seen: set[str] = set()
        owner: ClassRef
        for owner in self.trusted(klass)[0]:
            name: str
            binding: Binding
            member: Member | None
            for name, binding in self.body(owner).items():
                if name not in seen and not private(name) and (member := self._member(binding, owner, klass)):
                    found[name] = member
                seen.add(name)
        return found

    def functions(self, klass: ClassRef) -> dict[str, tuple[Function, ClassRef]]:
        """Read a class's public methods as `members` resolves them, each with the class defining it.

        Returns:
          Each one, by name: its overloads, and where they are.

        """
        found: dict[str, tuple[Function, ClassRef]] = {}
        if self.typed_dict(klass):
            return found
        seen: set[str] = set()
        owner: ClassRef
        for owner in self.trusted(klass)[0]:
            name: str
            binding: Binding
            for name, binding in self.body(owner).items():
                if name not in seen and not private(name) and isinstance(binding, Function):
                    found[name] = (binding, owner)
                seen.add(name)
        return found

    def body(self, klass: ClassRef) -> dict[str, Binding]:
        """Read what a class's own body binds.

        Returns:
          Each binding, by name (none if it isn't a class here).

        """
        node: ast.ClassDef | None = self.class_node(klass)
        return {} if node is None else self.stubs.class_namespace(klass.module, node, self.config).names

    def _member(self, binding: Binding, owner: ClassRef, klass: ClassRef) -> Member | None:
        """Read one member of `owner` (as `klass` has it): a method's return, a property's, an attribute's.

        Returns:
          It, or `None`.

        """
        defs: tuple[ast.FunctionDef | ast.AsyncFunctionDef, ...]
        annotation: ast.expr
        kind: str = ATTRIBUTE
        form: Form | None = None
        match binding:
            case Function(defs=defs):
                names: set[str] = {decorator_name(d) for d in defs[0].decorator_list}
                kind = ATTRIBUTE if names & _PROPERTIES else CLASSMETHOD if names & _CLASS_SIDE else _METHOD
                form = self.returns(defs, owner.module, klass)
            case Variable(annotation=annotation):
                form = self.form(annotation, owner.module, klass)
            case _:
                pass
        return None if form is None or form == ANY_STR else Member(kind, form, owner.module)

    def subscriptable(self, klass: ClassRef) -> bool:
        """Check whether a generic class can be subscripted at run time, as a module's annotations are.

        One of `typing`'s (its `collections.abc` class), or one whose own order defines
        `__class_getitem__`: a `typing` base the stubs give it isn't one it has at run time.

        Returns:
          Whether it can.

        """
        return klass.module in _TYPING or any(
            _CLASS_GETITEM in self.body(owner)
            for owner in self.trusted(klass)[0]
            if owner.module not in _TYPING
        )

    def constructs(self, klass: ClassRef) -> bool:
        """Check whether calling a class certainly gives an instance of it (its `__new__` says nothing else).

        Returns:
          Whether it does.

        """
        node: ast.ClassDef | None = self.class_node(klass)
        if (
            node is None
            or klass.module.split(".")[0] in _NO_CONSTRUCTORS
            or self.is_protocol(node, klass.module)
        ):
            return False
        classes: list[ClassRef]
        whole: bool
        classes, whole = self.trusted(klass)
        new: Binding | None = next(
            (body[_NEW] for body in (self.body(owner) for owner in classes) if _NEW in body),
            None,
        )
        if isinstance(new, Function):
            return self.returns(new.defs, klass.module, klass) == klass
        return whole and new is None


def readable(node: ast.FunctionDef | ast.AsyncFunctionDef) -> bool:
    """Check a function is one the tables read: not async, annotated, only known decorators.

    Returns:
      Whether it is.

    """
    names: set[str] = {decorator_name(decorator) for decorator in node.decorator_list}
    return (
        isinstance(node, ast.FunctionDef) and node.returns is not None and names <= _DECORATORS | _PROPERTIES
    )


def _union(parts: Iterable[Form | None]) -> Form | None:
    """Join builtin annotations with `|`, each once, in order.

    Returns:
      The union, or `None` if a part isn't a builtin annotation.

    """
    texts: list[str] = []
    part: Form | None
    for part in parts:
        if not isinstance(part, Text):
            return None
        if part.text not in texts:
            texts.append(part.text)
    return Text(" | ".join(texts)) if texts else None


def _constrained(forms: list[Form | None]) -> Form | None:
    """Read a constrained `TypeVar` whose constraints are text: `str` (`LiteralString` too), or `AnyStr`'s.

    Returns:
      `str`, `ANY_STR`, or `None` for any other constraints (or none).

    """
    kinds: frozenset[Form | None]
    if (kinds := frozenset(forms)) == _STR_ONLY:
        return Text(_STR)
    return ANY_STR if kinds == _TEXTS else None


def _literal(value: ast.expr) -> Form | None:
    """Widen one `Literal[...]` value to its type (`"a"` to `str`, `None` to `None`).

    Returns:
      Its form, or `None` for anything but a builtin constant.

    """
    constant: bool | int | str | bytes | None
    match value:
        case ast.Constant(value=bool() | int() | str() | bytes() | None as constant):
            return Text(_NONE if constant is None else type(constant).__name__)
        case _:
            return None


def _is_ellipsis(node: ast.expr) -> bool:
    return isinstance(node, ast.Constant) and node.value is Ellipsis


def _mentions(defs: Defs, word: str) -> bool:
    """Check whether any parameter annotation of any overload names `word`.

    Returns:
      Whether one does.

    """
    return any(
        word in _TEXT_WORDS.findall(ast.unparse(arg.annotation))
        for node in defs
        for arg in (*node.args.posonlyargs, *node.args.args, *node.args.kwonlyargs)
        if arg.annotation is not None
    )


def _any_str_overloads(defs: Defs, forms: list[Form | None]) -> bool:
    """Check for overloads that each take and return only `str`, or only `bytes`, with both there.

    Only their required positional parameters are looked at: a call whose arguments are all `str`
    can't match a `bytes` one, and the other way round.

    Returns:
      Whether they're such overloads.

    """
    if frozenset(forms) != _TEXTS:
        return False
    node: ast.FunctionDef | ast.AsyncFunctionDef
    form: Form | None
    for node, form in zip(defs, forms, strict=True):
        positional: list[ast.arg] = [*node.args.posonlyargs, *node.args.args]
        required: list[ast.arg] = positional[: len(positional) - len(node.args.defaults)]
        if not required or not all(
            _takes_only(arg, _BYTES if form == Text(_STR) else _STR) for arg in required
        ):
            return False
    return True


def _takes_only(arg: ast.arg, other: str) -> bool:
    """Check that a parameter doesn't take `other` (`str` or `bytes`), by the words of its annotation.

    Returns:
      Whether it doesn't (and is annotated).

    """
    words: list[str] = [] if arg.annotation is None else _TEXT_WORDS.findall(ast.unparse(arg.annotation))
    taking: bool = any(
        other in word.lower() or word in _EITHER or (other == _BYTES and _BUFFER in word.lower())
        for word in words
    )
    return bool(words) and not taking


def _c3(klass: ClassRef, lines: list[list[ClassRef]]) -> list[ClassRef] | None:
    """Merge the bases' method resolution orders (and the bases, last) by C3, as Python does.

    Returns:
      `klass`'s order, or `None` if there's none (Python would refuse the class).

    """
    merged: list[ClassRef] = [klass]
    pending: list[list[ClassRef]] = [line for line in lines if line]
    for _ in range(sum(len(line) for line in pending)):  # each round takes one class off
        if not pending:
            break
        head: ClassRef | None = next(
            (line[0] for line in pending if not any(line[0] in other[1:] for other in pending)),
            None,
        )
        if head is None:
            return None
        merged.append(head)
        pending = [rest for rest in ([c for c in line if c != head] for line in pending) if rest]
    return merged


def substituted(template: str, names: dict[str, str]) -> str:
    """Replace names in a template: a class's type parameters by what a subclass passes them.

    Returns:
      The template.

    """
    return ast.unparse(_replaced(ast.parse(template, mode="eval").body, names))


def _replaced(node: ast.expr, names: dict[str, str]) -> ast.expr:
    """Replace names in a template's tree, in place (a template is names, subscripts, tuples, unions).

    Returns:
      The tree.

    """
    name: str
    match node:
        case ast.Name(id=name) if name in names:
            return ast.parse(names[name], mode="eval").body
        case ast.Subscript():
            node.value, node.slice = _replaced(node.value, names), _replaced(node.slice, names)
        case ast.Tuple():
            node.elts = [_replaced(element, names) for element in node.elts]
        case ast.BinOp():
            node.left, node.right = _replaced(node.left, names), _replaced(node.right, names)
        case _:
            pass
    return node


def usable(text: str) -> bool:
    """Check a builtin annotation is one `--fix` may write: not vague, nested or a long tuple, not `None`.

    Returns:
      Whether it is.

    """
    expr: ast.expr = ast.parse(text, mode="eval").body
    long: bool = any(
        isinstance(node, ast.Subscript)
        and isinstance(node.slice, ast.Tuple)
        and len(node.slice.elts) > MAX_LENGTH
        for node in ast.walk(expr)
    )
    return text != _NONE and not is_vague(expr) and depth(expr) < NESTING and not long
