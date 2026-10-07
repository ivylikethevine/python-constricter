# SPDX-License-Identifier: MIT
"""What each checked file offers other files' `--fix`, read once: the cross-file index (`index`).

`read` takes a file's module name, its top-level functions' declared return types (as
`annotations.returns` picks them), its classes' attributes and methods' returns (as `classes` and
`method_returns` do), its generic classes and type variables, and what each top-level name refers
to; `constricter.fix.index.project` looks things up in it for each file.
"""

import ast
import bisect
import itertools
import re
from collections import Counter
from collections.abc import Iterable, Iterator, Mapping, Sequence
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path
from types import MappingProxyType
from typing import Final, NamedTuple, TypeAlias, cast

from constricter.fix.core.imports import taken_names
from constricter.fix.core.known import Origin, Passed, Returns
from constricter.fix.core.signatures import AWAIT
from constricter.fix.index.declared import Declarations, Signature, declarations, overloads
from constricter.fix.values import classvars
from constricter.fix.values.returned import unannotated, yields_itself
from constricter.rules import parsed
from constricter.rules.annotations import (
    awaited_returns,
    defined_type_vars,
    dotted,
    generic_classes,
    is_composite,
    key,
    node_name,
)
from constricter.rules.decorators import Held, Pass, is_fixture
from constricter.rules.syntax import child_statements, top_level
from constricter.rules.tables import Tables, module_tables
from constricter.rules.walked import classes as walked_classes
from constricter.rules.walked import of_type

_PACKAGE: Final = "__init__"
_TYPE_ALIAS: Final = "TypeAlias"  # the annotation, and the node class of `type X = ...` (Python 3.12+)
# What a type checker decides an `if` by, taking one arm alone: `sys.version_info`, `TYPE_CHECKING`.
_DECIDED: Final = frozenset({"version_info", "platform", "TYPE_CHECKING"})
SUFFIX: Final = ".py"
CONFTEST: Final = "conftest"  # the module pytest reads a directory's fixtures from
_UNNAMED: Final = frozenset({"__call__", "__enter__"})  # members a statement takes without naming them
_GET: Final = "get"
_CLASS: Final = "class"  # `project.CLASS`: the kind of name `classes_under` spells, with an alias
_ANNOTATION: Final = 200  # the longest string read for the names a type in it is written with
_DOTTED: Final = re.compile(r"[A-Za-z_]\w*(?:\.[A-Za-z_]\w*)+")
STUB: Final = ".pyi"


# A function's parameter: its name, kind (`p` positional only, `e` either, `k` keyword only), and
# whether it has a default and an annotation.
Param: TypeAlias = tuple[str, str, bool, bool]
_POSITIONAL: Final = "p"
_EITHER: Final = "e"
_KEYWORD: Final = "k"


