# SPDX-License-Identifier: MIT
"""What a module is checked with (`Settings`): its options, and what `--fix` knows of it.

Its own tables (`Tables`) joined with what other checked files say of it (`Outside`): functions'
returns, classes' members and lines of bases, the standard library's classes it takes from, what a
type checker sees otherwise (`facts`), and its parameters' types given from outside. A type the
module's own code writes with a type variable it imports is left out: `--fix` sees only its own.
"""

import ast
from collections.abc import Mapping, Sequence
from dataclasses import replace
from typing import Final, cast

from constricter.fix.core import imports, inherited
from constricter.fix.core.known import (
    Classes,
    ClassSide,
    Indirect,
    Known,
    LibraryNames,
    Limits,
    Outside,
    Partial,
)
from constricter.fix.libraries import stdlib
from constricter.fix.values import callables, classvars, entered, fills, reads, stored
from constricter.fix.values.doubts import facts, says_self
from constricter.offences import (
    STARRED_SUBSCRIPTS,
    Checks,
)
from constricter.rules import late, widened
from constricter.rules.annotations import free_of, free_of_all
from constricter.rules.calls import keyed, marked
from constricter.rules.declarations import (
    awaited_returns,
    casts,
    class_attributes,
    defined_type_vars,
    factories,
    self_returns,
)
from constricter.rules.decorators import passing
from constricter.rules.flow import Hierarchy
from constricter.rules.scoped import Seeded, Settings
from constricter.rules.syntax import (
    owners,
    python2_compatible,
)
from constricter.rules.tables import Tables
from constricter.rules.walked import of_type

TYPING_ALIAS: Final = (3, 10)  # the first Python whose `typing` has `TypeAlias`


def module_settings(
    tree: ast.Module,
    checks: Checks,
    lines: Sequence[str],
    own: Tables,
    outside: Outside | None = None,
) -> Settings:
    """Work out what the module `tree` is checked with (see the module docstring).

    `checks`: its options; `lines`: its source lines; `own`: its own tables; `outside`: what the CLI
    knows of it from the other checked files, if it's one of them.

    Returns:
      Its settings.

    """
    stored.hand(tree, {} if outside is None else outside.emptied)
    # The functions' declared returns: other checked files' (see `Outside`), then the module's own.
    calls: dict[str, str] = {**({} if outside is None else outside.calls), **own.returns, **own.side_calls}
    imported: Classes | None = None if outside is None else outside.classes
    # The bases whose members are known whole: the standard library's, and other checked files' below.
    bases: dict[str, str] = stdlib.bases(tree, stdlib.origins(tree))
    beyond: Mapping[str, inherited.Beyond] = {} if outside is None else outside.beyond
    library: dict[str, inherited.Library] = {
        text: (stdlib.members(path), stdlib.lines(path))
        for text, path in (*bases.items(), *((end, end) for end in inherited.several(beyond)))
        if path
    }
    # The file's own types that mention a type variable it imports (`--fix` sees only its own).
    free: frozenset[str] = frozenset() if outside is None else outside.type_vars
    selfish: dict[str, frozenset[str]] = self_returns(tree)
    return Settings(
        checks._replace(type_comments=checks.type_comments or python2_compatible(tree)),
        lines,
        Known(
            free_of(calls, free),
            factories(tree) | (frozenset[str]() if outside is None else outside.values),
            {**(imported.attributes if imported else {}), **free_of_all(own.classes, free)},
            {**(imported.methods if imported else {}), **free_of_all(own.methods, free)},
            Indirect(
                {**({} if outside is None else outside.awaits), **free_of(awaited_returns(tree), free)},
                _partial(own, free, outside),
                {**({} if outside is None else outside.tuples), **free_of(own.tuples, free)},
                {**({} if outside is None else outside.unions), **own.unions},
                {**({} if outside is None else outside.takers), **fills.takers(tree)},
            ),
            ClassSide(
                free_of_all(own.order.flattened(class_attributes(tree)), free),
                free_of_all(own.sides, free),
                inherited.lineage(
                    tree,
                    selfish,
                    # A base whose line the index followed is in sight too, another package's included.
                    frozenset(bases).union(imported.methods if imported else (), beyond),
                    beyond,
                    library,
                ),
                classvars.variables(tree, classvars.imported(tree), outside, checks.plain_bases),
                classvars.own_plain(tree, classvars.imported(tree), outside, checks.plain_bases),
            ),
            LibraryNames(
                casts(tree),
                stdlib.origins(tree),
                # What annotations alone can name: its own imports for type checking, and other files' types'.
                replace(
                    imports.plan(tree),
                    guarded={} if outside is None else {**outside.checking, **outside.guarded},
                ),
                {} if outside is None else outside.overloaded,
                frozenset() if outside is None else outside.installed_classes,
                {} if outside is None else outside.installed_parameters,
                {} if outside is None else outside.installed_lineage,
                {} if outside is None else outside.installed_aliases,
                checks.min_python is not None and checks.min_python >= STARRED_SUBSCRIPTS,
                checks.min_python is None or checks.min_python >= TYPING_ALIAS,
            ),
            Limits(checks.max_length, checks.vague, widened.marks(lines)),
            vouched=passing(tree, defined_type_vars(tree)).union(
                frozenset() if outside is None else outside.vouched,
            ),
        ),
        Hierarchy.for_module(
            tree,
            {name: frozenset(wider) for name, wider in checks.narrower},
            () if outside is None else outside.same,
        ),
        owners(tree, says_self),
        tuple(
            sorted(
                (node.lineno, node.col_offset)
                for node in cast("list[ast.NamedExpr]", of_type(tree, ast.NamedExpr))
            ),
        ),
        () if outside is None else outside.hints,
        facts(
            tree,
            selfish,
            stdlib.generics(stdlib.origins(tree)) | (outside.generics if outside else frozenset[str]()),
            {
                **({} if outside is None else outside.managers),
                **{name: (yielded, frozenset[str]()) for name, yielded in entered.managers(tree).items()},
            },
            defined_type_vars(tree) | free,
        )._replace(
            untyped=frozenset() if outside is None else outside.untyped,
            attributed=frozenset(
                node.value.id
                for node in cast("list[ast.Attribute]", of_type(tree, ast.Attribute))
                if isinstance(node.value, ast.Name)
            ),
            positional=callables.signatures(tree),
            excused=late.excusing(lines),
        ),
        Seeded(
            keyed(tree, {} if outside is None else outside.parameters),
            {} if outside is None else outside.fixtures,
            marked=marked(tree),
            reads=reads.members(tree, imported, () if outside is None else outside.same),
            named={} if outside is None else outside.named,
        ),
    )


def _partial(own: Tables, free: frozenset[str], outside: Outside | None) -> Partial:
    """Gather the returns only an unpacking can use: other checked files', then the module's own.

    Returns:
      Them, less the module's that mention a type variable it imports (`free`).

    """
    given: Partial = Partial() if outside is None else outside.partial
    return Partial(
        {**given.calls, **free_of(own.partial, free)},
        {**given.methods, **free_of_all(own.partial_methods, free)},
    )
