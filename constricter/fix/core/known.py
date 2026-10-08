# SPDX-License-Identifier: MIT
"""What `--fix` knows: a module's declarations it infers from (`Known`), and what it infers (`Inference`)."""

import builtins
import re
from collections.abc import Mapping
from dataclasses import dataclass, field
from types import MappingProxyType
from typing import TYPE_CHECKING, Final, NamedTuple, TypeAlias

from constricter.fix.core.inherited import Beyond, Lineage
from constricter.fix.core.signatures import Expansion, ReadSignature
from constricter.offences import MAX_LENGTH, VAGUE
from constricter.rules.annotations import free_of, free_of_all, roots

if TYPE_CHECKING:
    from typing_extensions import override  # `typing.override` is 3.12+
else:

    def override(func: object) -> object:
        """Mark an override (for type checkers only).

        Returns:
          `func`, unchanged.

        """
        return func


_BUILTINS: Final = frozenset(dir(builtins))
_DOT: Final = "."
_NAME: Final = re.compile(r"[A-Za-z_]\w*")  # each name in a return's template
# What a name refers to: a module and an attribute of it (`None`: the module itself).
Origin: TypeAlias = tuple[str, str | None]
# How a return template starts that's the type itself, as the module calling it writes it: a
# checked file's overload's (see `constricter.fix.index.stubbed.overloaded`).
SPELLED: Final = "="


# A `dict` itself, not a `UserDict`: every inference reads it, as fast as a `dict` is read.
class Typed(dict[str, str]):  # ruff: ignore[subclass-builtin]
    """A scope's names' types so far, counting each change: what's inferred of a value holds till then."""

    version: int = 0

    @override
    def __setitem__(self, name: str, annotation: str) -> None:
        """Type `name`, and count it."""
        self.version += 1
        super().__setitem__(name, annotation)

    @override
    def setdefault(self, name: str, annotation: str = "", /) -> str:
        """Type `name` if nothing has, and count it.

        Returns:
          Its type.

        """
        self.version += 1
        return super().setdefault(name, annotation)

    def taking(self, others: Mapping[str, str]) -> None:
        """Type each of `others`' names, and count it."""
        self.version += 1
        super().update(others)

    def forget(self, name: str) -> None:
        """Leave `name` with no type, and count it."""
        self.version += 1
        _ = super().pop(name, None)


class Guarded(NamedTuple):
    """A name a file can write only in an annotation: imported under `if TYPE_CHECKING:` (see `project`).

    `origin`: what it refers to; `statement`: the import to add for it, or `None` if the file has it.
    """

    origin: Origin
    statement: str | None


class Checking(NamedTuple):
    """A module's imports for type checking alone: where they go, whose types need one, and its own.

    `block`: the first and last line of the body of the `if TYPE_CHECKING:` among its leading
    imports, if it has one (else zeros); `lazy`: the top-level packages only its functions import,
    which may not be there to import when the module is (another platform's `pwd`); `bound`: what
    the imports under its top-level `if TYPE_CHECKING:`s bind, each name's dotted origin.
    """

    block: tuple[int, int] = (0, 0)
    lazy: frozenset[str] = frozenset()
    bound: Mapping[str, str] = MappingProxyType({})


class Classes(NamedTuple):
    """Classes' instance attributes (and properties) and methods' returns, by the class's name as spelled.

    What `classes` and `method_returns` read from a module, and `project.imported` adds for the
    classes a file imports from other checked files.
    """

    attributes: Mapping[str, Mapping[str, str]]
    methods: Mapping[str, Mapping[str, str]]


