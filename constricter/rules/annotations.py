# SPDX-License-Identifier: MIT
"""What an annotation says (LVA005, LVA006, LVA011), and what a module declares.

An annotation's vague parts, nesting depth and longest fixed-length tuple; a module's functions' and
methods' return types, its classes' attributes, and the factories it imports.
"""

import ast
import re
from collections.abc import Iterator, Mapping, Sequence
from functools import lru_cache
from typing import Final, TypeAlias, cast
from weakref import WeakKeyDictionary

from constricter.rules.decorators import Held, passing, spelled
from constricter.rules.keys import keys
from constricter.rules.quoted import parsed, written
from constricter.rules.syntax import child_statements, declared_return, top_level

_VAGUE: Final = frozenset({"Any", "object"})
_UNIONS: Final = frozenset({"Optional", "Union"})  # a union's members, as a subscript's arguments
# `collections.abc`'s generic classes (`typing` has each too).
ABSTRACT: Final = frozenset(
    {
        "AsyncGenerator",
        "AsyncIterable",
        "AsyncIterator",
        "Awaitable",
        "Callable",
        "Collection",
        "Container",
        "Coroutine",
        "Generator",
        "ItemsView",
        "Iterable",
        "Iterator",
        "KeysView",
        "Mapping",
        "MutableMapping",
        "MutableSequence",
        "MutableSet",
        "Reversible",
        "Sequence",
        "ValuesView",
    },
)
# Generics that say little without their parameters.
GENERICS: Final = ABSTRACT | frozenset(
    {
        "AbstractSet",
        "ChainMap",
        "Counter",
        "DefaultDict",
        "Deque",
        "Dict",
        "FrozenSet",
        "List",
        "Match",
        "OrderedDict",
        "Pattern",
        "Set",
        "Tuple",
        "Type",
        "defaultdict",
        "deque",
        "dict",
        "frozenset",
        "list",
        "set",
        "tuple",
        "type",
    },
)
_TUPLES: Final = frozenset({"tuple", "Tuple"})  # the annotations that list one type per element
_TYPE_VARS: Final = frozenset({"TypeVar", "ParamSpec", "TypeVarTuple"})
# Each module's classes and type variables, for as long as its tree lives: every class table
# reads them, for the index and then for the check.
_Classes: TypeAlias = tuple[ast.ClassDef, ...]
_Names: TypeAlias = frozenset[str]
_CLASS_NODES: Final[WeakKeyDictionary[ast.Module, _Classes]] = WeakKeyDictionary()
_TYPE_VARS_DEFINED: Final[WeakKeyDictionary[ast.Module, _Names]] = WeakKeyDictionary()
_TYPING_MODULES: Final = frozenset({"typing", "typing_extensions"})
_TYPING_VARS: Final = frozenset({"AnyStr"})  # the type variables `typing` itself defines
# Modules `_FACTORIES`' names are imported from (so an aliased or re-exported import is still found).
_FACTORY_MODULES: Final = frozenset({"enum", "typing", "typing_extensions"})
# A method returning `Self` returns its receiver's own class.
_SELF: Final = "Self"
# Decorators that make a method an attribute of its instances, or callable on its class.
_PROPERTIES: Final = frozenset({"property", "cached_property"})
_CLASS_SIDE: Final = frozenset({"classmethod", "staticmethod"})
_ACCESSORS: Final = frozenset({"setter", "deleter"})  # `@name.setter`: the same property, not a redefinition
_CLASS_VAR: Final = "ClassVar"
_TYPED_DICT: Final = "TypedDict"
_CAST: Final = "cast"
_UNDECORATED: Final[frozenset[str]] = frozenset()  # no decorators: a plain method


def imported_from(tree: ast.Module, modules: frozenset[str]) -> frozenset[str]:
    """Find the top-level names this module imports (`from module import name`) from one of `modules`.

    Only absolute imports are resolved; a relative one (`from . import x`) names no module here.

    Returns:
      Those names, as they're bound here (their alias, if importing gave them one).

    """
    names: set[str] = set()
    stmt: ast.stmt
    module: str
    for stmt in tree.body:
        match stmt:
            case ast.ImportFrom(module=str() as module, level=0) if module in modules:
                names.update(alias.asname or alias.name for alias in stmt.names)
            case _:
                pass
    return frozenset(names)


