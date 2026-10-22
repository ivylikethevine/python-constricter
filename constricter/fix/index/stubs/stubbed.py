"""Installed packages' functions whose arguments decide their type: their signatures, read for a call.

The functions and methods a file calls, and the classes it passes, found through its imports;
their stubs' overloads read by `constricter.fix.index.stubs.signatures` into the signatures the
standard library's tables hold (see `constricter.fix.libraries.overloads`), so a call is matched
the same way, and kept from one file to the next (`constricter.fix.index.stubs.read`).
"""

from collections.abc import Mapping
from pathlib import Path
from typing import TYPE_CHECKING, Final, NamedTuple, TypeAlias, cast

from constricter.fix.core.known import Guarded, Origin
from constricter.fix.core.signatures import Expansion, ReadSignature
from constricter.fix.index import own_overloads, project
from constricter.fix.index.modules import SUFFIX, Index, Module, module_name
from constricter.fix.index.stubs import chained, classnames
from constricter.fix.index.stubs.names import call_origin
from constricter.fix.index.stubs.read import MEMO, Expanded, Memo
from constricter.fix.index.stubs.signatures import Reader, read_all

if TYPE_CHECKING:
    from constricter.fix.index.stubs.declared import Class, Declarations, Signature

_KIND: Final = "signatures"


_Read: TypeAlias = dict[str, tuple[ReadSignature, ...]]  # functions' signatures, by a call's name


def overloaded(catalog: Index, path: Path, guarded: dict[str, Guarded] | None = None) -> _Read:
    """Find the functions the file at `path` calls whose arguments decide their type.

    An installed package's, and a checked file's defined with `@overload` (see `own_overloads`):
    `guarded` records the names their returns need imported for type checking.

    Returns:
      Each one's signatures (one variant, see `overloads.chosen`), by the call's name as written
      (`np.empty`); none for a file `catalog` doesn't have.

    """
    modules: dict[str, Module] = catalog.modules
    target: Module | None
    if path.suffix != SUFFIX or (target := modules.get(module_name(path))) is None:
        return {}
    found: dict[str, tuple[ReadSignature, ...]] = {}
    memo: dict[tuple[str, str], tuple[ReadSignature, ...]] = MEMO.of(modules).read
    key: str
    for key in sorted(target.called):
        origin: Origin | None = call_origin(modules, target, key)
        defined: tuple[Module, str] | None
        if origin is None or (defined := project.definition(modules, origin, _KIND)) is None:
            continue
        if not defined[0].installed:
            # Read each time: what a checked file's parameters take rests on the checked files' classes.
            read: tuple[ReadSignature, ...] = read_signatures(modules, *defined)
            found[key] = own_overloads.spelled(catalog, target, defined, read, guarded)
            continue
        where: tuple[str, str]
        if (where := (defined[0].name, defined[1])) not in memo:
            memo[where] = read_signatures(modules, *defined)
        found[key] = memo[where]
    return {key: read for key, read in found.items() if read}


def classes(catalog: Index, path: Path) -> frozenset[str]:
    """Find the installed classes the file at `path` passes as arguments (`dtype=np.float64`).

    A class, or an alias of one (`np.int32 = signedinteger[_32Bit]`), through any re-exports.

    Returns:
      Each as the file writes it; none for a file `catalog` doesn't have.

    """
    modules: dict[str, Module] = catalog.modules
    target: Module | None
    if path.suffix != SUFFIX or (target := modules.get(module_name(path))) is None:
        return frozenset()
    reader: Reader = Reader(modules)
    return frozenset(name for name in target.passed if reader.is_class(target, name))


class Methods(NamedTuple):
    """Installed classes' methods a file may call whose arguments or instance decide their type.

    `signatures`: each one's, by the class as the file writes it and the method (`np.ndarray.astype`);
    `parameters`: each such class's type parameters, in order, which a receiver's type binds;
    `lineage`: each installed class the file names, as it writes it, with where it's defined and its
    ancestors' (`numpy.float64`, `numpy.floating`, ...), `?` last where a base can't be followed: a
    receiver's type is matched against a method's `self` by them. `aliases`: each public alias of an
    installed generic class the file names (`npt.NDArray`), whose methods are its class's; the
    classes its expansion names are in `lineage` by their paths (`numpy.dtype`).
    """

    signatures: dict[str, tuple[ReadSignature, ...]]
    parameters: dict[str, tuple[str, ...]]
    lineage: dict[str, tuple[str, ...]]
    aliases: dict[str, Expansion]


