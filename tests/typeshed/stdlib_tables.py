# SPDX-License-Identifier: MIT
"""Generate `constricter/fix/tables/`, the standard-library tables `--fix` types calls from.

  local/.venv/bin/python -m tests.typeshed.stdlib_tables          # rewrite it
  local/.venv/bin/python -m tests.typeshed.stdlib_tables --check  # exit 1 if it's out of date

It reads the typeshed stubs basedpyright bundles (the dev group's pinned version), as each platform
(Linux, macOS, Windows) and each Python version constricter supports (3.11 to 3.14) sees them, and
keeps what comes out the same for all twelve:

- `returns`: functions (and classes' own classmethods and staticmethods) returning a builtin type
  (`int`, `list[str]`, `str | None`), by every public path they're reached through;
- `any_str`: functions returning their arguments' `str` or `bytes` (an `AnyStr`, or overloads);
- `classes`: non-generic classes, and functions returning one, by the class's public path: the
  shortest (`unittest.TestLoader`, not `unittest.loader.TestLoader`), then its own module's;
- `methods` and `attributes`: what each such class's public methods return, and its attributes and
  properties hold, inherited ones included (in their method resolution order), by that path;
- `aliases`: the class's other public paths;
- `overloads`: functions whose arguments decide their return, and generic classes' constructors,
  each signature as `tests/typeshed/overloads.py` reads it;
- `type_parameters` and `subscriptable`: each generic class's type parameters, and whether every
  Python can subscript it at run time; `generic_attributes`: its own attributes and properties, as
  templates its instance's type arguments bind;
- `variables`: module-level variables' types (`sys.path`, `os.sep`), as `returns` and `classes` hold
  a function's.

A return that names a `TypeVar` (but `AnyStr`), `Any`, or anything else vague, differs between
overloads, or is spelled with a class inside a generic (`list[Path]`), is left out; so is `typing`
(its factories), `enum`'s classes (their functional API makes a class), and what `_RUNTIME` lists.
"""

import json
import sys
from collections.abc import Sequence
from pathlib import Path
from typing import TYPE_CHECKING, Final, NamedTuple, TypeAlias

import basedpyright  # pyright: ignore[reportMissingTypeStubs]  # the dev group's: its bundled stubs

from constricter.fix.stdlib import Signature
from tests.typeshed.overloads import Overloads
from tests.typeshed.reading import (
    ANY_STR,
    ATTRIBUTE,
    CLASSMETHOD,
    ClassRef,
    Defs,
    Form,
    Member,
    Reading,
    Table,
    Text,
    usable,
)
from tests.typeshed.stubs import (
    CONFIGS,
    Alias,
    Config,
    Found,
    Function,
    Klass,
    Namespace,
    Stubs,
    Variable,
    private,
)

if TYPE_CHECKING:
    import ast

TYPESHED: Final = Path(basedpyright.__file__).parent / "dist" / "typeshed-fallback"
OUTPUT: Final = Path(__file__).parents[2] / "constricter" / "fix" / "tables"  # one JSON file per table
# Where each function or class only some platforms and Python versions have is (the tests' alone).
PARTIAL: Final = Path(__file__).with_name("partial.json")
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
_CHECK: Final = "--check"
_YES: Final = "y"


# Each signature of a function whose return its arguments decide (see `overloads.Overloads.entry`).
Signatures: TypeAlias = list[Signature]
# One of the tables (or `source`, where they're from).
_Json: TypeAlias = (
    Table
    | dict[str, Table]
    | dict[str, dict[str, str | None]]
    | dict[str, list[Signatures]]
    | dict[str, list[str]]
)


class _Tables(NamedTuple):
    """Every table, for one configuration or all of them together."""

    returns: Table
    overloads: dict[str, list[Signatures]]  # each configuration's reading, once
    classes: Table
    aliases: Table
    methods: dict[str, Table]
    attributes: dict[str, Table]
    method_overloads: dict[str, Table]  # each class's methods in `method_signatures`
    method_signatures: dict[str, list[Signatures]]  # as `overloads`, by where they're defined
    type_parameters: Table  # each generic class's, in order, comma-separated (`_T=`: with a default)
    bases: Table  # each class's public ancestors in the tables, nearest first, comma-separated
    subscriptable: Table  # each generic class's: `y` if it can be subscripted at run time, else `n`
    generic_attributes: dict[str, Table]  # each generic class's own attributes, as templates
    variables: Table  # module-level variables' types: builtin annotations, or classes' paths