class Module(NamedTuple):
    """What one file offers and uses: its name, functions' return types, names' origins, and classes'.

    `classes` and `methods`: each class's attributes and its methods' returns (see `Classes`), those
    it takes from the file's other classes too (see `Lineage`).
    """

    name: str
    returns: dict[str, str]
    names: dict[str, Origin]
    classes: Mapping[str, Mapping[str, str]] = MappingProxyType({})
    methods: Mapping[str, Mapping[str, str]] = MappingProxyType({})
    type_vars: frozenset[str] = frozenset()  # its module-level type variables
    # What it imports under a top-level `if` or `try` (`if TYPE_CHECKING:`), for `type_vars` alone.
    guarded: Mapping[str, Origin] = MappingProxyType({})
    unannotated: frozenset[str] = frozenset()  # its functions a `return` could type (`returned`)
    called: frozenset[str] = frozenset()  # what it calls through its top-level names (`f`, `u.f`)
    passed: frozenset[str] = frozenset()  # what it passes as an argument through them (`np.float64`)
    method_calls: frozenset[str] = frozenset()  # the methods it calls on anything (`astype` in `a.astype(x)`)
    attributes: frozenset[str] = frozenset()  # every attribute it reads or calls, of anything (`x` in `a.x`)
    returned: Returns = Returns()  # what they return, once it's checked
    generics: frozenset[str] = frozenset()  # its generic classes, which a type mustn't write bare
    installed: bool = False  # an installed package's, read for its types alone (see `installed`)
    # Its plain top-level functions with a parameter left unannotated (see `open_functions`), and
    # what every call passes each such parameter, once they're all seen (see `callers`). Plain
    # `dict`s: the CLI's worker processes send modules back, pickled.
    open: Mapping[str, tuple[Param, ...]] = {}
    parameters: Mapping[str, Mapping[str, Passed]] = {}  # see `Seeds`
    declared: Declarations | None = None  # an installed module's, for its overloads (see `declared`)
    # Its functions declaring a return under decorators other modules may vouch for, each with those
    # decorators as written, and its own decorators that give a function back (see `decorators`).
    held: Mapping[str, Held] = {}
    passes: Mapping[str, Pass] = {}
    vouched: frozenset[str] = frozenset()  # those of `held` they vouched for, now among `returns`
    aliases: Mapping[
        str,
        bool,
    ] = {}  # its type aliases, and whether each takes type arguments (see `_aliases`)
    # The names its top level assigns twice or more (see `_assigned`): variables, to a type checker.
    rebound: frozenset[str] = frozenset()
    # Its top-level names something in it binds as a value too (a local `m`, under `import pkg.m as m`).
    shadowed: frozenset[str] = frozenset()
    # Its classes' bases as written, their variables typed by their values, and which of them are
    # plain, once the index settles it (see `constricter.fix.values.classvars`, `plain.settled`).
    bases: Mapping[str, tuple[str, ...]] = {}
    bound: Mapping[str, frozenset[str]] = {}  # the names each of its classes' bodies binds
    members: Mapping[str, Mapping[str, str]] = {}
    plain: frozenset[str] = frozenset()
    # Its classes' classmethods' and staticmethods' declared returns (see `annotations.class_methods`);
    # those held back as `held` are, and those of them the index vouched for, now among `sides`.
    sides: Mapping[str, Mapping[str, str]] = {}
    held_sides: Mapping[str, Mapping[str, Held]] = {}
    vouched_sides: frozenset[tuple[str, str]] = frozenset()
    # Its functions' and classes' methods' declared returns that are tuples with a vague part, which
    # only an unpacking can use (see `known.Partial`): the methods as `methods` has them.
    partial: Mapping[str, str] = {}
    partial_methods: Mapping[str, Mapping[str, str]] = {}
    tuples: Mapping[str, str] = {}  # its named tuples' fields (see `targets.named_tuples`)
    # Its top-level pytest fixtures, and whether each is a generator (its value is what it yields).
    fixtures: Mapping[str, bool] = {}
    # A checked file's functions defined with `@overload`, each with its overloads' signatures.
    overloads: Mapping[str, tuple[Signature, ...]] = {}
    folder: str = ""  # a checked file's directory: where pytest looks for the `conftest.py`s above it
    # Its classes' methods a `return` could type (as `unannotated`), by name, whatever the class.
    loose: frozenset[str] = frozenset()
    # Its classes' methods declared to return a bare `Self` (see `annotations.self_returns`).
    selfish: Mapping[str, frozenset[str]] = {}
    awaits: Mapping[str, str] = {}  # what awaiting each of its `async def`s' calls gives (`awaited_returns`)
    # The dotted names a checked file writes (`u.helper`, `pkg.m.Row`, in a string too), by their
    # first name: of all a module it imports has, what it can mean (see `written_under`).
    written: Mapping[str, tuple[str, ...]] = {}


# The classes a module names by its own imports: each one's spelling, its module and its name
# there; and the generic ones it spells through a module.
_Spelled: TypeAlias = tuple[list[tuple[str, str, str]], list[str]]
_Under: TypeAlias = list[tuple[str, Origin]]  # classes' spellings after a package's name, and what each is


@dataclass
class Memo:
    """What's worked out once of an index's classes, for every file that asks.

    Which classes its modules define, what they're named by and their bases don't change as the
    files are checked (what their functions return does): what follows from those alone is kept
    here, by the index that has it and each one made from it with the same modules.
    """

    # A package's and its submodules' classes or aliases: each one's spelling after the package's
    # name, and what it is, by the package and the kind.
    under: dict[tuple[str, str], _Under] = field(default_factory=dict)
    # What a module names (see `_Spelled`), by its name and folder.
    spelled: dict[tuple[str, str], _Spelled] = field(default_factory=dict)
    # A class's line of bases (see `own_types.lineages`), by its path.
    lines: dict[str, tuple[str, ...]] = field(default_factory=dict)
    # The members a class declares a type for (attributes, methods' returns), by its module and name.
    members: dict[tuple[str, str], frozenset[str]] = field(default_factory=dict)


