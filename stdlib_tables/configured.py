# SPDX-License-Identifier: MIT
"""The standard-library tables as one configuration (a platform and a Python version) sees the stubs.

`tables_for` walks every public module's names in that configuration and enters each where it
belongs (see `stdlib_tables.generate`, which reads all twelve and keeps what they agree on): a
function's return, a class with its members, a generic class's type parameters and constructor, a
function whose arguments decide its return, by every public path each is reached through.
"""

import ast
from typing import Final, NamedTuple, TypeAlias

from constricter.fix.core.signatures import Signature
from stdlib_tables.accepting import CONTAINERS, SCALARS
from stdlib_tables.elements import element, entered_by_base
from stdlib_tables.forms import ANY_STR, ClassRef, Defs, Form, Text, usable
from stdlib_tables.overloads import Overloads
from stdlib_tables.reading import ANY, ATTRIBUTE, AWAITED, CLASSMETHOD, Member, Reading, Table
from stdlib_tables.stubs import (
    Alias,
    Binding,
    Config,
    Found,
    Function,
    Klass,
    Namespace,
    Stubs,
    Unknown,
    Variable,
    private,
)

# Modules nothing is taken from: `typing`'s classes are special forms and factories, `builtins` is
# typed apart, and these aren't imported for what they define (`encodings`' codecs register
# themselves; `xxlimited` is CPython's example extension).
_SKIPPED_MODULES: Final = frozenset(
    {"typing", "typing_extensions", "builtins", "encodings", "xxlimited", "__main__", "this", "antigravity"},
)
# In the stubs for every platform, but not in every Python CI runs the tests on (CPython's own, a
# debug build's), or not what they say there (`KW_ONLY`, `python_symbols` are instances, not classes).
_RUNTIME: Final = frozenset(
    {
        "sys.getrefcount",
        "sys.gettotalrefcount",
        "dataclasses.KW_ONLY",
        "lib2to3.pygram.python_symbols",
        "lib2to3.pygram.pattern_symbols",
    },
)
# The private classes a public function returns and nothing public stands for (what a `with`
# binds), and a private function code calls all the same.
_PRIVATE: Final = {
    "unittest.case": ("_AssertRaisesContext", "_AssertWarnsContext"),
    "unittest._log": ("_AssertLogsContext", "_LoggingWatcher"),
    "tempfile": ("_TemporaryFileWrapper",),
    "sys": ("_getframe",),
}
# Modules whose names installed packages' stubs annotate with, private or not (`scalars`).
_ANNOTATING: Final = frozenset({"typing", "typing_extensions", "builtins", "_typeshed", "collections.abc"})
YES: Final = "y"
_HOPS: Final = 8  # the variables followed from one bound to another's
_FUNCTION: Final = "def"  # a `functions` entry: what the path names
_ENTER: Final = "__enter__"


# Each signature of a function whose return its arguments decide (see `overloads.Overloads.entry`).
Signatures: TypeAlias = list[Signature]


class Tables(NamedTuple):
    """Every table, for one configuration or all of them together."""

    returns: Table
    overloads: dict[str, list[Signatures]]  # each configuration's reading, once
    classes: Table
    aliases: Table
    methods: dict[str, Table]
    attributes: dict[str, Table]
    method_overloads: dict[str, Table]  # each class's methods in `method_signatures` (`await m`: awaited)
    method_signatures: dict[str, list[Signatures]]  # as `overloads`, by where they're defined
    type_parameters: Table  # each generic class's, in order, comma-separated (`_T=`: with a default)
    bases: Table  # each class's public ancestors in the tables, nearest first, comma-separated
    subscriptable: Table  # each generic class's: `y` if it can be subscripted at run time, else `n`
    generic_attributes: dict[str, Table]  # a class's own attributes, as templates
    variables: Table  # module-level variables' types: builtin annotations, or classes' paths
    scalars: Table  # each class's and alias's verdict (`y`, `n`, `?`) per `SCALARS`, then `CONTAINERS`, type
    scalar_members: dict[str, list[str]]  # each scalar's members, its class's and its bases'
    functions: Table  # capitalised functions no other table types, each to `_FUNCTION`
    # What awaiting a call of each `async def` gives: a function's by its path, a method's by its
    # class's path and its name, each class's inherited ones included.
    awaited: Table
    awaited_overloads: dict[str, list[Signatures]]  # as `overloads`: an `async def`'s, awaited
    elements: Table  # what iterating each class's instance gives, as a template (see `generic_attributes`)