@dataclass
class ImportPlan:
    """How a module can name a library type, and the imports that takes (see `fix.core.imports.plan`).

    `bound`: each name its imports bind, and what that is (`io`, `io.BytesIO`); `taken`: every name
    bound anywhere in it; `after`: the line added imports go after; `defined`: each name it binds
    at its top level (an import, a class, a function, an assignment), and the line it's first bound
    on; `added`: each name an added import binds, and that import's statement, as `spell` chose them.
    `guarded`: the names other checked files' types and a type checker's hints are written with
    that the module imports (or is to import) under `if TYPE_CHECKING:` alone; `checking`: its own
    such imports, where one goes, and whose types need one (see `Checking`); `postponed`: whether
    it has `from __future__ import annotations`, so none of its annotations is evaluated.
    """

    bound: Mapping[str, str]
    taken: frozenset[str]
    after: int
    defined: Mapping[str, int] = field(default_factory=dict[str, int])
    added: dict[str, str] = field(default_factory=dict[str, str])
    guarded: Mapping[str, Guarded] = field(default_factory=dict[str, Guarded])
    checking: Checking = field(default_factory=Checking)
    postponed: bool = False
    values: frozenset[str] = frozenset()  # names it binds as values somewhere (see `imports.taken_names`)

    def spell(self, qualified: str) -> str | None:
        """Name `qualified` (`io.BufferedReader`) in this module, adding an import if it has to.

        Through an import it has (see `named`), for type checking alone too (`checking`, or one
        `guarded` already), else a new `from io import BufferedReader`, else a new `import io`, but
        only binding a name nothing in the module binds. Under `if TYPE_CHECKING:` for a module in
        `checking.lazy`.

        Returns:
          The name, or `None` if every way to write it is taken.

        """
        found: str | None
        if (found := self.named(qualified) or self._checked(qualified)) is not None:
            return found
        module: str
        name: str
        module, _, name = qualified.rpartition(".")
        statement: str = f"from {module} import {name}"
        if module.partition(_DOT)[0] in self.checking.lazy:
            return name if self.guard(name, (module, name), statement) else None
        if self._free(name, statement):
            self.added[name] = statement
            return name
        statement = f"import {module}"
        if _DOT not in module and self._free(module, statement):
            self.added[module] = statement
            return qualified
        return None

    def named(self, qualified: str) -> str | None:
        """Name `qualified` (`io.BufferedReader`) through an import the module has.

        `io.BufferedReader` after `import io`, `BufferedReader` after `from io import BufferedReader`.

        Returns:
          The name, or `None` if no import of its names it.

        """
        module: str
        name: str
        module, _, name = qualified.rpartition(".")
        bound: str
        origin: str
        for bound, origin in self.bound.items():
            if origin == qualified:
                return bound
        for bound, origin in self.bound.items():
            if origin == module:
                return f"{bound}.{name}"
        return None

    def _checked(self, qualified: str) -> str | None:
        """Name `qualified` through an import for type checking alone: one it has, or is to have.

        Returns:
          The name, or `None` if none binds it, or the module binds that name to a value too.

        """
        origins: dict[str, str] = dict(self.checking.bound)
        bound: str
        each: Guarded
        for bound, each in self.guarded.items():
            origins[bound] = _DOT.join(part for part in each.origin if part)
        return next(
            (bound for bound, origin in origins.items() if origin == qualified and bound not in self.values),
            None,
        )

    def guard(self, name: str, origin: Origin, statement: str) -> bool:
        """Let annotations be written with `name`, bound to `origin` for type checking alone.

        By the import `statement`, to add under `if TYPE_CHECKING:`. A name already guarded must be
        so by the same statement; a new import must bind a name nothing in the module binds.

        Returns:
          Whether they can.

        """
        found: Guarded | None
        if (found := self.guarded.get(name)) is not None:
            return found.statement == statement
        if name in self.added or not self._free(name, statement):
            return False
        # A new mapping: the one it had is the file's `Outside.guarded`, which other files' types read.
        self.guarded = {**self.guarded, name: Guarded(origin, statement)}
        return True

    def _free(self, name: str, statement: str) -> bool:
        """Check that `statement` may bind `name`: it already does, or nothing (not a builtin) does.

        Returns:
          Whether it may.

        """
        if name in self.added:
            return self.added[name] == statement
        return name not in self.taken and name not in _BUILTINS and name not in self.guarded


