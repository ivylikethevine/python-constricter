# SPDX-License-Identifier: MIT
"""One scope being checked: what it binds and reports, what `--fix` knows of it, and its late fixes."""

import ast
from collections.abc import Iterable, Iterator, Mapping, Sequence
from dataclasses import dataclass, field, replace
from typing import Final, NamedTuple, TypeAlias

from constricter.fix import fills, hinted
from constricter.fix.doubts import (
    Facts,
    Owner,
    corrected,
    doubts,
    is_constant,
    says_self,
    spelled_self,
    tested,
)
from constricter.fix.guesses import guessed, guessing
from constricter.fix.inference import inference, inferred
from constricter.fix.known import Hints, ImportPlan, Inference, Known
from constricter.offences import (
    CAN_BE_FINAL,
    LONG_TUPLE,
    NESTED_TYPE,
    UNANNOTATED,
    UNANNOTATED_MEMBER,
    UNTYPED_TARGET,
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
    is_vague,
    length,
    node_name,
    roots,
)
from constricter.rules.flow import Binding, Finding, Hierarchy, Lifetime, findings, members
from constricter.rules.rebinding import REBOUND, Refit, refit
from constricter.rules.syntax import FunctionDef, Start

_DISCARD: Final = "_"
_SELF: Final = "self"
_CLASSMETHOD: Final = "classmethod"
_STATICMETHOD: Final = "staticmethod"
_OPTIONAL: Final = "optional"  # the fix kind of a `None` default rebound to one type
_DECLARING: Final = frozenset({UNANNOTATED, UNTYPED_TARGET})  # the codes whose fix declares a name's type
_FILLED: Final = "filled"  # the fix kind (and guessing mechanism) of an empty container filled later
_NONE: Final = "None"
_FINAL: Final = "Final"
_FINAL_KIND: Final = "final"  # the fix kind of LVA012's `Final`
_TYPING_FINAL: Final = "typing.Final"
_TYPE_CHECKING: Final = "typing.TYPE_CHECKING"
_FINALS: Final = frozenset({_TYPING_FINAL, "typing_extensions.Final"})
_NO_ALIASES: Final = frozenset[str]()
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