class Index(NamedTuple):
    """Every checked file's module, and their names sorted for a module/submodule lookup."""

    modules: dict[str, Module]
    names: list[str]  # modules, sorted by name
    repeated: frozenset[str] = frozenset()  # the names more than one file has: `modules` has the last
    # Each checked `conftest.py` outside any package, by its directory: several share the one name.
    conftests: Mapping[str, Module] = {}
    memo: Memo | None = None  # `None`: nothing is kept (an index made by hand)


@lru_cache(maxsize=65536)  # asked of each checked file a dozen times: its folders are looked at once
def module_name(path: Path) -> str:
    """Name `path`'s module: its package folders (those with an `__init__.py`), then it.

    Returns:
      The dotted module name.

    """
    packages: list[Path] = list(
        itertools.takewhile(
            lambda folder: (folder / f"{_PACKAGE}{SUFFIX}").is_file(),
            path.resolve().parents,
        ),
    )
    return ".".join(
        [*(folder.name for folder in reversed(packages)), *([] if path.stem == _PACKAGE else [path.stem])],
    )


def absolute(name: str, module: str | None, level: int, *, is_package: bool) -> str:
    """Resolve `from <.level><module> import ...` in module `name`.

    Returns:
      The absolute module name.

    """
    if not level:
        return module or ""
    package: list[str] = name.split(".") if is_package else name.split(".")[:-1]
    base: list[str] = package[: len(package) - (level - 1)] if level > 1 else package
    return ".".join([*base, *([module] if module else [])])


def _names(tree: ast.Module, name: str, *, is_package: bool) -> dict[str, Origin]:
    """Map module `name`'s top-level names (the last binding wins).

    Returns:
      What each refers to.

    """
    names: dict[str, Origin] = {}
    stmt: ast.stmt
    for stmt in tree.body:
        match stmt:
            case ast.Import() | ast.ImportFrom():
                names.update(_imported(stmt, name, is_package=is_package))
            case _:
                names.update((bound, (name, bound)) for bound in _bound(stmt))
    return names


def _imported(stmt: ast.Import | ast.ImportFrom, name: str, *, is_package: bool) -> dict[str, Origin]:
    """Map the names one import in module `name` binds.

    Returns:
      What each refers to.

    """
    names: dict[str, Origin] = {}
    alias: ast.alias
    if isinstance(stmt, ast.Import):
        for alias in stmt.names:
            if alias.asname:
                names[alias.asname] = (alias.name, None)
            else:  # `import a.b` binds `a`
                names[alias.name.split(".")[0]] = (alias.name.split(".")[0], None)
        return names
    for alias in stmt.names:
        names[alias.asname or alias.name] = (
            absolute(name, stmt.module, stmt.level, is_package=is_package),
            alias.name,
        )
    return names


def _guarded(tree: ast.Module, name: str, *, is_package: bool) -> dict[str, Origin]:
    """Map the names module `name` imports under a top-level `if` or `try` (`if TYPE_CHECKING:`).

    Not what it binds at run time (`_names`): a type variable imported only for the checker is a type
    variable all the same.

    Returns:
      What each refers to.

    """
    return {
        bound: origin
        for stmt in tree.body
        if isinstance(stmt, ast.If | ast.Try | ast.TryStar)
        for node in ast.walk(stmt)
        if isinstance(node, ast.Import | ast.ImportFrom)
        for bound, origin in _imported(node, name, is_package=is_package).items()
    }


def _bound(stmt: ast.stmt) -> Iterator[str]:
    """Walk a top-level statement other than an import.

    Yields:
      Each name it binds.

    """
    node: ast.AST
    match stmt:
        case ast.FunctionDef() | ast.AsyncFunctionDef() | ast.ClassDef():
            yield stmt.name
        case ast.Assign() | ast.AnnAssign() | ast.AugAssign():
            targets: list[ast.expr] = stmt.targets if isinstance(stmt, ast.Assign) else [stmt.target]
            for node in (n for target in targets for n in ast.walk(target)):
                if isinstance(node, ast.Name):
                    yield node.id
        case _:
            pass


