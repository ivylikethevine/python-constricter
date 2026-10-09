# SPDX-License-Identifier: MIT
"""A checked file's classes' methods defined with `@overload`, for the calls their arguments decide.

On a receiver typed as the class, as the calling file spells it: read and written as its functions'
overloads are (see `constricter.fix.index.own_overloads`), each under `Class.method`.
"""

from pathlib import Path
from typing import TYPE_CHECKING, Final

from constricter.fix.core.known import Guarded
from constricter.fix.core.signatures import ReadSignature
from constricter.fix.index import own_overloads, project, stubbed
from constricter.fix.index.modules import SUFFIX, Index, Module, module_name
from constricter.rules.annotations import roots

if TYPE_CHECKING:
    from constricter.fix.index.declared import Signature

_SELF: Final = "Self"


def overloaded(
    catalog: Index,
    path: Path,
    guarded: dict[str, Guarded],
) -> dict[str, tuple[ReadSignature, ...]]:
    """Find the overloaded methods the file at `path` calls, of the checked files' classes it names.

    `guarded` records the names their returns need imported for type checking.

    Returns:
      Each one's signatures, by the class as the file writes it and the method (`Frame.get`); none
      for a file `catalog` doesn't have.

    """
    target: Module | None
    if path.suffix != SUFFIX or (target := catalog.modules.get(module_name(path))) is None:
        return {}
    found: dict[str, tuple[ReadSignature, ...]] = {}
    key: str
    defined: tuple[Module, str]
    named: dict[str, tuple[Module, str]] = {
        **dict(project.spelled_classes(catalog, target, (target.names, target.attributes), set())),
        **{name: (target, name) for name in target.bases},  # its own
    }
    for key, defined in named.items():
        name: str
        for name in sorted(target.method_calls):
            entry: str = f"{defined[1]}.{name}"
            written: tuple[Signature, ...] = (
                () if defined[0].installed else defined[0].overloads.get(entry, ())
            )
            # One returning `Self` is its receiver's class: not the type the signature writes; one
            # declaring its `self` is for some receivers alone.
            if not written or any(
                each.self_type is not None or _SELF in roots(each.returns or _SELF) for each in written
            ):
                continue
            found[f"{key}.{name}"] = own_overloads.spelled(
                catalog,
                target,
                (defined[0], entry),
                stubbed.read_signatures(catalog.modules, defined[0], entry),
                guarded,
            )
    return {entry: read for entry, read in found.items() if read}
