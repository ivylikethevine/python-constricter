"""Tests for the run folders as later runs read them (`tests.corpus.archive`)."""

import gzip
import json
from datetime import datetime
from pathlib import Path

from tests.corpus import archive
from tests.corpus.pipeline import Record, Store
from tests.corpus.run_config import REPORT, started


def test_a_run_is_read_from_its_report_or_else_its_records(tmp_path: Path) -> None:
    """Its report's records by corpus directory, version and step; a run with none, its own files'."""
    stopped: Store = Store(tmp_path / "stopped")
    stopped.write("standard library", "dev", "check", {"seconds": 1.0})
    _ = stopped.path("standard library", "dev", "census").write_text("{", encoding="utf-8")  # half written
    reported: Path = tmp_path / "reported"
    reported.mkdir()
    nested: Record = {"standard library": {"dev": {"check": {"seconds": 2.0}}}}
    _ = (reported / REPORT).write_text(json.dumps({"records": nested}), encoding="utf-8")
    (tmp_path / "empty").mkdir()
    assert sorted(each.name for each in archive.runs(tmp_path)) == ["reported", "stopped"]
    assert not archive.runs(tmp_path / "none")
    assert archive.kept(stopped.root) == {("standard-library", "dev", "check"): {"seconds": 1.0}}
    assert archive.kept(reported) == {("standard-library", "dev", "check"): {"seconds": 2.0}}


def test_a_runs_listings_are_one_file(tmp_path: Path) -> None:
    """The guesses, then each listing's lines a corpus at a time, each with its listing, corpus, version."""
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
    guessed: list[Record] = [{"package": "pandas", "kinds": "call"}]
    assert archive.gather(tmp_path, corpora, guessed) == [tmp_path / archive.LISTED]
    assert [
        json.loads(line)["listing"]
        for line in gzip.decompress((tmp_path / archive.LISTED).read_bytes()).splitlines()
    ] == [
        "guesses",
        "seen",
        "seen",
    ]
    assert archive.listed(tmp_path, "guesses") == guessed
    assert archive.listed(tmp_path, "seen") == [
        {"corpus": "pandas", "constricter": "dev", "path": "a.py", "seen": ["int"]},
        {"corpus": "standard library", "constricter": "dev", "path": "b.py", "seen": []},  # relative
    ]
    assert not archive.listed(tmp_path, "verdicts")
    assert not archive.gather(tmp_path / "none", corpora)
    assert not archive.listed(tmp_path / "none", "seen")


def test_a_run_with_its_report_alone_started_when_its_report_says(tmp_path: Path) -> None:
    """Its facts are its report's once `facts.toml` isn't kept."""
    facts: Record = {"run": {"started": "2026-10-20T08:00:00-07:00"}}
    _ = (tmp_path / REPORT).write_text(json.dumps(facts), encoding="utf-8")
    assert started(tmp_path) == datetime.fromisoformat("2026-10-20T08:00:00-07:00")