def _paths(stubs: Stubs, config: Config) -> dict[str, Found]:
    """Find every public path in the stubs (`module.name`), and what it names, in `config`; and `_PRIVATE`'s.

    Not a name that's also a submodule's (`curses.has_key`): which one it is depends on the imports.

    Returns:
      Each path's definition.

    """
    modules: frozenset[str] = frozenset(stubs.modules())
    found: dict[str, Found] = {}
    module: str
    space: Namespace | None
    target: Found | None
    for module in sorted(modules):
        skipped: bool = module.split(".")[0] in _SKIPPED_MODULES or (
            private(module) and module not in _PRIVATE
        )
        if skipped or (space := stubs.namespace(module, config)) is None:
            continue
        name: str
        for name in () if private(module) else sorted(space.public):
            path: str = f"{module}.{name}"
            if not private(name) and path not in modules and (target := stubs.lookup(module, name, config)):
                found[path] = target
        for name in _PRIVATE.get(module, ()):
            if (target := stubs.lookup(module, name, config)) is not None:
                found[f"{module}.{name}"] = target
    return found


def tables_for(stubs: Stubs, config: Config) -> Tables:
    """Build every table as `config` sees the stubs.

    Returns:
      Them.

    """
    reading: Reading = Reading(stubs, config)
    paths: dict[str, Found] = _paths(stubs, config)
    every: dict[ClassRef, str] = {}  # generic classes too, which only a return template names
    path: str
    found: Found
    for path, found in sorted(paths.items(), key=lambda item: _preference(*item)):
        if isinstance(found.binding, Klass):
            _ = every.setdefault(ClassRef(found.module, found.name), path)
    canonical: dict[ClassRef, str] = {
        klass: path for klass, path in every.items() if not reading.generic(klass)
    }
    tables: Tables = Tables({}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {})
    reader: _Reader = _Reader(reading, Overloads(reading, every), canonical)
    _enter_scalars(tables, reader, stubs, config)
    for path, found in paths.items():
        _enter(tables, reader, path, found)
    owner: ClassRef
    for owner, path in canonical.items():
        _enter_class(tables, reader, owner, path)
    for owner, path in every.items():
        _enter_generic(tables, reader, owner, path)
        yielded: str | None
        if (yielded := element(reader.overloads, owner)) is not None:
            tables.elements[path] = yielded
    return tables


class _Reader(NamedTuple):
    """What one configuration's tables are read with: its stubs, overloads and classes' paths."""

    reading: Reading
    overloads: Overloads
    canonical: dict[ClassRef, str]  # every public non-generic class's path


def _enter_scalars(tables: Tables, reader: _Reader, stubs: Stubs, config: Config) -> None:
    """Enter which scalars each class and alias takes, by its public paths and `_ANNOTATING`'s names."""
    paths: dict[str, Found] = {}
    module: str
    for module in sorted(_ANNOTATING):
        space: Namespace | None = stubs.namespace(module, config)
        name: str
        for name in sorted({} if space is None else space.names):
            found: Found | None
            if (found := stubs.lookup(module, name, config)) is not None:
                paths[f"{module}.{name}"] = found
    paths.update(_paths(stubs, config))
    path: str
    target: Found
    for path, target in paths.items():
        if isinstance(target.binding, Klass | Alias):
            bare: ast.Name = ast.Name(path.rpartition(".")[2])
            tables.scalars[path] = reader.overloads.accepts(bare, path.rpartition(".")[0]).values + (
                reader.overloads.takes(bare, path.rpartition(".")[0], CONTAINERS)
            )
    scalar: str
    members: frozenset[str] | None
    for scalar in (*SCALARS, *CONTAINERS):
        if (members := reader.overloads.scalar_members(scalar)) is not None:
            tables.scalar_members[scalar] = sorted(members)


def _enter_class(tables: Tables, reader: _Reader, klass: ClassRef, path: str) -> None:
    """Enter a class's members, its public ancestors, and its methods whose arguments decide their return.

    And its own attributes no builtin annotation or class alone types, as templates (`Signature`'s
    `parameters`, a `MappingProxyType[str, Parameter]`).
    """
    members: dict[str, Member] = reader.reading.members(klass)
    _enter_members(tables, path, members, reader.canonical)
    entered: Table = tables.attributes.get(path, {})
    templates: Table = {
        name: template for name, template in reader.overloads.attributes(klass).items() if name not in entered
    }
    if templates:
        tables.generic_attributes[path] = templates
    ancestors: list[str] = [
        reader.canonical[base] for base in reader.reading.trusted(klass)[0][1:] if base in reader.canonical
    ]
    if ancestors:
        tables.bases[path] = ",".join(ancestors)
    name: str
    method: str
    signatures: list[Signature]
    for name, (method, signatures) in reader.overloads.methods(klass, members).items():
        tables.method_overloads.setdefault(path, {})[name] = method
        tables.method_signatures[method] = [signatures]


