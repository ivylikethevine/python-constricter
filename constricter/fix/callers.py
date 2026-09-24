# SPDX-License-Identifier: MIT
"""Unannotated parameters typed by their callers: what every call in the checked files passes each one.

Once every file is checked, each module's `Observed` calls to the checked files' open functions (see
`modules.open_functions`) are matched to their parameters, as Python binds them. A parameter left
unannotated is typed when every call passes it, each an argument of the same known type
(`rules.calls` says which count); not if a call leaves it to its default, can't be matched, or
unpacks its arguments, nor if the function escapes (a callback), and never for a function no file
calls. The files defining them are then checked again knowing those types, as guesses (`callers`):
a caller outside the checked files may pass anything.
"""

from collections.abc import Iterable, Mapping, Sequence
from pathlib import Path
from typing import Final, TypeAlias

from constricter.fix import project
from constricter.fix.known import Call, Callee, Observed, Origin, Passed, Seeds
from constricter.fix.modules import SUFFIX, Index, Param

KIND: Final = "callers"  # the guessing mechanism (`FIX_KINDS`)
# A module's functions' typed parameters: each one's type and what it rests on, by name, by function.
Parameters: TypeAlias = dict[str, dict[str, Passed]]
_POSITIONAL: Final = frozenset({"p", "e"})
_KEYWORD: Final = frozenset({"e", "k"})
_UNPASSED: Final = ""  # a parameter a call leaves to its default


def parameters(observations: Iterable[Observed], catalog: Index) -> dict[str, Parameters]:
    """Type the checked files' functions' unannotated parameters by every call to them (see the docstring).

    Returns:
      Each typed parameter's type, by its function and module.

    """
    calls: dict[Callee, list[Call]] = {}
    escaped: set[Callee] = set()
    observed: Observed
    for observed in observations:
        escaped.update(observed.escaped)
        callee: Callee
        found: tuple[Call, ...]
        for callee, found in observed.calls.items():
            calls.setdefault(callee, []).extend(found)
    typed: dict[str, Parameters] = {}
    each: list[Call]
    for callee, each in calls.items():
        module: str
        function: str
        module, function = callee
        params: tuple[Param, ...] | None = (
            None
            if callee in escaped or module not in catalog.modules
            else catalog.modules[module].open.get(function)
        )
        types: dict[str, Passed]
        if types := {} if params is None else _typed(params, each):
            typed.setdefault(module, {})[function] = types
    return typed


def _typed(params: Sequence[Param], calls: Sequence[Call]) -> dict[str, Passed]:
    """Type a function's unannotated parameters by `calls`: each one's, if every call passes it the same.

    Returns:
      Each typed parameter's type, and what its arguments' types rest on together.

    """
    bound: list[dict[str, Passed | None] | None] = [_bound(params, call) for call in calls]
    found: dict[str, Passed] = {}
    param: Param
    for param in params:
        name: str = param[0]
        passed: list[Passed | None] = [
            None if one is None else one.get(name, (_UNPASSED, frozenset())) for one in bound
        ]
        types: set[str | None] = {None if one is None else one[0] for one in passed}
        only: str | None = types.pop() if len(types) == 1 else None
        if not param[3] and only:
            found[name] = (only, frozenset().union(*(one[1] for one in passed if one is not None)))
    return found


def _bound(params: Sequence[Param], call: Call) -> dict[str, Passed | None] | None:
    """Bind a call's arguments' types to a function's parameters, as Python binds the arguments.

    Returns:
      Each parameter's argument's type (`None`: unknown), by name, a parameter it leaves to its
      default missing; or `None` if they can't be bound (unpacked, too many, an unknown keyword, one
      bound twice): a call that fails, or can't be read.

    """
    positional: list[str] = [param[0] for param in params if param[1] in _POSITIONAL]
    if call.unpacked or len(call.positional) > len(positional):
        return None
    bound: dict[str, Passed | None] = dict(zip(positional, call.positional, strict=False))
    keyword: str
    typed: Passed | None
    for keyword, typed in call.keywords:
        if keyword in bound or not any(param[0] == keyword and param[1] in _KEYWORD for param in params):
            return None
        bound[keyword] = typed
    return bound


def callees(catalog: project.Index, path: Path) -> dict[str, Callee]:
    """Find the checked files' functions the file at `path` may call whose parameters aren't all annotated.

    Its own (`f`), and those it imports (`f`, `u.f`, through re-exports); not an installed package's.

    Returns:
      Each, as the file spells it, mapped to its module and name; nothing for a file `catalog` doesn't
      have.

    """
    target: project.Module | None
    if path.suffix != SUFFIX or (target := catalog.modules.get(project.module_name(path))) is None:
        return {}
    found: dict[str, Callee] = {name: (target.name, name) for name in target.open}
    key: str
    origin: Origin
    for key, origin in project.spellings(catalog, target, project.OPEN):
        defined: tuple[project.Module, str] | None = project.definition(catalog.modules, origin, project.OPEN)
        if defined is not None and not defined[0].installed:
            found[key] = (defined[0].name, defined[1])
    return found


def own_parameters(catalog: project.Index, path: Path) -> Seeds:
    """Find what every call passes the unannotated parameters of the file at `path`'s functions.

    Returns:
      Each function's parameters' types, by name (see `with_parameters`).

    """
    target: project.Module | None = (
        catalog.modules.get(project.module_name(path)) if path.suffix == SUFFIX else None
    )
    return {} if target is None else target.parameters


def with_parameters(catalog: project.Index, found: Mapping[str, Seeds]) -> project.Index:
    """Record what every call passes checked modules' functions' unannotated parameters (by module name).

    Returns:
      The index, with them.

    """
    modules: dict[str, project.Module] = dict(catalog.modules)
    name: str
    for name in found.keys() & modules.keys():
        modules[name] = modules[name]._replace(parameters=found[name])
    return project.Index(modules, catalog.names)
