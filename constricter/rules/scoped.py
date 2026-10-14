# SPDX-License-Identifier: MIT
"""What a scope (`constricter.rules.scope.Scope`) is checked with, and what it holds as it's checked.

Its module's `Settings` (and the parameters' types given from outside, `Seeded`); its `Kind` of
body; its plain bindings (`Assignments`), which LVA012 and `--fix` read; and what `--fix` has typed
in it so far (`Inferred`), late fixes included (`Late`).
"""

import ast
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from typing import NamedTuple, TypeAlias

from constricter.fix.core.known import Hints, Inference, Known, Passed, Typed
from constricter.fix.values import aliased
from constricter.fix.values.doubts import (
    Facts,
)
from constricter.offences import (
    Checks,
)
from constricter.rules.flow import Hierarchy, members
from constricter.rules.quoted import parsed as unquoted
from constricter.rules.quoted import unqualified
from constricter.rules.rebinding import REBOUND
from constricter.rules.syntax import FunctionDef, Start


@dataclass(frozen=True)
class Settings:
    """One module's options, and its source lines (to place a `**rest` capture)."""

    # The checks asked for (a module written for Python 2 counts its `# type:` comments whatever they say).
    checks: Checks
    lines: Sequence[str]
    known: Known  # what the module declares that `--fix` infers types from
    hierarchy: Hierarchy  # which types are narrower than which, for value flow
    owners: dict[int, str]  # each method's class, by `id()`, to type its `self`, for `--fix`
    # Where each of the module's `:=` starts, in source order: most modules have none, and needn't be
    # looked through for one; a statement's part without one needn't be either.
    walruses: tuple[Start, ...]
    # Type checkers' types, for what `--fix` can't type (`--infer-with`): each checker's, in order.
    hints: tuple[Hints, ...] = ()
    facts: Facts = field(default_factory=Facts)  # what a type checker sees otherwise (see `doubts`)
    parameters: "Seeded | None" = None  # what its functions' parameters are given from outside them


class Seeded(NamedTuple):
    """The types a module's functions' unannotated parameters are given from outside them: guesses.

    `callers`: what every call passes each parameter of its top-level functions, by `id()` (see
    `constricter.fix.index.callers`); `fixtures`: the pytest fixtures its tests can take, each one's
    value's type (see `constricter.fix.index.fixtures`). And `module`: the names the module binds
    once, at its top level, each with its type there, which every function reads it as. `marked`:
    what a class's `parametrize` gives each of its methods, by `id()` (see `calls.marked`).
    """

    callers: Mapping[int, Mapping[str, Passed]] = {}
    fixtures: Mapping[str, Passed] = {}
    module: Mapping[str, Passed] = {}
    marked: Mapping[int, Mapping[str, Passed]] = {}


class Kind(NamedTuple):
    """What kind of body a scope is: the code its unannotated names get, and whether `--fix` fixes it."""

    unannotated: str  # LVA001 in a function, LVA004 in a module or class body
    # A class body isn't: annotating a dataclass's variable makes it a field. Only a plain class's
    # variable typed by its value is fixed there (see `constricter.fix.values.classvars`).
    fixable: bool
    function: FunctionDef | None = None  # a function's own: its body, its returns
    owner: str | None = None  # a class body's: its class

    def body(self) -> Sequence[ast.stmt]:
        """Find the function's body.

        Returns:
          It, or nothing for a module or class body's scope.

        """
        return () if self.function is None else self.function.body


# A name's first plain assignment: its target, its value, and the value's inferred type, if any.
Plain: TypeAlias = tuple[ast.Name, ast.expr, Inference | None]
Bare: TypeAlias = tuple[ast.AnnAssign, Inference | None]
# One plain assignment: where, and whether it's in a loop's body.
Placed: TypeAlias = tuple[tuple[int, int], bool]


@dataclass
class Assignments:
    """A scope's plain `name = value` (or `name: T = value`) bindings, for LVA012 and `--fix`.

    `chained`: where the statement starts that first binds a name it can't annotate (`a = b = 0`,
    a loop's, an unpacking's, a `with`'s): a fix made late (`optional`, `filled`) declares it there.
    """

    found: dict[str, list[Placed]] = field(default_factory=dict[str, list[Placed]])  # each name's
    looping: int = 0  # how many loops deep the statement being visited is
    empty: dict[str, str] = field(default_factory=dict[str, str])  # names first bound empty: their kind
    chained: dict[str, tuple[int, int]] = field(default_factory=dict[str, tuple[int, int]])
    widened: set[str] = field(default_factory=set[str])  # the names a marked line annotates (see `widened`)
    # Each name `late.widens` may offer a wider type: its target, its value (what a loop's, an
    # unpacking's or a `with`'s is taken from: then in `chained` too), and the type `--fix` infers.
    plain: dict[str, "Plain"] = field(default_factory=dict[str, "Plain"])
    # Each marked declaration with no value (`x: Any`, before a loop), and what its name is bound to.
    bare: dict[str, "Bare"] = field(default_factory=dict[str, "Bare"])


# A name typed late: its type, and what that rests on if it's a guess (`FIX_KINDS`).
Late: TypeAlias = tuple[str, frozenset[str]]


