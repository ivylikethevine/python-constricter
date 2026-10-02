# SPDX-License-Identifier: MIT
"""One scope being checked: what it binds and reports, what `--fix` knows of it, and its late fixes."""

import ast
from collections.abc import Iterable, Iterator, Mapping, Sequence
from dataclasses import dataclass, field, replace
from typing import Final, NamedTuple, TypeAlias

from constricter.fix.core.known import Hints, ImportPlan, Inference, Known, Passed
from constricter.fix.libraries import stdlib
from constricter.fix.values import aliased, fills, hinted
from constricter.fix.values.doubts import (
    Facts,
    Owner,
    bare,
    corrected,
    doubts,
    is_constant,
    narrowed_first,
    says_self,
    tested,
    undeclared,
)
from constricter.fix.values.guesses import guessed, guessing
from constricter.fix.values.inference import inference, inferred
from constricter.fix.values.members import parsed
from constricter.fix.values.narrowed import narrowed_at
from constricter.offences import (
    LONG_TUPLE,
    MEMBER,
    NESTED_TYPE,
    UNANNOTATED,
    UNANNOTATED_MEMBER,
    VAGUE_TYPE,
    Checks,
    Edit,
    Fix,
    FixPolicy,
    Offence,
    at,
)
from constricter.rules.annotations import (
    depth,
    is_composite,
    is_vague,
    length,
    node_name,
    roots,
)
from constricter.rules.flow import Finding, Hierarchy, Lifetime, findings, members
from constricter.rules.quoted import written
from constricter.rules.rebinding import REBOUND
from constricter.rules.syntax import FunctionDef, Start

_SELF: Final = "self"
_CLASSMETHOD: Final = "classmethod"
_STATICMETHOD: Final = "staticmethod"
FINAL_KIND: Final = "final"  # the fix kind of LVA012's `Final`
_TYPING_FINAL: Final = "typing.Final"
_LITERAL_DOUBT: Final = frozenset({"literal"})  # a constant's literal, which `doubts` makes a guess
_TYPE_CHECKING: Final = "typing.TYPE_CHECKING"
_READS: Final = (ast.Name, ast.Attribute, ast.Subscript)  # a read of a value a type checker may narrow


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
    # What every call passes each unannotated parameter of its top-level functions, by `id()` (see
    # `constricter.fix.index.callers`): guesses, for what's computed from them.
    parameters: Mapping[int, Mapping[str, Passed]] = field(default_factory=dict[int, Mapping[str, Passed]])


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


# One plain assignment: where, and whether it's in a loop's body.
Placed: TypeAlias = tuple[tuple[int, int], bool]


@dataclass
class Assignments:
    """A scope's plain `name = value` (or `name: T = value`) bindings, for LVA012 and `--fix`.

    `chained`: where each name a chained assignment binds first (`a = b = 0`) starts; its fix,
    whenever it's made (`optional`, `filled`), declares it there, as it can't annotate it.
    """

    found: dict[str, list[Placed]] = field(default_factory=dict[str, list[Placed]])  # each name's
    looping: int = 0  # how many loops deep the statement being visited is
    empty: dict[str, str] = field(default_factory=dict[str, str])  # names first bound empty: their kind
    chained: dict[str, tuple[int, int]] = field(default_factory=dict[str, tuple[int, int]])


# A name typed late: its type, and what that rests on if it's a guess (`FIX_KINDS`).
Late: TypeAlias = tuple[str, frozenset[str]]


