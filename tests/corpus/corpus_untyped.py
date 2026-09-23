# SPDX-License-Identifier: MIT
"""Count what `--fix` still can't type in each corpus, and why: the numbers docs/ROADMAP.md quotes.

  local/.venv/bin/python -m tests.corpus.corpus_untyped                    # every corpus, as Markdown
  local/.venv/bin/python -m tests.corpus.corpus_untyped --top 60           # more categories per table
  local/.venv/bin/python -m tests.corpus.corpus_untyped --rows rows.jsonl  # and every binding, one a line

The corpora are `tests/corpus/corpus_table.py`'s. Each is checked by this checkout at `suffocate`
with `all-scopes` (`--format=json`), and every untyped binding it reports (LVA001, LVA002, LVA004)
is classified from the source: the statement that binds it (`assign`, `unpack`, `loop`, `with`,
`walrus`, ...), the shape of its value (`call: self.method()`, `attr: chained`, `empty list`, ...),
its scope, whether its function declares anything (a module's or class's body counts as annotated
when its file does), whether `--fix` offers a fix (and whether only as a guess), and, for a call or
attribute reached through an import, what it resolves to (`os.path.join`) and where that comes
from: the standard library, the corpus's own package, or a third-party one.

It prints, as Markdown: each corpus's untyped bindings, those with no fix at all, and how many of
those are in functions with no annotations; the commonest shapes with no fix in annotated
functions, in unannotated ones, and at module level; the groups the roadmap's items are sized by;
and calls through an import, by where it comes from. Files that don't parse as
Python 3 (Twisted's Python 2) are left out, their count on standard error.
"""

import argparse
import ast
import builtins
import functools
import importlib.machinery
import importlib.util
import json
import re
import subprocess  # runs this checkout's constricter on each corpus
import sys
import sysconfig
import tokenize
import warnings
from collections import Counter
from collections.abc import Callable, Iterable, Mapping, Sequence
from pathlib import Path
from typing import Final, NamedTuple, TextIO, TypeAlias, cast

from tests.corpus.corpus_table import WORK, Corpus, corpora

_Json: TypeAlias = "str | int | bool | list[_Json] | dict[str, _Json] | None"
_Result: TypeAlias = dict[str, _Json]
_Shape: TypeAlias = tuple[str, str]  # a value's shape, and what it resolves to through an import
_Scopes: TypeAlias = ast.FunctionDef | ast.AsyncFunctionDef | ast.Lambda
_Found: TypeAlias = tuple[str, ast.expr | None]  # a binding's statement kind, and its value
_ByNode: TypeAlias = Mapping[type[ast.expr], str]  # a name for each kind of node
_Groups: TypeAlias = Mapping[str, frozenset[str]]  # each group's label, and the shapes in it
_Kinds: TypeAlias = tuple[tuple[str, Iterable[str]], ...]  # each kind of name, and the names of it
_Section: TypeAlias = tuple[str, list[str]]  # a heading, and the lines under it

