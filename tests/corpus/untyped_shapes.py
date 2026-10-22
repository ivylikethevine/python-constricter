"""What a binding's value is, for `corpus_untyped`'s census: its shape, and what it resolves to.

A file's `Module` says what each of its names refers to (what it binds at its top, and imports
anywhere); a scope's `Names` adds its parameters and locals. `shape` names a value's kind by them
(`call: self.method()`, `attr: chained`, `empty list`, ...) with what a call or an attribute reached
through an import resolves to (`os.path.join`), and `origin` says where that comes from: the
standard library, the corpus's own package, or a third-party one. `binding` finds the statement
that binds a name, and its value.
"""

import ast
import builtins
import functools
import importlib.machinery
import importlib.util
import sys
import sysconfig
from collections.abc import Iterable, Mapping, Sequence
from typing import Final, NamedTuple, TypeAlias, cast

_Json: TypeAlias = "str | int | bool | list[_Json] | dict[str, _Json] | None"
_Shape: TypeAlias = tuple[str, str]  # a value's shape, and what it resolves to through an import
_Scopes: TypeAlias = ast.FunctionDef | ast.AsyncFunctionDef | ast.Lambda
_Found: TypeAlias = tuple[str, ast.expr | None]  # a binding's statement kind, and its value
_ByNode: TypeAlias = Mapping[type[ast.expr], str]  # a name for each kind of node
_Kinds: TypeAlias = tuple[tuple[str, Iterable[str]], ...]  # each kind of name, and the names of it

_BUILTINS: Final = frozenset(dir(builtins))
_STDLIB: Final = frozenset(sys.stdlib_module_names)
_HOMES: Final = frozenset({sysconfig.get_paths()["stdlib"], sysconfig.get_paths()["platstdlib"]})
_SITE: Final = "site-packages"  # installed packages, under the standard library's directory on some systems
_RELATIVE: Final = "<relative>"
_SELVES: Final = frozenset({"self", "cls"})
_PARAM: Final = "param"
_IMPORTED: Final = "imported"
_STDLIB_ORIGIN: Final = "stdlib"
_OWN: Final = "own package"
_THIRD_PARTY: Final = "third-party"
_MODULE_CALL: Final = "call: module.func()"
# Shapes whose name says it all, whatever the value's parts.
_NAMED: Final[_ByNode] = {ast.IfExp: "conditional", ast.Compare: "compare"}
_DISPLAYS: Final[_ByNode] = {ast.List: "list", ast.Tuple: "tuple", ast.Set: "set", ast.Dict: "dict"}
_COMPREHENSIONS: Final = (ast.ListComp, ast.SetComp, ast.DictComp, ast.GeneratorExp)
_UNPACKING: Final = (ast.Tuple, ast.List, ast.Starred)


class Module:
    """What one file binds at its top, and imports anywhere: what a name in it can refer to."""

    def __init__(self, tree: ast.Module) -> None:
        """Read `tree`."""
        self.parents: dict[ast.AST, ast.AST] = {
            child: node for node in ast.walk(tree) for child in ast.iter_child_nodes(node)
        }
        self.imports: dict[str, str] = {}  # each name an import binds, and what it is (`os.path.join`)
        self.modules: set[str] = set()  # those an `import` binds, to a module
        self.defs: dict[str, ast.FunctionDef | ast.AsyncFunctionDef] = {}
        self.classes: frozenset[str] = frozenset(
            stmt.name for stmt in tree.body if isinstance(stmt, ast.ClassDef)
        )
        node: ast.AST
        for node in ast.walk(tree):
            self._imported(node)
        stmt: ast.stmt
        for stmt in tree.body:
            if isinstance(stmt, ast.FunctionDef | ast.AsyncFunctionDef):
                self.defs[stmt.name] = stmt
        self.globals: frozenset[str] = frozenset(
            node.id
            for node in ast.walk(tree)
            if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Store) and self.scope(node) is tree
        )
        self.annotated: bool = any(
            declares(node)
            for node in ast.walk(tree)
            if isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef)
        )

    def _imported(self, node: ast.AST) -> None:
        """Record the names one import binds (the last import of a name wins, as a walk meets them)."""
        alias: ast.alias
        names: list[ast.alias]
        module: str | None
        level: int
        match node:
            case ast.Import(names=names):
                for alias in names:
                    bound: str = alias.asname or alias.name.split(".", 1)[0]
                    self.imports[bound] = alias.name if alias.asname else bound
                    self.modules.add(bound)
            case ast.ImportFrom(module=module, names=names, level=level):
                prefix: str = f"{_RELATIVE}.{module or ''}" if level else module or ""
                for alias in names:
                    self.imports[alias.asname or alias.name] = f"{prefix}.{alias.name}"
                    self.modules.discard(alias.asname or alias.name)
            case _:
                pass

    def through(self, name: str, *attributes: str) -> str:
        """Spell what `name.attr...` resolves to through the import that binds `name`.

        Returns:
          It, dotted (`os.path.join`).

        """
        return ".".join([self.imports[name], *attributes])

    def scope(self, node: ast.AST) -> ast.AST | None:
        """Find the function, lambda, class or module `node` is bound in.

        Returns:
          It, or `None` for a node outside the tree.

        """
        parent: ast.AST | None = self.parents.get(node)
        match parent:
            case (
                None
                | ast.FunctionDef()
                | ast.AsyncFunctionDef()
                | ast.Lambda()
                | ast.ClassDef()
                | ast.Module()
            ):
                return parent
            case _:
                return self.scope(parent)


