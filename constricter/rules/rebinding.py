# SPDX-License-Identifier: MIT
"""A first binding's fix, refitted to every value the name is bound to later, as a checker holds it to.

`x = 1` then `x = None` declares `x: int | None` before the first binding (annotated there, mypy
wouldn't narrow it to the `int` it's bound to), and `total = 0` then `total += 0.5` declares a
`float`; another type that doesn't fit (`x = 1` then `x = "a"`, a class and its base) leaves it
untyped: a union is better left to the author. A `Self` takes only `Self`. A later binding whose
type isn't known may be anything, and one whose type is a guess may be wrong: either makes the fix
a guess.
"""

from typing import Final, NamedTuple

from constricter.fix.known import Inference
from constricter.offences import Edit, Fix, Offence
from constricter.rules.flow import Binding, Hierarchy, members

_NONE: Final = "None"
_ONLY_NONE: Final = frozenset({_NONE})
_OPTIONAL: Final = "optional"  # the fix kind of a `None` added to a type
REBOUND: Final = "rebound"  # the fix kind (and guessing mechanism) of a later binding's type
# The types a later binding may widen a first one's to: the numeric tower's (`int`, then `float`).
_NUMBERS: Final = frozenset({"bool", "int", "float", "complex"})


class Refit(NamedTuple):
    """A fix refitted: its inference, what it rests on if a guess, whether it is one, and its edit."""

    found: Inference
    origins: frozenset[str]
    unsafe: bool
    edit: Edit
    span: tuple[int, int]


class _Later(NamedTuple):
    """What a name's later bindings say: the types that don't fit its fix, their guesses, any unknown."""

    misfits: frozenset[str]
    origins: frozenset[str]  # what the later bindings' guessed types rest on
    unknown: bool


def refit(
    o: Offence,
    fix: Fix,
    rest: list[Binding],
    hierarchy: Hierarchy,
    self_type: str | None,
) -> Refit | Fix | None:
    """Refit `o`'s `fix` to the name's `rest` of bindings (see the module docstring).

    `self_type`: how the module spells `Self`, if it imports it.

    Returns:
      `fix` itself, if it takes them all as it is; else its refit, to offer; or `None`, for no fix.

    """
    # `--fix`'s annotations are always readable; one that weren't would be its own one member.
    declared: frozenset[str] = members(fix.annotation) or frozenset({fix.annotation})
    later: _Later = _later(rest, declared, hierarchy)
    if (later.misfits or later.unknown) and self_type in declared:
        return None
    if not (later.misfits or later.unknown or later.origins):
        return fix
    rebound: frozenset[str] = frozenset({REBOUND}) if later.unknown else frozenset()
    kinds: frozenset[str] = fix.kinds | later.origins | rebound
    origins: frozenset[str] = later.origins | rebound | (fix.kinds if fix.unsafe else frozenset[str]())
    unsafe: bool = fix.unsafe or later.unknown or bool(later.origins)
    if not later.misfits:
        return Refit(Inference(fix.annotation, fix.reason, kinds), origins, unsafe, fix.edit, fix.span)
    atoms: frozenset[str] = declared | later.misfits
    widest: str | None
    if (widest := _widest(atoms - {_NONE}, hierarchy)) is None:
        return None
    return Refit(
        Inference(
            widest + (" | None" if _NONE in atoms else ""),
            f"{fix.reason}, and every value it's bound to later",
            kinds | {_OPTIONAL if later.misfits == _ONLY_NONE else REBOUND},
        ),
        origins,
        unsafe,
        Edit.DECLARE,
        fix.span if fix.edit is Edit.DECLARE else (o.line, o.col),
    )


def _later(rest: list[Binding], declared: frozenset[str], hierarchy: Hierarchy) -> _Later:
    """Read what the later bindings of a name declared as the union `declared` say.

    Returns:
      Their types that don't fit it, what their guesses rest on, and whether any is unknown.

    """
    misfits: set[str] = set()
    origins: frozenset[str] = frozenset()
    unknown: bool = False
    binding: Binding
    for binding in rest:
        text: str | None = binding.value or (None if binding.guess is None else binding.guess[0])
        found: frozenset[str] | None
        if text is None or (found := members(text)) is None:
            unknown = True
            continue
        if binding.value is None and binding.guess is not None:
            origins |= binding.guess[1]
        misfits.update(atom for atom in found if not _fits(atom, declared, hierarchy))
    return _Later(frozenset(misfits), origins, unknown)


def _fits(atom: str, declared: frozenset[str], hierarchy: Hierarchy) -> bool:
    """Check whether a value of type `atom` fits a name declared as the union `declared`.

    As value flow's `Hierarchy.fits` has it, but a generic only fits the same text: an annotation that
    says `list[int]` doesn't take a `list[str]`.

    Returns:
      Whether it does.

    """
    return any(atom == member or member in hierarchy.wider(atom) for member in declared)


def _widest(atoms: frozenset[str], hierarchy: Hierarchy) -> str | None:
    """Find the one type all of `atoms` fit: itself, if it's one; else the widest, if they're numbers.

    Not a class's base (`Base` for `Base` and `Sub`): a checker may see only one of them bound (the
    other, say, under `if not TYPE_CHECKING:`), and narrow to it.

    Returns:
      It, or `None`.

    """
    if len(atoms) == 1:
        return next(iter(atoms))
    widest: list[str] = [
        atom for atom in atoms if all(_fits(other, frozenset({atom}), hierarchy) for other in atoms)
    ]
    return widest[0] if widest and atoms <= _NUMBERS else None