def _paths(stubs: Stubs, config: Config) -> dict[str, Found]:
    """Find every public path in the stubs (`module.name`), and what it names, in `config`.

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
        skipped: bool = private(module) or module.split(".")[0] in _SKIPPED_MODULES
        if skipped or (space := stubs.namespace(module, config)) is None:
            continue
        name: str
        for name in sorted(space.public):
            path: str = f"{module}.{name}"
            if not private(name) and path not in modules and (target := stubs.lookup(module, name, config)):
                found[path] = target
    return found


def _read(stubs: Stubs, config: Config) -> _Tables:
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
    tables: _Tables = _Tables({}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {}, {})
    reader: _Reader = _Reader(reading, Overloads(reading, every), canonical)
    for path, found in paths.items():
        _enter(tables, reader, path, found)
    owner: ClassRef
    for owner, path in canonical.items():
        _enter_class(tables, reader, owner, path)
    for owner, path in every.items():
        _enter_generic(tables, reader, owner, path)
    return tables


class _Reader(NamedTuple):
    """What one configuration's tables are read with: its stubs, overloads and classes' paths."""

    reading: Reading
    overloads: Overloads
    canonical: dict[ClassRef, str]  # every public non-generic class's path


def _enter_class(tables: _Tables, reader: _Reader, klass: ClassRef, path: str) -> None:
    """Enter a class's members, its public ancestors, and its methods whose arguments decide their return."""
    members: dict[str, Member] = reader.reading.members(klass)
    _enter_members(tables, path, members, reader.canonical)
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


def _enter_generic(tables: _Tables, reader: _Reader, klass: ClassRef, path: str) -> None:
    """Enter a generic class's own methods' signatures, and its type parameters, which its instances bind."""
    params: list[str] | None
    if klass in reader.canonical or not (params := reader.overloads.type_parameters(klass)):
        return
    tables.type_parameters[path] = ",".join(params)
    tables.subscriptable[path] = _YES if reader.reading.subscriptable(klass) else "n"
    attributes: Table
    if attributes := reader.overloads.attributes(klass):
        tables.generic_attributes[path] = attributes
    name: str
    method: str
    signatures: list[Signature]
    for name, (method, signatures) in reader.overloads.methods(klass, (), inherited=False).items():
        tables.method_overloads.setdefault(path, {})[name] = method
        tables.method_signatures[method] = [signatures]


def _preference(path: str, found: Found) -> tuple[int, bool, int, str]:
    """Rank a class's public paths: the shortest, then the one in the module that defines it.

    Returns:
      The sort key.

    """
    return (path.count("."), path.rpartition(".")[0] != found.module, len(path), path)


def _enter(tables: _Tables, reader: _Reader, path: str, found: Found) -> None:
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
        case Variable(annotation=value):  # `sys.path`, `os.sep`
            _enter_variable(tables, reader, path, value, found.module)
        case Klass() if klass in reader.canonical:
            _enter_named(tables, reader, path, found)
        case Klass():  # a generic class, typed by what binds its parameters
            _enter_constructor(tables, reader, path, klass)
        case _:
            pass


def _enter_alias(tables: _Tables, reader: _Reader, path: str, value: "ast.expr", module: str) -> None:
    """Enter an alias: a generic class's constructor (`ref = ReferenceType`), or a bound method's return."""
    aliased: ClassRef | None
    if (aliased := _aliased(reader, value, module)) is not None:
        _enter_constructor(tables, reader, path, aliased)
    else:
        _entry(tables, path, reader.reading.bound_method(value, module), reader.canonical)


def _enter_variable(tables: _Tables, reader: _Reader, path: str, annotation: "ast.expr", module: str) -> None:
    """Enter a module-level variable's type (`sys.path`: `list[str]`), if the tables can hold it."""
    form: Form | None = reader.reading.form(annotation, module, None)
    value: str | None
    if (value := None if form is None else _value(form, reader.canonical)) is not None:
        tables.variables[path] = value


def _enter_named(tables: _Tables, reader: _Reader, path: str, found: Found) -> None:
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


def _enter_constructor(tables: _Tables, reader: _Reader, path: str, klass: ClassRef) -> None:
    """Enter a generic class's constructor, under a path naming it (see `Overloads.constructor`)."""
    signatures: Signatures | None
    if (signatures := reader.overloads.constructor(klass)) is not None:
        tables.overloads[path] = [signatures]