def factories(tree: ast.Module) -> frozenset[str]:
    """Find names this module imports that are known to build a class or special form.

    Not an instance of what they're named (`Enum`, `NamedTuple`, `TypeVar`, ... from `enum`,
    `typing` or `typing_extensions`), however they're aliased.

    Returns:
      Those names, as they're bound here.

    """
    return imported_from(tree, _FACTORY_MODULES)


def casts(tree: ast.Module) -> frozenset[str]:
    """Find how this module can name `typing.cast`: `cast` (or its alias), `typing.cast`, `t.cast`.

    Returns:
      Each spelling of a call to it, as `ast.unparse` writes the callee.

    """
    names: set[str] = set()
    stmt: ast.stmt
    module: str
    for stmt in tree.body:
        match stmt:
            case ast.ImportFrom(module=str() as module, level=0) if module in _FACTORY_MODULES - {"enum"}:
                names.update(alias.asname or alias.name for alias in stmt.names if alias.name == _CAST)
            case ast.Import():
                names.update(
                    f"{alias.asname or alias.name}.{_CAST}"
                    for alias in stmt.names
                    if alias.name in _FACTORY_MODULES - {"enum"}
                )
            case _:
                pass
    return frozenset(names)


def _class_nodes(tree: ast.Module) -> tuple[ast.ClassDef, ...]:
    """Find every class the module defines, however deep.

    Returns:
      Them, in source order.

    """
    found: tuple[ast.ClassDef, ...] | None
    if (found := _CLASS_NODES.get(tree)) is None:
        found = _CLASS_NODES[tree] = _read_class_nodes(tree)
    return found


def _read_class_nodes(tree: ast.Module) -> tuple[ast.ClassDef, ...]:
    return tuple(node for node in _statements(tree.body) if isinstance(node, ast.ClassDef))


def _statements(body: Sequence[ast.stmt]) -> Iterator[ast.stmt]:
    """Walk statements only, into every nested block (a function's and a class's too), not expressions.

    Much less than `ast.walk` visits, for what only a statement can be: a class, an annotated
    assignment.

    Yields:
      Each statement, before those inside it (depth first, in source order).

    """
    # A stack, not a recursion: a nested generator passes each statement up through every level.
    # `None` at its bottom ends it: popped, the walk's done.
    waiting: list[ast.stmt | None] = [None, *reversed(body)]
    stmt: ast.stmt
    for stmt in iter(waiting.pop, None):
        yield stmt
        waiting.extend(reversed(_blocks(stmt)))


def _blocks(stmt: ast.stmt) -> list[ast.stmt]:
    """Collect the statements directly inside `stmt`, a function's or class's body included.

    Returns:
      Them, in source order.

    """
    return (
        stmt.body
        if isinstance(stmt, ast.FunctionDef | ast.AsyncFunctionDef | ast.ClassDef)
        else child_statements(stmt)
    )


def classes(tree: ast.Module) -> dict[str, dict[str, str]]:
    """Map each class defined in the module to its instances' annotated attributes.

    A class-body annotation (`class C: x: int`), a `self.x: int = ...` annotated assignment anywhere
    in one of its methods, and a `@property`'s declared return (as `method_returns` reads a method's,
    and a vague one too, as an annotation's is kept) all count; a name that names more than one class
    in the module (however unlikely) gets the last one's attributes. A `TypedDict` class (under
    `TypedDict`, or one of the module's defined before it; not a generic one) has its keys instead,
    each spelled as `keys.key` does.

    Returns:
      Each class's name, mapped to its attributes' names and annotation text.

    """
    properties: dict[str, dict[str, str]] = _class_returns(tree, _PROPERTIES)
    vague: dict[str, dict[str, str]] = _class_returns(tree, _PROPERTIES, partly=True)
    found: dict[str, dict[str, str]] = {}
    keyed: set[str] = set()
    node: ast.ClassDef
    for node in _class_nodes(tree):
        if not _generic(node) and any(
            node_name(base) == _TYPED_DICT or (isinstance(base, ast.Name) and base.id in keyed)
            for base in node.bases
        ):
            keyed.add(node.name)
            found[node.name] = keys(node)
        else:
            found[node.name] = {
                **properties.get(node.name, {}),
                **vague.get(node.name, {}),
                **_attributes(node),
            }
    return found