_CODES: Final = frozenset({"LVA001", "LVA002", "LVA004"})
# How this checkout's constricter checks each corpus (its warnings about the corpus's own code, off).
_CHECK: Final = ("-W", "ignore", "-m", "constricter", "--format=json", "--level=suffocate")
_EVERYWHERE: Final = ("--all-scopes", "--jobs=0")
_NAME: Final = re.compile(r"'([^']+)'")
_BUILTINS: Final = frozenset(dir(builtins))
_STDLIB: Final = frozenset(sys.stdlib_module_names)
_HOMES: Final = frozenset({sysconfig.get_paths()["stdlib"], sysconfig.get_paths()["platstdlib"]})
_SITE: Final = "site-packages"  # installed packages, under the standard library's directory on some systems
_RELATIVE: Final = "<relative>"
_SELVES: Final = frozenset({"self", "cls"})
_PARAM: Final = "param"
_IMPORTED: Final = "imported"
_FUNCTION: Final = "function"
_MODULE: Final = "module"
_NOT_A_NAME: Final = "other (not a Name store)"
_UNKNOWN: Final = "?"
_STDLIB_ORIGIN: Final = "stdlib"
_OWN: Final = "own package"
_THIRD_PARTY: Final = "third-party"
_MODULE_CALL: Final = "call: module.func()"
_TOP: Final = 30
_TOP_MODULES: Final = 8
_SOURCE_WIDTH: Final = 120  # how much of a value's source a row keeps
# Shapes whose name says it all, whatever the value's parts.
_NAMED: Final[_ByNode] = {ast.IfExp: "conditional", ast.Compare: "compare"}
_DISPLAYS: Final[_ByNode] = {ast.List: "list", ast.Tuple: "tuple", ast.Set: "set", ast.Dict: "dict"}
_COMPREHENSIONS: Final = (ast.ListComp, ast.SetComp, ast.DictComp, ast.GeneratorExp)
_UNPACKING: Final = (ast.Tuple, ast.List, ast.Starred)
# A call to a name an import binds: `f()` after `from m import f`, or `f.g()`.
_IMPORTS: Final = frozenset({"call: imported function", "call: imported class", "call: imported.attr()"})
# The groups the roadmap's items are sized by, each a set of shapes (whatever the statement).
_GROUPS: Final[_Groups] = {
    "`self.x` read": frozenset({"attr: self.x"}),
    "`self.method()` call": frozenset({"call: self.method()"}),
    "Chained `.method()` call": frozenset({"call: chained .method()"}),
    "Call to an imported function or class": _IMPORTS,
    "`module.func()` call": frozenset({_MODULE_CALL}),
    "`getattr(...)`": frozenset({"call: builtin getattr()"}),
    "Empty container": frozenset({"empty list", "empty dict", "empty set"}),
    "Comprehension of unknown elements": frozenset(
        {f"{kind.__name__} (unknown elements)" for kind in _COMPREHENSIONS},
    ),
}


class Binding(NamedTuple):
    """One untyped binding, classified: what `--rows` writes a line of."""

    corpus: str
    path: str  # relative to the corpus's root
    line: int
    name: str
    code: str
    fixed: bool  # `--fix` offers a fix, certain or a guess
    unsafe: bool  # only as a guess
    scope: str  # `function`, `class`, `module`, or `?` when it isn't a plain name's binding
    annotated: bool  # its function declares something (a body outside one: its file does)
    binding: str  # the statement that binds it
    shape: str  # its value's
    dotted: str  # what a call or attribute resolves to through an import (`os.path.join`), or ""
    origin: str  # where that comes from: `stdlib`, `own package`, `third-party`, or ""
    source: str  # the value's source, cut short


class _Module:
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
            _declares(node)
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


class _Names(NamedTuple):
    """What a name means in one scope: its parameters (and whether each is annotated), locals, file."""

    module: _Module
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


def _declares(function: _Scopes) -> bool:
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


def _names(scope: ast.AST, module: _Module) -> _Names:
    """Read what a name can mean in `scope`: a function's parameters and locals; else the file's.

    Returns:
      Them.

    """
    if not isinstance(scope, _Scopes):
        return _Names(module, {}, frozenset())
    stores: frozenset[str] = frozenset(
        node.id for node in ast.walk(scope) if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Store)
    )
    return _Names(module, {arg.arg: arg.annotation is not None for arg in _arguments(scope.args)}, stores)


def _origin(dotted: str, own: str) -> str:
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


def shape(value: ast.expr | None, names: _Names) -> _Shape:
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


def _subscript(value: ast.Subscript, names: _Names) -> str:
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


def _copy(name: str, names: _Names) -> str:
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


def _attribute(value: ast.Attribute, names: _Names) -> _Shape:
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


def _call(call: ast.Call, names: _Names) -> _Shape:
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


def _named_call(name: str, names: _Names) -> _Shape:
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


def _method_call(name: str, attr: str, names: _Names) -> _Shape:
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


def _chained_call(func: ast.Attribute, names: _Names) -> _Shape:
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


def _binding(node: ast.Name, module: _Module) -> _Found:
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


def _target(node: ast.AST, module: _Module) -> ast.AST:
    """Find the whole target `node` is part of: itself, or the tuple or list it's unpacked from.

    Returns:
      It.

    """
    parent: ast.AST | None = module.parents.get(node)
    return _target(parent, module) if isinstance(parent, _UNPACKING) else node


def _read(path: Path) -> ast.Module | None:
    """Parse a file as the check did, with type comments if they parse.

    Returns:
      Its tree, or `None` if it doesn't parse as Python 3 (or can't be read).

    """
    try:
        source: str = _source(path)
    except (SyntaxError, UnicodeDecodeError, OSError):
        return None
    return _parsed(source, type_comments=True) or _parsed(source, type_comments=False)


