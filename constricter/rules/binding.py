# SPDX-License-Identifier: MIT
"""Binding the names a statement binds: each target typed, or declared before the statement.

`bind` is what `checker` calls for every statement: a plain `name = value` goes through the scope
(`Scope.assign`); a loop's or an unpacking's targets are split from the value's type and declared on a
line of their own before it; a loop typed only by its `# type:` comment (LVA003) declares that type
instead; `with open(...) as f` declares `f` first; and a `match`'s captures and an augmented
assignment are bound as they are.
"""

import ast
from typing import Final, cast

from constricter.fix import hinted
from constricter.fix.inference import LoopPart, inference, looped, looped_parts
from constricter.fix.known import Inference
from constricter.fix.opened import opened
from constricter.fix.targets import iterated, unpacked
from constricter.offences import COMMENT_TYPED_TARGET, UNTYPED_TARGET, Edit, Fix, at
from constricter.rules.flow import augmented
from constricter.rules.scope import Scope, certain_type, guesses_in
from constricter.rules.syntax import captures, comment_type, target_names, type_comment_span

_COMMENT: Final = "comment"  # the fix kind of LVA003's declaration


def bind(scope: Scope, stmt: ast.stmt) -> None:
    """Bind the names `stmt` binds that need typing, reporting the untyped ones."""
    targets: list[ast.expr]
    target: ast.expr
    items: list[ast.withitem]
    comment: str | None
    name: str
    single: ast.Name
    value: ast.expr
    cases: list[ast.match_case]
    op: ast.operator
    match stmt:
        case ast.Assign(targets=[ast.Name() as single], value=value, type_comment=comment):
            scope.assign(single, scope.unannotated(comment), value)
        case ast.Assign(targets=[ast.Tuple() | ast.List() as target], value=value, type_comment=comment):
            typed: Inference | None = inference(value, scope.settings.known, scope.inferred.types)
            _bind_declared(scope, stmt, target, typed, [value])
        case ast.Assign(targets=targets, type_comment=comment):
            _bind_targets(scope, targets, scope.unannotated(comment))
        case ast.With(items=items, type_comment=comment) | ast.AsyncWith(items=items, type_comment=comment):
            _bind_with(scope, stmt, items, scope.unannotated(comment))
        case (
            ast.For(target=target, iter=value, type_comment=None)
            | ast.AsyncFor(
                target=target,
                iter=value,
                type_comment=None,
            )
        ):
            _bind_loop(scope, stmt, target, value)
        case (
            ast.For(target=target, type_comment=str() as comment)
            | ast.AsyncFor(
                target=target,
                type_comment=str() as comment,
            )
        ):
            _bind_commented(scope, stmt, target, comment)
        case ast.Match(cases=cases):
            _bind_captures(scope, cases)
        case ast.AugAssign(target=ast.Name(id=name) as single, op=op, value=value):
            own: str | None = None if name in scope.inferred.guesses else scope.inferred.types.get(name)
            bound: str | None = augmented(op, certain_type(scope, value), own)
            scope.lifetime(name).bind(at(single), bound)
            scope.inferred.rebound(name, bound)
        case _:
            pass


def _bind_loop(scope: Scope, stmt: ast.For | ast.AsyncFor, target: ast.expr, value: ast.expr) -> None:
    """Bind a loop's target (see `_bind_declared`), over `enumerate` or `zip` one part at a time.

    `for i, x in enumerate(xs)` declares `i: int` even when `xs`'s elements aren't known, and a
    guess about them makes only `x`'s fix one.
    """
    parts: list[LoopPart] | None = looped_parts(
        value,
        scope.settings.known,
        scope.inferred.types,
    )
    elements: list[ast.expr]
    match target:
        case ast.Tuple(elts=elements) | ast.List(elts=elements) if (
            parts is not None
            and len(elements) == len(parts)
            and not any(isinstance(element, ast.Starred) for element in elements)
        ):
            element: ast.expr
            typed: Inference | None
            bases: list[ast.expr]
            for element, (typed, bases) in zip(elements, parts, strict=True):
                _bind_declared(scope, stmt, element, typed, bases)
        case _:
            _bind_declared(
                scope,
                stmt,
                target,
                looped(value, scope.settings.known, scope.inferred.types),
                iterated(value),
            )


