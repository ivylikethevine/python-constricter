"""Set each hinted step's measured peak beside its checker's servers' estimate for the corpus's files.

For every `infer-CHECKER` step a run folder's records measured: the corpus's Python bytes, the CPUs
it was given, the most memory its process tree held, the corpus's `check` step's (constricter's own
check, no servers), and what `protocol.SERVERS` estimates one server and as many servers as the CPUs
given (up to the checker's most) take for those bytes. Corpora not on disk are left out.

    local/.venv/bin/python scripts/scratch/hinted_sizes.py FOLDER

Reads the checkouts under `local/corpus-suites/`; writes nothing.
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[2]))

from constricter.cli.lsp.protocol import SERVERS, Server  # noqa: E402
from tests.corpus import catalog, corpus_sources, corpus_suite  # noqa: E402
from tests.corpus.sizing import GIB, _held, _size  # noqa: E402  # pylint: disable=protected-access

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
        "| Corpus | Step | Source (MB) | CPUs given | Held (GB) | Check (GB) | One server (GB) | Servers (GB) |"
    )
    print("| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |")
    for corpus in sorted(each.name for each in records.iterdir()):
        try:
            entry: catalog.Entry = known.entry(corpus)
        except KeyError:
            continue
        root: Path | None = _root(entry)
        if root is None or not root.is_dir():
            continue
        size: int = _size(root)
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
            print(
                f"| {corpus} | {checker} | {size / 1e6:.1f} | {cpus} | {held:.2f} | {check:.2f} | "
                f"{_held(server, 1, size) / GIB:.2f} | {_held(server, count, size) / GIB:.2f} |"
            )
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