def methods(catalog: Index, path: Path, guarded: Mapping[str, Guarded] | None = None) -> Methods:
    """Find the methods the file at `path` calls that an installed class it names declares (see `Methods`).

    Named through its imports, those under `if TYPE_CHECKING:` included, and those its fixes will add
    there (`guarded`, see `project.Imported`): a return type spelled through one is a receiver's.

    Returns:
      Them; none for a file `catalog` doesn't have.

    """
    modules: dict[str, Module] = catalog.modules
    found: Methods = Methods({}, {}, {}, {})
    target: Module | None
    if path.suffix != SUFFIX or (target := modules.get(module_name(path))) is None or not target.method_calls:
        return found
    reader: Reader = Reader(modules)
    memo: Memo = MEMO.of(modules)
    spelled: str
    origin: Origin
    names: dict[str, Origin] = {
        **{name: found.origin for name, found in (guarded or {}).items()},
        **target.guarded,
        **target.names,
    }
    names.update(_packages(modules, names))
    for spelled, origin in classnames.classes(modules, names, memo.packages):
        _class_methods(found, reader, target, spelled, origin)
    alias: Origin
    for spelled, alias in classnames.classes(modules, names, memo.packages, aliases=True):
        if alias not in memo.expansions:
            memo.expansions[alias] = reader.expansion(alias)
        expanded: Expanded | None
        if (expanded := memo.expansions[alias]) is None:
            continue
        paths: tuple[tuple[str, Origin], ...]
        origin, found.aliases[spelled], paths = expanded
        _class_methods(found, reader, target, spelled, origin)
        path_named: str
        for path_named, origin in paths:
            found.lineage[path_named] = _lineage(reader, origin)
    return found


def _packages(modules: Mapping[str, Module], names: Mapping[str, Origin]) -> dict[str, Origin]:
    """Find the installed packages a file takes names of without importing them (`from grids import make`).

    Returns:
      Each, by its name, where the file binds it to nothing: a fix may import one's alias, which
      is then a receiver's type, named by its dotted path.

    """
    tops: set[str] = {origin[0].partition(".")[0] for origin in names.values()} - set(names)
    return {top: (top, None) for top in tops if top in modules and modules[top].installed}


def _lineage(reader: Reader, origin: Origin) -> tuple[str, ...]:
    """Find an installed class's lineage (see `Methods.lineage`), and the methods it has, once.

    Returns:
      It.

    """
    memo: Memo = MEMO.of(reader.modules)
    if origin not in memo.lines:
        memo.lines[origin] = tuple(dict.fromkeys(reader.lineage(origin, 0)))
        memo.names[origin] = classnames.method_names(reader.modules, memo.lines[origin])
    return memo.lines[origin]


def _class_methods(found: Methods, reader: Reader, target: Module, spelled: str, origin: Origin) -> None:
    """Add an installed class's methods `target` calls, as it writes the class (`spelled`), to `found`."""
    found.lineage[spelled] = _lineage(reader, origin)
    memo: Memo = MEMO.of(reader.modules)
    module: Module = reader.modules[origin[0]]
    klass: Class = cast("Declarations", module.declared).classes[origin[1] or ""]
    name: str
    for name in sorted(memo.names[origin] & target.method_calls):
        if (origin, name) not in memo.methods:
            # Its lineage has the method: the class or a base declares it.
            memo.methods[origin, name] = cast(
                "tuple[ReadSignature, ...]",
                reader.method(module, klass, name, 0),
            )
        found.signatures[f"{spelled}.{name}"] = memo.methods[origin, name]
        found.parameters[spelled] = tuple(param for param, _ in klass.params)
        attr: str
        each: tuple[Signature, ...]
        # What it reads of the method's return, off the call (see `chained`).
        for attr, each in chained.attributes(module, klass, name, target.attributes).items():
            found.signatures[f"{spelled}.{chained.key(name, attr)}"] = read_all(
                reader,
                module,
                each,
                frozenset(param for param, _ in klass.params),
                dict(klass.params),
            )


def read_signatures(modules: Mapping[str, Module], module: Module, name: str) -> tuple[ReadSignature, ...]:
    """Read an installed function's signatures as the tables hold theirs.

    Returns:
      Them.

    """
    # Found by its signatures (`project.definition`): an installed module's, or a checked file's overloads.
    return read_all(Reader(modules), module, own_overloads.written(module, name), frozenset(), {})