def index(paths: Sequence[Path]) -> Index:
    """Read each `.py` file in `paths` (one that can't be read or parsed is left out).

    Returns:
      Each module's name, mapped to what it offers and uses.

    """
    return indexed(read(path) for path in paths)


def indexed(found: Iterable[Module | None]) -> Index:
    """Index modules already read (`read`'s, in any process): `None`s, for files it couldn't, left out.

    Returns:
      Each module's name, mapped to what it offers and uses.

    """
    counts: Counter[str] = Counter()
    modules: dict[str, Module] = {}
    conftests: dict[str, Module] = {}
    module: Module | None
    for module in found:
        if module is not None:
            counts[module.name] += 1
            modules[module.name] = module
            if module.name == CONFTEST and module.folder:
                conftests[module.folder] = module
    repeated: frozenset[str] = frozenset(name for name, count in counts.items() if count > 1)
    return Index(modules, sorted(modules), repeated, conftests, Memo())


def read(path: Path, name: str | None = None) -> Module | None:
    """Read what one `.py` file offers and uses.

    With `name`, an installed package's module (see `installed`): a stub (`.pyi`) too, named that,
    and not kept for a check.

    Returns:
      Its module, or `None` if it isn't a `.py` file, or can't be read or parsed.

    """
    if path.suffix not in ({SUFFIX} if name is None else {SUFFIX, STUB}) or not path.is_file():
        return None
    source: str | None
    if (source := _source(path)) is None:
        return None
    try:
        tree: ast.Module = parsed.parse(source, str(path))
    except (SyntaxError, ValueError):  # a null byte is a ValueError
        return None
    own: Tables = module_tables(tree)
    rebound: frozenset[str] = frozenset(bound for bound, count in _assigned(tree.body).items() if count > 1)
    if name is None:
        parsed.keep(source, (tree, own))  # for the check to take, rather than parse it and read it again
    named: str = name or module_name(path)
    names: dict[str, Origin] = _names(tree, named, is_package=path.stem == _PACKAGE)
    return Module(
        named,
        own.returns,
        names,
        own.classes,
        own.order.flattened(own.methods),
        defined_type_vars(tree),
        _guarded(tree, named, is_package=path.stem == _PACKAGE),
        unannotated(tree.body),
        _called(tree, names),
        generics=generic_classes(tree),
        loose=frozenset().union(*(unannotated(node.body) for node in walked_classes(tree))),
        selfish=dict(own.order.selfish),
        awaits=awaited_returns(tree),
        written={} if name is not None else _written(tree),
        passed=frozenset() if name is not None else _passed(tree, names),
        method_calls=frozenset() if name is not None else _method_calls(tree),
        attributes=frozenset() if name is not None else _attributes(tree),
        installed=name is not None,
        open=open_functions(tree),
        declared=None if name is None else declarations(tree),
        held=own.held,
        passes=own.passes,
        aliases={alias: generic for alias, generic in _aliases(tree).items() if alias not in rebound},
        rebound=rebound,
        shadowed=frozenset(names) & taken_names(tree)[1] if name is None else frozenset(),
        bases={} if name is not None else classvars.bases(tree),
        bound=dict(own.order.bound),
        members={} if name is not None else classvars.members(tree),
        sides=own.sides,
        held_sides=own.held_sides,
        partial=own.partial,
        partial_methods=own.order.flattened(own.partial_methods),
        tuples=own.tuples,
        fixtures=_fixtures(tree),
        overloads={} if name is not None else overloads(tree),
        folder="" if name is not None else str(path.resolve().parent),
    )