class Names(NamedTuple):
    """What a name means in one scope: its parameters (and whether each is annotated), locals, file."""

    module: Module
    params: Mapping[str, bool]
    stores: frozenset[str]

    def kind(self, name: str) -> str:
        """Say what `name` is here: `self`, `param`, `local`, `imported`, `moddef`, ..., `other`.

        Returns:
          The first that binds it, in that order.

        """
        if name in _SELVES and name in self.params:
            return name
        kinds: _Kinds = (
            (_PARAM, self.params),
            ("local", self.stores),
            (_IMPORTED, self.module.imports),
            ("moddef", self.module.defs),
            ("modclass", self.module.classes),
            ("global", self.module.globals),
            ("builtin", _BUILTINS),
        )
        kind: str
        names: Iterable[str]
        for kind, names in kinds:
            if name in names:
                return kind
        return "other"

    def is_module(self, name: str) -> bool:
        """Check that `name` is a module an `import` binds here (not shadowed by a parameter or local).

        Returns:
          Whether it is.

        """
        return self.kind(name) == _IMPORTED and name in self.module.modules


def declares(function: _Scopes) -> bool:
    """Check whether a function declares anything: a return, a parameter's type, a type comment.

    Returns:
      Whether it does (a lambda never does).

    """
    if isinstance(function, ast.Lambda):
        return False
    if function.type_comment or function.returns is not None:
        return True
    return any(arg.annotation is not None or arg.type_comment for arg in _arguments(function.args))


def _arguments(args: ast.arguments) -> list[ast.arg]:
    """List every parameter.

    Returns:
      Them, `*args` and `**kwargs` included.

    """
    return [
        arg
        for arg in (*args.posonlyargs, *args.args, *args.kwonlyargs, args.vararg, args.kwarg)
        if arg is not None
    ]


def names_in(scope: ast.AST, module: Module) -> Names:
    """Read what a name can mean in `scope`: a function's parameters and locals; else the file's.

    Returns:
      Them.

    """
    if not isinstance(scope, _Scopes):
        return Names(module, {}, frozenset())
    stores: frozenset[str] = frozenset(
        node.id for node in ast.walk(scope) if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Store)
    )
    return Names(module, {arg.arg: arg.annotation is not None for arg in _arguments(scope.args)}, stores)


def origin_of(dotted: str, own: str) -> str:
    """Say where what an import resolves to comes from.

    Returns:
      `stdlib`, `own package` (a relative import, or `own`'s), or `third-party`.

    """
    top: str
    if (top := dotted.split(".", 1)[0]) in {_RELATIVE, own}:
        return _OWN
    return _STDLIB_ORIGIN if _standard(top) else _THIRD_PARTY


@functools.cache
def _standard(top: str) -> bool:
    """Check whether a top-level module ships with Python: named as the standard library's, or found in it.

    Its own tests (`test`, `_testcapi`) aren't in `sys.stdlib_module_names`, but are in its directory.

    Returns:
      Whether it does.

    """
    if top in _STDLIB:
        return True
    spec: importlib.machinery.ModuleSpec | None = (
        importlib.util.find_spec(top) if top.isidentifier() else None
    )
    where: str | None = None if spec is None else spec.origin
    return where is not None and _SITE not in where and any(where.startswith(home) for home in _HOMES)


