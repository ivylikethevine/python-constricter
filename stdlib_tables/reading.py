"""Types read from typeshed's standard-library stubs, as one configuration sees them (see `Reading`).

What `stdlib_tables` builds its tables from: an annotation as a `Form` (a builtin annotation, a
class, or `AnyStr`), a function's return, a class's members in its method resolution order.
"""

import ast
from typing import Final, NamedTuple, TypeAlias

from stdlib_tables.forms import (
    ANY_STR,
    NONE,
    STR,
    ClassRef,
    Defs,
    Form,
    Text,
    any_str_overloads,
    c3,
    constrained,
    literal,
    mentions,
    union,
)
from stdlib_tables.stubs import (
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
AWAITED: Final = "awaited"  # an `async def` method: its form is what awaiting its call gives
_AENTER: Final = "__aenter__"
_BUILTINS: Final = "builtins"
_TUPLE: Final = "tuple"
_NEW: Final = "__new__"
_DUNDER: Final = "__"  # a dunder's, or a mangled name's, start
_ENTER: Final = "__enter__"
_GET_ITEM: Final = "__getitem__"
# The methods binary operators call on their left operand, read with a class's methods whose
# arguments decide their return (not `members`: what the right operand is always matters).
_FORWARD: Final = ("add", "sub", "mul", "truediv", "floordiv", "mod", "and", "or", "xor")
# And their reflected twins, called on the right operand where the left's can't take it (`2 * span`).
OPERATORS: Final = frozenset({f"__{name}__" for name in _FORWARD} | {f"__r{name}__" for name in _FORWARD})
_CLASS_GETITEM: Final = "__class_getitem__"
_TYPING: Final = frozenset({"typing", "typing_extensions"})
# Builtins spelled as themselves; `object` and `type` are vague, `function` and `ellipsis` internal.
_BUILTIN_SKIPPED: Final = frozenset({"object", "type", "function", "ellipsis"})
_TYPE_OF: Final = "type"  # subscripted, a class as a value: `type[C]`
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
_SEQUENCE: Final = 2  # `tuple[T, ...]`'s two parts
_MAX_DEPTH: Final = 20  # aliases followed before giving up


_SELF: Final = "Self"
# `typing`'s names an annotation may use: a `LiteralString` is a `str`; `Self` is the class it's on.
ANY: Final = "Any"  # `typing.Any`, as a function's whole return (see `Reading.returns_any`)
_FUTURES: Final = frozenset({"Future", "Task"})  # what a coroutine isn't (see `Reading.future_bound`)
_TYPING_FORMS: Final[dict[str, Form | None]] = {"LiteralString": Text(STR), "AnyStr": ANY_STR, _SELF: None}
Table: TypeAlias = dict[str, str]  # each entry's annotation, or a class's dotted path, by name


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
        self._members: dict[ClassRef, dict[str, Member]] = {}

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
                found = Text(NONE)
            case ast.Constant(value=str() as text):
                found = self._forward(text, module, owner, hops)
            case ast.BinOp(left=left, op=ast.BitOr(), right=right):
                found = union([self.form(side, module, owner, hops + 1) for side in (left, right)])
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
                return constrained([self.form(c, found.module, owner, hops + 1) for c in constraints])
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
            # A class as a value (`failureException: type[BaseException]`): of a builtin class alone.
            typed: bool = found.module == _BUILTINS and found.name == _TYPE_OF and len(args) == 1
            return self._type_of(args[0], module, owner, hops) if typed else None
        if name == _TUPLE and len(args) == _SEQUENCE and _is_ellipsis(args[1]):
            element: Form | None = self.form(args[0], module, owner, hops + 1)
            return Text(f"tuple[{element.text}, ...]") if isinstance(element, Text) else None
        parts: list[Form | None] = [self.form(arg, module, owner, hops + 1) for arg in args]
        texts: list[str] = [part.text for part in parts if isinstance(part, Text)]
        if not texts or len(texts) != len(parts) or ARITY.get(name, len(parts)) != len(parts):
            return None
        return Text(f"{name}[{', '.join(texts)}]")

    def _type_of(self, arg: ast.expr, module: str, owner: ClassRef | None, hops: int) -> Form | None:
        """Read `type[C]`'s form: a text, where `C` is a builtin class.

        Returns:
          It, or `None`.

        """
        klass: Form | None = self.form(arg, module, owner, hops + 1)
        return (
            Text(f"{_TYPE_OF}[{klass.text}]")
            if isinstance(klass, Text) and klass.text.isidentifier()
            else None
        )

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
            return union([literal(arg) for arg in args])
        if name == _OPTIONAL:
            parts.append(Text(NONE))
        if name in _UNIONS or (name in _WRAPPERS and len(parts) == 1):
            return union(parts)
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
                self._mro[klass] = c3(klass, [*known, bases])
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

    def returns(
        self,
        defs: Defs,
        module: str,
        owner: ClassRef | None,
        *,
        awaited: bool = False,
    ) -> Form | None:
        """Read what a function (each of its overloads) returns: an `async def`'s, awaited, if `awaited`.

        Returns:
          The form every overload agrees on, `ANY_STR` for `str`/`bytes` overloads, or `None`.

        """
        if any(not readable(node, awaited=awaited) for node in defs):
            return None
        forms: list[Form | None] = [
            None if node.returns is None else self.form(node.returns, module, owner) for node in defs
        ]
        if owner is None and any_str_overloads(defs, forms):
            return ANY_STR
        first: Form | None = forms[0]
        if first is None or any(form != first for form in forms):
            return None
        return None if first == ANY_STR and not mentions(defs, "AnyStr") else first

    def future_bound(self, annotation: ast.expr | None, module: str) -> bool:
        """Check whether a parameter is a type variable bounded by a future (`_FT`, a `Future[Any]`).

        Returns:
          Whether it is: a coroutine's call isn't one, though awaiting it gives something.

        """
        found: Found | None = None if annotation is None else self.ref(annotation, module)
        bound: ast.expr | None = (
            found.binding.bound if found is not None and isinstance(found.binding, TypeVariable) else None
        )
        head: ast.expr | None = bound.value if isinstance(bound, ast.Subscript) else bound
        return head is not None and ast.unparse(head).rpartition(".")[2] in _FUTURES

    def returns_any(self, defs: Defs, module: str) -> bool:
        """Check whether a function (each of its overloads) is declared to return `typing.Any` alone.

        Returns:
          Whether it is: a call of it is an `Any` (`json.loads`), which `vague` judges.

        """
        found: list[Found | None] = [
            None if node.returns is None or not readable(node) else self.ref(node.returns, module)
            for node in defs
        ]
        return bool(found) and all(
            each is not None and each.module in _TYPING and each.name == ANY for each in found
        )

    def members(self, klass: ClassRef) -> dict[str, Member]:
        """Read a class's public members, inherited ones included, as the class resolves them.

        Returns:
          Each member, by name.

        """
        if klass not in self._members:
            self._members[klass] = {} if self.typed_dict(klass) else self._resolved(klass)
        return self._members[klass]

    def _resolved(self, klass: ClassRef) -> dict[str, Member]:
        found: dict[str, Member] = {}
        seen: set[str] = set()
        owner: ClassRef
        for owner in self.trusted(klass)[0]:
            name: str
            binding: Binding
            member: Member | None
            for name, binding in self.body(owner).items():
                if name not in seen and _read(name) and (member := self._member(binding, owner, klass)):
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
                read: bool = _read(name) or name in OPERATORS
                if name not in seen and read and isinstance(binding, Function):
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
                if isinstance(defs[0], ast.AsyncFunctionDef) and kind == _METHOD:
                    kind, form = AWAITED, self.returns(defs, owner.module, klass, awaited=True)
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


def _read(name: str) -> bool:
    """Check whether a class's member is one the tables read: one a subclass may call, or a statement does.

    A public one, or one a single underscore keeps to the class and its subclasses (`self._expand_help()`
    in an `argparse.HelpFormatter`'s); not a dunder, nor a name the class mangles (`__x`). `with`
    gives what `__enter__` returns (`async with`, what `__aenter__` does, awaited), and a subscript
    what `__getitem__` does: the dunders a fix reads.

    Returns:
      Whether it is.

    """
    return name in {_ENTER, _AENTER, _GET_ITEM} or not private(name) or not name.startswith(_DUNDER)


def readable(node: ast.FunctionDef | ast.AsyncFunctionDef, *, awaited: bool = False) -> bool:
    """Check a function is one the tables read: annotated, only known decorators, and not async.

    Or, if `awaited`, async: its declared return is then what awaiting its call gives.

    Returns:
      Whether it is.

    """
    names: set[str] = {decorator_name(decorator) for decorator in node.decorator_list}
    return (
        isinstance(node, ast.AsyncFunctionDef) == awaited
        and node.returns is not None
        and names <= _DECORATORS | _PROPERTIES
    )


def _is_ellipsis(node: ast.expr) -> bool:
    return isinstance(node, ast.Constant) and node.value is Ellipsis