def class_attributes(tree: ast.Module) -> dict[str, dict[str, str]]:
    """Map each non-generic class defined in the module to the attributes its class itself has.

    A class-body annotation with a value (`limit: int = 3`), or a `ClassVar[T]` (as `T`): what `cls.x`
    reads in a classmethod. A bare annotation (`x: int`) only declares an instance attribute (a
    dataclass field), so it doesn't count.

    Returns:
      Each class's name, mapped to its class attributes' names and annotation text.

    """
    type_vars: frozenset[str] = defined_type_vars(tree)
    found: dict[str, dict[str, str]] = {}
    node: ast.AST
    stmt: ast.stmt
    name: str
    annotation: ast.expr
    value: ast.expr | None
    for node in _class_nodes(tree):
        if not _generic(node):
            attrs: dict[str, str] = {}
            for stmt in node.body:
                match stmt:
                    case ast.AnnAssign(target=ast.Name(id=name), annotation=annotation, value=value):
                        text: str | None = _class_var(annotation)
                        if text is None and value is not None:
                            text = written(annotation)
                        if text and not type_vars & set(_words(text)):
                            attrs[name] = text
                    case _:
                        pass
            found[node.name] = attrs
    return found


def _class_var(annotation: ast.expr) -> str | None:
    """Unwrap `ClassVar[T]`.

    Returns:
      `T` as text, or `None` if `annotation` isn't a parameterised `ClassVar`.

    """
    outer: ast.expr
    inner: ast.expr
    match annotation:
        case ast.Subscript(value=outer, slice=inner) if node_name(outer) == _CLASS_VAR:
            return written(inner)
        case _:
            return None


def class_methods(tree: ast.Module) -> dict[str, dict[str, str]]:
    """Map each non-generic class defined in the module to its classmethods' and staticmethods' returns.

    What `cls.method()` gives in a classmethod, under `method_returns`' rules.

    Returns:
      Each class's name, mapped to those methods' names and return annotation text.

    """
    return _class_returns(tree, _CLASS_SIDE)


def held_class_methods(tree: ast.Module) -> dict[str, dict[str, Held]]:
    """Find the classmethods and staticmethods declaring a return under decorators the module can't vouch for.

    As `class_methods` reads them, but for those decorators: another module's may give the method
    back (see `held`).

    Returns:
      Each class's name, mapped to those methods' names, return annotations and decorators.

    """
    known: frozenset[str] = _passing(tree)
    declared: dict[str, dict[str, str]] = _class_returns(tree, _CLASS_SIDE, anything=True)
    own: dict[str, dict[str, str]] = class_methods(tree)
    found: dict[str, dict[str, Held]] = {}
    node: ast.ClassDef
    for node in _class_nodes(tree):
        methods: dict[str, Held] = {
            stmt.name: Held(
                declared[node.name][stmt.name],
                tuple(
                    sorted(
                        {spelled(d) or "" for d in stmt.decorator_list if node_name(d) not in _CLASS_SIDE}
                        - known,
                    ),
                ),
            )
            for stmt in node.body
            if isinstance(stmt, ast.FunctionDef)
            and stmt.name in declared.get(node.name, {})
            and stmt.name not in own[node.name]
        }
        if methods:
            found[node.name] = methods
    return found


def _attributes(node: ast.ClassDef) -> dict[str, str]:
    attrs: dict[str, str] = {}
    stmt: ast.stmt
    name: str
    annotation: ast.expr
    for stmt in node.body:
        match stmt:
            case ast.AnnAssign(target=ast.Name(id=name), annotation=annotation):
                attrs[name] = written(annotation)
            case ast.FunctionDef() | ast.AsyncFunctionDef():
                attrs.update(_self_attributes(stmt))
            case _:
                pass
    return attrs


