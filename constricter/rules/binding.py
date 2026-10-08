# SPDX-License-Identifier: MIT
"""Binding the names a statement binds: each target typed, or declared before the statement.

`bind` is what `checker` calls for every statement: a plain `name = value` goes through the scope
(`Scope.assign`); a loop's or an unpacking's targets are split from the value's type and declared on a
line of their own before it; a loop typed only by its `# type:` comment (LVA003) declares that type
instead; `with manager as name` declares `name` first; and a `match`'s captures and an augmented
assignment are bound as they are. `walruses` binds a statement's `:=` targets, each declared before
it too.
"""

import ast
from collections.abc import Iterator, Mapping
from typing import Final, TypeAlias, cast

from constricter.fix.core.known import Inference, Known
from constricter.fix.libraries.opened import opened
from constricter.fix.values import shapes
from constricter.fix.values.doubts import bare
from constricter.fix.values.entered import entered, entered_async, entering
from constricter.fix.values.inference import LoopPart, inference, looped, looped_parts
from constricter.fix.values.targets import iterated, unpacked
from constricter.offences import COMMENT_TYPED_TARGET, UNTYPED_TARGET, VAGUE_TYPE, Edit, Fix, Offence, at
from constricter.rules.flow import augmented, members
from constricter.rules.scope import Late, Scope, certain_type, guessed_type, guesses_in
from constricter.rules.syntax import captures, comment_type, target_names, type_comment_span

_COMMENT: Final = "comment"  # the fix kind of LVA003's declaration
_UNPACK: Final = frozenset({"unpack"})  # the fix kind of an unpacking's split
_TUPLE: Final = ("tuple[", "Tuple[")  # how a tuple's type starts
_ANY: Final = ", ...]"  # and how one of any length ends
# A name's inference (`None`: unknown), whether it's a guess, and what the guess rests on.
# What `Scope.valued` gives.
_Valued: TypeAlias = tuple[Inference | None, bool, frozenset[str]]
_Named: TypeAlias = tuple[ast.Name, _Valued]
_COMPREHENSIONS: Final = (ast.ListComp, ast.SetComp, ast.DictComp, ast.GeneratorExp)
# Statements a declaration can't go before: a decorator's line is its definition's.
_DEFINITIONS: Final = (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)


def bind(scope: Scope, stmt: ast.stmt) -> None:
    """Bind the names `stmt` binds that need typing, reporting the untyped ones."""
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
        case ast.Assign(targets=[ast.Tuple() | ast.List() as target], value=value):
            _bind_unpacked(scope, stmt, target, value)
        case ast.Assign():
            _bind_assigned(scope, stmt)
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
            scope.lifetime(name).bind(at(single), bound, None if bound else _augmented_guess(scope, stmt))
            scope.inferred.rebound(name, bound)
        case _:
            pass


def walruses(scope: Scope, part: ast.AST, before: ast.stmt) -> None:
    """Bind the `:=` targets in `part`, an expression of a statement, each offered a declaration.

    Comprehensions included, lambdas excluded. A name can't be annotated where `:=` binds it: it's
    declared on a line of its own before `before` (its statement, or the `if` an `elif` belongs to),
    typed as a plain assignment's is. Not one inside a comprehension, whose value may read the
    comprehension's own names, nor where a line can't go before the statement: a definition (its
    decorators' lines are its own), or one that doesn't start its line (`else: x = (y := 1)`).
    Asked only in a module with a `:=` (`Settings.walruses`).
    """
    hidden: set[int] = _inside(part, ast.Lambda)
    line: bytes = scope.settings.lines[before.lineno - 1].encode() if scope.settings.lines else b""
    plain: bool = isinstance(before, _DEFINITIONS) or bool(line[: before.col_offset].strip())
    comprehended: set[int] = set() if plain else _inside(part, *_COMPREHENSIONS)
    code: str = scope.kind.unannotated
    node: ast.AST
    for node in ast.walk(part):
        if not isinstance(node, ast.NamedExpr) or id(node) in hidden:
            continue
        if plain or id(node) in comprehended:
            scope.bind(node.target.id, at(node.target), code)
        else:
            _bind_declaration(scope, before, node.target, code, scope.valued(node.value, node.lineno))


