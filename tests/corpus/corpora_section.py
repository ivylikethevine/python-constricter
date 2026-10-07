# SPDX-License-Identifier: MIT
"""A super corpora run's section of docs/RUNS.md: its tables, and what a fix broke.

`tests/corpus/super_corpora.py` runs the steps (`tests/corpus/corpora_steps.py`'s); this writes what
they gave as Markdown, laid out as Prettier does, and puts it in the file before the versions'
sections, which `corpus_table.record` rewrites.
"""

import platform
import re
import textwrap
from collections import Counter
from collections.abc import Sequence
from pathlib import Path
from typing import Final, NamedTuple, cast

from tests.corpus import corpus_suite, corpus_table
from tests.corpus.corpora_steps import (
    CENSUS,
    CHECK,
    INFER,
    NONE,
    TABLE,
    TESTS,
    TYPES,
    Census,
    Checked,
    Inferred,
    Sizes,
    Step,
    Steps,
    Tested,
    Typechecked,
    Unset,
    Value,
    checkers,
)
from tests.corpus.corpus_table import DEV, Measured

RUNS: Final = Path(__file__).resolve().parents[2] / "docs" / "RUNS.md"
_VERSIONS: Final = "\n## constricter "  # `corpus_table.record`'s sections, which a run's goes before
_SECTION: Final = "\n## "
_MODEL: Final = re.compile(r"^model name\s*:\s*(.+)$", re.MULTILINE)
_TOP_SHAPES: Final = 20
_TOP_KINDS: Final = 30
_TOP_TRACED: Final = 8  # the mechanisms named for a fixed run's new type errors
_PROSE_WIDTH: Final = 100  # .prettierrc.yaml's printWidth
_WORD: Final = re.compile(r"(?:`[^`]*`|[^\s`])+")  # what Prettier keeps on one line
_FAILED: Final = "failed"
_MECHANISMS_NOTE: Final = (
    "Fixes per mechanism (`--format=json`'s `kinds`), certain / guessed: a fix resting on several "
    "counts for each."
)
_CENSUS_NOTE: Final = (
    "Untyped bindings (`corpus_untyped`): those `--fix` offers only a guess for, those it offers "
    "nothing for, and the commonest shapes of the values with no fix:"
)
_SUITES_NOTE: Final = (
    "Each package's own tests and type checks, as released and after fixing its source "
    "(`corpus_suite.py`): the tests' outcome, and the type errors a fixed run has that the "
    "released one hasn't, by the mechanisms of the fixes they're traced to:"
)
_HINTS_NOTE: Final = (
    "`--fix --unsafe-fixes --infer-with` each checker, on a copy: what it fixed (and how many "
    "more than without the hints), the typed share after, and the files it broke:"
)
_TIMINGS_NOTE: Final = (
    "Seconds per step (and the CPUs its processes kept busy, on average), side by side; then the check "
    "at `suffocate` alone with every CPU: its seconds, per file, the main process's CPU seconds (and "
    "their share of the check's), and the second round's, of a profiled check:"
)


class Described(NamedTuple):
    """What a section says of its run: its heading and first words, the checkout's stamp, and its sizes."""

    heading: str
    intro: str
    stamp: str
    sized: Sizes
    minutes: float | None  # how long the whole run took; `None` for one that resumed another


def _machine(run: Described) -> str:
    """Describe the checkout, the machine and how it sized the run.

    Returns:
      A few sentences.

    """
    try:
        model: re.Match[str] | None = _MODEL.search(Path("/proc/cpuinfo").read_text(encoding="utf-8"))
    except OSError:
        model = None
    processor: str = model[1] if model else platform.processor() or platform.machine()
    sized: Sizes = run.sized
    memory: str = "" if sized.memory is None else f", {sized.memory / 2**30:.0f} GB"
    took: str = "" if run.minutes is None else f" The run took {run.minutes:.0f} minutes."
    return (
        f"constricter {corpus_table.label(DEV)} (`{run.stamp}`), Python {platform.python_version()}, on "
        f"{processor} ({sized.cpus} CPUs{memory}, {platform.system()}): `--jobs={sized.jobs}`, "
        f"{sized.workers} workers a suite, each step started once the CPUs it keeps busy are free, then "
        f"each corpus's timed check alone with every CPU.{took} Timings don't compare across machines."
    )