def _self_attributes(func: ast.FunctionDef | ast.AsyncFunctionDef) -> Iterator[tuple[str, str]]:
    """Find `self.attr: T = ...` annotated assignments anywhere in a method's body.

    Yields:
      Each attribute's name and annotation text.

    """
    node: ast.stmt
    name: str
    annotation: ast.expr
    for node in _statements(func.body):  # an annotated assignment is always a statement
        match node:
            case ast.AnnAssign(
                target=ast.Attribute(value=ast.Name(id="self"), attr=name),
                annotation=annotation,
            ):
                yield name, written(annotation)
            case _:
                pass


def is_composite(value: ast.expr) -> bool:
    """Check whether a value is written as a type made of others: a subscript, or a union.

    What a type alias's assignment binds (`Json = dict[str, "Json"] | str`), but for a bare class's
    (`Alias = Class`).

    Returns:
      Whether it is.

    """
    return isinstance(value, ast.Subscript) or (
        isinstance(value, ast.BinOp) and isinstance(value.op, ast.BitOr)
    )


def node_name(node: ast.AST) -> str:
    """Read a `Name`'s or `Attribute`'s simple name.

    Returns:
      It, or `""` if `node` is neither.

    """
    name: str
    match node:
        case ast.Name(id=name) | ast.Attribute(attr=name):
            return name
        case _:
            return ""


def dotted(node: ast.expr) -> str | None:
    """Spell a name, or a chain of attributes on one (`pkg.util.f`), as written.

    Returns:
      It, or `None` if `node` is anything else (`f().g`, `x[0].g`).

    """
    name: str
    value: ast.expr
    base: str | None
    match node:
        case ast.Name(id=name):
            return name
        case ast.Attribute(value=value, attr=name) if (base := dotted(value)) is not None:
            return f"{base}.{name}"
        case _:
            return None


def is_vague(annotation: ast.expr) -> bool:
    """Check an annotation for vague types.

    Returns:
      Whether it has `Any`, `object` or a generic without its parameters in it.

    """
    root: ast.expr = parsed(annotation)
    subscripted: set[int] = {id(node.value) for node in ast.walk(root) if isinstance(node, ast.Subscript)}
    node: ast.AST
    for node in ast.walk(root):
        name: str = node_name(node)
        if name in _VAGUE or (name in GENERICS and id(node) not in subscripted):
            return True
    return False


def vague_parts(annotation: ast.expr) -> tuple[int, bool]:
    """Count an annotation's vague parts (see `is_vague`), and say whether one stands alone.

    Alone: the annotation itself or a member of its union (`Any`, `Any | None`, `Optional[object]`),
    where it says nothing at all. Anywhere else it's inside a type that says the rest
    (`tuple[str, Any]`), as a generic without its parameters is (`list`).

    Returns:
      How many there are, and whether one does.

    """
    root: ast.expr = parsed(annotation)
    subscripted: set[int] = {id(node.value) for node in ast.walk(root) if isinstance(node, ast.Subscript)}
    count: int = sum(
        node_name(node) in _VAGUE or (node_name(node) in GENERICS and id(node) not in subscripted)
        for node in ast.walk(root)
    )
    return count, any(node_name(member) in _VAGUE for member in _union_members(root))


def _union_members(node: ast.expr) -> list[ast.expr]:
    """Flatten an annotation's outermost union: `A | B`, `Optional[A]`, `Union[A, B]`.

    Returns:
      Its members; the annotation itself, if it's no union.

    """
    left: ast.expr
    right: ast.expr
    head: ast.expr
    inner: ast.expr
    match node:
        case ast.BinOp(op=ast.BitOr(), left=left, right=right):
            return [*_union_members(left), *_union_members(right)]
        case ast.Subscript(value=head, slice=inner) if node_name(head) in _UNIONS:
            parts: list[ast.expr] = inner.elts if isinstance(inner, ast.Tuple) else [inner]
            return [member for part in parts for member in _union_members(part)]
        case _:
            return [node]


