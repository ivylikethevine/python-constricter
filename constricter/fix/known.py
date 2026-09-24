# SPDX-License-Identifier: MIT
"""What `--fix` knows: a module's declarations it infers from (`Known`), and what it infers (`Inference`)."""

import builtins
from collections.abc import Mapping
from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Final, NamedTuple, TypeAlias

from constricter.offences import MAX_LENGTH
from constricter.rules.annotations import free_of, free_of_all

_BUILTINS: Final = frozenset(dir(builtins))
_DOT: Final = "."
# What a name refers to: a module and an attribute of it (`None`: the module itself).
Origin: TypeAlias = tuple[str, str | None]


class Guarded(NamedTuple):
    """A name a file can write only in an annotation: imported under `if TYPE_CHECKING:` (see `project`).

    `origin`: what it refers to; `statement`: the import to add for it, or `None` if the file has it.
    """

    origin: Origin
    statement: str | None


class Classes(NamedTuple):
    """Classes' instance attributes (and properties) and methods' returns, by the class's name as spelled.

    What `classes` and `method_returns` read from a module, and `project.imported` adds for the
    classes a file imports from other checked files.
    """

    attributes: Mapping[str, Mapping[str, str]]
    methods: Mapping[str, Mapping[str, str]]


@dataclass
class ImportPlan:
    """How a module can name a library type, and the imports that takes (see `fix.imports.plan`).

    `bound`: each name its imports bind, and what that is (`io`, `io.BytesIO`); `taken`: every name
    bound anywhere in it; `after`: the line added imports go after; `defined`: each name it binds
    at its top level (an import, a class, a function, an assignment), and the line it's first bound
    on; `added`: each name an added import binds, and that import's statement, as `spell` chose them.
    `guarded`: the names other checked files' types are written with that the module imports (or is
    to import) under `if TYPE_CHECKING:` alone; `block`: the first and last line of the body of the
    `if TYPE_CHECKING:` among its leading imports, if it has one (else zeros); `postponed`: whether
    it has `from __future__ import annotations`, so none of its annotations is evaluated.
    """

    bound: Mapping[str, str]
    taken: frozenset[str]
    after: int
    defined: Mapping[str, int] = field(default_factory=dict[str, int])
    added: dict[str, str] = field(default_factory=dict[str, str])
    guarded: Mapping[str, Guarded] = field(default_factory=dict[str, Guarded])
    block: tuple[int, int] = (0, 0)
    postponed: bool = False
    values: frozenset[str] = frozenset()  # names it binds as values somewhere (see `imports._taken`)

    def spell(self, qualified: str) -> str | None:
        """Name `qualified` (`io.BufferedReader`) in this module, adding an import if it has to.

        Through an import it has (`io.BufferedReader` after `import io`, `BufferedReader` after
        `from io import BufferedReader`), else a new `from io import BufferedReader`, else a new
        `import io`, but only binding a name nothing in the module binds.

        Returns:
          The name, or `None` if every way to write it is taken.

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
        statement: str = f"from {module} import {name}"
        if self._free(name, statement):
            self.added[name] = statement
            return name
        statement = f"import {module}"
        if _DOT not in module and self._free(module, statement):
            self.added[module] = statement
            return qualified
        return None

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

    `typing.cast` (see `casts`), and the standard library's (see `stdlib.origins`).
    """

    casts: frozenset[str] = frozenset()
    stdlib: Mapping[str, str] = MappingProxyType({})
    plan: ImportPlan | None = None  # how to name a type the module doesn't import yet


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


class ClassSide(NamedTuple):
    """What each class the module defines offers on the class itself: `class_attributes`, `class_methods`."""

    attributes: Mapping[str, Mapping[str, str]]
    methods: Mapping[str, Mapping[str, str]]


@dataclass(frozen=True)
class Known:
    """What a module declares that `--fix` can infer a value's type from.

    `calls`: its functions' return types (`returns`, plus other modules', see `project.calls`).
    `factories`: names that build a class or special form rather than an instance of it (see
    `factories`), so a call to one is never guessed to construct one. `classes` and `methods`: each
    class's annotated attributes (see `classes`) and methods' return types (see `method_returns`).
    `awaits`: what awaiting a call to each of its `async def`s gives (see `awaited_returns`).
    `class_side`: what `cls.x` and `cls.method()` give in a classmethod, where `cls` is `type[C]`
    (see `ClassSide`). `names`: how it names library functions (see `LibraryNames`). `returned`: what
    its unannotated functions return (see `Returned`).
    """

    calls: Mapping[str, str]
    factories: frozenset[str]
    classes: Mapping[str, Mapping[str, str]]
    methods: Mapping[str, Mapping[str, str]]
    awaits: Mapping[str, str] = field(default_factory=dict[str, str])
    class_side: "ClassSide" = field(default_factory=lambda: ClassSide({}, {}))
    names: LibraryNames = field(default_factory=LibraryNames)
    max_length: int = MAX_LENGTH  # the longest tuple display typed element by element (LVA011's)
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
    (see `Guarded`) refers to.
    """

    # Plain `dict`s, not `MappingProxyType`s: the CLI's worker processes are sent them, pickled.
    calls: Mapping[str, str] = {}
    guesses: Mapping[str, frozenset[str]] = {}
    names: Mapping[str, Origin] = {}


class Hints(NamedTuple):
    """A type checker's inlay hints for one file (`--infer-with`): which checker, and each type.

    Each hint's type is its text as the checker printed it (`int`, `list[str]`), by where the name
    it types ends: its line (from 1) and UTF-8 byte column, as `ast`'s `end_col_offset`.
    """

    checker: str = ""
    # A plain `dict`, not a `MappingProxyType`: the CLI's worker processes are sent it, pickled.
    types: Mapping[tuple[int, int], str] = {}


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


class Outside(NamedTuple):
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
    `constricter.fix.callers`).
    """

    calls: Mapping[str, str] = {}
    classes: Classes | None = None
    hints: tuple[Hints, ...] = ()  # each checker's, in the order they were named
    type_vars: frozenset[str] = frozenset()
    returned: Returns = Returns()
    guarded: Mapping[str, Guarded] = {}
    generics: frozenset[str] = frozenset()  # other checked files' generic classes, as it spells them
    callees: Mapping[str, Callee] = {}
    parameters: Mapping[str, Mapping[str, Passed]] = {}  # see `Seeds`

    def usable(self, taken: frozenset[str]) -> "Outside":
        """Drop what other files offer whose type needs a name imported that the module binds already.

        That's a name to import under `if TYPE_CHECKING:` (see `Guarded`) that the module binds anywhere
        else, a function's local or parameter included: the import would shadow it, or it the import.

        Returns:
          What's left.

        """
        clashing: frozenset[str] = frozenset(
            name for name, found in self.guarded.items() if found.statement is not None and name in taken
        )
        if not clashing:
            return self
        members: Classes | None = self.classes
        return Outside(
            free_of(self.calls, clashing),
            None
            if members is None
            else Classes(free_of_all(members.attributes, clashing), free_of_all(members.methods, clashing)),
            self.hints,
            self.type_vars,
            Returns(free_of(self.returned.calls, clashing), self.returned.guesses, self.returned.names),
            {name: found for name, found in self.guarded.items() if name not in clashing},
            self.generics,
            self.callees,
            self.parameters,
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