def _simple(value: ast.expr) -> str | None:
    """Name the shape of a value whose parts don't matter: a literal, display, comprehension, ...

    Returns:
      It, or `None` for one that refers to something (a call, an attribute, a name, ...).

    """
    if type(value) in _NAMED:
        return _NAMED[type(value)]
    if isinstance(value, _COMPREHENSIONS):
        return f"{type(value).__name__} (unknown elements)"
    if isinstance(value, ast.Constant):
        return "None literal" if value.value is None else "other constant"
    if isinstance(value, ast.BoolOp):
        return f"boolop ({type(value.op).__name__.lower()})"
    if isinstance(value, ast.UnaryOp):
        return f"unaryop {type(value.op).__name__}"
    return _display(value)


def _display(value: ast.expr) -> str | None:
    """Name a list, tuple, set or dict display's shape: empty, or of elements `--fix` couldn't type.

    Returns:
      It, or `None` for anything else.

    """
    if type(value) not in _DISPLAYS:
        return None
    kind: str = _DISPLAYS[type(value)]
    elements: Sequence[ast.expr | None] = (
        value.keys if isinstance(value, ast.Dict) else cast("ast.List", value).elts
    )
    return f"{kind} (mixed/unknown elements)" if elements else f"empty {kind}"


def shape(value: ast.expr | None, names: Names) -> _Shape:
    """Classify a value by its shape, and what it resolves to through an import.

    Returns:
      Its shape (`call: self.method()`, `attr: chained`, ...), and the dotted name it resolves to
      (or "").

    """
    if value is None:
        return "no value", ""
    simple: str | None
    if (simple := _simple(value)) is not None:
        return simple, ""
    found: _Shape
    inner: ast.expr
    name: str
    match value:
        case ast.Call():
            found = _call(value, names)
        case ast.Attribute():
            found = _attribute(value, names)
        case ast.Subscript():
            found = (_subscript(value, names), "")
        case ast.Name(id=name):
            found = (_copy(name, names), "")
        case ast.BinOp():
            found = (_binop(value), "")
        case ast.Await(value=inner):
            awaited: _Shape = shape(inner, names)
            found = (f"await: {awaited[0]}", awaited[1])
        case _:
            found = (type(value).__name__, "")
    return found


def _subscript(value: ast.Subscript, names: Names) -> str:
    """Name the shape of a subscript: of a name (by what the name is), or of anything else.

    Returns:
      It.

    """
    name: str
    match value.value:
        case ast.Name(id=name):
            return f"subscript: {names.kind(name)}[...]"
        case _:
            return "subscript: other"


def _copy(name: str, names: Names) -> str:
    """Name the shape of a plain copy of `name`.

    Returns:
      It: `copy: local`, `copy: param (annotated)`, ...

    """
    kind: str
    if (kind := names.kind(name)) != _PARAM:
        return f"copy: {kind}"
    return "copy: param (annotated)" if names.params[name] else "copy: param (unannotated)"


def _binop(value: ast.BinOp) -> str:
    """Name the shape of an arithmetic value `--fix` couldn't type.

    Returns:
      It: `%`-formatting of a literal, one literal side, or neither.

    """
    left: ast.expr = value.left
    if (
        isinstance(value.op, ast.Mod)
        and isinstance(left, ast.Constant)
        and isinstance(left.value, str | bytes)
    ):
        return "binop: literal % formatting"
    if isinstance(left, ast.Constant | ast.JoinedStr) or isinstance(value.right, ast.Constant):
        return "binop (one side literal)"
    return "binop (unknown operands)"


def _attribute(value: ast.Attribute, names: Names) -> _Shape:
    """Classify an attribute read: of a module, of a name (by what the name is), or of anything else.

    Returns:
      Its shape, and what it resolves to (for a module's).

    """
    name: str
    match value.value:
        case ast.Name(id=name) if names.is_module(name):
            return "attr: module.x", names.module.through(name, value.attr)
        case ast.Name(id=name):
            return f"attr: {names.kind(name)}.x", ""
        case _:
            return "attr: chained", ""