def _written(tree: ast.Module) -> dict[str, tuple[str, ...]]:
    """Find the dotted names a module writes: each attribute chain on a name, and those its strings hold.

    A string's (an annotation in quotes, a `cast`'s target) and a type comment's count: a type may
    be written in either.

    Returns:
      Them, sorted, by their first name; each chain's own beginnings too (`pkg.m`, of `pkg.m.Row`).

    """
    found: set[str] = set()
    node: ast.AST
    for node in of_type(tree, ast.Attribute):
        text: str | None
        if (text := dotted(cast("ast.Attribute", node))) is not None:
            found.add(text)
    texts: list[str] = [
        node.value
        for node in cast("list[ast.Constant]", of_type(tree, ast.Constant))
        if isinstance(node.value, str) and len(node.value) <= _ANNOTATION
    ]
    texts.extend(
        cast("str | None", getattr(node, "type_comment", None)) or ""
        for kind in (ast.FunctionDef, ast.AsyncFunctionDef, ast.Assign, ast.For, ast.With, ast.arg)
        for node in of_type(tree, kind)
    )
    chain: str
    for chain in cast("list[str]", _DOTTED.findall("\n".join(texts))):
        parts: list[str] = chain.split(".")
        found.update(".".join(parts[:count]) for count in range(2, len(parts) + 1))
    grouped: dict[str, list[str]] = {}
    for chain in sorted(found):
        grouped.setdefault(chain.partition(".")[0], []).append(chain)
    return {root: tuple(chains) for root, chains in grouped.items()}


def written_under(target: Module, local: str) -> Iterator[tuple[str, str, str]]:
    """Find the names `target` writes under `local`, a module it imports (`u.helper`, `pkg.util.helper`).

    Yields:
      Each one, the submodule it's written through (`""`, or `.util`), and its last name.

    """
    prefix: str = f"{local}."
    chain: str
    for chain in target.written.get(local.partition(".")[0], ()):
        if chain.startswith(prefix):
            sub: str
            name: str
            sub, _, name = chain.removeprefix(local).rpartition(".")
            yield chain, sub, name


def submodules(catalog: Index, prefix: str) -> Iterator[Module]:
    """Find the module named `prefix`, and every module dotted under it (`pkg.util` under `pkg`).

    A module's identifier characters all sort after `.`, so the names in `[prefix, prefix + "/")` are
    exactly `prefix` itself and those starting with `prefix + "."` (`/` is the character after `.`).

    Yields:
      Each such module, by name.

    """
    start: int = bisect.bisect_left(catalog.names, prefix)
    stop: int = bisect.bisect_left(catalog.names, f"{prefix}/")
    name: str
    for name in catalog.names[start:stop]:
        yield catalog.modules[name]


def classes_under(catalog: Index, local: str, package: str, kind: str) -> Iterator[tuple[str, Origin]]:
    """Spell the classes (or, by `kind`, the aliases) of `package` and its submodules as a file may name them.

    One importing it as `local`: every one, written in the file or not, since a type written for it
    may name any (`m.Row`, by `import m`).

    Returns:
      Each spelling (`m.Row`, `pkg.m.Row`), and the module and name it is.

    """
    found: _Under | None
    if (found := None if catalog.memo is None else catalog.memo.under.get((package, kind))) is None:
        found = [
            (f"{other.name.removeprefix(package)}.{name}", (other.name, name))
            for other in submodules(catalog, package)
            for name in (other.classes if kind == _CLASS else other.aliases)
        ]
        if catalog.memo is not None:
            catalog.memo.under[package, kind] = found
    return ((f"{local}{suffix}", origin) for suffix, origin in found)


def _fixtures(tree: ast.Module) -> dict[str, bool]:
    """Find the module's top-level pytest fixtures.

    Returns:
      Each one's name, and whether it's a generator.

    """
    return {
        stmt.name: yields_itself(stmt)
        for stmt in tree.body
        if isinstance(stmt, ast.FunctionDef) and is_fixture(stmt)
    }


def _aliases(tree: ast.Module) -> dict[str, bool]:
    """Find a module's type aliases, at its top level or under an `if` or `try` there.

    A name annotated `TypeAlias`, bound to a subscript or a union (`Json = dict[str, "Json"] | str`),
    or a `type` statement's.

    Returns:
      Each one's name, and whether it takes type arguments: its value names one of the module's type
      variables, or it has type parameters of its own.

    """
    type_vars: frozenset[str] = defined_type_vars(tree)
    found: dict[str, bool] = {}
    stmt: ast.stmt
    name: str
    value: ast.expr
    annotation: ast.expr
    for stmt in top_level(tree.body):
        match stmt:
            case ast.AnnAssign(
                target=ast.Name(id=name),
                annotation=annotation,
                value=ast.expr() as value,
            ) if node_name(annotation) == _TYPE_ALIAS:
                found[name] = _names_any(value, type_vars)
            case ast.Assign(targets=[ast.Name(id=name)], value=value) if is_composite(value):
                found[name] = _names_any(value, type_vars)
            case _ if type(stmt).__name__ == _TYPE_ALIAS:
                named: ast.Name = cast("ast.Name", getattr(stmt, "name", None))
                found[named.id] = bool(cast("object", getattr(stmt, "type_params", ())))
            case _:
                pass
    return found


