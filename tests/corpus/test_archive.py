"""Tests for the run folders as later runs read them (`tests.corpus.archive`)."""

import json
from pathlib import Path

from tests.corpus import archive
from tests.corpus.pipeline import Record, Store


def test_a_run_is_read_from_its_report_or_else_its_records(tmp_path: Path) -> None:
    """Its report's records by corpus directory, version and step; a run with none, its own files'."""
    stopped: Store = Store(tmp_path / "stopped")
    stopped.write("standard library", "dev", "check", {"seconds": 1.0})
    _ = stopped.path("standard library", "dev", "census").write_text("{", encoding="utf-8")  # half written
    reported: Path = tmp_path / "reported"
    reported.mkdir()
    nested: Record = {"standard library": {"dev": {"check": {"seconds": 2.0}}}}
    _ = (reported / archive.REPORT).write_text(json.dumps({"records": nested}), encoding="utf-8")
    (tmp_path / "empty").mkdir()
    assert sorted(each.name for each in archive.runs(tmp_path)) == ["reported", "stopped"]
    assert not archive.runs(tmp_path / "none")
    assert archive.kept(stopped.root) == {("standard-library", "dev", "check"): {"seconds": 1.0}}
    assert archive.kept(reported) == {("standard-library", "dev", "check"): {"seconds": 2.0}}


def test_a_runs_listings_are_one_file_each(tmp_path: Path) -> None:
    """Each corpus's lines in the run's order, with its corpus and version; none where no corpus has one."""
    store: Store = Store(tmp_path)
    corpora: list[tuple[str, str]] = [("pandas", "dev"), ("standard library", "dev")]
    seen: dict[str, list[Record]] = {
        "pandas": [{"path": "a.py", "seen": ["int"]}],
        "standard library": [{"path": str(Path(archive.__file__).resolve().parents[2] / "b.py"), "seen": []}],
    }
    corpus: str
    lines: list[Record]
    for corpus, lines in seen.items():
        path: Path = store.path(corpus, "dev", "traced", ".seen.jsonl")
        path.parent.mkdir(parents=True, exist_ok=True)
        _ = path.write_text("".join(f"{json.dumps(line)}\n" for line in lines), encoding="utf-8")
    assert archive.gather(tmp_path, corpora) == [tmp_path / "traced.seen.jsonl"]
    written: list[Record] = [
        json.loads(line) for line in (tmp_path / "traced.seen.jsonl").read_text(encoding="utf-8").splitlines()
    ]
    assert [(each["corpus"], each["constricter"]) for each in written] == corpora
    assert written == [
        {"corpus": "pandas", "constricter": "dev", "path": "a.py", "seen": ["int"]},
        {"corpus": "standard library", "constricter": "dev", "path": "b.py", "seen": []},  # relative
    ]
    assert not archive.gather(tmp_path / "none", corpora)
