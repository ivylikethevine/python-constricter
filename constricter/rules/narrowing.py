# SPDX-License-Identifier: MIT
"""Value flow over a module's scopes, and its findings (LVA008, LVA009, LVA010) as offences with fixes."""

import ast
from collections.abc import Sequence
from functools import lru_cache
from typing import Final

from constricter.offences import NARROW, Edit, Fix, FixPolicy, Offence
from constricter.rules.annotations import node_name
from constricter.rules.flow import Finding, Kind
from constricter.rules.scope import Scope
from constricter.rules.walked import of_type

_TYPE_CHECKING: Final = "TYPE_CHECKING"


def flow_offences(found: list[Finding], policy: FixPolicy) -> list[Offence]:
    """Report value-flow findings as offences, a finding's kind as its code.

    Each declaration LVA008 or LVA010 would narrow gets one fix, a guess (`--unsafe-fixes`: a
    declared type can be wider on purpose): the LVA008 finding's narrowed type if there's one,
    since it's already within the members the values use, else the union without its unused
    members, on the first LVA010 finding. Two rewrites of one annotation can't both apply. `policy`
    decides whether it's offered (`narrow`), and whether it's trusted.

    Returns:
      The offences.

    """
    offences: list[Offence] = []
    fixed: set[tuple[int, int]] = set()
    finding: Finding
    narrowed: set[tuple[int, int]] = {(f.line, f.col) for f in found if f.kind is Kind.NARROWABLE}
    for finding in sorted(found, key=lambda f: f.kind is not Kind.NARROWABLE):
        where: tuple[int, int] = (finding.line, finding.col)
        edit: Fix | None = None
        if (
            finding.span
            and finding.rewrite
            and where not in fixed
            and (finding.kind is Kind.NARROWABLE or where not in narrowed)
        ):
            fixed.add(where)
            reason: str = (
                "the values it's bound to"
                if finding.kind is Kind.NARROWABLE
                else "the members its values use"
            )
            kinds: frozenset[str] = frozenset({NARROW})
            if policy.allows(kinds):
                edit = Fix(
                    finding.rewrite,
                    reason,
                    unsafe=not policy.trusts(kinds),
                    edit=Edit.REPLACE,
                    span=finding.span,
                    kinds=kinds,
                )
        offences.append(Offence(*where, finding.name, finding.kind.value, edit, detail=finding.detail))
    return offences


def module_flow(tree: ast.Module, scopes: Sequence[Scope]) -> list[Finding]:
    """Compare each name's values with its declared type, in each of `scopes`.

    Returns:
      Every finding, in source order.

    """
    escaped: frozenset[str]
    checking_only: frozenset[str]
    escaped, checking_only = module_names(tree)
    return sorted(found for scope in scopes for found in scope.value_flow(escaped, checking_only))


@lru_cache(maxsize=16)  # `module_flow` runs once per round of the checker's `_returned`, on the same tree
def module_names(tree: ast.Module) -> tuple[frozenset[str], frozenset[str]]:
    """Find the names value flow leaves alone in a module.

    Returns:
      Those a `global` or `nonlocal` writes from elsewhere, and those annotated only for type
      checkers (`if TYPE_CHECKING: x: str`), whose runtime values may differ on purpose.

    """
    escaped: set[str] = set()
    checking_only: set[str] = set()
    node: ast.AST
    for node in of_type(tree, ast.Global, ast.Nonlocal, ast.If):
        if isinstance(node, ast.Global | ast.Nonlocal):
            escaped.update(node.names)
        elif isinstance(node, ast.If) and node_name(node.test) == _TYPE_CHECKING:  # the only other kind
            checking_only.update(
                stmt.target.id
                for stmt in node.body
                if isinstance(stmt, ast.AnnAssign) and isinstance(stmt.target, ast.Name)
            )
    return frozenset(escaped), frozenset(checking_only)