def _assigned(body: Sequence[ast.stmt]) -> Counter[str]:
    """Count how many times a run of a module's top level may assign each name, as a type checker reads it.

    Under its `if`s and `try`s too: both arms of an `if`, but one of an `if` a checker decides
    (`sys.version_info >= (3, 10)`, `TYPE_CHECKING`), and never the arm a constant rules out
    (`elif False:`). A name assigned twice is a variable to it, not an alias (`if MYPY: X = A` /
    `else: X = B`).

    Returns:
      Each name's count.

    """
    counts: Counter[str] = Counter()
    stmt: ast.stmt
    name: str
    test: ast.expr
    constant: bool
    for stmt in body:
        match stmt:
            case (
                ast.Assign(targets=[ast.Name(id=name)])
                | ast.AnnAssign(target=ast.Name(id=name), value=ast.expr())
            ):
                counts[name] += 1
            case ast.If(test=ast.Constant(value=bool() as constant)):
                counts += _assigned(stmt.body if constant else stmt.orelse)
            case ast.If(test=test):
                arms: tuple[Counter[str], Counter[str]] = (_assigned(stmt.body), _assigned(stmt.orelse))
                counts += (arms[0] | arms[1]) if _names_any(test, _DECIDED) else (arms[0] + arms[1])
            case ast.Try() | ast.TryStar():
                counts += _assigned(child_statements(stmt))
            case _:
                pass
    return counts


def _names_any(value: ast.expr, names: frozenset[str]) -> bool:
    return any(node_name(node) in names for node in ast.walk(value))


def open_functions(tree: ast.Module) -> dict[str, tuple[Param, ...]]:
    """Find a module's plain top-level functions with a parameter left unannotated.

    Plain: not decorated (a decorator may change how it's called), without `*args` or `**kwargs`
    (whose arguments can't be matched), and defined once.

    Returns:
      Each one's parameters, by its name.

    """
    counts: dict[str, int] = {}
    stmt: ast.stmt
    for stmt in tree.body:
        if isinstance(stmt, ast.FunctionDef | ast.AsyncFunctionDef | ast.ClassDef):
            counts[stmt.name] = counts.get(stmt.name, 0) + 1
    return {
        stmt.name: _params(stmt.args)
        for stmt in tree.body
        if isinstance(stmt, ast.FunctionDef | ast.AsyncFunctionDef)
        and counts[stmt.name] == 1
        and _plain(stmt)
    }


def _plain(function: ast.FunctionDef | ast.AsyncFunctionDef) -> bool:
    """Check a function is undecorated, without `*args` or `**kwargs`, and has an unannotated parameter.

    Returns:
      Whether it is.

    """
    args: ast.arguments = function.args
    return (
        not function.decorator_list
        and args.vararg is None
        and args.kwarg is None
        and any(arg.annotation is None for arg in (*args.posonlyargs, *args.args, *args.kwonlyargs))
    )


def _params(args: ast.arguments) -> tuple[Param, ...]:
    """Read a function's parameters (see `Param`).

    Returns:
      Them, in order.

    """
    positional: list[ast.arg] = [*args.posonlyargs, *args.args]
    first_default: int = len(positional) - len(args.defaults)
    return (
        *(
            (
                arg.arg,
                _POSITIONAL if at < len(args.posonlyargs) else _EITHER,
                at >= first_default,
                arg.annotation is not None,
            )
            for at, arg in enumerate(positional)
        ),
        *(
            (arg.arg, _KEYWORD, default is not None, arg.annotation is not None)
            for arg, default in zip(args.kwonlyargs, args.kw_defaults, strict=True)
        ),
    )