def _inside(part: ast.AST, *kinds: type[ast.AST]) -> set[int]:
    """Find every node inside a node of one of `kinds`, in `part`.

    Returns:
      Their `id()`s.

    """
    return {id(inner) for outer in ast.walk(part) if isinstance(outer, kinds) for inner in ast.walk(outer)}


def _bind_assigned(scope: Scope, stmt: ast.Assign) -> None:
    """Bind a chained assignment's names (`a = b = 0`), each offered a declaration before it, or others'."""
    code: str | None = scope.unannotated(stmt.type_comment)
    if not all(isinstance(target, ast.Name) for target in stmt.targets):
        _bind_targets(scope, stmt.targets, code)
        return
    target: ast.expr
    for target in stmt.targets:
        scope.assign(cast("ast.Name", target), code, stmt.value, stmt)


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


def _bind_unpacked(scope: Scope, stmt: ast.Assign, target: ast.expr, value: ast.expr) -> None:
    """Bind an unpacking's names, offering to declare each before `stmt` (see `_unpacked`).

    Every name is typed before any is bound, as its value is evaluated: `a, b = b, a`.
    """
    code: str | None = scope.unannotated(stmt.type_comment)
    name: ast.Name
    typed: _Valued
    for name, typed in list(_unpacked(scope, stmt, target, value)):
        _bind_declaration(scope, stmt, name, code, typed)


def _source(stmt: ast.stmt, name: ast.Name) -> ast.expr | None:
    """Find what a loop iterates, an unpacking splits or a `with` enters to bind `name`.

    Returns:
      It, or `None` for a name `stmt` binds otherwise (a `:=`'s, a chained assignment's).

    """
    target: ast.expr
    value: ast.expr
    items: list[ast.withitem]
    pairs: Iterator[tuple[ast.Name, ast.expr]]
    match stmt:
        case ast.For(target=target, iter=value) | ast.AsyncFor(target=target, iter=value):
            pairs = ((each, value) for each in target_names(target))
        case ast.Assign(targets=[target], value=value):
            pairs = _sources(target, value)
        case ast.With(items=items) | ast.AsyncWith(items=items):
            pairs = (
                (each, item.context_expr)
                for item in items
                if item.optional_vars is not None
                for each in target_names(item.optional_vars)
            )
        case _:
            return None
    return next((taken for each, taken in pairs if each is name), None)


def _sources(target: ast.expr, value: ast.expr) -> Iterator[tuple[ast.Name, ast.expr]]:
    """Pair each name an unpacking of `value` into `target` binds with what it's taken from.

    Yields:
      Each name, with its own value where a display of as many is split with the target (see
      `_unpacked`), else with `value`.

    """
    targets: list[ast.expr]
    values: list[ast.expr]
    match (target, value):
        case (
            ast.Tuple(elts=targets) | ast.List(elts=targets),
            ast.Tuple(elts=values) | ast.List(elts=values),
        ) if len(targets) == len(values) and not any(
            isinstance(part, ast.Starred) for part in (*targets, *values)
        ):
            part: ast.expr
            item: ast.expr
            for part, item in zip(targets, values, strict=True):
                yield from _sources(part, item)
        case _:
            name: ast.Name
            for name in target_names(target):
                yield name, value


def _unpacked(scope: Scope, stmt: ast.Assign, target: ast.expr, value: ast.expr) -> Iterator[_Named]:
    """Type each name an unpacking of `value` into `target` binds.

    A display of as many values is split with its target, each name typed by its own value as a
    plain assignment's is (`a, b = x, 1` declares `b: int` whatever `x` is); any other value's type
    is split over the names (see `unpacked`), or its elements' is (`a, b = range(2)`).

    Yields:
      Each name, with its inference, whether that's a guess, and what the guess rests on.

    """
    targets: list[ast.expr]
    values: list[ast.expr]
    name: ast.Name
    match (target, value):
        case (
            ast.Tuple(elts=targets) | ast.List(elts=targets),
            ast.Tuple(elts=values) | ast.List(elts=values),
        ) if len(targets) == len(values) and not any(
            isinstance(part, ast.Starred) for part in (*targets, *values)
        ):
            part: ast.expr
            item: ast.expr
            for part, item in zip(targets, values, strict=True):
                yield from _unpacked(scope, stmt, part, item)
        case (ast.Name() as name, _):
            fix: Inference | None
            unsafe: bool
            origins: frozenset[str]
            fix, unsafe, origins = scope.valued(value, stmt.lineno)
            yield name, (None if fix is None else fix._replace(kinds=fix.kinds | _UNPACK), unsafe, origins)
        case _:
            yield from _unpacked_whole(scope, stmt, target, value)