def vague_fits(annotation: ast.expr, level: int) -> bool:
    """Check whether an annotation is no vaguer than `level` allows (`vague`, LVA005's).

    Below 0, no vague part at all. At 0, one, inside a type that says the rest (`tuple[str, Any]`).
    From 1, `level + 1` of them (`tuple[Any, Any]` at 1), and one alone (`Any`).

    Returns:
      Whether it is.

    """
    count: int
    alone: bool
    count, alone = vague_parts(annotation)
    return not count or (count <= level + 1 and (level > 0 or not alone))


def length(annotation: ast.expr) -> int:
    """Measure the longest fixed-length tuple an annotation lists, one type per element.

    `tuple[int, str]` is 2; `tuple[int, ...]` (any length) and anything but a tuple are 0.

    Returns:
      The most elements any `tuple[...]` or `Tuple[...]` in it lists.

    """
    node: ast.AST
    head: ast.expr
    elements: list[ast.expr]
    lengths: list[int] = [0]
    for node in ast.walk(parsed(annotation)):
        match node:
            case ast.Subscript(value=head, slice=ast.Tuple(elts=elements)) if node_name(head) in _TUPLES:
                lengths.append(0 if _variadic(elements) else len(elements))
            case ast.Subscript(value=head) if node_name(head) in _TUPLES:
                lengths.append(1)
            case _:
                pass
    return max(lengths)


def _variadic(elements: list[ast.expr]) -> bool:
    """Check whether a tuple annotation's elements end in `...` (`tuple[int, ...]`: any length).

    Returns:
      Whether they do.

    """
    # `tuple[()]` (the empty tuple) has no elements at all.
    return bool(elements) and isinstance(elements[-1], ast.Constant) and elements[-1].value is Ellipsis


def depth(annotation: ast.expr) -> int:
    """Measure how deeply an annotation's subscripts nest.

    Returns:
      The depth: `dict[str, list[int]]` is 2.

    """
    node: ast.expr = parsed(annotation)
    inner: ast.expr
    parts: list[ast.expr]
    left: ast.expr
    right: ast.expr
    match node:
        case ast.Subscript(slice=inner):
            return 1 + depth(inner)
        case ast.Tuple(elts=parts) | ast.List(elts=parts):
            return max((depth(part) for part in parts), default=0)
        case ast.BinOp(left=left, right=right):
            return max(depth(left), depth(right))
        case _:
            return 0


def returns(tree: ast.Module) -> dict[str, str]:
    """Return the declared return type of each plain top-level function whose calls `--fix` can annotate.

    Skipped: generic, async and redefined functions, one decorated by anything but a decorator that
    gives it back (see `decorators.passing`), and returns that are `None`, vague, or mention a
    module-level `TypeVar` (a call's type then depends on its arguments).

    Returns:
      Each such function's name, and its return annotation as source text.

    """
    return _declared_returns(tree.body, defined_type_vars(tree), vouched=_passing(tree))


@lru_cache(maxsize=4)  # asked for a module's functions, then its classes' methods
def _passing(tree: ast.Module) -> frozenset[str]:
    """Spell the decorators the module alone vouches for (see `decorators.passing`).

    Returns:
      Them.

    """
    return passing(tree, defined_type_vars(tree))


def held(tree: ast.Module) -> dict[str, Held]:
    """Find the plain top-level functions declaring a return under decorators the module can't vouch for.

    As `returns` reads them, but for those decorators: another module's may give the function back.

    Returns:
      Each one's name, its return annotation and those decorators (see `Held`).

    """
    known: frozenset[str] = _passing(tree)
    declared: dict[str, str] = _declared_returns(tree.body, defined_type_vars(tree), vouched=None)
    return {
        stmt.name: Held(
            declared[stmt.name],
            tuple(sorted({spelled(d) or "" for d in stmt.decorator_list} - known)),
        )
        for stmt in tree.body
        if isinstance(stmt, ast.FunctionDef) and stmt.name in declared and stmt.name not in returns(tree)
    }


