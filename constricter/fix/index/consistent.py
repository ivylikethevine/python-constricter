"""Names the checked files annotate alike, for the parameters that leave them bare.

A parameter's name says much of what it holds (`request`, `df`): one the checked files' functions
annotate a parameter by at least `AGREED` times, every time the same type (by what each
annotation's names refer to, through re-exports), is taken for that type where a function leaves it
unannotated with no default. A guess (`named`): nothing ties one function's `df` to another's.
"""

import ast
import builtins
from collections import Counter
from collections.abc import Mapping
from pathlib import Path
from typing import Final, TypeAlias

from constricter.fix.core.known import Guarded, Origin, Passed
from constricter.fix.index import project
from constricter.fix.index.modules import SUFFIX, Index, Module
from constricter.rules.annotations import roots

KIND: Final = "named"  # the guessing mechanism (`FIX_KINDS`)
AGREED: Final = 3  # the fewest annotations of a name, all alike, that type it
_BUILTINS: Final = frozenset(dir(builtins))
_DOT: Final = "."
# What an annotation says nothing by: a parameter so typed is as vague as one left bare.
_VAGUE: Final = frozenset({"typing.Any", "typing_extensions.Any", "builtins.object", "builtins.None"})
_Written: TypeAlias = list[tuple[Module, str]]  # a name's annotations, each with its module


def agreed(catalog: Index) -> Mapping[str, tuple[str, str]]:
    """Find each name the checked files annotate alike, at least `AGREED` times, that one leaves bare.

    Returns:
      Each one's commonest spelling, and the first module by name that writes it.

    """
    if catalog.memo is not None and catalog.memo.named is not None:
        return catalog.memo.named
    checked: list[Module] = [
        module
        for name, module in sorted(catalog.modules.items())
        if not module.installed and name not in catalog.repeated
    ]
    wanted: frozenset[str] = frozenset[str]().union(*(module.bare for module in checked))
    written: dict[str, _Written] = {}
    module: Module
    for module in checked:
        name: str
        for name in module.annotated.keys() & wanted:
            written.setdefault(name, []).extend((module, text) for text in module.annotated[name])
    found: dict[str, tuple[str, str]] = {}
    texts: _Written
    for name, texts in written.items():
        if len(texts) >= AGREED and _alike(catalog.modules, texts):
            found[name] = _commonest(texts)
    if catalog.memo is not None:
        catalog.memo.named = found
    return found


def _commonest(texts: _Written) -> tuple[str, str]:
    """Pick the spelling of a type most of its annotations write, the first module's of a tie.

    Returns:
      Its module's name, and it.

    """
    text: str = Counter(text for _, text in texts).most_common(1)[0][0]
    return next((module.name, each) for module, each in texts if each == text)


def _alike(modules: Mapping[str, Module], texts: _Written) -> bool:
    """Check whether annotations, each in its module, are all of one type that says something.

    Returns:
      Whether they are.

    """
    first: str | None = _meaning(modules, *texts[0])
    return (
        first is not None
        and first not in _VAGUE
        and all(_meaning(modules, module, text) == first for module, text in texts[1:])
    )


def _meaning(modules: Mapping[str, Module], module: Module, annotation: str) -> str | None:
    """Write an annotation by what its names refer to in `module`: `pandas.DataFrame` for `pd.DataFrame`.

    Returns:
      It, or `None` where a name refers to nothing the module binds at its top level.

    """
    renamed: dict[str, str] = {}
    root: str
    for root in roots(annotation):
        origin: Origin | None = (
            module.names.get(root)
            or module.guarded.get(root)
            or (("builtins", root) if root in _BUILTINS else None)
        )
        if origin is None:
            return None
        origin = project.canonical_origin(modules, origin)
        renamed[root] = origin[0] if origin[1] is None else f"{origin[0]}{_DOT}{origin[1]}"
    tree: ast.expr = ast.parse(annotation, mode="eval").body
    node: ast.AST
    for node in ast.walk(tree):
        if isinstance(node, ast.Name):
            node.id = renamed.get(node.id, node.id)
    return ast.unparse(tree)


def visible(catalog: Index, path: Path, guarded: dict[str, Guarded]) -> dict[str, Passed]:
    """Type the parameters the file at `path` leaves bare by their names, as it can write each type.

    `guarded` records the names those types need imported for type checking (see `project.spelled_in`).

    Returns:
      Each such name's type, and what it rests on; nothing for a file `catalog` doesn't have.

    """
    target: Module | None = catalog.modules.get(project.module_name(path)) if path.suffix == SUFFIX else None
    if target is None or target.name in catalog.repeated:  # another file's module, maybe
        return {}
    named: Mapping[str, tuple[str, str]] = agreed(catalog)
    found: dict[str, Passed] = {}
    name: str
    for name in sorted(named.keys() & target.bare):
        defined: str
        annotation: str
        defined, annotation = named[name]
        written: str | None = project.spelled_in(
            catalog,
            target,
            catalog.modules[defined],
            annotation,
            guarded,
        )
        if written is not None:
            found[name] = (written, frozenset({KIND}))
    return found
