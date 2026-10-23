"""One scope being checked: what it binds and reports, what `--fix` knows of it, and its late fixes."""

import ast
import re
from collections.abc import Iterable, Mapping
from dataclasses import replace
from typing import Final

from constricter.fix.core.imports import guarded_imports, imports_of, through, unwritable
from constricter.fix.core.known import Hints, ImportPlan, Inference, Typed
from constricter.fix.libraries import stdlib
from constricter.fix.libraries.library import chains
from constricter.fix.values import aliased, callables, fills, hinted
from constricter.fix.values.doubts import (
    Facts,
    Owner,
    as_declared,
    bare,
    corrected,
    doubts,
    is_constant,
    narrowed_first,
    narrowing,
    none_tested,
    says_self,
    tested,
    undeclared,
)
from constricter.fix.values.guesses import guessed, guessing
from constricter.fix.values.inference import inference, inferred
from constricter.fix.values.members import fits, parsed
from constricter.fix.values.narrowed import narrowed_at, narrowed_to, read_narrowed
from constricter.fix.values.refused import refused
from constricter.offences import (
    LONG_TUPLE,
    MEMBER,
    NESTED_TYPE,
    UNANNOTATED,
    UNANNOTATED_MEMBER,
    UNTYPED_PARAMETERS,
    VAGUE_TYPE,
    WIDEN_KINDS,
    Checks,
    Edit,
    Fix,
    FixPolicy,
    Offence,
    at,
)
from constricter.rules import widened
from constricter.rules.annotations import (
    depth,
    is_composite,
    length,
    node_name,
    roots,
    vague_fits,
)
from constricter.rules.flow import Finding, Lifetime, findings, members
from constricter.rules.quoted import newer, quote
from constricter.rules.scoped import Assignments, Inferred, Kind, Late, Settings
from constricter.rules.syntax import FunctionDef