class Kind(NamedTuple):
    """What kind of body a scope is: the code its unannotated names get, and whether `--fix` fixes it."""

    unannotated: str  # LVA001 in a function, LVA004 in a module or class body
    fixable: bool  # a class body never is: annotating a dataclass's variable makes it a field
    function: FunctionDef | None = None  # a function's own: its body, its returns

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
    """A scope's plain `name = value` (or `name: T = value`) bindings, for LVA012."""

    found: dict[str, list[Placed]] = field(default_factory=dict[str, list[Placed]])  # each name's
    looping: int = 0  # how many loops deep the statement being visited is
    empty: dict[str, str] = field(default_factory=dict[str, str])  # names first bound empty: their kind


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

    def learn(self, name: str, annotation: str, origins: frozenset[str] | None) -> None:
        """Record `name`'s type, the first time it's typed; `origins`: what it rests on, if it's a guess."""
        if name in self.types:
            return
        self.types[name] = annotation
        if origins is not None:
            self.guess(name, origins)

    def guess(self, name: str, origins: frozenset[str]) -> None:
        """Take what's inferred from `name` from here on for a guess, resting on `origins`."""
        self.guesses.add(name)
        self.origins[name] = origins

    def rebound(self, name: str, typed: str | None) -> None:
        """Record `name` bound again, to a value of type `typed` (`None`: unknown).

        A type checker narrows a name to what it's assigned: from here on it's `typed`, if known. That's
        certain for a member of a declared union (`int | None`, then `1`), which every checker narrows;
        otherwise (mypy narrows nothing else, and an unknown value may be anything) what's inferred
        from it is a guess, resting on `rebound`.
        """
        current: str | None = self.types.get(name)
        if current is None or typed == current:
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

    def bind(self, name: str, where: tuple[int, int], code: str | None, fix: Fix | None = None) -> None:
        """Bind `name` to a value value flow can't see; unless it's already bound, report `code`.

        `code` is reported at `(line, col)` (`None` means typed), offering `fix` if there's one.
        """
        self.lifetime(name).bind(where, None)
        if name in self.declared:
            self.inferred.rebound(name, None)
        self._first(name, where, code, fix)

    def assign(self, target: ast.Name, code: str | None, value: ast.expr) -> None:
        """Bind `target` to `value` (`name = value`), offering `--fix`'s annotation for it."""
        name: str = target.id
        again: bool = name in self.declared
        facts: Facts = self.settings.facts
        function: FunctionDef | None = self.kind.function
        fix: Inference | None
        if (fix := inference(value, self.settings.known, self.inferred.types)) is not None:
            fix = corrected(value, fix, self._owner(), facts.generics, self.settings.known.names.plan)
        unsafe: bool
        origins: frozenset[str]
        unsafe, origins = guesses_in(self, [value])
        if fix is not None and not unsafe:
            origins = doubts(
                value,
                fix,
                constant=function is None and is_constant(name) and name in facts.passed,
                narrowed=function is not None and ast.unparse(value) in tested(function, facts.tests),
            )
            unsafe = bool(origins)
        # Value flow's type is `--fix`'s own, if certain: worked out once, here, for both.
        certain: str | None = certain_type(self, value, (None if fix is None else fix.annotation, unsafe))
        if fix is None and (fix := self.hint(target)) is not None:
            unsafe, origins = True, frozenset({hinted.KIND})
        self.lifetime(name).bind(
            at(target),
            certain,
            (fix.annotation, origins) if fix is not None and unsafe else None,
        )
        self.assigned(name, at(target))
        if again:
            self.inferred.rebound(name, certain)
        kind: str | None
        if (kind := fills.empty(value)) is not None:
            _ = self.assignments.empty.setdefault(name, kind)
        self._first(name, at(target), code, None if fix is None else self.offer(fix, origins, unsafe=unsafe))
        if fix is not None:
            self.inferred.learn(name, fix.annotation, origins if unsafe else None)

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
        return Owner(owner, args[0].arg, self.settings.facts.selfish.get(owner, frozenset()))

    def hint(self, target: ast.Name) -> Inference | None:
        """Type `target` by the type checkers' hints for it (`--infer-with`): the first the file can use.

        Returns:
          The inference (a guess), or `None`.

        """
        # Not used at all where not offered: what follows from it would rest on it unseen.
        if not self.settings.checks.fixes.allows(frozenset({hinted.KIND})):
            return None
        where: tuple[int, int] = (target.lineno, target.end_col_offset or 0)
        found: Hints
        for found in self.settings.hints:
            text: str | None = found.types.get(where)
            typed: Inference | None
            if text is not None and (
                typed := hinted.hinted(
                    text,
                    found.checker,
                    self.settings.known,
                    nesting=self.settings.checks.nesting,
                    # A module body's annotation is evaluated there: only what's bound before it will do.
                    before=target.lineno if self.kind.function is None else None,
                )
            ):
                return typed
        return None

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
            imports=_imports(f"{fix.annotation} | {guard}" if guard else fix.annotation, plan),
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

        The offence offers `fix`, unless this is a class body (a dataclass's annotation is a field).
        """
        if name not in self.declared:
            self.declared.add(name)
            self.first.append(name)
            if code is not None:
                self.offences.append(Offence(*where, name, code, fix if self.kind.fixable else None))

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

    def optionals(self) -> None:
        """Offer `T | None` to a name first bound to `None`, then only ever to a known `T`.

        Every later binding must have a type value flow is sure of (or `--fix` guessed, which makes
        this a guess too), all the same one, not itself allowing `None`, and nothing in another scope
        may write the name (`nonlocal`, `global`).
        """
        index: int
        o: Offence
        for index, o in enumerate(self.offences):
            lifetime: Lifetime | None = self.flow.get(o.name)
            if o.code != UNANNOTATED or _fixed(o) or lifetime is None or lifetime.escaped:
                continue
            first: Binding
            rest: list[Binding]
            first, *rest = lifetime.bindings
            guesses: list[Late] = [
                binding.guess for binding in rest if binding.value is None and binding.guess is not None
            ]
            types: set[str | None] = {binding.value or (binding.guess or (None,))[0] for binding in rest}
            if first.at != (o.line, o.col) or first.value != _NONE or len(types) != 1:
                continue
            found: str | None = types.pop()
            if found is None or _NONE in (members(found) or [found]):
                continue
            origins: frozenset[str] = frozenset[str]().union(*(rests for _, rests in guesses))
            reason: str = f"`None`, then only `{found}`"
            fix: Fix | None = self.offer(
                Inference(f"{found} | None", reason, frozenset({_OPTIONAL}) | origins),
                origins,
                unsafe=bool(guesses),
            )
            self.offences[index] = replace(o, edit=fix)
            self.inferred.late[o.name] = (f"{found} | None", origins)

    def rebinds(self) -> None:
        """Refit each first binding's fix to every value the name is bound to later (see `rebinding`).

        A name something out of sight writes is left alone.
        """
        index: int
        o: Offence
        plan: ImportPlan | None = self.settings.known.names.plan
        self_type: str | None = None if plan is None else spelled_self(plan)
        for index, o in enumerate(self.offences):
            lifetime: Lifetime | None = self.flow.get(o.name)
            fix: Fix | None = o.edit
            if o.code not in _DECLARING or fix is None or lifetime is None or lifetime.escaped:
                continue
            first: Binding
            rest: list[Binding]
            first, *rest = lifetime.bindings
            if first.at != (o.line, o.col) or not rest:
                continue
            found: Refit | Fix | None = refit(o, fix, rest, self.settings.hierarchy, self_type)
            refitted: Fix | None = self._offered(found) if isinstance(found, Refit) else found
            self.offences[index] = replace(o, edit=refitted)

    def _offered(self, found: Refit) -> Fix | None:
        """Offer a refit fix, as the project's fix policy has it (see `offer`).

        Returns:
          The fix, or `None` if it isn't offered.

        """
        return self.offer(found.found, found.origins, unsafe=found.unsafe, edit=found.edit, span=found.span)

    def fills(self) -> None:
        """Offer an empty container, bound nowhere else, the type of what its function adds to it.

        A guess (see `constricter.fix.fills`), resting on `filled` for `unsafe-fix-select`.
        """
        index: int
        o: Offence
        for index, o in enumerate(self.offences):
            lifetime: Lifetime | None = self.flow.get(o.name)
            kind: str | None = self.assignments.empty.get(o.name)
            if o.code != UNANNOTATED or _fixed(o) or kind is None:
                continue
            if lifetime is None or lifetime.escaped or len(lifetime.bindings) != 1:
                continue
            found: Inference | None
            if (
                found := fills.filled(
                    self.kind.body(),
                    o.name,
                    kind,
                    self.settings.known,
                    self.inferred.types,
                )
            ) is None:
                continue
            fix: Fix | None = self.offer(found, frozenset({_FILLED}), unsafe=True)
            self.offences[index] = replace(o, edit=fix)
            # What the scope infers from it (its `return`s) knows its type, a guess.
            self.inferred.late[o.name] = (found.annotation, frozenset({_FILLED}))

    def finals(self) -> list[Offence]:
        """Find the names that could be `Final` (LVA012); run after `value_flow`, which marks escapes.

        Returns:
          An offence for each name bound exactly once, by a plain assignment outside any loop, and not
          declared apart from it or already `Final`, nor written from another scope; with a fix
          (see `_final`) where one is offered.

        """
        found: list[Offence] = []
        plan: ImportPlan | None = self.settings.known.names.plan
        # What else the module calls `Final`: `from typing import Final as F`.
        aliases: frozenset[str] = frozenset(
            () if plan is None else (name for name, origin in plan.bound.items() if origin in _FINALS),
        )
        name: str
        lifetime: Lifetime
        for name, lifetime in self.flow.items():
            if (
                name == _DISCARD
                or lifetime.escaped
                or self.kind.unannotated == UNANNOTATED_MEMBER
                or len(lifetime.bindings) != 1
            ):
                continue
            where: tuple[int, int] = lifetime.bindings[0].at
            if self.assignments.found.get(name) == [(where, False)] and (
                lifetime.declared is None
                or (lifetime.declared_at == where and not is_final(lifetime.declared, aliases))
            ):
                found.append(Offence(*where, name, CAN_BE_FINAL, self._final(name, lifetime)))
        return [self._evaluated(o) for o in found]

    def _evaluated(self, offence: Offence) -> Offence:
        """Quote a module body's fix whose type names what the module imports for type checking alone.

        A module's annotations are evaluated when it runs (unless it postpones them), and those
        names aren't bound then.

        Returns:
          The offence, its fix quoted if it must be.

        """
        plan: ImportPlan | None = self.settings.known.names.plan
        fix: Fix | None = offence.edit
        if (
            fix is None
            or plan is None
            or plan.postponed
            or self.kind.function is not None
            or not roots(fix.annotation) & plan.guarded.keys()
        ):
            return offence
        return replace(offence, edit=fix._replace(annotation=_quoted(fix.annotation)))

    def _final(self, name: str, lifetime: Lifetime) -> Fix | None:
        """Offer LVA012's `Final`: around the annotation there (`Final[int]`), or as one (`: Final`).

        An unannotated name LVA001 would annotate gets `Final[T]` with LVA001's type instead, and
        LVA001's own fix is dropped: both write where the name is bound, and this one does for both.

        Returns:
          The fix, or `None` where the scope isn't fixed, the `final` kind isn't selected, an
          annotation spans lines, or the module can't name `Final`.

        """
        plan: ImportPlan | None = self.settings.known.names.plan
        spelled: str | None = None if plan is None else plan.spell(_TYPING_FINAL)
        kinds: frozenset[str] = frozenset({_FINAL_KIND})
        if (
            plan is None
            or spelled is None
            or not self.kind.fixable
            or not self.settings.checks.fixes.allows(kinds)
        ):
            return None
        reason: str = "bound once, and never rebound"
        if lifetime.declared is not None:
            if lifetime.declared_span is None:
                return None
            line: int = lifetime.declared_at[0]
            start: int
            end: int
            start, end = lifetime.declared_span
            text: str = self.settings.lines[line - 1].encode()[start:end].decode()
            return _final_fix(
                Fix(f"{spelled}[{text}]", reason, edit=Edit.REPLACE, span=(start, end), kinds=kinds),
                plan,
            )
        index: int
        o: Offence
        for index, o in enumerate(self.offences):
            if (
                o.name == name
                and o.code == UNANNOTATED
                and o.edit is not None
                and o.edit.edit == Edit.ANNOTATE
            ):
                self.offences[index] = replace(o, edit=None)
                return _final_fix(
                    o.edit._replace(annotation=f"{spelled}[{o.edit.annotation}]", kinds=o.edit.kinds | kinds),
                    plan,
                )
        return _final_fix(Fix(spelled, reason, kinds=kinds), plan)

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
        return [self._evaluated(o) for o in self.offences if self._covered(o.name)]

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

    def walrus(self, node: ast.AST) -> None:
        """Bind `:=` targets in an expression, comprehensions included, lambdas excluded.

        Asked only in a module with one (`Settings.walruses`).
        """
        in_lambda: set[int] = {
            id(inner)
            for outer in ast.walk(node)
            if isinstance(outer, ast.Lambda)
            for inner in ast.walk(outer)
        }
        current: ast.AST
        for current in ast.walk(node):
            if isinstance(current, ast.NamedExpr) and id(current) not in in_lambda:
                self.bind(current.target.id, at(current.target), self.kind.unannotated)

    def unannotated(self, type_comment: str | None) -> str | None:
        """Decide the code for an `=` or `with` binding.

        Returns:
          The code, or `None` if a counted type comment types it.

        """
        return (
            None if type_comment is not None and self.settings.checks.type_comments else self.kind.unannotated
        )


def is_final(annotation: str, aliases: frozenset[str] = _NO_ALIASES) -> bool:
    """Check whether an annotation is `Final` (`Final[T]`, `typing.Final`, ...), or one of `aliases` for it.

    Returns:
      Whether it is.

    """
    # `annotation` is always `ast.unparse`'s own output, so it's always valid Python to parse back.
    root: ast.expr = ast.parse(annotation, mode="eval").body
    return node_name(root.value if isinstance(root, ast.Subscript) else root) in aliases | {_FINAL}


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


def _imports(annotation: str, plan: ImportPlan) -> tuple[str, ...]:
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


def _final_fix(fix: Fix, plan: ImportPlan) -> Fix:
    """Give a `Final` fix the imports its annotation needs.

    Returns:
      It, with them.

    """
    return fix._replace(imports=_imports(fix.annotation, plan), after=plan.after)


def _fixed(offence: Offence) -> bool:
    """Check whether an offence already has a fix a late one (`optionals`, `fills`) mustn't replace.

    Returns:
      Whether it has one, other than a type checker's hint (`--infer-with`), which one would.

    """
    return offence.edit is not None and hinted.KIND not in offence.edit.kinds
