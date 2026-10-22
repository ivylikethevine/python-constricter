"""The rules: every local variable is typed where it's first bound (see README)."""

import ast
from collections.abc import Iterator, Mapping, Sequence
from dataclasses import replace
from typing import Final, NamedTuple, cast

from constricter.fix.core import imports
from constricter.fix.core.known import (
    Guarded,
    ImportPlan,
    Observed,
    Outside,
    Passed,
    Returned,
    Returns,
)
from constricter.fix.values import returned, stored
from constricter.jsonc import as_text
from constricter.offences import (
    DEFAULT_CHECKS,
    UNANNOTATED,
    UNANNOTATED_MEMBER,
    UNTYPED_TARGET,
    Checks,
    Offence,
)
from constricter.rules import attributes, late, parsed, recorded
from constricter.rules.calls import keyed, observed
from constricter.rules.flow import Finding
from constricter.rules.narrowing import flow_offences, module_flow
from constricter.rules.redundant import redundant
from constricter.rules.scope import Scope
from constricter.rules.scoped import Seeded, Settings
from constricter.rules.scoping import body_scopes, bound_once, finish, function_scope, module_scopes
from constricter.rules.settings import module_settings
from constricter.rules.syntax import (
    FUNCTION_DEFS,
    FunctionDef,
    child_statements,
)
from constricter.rules.tables import Tables, module_tables

_KEPT: Final = "_constricter_kept"  # the attribute a tree holds its last check in
_ROUNDS: Final = 5  # how many times to re-check what calls an unannotated function, at most
_TYPE_CHECKING: Final = "TYPE_CHECKING"


def check_source(
    source: str | bytes,
    filename: str = "<unknown>",
    checks: Checks = DEFAULT_CHECKS,
    *,
    outside: Outside | None = None,
) -> list[Offence]:
    """Return the offences in `source`, sorted. Raises `SyntaxError`.

    `outside` adds what's known of it from other files and a type checker, for `--fix` (see `Outside`).

    Returns:
      Every offence; `# noqa` comments are the caller's to apply.

    """
    return checked_source(source, filename, checks, outside=outside).offences


def checked_source(
    source: str | bytes,
    filename: str = "<unknown>",
    checks: Checks = DEFAULT_CHECKS,
    *,
    outside: Outside | None = None,
) -> "Checked":
    """Check `source`, as `check_source` does.

    Returns:
      Its offences, and what its functions return (see `Checked`).

    """
    tree: ast.Module
    own: Tables | None
    tree, own = _parse(source, filename)
    found: Checked = checked_tree(tree, checks, lines=as_text(source).splitlines(), outside=outside, own=own)
    if own is not None and isinstance(source, str):
        # Kept again: a file is checked again once its callers type its parameters, or its cycle's
        # files change what it imports. One `--fix` changed since is no longer this text.
        parsed.keep(source, (tree, own))
    return found


def _parse(source: str | bytes, filename: str) -> tuple[ast.Module, Tables | None]:
    """Parse `source` (see `parsed.parse`), or take the tree the index kept for it (`parsed.take`).

    Returns:
      The module, and the tables the index read from it if it was kept. Raises `SyntaxError`.

    """
    kept: parsed.Kept | None = parsed.take(source) if isinstance(source, str) else None
    return kept or (parsed.parse(source, filename), None)


def check_tree(
    tree: ast.Module,
    checks: Checks = DEFAULT_CHECKS,
    *,
    lines: Sequence[str] = (),
    outside: Outside | None = None,
    own: Tables | None = None,
) -> list[Offence]:
    """Return the offences in a parsed module, sorted.

    `# type:` comments are seen only if it was parsed with `type_comments=True`; they count for `=`
    and `with` too in a module written to run on Python 2. With its source `lines`, a `**rest`
    capture is reported at its name rather than at its pattern's start. `outside` adds what's known
    of it from other files and a type checker, for `--fix` (see `Outside`). `own`: the module's own
    tables, if already read from this tree (see `parsed.keep`).

    Returns:
      Every offence, in source order.

    """
    return checked_tree(tree, checks, lines=lines, outside=outside, own=own).offences


