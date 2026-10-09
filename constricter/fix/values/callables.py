# SPDX-License-Identifier: MIT
"""`--fix` for a function, a bound method or a lambda bound to a name: `dump = json.dumps`, `grow = it.grow`.

A `Callable[..., R]`, `R` what a call of it gives whatever it's passed: a function declaring its
return (the module's, another checked file's, a builtin's or the standard library's with one), or
a method one does on a receiver whose type is known. Its parameters are left open (`...`): a
`Callable[[A], R]` would refuse the keywords and defaults a call through the name may use; they're
listed where the function has neither, and no call through the name passes one (`_taken`). Not a
class (a `type[C]`), a callee typed only by its `return`s, nor a name the function reads an
attribute of (`run.cache_clear()`), which a `Callable` doesn't have. A lambda is one of what its
body gives, where that rests on none of its parameters or its function's names: `Callable[[], R]`
if it takes none; one resting on its parameters, by what every call of it in its function passes
them (`called`). A module's or a class body's name is one too: a plain class's, as a guess.
"""

import ast
import builtins
from collections import Counter
from collections.abc import Callable, Mapping, Sequence
from itertools import islice
from typing import Final, NamedTuple, TypeAlias

from constricter.fix.core.known import ImportPlan, Inference, Known
from constricter.fix.libraries import stdlib
from constricter.fix.values.fills import Uses
from constricter.fix.values.guesses import fixed_by_callee
from constricter.fix.values.inference import inference
from constricter.rules.annotations import defined_type_vars, dotted, roots
from constricter.rules.syntax import FunctionDef
from constricter.rules.walked import classes, walk

KIND: Final = "callable"  # the fix kind of a function or method bound to a name
_CALLERS: Final = "callers"  # and of what every call passes a parameter (see `constricter.fix.index.callers`)
_CALLABLE: Final = "collections.abc.Callable"
_OPEN: Final = "..."  # a `Callable`'s parameters, left open
_SELF: Final = "Self"
_Infer: TypeAlias = Callable[[ast.expr], Inference | None]


class Site(NamedTuple):
    """Where a name is bound to a callable.

    `function`: the function it's bound in (`None`: a module's or a class's body); `owner`: a class
    body's class; `attributed`: the names the module reads an attribute of, anywhere; `positional`:
    its functions' parameters' types, where a `Callable` can list them (see `signatures`).
    """

    function: FunctionDef | None
    owner: str | None = None
    attributed: frozenset[str] = frozenset()
    positional: Mapping[str, tuple[str, ...]] = {}


def signatures(tree: ast.Module) -> dict[str, tuple[str, ...]]:
    """Read what each of the module's functions takes, where a `Callable` can say it: `[int, str]`.

    A plain `def` at its top level, or (as `Class.method`, less its first parameter) directly in a
    class, defined once and undecorated, every parameter positional, annotated and without a
    default, none naming a type variable or `Self`.

    Returns:
      Each one's parameters' types, in order.

    """
    unusable: frozenset[str] = defined_type_vars(tree) | {_SELF}
    found: dict[str, tuple[str, ...]] = _signatures(tree.body, "", unusable)
    owners: Counter[str] = Counter(node.name for node in classes(tree))
    node: ast.ClassDef
    for node in classes(tree):
        if owners[node.name] == 1:
            found.update(_signatures(node.body, f"{node.name}.", unusable))
    return found


def _signatures(
    body: Sequence[ast.stmt],
    prefix: str,
    unusable: frozenset[str],
) -> dict[str, tuple[str, ...]]:
    """Read what the functions directly in `body` take (see `signatures`); `prefix`: a class's, its methods'.

    Returns:
      Each one's parameters' types, by its name after `prefix`.

    """
    counts: Counter[str] = Counter(
        stmt.name for stmt in body if isinstance(stmt, ast.FunctionDef | ast.AsyncFunctionDef)
    )
    found: dict[str, tuple[str, ...]] = {}
    stmt: ast.stmt
    for stmt in body:
        if not isinstance(stmt, ast.FunctionDef) or counts[stmt.name] != 1 or stmt.decorator_list:
            continue
        args: ast.arguments = stmt.args
        skipped: int = 1 if prefix else 0  # a method's `self`
        named: list[ast.arg] = [*args.posonlyargs, *args.args][skipped:]
        types: list[str] = [ast.unparse(arg.annotation) for arg in named if arg.annotation is not None]
        plain: bool = not (args.defaults or args.kwonlyargs or args.vararg or args.kwarg)
        if plain and len(types) == len(named) and not unusable & roots(f"[{', '.join(types)}]"):
            found[f"{prefix}{stmt.name}"] = tuple(types)
    return found