def method_returns(tree: ast.Module, *, awaited: bool = False) -> dict[str, dict[str, str]]:
    """Map each non-generic class defined in the module to its methods' (`awaited`: `async` ones') returns.

    For `--fix` to type `obj.method()` on a local already typed as that class. A method counts under
    the same rules as `returns`' functions: a plain `def` directly in the class body, not decorated
    (so no `staticmethod`, `classmethod` or `property`) or redefined, whose return isn't `None`,
    vague, or a `TypeVar`. A generic class (`class C[T]`, or any subscripted base like `Generic[T]`)
    is skipped whole: its methods' returns depend on how it's parameterised. A bare `Self` return is
    the class itself; one that only mentions `Self` (`list[Self]`) is skipped.

    Returns:
      Each class's name, mapped to its methods' names and return annotation text.

    """
    return _class_returns(tree, _UNDECORATED, awaited=awaited)


def partial_returns(tree: ast.Module) -> dict[str, str]:
    """Return the declared return of each function `returns` leaves out for a vague part.

    `tuple[Row, dict[str, Any]]` types a call only as far as `vague` allows (see `vague_fits`), and
    an unpacking's names part by part.

    Returns:
      Each such function's name, and its return annotation as source text.

    """
    return _partial_returns(tree.body, defined_type_vars(tree), vouched=_passing(tree))


def partial_method_returns(tree: ast.Module) -> dict[str, dict[str, str]]:
    """Map each non-generic class to its methods' declared returns that have a vague part.

    As `partial_returns` reads functions': its plain methods', and its classmethods' and staticmethods'.

    Returns:
      Each class's name, mapped to those methods' names and return annotation text.

    """
    sides: dict[str, dict[str, str]] = _class_returns(tree, _CLASS_SIDE, partly=True)
    return {
        owner: {**sides[owner], **methods}
        for owner, methods in _class_returns(tree, _UNDECORATED, partly=True).items()
    }


def _class_returns(
    tree: ast.Module,
    decorators: frozenset[str],
    *,
    anything: bool = False,
    partly: bool = False,
    awaited: bool = False,
) -> dict[str, dict[str, str]]:
    """Map each non-generic class to the declared returns of its methods decorated by one of `decorators`.

    None of them (an empty set) means plain methods; see `method_returns` for the rules. Any other
    decorator must be one the module vouches for (see `decorators.passing`), or (`anything`) one
    `decorators.spelled` reads. `partly`: those left out for a vague part, instead.

    Returns:
      Each class's name, mapped to those methods' names and return annotation text.

    """
    type_vars: frozenset[str] = defined_type_vars(tree)
    found: dict[str, dict[str, str]] = {}
    node: ast.ClassDef
    for node in _class_nodes(tree):
        if not _generic(node):
            found[node.name] = {
                name: node.name if _is_self(annotation) else annotation
                for name, annotation in (_partial_returns if partly else _declared_returns)(
                    node.body,
                    type_vars,
                    awaited=awaited,
                    decorators=decorators,
                    vouched=None if anything else _passing(tree),
                ).items()
                if _is_self(annotation) or _SELF not in _words(annotation)
            }
    return found


def self_returns(tree: ast.Module) -> dict[str, frozenset[str]]:
    """Map each class to its methods (classmethods and staticmethods too) declared to return a bare `Self`.

    `method_returns` types such a call as the class; but called on `self` or `cls` it's `Self`, which
    a subclass's is too, so `--fix` writes that instead (see `constricter.fix.values.doubts`).

    Returns:
      Each class's name, and those methods' names.

    """
    return {
        node.name: frozenset(
            stmt.name
            for stmt in node.body
            if isinstance(stmt, ast.FunctionDef | ast.AsyncFunctionDef)
            and stmt.returns is not None
            and _is_self(written(stmt.returns))
        )
        for node in _class_nodes(tree)
    }


def generic_classes(tree: ast.Module) -> frozenset[str]:
    """Find the generic classes the module defines (see `_generic`).

    Returns:
      Their names: written bare, as `--fix` would write `self`'s type, each is missing its arguments.

    """
    return frozenset(node.name for node in _class_nodes(tree) if _generic(node))


def _generic(node: ast.ClassDef) -> bool:
    """Check whether a class is generic: `class C[T]`, or any subscripted base like `Generic[T]`.

    Returns:
      Whether it is: its members' types then depend on how it's parameterised.

    """
    return bool(cast("object", getattr(node, "type_params", ()))) or any(  # Python 3.12+'s `class C[T]`
        isinstance(base, ast.Subscript) for base in node.bases
    )