def _unpacked_whole(scope: Scope, stmt: ast.Assign, target: ast.expr, value: ast.expr) -> Iterator[_Named]:
    """Type each name an unpacking of `value` binds by `value`'s own type, split over them.

    Its type as any value's is inferred (a call's declared return with a vague part too: a part
    vaguer than `vague` allows is its name's type, and no fix); else what iterating it gives, each
    name an element.

    Yields:
      Each name, with its inference, whether that's a guess, and what the guess rests on.

    """
    known: Known = scope.settings.known
    typed: Inference | None = inference(value, known, scope.inferred.types)
    element: Inference | None
    if (element := None if typed else looped(value, known, scope.inferred.types)) is not None:
        typed = element._replace(annotation=f"tuple[{element.annotation}, ...]")
        yield from _split(scope, stmt, target, typed, iterated(value))
        return
    yield from _split(scope, stmt, target, typed, [value])


def _bind_declared(
    scope: Scope,
    stmt: ast.For | ast.AsyncFor,
    target: ast.expr,
    typed: Inference | None,
    bases: list[ast.expr],
) -> None:
    """Bind each name in a loop's `target`, offering to declare each before `stmt` (see `_split`)."""
    name: ast.Name
    part: _Valued
    for name, part in _split(scope, stmt, target, typed, bases):
        _bind_declaration(scope, stmt, name, UNTYPED_TARGET, part)


def _split(
    scope: Scope,
    stmt: ast.stmt,
    target: ast.expr,
    typed: Inference | None,
    bases: list[ast.expr],
) -> Iterator[_Named]:
    """Type each name in `target` (a loop's, or an unpacking's).

    `typed` is what the whole target gets (a loop's element, an unpacked value's type), split over
    its names (see `unpacked`); a name whose part isn't known gets no fix. The fixes are guesses if
    any of `bases`, the values `typed` came from, is.

    Yields:
      Each name, with its inference, whether that's a guess, and what the guess rests on.

    """
    unsafe: bool
    origins: frozenset[str]
    unsafe, origins = (False, frozenset()) if typed is None else guesses_in(scope, bases)
    # An unpacking's names are split from the value's type; a loop's are what it iterates (`loop`).
    split: frozenset[str] = frozenset() if isinstance(stmt, ast.For | ast.AsyncFor) else _UNPACK
    name: ast.Name
    annotation: str | None
    whole: str | None = None if typed is None else typed.annotation
    tuples: Mapping[str, str] = scope.settings.known.indirect.tuples
    parts: list[tuple[ast.Name, str | None]] = unpacked(target, whole, tuples)
    mixed: bool = _by_position(parts, whole or "", tuples)
    for name, annotation in parts:
        part: Inference | None = (
            None
            if typed is None or annotation is None or mixed
            else Inference(annotation, typed.reason, typed.kinds | split)
        )
        yield name, (part, unsafe, origins)


def _by_position(parts: list[tuple[ast.Name, str | None]], whole: str, tuples: Mapping[str, str]) -> bool:
    """Whether `parts`, split from `whole`, share a union that may be by position.

    A union over several names, of anything but a tuple of that many, is by position as often as
    not (`name, length`, of `[["prefix", 24], ...]`): each has no fix.

    Returns:
      Whether each name's part is the same union, of a `whole` that isn't a tuple of that many.

    """
    fixed: bool = tuples.get(whole, whole).startswith(_TUPLE) and not whole.endswith(_ANY)
    return (
        not fixed
        and len(parts) > 1
        and len({annotation for _, annotation in parts}) == 1
        and len(members(parts[0][1] or "") or ()) > 1
    )