class LibraryNames(NamedTuple):
    """How the module names the library functions `--fix` knows.

    `typing.cast` (see `casts`), and the standard library's (see `stdlib.origins`). `installed`: the
    installed packages' functions it calls whose arguments decide their type, by the call's name as
    written, each with its signatures (their classes' methods too, as `np.ndarray.astype`), and
    `classes` the installed classes it passes as arguments, which may bind their type variables;
    `parameters`: those methods' classes' type parameters, which a receiver's type binds; `lineage`:
    the installed classes it names, each with where it and its ancestors are defined, which a
    receiver's type is matched by; `aliases`: the public aliases of installed generic classes it
    names, whose methods are their classes' (see `constricter.fix.index.stubbed`). `starred`: whether
    every Python the module runs on parses an unpacked tuple in a subscript (`tuple[int, *Ts]`,
    3.11's syntax), so an annotation may be written with one.
    """

    casts: frozenset[str] = frozenset()
    stdlib: Mapping[str, str] = MappingProxyType({})
    plan: ImportPlan | None = None  # how to name a type the module doesn't import yet
    installed: Mapping[str, tuple[ReadSignature, ...]] = MappingProxyType({})
    classes: frozenset[str] = frozenset()
    parameters: Mapping[str, tuple[str, ...]] = MappingProxyType({})
    lineage: Mapping[str, tuple[str, ...]] = MappingProxyType({})
    aliases: Mapping[str, Expansion] = MappingProxyType({})
    starred: bool = False


class Returned(NamedTuple):
    """Return types read from unannotated functions' own `return` statements (see `returned`).

    `calls`: the module's functions', by name (certain); `methods`: its classes' methods', by class
    (guesses: a subclass may override one). `guesses`: for a function (by name) or method (`C.m`)
    whose `return`s are themselves guesses, what they rest on (`FIX_KINDS`), which its calls do too.
    `attributes`: its classes' unannotated instance attributes typed by their every `self.x = value`,
    by class (guesses: a subclass or outside code may assign one too); a guessed value's origins are
    in `guesses` as `C.x`.
    """

    calls: Mapping[str, str] = MappingProxyType({})
    methods: Mapping[str, Mapping[str, str]] = MappingProxyType({})
    guesses: Mapping[str, frozenset[str]] = MappingProxyType({})
    attributes: Mapping[str, Mapping[str, str]] = MappingProxyType({})


class Partial(NamedTuple):
    """Declared returns that have a vague part (`tuple[Row, dict[str, Any]]`, `Any`).

    One types a call only as far as `vague` allows (see `Limits.vague`); an unpacking takes its
    parts. `calls`: functions', by the call's name as written; `methods`: classes' methods', by the
    class's name as spelled.
    """

    # Plain `dict`s, not `MappingProxyType`s: the CLI's worker processes are sent them, pickled.
    calls: Mapping[str, str] = {}
    methods: Mapping[str, Mapping[str, str]] = {}


class Indirect(NamedTuple):
    """Declared returns that type something other than a plain call.

    `awaits`: what awaiting a call to each of the module's `async def`s gives (see
    `awaited_returns`); `partial`: those only an unpacking can use (see `Partial`), other checked
    files' too. `tuples`: the named tuples the module names, its own and other checked files', each
    with the tuple unpacking one gives (see `targets.named_tuples`). `unions`: the type aliases of a
    union it names, its own and other checked files', each with the union as its module writes it
    (see `targets.aliased_unions`).
    """

    awaits: Mapping[str, str] = MappingProxyType({})
    partial: Partial = Partial()
    tuples: Mapping[str, str] = MappingProxyType({})
    unions: Mapping[str, str] = MappingProxyType({})


class ClassSide(NamedTuple):
    """What each class the module defines offers beyond its instances' own members.

    On the class itself: `class_attributes`, `class_methods`. From its bases: `lineage`, which base
    an instance takes a method from (see `Lineage`). In its body: `variables`, the plain classes'
    typed by their values, the module's own and those it imports (see `constricter.fix.values.classvars`).
    """

    attributes: Mapping[str, Mapping[str, str]]
    methods: Mapping[str, Mapping[str, str]]
    lineage: Lineage = Lineage()
    variables: Mapping[str, Mapping[str, str]] = MappingProxyType({})


class Limits(NamedTuple):
    """What the rules let an annotation be, which `--fix` writes no further than.

    `max_length`: the longest tuple display typed element by element (LVA011's); `vague`: how vague a
    type may be (LVA005's level, see `annotations.vague_fits`). `marks`: the lines a widening marked,
    whose annotations are vaguer by design, each with its mark's columns (see `rules.widened`).
    """

    max_length: int = MAX_LENGTH
    vague: int = VAGUE
    marks: Mapping[int, tuple[int, int]] = MappingProxyType({})