def _is_self(annotation: str) -> bool:
    """Check whether an annotation is exactly `Self` (bare, or `typing.Self` and the like).

    Returns:
      Whether it is.

    """
    # `annotation` is always `ast.unparse`'s own output, so it's always valid Python to parse back.
    return node_name(ast.parse(annotation, mode="eval").body) == _SELF


def free_of(types: Mapping[str, str], type_vars: frozenset[str]) -> dict[str, str]:
    """Drop the types that mention one of `type_vars` (a call's type then depends on its arguments).

    Returns:
      The others.

    """
    return {name: annotation for name, annotation in types.items() if not type_vars & set(_words(annotation))}


def free_of_all(
    tables: Mapping[str, Mapping[str, str]],
    type_vars: frozenset[str],
) -> dict[str, dict[str, str]]:
    """Drop each class's member types that mention one of `type_vars` (see `free_of`).

    Returns:
      The others, per class.

    """
    return {owner: free_of(types, type_vars) for owner, types in tables.items()}


def defined_type_vars(tree: ast.Module) -> frozenset[str]:
    """Find the module-level names bound to a `TypeVar`, `ParamSpec` or `TypeVarTuple`, or `typing.AnyStr`.

    Returns:
      Those names.

    """
    found: frozenset[str] | None
    if (found := _TYPE_VARS_DEFINED.get(tree)) is None:
        found = _TYPE_VARS_DEFINED[tree] = _read_defined_type_vars(tree)
    return found


def _read_defined_type_vars(tree: ast.Module) -> frozenset[str]:
    names: set[str] = set()
    stmt: ast.stmt
    name: str
    func: ast.expr
    module: str
    for stmt in top_level(tree.body):  # under an `if TYPE_CHECKING:` too
        match stmt:
            case ast.Assign(targets=[ast.Name(id=name)], value=ast.Call(func=func)) if (
                node_name(func) in _TYPE_VARS
            ):
                names.add(name)
            case ast.ImportFrom(module=str() as module, level=0) if module in _TYPING_MODULES:
                names.update(alias.asname or alias.name for alias in stmt.names if alias.name in _TYPING_VARS)
            case ast.Import(names=[*_]) if any(alias.name in _TYPING_MODULES for alias in stmt.names):
                names.update(_TYPING_VARS)  # `typing.AnyStr`: the word `AnyStr`
            case _:
                pass
    return frozenset(names)


def awaited_returns(tree: ast.Module) -> dict[str, str]:
    """Return the declared return type of each plain top-level `async def`: what awaiting a call gives.

    The same rules as `returns`' functions, for `async def` instead of `def`.

    Returns:
      Each such function's name, and its return annotation as source text.

    """
    return _declared_returns(tree.body, defined_type_vars(tree), awaited=True)


def _declared_returns(
    body: Sequence[ast.stmt],
    type_vars: frozenset[str],
    *,
    awaited: bool = False,
    decorators: frozenset[str] = _UNDECORATED,
    vouched: frozenset[str] | None = _UNDECORATED,
) -> dict[str, str]:
    """Find the plain functions (`async` ones if `awaited`) directly in `body` `--fix` can annotate.

    Plain means decorated only as `vouched` spells (`None`: by anything `decorators.spelled`
    reads), and with `decorators`, by exactly one of them too. A property's `@name.setter` or
    `@name.deleter` is the same property, not a redefinition. Not one whose return has a vague
    part (see `_partial_returns`).

    Returns:
      Each such function's name, and its return annotation as source text.

    """
    found: dict[str, tuple[str, bool]] = _every_return(
        body,
        type_vars,
        awaited=awaited,
        decorators=decorators,
        vouched=vouched,
    )
    return {name: annotation for name, (annotation, partial) in found.items() if not partial}