def _called(tree: ast.Module, names: Mapping[str, Origin]) -> frozenset[str]:
    """Find what the module calls through its top-level names: `f()`, `u.f()`, `pkg.util.f()`.

    Returns:
      Each callee, as written.

    """
    callees: Iterator[str | None] = (
        dotted(node.func) for node in cast("list[ast.Call]", of_type(tree, ast.Call))
    )
    return frozenset(callee for callee in callees if callee is not None and callee.partition(".")[0] in names)


def _passed(tree: ast.Module, names: Mapping[str, Origin]) -> frozenset[str]:
    """Find what the module passes as an argument through its top-level names: `np.float64`, `Row`.

    Returns:
      Each, as written.

    """
    arguments: Iterator[str | None] = (
        dotted(argument)
        for node in cast("list[ast.Call]", of_type(tree, ast.Call))
        for argument in (*node.args, *(keyword.value for keyword in node.keywords))
    )
    return frozenset(name for name in arguments if name is not None and name.partition(".")[0] in names)


def _method_calls(tree: ast.Module) -> frozenset[str]:
    """Name the methods the module calls on anything: `astype` in `a.astype(x)`.

    Returns:
      Them.

    """
    return frozenset(
        node.func.attr
        for node in cast("list[ast.Call]", of_type(tree, ast.Call))
        if isinstance(node.func, ast.Attribute)
    )


def _attributes(tree: ast.Module) -> frozenset[str]:
    """Name the attributes the module takes of anything: `x` in `a.x`, `astype` in `a.astype(x)`.

    And those its statements take without naming them: a call's `__call__`, a `with`'s `__enter__`;
    and the literal keys it reads of anything (`d["x"]`, `d.get("x")`), as a `TypedDict`'s are held
    (see `annotations.key`), and the methods it awaits a call of, as an `async def`'s are held.

    Returns:
      Them: all of another file's class's members it can use.

    """
    named: frozenset[str] = frozenset(
        node.attr for node in cast("list[ast.Attribute]", of_type(tree, ast.Attribute))
    )
    indexes: list[ast.expr] = [
        node.slice for node in cast("list[ast.Subscript]", of_type(tree, ast.Subscript))
    ]
    indexes.extend(
        node.args[0]
        for node in cast("list[ast.Call]", of_type(tree, ast.Call))
        if node.args and isinstance(node.func, ast.Attribute) and node.func.attr == _GET
    )
    awaited: frozenset[str] = frozenset(
        AWAIT + node.value.func.attr
        for node in cast("list[ast.Await]", of_type(tree, ast.Await))
        if isinstance(node.value, ast.Call) and isinstance(node.value.func, ast.Attribute)
    )
    keys: frozenset[str] = frozenset(
        key(index.value)
        for index in indexes
        if isinstance(index, ast.Constant) and isinstance(index.value, str)
    )
    return named | keys | awaited | _quoted(tree) | _UNNAMED


def _quoted(tree: ast.Module) -> frozenset[str]:
    """Name the attributes the module's quoted annotations take: `Study` in `study: "optuna.Study"`.

    Returns:
      Them.

    """
    functions: list[ast.FunctionDef | ast.AsyncFunctionDef] = cast(
        "list[ast.FunctionDef | ast.AsyncFunctionDef]",
        of_type(tree, ast.FunctionDef, ast.AsyncFunctionDef),
    )
    annotations: list[ast.expr | None] = [
        *(node.annotation for node in cast("list[ast.arg]", of_type(tree, ast.arg))),
        *(node.annotation for node in cast("list[ast.AnnAssign]", of_type(tree, ast.AnnAssign))),
        *(node.returns for node in functions),
    ]
    return frozenset(
        part
        for annotation in annotations
        if annotation is not None
        for node in ast.walk(annotation)
        if isinstance(node, ast.Constant) and isinstance(node.value, str)
        for dotted in cast("list[str]", _DOTTED.findall(node.value))
        for part in dotted.split(".")[1:]
    )


def _source(path: Path) -> str | None:
    """Read a module's text.

    Returns:
      It, or `None` if it can't be read, or decoded (`SyntaxError`: an unknown encoding).

    """
    try:
        return parsed.text(path.read_bytes())
    except (OSError, SyntaxError, ValueError):  # UnicodeDecodeError is a ValueError
        return None