def _function(tables: _Tables, reader: _Reader, path: str, module: str, defs: Defs) -> None:
    """Enter a function: under `returns` or `classes` if it always returns the same, else `overloads`."""
    form: Form | None = reader.reading.returns(defs, module, None)
    signatures: Signatures | None
    if form != ANY_STR and form is not None and _value(form, reader.canonical) is not None:
        _entry(tables, path, form, reader.canonical)
    elif (signatures := reader.overloads.entry(defs, module)) is not None:
        tables.overloads[path] = [signatures]


def _enter_members(
    tables: _Tables,
    path: str,
    members: dict[str, Member],
    canonical: dict[ClassRef, str],
) -> None:
    """Enter a class's members' types under its path: its methods' returns, and its attributes'."""
    name: str
    member: Member
    value: str | None
    for name, member in members.items():
        if (value := _value(member.form, canonical)) is not None:
            (tables.attributes if member.kind == ATTRIBUTE else tables.methods).setdefault(path, {})[name] = (
                value
            )


def _entry(tables: _Tables, path: str, form: Form | None, canonical: dict[ClassRef, str]) -> None:
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


def _common(each: list[Table]) -> Table:
    """Keep the entries every table that has them has the same.

    One only some platforms or Python versions have is kept: code calling it runs where it's there.

    Returns:
      Them.

    """
    found: dict[str, set[str]] = {}
    one: Table
    for one in each:
        key: str
        value: str
        for key, value in one.items():
            found.setdefault(key, set()).add(value)
    return {key: values.pop() for key, values in found.items() if len(values) == 1}


def _variants(each: list[dict[str, list[Signatures]]]) -> dict[str, list[Signatures]]:
    """Keep each function's signatures as each configuration that has it reads them, each once.

    `--fix` types a call only when every variant gives it the same type.

    Returns:
      Each function's variants.

    """
    found: dict[str, list[Signatures]] = {}
    one: dict[str, list[Signatures]]
    for one in each:
        path: str
        read: list[Signatures]
        for path, read in one.items():
            variants: list[Signatures] = found.setdefault(path, [])
            variants.extend(signatures for signatures in read if signatures not in variants)
    return found


def _common_by_class(each: list[dict[str, Table]]) -> dict[str, Table]:
    """Keep each class's members every configuration that has them has the same (see `_common`).

    Returns:
      Them, by class (a class with none left out).

    """
    found: dict[str, Table] = {}
    klass: str
    kept: Table
    for klass in dict.fromkeys(key for one in each for key in one):
        if kept := _common([one[klass] for one in each if klass in one]):
            found[klass] = kept
    return found


def _agreed(tables: list[_Tables]) -> _Tables:
    """Keep what every configuration's tables that have an entry agree on.

    Returns:
      The entries that are the same in each that has them.

    """
    return _Tables(
        _common([one.returns for one in tables]),
        _variants([one.overloads for one in tables]),
        _common([one.classes for one in tables]),
        _common([one.aliases for one in tables]),
        _common_by_class([one.methods for one in tables]),
        _common_by_class([one.attributes for one in tables]),
        _common_by_class([one.method_overloads for one in tables]),
        _variants([one.method_signatures for one in tables]),
        _common([one.type_parameters for one in tables]),
        _common([one.bases for one in tables]),
        _common([one.subscriptable for one in tables]),
        _common_by_class([one.generic_attributes for one in tables]),
        _common([one.variables for one in tables]),
    )


def generate(typeshed: Path = TYPESHED) -> dict[Path, str]:
    """Generate the tables from the stubs under `typeshed`, one file each (see `write`).

    And `PARTIAL`, for the tests alone.

    Returns:
      Each file's text, by path.

    """
    stubs: Stubs = Stubs(typeshed)
    each: list[_Tables] = [_read(stubs, config) for config in CONFIGS]
    tables: _Tables = _agreed(each)
    document: dict[str, _Json] = {
        "source": {
            "generator": "tests/typeshed/stdlib_tables.py",
            "typeshed": (typeshed / "commit.txt").read_text(encoding="utf-8").strip(),
        },
        "returns": tables.returns,
        "overloads": tables.overloads,
        "classes": tables.classes,
        "aliases": tables.aliases,
        "methods": inherited(tables.methods, tables.bases),
        "attributes": inherited(tables.attributes, tables.bases),
        "bases": tables.bases,
        "method_overloads": inherited(tables.method_overloads, tables.bases),
        "method_signatures": tables.method_signatures,
        "type_parameters": tables.type_parameters,
        # Where Pythons differ (`array.array`, 3.12+), the entry is left out: not subscriptable.
        "subscriptable": {path: value for path, value in tables.subscriptable.items() if value == _YES},
        "generic_attributes": tables.generic_attributes,
        "variables": tables.variables,
    }
    files: dict[Path, str] = {OUTPUT / f"{name}.json": write(table) for name, table in document.items()}
    files[PARTIAL] = write(_partial(each))
    return files