def aliased(
    target: ast.Name,
    value: ast.expr,
    site: Site,
    known: Known,
    typed: tuple[Mapping[str, str], _Infer],
) -> tuple[Inference, ast.expr] | None:
    """Infer a name bound to a function, a bound method or a lambda, at `site`: a `Callable[..., R]`.

    `typed`: the scope's typed names, and what infers a value with them. Its parameters are listed
    (`Callable[[A], R]`) where the function declares them all positional, and every call through
    the name in its function passes them so.

    Returns:
      The inference, and the call that gives `R` (whose guesses are its own); `None` for any other
      value, one whose call's type its arguments decide or nothing declares, a class, a module that
      can't name `Callable`, or a name an attribute is read of.

    """
    if isinstance(value, ast.Lambda):
        return _lambda(target, value, site, known)
    if not isinstance(value, ast.Name | ast.Attribute) or _is_class(value, known):
        return None
    call: ast.Call = ast.copy_location(ast.Call(value, [], []), value)
    fixed: bool = fixed_by_callee(call, known, typed[0]) or (
        stdlib.resolved(value, known.names.stdlib) in stdlib.RETURNS
    )
    found: Inference | None = typed[1](call) if fixed else _method(value, site, known)
    plan: ImportPlan | None = known.names.plan
    if found is None or plan is None or _read(target.id, site):
        return None
    spelled: str | None
    if (spelled := plan.spell(_CALLABLE)) is None:
        return None
    taken: str = _taken(target.id, value, site, known, typed[1])
    reason: str = f"`{ast.unparse(value)}`, whose call gives {found.reason}"
    return Inference(f"{spelled}[{taken}, {found.annotation}]", reason, found.kinds | {KIND}), call


def _method(value: ast.expr, site: Site, known: Known) -> Inference | None:
    """Type a call of one of a class's own methods, named in its body (`items = _items`).

    Returns:
      Its declared return, or `None` for anything else, anywhere else.

    """
    declared: str | None = (
        known.methods.get(site.owner or "", {}).get(value.id) if isinstance(value, ast.Name) else None
    )
    if declared is None or not isinstance(value, ast.Name):
        return None
    return Inference(declared, f"`{site.owner}.{value.id}`'s declared return type", frozenset({"method"}))


def _taken(name: str, value: ast.Name | ast.Attribute, site: Site, known: Known, infer: _Infer) -> str:
    """Write what a callable bound to `name` takes: its parameters' types, or `...`.

    Listed for one of the module's functions, or a method of its classes on a receiver whose type
    is known, that `signatures` reads, bound in a function whose every call through the name passes
    as many arguments, by position.

    Returns:
      A `Callable`'s first argument.

    """
    key: str | None = None
    owner: Inference | None = None if isinstance(value, ast.Name) else infer(value.value)
    if isinstance(value, ast.Name):
        key = value.id
    elif owner is not None:
        key = f"{known.class_side.lineage.definer(owner.annotation, value.attr)}.{value.attr}"
    taken: tuple[str, ...] | None = site.positional.get(key or "")
    if taken is None or site.function is None:
        return _OPEN
    calls: list[ast.Call] = [
        node
        for node in walk(site.function)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == name
    ]
    positional: bool = all(
        not call.keywords
        and len(call.args) == len(taken)
        and not any(isinstance(arg, ast.Starred) for arg in call.args)
        for call in calls
    )
    return f"[{', '.join(taken)}]" if positional else _OPEN