def _bind_declared(
    scope: Scope,
    stmt: ast.stmt,
    target: ast.expr,
    typed: Inference | None,
    bases: list[ast.expr],
) -> None:
    """Bind each name in `target` (a loop's, or an unpacking's), offering to declare each before `stmt`.

    `typed` is what the whole target gets (a loop's element, an unpacked value's type), split over
    its names (see `unpacked`); a name whose part isn't known gets no fix. The fixes are guesses if
    any of `bases`, the values `typed` came from, is. A loop's untyped target is LVA002, an
    unpacking's LVA001 (or LVA004), unless a type comment types it.
    """
    unsafe: bool
    origins: frozenset[str]
    unsafe, origins = (False, frozenset()) if typed is None else guesses_in(scope, bases)
    # An unpacking's names are split from the value's type; a loop's are what it iterates (`loop`).
    split: frozenset[str] = frozenset() if isinstance(stmt, ast.For | ast.AsyncFor) else frozenset({"unpack"})
    code: str | None = (
        UNTYPED_TARGET
        if isinstance(stmt, ast.For | ast.AsyncFor)
        else scope.unannotated(cast("ast.Assign", stmt).type_comment)
    )
    name: ast.Name
    annotation: str | None
    for name, annotation in unpacked(target, None if typed is None else typed.annotation):
        part: Inference | None = (
            None
            if typed is None or annotation is None
            else Inference(annotation, typed.reason, typed.kinds | split)
        )
        _bind_declaration(scope, stmt, name, code, (part, unsafe, origins))


def _bind_declaration(
    scope: Scope,
    stmt: ast.stmt,
    name: ast.Name,
    code: str | None,
    typed: tuple[Inference | None, bool, frozenset[str]],
) -> None:
    """Bind one name a statement binds, offering to declare it before `stmt` as `typed` has it.

    `typed`: its inference (`None`: unknown, when the type checker's hint is asked), whether that's a
    guess, and what the guess rests on.
    """
    found: Inference | None
    unsafe: bool
    origins: frozenset[str]
    found, unsafe, origins = typed
    if found is None and (found := scope.hint(name)) is not None:
        unsafe, origins = True, frozenset({hinted.KIND})
    fix: Fix | None = None
    if found is not None:
        fix = scope.offer(
            found,
            origins,
            unsafe=unsafe,
            edit=Edit.DECLARE,
            span=(stmt.lineno, stmt.col_offset),
        )
        # What the rest of the scope infers from `name` knows its type, as for `name = value`.
        scope.inferred.learn(name.id, found.annotation, origins if unsafe else None)
    scope.bind(name.id, at(name), code, fix)


def _bind_commented(scope: Scope, stmt: ast.For | ast.AsyncFor, target: ast.expr, comment: str) -> None:
    """Bind a loop's target typed only by its `# type:` comment (LVA003), offering to declare it instead.

    The comment's type (`int`, or `int, str` for a tuple target) is split over the target's names as
    an unpacking's is; each is declared before the loop, and the comment dropped, since a type checker
    would see the name declared twice. Only for a loop whose header is on one line, where the comment
    is found after its iterable.
    """
    drop: tuple[int, int] | None = type_comment_span(scope.settings.lines, stmt)
    annotation: str | None = comment_type(comment) if drop is not None else None
    name: ast.Name
    part: str | None
    for name, part in unpacked(target, annotation):
        fix: Fix | None = None
        if part is not None and drop is not None:
            fix = scope.offer(
                Inference(part, "its `# type:` comment", frozenset({_COMMENT})),
                frozenset(),
                unsafe=False,
                edit=Edit.DECLARE,
                span=(stmt.lineno, stmt.col_offset),
            )
            fix = None if fix is None else fix._replace(drop=drop)
        scope.bind(name.id, at(name), COMMENT_TYPED_TARGET, fix)


def _bind_with(scope: Scope, stmt: ast.stmt, items: list[ast.withitem], code: str | None) -> None:
    """Bind each `with` item's target, offering to declare `with open(path, mode) as f`'s `f` first.

    The file object `open` gives is its context manager's own (`__enter__` returns `self`), typed by
    its literal mode; any other item's names are bound untyped, as are an `async with`'s (a file
    object isn't an asynchronous context manager).
    """
    item: ast.withitem
    name: ast.Name
    target: ast.expr
    for item in items:
        typed: Inference | None = (
            opened(item.context_expr, scope.settings.known) if isinstance(stmt, ast.With) else None
        )
        match item.optional_vars:
            case ast.Name() as name:
                _bind_declaration(scope, stmt, name, code, (typed, False, frozenset()))
            case None:
                pass
            case target:
                _bind_targets(scope, [target], code)


def _bind_targets(scope: Scope, targets: list[ast.expr], code: str | None) -> None:
    """Bind every name in `targets`, reporting `code` for each first binding."""
    target: ast.expr
    name: ast.Name
    for target in targets:
        for name in target_names(target):
            scope.bind(name.id, at(name), code)


def _bind_captures(scope: Scope, cases: list[ast.match_case]) -> None:
    """Bind every name the `case` patterns capture: LVA002 unless declared first."""
    case: ast.match_case
    name: str
    where: tuple[int, int]
    for case in cases:
        for name, where in captures(case.pattern, scope.settings.lines):
            scope.bind(name, where, UNTYPED_TARGET)