_SELF: Final = "self"
_NONE: Final = "None"
_CLASSMETHOD: Final = "classmethod"
_STATICMETHOD: Final = "staticmethod"
_SELF_WORD: Final = re.compile(r"\bSelf\b")  # `Self` in an annotation, `typing.Self` too
FINAL_KIND: Final = "final"  # the fix kind of LVA012's `Final`
_TYPING_FINAL: Final = "typing.Final"
_LITERAL_DOUBT: Final = frozenset({"literal"})  # a constant's literal, which `doubts` makes a guess
_READS: Final = (ast.Name, ast.Attribute, ast.Subscript)  # a read of a value a type checker may narrow
TESTED: Final = "tested"  # the fix kind of a read a test around it narrows


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
        # What `--fix` knows of the names bound so far.
        self.inferred: Inferred = Inferred(unions=settings.known.indirect.unions)
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
        typed: str | Late | None = None,
    ) -> None:
        """Bind `name` to a value value flow can't see; unless it's already bound, report `code`.

        `code` is reported at `(line, col)` (`None` means typed), offering `fix` if there's one.
        `typed`: the value's type, if `--fix` knows it (a loop's element), which a fix for the name's
        first binding is held to (see `rebinding`): its text where it's certain, which a name
        declared already is then bound to; else the guess and what it rests on, as `assign` binds one.
        """
        certain: str | None = typed if isinstance(typed, str) else None
        guess: Late | None = (typed, frozenset()) if isinstance(typed, str) else typed
        self.lifetime(name).bind(where, None, guess)
        if name in self.declared:
            self.inferred.rebound(name, certain)
        self._first(name, where, code, fix)

    def assign(
        self,
        target: ast.Name,
        code: str | None,
        value: ast.expr,
        chained: ast.stmt | None = None,
        *,
        commented: Fix | bool = False,
    ) -> None:
        """Bind `target` to `value` (`name = value`), offering `--fix`'s annotation for it.

        One of a `chained` assignment's names (`a = b = 0`), which can't be annotated where it's bound,
        is offered a declaration before it instead (`a: int`); not a `Final` one, which needs its value.
        A `commented` one (`x = v  # type: T`) is offered its comment's fix instead, and read as that
        type; with none (`True`), no fix: an annotation beside the comment won't parse with it.
        """
        name: str = target.id
        if aliased.factory(value, self.settings.known):  # a type: nothing to annotate it with
            self.declared.add(name)
            self.opaque([name])
            return
        again: bool = name in self.declared
        fix: Inference | None
        unsafe: bool
        origins: frozenset[str]
        constant: bool = (
            self.kind.function is None
            and self.kind.owner is None
            and is_constant(name)
            and name in self.settings.facts.passed
            and chained is None
        )
        fix, unsafe, origins = self.valued(value, target.lineno, constant=constant)
        if fix is not None and constant and origins == _LITERAL_DOUBT:
            fix = self._constant(name, fix)
        # Value flow's type is `--fix`'s own, if certain: worked out once, here, for both.
        certain: str | None = certain_type(self, value, (None if fix is None else fix.annotation, unsafe))
        if self.kind.owner is not None:
            fix, unsafe, origins = self._member(name, fix, value)
        if fix is None or not self.writable(fix):
            fix, unsafe, origins = self._unvalued(
                target,
                value,
                (fix, unsafe, origins),
                alias=chained is None and not again,
            )
        # Past `vague`, a type holds no other binding's fix to it: unknown there, and to value flow.
        vague: bool = fix is not None and not self.writable(fix)
        guess: Late | None = (fix.annotation, origins) if fix is not None and unsafe else None
        self.lifetime(name).bind(at(target), certain, None if vague else guess)
        self.assigned(name, at(target))
        if again:
            self.inferred.rebound(name, fix.annotation if fix and vague and not unsafe else certain, guess)
        self._emptied(name, value)
        if chained is not None and not again:
            _ = self.assignments.chained.setdefault(name, (chained.lineno, chained.col_offset))
        # A wider type only for a name first bound here, by a statement of its own.
        self._first(
            name,
            at(target),
            code,
            self._offered(
                target,
                (fix, unsafe, origins),
                None if chained or again else value,
                commented=commented,
            ),
        )
        if not again and code is not None and self.offences[-1:]:
            self.offences[-1] = self._unfixed(self.offences[-1], name, value)
        if fix is not None and aliased.declares(parsed(fix.annotation)):
            self.inferred.aliases.add(name)  # `TypeAlias` isn't its value's type
        elif fix is not None:
            self.inferred.learn(name, fix.annotation, origins if unsafe else None, again=again)
        # A call of no type to write still types what's read of the name (`both.out`), bound once.
        self.inferred.types.hold(
            name,
            value if fix is None and not again and chains(value, self.settings.known) else None,
        )

    def _emptied(self, name: str, value: ast.expr) -> None:
        """Note `name` bound first to an empty container (see `fills.empty`), and its kind."""
        kind: str | None
        if (kind := fills.empty(value) or fills.keyed_empty(value, self.settings.known)) is not None:
            _ = self.assignments.empty.setdefault(name, kind)

    def _unvalued(
        self,
        target: ast.Name,
        value: ast.expr,
        vague: tuple[Inference | None, bool, frozenset[str]],
        *,
        alias: bool,
    ) -> tuple[Inference | None, bool, frozenset[str]]:
        """Type a name its value gives no type: a module's type alias (`alias`: it may be one), or a hint.

        `vague`: what `valued` made of it, a type too vague to write: the name's still, with neither.

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
        function: FunctionDef | None = self.kind.function
        owner: str | None = self.kind.owner
        types: Typed = self.inferred.types
        facts: Facts = self.settings.facts
        # In a function; or a module's or a plain class's body, for a name first bound there.
        body: bool = alias and (owner is None or owner in self.settings.known.class_side.plain)
        called: tuple[Inference, ast.expr] | None = (
            None
            if found is not None or vague[0] is not None or not (function is not None or body)
            else callables.aliased(
                target,
                value,
                callables.Site(function, owner, facts.attributed, facts.positional),
                self.settings.known,
                (types, lambda arg: inference(arg, self.settings.known, types)),
            )
        )
        if called is not None and owner is not None:  # a class's variable: a guess (see `_member`)
            found = called[0]._replace(kinds=called[0].kinds | {MEMBER}), True, frozenset({MEMBER})
        elif called is not None:
            found = called[0], *guesses_in(self, [called[1]])
        hint: Inference | None
        if found is None and (hint := self.hint(target, value)) is not None:
            found = hint, True, hint.kinds
        return found or vague

    def _member(
        self,
        name: str,
        fix: Inference | None,
        value: ast.expr,
    ) -> tuple[Inference | None, bool, frozenset[str]]:
        """Offer a class body's fix only for a plain class's variable typed by its `value`: a guess.

        Returns:
          The inference, whether it's a guess, and what it rests on, as `valued` does; none for any
          other binding of a class body.

        """
        typed: str | None = self.settings.known.class_side.variables.get(self.kind.owner or "", {}).get(name)
        # The variable's type is its value's, or what a base holds it to (`maxDiff`, an `int | None`).
        held: frozenset[str] = frozenset() if typed is None else self.inferred.members(typed)
        if fix is None and _NONE in held and isinstance(value, ast.Constant) and value.value is None:
            fix = Inference(_NONE, "what a class above it declares it", frozenset())
        # A checked file's class, by name: the index typed it so (`plain.settled`).
        if fix is None and typed is not None and isinstance(value, ast.Name) and typed == f"type[{value.id}]":
            fix = Inference(typed, f"the class `{value.id}` it names", frozenset())
        if fix is None or typed is None or fix.annotation not in held:
            return None, False, frozenset()
        return fix._replace(annotation=typed, kinds=fix.kinds | {MEMBER}), True, frozenset({MEMBER})

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
        # An alias of a union is narrowed as the union it names.
        named: Inference | None = (
            None
            if fix is None
            else fix._replace(annotation=self.inferred.unions.get(fix.annotation, fix.annotation))
        )
        left: Inference | None
        if (left := None if named is None else self._tested(value, named, line)) is not None:
            fix = left
        elif named is not None and (
            (
                narrowed_first(value, named)
                and not (named.annotation != _NONE and as_declared(value, function, facts.tests))
            )
            or narrowed_at(facts.narrowed, value, line, union=len(members(named.annotation) or ()) > 1)
            or self._takes_narrowed(value, named, line)
        ):
            fix = None
        if fix is None or named is None:
            return None, False, frozenset()
        unsafe: bool
        origins: frozenset[str]
        unsafe, origins = guesses_in(self, [value])
        if not unsafe:
            # A read the tests around it narrow is what they leave, whatever else tests it.
            own: frozenset[str] = frozenset({ast.unparse(value)} if left is not None else ())
            origins = doubts(
                value,
                fix,
                constant=constant,
                narrowed=frozenset() if function is None else tested(function, facts.tests) - own,
            )
            unsafe = bool(origins)
        return fix, unsafe, origins

    def tested_read(self, value: ast.expr, found: Inference) -> Inference | None:
        """Type a read the tests around it narrow, as a binding of it would be (see `_tested`).

        Returns:
          The inference, or `None` where no test narrows it, or one narrows it otherwise.

        """
        named: Inference = found._replace(
            annotation=self.inferred.unions.get(found.annotation, found.annotation),
        )
        return self._tested(value, named, value.lineno)

    def _tested(self, value: ast.expr, named: Inference, line: int) -> Inference | None:
        """Type a read the tests around it narrow by what they leave of its union.

        `conn = self.conn` after `if self.conn is None: return` is a `Conn`, of a `Conn | None`;
        in `if isinstance(x, int):`, `y = x` is an `int`, of an `int | str`. Only a name's or an
        attribute's read in a function (see `narrowed.narrowed_to`).

        Returns:
          The inference, or `None` where no test narrows it, or one narrows it otherwise.

        """
        function: FunctionDef | None = self.kind.function
        if function is None or not isinstance(value, ast.Name | ast.Attribute):
            return None
        text: str = ast.unparse(value)
        union: frozenset[str] = members(named.annotation) or frozenset()
        if not union or not read_narrowed(self.settings.facts.narrowed, text, line, union=len(union) > 1):
            return None
        written: str = named.annotation
        ordered: list[str] = sorted(union, key=lambda m: (written.find(m) < 0, written.find(m), m))
        left: list[str] | None = narrowed_to(self.settings.facts.narrowed, text, line, ordered, function)
        if left is None or len(left) == len(ordered):
            return None
        return Inference(
            " | ".join(left),
            f"{named.reason}, narrowed by the test around it",
            named.kinds | {TESTED},
            named.reads,
        )

    def _takes_narrowed(self, value: ast.expr, fix: Inference, line: int) -> bool:
        """Check whether a fix takes its type from a read narrowed at `line`: `deepcopy(x)`, in `if x:`.

        Or holds one in a display (`[x]`, `[self.x]`, there): its elements are the narrowed type's.

        Returns:
          Whether it does: the read has another type there than it's declared.

        """
        types: Mapping[str, str] = self.inferred.types
        held: list[str] = [
            ast.unparse(element)
            for element in (value.elts if isinstance(value, ast.List | ast.Set | ast.Tuple) else ())
            if isinstance(element, _READS)
        ]
        return any(
            read_narrowed(
                self.settings.facts.narrowed,
                read,
                line,
                union=len(self.inferred.members(types.get(read, ""))) > 1,
            )
            for read in (*fix.reads, *held)
        )

    def _constant(self, name: str, fix: Inference) -> Inference | None:
        """Declare an ALL_CAPS constant passed to a call `Final`, which keeps its literal's `Literal` type.

        `str` would widen it, where a parameter may take only some values (see `doubts`). A guess
        still (a name bound again is left alone, see `rebinds`), and only where the module can name
        `Final`. What's read of `name` has its literal's type, `fix`'s.

        Returns:
          The `Final` inference, or `None`.

        """
        plan: ImportPlan | None = self.settings.known.names.plan
        spelled: str | None = None if plan is None else plan.spell(_TYPING_FINAL)
        self.inferred.learn(name, fix.annotation, _LITERAL_DOUBT)
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
        where: tuple[int, int] = (target.lineno, target.end_col_offset or 0)
        composite: bool = value is not None and self.kind.function is None and is_composite(value)
        found: Hints
        for found in self.settings.hints:
            # Not used at all where not offered: what follows from it would rest on it unseen.
            text: str | None = (
                found.types.get(where) if self.settings.checks.fixes.allows(frozenset({found.kind})) else None
            )
            typed: str | None
            if text == hinted.ALIAS:
                if composite and (typed := hinted.type_alias(self.settings.known, target.lineno)) is not None:
                    return hinted.inference(typed, found)
                continue
            if (
                text is None
                or (
                    typed := hinted.hinted(
                        text,
                        self.settings.known,
                        hinted.Site(
                            self.settings.checks.nesting,
                            # A module body's annotation is evaluated there: only what's bound before it.
                            target.lineno if self.kind.function is None else None,
                            isinstance(value, ast.BinOp),
                        ),
                        found.offered.get(where),
                    )
                )
                is None
            ):
                continue
            typed = self._optional(target.id, typed)
            if (
                # A generic class a checker prints bare has arguments it doesn't know.
                not bare(typed, self.settings.facts.generics)
                and not hinted.renames(target.id, typed, local=self.kind.function is not None)
                and not (self._undeclared(typed) or self._misread(target.id, typed))
            ):
                return hinted.inference(typed, found)
        return None

    def _optional(self, name: str, annotation: str) -> str:
        """Add `None` to a hint for a name this scope's function compares with `None`, if it lacks one.

        The hint is the first value's type as the checker reads it; a test for `None` says the author
        expects one (`rec = fairy.record`, hinted `Record`, then `if rec is not None`), and the
        package's own checker may read the value as `Record | None`.

        Returns:
          The annotation, `None` added where the test says so.

        """
        function: FunctionDef | None
        if (function := self.kind.function) is None or name not in none_tested(function):
            return annotation
        return annotation if _NONE in (members(annotation) or ()) else f"{annotation} | {_NONE}"

    def _misread(self, name: str, annotation: str) -> bool:
        """Check whether a hint is one this scope's function reads otherwise than declared.

        A union for a name it never tests: used as it is, it's taken for one of its members
        (`opt.cb`, hinted `Option | None`), which the union declared would make an error; tested
        (`if opt is None`), a checker narrows it. And any hint for a name it returns where its
        signature says `Self`: the checker hints the class, which isn't `Self`. And a hint naming
        `Self` where its signature doesn't: pyrefly takes `self` for `Self` everywhere
        (`type(self)(...)`, `self[mask]`), mypy only there, and for its class elsewhere.

        Returns:
          Whether it is.

        """
        function: FunctionDef | None
        if (function := self.kind.function) is None:
            return False
        if _SELF_WORD.search(annotation) is not None and not says_self(function):
            return True
        if len(self.inferred.members(annotation)) > 1:  # an alias of a union is one
            return name not in narrowing(function)
        return says_self(function) and any(
            isinstance(node.value, ast.Name) and node.value.id == name
            for node in ast.walk(function)
            if isinstance(node, ast.Return)
        )

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
          The fix, or `None` if a mechanism that decided it isn't selected, or is ignored, or it's
          vaguer than `vague` allows (it would be LVA005).

        """
        policy: FixPolicy = self.settings.checks.fixes
        widening: bool = bool(fix.kinds & WIDEN_KINDS)  # written whatever `vague` allows, and marked
        if not policy.allows(fix.kinds) or not (widening or self.writable(fix)):
            return None
        certain: bool = not unsafe or policy.trusts(origins)
        plan: ImportPlan = self.settings.known.names.plan or ImportPlan({}, frozenset(), 0)
        if self.kind.owner is None:  # a class's own body names its classes bare
            fix = fix._replace(annotation=through(fix.annotation, plan, self.settings.facts.nested))
        if unwritable(fix.annotation, plan, self.settings.facts.nested):
            return None
        guarded: tuple[str, ...] = guarded_imports(fix.annotation, plan)
        guard: str | None = ""
        if guarded and plan.checking.block == (0, 0) and (guard := plan.type_checking()) is None:
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
            block=plan.checking.block,
        )

    def _offered(
        self,
        target: ast.Name,
        typed: tuple[Inference | None, bool, frozenset[str]],
        widen: ast.expr | None,
        *,
        commented: Fix | bool = False,
    ) -> Fix | None:
        """Offer `target`'s fix as `typed` has it (see `valued`), else a wider one for its value `widen`.

        A wider type (see `widened.wider`) only where `fix-widen` asks for it. A `commented` name's
        fix is its comment's (see `assign`), and what's read of it has that type.

        Returns:
          The fix, or `None`.

        """
        found: Inference | None
        fix: Fix | None
        if isinstance(commented, Fix):
            self.inferred.learn(target.id, commented.annotation, None, again=target.id in self.declared)
            return commented
        if commented:
            return None
        if typed[0] is not None and (fix := self.placed(target.id, typed[0], typed[2], unsafe=typed[1])):
            return fix
        if widen is None:
            return None
        self.assignments.plain[target.id] = (target, widen, typed[0])
        if UNTYPED_PARAMETERS not in self.settings.checks.fixes.widen:
            return None
        found = widened.wider(
            self.kind.function,
            (target, widen),
            self.inferred.types,
            self.settings.known.names.plan,
        )
        return None if found is None else self.offer(found, frozenset(), unsafe=False)

    def writable(self, fix: Inference) -> bool:
        """Check that a type is no vaguer than `vague` allows: one that isn't is known, and never written.

        Returns:
          Whether it is.

        """
        return fits(fix.annotation, self.settings.checks.vague)

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

    def _unfixed(self, offence: Offence, name: str, value: ast.expr) -> Offence:
        """Say why the offence just reported for `name`, bound to a call, has no fix (`refused`).

        Returns:
          The offence, with the reason; any other as it is.

        """
        if offence.name != name or offence.edit is not None:
            return offence
        why: str = refused(value, self.settings.known, self.inferred.types, self.settings.facts.untyped)
        return replace(offence, unfixed=why) if why else offence

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
        for name in self.flow.keys() if body else self.flow.keys() & escaped:
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
        standard-library class that can't be at run time (`itertools.count[int]`). And any scope's
        written as the project's oldest Python (`min-python`) doesn't read a type: `int | None`
        before 3.10, `list[int]` before 3.9.

        Returns:
          The offence, its fix quoted if it must be.

        """
        plan: ImportPlan | None = self.settings.known.names.plan
        fix: Fix | None = offence.edit
        if fix is None or plan is None or plan.postponed:
            return offence
        if newer(fix.annotation, self.settings.checks.min_python):
            return replace(offence, edit=fix._replace(annotation=quote(fix.annotation)))
        if self.kind.function is not None:
            return offence
        line: int = fix.span[0] if fix.edit is Edit.DECLARE else offence.line
        names: frozenset[str] = roots(fix.annotation)
        unbound: bool = bool(plan.guarded.keys() & names) or any(
            name in self.settings.facts.checking or plan.defined.get(name, 0) >= line for name in names
        )
        if not unbound and stdlib.evaluable(fix.annotation, self.settings.known):
            return offence
        return replace(offence, edit=fix._replace(annotation=quote(fix.annotation)))

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

    def annotation(self, name: str, annotation: ast.expr, *, marked: bool = False) -> None:
        """Report a vague annotation (LVA005), too deep a one (LVA006), or too long a tuple (LVA011).

        Vague as far as `vague` allows (see `vague_fits`) isn't LVA005, nor is a widening's own
        (`marked`: see `widened`).
        """
        if not marked and not vague_fits(
            annotation,
            self.settings.checks.vague,
        ):
            self.offences.append(Offence(*at(annotation), name, VAGUE_TYPE))
        if depth(annotation) >= self.settings.checks.nesting:
            self.offences.append(Offence(*at(annotation), name, NESTED_TYPE))
        longest: int
        if (longest := length(annotation)) > self.settings.known.limits.max_length:
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
    have narrowed the name, which value flow (blind to control flow) can't see. A type vaguer than
    `vague` allows is unknown too: its `Any` fits whatever the name is declared. `worked_out`:
    `--fix`'s annotation for `value` and whether it's a guess, if they're known already.

    Returns:
      The type as text, or `None` if it's unknown or only a guess.

    """
    if isinstance(value, ast.Constant) and value.value is None:
        return _NONE
    annotation: str | None
    unsafe: bool
    annotation, unsafe = worked_out or (
        inferred(value, scope.settings.known, scope.inferred.types),
        guessed(value, scope.settings.known, frozenset(scope.inferred.guesses), scope.inferred.types),
    )
    if isinstance(value, _READS) and annotation is not None and len(members(annotation) or ()) > 1:
        return None  # a read of a union is narrowed where the code checks it, which value flow can't see
    if unsafe or annotation is None or not vague_fits(parsed(annotation), scope.settings.checks.vague):
        return None
    return annotation


def guessed_type(scope: Scope, value: ast.expr) -> Late | None:
    """Infer `value`'s type where `--fix` only guesses it: what `certain_type` leaves unknown.

    Returns:
      The type and what the guess rests on; `None` if it's unknown, certain, or vaguer than `vague`
      allows.

    """
    annotation: str | None = inferred(value, scope.settings.known, scope.inferred.types)
    unsafe: bool
    origins: frozenset[str]
    unsafe, origins = guesses_in(scope, [value])
    if not unsafe or annotation is None or not vague_fits(parsed(annotation), scope.settings.checks.vague):
        return None
    return annotation, origins