def _value(found: Steps, name: str) -> Value | None:
    step: Step | None = found.get(name)
    return None if step is None else step.value


def _seconds(found: Steps, name: str) -> str:
    step: Step | None
    if (step := found.get(name)) is None:
        return NONE
    if step.value is None:
        return _FAILED
    busy: str = f" ({step.cpu / step.seconds:.1f})" if step.cpu and step.seconds else ""
    return f"{step.seconds:,.0f}{busy}"


def _mechanisms(names: Sequence[str], found: dict[str, Steps]) -> list[str]:
    """Tabulate the fixes per mechanism: certain ones and guesses, per corpus.

    Returns:
      The table's lines.

    """
    checked: dict[str, Checked] = {
        name: cast("Checked", _value(found[name], CHECK)) for name in names if _value(found[name], CHECK)
    }
    total: Counter[str] = Counter()
    each: Checked
    for each in checked.values():
        total.update(each.certain)
        total.update(each.guesses)
    rows: list[list[str]] = [["Mechanism", *checked, "Certain", "Guessed"]]
    kind: str
    for kind, _ in total.most_common(_TOP_KINDS):
        rows.append(
            [
                f"`{kind}`",
                *(f"{one.certain[kind]:,} / {one.guesses[kind]:,}" for one in checked.values()),
                f"{sum(one.certain[kind] for one in checked.values()):,}",
                f"{sum(one.guesses[kind] for one in checked.values()):,}",
            ],
        )
    return corpus_table.table(rows, right=1)


def _censuses(names: Sequence[str], found: dict[str, Steps]) -> list[str]:
    """Tabulate the census: each corpus's untyped bindings, then the unfixed ones' commonest shapes.

    Returns:
      The two tables' lines.

    """
    taken: dict[str, Census] = {
        name: cast("Census", _value(found[name], CENSUS)) for name in names if _value(found[name], CENSUS)
    }
    first: list[list[str]] = [["Corpus", "Untyped", "Only a guess", "No fix", "In files that don't parse"]]
    name: str
    one: Census
    for name, one in taken.items():
        first.append(
            [
                name,
                f"{one.untyped:,}",
                f"{one.guessed:,}",
                f"{one.unfixed:,} ({one.unfixed / max(one.untyped, 1):.1%})",
                f"{one.unparsed:,}",
            ],
        )
    shapes: Counter[str] = Counter()
    for one in taken.values():
        shapes.update(one.shapes)
    second: list[list[str]] = [["No fix: the value's shape", *taken, "Total"]]
    shape: str
    count: int
    for shape, count in shapes.most_common(_TOP_SHAPES):
        second.append([shape, *(f"{one.shapes[shape]:,}" for one in taken.values()), f"{count:,}"])
    return [*corpus_table.table(first, right=1), "", *corpus_table.table(second, right=1)]


def _counts(outcome: corpus_suite.Outcome) -> str:
    if corpus_suite.stopped(outcome):
        return "stopped: it ran too long"
    return ", ".join(f"{count:,} {kind}" for kind, count in outcome.counts.items()) or "nothing ran"


def _after(released: corpus_suite.Outcome, outcome: corpus_suite.Outcome, change: str) -> str:
    verdict: str = "the same" if outcome == released else f"DIFFERENT: {_counts(outcome)}"
    return f"{verdict} ({change})"


def _tested(found: Steps) -> Tested | None:
    value: Value | None = _value(found, TESTS)
    return value if isinstance(value, Tested) else None


def _typechecked(found: Steps) -> Typechecked | None:
    value: Value | None = _value(found, TYPES)
    return value if isinstance(value, Typechecked) else None


def _listed(start: str, items: Sequence[str]) -> list[str]:
    """Lay a list item's comma-separated `items` out after `start`, as Prettier fills a paragraph.

    Broken at any space but one in a code span, the lines after the first indented under the item.

    Returns:
      The lines.

    """
    lines: list[str] = [start]
    word: str
    for word in cast("list[str]", _WORD.findall(", ".join(items))):
        if len(lines[-1]) + 1 + len(word) > _PROSE_WIDTH:
            lines.append(f"  {word}")
        else:
            lines[-1] = f"{lines[-1]} {word}"
    return lines