def _bind_declaration(
    scope: Scope,
    stmt: ast.stmt,
    name: ast.Name,
    code: str | None,
    typed: _Valued,
) -> None:
    """Bind one name a statement binds, offering to declare it before `stmt` as `typed` has it.

    `typed`: its inference (`None`: unknown, when the type checker's hint is asked), whether that's a
    guess, and what the guess rests on. A loop's, an unpacking's or a `with`'s name left with no fix
    is noted with what it's taken from (see `_source`), for `late.widens`, whose wider type is
    declared before `stmt` too.
    """
    found: Inference | None
    unsafe: bool
    origins: frozenset[str]
    found, unsafe, origins = typed
    hint: Inference | None
    if (found is None or not scope.writable(found)) and (hint := scope.hint(name)) is not None:
        found, unsafe, origins = hint, True, hint.kinds
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
        scope.inferred.learn(
            name.id,
            found.annotation,
            origins if unsafe else None,
            again=name.id in scope.declared,
        )
    source: ast.expr | None
    if (source := None if fix or name.id in scope.declared else _source(stmt, name)) is not None:
        scope.assignments.plain[name.id] = (name, source, found)
        scope.assignments.chained[name.id] = (stmt.lineno, stmt.col_offset)
    certain: bool = found is not None and not unsafe and scope.writable(found)
    scope.bind(name.id, at(name), code, fix, found.annotation if found is not None and certain else None)


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
    """Bind each `with` item's target, offering to declare `with manager as name`'s `name` first.

    As what the manager's `__enter__` returns (see `constricter.fix.values.entered`); the file object
    `open` gives, which is its own context manager, by its literal mode. A target that unpacks takes
    that type split over its names, as an unpacking's are (but for a vague part). An `async with`'s
    is typed by a standard-library manager's `__aenter__` alone, and not split.
    """
    item: ast.withitem
    name: ast.Name
    target: ast.expr
    for item in items:
        typed: _Valued = _entered(scope, item.context_expr, asynchronous=isinstance(stmt, ast.AsyncWith))
        match item.optional_vars:
            case ast.Name() as name:
                _bind_declaration(scope, stmt, name, code, typed)
            case None:
                pass
            case target if isinstance(stmt, ast.With):
                named: _Named
                for named in _entered_parts(scope, target, item.context_expr, typed):
                    _bind_declaration(scope, stmt, named[0], code, named[1])
            case target:
                _bind_targets(scope, [target], code)


def _entered_parts(scope: Scope, target: ast.expr, manager: ast.expr, typed: _Valued) -> Iterator[_Named]:
    """Type each name a `with` statement's unpacking `target` binds, entering `manager`.

    `typed`: what the whole target gets (see `_entered`), split over its names as an unpacking's
    value is; where that's unknown, an `__enter__` declared to return a vague part is split instead
    (see `shapes.partly`). A part vaguer than `vague` allows is its name's type, and no fix.

    Yields:
      Each name, with its inference, whether that's a guess, and what the guess rests on.

    """
    known: Known = scope.settings.known
    whole: Inference | None = typed[0]
    doubt: tuple[bool, frozenset[str]] = typed[1:]
    if whole is None:
        whole = shapes.partly(
            entering(manager),
            known,
            lambda part: inference(part, known, scope.inferred.types),
        )
        doubt = guesses_in(scope, [manager])
    name: ast.Name
    part: str | None
    for name, part in unpacked(target, None if whole is None else whole.annotation, known.indirect.tuples):
        split: Inference | None = (
            None if whole is None or part is None else Inference(part, whole.reason, whole.kinds | _UNPACK)
        )
        yield name, (split, *doubt)


def _entered(scope: Scope, manager: ast.expr, *, asynchronous: bool = False) -> _Valued:
    """Infer what a `with` statement binds its target to, entering `manager`.

    Returns:
      The inference, whether it's a guess (the manager's type is one), and what the guess rests on;
      none for a generic class written without its arguments.

    """
    known: Known = scope.settings.known
    file: Inference | None
    if not asynchronous and (file := opened(manager, known)) is not None:
        return file, False, frozenset()
    found: tuple[Inference, list[ast.expr]] | None = (
        entered_async(manager, known, scope.inferred.types)
        if asynchronous
        else entered(manager, known, scope.inferred.types, scope.settings.facts.managers)
    )
    if found is None or bare(found[0].annotation, scope.settings.facts.generics):
        return None, False, frozenset()
    return (found[0], *guesses_in(scope, found[1]))


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