def _lambda(
    target: ast.Name,
    value: ast.Lambda,
    site: Site,
    known: Known,
) -> tuple[Inference, ast.expr] | None:
    """Infer a name bound to a lambda: a `Callable` of what its body gives, whatever its names hold.

    `Callable[[], R]` for one that takes nothing, `Callable[..., R]` otherwise: nothing types its
    parameters, and its function's names are read only when it's called, so its body's type rests
    on neither.

    Returns:
      The inference, and the body (whose guesses are its own); or `None` (see `aliased`).

    """
    args: ast.arguments = value.args
    params: bool = any((args.posonlyargs, args.args, args.kwonlyargs, args.vararg, args.kwarg))
    # With none of the function's names: it reads them when it's called, whatever they hold then.
    found: Inference | None = inference(value.body, known, {})
    plan: ImportPlan | None = known.names.plan
    spelled: str | None = None if plan is None or found is None else plan.spell(_CALLABLE)
    if found is None or spelled is None or _read(target.id, site):
        return None
    taken: str = _OPEN if params else "[]"
    reason: str = f"a lambda, whose body is {found.reason}"
    return Inference(f"{spelled}[{taken}, {found.annotation}]", reason, found.kinds | {KIND}), value.body


def called(
    value: ast.Lambda,
    name: str,
    uses: Uses,
    known: Known,
    declared: Mapping[str, str],
) -> tuple[Inference, list[ast.expr]] | None:
    """Infer a lambda bound to `name` whose body rests on its parameters, by what its calls pass them.

    Every use of the name in its function (`uses`) a call passing each parameter by position, each
    one's arguments of one type: its body is typed with those, and none of the function's names. A
    lambda of plain positional parameters, without defaults. A guess (`callers`): a call added
    later may pass another type.

    Returns:
      The inference (a `Callable[..., R]`), and the arguments it rests on; or `None`.

    """
    args: ast.arguments = value.args
    params: list[ast.arg] = [*args.posonlyargs, *args.args]
    passed: list[ast.expr] | None = _passed(name, uses, len(params))
    if args.defaults or args.kwonlyargs or args.vararg or args.kwarg or name in uses.nested:
        return None
    if not (params and passed):
        return None
    given: list[Inference | None] = [inference(arg, known, declared) for arg in passed]
    typed: dict[str, str | None] = {
        param.arg: _one(
            {None if each is None else each.annotation for each in islice(given, at, None, len(params))},
        )
        for at, param in enumerate(params)
    }
    found: Inference | None = (
        None
        if None in typed.values()
        else inference(value.body, known, {param: text for param, text in typed.items() if text})
    )
    plan: ImportPlan | None = known.names.plan
    spelled: str | None = None if plan is None or found is None else plan.spell(_CALLABLE)
    if found is None or spelled is None:
        return None
    reason: str = f"a lambda, whose body is {found.reason}, given what its calls pass it"
    kinds: frozenset[str] = found.kinds.union({KIND, _CALLERS}, *(each.kinds for each in given if each))
    return Inference(f"{spelled}[{_OPEN}, {found.annotation}]", reason, kinds), passed


def _one(types: set[str | None]) -> str | None:  # the one type every call passes, if they agree
    return next(iter(types)) if len(types) == 1 else None


def _passed(name: str, uses: Uses, count: int) -> list[ast.expr] | None:
    """List what every call of `name` in its function passes it: `count` arguments each, by position.

    Returns:
      The arguments, call after call; `None` where a use isn't such a call.

    """
    found: list[ast.expr] = []
    node: ast.Name
    for node in uses.names.get(name, []):
        parent: ast.AST | None = uses.parents.get(id(node))
        if (
            not isinstance(parent, ast.Call)
            or parent.func is not node
            or parent.keywords
            or len(parent.args) != count
            or any(isinstance(arg, ast.Starred) for arg in parent.args)
        ):
            return None
        found.extend(parent.args)
    return found


def _is_class(value: ast.expr, known: Known) -> bool:
    """Check whether a name is a class the module knows, or a builtin one it doesn't rebind.

    Returns:
      Whether it is: calling it constructs one, and the name is a `type[C]`.

    """
    name: str | None
    if (name := dotted(value)) is None:
        return False
    return name in known.classes or (known.is_builtin(name) and isinstance(vars(builtins).get(name), type))


def _read(name: str, site: Site) -> bool:
    """Check whether an attribute of `name` is read where it's bound (`name.cache_clear()`, `name.__name__`).

    In its function; anywhere in the module, for a module's or a class body's name.

    Returns:
      Whether one is.

    """
    if site.function is None:
        return name in site.attributed
    return any(
        isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name) and node.value.id == name
        for node in walk(site.function)
    )