class Checked(NamedTuple):
    """A module's offences, what its unannotated functions return, and what it passes others' functions.

    What they return is for the files importing them; what it passes, for `fix.index.callers`.
    """

    offences: list[Offence]
    returned: Returns
    calls: Observed = Observed()


def checked_tree(
    tree: ast.Module,
    checks: Checks = DEFAULT_CHECKS,
    *,
    lines: Sequence[str] = (),
    outside: Outside | None = None,
    own: Tables | None = None,
) -> Checked:
    """Check a parsed module, as `check_tree` does.

    Returns:
      Its offences, in source order, and what its functions return (see `returned.exported`).

    """
    own = own or module_tables(tree)
    read: ImportPlan = imports.plan(tree)
    outside = None if outside is None else outside.usable(read.taken, imports.present(read, outside.guarded))
    # A second check's scopes it didn't check again are its first's, finished then.
    finished: frozenset[int] = _kept_scopes(tree)
    done: _Round = _resumed(tree, checks, outside) or _started(tree, checks, lines, own, outside)
    # Kept with the tree, for as long as it is: a second check may only know its parameters anew.
    vars(tree)[_KEPT] = _Kept(outside, checks, done)
    settings: Settings = done.settings
    scopes: list[Scope] = done.scopes()
    # A finding's kind is the code that reports it (LVA008, LVA009, LVA010).
    finish(tree, [scope for scope in scopes if id(scope) not in finished])
    finals: list[Offence] = [o for scope in scopes for o in late.finals(scope)] if checks.final else []
    reported: list[Offence] = [o for scope in scopes for o in scope.reported()]
    exported: Returns = returned.exported(done.found, settings.known.class_side.lineage)
    plan: ImportPlan = settings.known.names.plan or imports.plan(tree)
    # With the imports its fixes add under `if TYPE_CHECKING:`, which `outside.guarded` doesn't hold.
    guarded: dict[str, Guarded] = {
        **{name: each for name, each in plan.guarded.items() if each.statement is not None},
        **({} if outside is None else outside.guarded),
    }
    return Checked(
        sorted(
            [
                *reported,
                *redundant(tree, settings.checks.fixes),
                *flow_offences(module_flow(tree, scopes), settings.checks.fixes),
                *finals,
                *_attributes(tree, checks, done),
            ],
        ),
        exported._replace(names=imports.exported_names(exported, guarded, plan.added)),
        observed(tree, scopes, settings.known, {} if outside is None else outside.callees),
    )


def _attributes(tree: ast.Module, checks: Checks, done: "_Round") -> list[Offence]:
    """Report the plain classes' undeclared instance attributes (LVA013), where it's asked for.

    Returns:
      Their offences, each fixed as its method's scope offers it.

    """
    if not checks.attributes:
        return []
    return attributes.unannotated(
        tree,
        done.found,
        done.table.assigned,
        {id(func): scope for scope, func in done.functions},
    )


def _kept_scopes(tree: ast.Module) -> frozenset[int]:
    """Identify the scopes of a module's last check, kept on its tree (see `_Kept`).

    Returns:
      Their `id`s; none before its first.

    """
    kept: _Kept | None = cast("_Kept | None", vars(tree).get(_KEPT))
    return frozenset() if kept is None else frozenset(id(scope) for scope in kept.done.scopes())


def _started(
    tree: ast.Module,
    checks: Checks,
    lines: Sequence[str],
    own: Tables,
    outside: Outside | None,
) -> "_Round":
    """Check a module from the start (see `_settled`).

    Returns:
      The check.

    """
    first: Settings = module_settings(tree, checks, lines, own, outside)
    imported: Returns = Returns() if outside is None else outside.returned
    return _settled(tree, first, imported, bound_once(tree, first))