@dataclass
class Inferred:
    """What `--fix` knows of a scope's names so far."""

    types: dict[str, str] = field(default_factory=dict[str, str])  # each known type, for `x = y`'s
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

    def declare(self, name: str, annotation: ast.expr) -> None:
        """Record the type `name` is annotated with: its own from here on, or an alias's declaration."""
        if aliased.declares(annotation):
            self.aliases.add(name)
        else:
            _ = self.types.setdefault(name, written(annotation))

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
        (`config = config or Config()`), and what that rests on: the name's from here on, as one.
        """
        current: str | None = self.types.get(name)
        if current is None or typed == current:
            return
        if typed is None and guess is not None:
            self.types[name] = guess[0]
            self.guess(name, self.origins.get(name, frozenset()) | guess[1])
            return
        if typed is not None:
            self.types[name] = typed
            if typed in (members(current) or ()) and len(members(current) or ()) > 1:
                return
        if name not in self.guesses:
            self.guess(name, frozenset({REBOUND}))

    def rejoined(self, before: Mapping[str, str]) -> None:
        """Take each name a branch (`if`, a loop, `try`, `match`) retyped back to its type `before` it.

        The branch may not have run: past it, a name is what it was, or what the branch made it. That's
        its type before, certainly, if that's a union the branch's type is a member of (`int | None`,
        narrowed to `int` inside `if`); otherwise `rebound` already made it a guess.
        """
        name: str
        annotation: str
        for name, annotation in before.items():
            self.types[name] = annotation


class Scope:
    """One function body: names bound so far and offences found."""

    def __init__(
        self,
        declared: set[str],
        nested: list[FunctionDef],
        settings: Settings,
        kind: "Kind | None" = None,
    ) -> None:
        """Start a scope where `declared` are bound already, collecting nested functions into `nested`."""
        self.declared: set[str] = declared
        self.nested: list[FunctionDef] = nested
        self.settings: Settings = settings
        self.kind: Kind = kind or Kind(UNANNOTATED, fixable=True)
        self.offences: list[Offence] = []
        self.first: list[str] = []  # each first binding the rules cover, typed or not
        self.inferred: Inferred = Inferred()  # what `--fix` knows of the names bound so far
        self.flow: dict[str, Lifetime] = {}  # every binding of each name, for value flow
        self.assignments: Assignments = Assignments()  # for LVA012

    def lifetime(self, name: str) -> Lifetime:
        """Find `name`'s value-flow record, starting one if it has none.

        Returns:
          It.

        """
        return self.flow.setdefault(name, Lifetime())

    def bind(
        self,
        name: str,
        where: tuple[int, int],
        code: str | None,
        fix: Fix | None = None,
        typed: str | None = None,
    ) -> None:
        """Bind `name` to a value value flow can't see; unless it's already bound, report `code`.

        `code` is reported at `(line, col)` (`None` means typed), offering `fix` if there's one.
        `typed`: the value's certain type, if `--fix` knows it (a loop's element), which a name
        declared already is then bound to.
        """
        self.lifetime(name).bind(where, None)
        if name in self.declared:
            self.inferred.rebound(name, typed)
        self._first(name, where, code, fix)

    def assign(
        self,
        target: ast.Name,
        code: str | None,
        value: ast.expr,
        chained: ast.stmt | None = None,
    ) -> None:
        """Bind `target` to `value` (`name = value`), offering `--fix`'s annotation for it.

        One of a `chained` assignment's names (`a = b = 0`), which can't be annotated where it's bound,
        is offered a declaration before it instead (`a: int`); not a `Final` one, which needs its value.
        """
        name: str = target.id
        again: bool = name in self.declared
        facts: Facts = self.settings.facts
        fix: Inference | None
        unsafe: bool
        origins: frozenset[str]
        constant: bool = (
            self.kind.function is None
            and self.kind.owner is None
            and is_constant(name)
            and name in facts.passed
            and chained is None
        )
        fix, unsafe, origins = self.valued(value, target.lineno, constant=constant)
        if fix is not None and constant and origins == _LITERAL_DOUBT:
            fix = self._constant(fix)
        # Value flow's type is `--fix`'s own, if certain: worked out once, here, for both.
        certain: str | None = certain_type(self, value, (None if fix is None else fix.annotation, unsafe))
        if self.kind.owner is not None:
            fix, unsafe, origins = self._member(name, fix)
        if fix is None:
            fix, unsafe, origins = self._unvalued(target, value, alias=chained is None and not again)
        self.lifetime(name).bind(
            at(target),
            certain,
            (fix.annotation, origins) if fix is not None and unsafe else None,
        )
        self.assigned(name, at(target))
        if again:
            self.inferred.rebound(name, certain, (fix.annotation, origins) if fix and unsafe else None)
        kind: str | None
        if (kind := fills.empty(value)) is not None:
            _ = self.assignments.empty.setdefault(name, kind)
        if chained is not None and not again:
            _ = self.assignments.chained.setdefault(name, (chained.lineno, chained.col_offset))
        self._first(
            name,
            at(target),
            code,
            None if fix is None else self.placed(name, fix, origins, unsafe=unsafe),
        )
        if fix is not None and aliased.declares(parsed(fix.annotation)):
            self.inferred.aliases.add(name)  # `TypeAlias` isn't its value's type
        elif fix is not None:
            self.inferred.learn(name, fix.annotation, origins if unsafe else None, again=again)

    def _unvalued(
        self,
        target: ast.Name,
        value: ast.expr,
        *,
        alias: bool,
    ) -> tuple[Inference | None, bool, frozenset[str]]:
        """Type a name its value gives no type: a module's type alias (`alias`: it may be one), or a hint.

        Returns:
          The inference, whether it's a guess, and what it rests on, as `valued` does.

        """
        checks: Checks = self.settings.checks
        found: tuple[Inference, bool, frozenset[str]] | None = (
            aliased.declared(
                target,
                value,
                self.settings.known,
                self.settings.facts,
                (frozenset(self.inferred.aliases), checks.min_python),
            )
            if alias and self.kind.function is None and self.kind.owner is None
            else None
        )
        hint: Inference | None
        if found is None and (hint := self.hint(target, value)) is not None:
            found = hint, True, frozenset({hinted.KIND})
        return found or (None, False, frozenset())

    def _member(self, name: str, fix: Inference | None) -> tuple[Inference | None, bool, frozenset[str]]:
        """Offer a class body's fix only for a plain class's variable typed by its value: a guess.

        Returns:
          The inference, whether it's a guess, and what it rests on, as `valued` does; none for any
          other binding of a class body.

        """
        typed: str | None = self.settings.known.class_side.variables.get(self.kind.owner or "", {}).get(name)
        if fix is None or typed is None or fix.annotation != typed:
            return None, False, frozenset()
        return fix._replace(kinds=fix.kinds | {MEMBER}), True, frozenset({MEMBER})

    def valued(
        self,
        value: ast.expr,
        line: int,
        *,
        constant: bool = False,
    ) -> tuple[Inference | None, bool, frozenset[str]]:
        """Infer the annotation of a name bound to `value` on `line`, as a type checker would see it.

        `constant`: whether the name is an ALL_CAPS module-level one passed to a call (see `doubts`).

        Returns:
          The inference (`None` where there's none to offer), whether it's a guess, and what a guess
          rests on.

        """
        facts: Facts = self.settings.facts
        function: FunctionDef | None = self.kind.function
        fix: Inference | None
        if (fix := inference(value, self.settings.known, self.inferred.types)) is not None:
            fix = corrected(value, fix, self._owner(), facts.generics, self.settings.known.names.plan)
        if fix is not None and (
            narrowed_first(value, fix)
            or narrowed_at(facts.narrowed, value, line, union=len(members(fix.annotation) or ()) > 1)
        ):
            fix = None
        if fix is None:
            return None, False, frozenset()
        unsafe: bool
        origins: frozenset[str]
        unsafe, origins = guesses_in(self, [value])
        if not unsafe:
            origins = doubts(
                value,
                fix,
                constant=constant,
                narrowed=frozenset() if function is None else tested(function, facts.tests),
            )
            unsafe = bool(origins)
        return fix, unsafe, origins

    def _constant(self, fix: Inference) -> Inference | None:
        """Declare an ALL_CAPS constant passed to a call `Final`, which keeps its literal's `Literal` type.

        `str` would widen it, where a parameter may take only some values (see `doubts`). A guess
        still (a name bound again is left alone, see `rebinds`), and only where the module can name
        `Final`.

        Returns:
          The `Final` inference, or `None`.

        """
        plan: ImportPlan | None = self.settings.known.names.plan
        spelled: str | None = None if plan is None else plan.spell(_TYPING_FINAL)
        return (
            None
            if spelled is None
            else Inference(spelled, f"{fix.reason}, a constant passed to a call", fix.kinds | {FINAL_KIND})
        )

    def _owner(self) -> Owner | None:
        """Find the class this scope is a method of, if its instance (or class) is a `Self` in it.

        That's a method whose signature says `Self`: in any other, mypy takes `self` for its class.

        Returns:
          It, or `None` outside such a method, or in one whose first parameter isn't `self` or a
          classmethod's.

        """
        function: FunctionDef | None = self.kind.function
        owner: str | None = None if function is None else self.settings.owners.get(id(function))
        if function is None or owner is None:
            return None
        args: list[ast.arg] = [*function.args.posonlyargs, *function.args.args]
        decorators: list[str] = [node_name(d) for d in function.decorator_list]
        if (
            not args
            or _STATICMETHOD in decorators
            or not (args[0].arg == _SELF or decorators == [_CLASSMETHOD])
            or not says_self(function)
        ):
            return None
        return Owner(owner, args[0].arg, self.settings.known.class_side.lineage.selfish_of(owner))

    def hint(self, target: ast.Name, value: ast.expr | None = None) -> Inference | None:
        """Type `target` by the type checkers' hints for it (`--infer-with`): the first the file can use.

        `value`: what a plain assignment binds it to. One hinted `TypeAlias` is declared an alias,
        in a module body, where it's written as a type made of others (not a bare class's alias,
        which declared one loses the class's type parameters).

        Returns:
          The inference (a guess), or `None`.

        """
        # Not used at all where not offered: what follows from it would rest on it unseen.
        if not self.settings.checks.fixes.allows(frozenset({hinted.KIND})):
            return None
        where: tuple[int, int] = (target.lineno, target.end_col_offset or 0)
        composite: bool = value is not None and self.kind.function is None and is_composite(value)
        found: Hints
        for found in self.settings.hints:
            text: str | None = found.types.get(where)
            typed: str | None
            if text == hinted.ALIAS:
                if composite and (typed := hinted.type_alias(self.settings.known, target.lineno)) is not None:
                    return hinted.inference(typed, found.checker)
                continue
            if (
                text is not None
                and (
                    typed := hinted.hinted(
                        text,
                        self.settings.known,
                        nesting=self.settings.checks.nesting,
                        # A module body's annotation is evaluated there: only what's bound before it will do.
                        before=target.lineno if self.kind.function is None else None,
                        offered=found.offered.get(where),
                    )
                )
                # A generic class a checker prints bare has arguments it doesn't know.
                and not bare(typed, self.settings.facts.generics)
                and not hinted.renames(target.id, typed, local=self.kind.function is not None)
                and not self._undeclared(typed)
            ):
                return hinted.inference(typed, found.checker)
        return None

    def _undeclared(self, annotation: str) -> bool:
        """Check whether a hint names a type variable this scope's function doesn't declare.

        See `undeclared`.

        Returns:
          Whether it does.

        """
        facts: Facts = self.settings.facts
        function: FunctionDef | None = self.kind.function
        owner: str | None = None if function is None else self.settings.owners.get(id(function))
        return undeclared(annotation, function, facts.type_vars, facts.bound.get(owner or "", frozenset()))

    def placed(self, name: str, fix: Inference, origins: frozenset[str], *, unsafe: bool) -> Fix | None:
        """Offer `name`'s fix where it can go: at its binding, or declared before a chained assignment.

        Returns:
          The fix (see `offer`).

        """
        span: tuple[int, int] | None
        if (span := self.assignments.chained.get(name)) is None:
            return self.offer(fix, origins, unsafe=unsafe)
        return self.offer(fix, origins, unsafe=unsafe, edit=Edit.DECLARE, span=span)

    def offer(
        self,
        fix: Inference,
        origins: frozenset[str],
        *,
        unsafe: bool,
        edit: Edit = Edit.ANNOTATE,
        span: tuple[int, int] = (0, 0),
    ) -> Fix | None:
        """Offer `fix` as the project's fix policy has it: selected, and a guess unless trusted.

        Returns:
          The fix, or `None` if a mechanism that decided it isn't selected, or is ignored.

        """
        policy: FixPolicy = self.settings.checks.fixes
        if not policy.allows(fix.kinds):
            return None
        certain: bool = not unsafe or policy.trusts(origins)
        plan: ImportPlan = self.settings.known.names.plan or ImportPlan({}, frozenset(), 0)
        guarded: tuple[str, ...] = _guarded_imports(fix.annotation, plan)
        guard: str | None = ""
        if guarded and plan.block == (0, 0) and (guard := plan.spell(_TYPE_CHECKING)) is None:
            return None  # nothing can be `TYPE_CHECKING` to import them under
        return Fix(
            fix.annotation,
            fix.reason,
            not certain,
            edit,
            span,
            fix.kinds,
            # With the import `TYPE_CHECKING` takes, for a new block.
            imports=imports_of(f"{fix.annotation} | {guard}" if guard else fix.annotation, plan),
            after=plan.after,
            guarded=guarded,
            guard=guard or "",
            block=plan.block,
        )

    def _first(
        self,
        name: str,
        where: tuple[int, int],
        code: str | None,
        fix: Fix | None,
    ) -> None:
        """Unless `name` is already bound, record its first binding, reporting `code` (`None`: typed).

        The offence offers `fix`, unless this is a class body (a dataclass's annotation is a field),
        where only a plain class's variable's (`_member`) is.
        """
        if name not in self.declared:
            self.declared.add(name)
            self.first.append(name)
            if code is not None:
                offered: bool = self.kind.fixable or (fix is not None and MEMBER in fix.kinds)
                self.offences.append(Offence(*where, name, code, fix if offered else None))

    def declare(self, name: str) -> None:
        """Bind `name` by an annotation (`name: T`, `name: T = ...`): a typed first binding."""
        # position is unused: `code` is `None`, so nothing is reported
        self._first(name, (0, 0), None, None)

    def opaque(self, names: Iterable[str]) -> None:
        """Record bindings whose values value flow can't see: an import, a `def`, `except ... as`."""
        name: str
        for name in names:
            self.lifetime(name).bind((0, 0), None)

    def mark_escaped(self, escaped: frozenset[str]) -> None:
        """Mark the names something out of sight writes: `escaped` ones, or any in a module or class body.

        A module or class body's names are state anything can rebind out of its sight (an instance's
        `self.x = ...`, another module's `mod.X = ...`, `monkeypatch`, `globals().update(...)`).
        """
        name: str
        body: bool = self.kind.unannotated == UNANNOTATED_MEMBER
        for name in self.flow.keys() if body else escaped & self.flow.keys():
            self.flow[name].escaped = True

    def value_flow(self, escaped: frozenset[str], skipped: frozenset[str]) -> list[Finding]:
        """Compare each name's values with its declared type.

        `escaped` names are written elsewhere; `skipped` ones aren't compared at all.

        Returns:
          The findings, for names the rules cover.

        """
        self.mark_escaped(escaped)
        return [
            found
            for name, lifetime in self.flow.items()
            if self._covered(name) and name not in skipped
            for found in findings(name, lifetime, self.settings.hierarchy)
        ]

    def assigned(self, name: str, where: tuple[int, int]) -> None:
        """Record a plain assignment to `name` at `where`, for LVA012."""
        self.assignments.found.setdefault(name, []).append((where, self.assignments.looping > 0))

    def evaluated(self, offence: Offence) -> Offence:
        """Quote a module body's fix that can't be evaluated when the module runs (unless it postpones them).

        One whose type names what the module imports for type checking alone (under an `if` on a
        flag), or binds only further down (both unbound then, as a quoted annotation's or a
        `# type:` comment's names may be), or subscripts a
        standard-library class that can't be at run time (`itertools.count[int]`).

        Returns:
          The offence, its fix quoted if it must be.

        """
        plan: ImportPlan | None = self.settings.known.names.plan
        fix: Fix | None = offence.edit
        if fix is None or plan is None or plan.postponed or self.kind.function is not None:
            return offence
        line: int = fix.span[0] if fix.edit is Edit.DECLARE else offence.line
        names: frozenset[str] = roots(fix.annotation)
        unbound: bool = bool(names & plan.guarded.keys()) or any(
            name in self.settings.facts.checking or plan.defined.get(name, 0) >= line for name in names
        )
        if not unbound and stdlib.evaluable(fix.annotation, self.settings.known):
            return offence
        return replace(offence, edit=fix._replace(annotation=_quoted(fix.annotation)))

    def _covered(self, name: str) -> bool:
        """Check whether the rules cover `name` here.

        Returns:
          Whether they do; a module or class body's dunder names are exempt.

        """
        return self.kind.unannotated != UNANNOTATED_MEMBER or not (
            name.startswith("__") and name.endswith("__")
        )

    def reported(self) -> list[Offence]:
        """Filter the offences found.

        Returns:
          All but those for exempt names.

        """
        return [self.evaluated(o) for o in self.offences if self._covered(o.name)]

    def bound(self) -> list[str]:
        """List the first bindings the rules cover.

        Returns:
          Their names, typed or not.

        """
        return [name for name in self.first if self._covered(name)]

    def annotation(self, name: str, annotation: ast.expr) -> None:
        """Report a vague annotation (LVA005), too deep a one (LVA006), or too long a tuple (LVA011)."""
        if is_vague(annotation):
            self.offences.append(Offence(*at(annotation), name, VAGUE_TYPE))
        if depth(annotation) >= self.settings.checks.nesting:
            self.offences.append(Offence(*at(annotation), name, NESTED_TYPE))
        longest: int
        if (longest := length(annotation)) > self.settings.known.max_length:
            self.offences.append(Offence(*at(annotation), name, LONG_TUPLE, detail=str(longest)))

    def unannotated(self, type_comment: str | None) -> str | None:
        """Decide the code for an `=` or `with` binding.

        Returns:
          The code, or `None` if a counted type comment types it.

        """
        return (
            None if type_comment is not None and self.settings.checks.type_comments else self.kind.unannotated
        )


def guesses_in(scope: Scope, values: Iterable[ast.expr]) -> tuple[bool, frozenset[str]]:
    """Work out whether any of `values`' types is a guess, and what the guesses rest on (see `guessing`).

    Returns:
      Whether one is, and the guessing mechanisms (`FIX_KINDS`) theirs rest on.

    """
    unsafe: bool = False
    found: set[str] = set()
    value: ast.expr
    for value in values:
        guess: bool
        origins: frozenset[str]
        guess, origins = guessing(
            value,
            scope.settings.known,
            frozenset(scope.inferred.guesses),
            scope.inferred.origins,
            scope.inferred.types,
        )
        unsafe = unsafe or guess
        found.update(origins)
    return unsafe, frozenset(found)


def certain_type(
    scope: Scope,
    value: ast.expr,
    worked_out: tuple[str | None, bool] | None = None,
) -> str | None:
    """Infer `value`'s type for value flow: only a certain `--fix` inference, never a guess.

    `None` itself (which `--fix` never offers: `x: None = None` says nothing) is `"None"` here. A
    copy of a name typed as a union is unknown: an `isinstance` or `is None` check before it may
    have narrowed the name, which value flow (blind to control flow) can't see. `worked_out`: `--fix`'s
    annotation for `value` and whether it's a guess, if they're known already.

    Returns:
      The type as text, or `None` if it's unknown or only a guess.

    """
    if isinstance(value, ast.Constant) and value.value is None:
        return "None"
    annotation: str | None
    unsafe: bool
    annotation, unsafe = worked_out or (
        inferred(value, scope.settings.known, scope.inferred.types),
        guessed(value, scope.settings.known, frozenset(scope.inferred.guesses), scope.inferred.types),
    )
    if isinstance(value, _READS) and annotation is not None and len(members(annotation) or ()) > 1:
        return None  # a read of a union is narrowed where the code checks it, which value flow can't see
    return None if unsafe else annotation


def imports_of(annotation: str, plan: ImportPlan) -> tuple[str, ...]:
    """Find the imports `annotation` needs: those `plan` added for a name it's written with.

    Returns:
      Their statements, sorted.

    """
    # `annotation` is always `ast.unparse`'s own output (or a name `plan` spelled), so it parses.
    return tuple(sorted({plan.added[root] for root in roots(annotation) if root in plan.added}))


def _guarded_imports(annotation: str, plan: ImportPlan) -> tuple[str, ...]:
    """Find the imports under `if TYPE_CHECKING:` `annotation` needs (see `Guarded`).

    Returns:
      Their statements, sorted.

    """
    statements: Iterator[str | None] = (
        plan.guarded[root].statement for root in roots(annotation) if root in plan.guarded
    )
    return tuple(sorted({statement for statement in statements if statement is not None}))


def _quoted(annotation: str) -> str:
    """Quote an annotation: in double quotes, unless it has one or a backslash (a `Literal`'s string).

    Returns:
      It, as a string literal.

    """
    plain: bool = not {'"', "\\"} & set(annotation)
    return f'"{annotation}"' if plain else ast.unparse(ast.Constant(annotation))
