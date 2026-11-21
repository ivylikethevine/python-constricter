"""Set each hinted step's measured peak beside the runner's estimate for an unmeasured one.

For every `infer-CHECKER` step a run folder's records measured: the corpus's Python bytes, the bytes
of what it imports from its environment (`hinted_memory.imported`), the CPUs it was given, the most memory
its process tree held, the corpus's `check` step's (constricter's own check, no servers), what
`hinted_memory.HINTED_SIZES` estimates the step holds with as many servers as the CPUs given (up to the
checker's most), and how many of its rounds read their hints from the store (a round read there
starts no server, so only `[0, N]` rows measure the servers). Corpora not on disk are left out.

    local/.venv/bin/python scripts/scratch/hinted_sizes.py FOLDER > local/runs/hinted-sizes.md

Reads the checkouts under `local/corpus-suites/` and `local/corpus-sources/`; writes nothing. Its
rows of `mega-11-11-2026-1113` and `alt-fresh-11-20-2026-1800` are what `HINTED_SIZES` was fitted
to; a few seconds a run on 16CPU/60GB.
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[2]))

from constricter.cli.lsp.protocol import SERVERS, Server  # noqa: E402
from tests.corpus import catalog, corpus_sources, corpus_suite, trees  # noqa: E402
from tests.corpus.hinted_memory import HINTED_SIZES, imported  # noqa: E402
from tests.corpus.sizing import GIB, _size  # noqa: E402  # pylint: disable=protected-access

_INFER = "infer-"


def _root(entry: catalog.Entry) -> Path | None:
    if entry.suite is not None:
        return corpus_suite.WORK / f"{entry.name}-{entry.suite.tag}" / entry.suite.source
    if entry.source is not None:
        return corpus_sources.unpacked(entry.name, entry.source) / entry.source.package
    return None


def _used(path: Path) -> dict[str, object]:
    if not path.is_file():
        return {}
    used: object = json.loads(path.read_text(encoding="utf-8")).get("used", {})
    return used if isinstance(used, dict) else {}


def main(argv: list[str]) -> int:
    records: Path = Path(argv[0]) / "records"
    known: catalog.Catalog = catalog.load()
    print(
        "| Corpus | Step | Source (MB) | Imported (MB) | CPUs given | Held (GB) | Check (GB) | Estimate (GB) "
        "| Rounds from the store |"
    )
    print("| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |")
    for corpus in sorted(each.name for each in records.iterdir()):
        try:
            entry: catalog.Entry = known.entry(corpus)
        except KeyError:
            continue
        root: Path | None = _root(entry)
        if root is None or not root.is_dir():
            continue
        size: int = _size(root)
        outside: int = imported(root, trees.found(entry, settle=False).environment)
        for kept in sorted(records.glob(f"{corpus}/*/{_INFER}*.json")):
            checker: str = kept.stem.removeprefix(_INFER)
            if checker not in SERVERS:
                continue
            used: dict[str, object] = _used(kept)
            given: object = used.get("given", {})
            cpus: int = int(given.get("cpus", 0)) if isinstance(given, dict) else 0
            held: float = float(str(used.get("memory", 0.0)))
            check: float = float(str(_used(kept.parent / "check.json").get("memory", 0.0)))
            server: Server = SERVERS[checker]
            count: int = max(1, min(cpus, server.most))
            estimate: int = HINTED_SIZES[checker].held(count, size, outside, whole=server.whole)
            stored: object = json.loads(kept.read_text(encoding="utf-8")).get("stored", {})
            read: object = stored.get(checker, [0, 0]) if isinstance(stored, dict) else [0, 0]
            print(
                f"| {corpus} | {checker} | {size / 1e6:.1f} | {outside / 1e6:.1f} | {cpus} | {held:.2f} | "
                f"{check:.2f} | {estimate / GIB:.2f} | {read} |"
            )
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
