# SPDX-License-Identifier: MIT
"""A scope's late fixes: those that need the whole scope seen, run once it's checked (see `checker`).

`optionals` (`None`, then one type), `rebinds` (a fix refitted to every later value), `fills` (an
empty container typed by what's added to it), and `finals` (LVA012's `Final`).
"""

import ast
from collections.abc import Sequence
from dataclasses import replace
from typing import TYPE_CHECKING, Final

from constricter.fix import fills as filling
from constricter.fix import hinted
from constricter.fix.doubts import contains_inner, spelled_self
from constricter.fix.known import ImportPlan, Inference
from constricter.offences import (
    CAN_BE_FINAL,
    UNANNOTATED,
    UNANNOTATED_MEMBER,
    UNTYPED_TARGET,
    Edit,
    Fix,
    Offence,
)
from constricter.rules.annotations import node_name
from constricter.rules.flow import Binding, Lifetime, members
from constricter.rules.rebinding import Refit, refit
from constricter.rules.scope import FINAL_KIND, Late, Scope, imports_of
from constricter.rules.walked import walk

if TYPE_CHECKING:
    from constricter.rules.syntax import FunctionDef

_DISCARD: Final = "_"
_OPTIONAL: Final = "optional"  # the fix kind of a `None` default rebound to one type
_DECLARING: Final = frozenset({UNANNOTATED, UNTYPED_TARGET})  # the codes whose fix declares a name's type
_FILLED: Final = "filled"  # the fix kind (and guessing mechanism) of an empty container filled later
_NONE: Final = "None"
_FINAL: Final = "Final"
_TYPING_FINAL: Final = "typing.Final"
_FINALS: Final = frozenset({_TYPING_FINAL, "typing_extensions.Final"})
_NO_ALIASES: Final = frozenset[str]()


def optionals(scope: Scope) -> None:
    """Offer `T | None` to a name first bound to `None`, then only ever to a known `T`.

    Every later binding must have a type value flow is sure of (or `--fix` guessed, which makes
    this a guess too), all the same one, not itself allowing `None`, and nothing in another scope
    may write the name (`nonlocal`, `global`), nor read it: a function or lambda inside this one
    reading it sees the declared `T | None`, where a type checker without it would see what the
    name was narrowed to.
    """
    index: int
    o: Offence
    enclosed: frozenset[str] | None = None
    for index, o in enumerate(scope.offences):
        lifetime: Lifetime | None = scope.flow.get(o.name)
        if o.code != UNANNOTATED or _fixed(o) or lifetime is None or lifetime.escaped:
            continue
        if enclosed is None:
            function: FunctionDef | None = scope.kind.function
            inside: bool = function is not None and contains_inner(function, scope.settings.facts.inner)
            enclosed = _enclosed_reads(scope.kind.body()) if inside else frozenset()
        if o.name in enclosed:
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
        fix: Fix | None = scope.placed(
            o.name,
            Inference(f"{found} | None", reason, frozenset({_OPTIONAL}) | origins),
            origins,
            unsafe=bool(guesses),
        )
        scope.offences[index] = replace(o, edit=fix)
        scope.inferred.late[o.name] = (f"{found} | None", origins)


def rebinds(scope: Scope) -> None:
    """Refit each first binding's fix to every value the name is bound to later (see `rebinding`).

    A name something out of sight writes is left alone.
    """
    index: int
    o: Offence
    plan: ImportPlan | None = scope.settings.known.names.plan
    self_type: str | None = None if plan is None else spelled_self(plan)
    for index, o in enumerate(scope.offences):
        lifetime: Lifetime | None = scope.flow.get(o.name)
        fix: Fix | None = o.edit
        if o.code != CAN_BE_FINAL and fix is not None and lifetime is not None and FINAL_KIND in fix.kinds:
            if len(lifetime.bindings) > 1:  # a constant's `Final` (see `_constant`): bound again, it's none
                scope.offences[index] = replace(o, edit=None)
            continue
        if o.code not in _DECLARING or fix is None or lifetime is None or lifetime.escaped:
            continue
        first: Binding
        rest: list[Binding]
        first, *rest = lifetime.bindings
        if first.at != (o.line, o.col) or not rest:
            continue
        found: Refit | Fix | None = refit(o, fix, rest, scope.settings.hierarchy, self_type)
        refitted: Fix | None = _offered(scope, found) if isinstance(found, Refit) else found
        scope.offences[index] = replace(o, edit=refitted)


def _offered(scope: Scope, found: Refit) -> Fix | None:
    """Offer a refit fix, as the project's fix policy has it (see `offer`).

    Returns:
      The fix, or `None` if it isn't offered.

    """
    return scope.offer(found.found, found.origins, unsafe=found.unsafe, edit=found.edit, span=found.span)


