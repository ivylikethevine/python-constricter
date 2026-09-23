# SPDX-License-Identifier: MIT
"""What `--fix` knows: a module's declarations it infers from (`Known`), and what it infers (`Inference`)."""

import builtins
from collections.abc import Mapping
from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Final, NamedTuple

from constricter.offences import MAX_LENGTH

_BUILTINS: Final = frozenset(dir(builtins))
_DOT: Final = "."


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
    bound anywhere in it; `after`: the line added imports go after; `added`: each name an added
    import binds, and that import's statement, as `spell` chose them.
    """

    bound: Mapping[str, str]
    taken: frozenset[str]
    after: int
    added: dict[str, str] = field(default_factory=dict[str, str])

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
        return name not in self.taken and name not in _BUILTINS


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
    """

    calls: Mapping[str, str] = MappingProxyType({})
    methods: Mapping[str, Mapping[str, str]] = MappingProxyType({})
    guesses: Mapping[str, frozenset[str]] = MappingProxyType({})


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


class Inference(NamedTuple):
    """An annotation `--fix` would add, how the value decided it (`--show-fixes`), and by which means.

    `kinds` are the `FIX_KINDS` ids of every mechanism that decided it, parts included (`[1, 2]`
    is a `container` of `literal`s), for `fix-select` and `fix-ignore`.
    """

    annotation: str
    reason: str
    kinds: frozenset[str] = frozenset()
