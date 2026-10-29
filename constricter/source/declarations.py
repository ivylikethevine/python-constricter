"""What a module declares, for `--fix`.

Its functions' and methods' return types, its classes' attributes, its type variables, and the
factories and casts it imports (see `constricter.source.annotations` for what an annotation says).
"""

import ast
from collections import Counter
from collections.abc import Iterator, Mapping, Sequence
from functools import lru_cache
from typing import Final, NamedTuple, TypeAlias, cast
from weakref import WeakKeyDictionary

from constricter.source.annotations import node_name, words
from constricter.source.concrete import binds_all, unbound_names
from constricter.source.decorators import Held, passing, spelled
from constricter.source.keys import key, keys
from constricter.source.quoted import written
from constricter.source.syntax import child_statements, top_level
from constricter.source.usable import OVERLOADS, agreed, usable_return

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
_GENERIC_BASES: Final = frozenset({"Generic", "Protocol"})  # a base that lists a class's type parameters
_TYPE_VAR: Final = "TypeVar"  # the node class of a plain type parameter (`ast.TypeVar`, Python 3.12+)
_GET: Final = "__get__"  # a descriptor's: what an instance's attribute of it gives
_DEFAULT: Final = "default"  # a type variable's default, as `TypeVar` takes it
_NO_NAMES: Final[frozenset[str]] = frozenset()