@dataclass(frozen=True)
class Known:
    """What a module declares that `--fix` can infer a value's type from.

    `calls`: its functions' return types (`returns`, plus other modules', see `project.calls`).
    `factories`: names that build a class or special form rather than an instance of it (see
    `factories`), so a call to one is never guessed to construct one. `classes` and `methods`: each
    class's annotated attributes (see `classes`) and methods' return types (see `method_returns`).
    `indirect`: its declared returns no plain call has (see `Indirect`).
    `class_side`: what `cls.x` and `cls.method()` give in a classmethod, where `cls` is `type[C]`
    (see `ClassSide`). `names`: how it names library functions (see `LibraryNames`). `returned`: what
    its unannotated functions return (see `Returned`).
    """

    calls: Mapping[str, str]
    factories: frozenset[str]
    classes: Mapping[str, Mapping[str, str]]
    methods: Mapping[str, Mapping[str, str]]
    indirect: Indirect = field(default_factory=Indirect)
    class_side: "ClassSide" = field(default_factory=lambda: ClassSide({}, {}))
    names: LibraryNames = field(default_factory=LibraryNames)
    limits: Limits = field(default_factory=Limits)
    returned: Returned = field(default_factory=Returned)

    def is_builtin(self, name: str) -> bool:
        """Check that `name` still means the builtin: nothing in the module binds it (a parameter, say).

        Returns:
          Whether it does; with no import plan (a module not read for one), whether it's a builtin.

        """
        return name in _BUILTINS and (self.names.plan is None or name not in self.names.plan.taken)


class Returns(NamedTuple):
    """What a module's unannotated functions return (`Returned.calls`), for the files importing them.

    `calls`: each function's type, by its name (or, imported, as the importing file spells it: `f`,
    `u.f`); `guesses`: for one whose `return`s are guesses, what they rest on (`FIX_KINDS`);
    `names`: what each name their types use that the module imports for type checking alone
    (see `Guarded`) refers to. `methods`: its classes' methods' (`Returned.methods`), by class (as
    the importing file spells it), a guessed one's origins in `guesses` as `C.m`.
    """

    # Plain `dict`s, not `MappingProxyType`s: the CLI's worker processes are sent them, pickled.
    calls: Mapping[str, str] = {}
    guesses: Mapping[str, frozenset[str]] = {}
    names: Mapping[str, Origin] = {}
    methods: Mapping[str, Mapping[str, str]] = {}


class Offered(NamedTuple):
    """What a type checker's hint would write if its editor accepted it (the hint's own edits).

    `text`: the annotation as it would insert it, which may spell a class through a module the file
    imports (`collections.Counter[str]`, where the hint shows `Counter[str]`); `imports`: the
    imports it would add for the names in it, each a statement binding one name
    (`from shapes import Shape`, `import shapes`).
    """

    text: str
    imports: tuple[str, ...] = ()


class Hints(NamedTuple):
    """A type checker's inlay hints for one file (`--infer-with`): which checker, and each type.

    Or a traced run's types for it (`--infer-from`), of `kind` `traced`: what its fixes rest on.

    Each hint's type is its text as the checker printed it (`int`, `list[str]`), by where the name
    it types ends: its line (from 1) and UTF-8 byte column, as `ast`'s `end_col_offset`.
    `offered`: what each hint that has edits would write (see `Offered`), by the same place.
    """

    checker: str = ""
    # Plain `dict`s, not `MappingProxyType`s: the CLI's worker processes are sent them, pickled.
    types: Mapping[tuple[int, int], str] = {}
    offered: Mapping[tuple[int, int], Offered] = {}
    kind: str = "checker"


# An argument's type, and what it rests on if it's a guess (`FIX_KINDS`; none: it's certain).
Passed: TypeAlias = tuple[str, frozenset[str]]
# A module's functions' parameters every call passes one type: each one's, by name, by function.
Seeds: TypeAlias = Mapping[str, Mapping[str, Passed]]