def _parsed(source: str, *, type_comments: bool) -> ast.Module | None:
    """Parse source quietly: an old file's invalid escape sequences only warn.

    Returns:
      Its tree, or `None` if it doesn't parse.

    """
    with warnings.catch_warnings(action="ignore"):
        try:
            return ast.parse(source, type_comments=type_comments)
        except SyntaxError:
            return None


def _source(path: Path) -> str:
    """Read a file's source in the encoding it declares (PEP 263, or a BOM).

    Returns:
      It.

    """
    file: TextIO
    with tokenize.open(path) as file:
        return file.read()


class _File(NamedTuple):
    """One parsed file of a corpus, and what's needed to classify its untyped bindings."""

    corpus: Corpus
    path: Path
    module: _Module
    stores: Mapping[tuple[int, int, str], ast.Name]  # each name's first store, by line and column (from 1)


def _file(corpus: Corpus, path: Path) -> _File | None:
    """Read one file of a corpus.

    Returns:
      It, or `None` if it doesn't parse.

    """
    tree: ast.Module | None
    if (tree := _read(path)) is None:
        return None
    stores: dict[tuple[int, int, str], ast.Name] = {}
    node: ast.AST
    for node in ast.walk(tree):
        if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Store):
            _ = stores.setdefault((node.lineno, node.col_offset + 1, node.id), node)
    return _File(corpus, path, _Module(tree), stores)


class _Description(NamedTuple):
    """`Binding`'s fields from `scope` on: how one binding was classified."""

    scope: str
    annotated: bool
    binding: str
    shape: str
    dotted: str
    origin: str
    source: str


def _classified(file: _File, result: _Result, scopes: dict[int, tuple[str, bool, _Names]]) -> Binding:
    """Classify one untyped binding the check reported in `file`.

    `scopes` caches each scope's kind, whether it's annotated, and its names, by the scope's `id`.

    Returns:
      It.

    """
    found: re.Match[str] | None = _NAME.search(str(result["message"]))
    name: str = found.group(1) if found else _UNKNOWN
    fix: _Result | None = cast("_Result | None", result["fix"])
    line: int = cast("int", result["line"])
    node: ast.Name | None = file.stores.get((line, cast("int", result["column"]), name))
    described: _Description = (
        _Description(_UNKNOWN, file.module.annotated, _NOT_A_NAME, "-", "", "", "")
        if node is None
        else _described(node, file, scopes)
    )
    return Binding(
        file.corpus.name,
        str(file.path.relative_to(file.corpus.root)),
        line,
        name,
        str(result["code"]),
        fix is not None,
        fix is not None and bool(fix["unsafe"]),
        *described,
    )


def _described(
    node: ast.Name,
    file: _File,
    scopes: dict[int, tuple[str, bool, _Names]],
) -> _Description:
    """Describe the binding of `node`: its scope, statement, value and what that resolves to.

    Returns:
      It.

    """
    scope: ast.AST | None = file.module.scope(node)
    if id(scope) not in scopes:
        scopes[id(scope)] = _scope(scope, file.module)
    kind: str
    annotated: bool
    names: _Names
    kind, annotated, names = scopes[id(scope)]
    binding: str
    value: ast.expr | None
    binding, value = _binding(node, file.module)
    value_shape: str
    dotted: str
    value_shape, dotted = shape(value, names)
    return _Description(
        kind,
        annotated,
        binding,
        value_shape,
        dotted,
        _origin(dotted, file.corpus.name) if dotted else "",
        "" if value is None else ast.unparse(value)[:_SOURCE_WIDTH],
    )


def _scope(scope: ast.AST | None, module: _Module) -> tuple[str, bool, _Names]:
    """Describe a scope: its kind, whether it's annotated, and what a name in it can mean.

    Returns:
      `function` (and whether it declares anything), `class` or `module` (and whether its file
      does), and its names.

    """
    if isinstance(scope, _Scopes):
        return _FUNCTION, _declares(scope), _names(scope, module)
    kind: str = "class" if isinstance(scope, ast.ClassDef) else _MODULE
    return kind, module.annotated, _Names(module, {}, frozenset())