def _partial_returns(
    body: Sequence[ast.stmt],
    type_vars: frozenset[str],
    *,
    awaited: bool = False,
    decorators: frozenset[str] = _UNDECORATED,
    vouched: frozenset[str] | None = _UNDECORATED,
) -> dict[str, str]:
    """Find the plain functions directly in `body` whose declared return has a vague part.

    As `_declared_returns` finds the others.

    Returns:
      Each such function's name, and its return annotation as source text.

    """
    found: dict[str, tuple[str, bool]] = _every_return(
        body,
        type_vars,
        awaited=awaited,
        decorators=decorators,
        vouched=vouched,
    )
    return {name: annotation for name, (annotation, partial) in found.items() if partial}


def _every_return(
    body: Sequence[ast.stmt],
    type_vars: frozenset[str],
    *,
    awaited: bool,
    decorators: frozenset[str],
    vouched: frozenset[str] | None,
) -> dict[str, tuple[str, bool]]:
    """Read the declared return of each plain function directly in `body` (see `_declared_returns`).

    Returns:
      Each one's name, its return annotation as source text, and whether that has a vague
      part.

    """
    counts: dict[str, int] = {}
    found: dict[str, tuple[str, bool]] = {}
    stmt: ast.stmt
    name: str
    for stmt in body:
        match stmt:
            case ast.FunctionDef(name=name) | ast.AsyncFunctionDef(name=name) if not _accessor(stmt):
                counts[name] = counts.get(name, 0) + 1
                declared: tuple[str, bool] | None = _usable_return(stmt)
                if (
                    declared is not None
                    and isinstance(stmt, ast.AsyncFunctionDef) == awaited
                    and _plain(stmt, decorators, vouched)
                ):
                    found[name] = declared
            case _:
                pass
    return {
        name: read
        for name, read in found.items()
        if counts[name] == 1 and not type_vars & set(_words(read[0]))
    }


def _accessor(func: ast.FunctionDef | ast.AsyncFunctionDef) -> bool:
    """Check whether `func` is a property's setter or deleter (`@name.setter`).

    Returns:
      Whether it is.

    """
    return any(
        isinstance(decorator, ast.Attribute) and decorator.attr in _ACCESSORS
        for decorator in func.decorator_list
    )


def _plain(
    func: ast.FunctionDef | ast.AsyncFunctionDef,
    decorators: frozenset[str],
    vouched: frozenset[str] | None,
) -> bool:
    """Check that `func` is decorated as asked, for its declared return to type its calls.

    Returns:
      Whether it is: decorated by exactly one of `decorators` (if any), and otherwise only as
      `vouched` spells (`None`: by anything spelled).

    """
    others: list[ast.expr] = [d for d in func.decorator_list if node_name(d) not in decorators]
    spellings: list[str | None] = [spelled(decorator) for decorator in others]
    return (
        len(func.decorator_list) - len(others) == bool(decorators)
        and None not in spellings
        and (vouched is None or vouched.issuperset(spellings))
    )


# By the function alone: each class's body is read for its methods, its properties, its
# classmethods and those held back, and a function's declared return is the same to them all.
@lru_cache(maxsize=4096)
def _usable_return(func: ast.FunctionDef | ast.AsyncFunctionDef) -> tuple[str, bool] | None:
    """Read the return type `func` declares, if its calls always have it.

    Returns:
      Its annotation as source text, and whether it has a vague part (`tuple[Row, dict[str, Any]]`,
      `Any`); `None` for a generic function, no return, or `None`.

    """
    declared: ast.expr | None = declared_return(func)
    if (
        cast("object", getattr(func, "type_params", ()))  # Python 3.12+'s `def f[T]()`
        or declared is None
        or (isinstance(declared, ast.Constant) and declared.value is None)
    ):
        return None
    return written(declared), is_vague(declared)


def _words(annotation: str) -> list[str]:
    return [word for word in re.split(r"\W+", annotation) if word]


@lru_cache(maxsize=4096)  # asked of each fix's annotation several times: a few thousand distinct
def roots(annotation: str) -> frozenset[str]:
    """Find the names an annotation (maybe a string one) is written with.

    Returns:
      The names: `m.Row` gives `m`; none for a string that isn't an expression.

    """
    tree: ast.expr = parsed(ast.parse(annotation, mode="eval").body)
    return frozenset(node.id for node in ast.walk(tree) if isinstance(node, ast.Name))
