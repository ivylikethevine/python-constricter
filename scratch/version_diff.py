"""Compare two versions' findings and fixes in one corpus run, corpus by corpus.

    python3 scratch/version_diff.py local/corpus-runs/FOLDER [A B]

A and B are two of the run's recorded versions (`records/<corpus>/<version>/`); by default its
first two, as `tests/corpus/runs/compiled.toml` names them: `<label>+dev` and `compiled`. For each
corpus both measured, it compares the check's offences per code and per level and its files, and
each fix step's fixes (`<step>.fixes.jsonl`: each binding's annotation and tier) and broken files;
then their timed checks' seconds in one process and with every worker, and instructions, where both
have them. Prints a line for each corpus that differs, with its first difference, and a summary;
exits 1 if any differs.
"""

import json
import statistics
import sys
from pathlib import Path


def _record(folder: Path, name: str) -> dict[str, object]:
    path = folder / f"{name}.json"
    return json.loads(path.read_text()) if path.exists() else {}


def _fixes(folder: Path, step: str) -> set[tuple[str, int, str, str, str]]:
    path = folder / f"{step}.fixes.jsonl"
    found: set[tuple[str, int, str, str, str]] = set()
    for line in path.read_text().splitlines() if path.exists() else ():
        each = json.loads(line)
        found.add((each["path"], each["line"], each["name"], each["annotation"], each["tier"]))
    return found


def _differs(one: Path, other: Path) -> str | None:
    """Find the first way two versions' records of one corpus differ.

    Returns:
      It, said; `None` where they agree.
    """
    a, b = _record(one, "check"), _record(other, "check")
    for key in ("files", "codes", "levels"):
        if a.get(key) != b.get(key):
            return f"check: {key} differ ({a.get(key)!r:.80} against {b.get(key)!r:.80})"
    steps = sorted({path.name.removesuffix(".fixes.jsonl") for path in one.glob("*.fixes.jsonl")})
    for step in steps:
        left, right = _fixes(one, step), _fixes(other, step)
        if left != right:
            only = sorted(left - right)[:1] or sorted(right - left)[:1]
            return f"{step}: {len(left ^ right)} fixes differ, first {only[0]}"
        for key in ("fixed", "broken", "left"):
            if _record(one, step).get(key) != _record(other, step).get(key):
                return f"{step}: {key} differs"
    return None


_TIMED = ("median one", "median every", "median one instructions")  # in `timing.json`: what's compared


def _timed(folder: Path) -> dict[str, float]:
    record = _record(folder, "timing")
    return {key: float(record[key]) for key in _TIMED if isinstance(record.get(key), (int, float))}


def main() -> int:
    """Compare, print, and say whether anything differs.

    Returns:
      1 if a corpus differs, else 0.
    """
    run = Path(sys.argv[1])
    corpora = sorted(path for path in (run / "records").iterdir() if path.is_dir())
    versions = sys.argv[2:4] or sorted({version.name for corpus in corpora for version in corpus.iterdir()})[:2]
    if len(versions) < 2:
        print(f"{run.name} has fewer than two versions: {versions}")
        return 1
    print(f"{run.name}: {versions[0]} against {versions[1]}")
    differing = 0
    ratios: dict[str, list[float]] = {key: [] for key in _TIMED}
    for corpus in corpora:
        one, other = corpus / versions[0], corpus / versions[1]
        if not (one.is_dir() and other.is_dir()):
            continue
        if (said := _differs(one, other)) is not None:
            differing += 1
            print(f"  {corpus.name}: {said}")
        a, b = _timed(one), _timed(other)
        for key in a.keys() & b.keys():
            if b[key]:
                ratios[key].append(a[key] / b[key])
    compared = sum((corpus / versions[0]).is_dir() and (corpus / versions[1]).is_dir() for corpus in corpora)
    print(f"{compared - differing} of {compared} corpora the same")
    for key, each in ratios.items():
        if each:
            print(f"{versions[1]}: {statistics.median(each):.2f} times as fast by {key!r}, the median of {len(each)} corpora")
    return int(bool(differing))


if __name__ == "__main__":
    sys.exit(main())