def _enter_generic(tables: Tables, reader: _Reader, klass: ClassRef, path: str) -> None:
    """Enter a generic class's own methods' signatures, and its type parameters, which its instances bind."""
    params: list[str] | None
    if klass in reader.canonical or not (params := reader.overloads.type_parameters(klass)):
        return
    tables.type_parameters[path] = ",".join(params)
    tables.subscriptable[path] = YES if reader.reading.subscriptable(klass) else "n"
    if reader.overloads.enters_itself(klass):  # `with` gives the instance, whatever its arguments
        tables.methods.setdefault(path, {})[_ENTER] = path
    attributes: Table
    if attributes := reader.overloads.attributes(klass):
        tables.generic_attributes[path] = attributes
    name: str
    method: str
    signatures: list[Signature]
    for name, (method, signatures) in reader.overloads.methods(klass, (), inherited=False).items():
        tables.method_overloads.setdefault(path, {})[name] = method
        tables.method_signatures[method] = [signatures]
    given: str | None
    if (given := entered_by_base(reader.overloads, klass)) is not None:  # `with closing(thing)`: by its base
        tables.method_overloads.setdefault(path, {})[_ENTER] = f"{path}.{_ENTER}"
        tables.method_signatures[f"{path}.{_ENTER}"] = [[Signature(params=[], returns=given)]]
    # What it inherits with one type, whatever its arguments (`TextIOWrapper.read()`, `TextIOBase`'s).
    own: dict[str, Binding] = reader.reading.body(klass)
    _enter_members(
        tables,
        path,
        {name: member for name, member in reader.reading.members(klass).items() if name not in own},
        reader.canonical,
    )


def _preference(path: str, found: Found) -> tuple[int, bool, int, str]:
    """Rank a class's public paths: the shortest, then the one in the module that defines it.

    Returns:
      The sort key.

    """
    return (path.count("."), path.rpartition(".")[0] != found.module, len(path), path)


def _enter(tables: Tables, reader: _Reader, path: str, found: Found) -> None:
    """Enter what one public path names: a function's return, or a class, its classmethods and alias.

    A function whose every signature returns the same builtin or class goes in `returns` or
    `classes`; one whose arguments decide it, in `overloads`.
    """
    defs: tuple[ast.FunctionDef | ast.AsyncFunctionDef, ...]
    value: ast.expr
    klass: ClassRef = ClassRef(found.module, found.name)
    match found.binding:
        case _ if path in _RUNTIME:
            pass
        case Function(defs=defs):
            _function(tables, reader, path, found.module, defs)
        case Alias(value=value):
            _enter_alias(tables, reader, path, value, found.module)
            _enter_callable(tables, reader, path, value, found.module)
        case Variable(annotation=value):  # `sys.path`, `os.sep`
            _enter_variable(tables, reader, path, value, found.module)
            _enter_callable(tables, reader, path, value, found.module)
        case Klass() if klass in reader.canonical:
            _enter_named(tables, reader, path, found)
        case Klass():  # a generic class, typed by what binds its parameters
            _enter_constructor(tables, reader, path, klass)
        case _:
            pass


def _enter_alias(tables: Tables, reader: _Reader, path: str, value: "ast.expr", module: str) -> None:
    """Enter an alias: a generic class's constructor (`ref = ReferenceType`), or a bound method's return."""
    aliased: ClassRef | None
    if (aliased := _aliased(reader, value, module)) is not None:
        _enter_constructor(tables, reader, path, aliased)
    else:
        _entry(tables, path, reader.reading.bound_method(value, module), reader.canonical)


def _enter_callable(tables: Tables, reader: _Reader, path: str, value: "ast.expr", module: str) -> None:
    """Enter a capitalised variable no table types under `functions`: a call of it constructs no such class.

    `multiprocessing.Value`, bound to a context's method. Not one that names a class
    (`Pattern = re.Pattern`, `x: type[C]`), nor a constant (`os.EX_OK`).
    """
    name: str = path.rpartition(".")[2]
    held: bool = (
        path in tables.returns
        or path in tables.classes
        or path in tables.overloads
        or path in tables.variables
        or path in tables.aliases
    )
    if name[:1].isupper() and not name.isupper() and not held and _calls(reader, value, module):
        tables.functions[path] = _FUNCTION


def _calls(reader: _Reader, value: "ast.expr", module: str, hops: int = 0) -> bool:
    """Check whether what a variable is bound to, or declared as, is no class: a function, or unknown.

    Returns:
      Whether it is; not for a type's alias or a `type[C]`, nor through more variables than `_HOPS`.

    """
    if isinstance(value, (ast.Subscript, ast.BinOp)) or hops > _HOPS:
        return False
    target: Found | None = reader.reading.ref(value, module)
    if target is not None and isinstance(target.binding, Variable):  # bound to another's variable
        return _calls(reader, target.binding.annotation, target.module, hops + 1)
    return target is None or isinstance(target.binding, (Function, Unknown))