class Call(NamedTuple):
    """One call to a checked file's function: what `--fix` knows each argument's type to be (`None`: unknown).

    `unpacked`: whether it passes `*args` or `**kwargs`, whose arguments can't be matched.
    """

    positional: tuple[Passed | None, ...] = ()
    keywords: tuple[tuple[str, Passed | None], ...] = ()
    unpacked: bool = False


Callee: TypeAlias = tuple[str, str]  # a checked file's function: its module and name


class Observed(NamedTuple):
    """What a module does with checked files' functions whose parameters aren't all annotated.

    `calls`: each call to one, by the function; `escaped`: those it uses other than by calling them
    (a callback, a stored reference), whose callers can't be known.
    """

    # Plain `dict`s and tuples, not `MappingProxyType`s: the CLI's worker processes send them back, pickled.
    calls: Mapping[Callee, tuple[Call, ...]] = {}
    escaped: frozenset[Callee] = frozenset()


@dataclass(frozen=True, slots=True, kw_only=True)
class Outside:  # pylint: disable=too-many-instance-attributes
    """What the CLI knows of a file from outside it, for `--fix`.

    `calls`: the return types of functions other checked files define, `returned` those of their
    unannotated functions (see `Returns`), and `classes` their classes' attributes and methods'
    returns, as the file spells them (see `project.imported`); `hints`, a
    type checker's types for what `--fix` can't type itself (`--infer-with`); `type_vars`, the names
    it imports that are type variables where they're defined (see `project.type_vars`), which a
    type its own functions declare can't be written with outside them; `guarded`, the names those
    types are written with that it can use in an annotation alone (see `Guarded`); `generics`, the
    generic classes it imports from them, which a fix mustn't write bare. `callees`: the functions of
    checked files it may call whose parameters aren't all annotated, as it spells them (`f`, `u.f`);
    `parameters`: for its own such functions, each parameter every call passes one type (see
    `constricter.fix.index.callers`). `plain`: which of its own classes are plain, as the index of checked
    files settles it (`None`: as the file alone sees, see `constricter.fix.values.classvars`); `members`:
    the variables of the plain classes it imports from them, typed by their values, as it spells
    each class. `same`: each group of ways it spells one class or alias another module defines
    (`CoreSchema`, `core_schema.CoreSchema`; see `linked.same`). `partial`: the returns of other
    checked files' functions and methods that only an unpacking can use (see `Partial`). `tuples`:
    the named tuples it imports from them, as it spells each (see `Indirect.tuples`), and `unions`
    their type aliases of a union (see `Indirect.unions`). `untyped`: the functions it calls of
    theirs that declare no return, as it spells each call (see `linked.untyped`).
    """

    calls: Mapping[str, str] = field(default_factory=dict[str, str])
    classes: Classes | None = None
    hints: tuple[Hints, ...] = ()  # each checker's, in the order they were named
    type_vars: frozenset[str] = frozenset()
    returned: Returns = field(default_factory=Returns)
    guarded: Mapping[str, Guarded] = field(default_factory=dict[str, Guarded])
    generics: frozenset[str] = frozenset()  # other checked files' generic classes, as it spells them
    callees: Mapping[str, Callee] = field(default_factory=dict[str, Callee])
    # See `Seeds`
    parameters: Mapping[str, Mapping[str, Passed]] = field(
        default_factory=dict[str, Mapping[str, Passed]],
    )
    # See `LibraryNames.installed`
    overloaded: Mapping[str, tuple[ReadSignature, ...]] = field(
        default_factory=dict[str, tuple[ReadSignature, ...]],
    )
    installed_classes: frozenset[str] = frozenset()  # see `LibraryNames.classes`
    # See `LibraryNames.parameters`
    installed_parameters: Mapping[str, tuple[str, ...]] = field(default_factory=dict[str, tuple[str, ...]])
    # See `LibraryNames.lineage`
    installed_lineage: Mapping[str, tuple[str, ...]] = field(default_factory=dict[str, tuple[str, ...]])
    # See `LibraryNames.aliases`
    installed_aliases: Mapping[str, Expansion] = field(
        default_factory=dict[str, Expansion],
    )
    # The classes it imports under `if TYPE_CHECKING:` alone, which an annotation can name (see `offers.own`).
    checking: Mapping[str, Guarded] = field(default_factory=dict[str, Guarded])
    plain: frozenset[str] | None = None
    members: Mapping[str, Mapping[str, str]] = field(default_factory=dict[str, Mapping[str, str]])
    same: tuple[frozenset[str], ...] = ()
    partial: Partial = field(default_factory=Partial)
    tuples: Mapping[str, str] = field(default_factory=dict[str, str])
    # The pytest fixtures its tests can take: each one's value's type (see `constricter.fix.index.fixtures`).
    fixtures: Mapping[str, Passed] = field(default_factory=dict[str, Passed])
    # Its classes' bases other checked files define: where each one's own end (see `Lineage.beyond`).
    beyond: Mapping[str, Beyond] = field(default_factory=dict[str, Beyond])
    # What awaiting a call of each `async def` it imports from them gives, as it spells the call.
    awaits: Mapping[str, str] = field(default_factory=dict[str, str])
    # The names it imports that another checked module binds by assignment (see `linked.values`).
    values: frozenset[str] = frozenset()
    unions: Mapping[str, str] = field(default_factory=dict[str, str])
    untyped: frozenset[str] = frozenset()

    def usable(self, taken: frozenset[str], present: frozenset[str]) -> "Outside":
        """Drop what other files offer whose type needs a name imported that the module binds already.

        That's a name to import under `if TYPE_CHECKING:` (see `Guarded`) that the module binds anywhere
        else, a function's local or parameter included: the import would shadow it, or it the import.
        A checked file's overloaded function is dropped whole, if any of its signatures returns such a
        type: which one a call takes isn't known here.
        `present`: those it imports so already (see `imports.present`), which `--fix` wrote since the
        files were indexed: each is one the file has.

        Returns:
          What's left.

        """
        guarded: dict[str, Guarded] = {
            name: Guarded(found.origin, None) if name in present else found
            for name, found in self.guarded.items()
        }
        clashing: frozenset[str] = frozenset(
            name for name, found in guarded.items() if found.statement is not None and name in taken
        )
        if not clashing and guarded == self.guarded:
            return self
        members: Classes | None = self.classes
        return Outside(
            calls=free_of(self.calls, clashing),
            classes=None
            if members is None
            else Classes(free_of_all(members.attributes, clashing), free_of_all(members.methods, clashing)),
            hints=self.hints,
            type_vars=self.type_vars,
            returned=Returns(
                free_of(self.returned.calls, clashing),
                self.returned.guesses,
                self.returned.names,
                free_of_all(self.returned.methods, clashing),
            ),
            guarded={name: found for name, found in guarded.items() if name not in clashing},
            generics=self.generics,
            callees=self.callees,
            parameters=self.parameters,
            overloaded={
                callee: signatures
                for callee, signatures in self.overloaded.items()
                if not any(clashing.intersection(_NAME.findall(each.returns or "")) for each in signatures)
            },
            installed_classes=self.installed_classes,
            installed_parameters=self.installed_parameters,
            installed_lineage=self.installed_lineage,
            installed_aliases=self.installed_aliases,
            checking=self.checking,
            plain=self.plain,
            members=self.members,
            same=self.same,
            partial=Partial(
                free_of(self.partial.calls, clashing),
                free_of_all(self.partial.methods, clashing),
            ),
            tuples=free_of(self.tuples, clashing),
            fixtures={name: typed for name, typed in self.fixtures.items() if not roots(typed[0]) & clashing},
            beyond=self.beyond,
            awaits=free_of(self.awaits, clashing),
            values=self.values,
            unions=self.unions,
            untyped=self.untyped,
        )


class Inference(NamedTuple):
    """An annotation `--fix` would add, how the value decided it (`--show-fixes`), and by which means.

    `kinds` are the `FIX_KINDS` ids of every mechanism that decided it, parts included (`[1, 2]`
    is a `container` of `literal`s), for `fix-select` and `fix-ignore`. `reads`: the names,
    attributes and subscripts (as source text) whose own types it takes as they are (`deque([x])`'s
    `x`), which a type checker sees narrowed where the function tests them.
    """

    annotation: str
    reason: str
    kinds: frozenset[str] = frozenset()
    reads: tuple[str, ...] = ()