def _call(call: ast.Call, names: Names) -> _Shape:
    """Classify a call by its callee.

    Returns:
      Its shape, and what the callee resolves to through an import (or "").

    """
    func: ast.expr = call.func
    name: str
    attr: str
    literal: ast.Constant
    match func:
        case ast.Name(id=name):
            return _named_call(name, names)
        case ast.Attribute(value=ast.Name(id=name), attr=attr):
            return _method_call(name, attr, names)
        case ast.Attribute(value=ast.Constant() as literal):
            return f"call: {type(literal.value).__name__}-literal.method()", ""
        case ast.Attribute(value=ast.JoinedStr()):
            return "call: str-literal.method()", ""
        case ast.Attribute():
            return _chained_call(func, names)
        case _:
            return "call: other callee", ""


def _named_call(name: str, names: Names) -> _Shape:
    """Classify a call to a plain name, by what the name is.

    Returns:
      Its shape, and what it resolves to (for an imported one).

    """
    kind: str = names.kind(name)
    capitalised: bool = name[:1].isupper()
    match kind:
        case "builtin":
            return f"call: builtin {name}()", ""
        case "moddef":
            declared: bool = names.module.defs[name].returns is not None
            return f"call: module function ({'annotated' if declared else 'unannotated'})", ""
        case "modclass":
            return "call: module class", ""
        case "imported":
            return f"call: imported {'class' if capitalised else 'function'}", names.module.through(name)
        case _:
            return ("call: capitalised" if capitalised else f"call: {kind} name"), ""


def _method_call(name: str, attr: str, names: Names) -> _Shape:
    """Classify a call to `name.attr(...)`: a module's function, an imported name's, or a method.

    Returns:
      Its shape, and what it resolves to (through an import).

    """
    kind: str
    if (kind := names.kind(name)) != _IMPORTED:
        return f"call: {kind}.method()", ""
    return (_MODULE_CALL if name in names.module.modules else "call: imported.attr()"), names.module.through(
        name,
        attr,
    )


def _chained_call(func: ast.Attribute, names: Names) -> _Shape:
    """Classify a call through a longer chain: a module's (`os.path.join`), or a method of anything.

    Returns:
      Its shape, and what it resolves to (for a module's).

    """
    root: ast.expr
    attributes: list[str]
    root, attributes = _chain(func.value, [func.attr])
    if isinstance(root, ast.Name) and names.is_module(root.id):
        return _MODULE_CALL, names.module.through(root.id, *attributes)
    return "call: chained .method()", ""


def _chain(node: ast.expr, attributes: list[str]) -> tuple[ast.expr, list[str]]:
    """Follow an attribute chain to its root.

    Returns:
      The root, and the attributes from it, in order.

    """
    value: ast.expr
    attr: str
    match node:
        case ast.Attribute(value=value, attr=attr):
            return _chain(value, [attr, *attributes])
        case _:
            return node, attributes


def binding_of(node: ast.Name, module: Module) -> _Found:
    """Say which statement binds `node`, and with what value.

    Returns:
      Its kind (`assign`, `unpack`, `loop`, `with`, `walrus`, ...), and its value (`None` if none).

    """
    target: ast.AST = _target(node, module)
    unpacked: bool = target is not node
    statement: ast.AST | None = module.parents.get(target)
    found: _Found
    value: ast.expr
    loop: ast.expr
    match statement:
        case ast.Assign(value=value):
            found = ("unpack" if unpacked else "assign", value)
        case ast.AugAssign(value=value):
            found = ("augassign", value)
        case ast.For(target=loop, iter=value) | ast.AsyncFor(target=loop, iter=value) if loop is target:
            found = ("loop", value)
        case ast.withitem(context_expr=value):
            found = ("with-unpack" if unpacked else "with", value)
        case ast.NamedExpr(value=value):
            found = ("walrus", value)
        case ast.comprehension(iter=value):
            found = ("comprehension", value)
        case _:
            found = (f"other:{type(statement).__name__}", None)
    return found


def _target(node: ast.AST, module: Module) -> ast.AST:
    """Find the whole target `node` is part of: itself, or the tuple or list it's unpacked from.

    Returns:
      It.

    """
    parent: ast.AST | None = module.parents.get(node)
    return _target(parent, module) if isinstance(parent, _UNPACKING) else node