def fills(scope: Scope) -> None:
    """Offer an empty container, bound nowhere else, the type of what its function adds to it.

    A guess (see `constricter.fix.fills`), resting on `filled` for `unsafe-fix-select`.
    """
    index: int
    o: Offence
    body: filling.Uses | None = None  # read once, for the first container to judge
    for index, o in enumerate(scope.offences):
        lifetime: Lifetime | None = scope.flow.get(o.name)
        kind: str | None = scope.assignments.empty.get(o.name)
        if o.code != UNANNOTATED or _fixed(o) or kind is None:
            continue
        if lifetime is None or lifetime.escaped or len(lifetime.bindings) != 1:
            continue
        body = body or filling.uses(scope.kind.body())
        found: Inference | None
        if (
            found := filling.filled(
                body,
                o.name,
                kind,
                scope.settings.known,
                scope.inferred.types,
            )
        ) is None:
            continue
        fix: Fix | None = scope.placed(o.name, found, frozenset({_FILLED}), unsafe=True)
        scope.offences[index] = replace(o, edit=fix)
        # What the scope infers from it (its `return`s) knows its type, a guess.
        scope.inferred.late[o.name] = (found.annotation, frozenset({_FILLED}))


def finals(scope: Scope) -> list[Offence]:
    """Find the names that could be `Final` (LVA012); run after `value_flow`, which marks escapes.

    Returns:
      An offence for each name bound exactly once, by a plain assignment outside any loop, and not
      declared apart from it or already `Final`, nor written from another scope; with a fix
      (see `_final`) where one is offered.

    """
    found: list[Offence] = []
    plan: ImportPlan | None = scope.settings.known.names.plan
    # What else the module calls `Final`: `from typing import Final as F`.
    aliases: frozenset[str] = frozenset(
        () if plan is None else (name for name, origin in plan.bound.items() if origin in _FINALS),
    )
    name: str
    lifetime: Lifetime
    for name, lifetime in scope.flow.items():
        if (
            name == _DISCARD
            or lifetime.escaped
            or scope.kind.unannotated == UNANNOTATED_MEMBER
            or len(lifetime.bindings) != 1
        ):
            continue
        where: tuple[int, int] = lifetime.bindings[0].at
        if scope.assignments.found.get(name) == [(where, False)] and (
            lifetime.declared is None
            or (lifetime.declared_at == where and not is_final(lifetime.declared, aliases))
        ):
            found.append(Offence(*where, name, CAN_BE_FINAL, _final(scope, name, lifetime)))
    return [scope.evaluated(o) for o in found]


def _final(scope: Scope, name: str, lifetime: Lifetime) -> Fix | None:
    """Offer LVA012's `Final`: around the annotation there (`Final[int]`), or as one (`: Final`).

    An unannotated name LVA001 would annotate gets `Final[T]` with LVA001's type instead, and
    LVA001's own fix is dropped: both write where the name is bound, and this one does for both.

    Returns:
      The fix, or `None` where the scope isn't fixed, the `final` kind isn't selected, an
      annotation spans lines, or the module can't name `Final`.

    """
    plan: ImportPlan | None = scope.settings.known.names.plan
    spelled: str | None = None if plan is None else plan.spell(_TYPING_FINAL)
    kinds: frozenset[str] = frozenset({FINAL_KIND})
    if (
        plan is None
        or spelled is None
        or not scope.kind.fixable
        or not scope.settings.checks.fixes.allows(kinds)
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
        text: str = scope.settings.lines[line - 1].encode()[start:end].decode()
        return _final_fix(
            Fix(f"{spelled}[{text}]", reason, edit=Edit.REPLACE, span=(start, end), kinds=kinds),
            plan,
        )
    index: int
    o: Offence
    for index, o in enumerate(scope.offences):
        if o.name == name and o.code == UNANNOTATED and o.edit is not None and o.edit.edit == Edit.ANNOTATE:
            scope.offences[index] = replace(o, edit=None)
            return _final_fix(
                o.edit._replace(annotation=f"{spelled}[{o.edit.annotation}]", kinds=o.edit.kinds | kinds),
                plan,
            )
    return _final_fix(Fix(spelled, reason, kinds=kinds), plan)


def is_final(annotation: str, aliases: frozenset[str] = _NO_ALIASES) -> bool:
    """Check whether an annotation is `Final` (`Final[T]`, `typing.Final`, ...), or one of `aliases` for it.

    Returns:
      Whether it is.

    """
    # `annotation` is always `ast.unparse`'s own output, so it's always valid Python to parse back.
    root: ast.expr = ast.parse(annotation, mode="eval").body
    return node_name(root.value if isinstance(root, ast.Subscript) else root) in aliases | {_FINAL}


def _final_fix(fix: Fix, plan: ImportPlan) -> Fix:
    """Give a `Final` fix the imports its annotation needs.

    Returns:
      It, with them.

    """
    return fix._replace(imports=imports_of(fix.annotation, plan), after=plan.after)


def _enclosed_reads(body: Sequence[ast.stmt]) -> frozenset[str]:
    """Name what the functions and lambdas inside a function's `body` read.

    Returns:
      Each name read in one, however deep.

    """
    return frozenset(
        node.id
        for stmt in body
        for inner in walk(stmt)
        if isinstance(inner, ast.FunctionDef | ast.AsyncFunctionDef | ast.Lambda)
        for node in walk(inner)
        if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load)
    )


def _fixed(offence: Offence) -> bool:
    """Check whether an offence already has a fix a late one (`optionals`, `fills`) mustn't replace.

    Returns:
      Whether it has one, other than a type checker's hint (`--infer-with`), which one would.

    """
    return offence.edit is not None and hinted.KIND not in offence.edit.kinds