def census(corpus: Corpus) -> tuple[list[Binding], int]:
    """Check one corpus with this checkout and classify every untyped binding it reports.

    Returns:
      The bindings, and how many reported ones were in files that don't parse (left out).

    """
    # From `WORK`, where no `pyproject.toml` configures it. It exits 2, saying why, for a file it
    # can't read (the standard library's tests have some; Twisted's Python 2): the report has the rest.
    output: str = subprocess.run(
        [sys.executable, *_CHECK, *_EVERYWHERE, str(corpus.root)],
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        check=False,
        cwd=WORK,
        encoding="utf-8",
    ).stdout
    results: list[_Result] = [
        result for result in cast("list[_Result]", json.loads(output or "[]")) if result["code"] in _CODES
    ]
    by_path: dict[str, list[_Result]] = {}
    result: _Result
    for result in results:
        by_path.setdefault(str(result["path"]), []).append(result)
    bindings: list[Binding] = []
    unparsed: int = 0
    path: str
    reported: list[_Result]
    for path, reported in sorted(by_path.items()):
        file: _File | None
        if (file := _file(corpus, Path(path))) is None:
            unparsed += len(reported)
            continue
        scopes: dict[int, tuple[str, bool, _Names]] = {}
        bindings.extend(_classified(file, one, scopes) for one in reported)
    return bindings, unparsed


def _share(part: int, whole: int) -> str:
    """Write `part` with its percentage of `whole`.

    Returns:
      It, as `1,234 (5.6%)`.

    """
    return f"{part:,} ({part / whole:.1%})" if whole else f"{part:,}"


def _table(header: Sequence[str], rows: Iterable[Sequence[str]]) -> list[str]:
    """Lay a table out as Markdown, its first column left-aligned and the rest right-aligned.

    Returns:
      Its lines.

    """
    every: list[Sequence[str]] = [header, *rows]
    widths: list[int] = [max(3, *(len(row[i]) for row in every)) for i in range(len(header))]

    def line(row: Sequence[str]) -> str:
        return (
            "| "
            + " | ".join(
                cell.ljust(widths[i]) if not i else cell.rjust(widths[i]) for i, cell in enumerate(row)
            )
            + " |"
        )

    separator: list[str] = ["-" * widths[0], *("-" * (w - 1) + ":" for w in widths[1:])]
    return [line(header), "| " + " | ".join(separator) + " |", *(line(row) for row in every[1:])]


def _ranked(counts: Counter[str], top: int) -> list[tuple[str, int]]:
    """Rank counts, largest first, ties by name, so the tables don't vary from run to run.

    Returns:
      The first `top`.

    """
    return sorted(counts.items(), key=lambda item: (-item[1], item[0]))[:top]


def _totals(bindings: Sequence[Binding], corpora_seen: Sequence[str]) -> list[str]:
    """Tabulate each corpus's untyped bindings, those with no fix, and those in unannotated functions.

    Returns:
      The table's lines.

    """

    def row(name: str, of: Sequence[Binding]) -> list[str]:
        missed: list[Binding] = [b for b in of if not b.fixed]
        bare: int = sum(b.scope == _FUNCTION and not b.annotated for b in missed)
        return [name, f"{len(of):,}", _share(len(missed), len(of)), _share(bare, len(missed))]

    return _table(
        ["Corpus", "Untyped", "No fix", "No fix, in a function with no annotations"],
        [
            *(row(name, [b for b in bindings if b.corpus == name]) for name in corpora_seen),
            row("**Total**", bindings),
        ],
    )


def _shapes(missed: Sequence[Binding], keep: Callable[[Binding], bool], top: int) -> list[str]:
    """Tabulate the commonest `binding: shape` among the bindings with no fix that `keep` selects.

    Returns:
      The table's lines, headed by how many there are.

    """
    counts: Counter[str] = Counter(f"{b.binding}: {b.shape}" for b in missed if keep(b))
    total: int = counts.total()
    return [
        f"{total:,} bindings; the {min(top, len(counts))} commonest shapes:",
        "",
        *_table(
            ["Binding: value", "Count", "Share"],
            [[key, f"{count:,}", f"{count / total:.1%}"] for key, count in _ranked(counts, top)],
        ),
    ]


def _groups(missed: Sequence[Binding]) -> list[str]:
    """Tabulate the groups the roadmap's items are sized by, whatever statement binds them.

    Returns:
      The table's lines.

    """
    rows: list[list[str]] = []
    label: str
    shapes: frozenset[str]
    for label, shapes in _GROUPS.items():
        members: list[Binding] = [b for b in missed if b.shape in shapes]
        in_annotated: int = sum(b.scope == _FUNCTION and b.annotated for b in members)
        rows.append([label, f"{len(members):,}", f"{in_annotated:,}"])
    return _table(["No fix, by what the value is", "All", "In annotated functions"], rows)