def _augmented_guess(scope: Scope, stmt: ast.AugAssign) -> Late | None:
    """Guess the type `name op= value` binds, where the name's type or the value's is only a guess.

    As the statement binds it once `--fix` has written those guesses, and they're declared.

    Returns:
      The type and what the guess rests on, or `None` if it's unknown still.

    """
    name: str = cast("ast.Name", stmt.target).id
    operand: Late | None = guessed_type(scope, stmt.value)
    certain: str | None = None if operand else certain_type(scope, stmt.value)
    bound: str | None = augmented(stmt.op, operand[0] if operand else certain, scope.inferred.types.get(name))
    none: frozenset[str] = frozenset()
    own: frozenset[str] = scope.inferred.origins.get(name, none) if name in scope.inferred.guesses else none
    origins: frozenset[str] = own | (operand[1] if operand else none)
    return (bound, origins) if bound is not None and origins else None


def annotated(scope: Scope, stmt: ast.AnnAssign, target: ast.Name) -> None:
    """Bind the name an annotated assignment declares (`name: T`, `name: T = value`).

    One a widening annotated (its statement's last line is marked: see `widened`) is typed by its
    value where `--fix` now knows it (see `_rewidened`), and has no type otherwise: a second pass
    then finds nothing the first didn't.
    """
    name: str = target.id
    annotation: ast.expr = stmt.annotation
    fresh: bool = name not in scope.declared
    marked: bool = stmt.end_lineno in scope.settings.known.limits.marks
    scope.declare(name)
    scope.annotation(name, annotation, marked=marked)
    if fresh and marked and _rewidened(scope, stmt, target):
        return
    if not marked:  # a widening's type says nothing of the value: what's read of the name has none
        scope.inferred.declare(name, annotation)
    scope.lifetime(name).declare(ast.unparse(annotation), at(target), _span(annotation, target))
    if stmt.value is not None:
        scope.lifetime(name).bind(at(target), certain_type(scope, stmt.value))
        scope.assigned(name, at(target))


def _rewidened(scope: Scope, stmt: ast.AnnAssign, target: ast.Name) -> bool:
    """Offer a marked annotation's value's own type in its place (LVA005), where `--fix` now knows it.

    The annotation is a widening's (see `widened`): the name is first bound here, as it was before
    it was written. Its fix writes over the annotation and deletes the mark; the name is then what
    its value makes it, to the rest of the scope.

    Returns:
      Whether it's offered; not for an annotation over several lines, a value `--fix` still can't
      type, or a scope it leaves alone.

    """
    name: str = target.id
    span: tuple[int, int] | None = _span(stmt.annotation, target)
    scope.assignments.widened.add(name)
    if stmt.value is None or span is None or not scope.kind.fixable:
        return False
    found: Inference | None
    unsafe: bool
    origins: frozenset[str]
    found, unsafe, origins = scope.valued(stmt.value, target.lineno)
    fix: Fix | None = (
        None if found is None else scope.offer(found, origins, unsafe=unsafe, edit=Edit.REPLACE, span=span)
    )
    if found is None or fix is None:
        return False
    last: int = stmt.end_lineno or target.lineno
    marked: Fix = fix._replace(drop=scope.settings.known.limits.marks[last], mark=last)
    scope.offences.append(Offence(*at(stmt.annotation), name, VAGUE_TYPE, marked))
    scope.lifetime(name).bind(at(target), None if unsafe else found.annotation)
    scope.assigned(name, at(target))
    scope.inferred.learn(name, found.annotation, origins if unsafe else None)
    return True


def _span(annotation: ast.expr, target: ast.expr) -> tuple[int, int] | None:
    """Find an annotation's columns, if it's all on its target's line (so `--fix` can rewrite it).

    Returns:
      Its start and end columns (UTF-8 bytes, as `ast` counts), or `None`.

    """
    one_line: bool = annotation.lineno == annotation.end_lineno == target.lineno
    return (annotation.col_offset, annotation.end_col_offset or 0) if one_line else None
