"""Set the memory each constricter step held beside its corpus's source bytes: their ratio, by step.

For each corpus a run folder's records measured and that's on disk, the corpus's Python bytes and
each `check`, `census`, `coverage` and `fix-*` step's most memory held, then by step the ratio's
median, 90th percentile and most, and the corpus that held the most for its bytes. What sizes a
first run's unmeasured step by its files (`sizing.Plan._unmeasured`).

    local/.venv/bin/python scripts/scratch/check_sizes.py FOLDER

Reads the checkouts under `local/corpus-suites/` and the sdists under `local/corpus-sources/`.
"""

import json
import statistics
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[2]))

from tests.corpus import catalog, corpus_sources, corpus_suite  # noqa: E402
from tests.corpus.sizing import GIB, _size  # noqa: E402  # pylint: disable=protected-access

_STEPS = ("check", "census", "coverage", "fix-certain", "fix-likely", "fix-unsafe")
_DECILES = 10


def _root(entry: catalog.Entry) -> Path | None:
    if entry.suite is not None:
        return corpus_suite.WORK / f"{entry.name}-{entry.suite.tag}" / entry.suite.source
    if entry.source is not None:
        return corpus_sources.unpacked(entry.name, entry.source) / entry.source.package
    return None


def main(argv: list[str]) -> int:
    """Print each step's ratios of bytes held to source bytes.

    Returns:
      0.
    """
    records: Path = Path(argv[0]) / "records"
    known: catalog.Catalog = catalog.load()
    ratios: dict[str, list[tuple[float, str, float, float]]] = {step: [] for step in _STEPS}
    for corpus in sorted(each.name for each in records.iterdir()):
        try:
            root: Path | None = _root(known.entry(corpus))
        except KeyError:
            continue
        if root is None or not root.is_dir():
            continue
        size: int = _size(root)
        for step in _STEPS:
            for kept in records.glob(f"{corpus}/*/{step}.json"):
                used: dict[str, float] = json.loads(kept.read_text(encoding="utf-8")).get("used", {})
                held: float = float(used.get("memory", 0.0)) * GIB
                if held and size:
                    ratios[step].append((held / size, corpus, size / 1e6, held / GIB))
    for step, found in ratios.items():
        if not found:
            continue
        values: list[float] = sorted(each[0] for each in found)
        most: tuple[float, str, float, float] = max(found)
        ninth: float = statistics.quantiles(values, n=_DECILES)[-1] if len(values) > 1 else values[0]
        largest: str = ", ".join(
            f"{name} {megabytes:.1f} MB {held:.2f} GB"
            for _, name, megabytes, held in sorted(found, key=lambda each: -each[3])[:_SHOWN]
        )
        print(
            f"{step:12} {len(values):3} corpora  median {statistics.median(values):6.0f}  "
            f"p90 {ninth:6.0f}  most {most[0]:6.0f} ({most[1]}: {most[2]:.1f} MB, {most[3]:.2f} GB)\n"
            f"             held most: {largest}",
        )
    return 0


_SHOWN = 6  # the corpora that held the most, each step


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