def _origins(calls: Sequence[Binding]) -> list[str]:
    """Tabulate calls through an import by where the import comes from, and which modules.

    Returns:
      The table's lines.

    """
    rows: list[list[str]] = []
    origin: str
    for origin in (_STDLIB_ORIGIN, _OWN, _THIRD_PARTY):
        mine: list[Binding] = [b for b in calls if b.origin == origin]
        # A third-party package by its top level; anything else by the module itself.
        modules: Counter[str] = Counter(
            b.dotted.split(".", 1)[0] if origin == _THIRD_PARTY else b.dotted.rsplit(".", 1)[0] for b in mine
        )
        common: str = ", ".join(f"`{name}` {count:,}" for name, count in _ranked(modules, _TOP_MODULES))
        rows.append([origin, f"{len(mine):,}", common])
    return _table(["Module from", "Calls", "Commonest modules"], rows)


def _imports(missed: Sequence[Binding], top: int) -> list[str]:
    """Tabulate the calls with no fix that go through an import, by where it comes from.

    Returns:
      The lines: `module.func()` calls, calls to an imported name, then the standard library's
      commonest functions among both.

    """
    through_modules: list[Binding] = [b for b in missed if b.shape == _MODULE_CALL]
    through_names: list[Binding] = [b for b in missed if b.shape in _IMPORTS]
    functions: Counter[str] = Counter(
        b.dotted for b in (*through_modules, *through_names) if b.origin == _STDLIB_ORIGIN
    )
    return [
        "Through a module an `import` binds (`os.path.join(...)`, `np.array(...)`):",
        "",
        *_origins(through_modules),
        "",
        "Through a name imported from a module (`join(...)` after `from os.path import join`):",
        "",
        *_origins(through_names),
        "",
        "The standard library's commonest functions among both:",
        "",
        *_table(
            ["Function", "Calls"],
            [[f"`{name}`", f"{count:,}"] for name, count in _ranked(functions, top)],
        ),
    ]


def report(bindings: Sequence[Binding], corpora_seen: Sequence[str], top: int = _TOP) -> str:
    """Write the census as Markdown.

    Returns:
      Its sections, each a heading and a table.

    """
    missed: list[Binding] = [b for b in bindings if not b.fixed]
    sections: list[_Section] = [
        ("Untyped bindings, and those `--fix` offers nothing for", _totals(bindings, corpora_seen)),
        (
            "No fix, in functions that declare something",
            _shapes(missed, lambda b: b.scope == _FUNCTION and b.annotated, top),
        ),
        (
            "No fix, in functions that declare nothing",
            _shapes(missed, lambda b: b.scope == _FUNCTION and not b.annotated, top),
        ),
        ("No fix, in a module's body", _shapes(missed, lambda b: b.scope == _MODULE, top)),
        ("No fix, by group", _groups(missed)),
        ("Calls with no fix through an import, by where it comes from", _imports(missed, top)),
    ]
    return "\n".join(f"## {heading}\n\n" + "\n".join(lines) + "\n" for heading, lines in sections)


def main(argv: Sequence[str] | None = None) -> int:
    """Take the census of every corpus and print it (writing every binding, with `--rows`).

    Returns:
      0.

    """
    parser: argparse.ArgumentParser = argparse.ArgumentParser(description="What `--fix` can't type, and why.")
    _ = parser.add_argument("--top", type=int, default=_TOP, help="categories per table (30)")
    _ = parser.add_argument("--rows", type=Path, help="also write every binding to this file, as JSON lines")
    options: argparse.Namespace = parser.parse_args(argv)
    WORK.mkdir(parents=True, exist_ok=True)
    bindings: list[Binding] = []
    seen: list[str] = []
    corpus: Corpus
    for corpus in corpora():
        found: list[Binding]
        unparsed: int
        found, unparsed = census(corpus)
        bindings.extend(found)
        seen.append(corpus.name)
        _ = sys.stderr.write(
            f"{corpus.name}: {len(found):,} untyped ({unparsed:,} in files that don't parse)\n",
        )
    rows: Path | None
    if (rows := cast("Path | None", options.rows)) is not None:
        _ = rows.write_text("".join(json.dumps(b._asdict()) + "\n" for b in bindings), encoding="utf-8")
    _ = sys.stdout.write(report(bindings, seen, cast("int", options.top)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