def inherited(members: dict[str, Table], bases: Table) -> dict[str, dict[str, str | None]]:
    """Write each class's members as it has them apart from its public ancestors (`bases`).

    `--fix` resolves a member as a class's own entry, else its ancestors' in order (each resolved
    the same way): a member the class has as its nearest ancestor does is left out, and one it
    hides (a member it defines that the tables can't hold) is `None`. Checked against the full
    tables, entry by entry.

    Returns:
      Each class's entries.

    """
    found: dict[str, dict[str, str | None]] = {}
    klass: str
    for klass in dict.fromkeys([*members, *bases]):
        through: dict[str, str] = {}
        ancestor: str
        name: str
        value: str
        for ancestor in bases.get(klass, "").split(",") if klass in bases else []:
            for name, value in members.get(ancestor, {}).items():
                _ = through.setdefault(name, value)
        own: Table = members.get(klass, {})
        entries: dict[str, str | None] = {
            **{name: value for name, value in own.items() if through.get(name) != value},
            **dict.fromkeys(through.keys() - own.keys()),
        }
        if entries:
            found[klass] = entries
    assert all(_resolved(found, bases, klass) == table for klass, table in members.items())
    return found


def _resolved(own: dict[str, dict[str, str | None]], bases: Table, klass: str) -> Table:
    """Resolve a class's members as `--fix` does (`stdlib._member`): its own entries, then each ancestor's.

    Returns:
      Them.

    """
    found: dict[str, str | None] = {}
    ancestor: str
    for ancestor in bases.get(klass, "").split(",") if klass in bases else []:
        name: str
        value: str
        for name, value in _resolved(own, bases, ancestor).items():
            _ = found.setdefault(name, value)
    found.update(own.get(klass, {}))
    return {name: value for name, value in found.items() if value is not None}


def write(table: _Json) -> str:
    """Write a table as JSON, one entry a line, sorted: a change to one entry is a change to its line.

    Returns:
      The text.

    """
    entries: list[str] = [
        f"{json.dumps(key)}: {json.dumps(value, separators=(',', ':'), sort_keys=True)}"
        for key, value in sorted(table.items())
    ]
    return "{\n" + ",\n".join(entries) + "\n}\n"


def _partial(each: list[_Tables]) -> dict[str, list[str]]:
    """Find the functions and classes only some configurations have, for the tests to look for there alone.

    Returns:
      Each one's configurations (`linux-3.12`), by path.

    """
    found: dict[str, list[str]] = {}
    config: Config
    tables: _Tables
    for config, tables in zip(CONFIGS, each, strict=True):
        path: str
        for path in {*tables.returns, *tables.overloads, *tables.classes}:
            found.setdefault(path, []).append(f"{config[0]}-3.{config[1]}")
    return {path: configs for path, configs in sorted(found.items()) if len(configs) < len(CONFIGS)}


def main(argv: Sequence[str]) -> int:
    """Write the tables, or with `--check`, compare them with what's written.

    Returns:
      The exit status: 1 if `--check` finds them out of date.

    """
    files: dict[Path, str] = generate()
    written: list[Path] = [*OUTPUT.glob("*.json"), PARTIAL]
    if _CHECK not in argv:
        OUTPUT.mkdir(exist_ok=True)
        stale: Path
        for stale in written:
            if stale not in files:
                stale.unlink()
        path: Path
        text: str
        for path, text in files.items():
            _ = path.write_text(text, encoding="utf-8")
        return 0
    if {path: path.read_text(encoding="utf-8") for path in written if path.exists()} == files:
        return 0
    _ = sys.stderr.write(f"{OUTPUT} is out of date: run tests/typeshed/stdlib_tables.py\n")
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