def _enter_variable(tables: Tables, reader: _Reader, path: str, annotation: "ast.expr", module: str) -> None:
    """Enter a module-level variable's type, if the tables can hold it.

    A builtin annotation or a class's path (`sys.path`: `list[str]`), else a template naming classes
    by their paths (`sys.modules`: `dict[str, types.ModuleType]`).
    """
    form: Form | None = reader.reading.form(annotation, module, None)
    value: str | None = None if form is None else _value(form, reader.canonical)
    if value is None and form is None:
        value = reader.overloads.template(annotation, module)
    if value is not None:
        tables.variables[path] = value


def _enter_named(tables: Tables, reader: _Reader, path: str, found: Found) -> None:
    """Enter a non-generic class under one of its paths: its alias, what constructs it, its classmethods."""
    klass: ClassRef = ClassRef(found.module, found.name)
    canonical: dict[ClassRef, str] = reader.canonical
    if canonical[klass] != path:
        tables.aliases[path] = canonical[klass]
    if reader.reading.constructs(klass):
        tables.classes[path] = canonical[klass]
    name: str
    member: Member
    # Only those its own module's classes define: typeshed makes some classes subclass an abstract
    # class they're only registered with at runtime (`importlib.abc`'s).
    for name, member in reader.reading.members(klass).items():
        if member.kind == CLASSMETHOD and member.module == found.module:
            _entry(tables, f"{path}.{name}", member.form, canonical)


def _aliased(reader: _Reader, value: "ast.expr", module: str) -> ClassRef | None:
    """Find the generic class an alias names (`ref = ReferenceType`), if it is one.

    Returns:
      It, or `None`.

    """
    target: Found | None = reader.reading.ref(value, module)
    if target is None or not isinstance(target.binding, Klass):
        return None
    klass: ClassRef = ClassRef(target.module, target.name)
    return None if klass in reader.canonical else klass


def _enter_constructor(tables: Tables, reader: _Reader, path: str, klass: ClassRef) -> None:
    """Enter a generic class's constructor, under a path naming it (see `Overloads.constructor`)."""
    signatures: Signatures | None
    if (signatures := reader.overloads.constructor(klass)) is not None:
        tables.overloads[path] = [signatures]


def _function(tables: Tables, reader: _Reader, path: str, module: str, defs: Defs) -> None:
    """Enter a function: under `returns` or `classes` if it always returns the same, else `overloads`.

    An `async def`: under `awaited` or `awaited_overloads`, as what awaiting its call gives.

    One none of them can hold is under `functions`, if its name is capitalised.
    """
    form: Form | None = reader.reading.returns(defs, module, None)
    signatures: Signatures | None
    value: str | None
    awaited: Form | None = reader.reading.returns(defs, module, None, awaited=True)
    value = None if awaited is None or awaited == ANY_STR else _value(awaited, reader.canonical)
    if value is not None:
        tables.awaited[path] = value
    elif form != ANY_STR and form is not None and _value(form, reader.canonical) is not None:
        _entry(tables, path, form, reader.canonical)
    elif reader.reading.returns_any(defs, module):
        tables.returns[path] = ANY
    elif (signatures := reader.overloads.entry(defs, module)) is not None:
        tables.overloads[path] = [signatures]
    elif (signatures := reader.overloads.entry(defs, module, awaited=True)) is not None:
        tables.awaited_overloads[path] = [signatures]
    elif path.rpartition(".")[2][:1].isupper():
        tables.functions[path] = _FUNCTION


def _enter_members(
    tables: Tables,
    path: str,
    members: dict[str, Member],
    canonical: dict[ClassRef, str],
) -> None:
    """Enter a class's members' types under its path: its methods' returns, and its attributes'."""
    name: str
    member: Member
    value: str | None
    for name, member in members.items():
        if (value := _value(member.form, canonical)) is None:
            continue
        if member.kind == AWAITED:
            tables.awaited[f"{path}.{name}"] = value
        else:
            (tables.attributes if member.kind == ATTRIBUTE else tables.methods).setdefault(path, {})[name] = (
                value
            )


def _entry(tables: Tables, path: str, form: Form | None, canonical: dict[ClassRef, str]) -> None:
    """Enter a function's (or classmethod's) return under `path`, in the table its form belongs in."""
    value: str | None
    if form is not None and (value := _value(form, canonical)) is not None:
        (tables.classes if isinstance(form, ClassRef) else tables.returns)[path] = value


def _value(form: Form, canonical: dict[ClassRef, str]) -> str | None:
    """Spell a form as a table holds it: a builtin annotation, or a class's canonical path.

    Returns:
      It, or `None` for `AnyStr`, a class with no public path, or an annotation `--fix` shouldn't write.

    """
    text: str
    match form:
        case Text(text=text):
            return text if usable(text) else None
        case ClassRef():
            return canonical.get(form)
        case _:
            return None