def _unset(names: Sequence[str], found: dict[str, Steps]) -> list[str]:
    """List the suites that couldn't be set up, each with why.

    Returns:
      A line for each.

    """
    lines: list[str] = []
    name: str
    for name in names:
        step: str
        for step in (TESTS, TYPES):
            value: Value | None = _value(found[name], step)
            if isinstance(value, Unset):
                said: str = f"- {name}: its `{step}` couldn't be set up ({value.reason})"
                lines += textwrap.wrap(said, _PROSE_WIDTH, subsequent_indent="  ", break_on_hyphens=False)
    return lines


def _suites(names: Sequence[str], found: dict[str, Steps]) -> list[str]:
    """Tabulate the packages' own tests and type checks, as released and after each fix.

    Returns:
      The two tables' lines, and each new type error's mechanism counts.

    """
    tests: list[list[str]] = [["Package", "Tag", "Released", "After `--fix`", "After `--fix --unsafe-fixes`"]]
    types: list[list[str]] = []
    traced: list[str] = []
    name: str
    for name in names:
        tested: Tested | None
        if (tested := _tested(found[name])) is not None:
            tests.append(
                [
                    name,
                    tested.tag,
                    _counts(tested.released) + (" (run twice)" if tested.again else ""),
                    *(_after(tested.released, outcome, change) for _, change, outcome, _ in tested.fixed),
                    *([NONE] * (len(corpus_suite.MODES) - len(tested.fixed))),
                ],
            )
        checked: Typechecked | None
        if (checked := _typechecked(found[name])) is not None:
            if not types:
                types.append(
                    ["Package", "Checks", "Released errors", *(f"New: `{m}`" for m, _ in checked.fixed)],
                )
            types.append(
                [
                    name,
                    f"`{checked.checks}`",
                    f"{checked.released:,}",
                    *(f"{len(compared.new):,}" for _, compared in checked.fixed),
                ],
            )
            label: str
            compared: corpus_suite.Compared
            for label, compared in checked.fixed:
                kinds: Counter[str]
                if kinds := Counter(blamed.kind for blamed in compared.new):
                    listed: list[str] = [
                        f"`{kind}` {count}" for kind, count in kinds.most_common(_TOP_TRACED)
                    ]
                    more: int = len(compared.new) - sum(count for _, count in kinds.most_common(_TOP_TRACED))
                    listed += [f"and {more} of other mechanisms"] if more else []
                    traced.extend(_listed(f"- {name}, `{label}`:", listed))
    unset: list[str] = _unset(names, found)
    if len(tests) == 1:
        return ["None of these corpora's suites ran.", "", *unset]
    return [
        *corpus_table.table(tests, right=5),
        "",
        *(corpus_table.table(types, right=2) if types else []),
        "",
        *traced,
        *unset,
    ]


def _hints(names: Sequence[str], found: dict[str, Steps]) -> list[str]:
    """Tabulate `--infer-with` each checker: what it fixed beyond the guesses, and the typed share after.

    Returns:
      The table's lines.

    """
    available: list[str] = checkers()
    rows: list[list[str]] = [
        [
            "Corpus",
            "Fixed and guessed",
            *(part for c in available for part in (f"With `{c}`", "Typed", "Broken")),
        ],
    ]
    name: str
    for name in names:
        base: Measured | None = cast("Measured | None", _value(found[name], TABLE))
        both: int | None = None if base is None or base.fixed is None else base.fixed + (base.guessed or 0)
        row: list[str] = [name, NONE if both is None else f"{both:,}"]
        checker: str
        for checker in available:
            hinted: Inferred | None = cast("Inferred | None", _value(found[name], f"{INFER}{checker}"))
            if hinted is None or hinted.fixed is None:
                row += [_FAILED, NONE, NONE]
                continue
            more: str = "" if both is None else f" ({hinted.fixed - both:+,})"
            share: str = f"{hinted.typed.typed / hinted.typed.total:.1%}" if hinted.typed.total else NONE
            row += [f"{hinted.fixed:,}{more}", share, f"{hinted.broken:,}"]
        rows.append(row)
    return corpus_table.table(rows, right=1)