class GenericClass(NamedTuple):
    """A generic class's type parameters, in order, and its members' types, which may name them.

    `attributes`: its annotated attributes and properties; `methods`: its plain methods' declared
    returns, `Self` where one returns its receiver (see `generic_members`); `bases`: its subscripted
    bases as written (`Base[T]`), whose members it takes; `bound`: the names its body binds, which
    it takes from none.
    """

    params: tuple[str, ...]
    attributes: Mapping[str, str]
    methods: Mapping[str, str]
    bases: tuple[str, ...] = ()
    bound: frozenset[str] = frozenset()


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
            case ast.ImportFrom(module=str() as module, level=0) if module in _TYPING_MODULES:
                names.update(alias.asname or alias.name for alias in stmt.names if alias.name == _CAST)
            case ast.Import():
                names.update(
                    f"{alias.asname or alias.name}.{_CAST}"
                    for alias in stmt.names
                    if alias.name in _TYPING_MODULES
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
    called: dict[str, str] | None
    for node in _class_nodes(tree):
        if (called := _called_keys(node)) is not None:
            keyed.add(node.name)
            found[node.name] = called
        elif not _generic(node, tree) and any(
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


def _called_keys(node: ast.ClassDef) -> dict[str, str] | None:
    """Read the keys of a class whose one base is a `TypedDict("D", {"a": int, ...})` call.

    Returns:
      Each key's type as written; `None` for a class under anything else.

    """
    func: ast.expr
    names: list[ast.expr | None]
    values: list[ast.expr]
    match node.bases:
        case [
            ast.Call(
                func=func,
                args=[ast.Constant(value=str()), ast.Dict(keys=names, values=values)],
            ),
        ] if node_name(func) == _TYPED_DICT and all(
            isinstance(name, ast.Constant) and isinstance(name.value, str) for name in names
        ):
            return {
                key(str(cast("ast.Constant", name).value)): written(value)
                for name, value in zip(names, values, strict=True)
            }
        case _:
            return None


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
        if not _generic(node, tree):
            attrs: dict[str, str] = {}
            for stmt in node.body:
                match stmt:
                    case ast.AnnAssign(target=ast.Name(id=name), annotation=annotation, value=value):
                        text: str | None = _class_var(annotation)
                        if text is None and value is not None:
                            text = written(annotation)
                        if text and not type_vars & set(words(text)):
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
    vouched: dict[str, str] = returns(tree)
    return {
        stmt.name: Held(
            declared[stmt.name],
            tuple(sorted({spelled(d) or "" for d in stmt.decorator_list} - known)),
        )
        for stmt in tree.body
        if isinstance(stmt, ast.FunctionDef) and stmt.name in declared and stmt.name not in vouched
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
        if not _generic(node, tree):
            found[node.name] = {
                name: node.name if _is_self(annotation) else annotation
                for name, annotation in (_partial_returns if partly else _declared_returns)(
                    node.body,
                    type_vars,
                    awaited=awaited,
                    decorators=decorators,
                    vouched=None if anything else _passing(tree),
                ).items()
                if _is_self(annotation) or _SELF not in words(annotation)
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


def generic_classes(tree: ast.Module, defaulted: frozenset[str] | None = None) -> frozenset[str]:
    """Find the generic classes the module defines (see `_generic`).

    `defaulted`: the type variables with a default it names (`TypeVar("T", default=int)`): a class
    whose every parameter is one of them is left out, as a type checker reads it bare with those
    (see `generic_names`); `None`, every generic class.

    Returns:
      Their names: written bare, as `--fix` would write `self`'s type, each is missing its arguments.

    """
    return frozenset(
        node.name
        for node in _class_nodes(tree)
        if _generic(node, tree) and (defaulted is None or not _all_defaulted(node, tree, defaulted))
    )


def generic_names(tree: ast.Module) -> dict[str, frozenset[str]]:
    """Name what each generic class's subscripted bases name that may be a type variable (`Generic[T]`'s `T`).

    Not a `class C[T]`'s, whose parameters say whether they have a default themselves.

    Returns:
      Each such class's name, and those names, as written.

    """
    type_vars: frozenset[str] = defined_type_vars(tree)
    return {
        node.name: _unbound(node, tree, type_vars)
        for node in _class_nodes(tree)
        if not getattr(node, "type_params", ()) and _generic(node, tree)
    }


def _unbound(node: ast.ClassDef, tree: ast.Module, type_vars: frozenset[str]) -> frozenset[str]:
    """Name what a class's subscripted bases name that may be a type variable (see `concrete.unbound_names`).

    Returns:
      Them.

    """
    subscripted: list[ast.expr] = [base.slice for base in node.bases if isinstance(base, ast.Subscript)]
    return frozenset[str]().union(*(unbound_names(each, tree, type_vars) for each in subscripted))


def _all_defaulted(node: ast.ClassDef, tree: ast.Module, defaulted: frozenset[str]) -> bool:
    """Check whether every type parameter a generic class may have has a default.

    `class C[T = int]`'s own, or else each name its subscripted bases name that may be a type
    variable, of `defaulted`.

    Returns:
      Whether it has.

    """
    params: list[ast.AST]
    if params := list(cast("list[ast.AST]", getattr(node, "type_params", []))):
        return all(getattr(param, "default_value", None) is not None for param in params)
    names: frozenset[str] = _unbound(node, tree, defined_type_vars(tree))
    return bool(names) and names <= defaulted


def defaulted_type_vars(tree: ast.Module) -> frozenset[str]:
    """Find the module-level names bound to a type variable with a default (`TypeVar("T", default=int)`).

    Returns:
      Those names.

    """
    names: set[str] = set()
    stmt: ast.stmt
    name: str
    func: ast.expr
    keywords: list[ast.keyword]
    for stmt in top_level(tree.body):  # under an `if TYPE_CHECKING:` too
        match stmt:
            case ast.Assign(targets=[ast.Name(id=name)], value=ast.Call(func=func, keywords=keywords)) if (
                node_name(func) in _TYPE_VARS and any(keyword.arg == _DEFAULT for keyword in keywords)
            ):
                names.add(name)
            case _:
                pass
    return frozenset(names)


def descriptors(tree: ast.Module) -> dict[str, str | None]:
    """Find the module's descriptors: the classes defined once whose bodies define `__get__`.

    An attribute a class body annotates with one is read through an instance as `__get__` returns.

    Returns:
      Each one's name, and that return where a plain `__get__` declares it (see `_declared_returns`),
      not as `Self`; `None` where it's overloaded, undeclared, vague or names a type variable.

    """
    counts: Counter[str] = Counter(node.name for node in _class_nodes(tree))
    node: ast.ClassDef
    type_vars: frozenset[str] = defined_type_vars(tree)
    found: dict[str, str | None] = {}
    for node in _class_nodes(tree):
        if counts[node.name] == 1 and any(
            isinstance(stmt, ast.FunctionDef | ast.AsyncFunctionDef) and stmt.name == _GET
            for stmt in node.body
        ):
            returned: str | None = _declared_returns(node.body, type_vars).get(_GET)
            found[node.name] = None if returned is None or _is_self(returned) else returned
    return found


def _generic(node: ast.ClassDef, tree: ast.Module) -> bool:
    """Check whether a class is generic: `class C[T]`, or a subscripted base that may pass a type variable.

    A base whose subscript names only what can't be one binds every parameter it inherits
    (`class Dataset(Mapping[Hashable, "DataArray"])`): see `concrete.binds_all`.

    Returns:
      Whether it is: its members' types then depend on how it's parameterised.

    """
    return bool(cast("object", getattr(node, "type_params", ()))) or any(  # Python 3.12+'s `class C[T]`
        isinstance(base, ast.Subscript) and not binds_all(base.slice, tree, defined_type_vars(tree))
        for base in node.bases
    )


def generic_members(tree: ast.Module, imported: frozenset[str] = _NO_NAMES) -> dict[str, GenericClass]:
    """Read each generic class the module defines once: its type parameters and members' types.

    Its parameters are those `class C[T]` lists, or a `Generic[...]` or `Protocol[...]` base lists
    (whichever module defines them), or else the type variables it defines that its subscripted
    bases name, in the order they first do (`class C(Base[K, V])`). Its members are typed as
    `classes` and `method_returns` type a plain class's, but for its own parameters: a member whose
    type names any other type variable, the module's or one of `imported` (those it imports), is
    left out (`def get(self, d: D) -> T | D`), as is one that mentions `Self` other than bare.

    Returns:
      Each class's name, and what it declares.

    """
    type_vars: frozenset[str] = defined_type_vars(tree)
    counts: Counter[str] = Counter(node.name for node in _class_nodes(tree))
    node: ast.ClassDef
    found: dict[str, GenericClass] = {}
    vouched: frozenset[str] = _passing(tree)
    for node in _class_nodes(tree):
        params: tuple[str, ...] = _params(node, type_vars) if _generic(node, tree) else ()
        if not params or counts[node.name] > 1:
            continue
        others: frozenset[str] = (type_vars | imported) - frozenset(params)
        methods: dict[str, str] = _declared_returns(node.body, others, vouched=vouched)
        attributes: dict[str, str] = {
            **_declared_returns(node.body, others, decorators=_PROPERTIES, vouched=vouched),
            **_attributes(node),
        }
        found[node.name] = GenericClass(
            params,
            {name: text for name, text in attributes.items() if _typed_by(text, others)},
            {
                name: _SELF if _is_self(text) else text
                for name, text in methods.items()
                if _is_self(text) or _typed_by(text, others)
            },
            tuple(ast.unparse(base) for base in node.bases if isinstance(base, ast.Subscript)),
            _binds(node.body),
        )
    return found


def _binds(body: Sequence[ast.stmt]) -> frozenset[str]:
    """Name what a class's body binds: its functions, classes and variables.

    Returns:
      The names.

    """
    targets: list[ast.expr] = [
        target
        for stmt in body
        for target in (
            stmt.targets
            if isinstance(stmt, ast.Assign)
            else [stmt.target]
            if isinstance(stmt, ast.AnnAssign | ast.AugAssign)
            else []
        )
    ]
    defined: frozenset[str] = frozenset(
        stmt.name for stmt in body if isinstance(stmt, ast.FunctionDef | ast.AsyncFunctionDef | ast.ClassDef)
    )
    return defined | {
        node.id for target in targets for node in ast.walk(target) if isinstance(node, ast.Name)
    }


def _typed_by(text: str, others: frozenset[str]) -> bool:
    """Check whether a generic class's member's type names none of `others`, nor `Self` but bare.

    Returns:
      Whether it does.

    """
    named: set[str] = set(words(text))
    return not named & others and _SELF not in named and _CLASS_VAR not in named


def _params(node: ast.ClassDef, type_vars: frozenset[str]) -> tuple[str, ...]:
    """Name a generic class's type parameters, in order (see `generic_members`).

    Returns:
      Them: a `Generic[...]`'s or `Protocol[...]`'s arguments, or else the type variables the module
      defines that its subscripted bases name; none where one is a `ParamSpec` or a
      `TypeVarTuple` (`*Ts`), or a listed argument isn't a name.

    """
    listed: list[ast.AST]
    if listed := list(cast("list[ast.AST]", getattr(node, "type_params", []))):  # Python 3.12+'s `class C[T]`
        plain: bool = all(type(each).__name__ == _TYPE_VAR for each in listed)
        return tuple(cast("str", getattr(each, "name", "")) for each in listed) if plain else ()
    subscripted: list[ast.Subscript] = [base for base in node.bases if isinstance(base, ast.Subscript)]
    listing: list[ast.Subscript]
    # Each a type variable, whichever module defines it: Python takes nothing else there.
    if listing := [base for base in subscripted if node_name(base.value) in _GENERIC_BASES]:
        args: list[ast.expr] = [
            arg
            for each in listing
            for arg in (each.slice.elts if isinstance(each.slice, ast.Tuple) else [each.slice])
        ]
        if not all(isinstance(arg, ast.Name) for arg in args):
            return ()
        return tuple(dict.fromkeys(cast("ast.Name", arg).id for arg in args))
    names: list[str] = []
    base: ast.Subscript
    for base in subscripted:
        part: ast.AST
        for part in ast.walk(base.slice):
            if isinstance(part, ast.Name) and part.id in type_vars and part.id not in names:
                names.append(part.id)
    return tuple(names)


def _is_self(annotation: str) -> bool:
    """Check whether an annotation is exactly `Self` (bare, or `typing.Self` and the like).

    Returns:
      Whether it is.

    """
    # `annotation` is always `ast.unparse`'s own output, so it's always valid Python to parse back.
    return node_name(ast.parse(annotation, mode="eval").body) == _SELF


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
    defined: dict[str, list[ast.FunctionDef | ast.AsyncFunctionDef]] = {}
    stmt: ast.stmt
    for stmt in body:
        if isinstance(stmt, ast.FunctionDef | ast.AsyncFunctionDef) and not _accessor(stmt):
            defined.setdefault(stmt.name, []).append(stmt)
    found: dict[str, tuple[str, bool]] = {}
    name: str
    defs: list[ast.FunctionDef | ast.AsyncFunctionDef]
    for name, defs in defined.items():
        declared: tuple[str, bool] | None = usable_return(defs[0]) if len(defs) == 1 else agreed(defs)
        if (
            declared is not None
            and isinstance(defs[-1], ast.AsyncFunctionDef) == awaited
            and _plain(defs[-1], decorators, vouched)
            and all(_plain(each, decorators, vouched, ignored=OVERLOADS) for each in defs[:-1])
        ):
            found[name] = declared
    return {name: read for name, read in found.items() if not type_vars & set(words(read[0]))}


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
    *,
    ignored: frozenset[str] = _NO_NAMES,
) -> bool:
    """Check that `func` is decorated as asked, for its declared return to type its calls.

    `ignored`: decorators passed over (an overload's `@overload`).

    Returns:
      Whether it is: decorated by exactly one of `decorators` (if any), and otherwise only as
      `vouched` spells (`None`: by anything spelled).

    """
    listed: list[ast.expr] = [d for d in func.decorator_list if node_name(d) not in ignored]
    others: list[ast.expr] = [d for d in listed if node_name(d) not in decorators]
    spellings: list[str | None] = [spelled(decorator) for decorator in others]
    return (
        len(listed) - len(others) == bool(decorators)
        and None not in spellings
        and (vouched is None or vouched.issuperset(spellings))
    )
