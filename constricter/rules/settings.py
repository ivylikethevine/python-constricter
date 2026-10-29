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
from constricter.fix.values.tables import Tables
from constricter.offences import (
    STARRED_SUBSCRIPTS,
    Checks,
)
from constricter.rules import late, widened
from constricter.rules.calls import keyed, marked
from constricter.rules.scoped import Seeded, Settings
from constricter.source.annotations import free_of, free_of_all
from constricter.source.declarations import (
    GenericClass,
    awaited_returns,
    casts,
    class_attributes,
    defaulted_type_vars,
    defined_type_vars,
    descriptors,
    factories,
    generic_members,
    self_returns,
)
from constricter.source.decorators import passing
from constricter.source.flow import Hierarchy
from constricter.source.syntax import (
    owners,
    python2_compatible,
)
from constricter.source.walked import of_type

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
    seen: Outside = outside or Outside()  # its defaults, where the CLI knows nothing of the module
    origins: dict[str, str] = stdlib.origins(tree)
    stored.hand(tree, seen.emptied)
    # The functions' declared returns: other checked files' (see `Outside`), then the module's own.
    calls: dict[str, str] = {**seen.calls, **own.returns, **own.side_calls}
    imported: Classes | None = seen.classes
    # The bases whose members are known whole: the standard library's, and other checked files' below.
    bases: dict[str, str] = stdlib.bases(tree, origins)
    beyond: Mapping[str, inherited.Beyond] = seen.beyond
    library: dict[str, inherited.Library] = {
        text: (stdlib.members(path), stdlib.lines(path))
        for text, path in (*bases.items(), *((end, end) for end in inherited.several(beyond)))
        if path
    }
    # The file's own types that mention a type variable it imports (`--fix` sees only its own).
    free: frozenset[str] = seen.type_vars
    selfish: dict[str, frozenset[str]] = self_returns(tree)
    # The generic classes it names, as it spells them: other checked files', then its own.
    generic: dict[str, GenericClass] = {**seen.generic, **generic_members(tree, free)}
    return Settings(
        checks._replace(type_comments=checks.type_comments or python2_compatible(tree)),
        lines,
        Known(
            free_of(calls, free),
            factories(tree) | seen.values,
            {**(imported.attributes if imported else {}), **free_of_all(own.classes, free)},
            {**(imported.methods if imported else {}), **free_of_all(own.methods, free)},
            Indirect(
                {**seen.awaits, **free_of(awaited_returns(tree), free)},
                _partial(own, free, outside),
                {**seen.tuples, **free_of(own.tuples, free)},
                {**seen.unions, **own.unions},
                {**seen.takers, **fills.takers(tree)},
            ),
            ClassSide(
                free_of_all(own.order.flattened(class_attributes(tree)), free),
                free_of_all(own.sides, free),
                inherited.lineage(
                    tree,
                    selfish,
                    # A base whose line the index followed is in sight too, another package's included,
                    # and a generic class given its arguments (`Result[Row]`), whose members bind them.
                    frozenset(bases).union(
                        imported.methods if imported else (),
                        beyond,
                        _given(tree, generic),
                    ),
                    beyond,
                    library,
                ),
                classvars.variables(tree, classvars.imported(tree), outside, checks.plain_bases),
                classvars.own_plain(tree, classvars.imported(tree), outside, checks.plain_bases),
            ),
            LibraryNames(
                casts(tree),
                origins,
                # What annotations alone can name: its own imports for type checking, and other files' types'.
                replace(
                    imports.plan(tree),
                    guarded={**seen.checking, **seen.guarded},
                    factories=seen.factories,
                ),
                seen.overloaded,
                seen.installed_classes,
                seen.installed_parameters,
                seen.installed_lineage,
                seen.installed_aliases,
                checks.min_python is not None and checks.min_python >= STARRED_SUBSCRIPTS,
                checks.min_python is None or checks.min_python >= TYPING_ALIAS,
            ),
            Limits(checks.max_length, checks.vague, widened.marks(lines)),
            vouched=passing(tree, defined_type_vars(tree)).union(seen.vouched),
            generic=generic,
            descriptors={**seen.descriptors, **descriptors(tree)},
        ),
        Hierarchy.for_module(
            tree,
            {name: frozenset(wider) for name, wider in checks.narrower},
            seen.same,
        ),
        owners(tree, says_self),
        tuple(
            sorted(
                (node.lineno, node.col_offset)
                for node in cast("list[ast.NamedExpr]", of_type(tree, ast.NamedExpr))
            ),
        ),
        seen.hints,
        facts(
            tree,
            selfish,
            stdlib.generics(origins) | seen.generics,
            {
                **seen.managers,
                **{name: (yielded, frozenset[str]()) for name, yielded in entered.managers(tree).items()},
            },
            (defined_type_vars(tree) | free, defaulted_type_vars(tree) | seen.defaulted),
        )._replace(
            untyped=seen.untyped,
            attributed=frozenset(
                node.value.id
                for node in cast("list[ast.Attribute]", of_type(tree, ast.Attribute))
                if isinstance(node.value, ast.Name)
            ),
            positional=callables.signatures(tree),
            excused=late.excusing(lines),
        ),
        Seeded(
            keyed(tree, seen.parameters),
            seen.fixtures,
            marked=marked(tree),
            reads=reads.members(tree, imported, seen.same, seen.read_members),
            named=seen.named,
        ),
    )


def _given(tree: ast.Module, generic: Mapping[str, GenericClass]) -> frozenset[str]:
    """Name the module's classes' bases that are a generic class given its arguments (`Result[Row]`).

    Returns:
      Each, as written.

    """
    return frozenset(
        ast.unparse(base)
        for node in cast("list[ast.ClassDef]", of_type(tree, ast.ClassDef))
        for base in node.bases
        if isinstance(base, ast.Subscript) and ast.unparse(base.value) in generic
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