def _timings(names: Sequence[str], found: dict[str, Steps]) -> list[str]:
    """Tabulate each step's seconds, and the timed check's: per file, its main process, its second round.

    Returns:
      The table's lines.

    """
    beside: list[str] = list(dict.fromkeys(step for name in names for step in found[name] if step != CHECK))
    rows: list[list[str]] = [
        [
            "Corpus",
            "Files",
            *(f"`{step}`" for step in beside),
            "Check",
            "Per file",
            "Main process",
            "Second round",
        ],
    ]
    name: str
    for name in names:
        checked: Checked | None = cast("Checked | None", _value(found[name], CHECK))
        timed: list[str] = [NONE, _FAILED, NONE, NONE, NONE]
        if checked is not None:
            first: float = checked.whole - checked.second
            timed = [
                f"{checked.files:,}",
                f"{checked.seconds:.1f}",
                f"{checked.seconds / max(checked.files, 1) * 1000:.1f} ms",
                f"{checked.main:.1f} ({checked.main / checked.seconds:.0%})",
                f"{checked.second:.1f} ({checked.second / first:.0%} of the first)" if first > 0 else NONE,
            ]
        rows.append([name, timed[0], *(_seconds(found[name], step) for step in beside), *timed[1:]])
    return corpus_table.table(rows, right=1)


def _fill(text: str) -> str:
    return textwrap.fill(text, width=_PROSE_WIDTH)


def section(found: dict[str, Steps], run: Described) -> str:
    """Write the run's section as Markdown.

    Returns:
      It, from its heading on.

    """
    names: list[str] = list(found)
    tabled: list[Measured] = [
        cast("Measured", _value(found[name], TABLE)) for name in names if _value(found[name], TABLE)
    ]
    parts: list[str] = [
        run.heading,
        "",
        _fill(f"{run.intro} {_machine(run)}"),
        "",
        corpus_table.tables(tabled) if tabled else "",
        "",
        _fill(_MECHANISMS_NOTE),
        "",
        *_mechanisms(names, found),
        "",
        _fill(_CENSUS_NOTE),
        "",
        *_censuses(names, found),
        "",
        _fill(_SUITES_NOTE),
        "",
        *_suites(names, found),
        "",
        _fill(_HINTS_NOTE),
        "",
        *_hints(names, found),
        "",
        _fill(_TIMINGS_NOTE),
        "",
        *_timings(names, found),
    ]
    text: str = "\n".join(parts)
    return re.sub(r"\n{3,}", "\n\n", text).rstrip() + "\n"


def record(text: str, heading: str, runs: Path = RUNS) -> None:
    """Write the section into `runs`, in place of the one of its `heading`, before the versions' sections."""
    whole: str = runs.read_text(encoding="utf-8")
    head: str
    versions: str
    rest: str
    head, versions, rest = whole.partition(_VERSIONS)
    after: str = ""
    if heading in head:
        old: str
        head, _, old = head.partition(heading)
        following: int = old.find(_SECTION)
        after = "" if following < 0 else old[following:].strip() + "\n"
    body: str = f"{head.rstrip()}\n\n{text}" + (f"\n{after}" if after else "")
    _ = runs.write_text(f"{body}{versions}{rest}", encoding="utf-8")


def broken(found: dict[str, Steps]) -> list[str]:
    """List what a fix broke, and the steps that failed.

    Returns:
      A line for each.

    """
    lines: list[str] = []
    name: str
    chain: Steps
    for name, chain in found.items():
        lines += [f"{name}: {step} failed" for step, kept in chain.items() if kept.value is None]
        tabled: Measured | None = cast("Measured | None", _value(chain, TABLE))
        if tabled is not None and tabled.broken:
            lines.append(f"{name}: {tabled.broken} files no longer compile")
        if tabled is not None and tabled.left:
            lines.append(f"{name}: a second pass adds {tabled.left} lines")
        tested: Tested | None
        if (tested := _tested(chain)) is not None:
            lines += [
                f"{name}: tests differ after {label}"
                for label, _, outcome, _ in tested.fixed
                if outcome != tested.released
            ]
        checked: Typechecked | None
        if (checked := _typechecked(chain)) is not None:
            lines += [
                f"{name}: {len(compared.new)} new type errors after {label}"
                for label, compared in checked.fixed[: len(corpus_suite.MODES)]
                if compared.new
            ]
    return lines
