"""Why `--fix` offers no type for a call: the reason `--format=json` gives an offence it can't fix.

The corpus census reads it (`unfixed`), so what each roadmap item could reach is counted in one run
rather than sized from rows by hand. Only a call has one (`f()`, `x.m()`, `await` of either): any
other value's shape already says why (see `tests/corpus/untyped_shapes.py`).
"""

import ast
from collections.abc import Mapping
from typing import Final

from constricter.fix.core.known import ImportPlan, Inference, Known
from constricter.fix.values.inference import inference
from constricter.fix.values.members import fits
from constricter.source.annotations import dotted

# Each reason, by its stable id, and what it means (docs/FIXES.md lists them).
REASONS: Final[dict[str, str]] = {
    "vague": "a type it knows, vaguer than `vague` allows (`Any`, `dict[str, Any]`)",
    "declined": "a type it knows, not offered: a type checker may see the value otherwise",
    "receiver": "a method of a receiver of no known type",
    "member": "a method its receiver's known class has no declared type for",
    "untyped": "a function of the module's or another checked file's that declares no return",
    "library": "a standard-library function or builtin whose arguments don't decide its type",
    "imported": "a function or class imported from outside the checked files and the standard library",
    "local": "a local name or parameter of no known type, called",
    "other": "anything else: a call of a call, of a subscript, of a lambda",
}
_VAGUE: Final = "vague"
_DECLINED: Final = "declined"
_RECEIVER: Final = "receiver"
_MEMBER: Final = "member"
_UNTYPED: Final = "untyped"
_LIBRARY: Final = "library"
_IMPORTED: Final = "imported"
_LOCAL: Final = "local"
_OTHER: Final = "other"


def refused(value: ast.expr, known: Known, types: Mapping[str, str], untyped: frozenset[str]) -> str:
    """Say why a call bound with no fix has none (see `REASONS`).

    `types`: what the scope's names are typed as; `untyped`: the other checked files' functions the
    module calls that declare no return, as it spells them (see `Facts.untyped`).

    Returns:
      The reason's id; `""` for a value that isn't a call.

    """
    call: ast.expr = value.value if isinstance(value, ast.Await) else value
    if not isinstance(call, ast.Call):
        return ""
    found: Inference | None
    if (found := inference(value, known, types)) is not None:
        return _DECLINED if fits(found.annotation, known.limits.vague) else _VAGUE
    func: ast.expr = call.func
    callee: str | None = dotted(func)
    plan: ImportPlan | None = known.names.plan
    root: str = "" if callee is None else callee.split(".", 1)[0]
    imported: bool = root in known.names.stdlib or (plan is not None and root in plan.bound)
    if isinstance(func, ast.Attribute) and not (imported and root not in types):
        return _MEMBER if inference(func.value, known, types) is not None else _RECEIVER
    return _OTHER if callee is None else _callee(callee, known, (types, untyped))


def _callee(callee: str, known: Known, scope: tuple[Mapping[str, str], frozenset[str]]) -> str:
    """Say why a call of a name, or of a module's function (`os.path.join`), has no fix.

    `scope`: what its names are typed as, and the checked files' functions declaring no return.

    Returns:
      The reason's id.

    """
    root: str = callee.split(".", 1)[0]
    plan: ImportPlan | None = known.names.plan
    defined: bool = plan is not None and root in plan.defined and root not in plan.bound
    reason: str
    if callee in scope[1] or defined:
        reason = _UNTYPED
    elif root in known.names.stdlib or (known.is_builtin(root) and root not in scope[0]):
        reason = _LIBRARY
    elif plan is not None and root in plan.bound:
        reason = _IMPORTED
    else:
        reason = _LOCAL
    return reason