class _Round(NamedTuple):
    """A module's check as its rounds leave it: what checking it again starts from (see `_resumed`).

    The settings with what its functions return, each function with its latest scope, the module's
    and classes' bodies' scopes, the table its functions' `return`s are recorded in, and what they
    return.
    """

    settings: Settings
    functions: list[tuple[Scope, FunctionDef]]
    bodies: list[Scope]
    table: returned.Table
    found: Returned

    def scopes(self) -> list[Scope]:
        """List every scope: the functions', then the bodies'.

        Returns:
          Them.

        """
        return [scope for scope, _ in self.functions] + self.bodies


class _Kept(NamedTuple):
    """A module's last check, kept on its tree: what it knew from outside, its checks, and how it ended."""

    outside: Outside | None
    checks: Checks
    done: _Round

    def __deepcopy__(self, _memo: dict[int, object]) -> None:
        """Keep nothing in a copied tree: its nodes are new, so its check starts over.

        Any node's deep copy can reach the tree: `ast.Load()` is one object every tree shares, and
        pyflakes gives it a parent.
        """


def _resumed(tree: ast.Module, checks: Checks, outside: Outside | None) -> _Round | None:
    """Check a module again from where its last check ended, where only its parameters are typed anew.

    A file whose functions' parameters every call types (`Outside.parameters`) is checked a second
    time knowing them: with the same tree, checks and everything else from outside, only those
    functions are checked again, and what their new types reach, as any round's are (`_rounds`).

    Returns:
      The check; or `None` where it must start over: no check kept, anything else changed, LVA012
      asked for (its fix rewrites a scope's own), or a name of the module's top level typed anew.

    """
    kept: _Kept | None = cast("_Kept | None", vars(tree).get(_KEPT))
    if kept is None or outside is None or kept.outside is None or checks.final or kept.checks != checks:
        return None
    if replace(outside, parameters={}) != replace(kept.outside, parameters={}):
        return None
    seeded: Seeded = kept.done.settings.parameters or Seeded()
    passed: Mapping[int, Mapping[str, Passed]] = keyed(tree, outside.parameters)
    again: set[int] = {
        id(scope)
        for scope, func in kept.done.functions
        if seeded.callers.get(id(func)) != passed.get(id(func))
    }
    settings: Settings = replace(kept.done.settings, parameters=seeded._replace(callers=passed))
    done: _Round = _rounds(tree, kept.done._replace(settings=settings), outside.returned, again)
    return done if bound_once(tree, done.settings) == seeded.module else None


def _settled(
    tree: ast.Module,
    first: Settings,
    imported: Returns,
    names: dict[str, Passed],
    rounds: int = _ROUNDS,
) -> _Round:
    """Check the module's scopes, its functions reading its top level's `names` as typed (`bound_once`).

    A name the module binds to what an unannotated function returns is typed only once that
    function is checked: the scopes are then checked once more, knowing it, until no name's type
    is new (`rounds` times at most).

    Returns:
      The settings with what its functions return, the scopes checked with them, and what its own
      return.

    """
    table: returned.Table = returned.Table(tree, imported, first.known.vouched)
    seeded: Seeded = first.parameters or Seeded()
    # The table, filled in as the functions are checked in call order, is what they all read.
    settings: Settings = replace(
        first,
        known=replace(first.known, returned=table.returned),
        parameters=seeded._replace(module=names),
    )
    checked: _Round = _returned(tree, settings, module_scopes(tree, settings, table), table, imported)
    latest: dict[str, Passed] = bound_once(tree, checked.settings)
    return checked if latest == names or rounds <= 1 else _settled(tree, first, imported, latest, rounds - 1)


class Coverage(NamedTuple):
    """How many of a module's typeable first bindings are typed, of how many.

    `widened`: those a widening annotated (see `widened`), counted apart: not among the typed.
    """

    typed: int
    total: int
    widened: int = 0

    @property
    def percent(self) -> float:
        """The typed share, as a percentage (100 when there's nothing to type)."""
        return 100 * self.typed / self.total if self.total else 100.0


