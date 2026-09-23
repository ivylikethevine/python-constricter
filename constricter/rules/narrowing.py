# SPDX-License-Identifier: MIT
"""Value flow's findings (LVA008, LVA009, LVA010) as offences, with LVA008's and LVA010's narrowing fixes."""

from constricter.offences import NARROW, Edit, Fix, FixPolicy, Offence
from constricter.rules.flow import Finding, Kind


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