@dataclass
class Inferred:
    """What `--fix` knows of a scope's names so far."""

    types: Typed = field(default_factory=Typed)  # each known type, for `x = y`'s
    guesses: set[str] = field(default_factory=set[str])  # `types` from an unsafe fix: copies are too
    # Each guess's guessing mechanisms (`FIX_KINDS`), for `unsafe-fix-select` to trust or not.
    origins: dict[str, frozenset[str]] = field(default_factory=dict[str, frozenset[str]])
    returns: list[ast.expr | None] = field(default_factory=list[ast.expr | None])  # its `return`s' values
    # Its `self.x = value` assignments: each attribute, and its value.
    assigned: list[tuple[str, ast.expr]] = field(default_factory=list[tuple[str, ast.expr]])
    # Names typed only once the whole scope was seen (a container filled later, `None` rebound): the
    # type, and what it rests on if a guess; and those it was checked again knowing.
    late: dict[str, Late] = field(default_factory=dict[str, "Late"])
    seeded: dict[str, Late] = field(default_factory=dict[str, "Late"])
    # The names declared type aliases (`X: TypeAlias = ...`): `TypeAlias` isn't their values' type.
    aliases: set[str] = field(default_factory=set[str])
    unions: Mapping[str, str] = field(default_factory=dict[str, str])  # see `Indirect.unions`

    def members(self, annotation: str) -> frozenset[str]:
        """Split a type into its union's members, an alias of a union read as the union it names.

        Returns:
          Them; none for a type that can't be read.

        """
        return members(self.unions.get(annotation, annotation)) or frozenset()

    def declare(self, name: str, annotation: ast.expr, held: str | None = None) -> None:
        """Record the type `name` is annotated with: its own from here on, or an alias's declaration.

        A `Final[T]`'s or a `ClassVar[T]`'s is `T`, and a bare one's its value's (`held`, if known).
        """
        text: str | None = unqualified(unquoted(annotation)) or held
        if aliased.declares(annotation):
            self.aliases.add(name)
        elif text:
            _ = self.types.setdefault(name, text)

    def learn(
        self,
        name: str,
        annotation: str,
        origins: frozenset[str] | None,
        *,
        again: bool = False,
    ) -> None:
        """Record `name`'s type, the first time it's typed; `origins`: what it rests on, if it's a guess.

        `again`: whether it was bound before, to a value of no known type, which it may still hold
        (another branch's): its type is then a guess, resting on `rebound`.
        """
        if name in self.types:
            return
        self.types[name] = annotation
        if origins is None and again:
            origins = frozenset({REBOUND})
        if origins is not None:
            self.guess(name, origins)

    def guess(self, name: str, origins: frozenset[str]) -> None:
        """Take what's inferred from `name` from here on for a guess, resting on `origins`."""
        self.guesses.add(name)
        self.origins[name] = origins

    def rebound(self, name: str, typed: str | None, guess: Late | None = None) -> None:
        """Record `name` bound again, to a value of type `typed` (`None`: unknown).

        A type checker narrows a name to what it's assigned: from here on it's `typed`, if known. That's
        certain for a member of a declared union (`int | None`, then `1`), which every checker narrows;
        otherwise (mypy narrows nothing else, and an unknown value may be anything) what's inferred
        from it is a guess, resting on `rebound`. `guess`: the value's type where it's only a guess
        (`config = config or Config()`), and what that rests on: the name's from here on, as one. A
        union bound to a value of no known type is narrowed to that: the name has no type until its
        branch ends.
        """
        current: str | None = self.types.get(name)
        self.types.hold(name, None)
        if current is None or typed == current:
            return
        if typed is None and guess is not None:
            self.types[name] = guess[0]
            self.guess(name, self.origins.get(name, frozenset()) | guess[1])
            return
        union: frozenset[str] = self.members(current)
        if typed is None and len(union) > 1:
            self.types.forget(name)  # its type again past a branch (see `rejoined`), as a guess
        if typed is not None:
            self.types[name] = typed
            if typed in union and len(union) > 1:
                return
        if name not in self.guesses:
            self.guess(name, frozenset({REBOUND}))

    def rejoined(self, before: Mapping[str, str], untyped: frozenset[str]) -> None:
        """Take each name a branch (`if`, a loop, `try`, `match`) retyped back to its type `before` it.

        The branch may not have run: past it, a name is what it was, or what the branch made it. That's
        its type before, certainly, if that's a union the branch's type is a member of (`int | None`,
        narrowed to `int` inside `if`); otherwise `rebound` already made it a guess, as it is where
        the branch left it no type. One of `untyped`, bound before the branch or in an arm of it to a
        value of no known type, may still hold it: it has none past it.
        """
        name: str
        annotation: str
        for name, annotation in before.items():
            if name not in self.types and name not in self.guesses:
                self.guess(name, frozenset({REBOUND}))
            self.types[name] = annotation
        for name in self.types.keys() & untyped:
            self.forget(name)

    def forget(self, name: str) -> None:
        """Take `name` for a value of no known type from here on."""
        self.types.forget(name)
        self.guesses.discard(name)
        _ = self.origins.pop(name, None)