# The codes that mean a binding has no type at all (LVA003's type comment is a type).
_UNTYPED: Final = frozenset({UNANNOTATED, UNTYPED_TARGET, UNANNOTATED_MEMBER})


def annotation_coverage(source: str | bytes, checks: Checks = DEFAULT_CHECKS) -> Coverage:
    """Count the first bindings in `source` the rules cover, and how many are typed.

    Returns:
      The counts; `# noqa` comments don't make a binding typed. Raises `SyntaxError`.

    """
    tree: ast.Module = _parse(source, "<unknown>")[0]
    settings: Settings = module_settings(tree, checks, as_text(source).splitlines(), module_tables(tree))
    scopes: list[Scope] = module_scopes(tree, settings)
    total: int = sum(len(scope.bound()) for scope in scopes)
    untyped: int = sum(o.code in _UNTYPED for scope in scopes for o in scope.reported())
    wider: int = sum(len(scope.assignments.widened.intersection(scope.bound())) for scope in scopes)
    if checks.attributes:  # each plain class's instance attribute, typed where an annotation declares it
        declared: int
        every: int
        declared, every = attributes.counted(tree)
        total += every
        untyped += every - declared
    return Coverage(total - untyped - wider, total, wider)


def _returned(
    tree: ast.Module,
    settings: Settings,
    scopes: list[Scope],
    table: returned.Table,
    imported: Returns,
) -> _Round:
    """Check again what the first pass, in call order, couldn't type the first time.

    That pass typed each function knowing its callees' returns (see `module_scopes`); what's left is a
    function checked before a callee of its was typed (a cycle, `table.stale`), or with a late-typed
    name it didn't know from the start: `_rounds` checks those again.

    Returns:
      The check (see `_Round`), its settings with what the functions it imports return too.

    """
    found: Returned = returned.returned(
        tree,
        table.recorded,
        table.assigned,
        table.used,
        settings.known.vouched,
    )
    settings = replace(settings, known=replace(settings.known, returned=returned.joined(imported, found)))
    functions: list[tuple[Scope, FunctionDef]] = [
        (scope, scope.kind.function) for scope in scopes if scope.kind.function is not None
    ]
    # The first pass knew no attribute's type: they're read once every method is checked.
    again: set[int] = {
        id(scope)
        for scope, func in functions
        if table.stale(func)
        or scope.inferred.late.keys() - scope.inferred.seeded.keys()
        or stored.reads_own(tree, func, settings.owners, found)
    }
    bodies: list[Scope] = [scope for scope in scopes if scope.kind.function is None]
    return _rounds(tree, _Round(settings, functions, bodies, table, found), imported, again)


def _rounds(tree: ast.Module, start: _Round, imported: Returns, again: set[int]) -> _Round:
    """Check the functions whose scopes are in `again` once more, and then what their new types reach.

    Each round checks them again, reads what the unannotated functions return, and checks again any
    function calling one whose type is new; repeated until nothing changes, so `--fix` finds in one
    run what it would over several. The bodies are checked again if the rounds typed what they use.

    Returns:
      The check as the rounds leave it.

    """
    settings: Settings = start.settings
    functions: list[tuple[Scope, FunctionDef]] = start.functions
    table: returned.Table = start.table
    found: Returned = start.found
    changed: bool = False
    retyped: set[str] = set()  # the attributes the rounds typed anew
    _round: int
    for _round in range(_ROUNDS):
        if not again:
            break
        functions = _checked_again(tree, functions, again, settings, table)
        latest: Returned = returned.returned(
            tree,
            table.recorded,
            table.assigned,
            table.used,
            settings.known.vouched,
        )
        typed: bool = latest != found and returned.called(tree, tree, latest)  # even if only a body calls one
        # Attributes typed anew: what reads one, of any value, may be typed now.
        newly: set[str] = returned.retyped(found, latest)
        # Kept even when nothing here calls it: other files import what the module's functions return.
        if latest != found:
            found = latest
            settings = replace(
                settings,
                known=replace(settings.known, returned=returned.joined(imported, found)),
            )
            changed = changed or typed
            retyped |= newly
        again = {
            id(scope)
            for scope, func in functions
            if (typed and returned.called(tree, func, found))
            or stored.reads(tree, func, newly, anywhere=True)
            or scope.inferred.late.keys() - scope.inferred.seeded.keys()
        }
    bodies: list[Scope] = _bodies(
        tree,
        settings,
        start.bodies,
        (retyped if changed or retyped else None, found),
    )
    return _Round(settings, functions, bodies, table, found)


def _checked_again(
    tree: ast.Module,
    functions: list[tuple[Scope, FunctionDef]],
    again: set[int],
    settings: Settings,
    table: returned.Table,
) -> list[tuple[Scope, FunctionDef]]:
    """Check the functions whose scopes are in `again` once more, recording their `return`s and assignments.

    Returns:
      Every function, with its latest scope.

    """
    fresh: list[tuple[Scope, FunctionDef]] = [
        (function_scope(func, [], settings, scope.inferred.late), func)
        for scope, func in functions
        if id(scope) in again
    ]
    renewed: dict[int, Scope] = {id(func): scope for scope, func in fresh}
    finish(tree, [scope for scope, _ in fresh])
    table.recorded.update((id(func), recorded.returns(scope, func, tree)) for scope, func in fresh)
    table.assigned.update((id(func), recorded.assigned(scope)) for scope, func in fresh)
    table.used.update((id(func), recorded.used(scope, func, tree)) for scope, func in fresh)
    return [(renewed.get(id(func), scope), func) for scope, func in functions]


def _bodies(
    tree: ast.Module,
    settings: Settings,
    bodies: list[Scope],
    news: tuple[set[str] | None, Returned],
) -> list[Scope]:
    """Check the module and class bodies again, if the rounds typed anything they use.

    They were checked after every function, knowing the first pass's types: only what the rounds
    typed since is news to them (`news`: the attributes they typed, `None` if nothing at all; and
    what the module's own functions return).

    Returns:
      Their scopes, checked again or as they were.

    """
    retyped: set[str] | None
    own: Returned
    retyped, own = news
    if (
        retyped is not None
        and bodies
        and any(
            returned.called(tree, stmt, own) or stored.reads(tree, stmt, retyped, anywhere=True)
            for stmt in _body_statements(tree.body)
        )
    ):
        return body_scopes(tree, settings)
    return bodies


def _body_statements(body: Sequence[ast.stmt]) -> Iterator[ast.stmt]:
    """Walk a module's and its classes' own statements, not their functions'.

    Yields:
      Each statement (a function's definition too, but not what's inside it).

    """
    stmt: ast.stmt
    for stmt in body:
        yield stmt
        if isinstance(stmt, ast.ClassDef):
            yield from _body_statements(stmt.body)
        elif not isinstance(stmt, FUNCTION_DEFS):
            yield from _body_statements(child_statements(stmt))


def value_flow(
    source: str | bytes,
    filename: str = "<unknown>",
    checks: Checks = DEFAULT_CHECKS,
) -> list[Finding]:
    """Return the value-flow findings in `source`, sorted (see `constricter.flow`). Raises `SyntaxError`.

    `check_tree` reports each as the code its kind names (LVA008, LVA009, LVA010).

    Returns:
      Every finding, in source order.

    """
    tree: ast.Module = _parse(source, filename)[0]
    # Its lines place a `**rest` capture at its name, as `check_source` does.
    settings: Settings = module_settings(tree, checks, as_text(source).splitlines(), module_tables(tree))
    return module_flow(tree, module_scopes(tree, settings))
