# SPDX-License-Identifier: MIT
"""The corpus catalog: its sets, the tiers and groups they make, and where a corpus comes from."""

import tomllib
from pathlib import Path
from typing import Final, TypeAlias, cast

import pytest

from tests.corpus import __main__ as runner
from tests.corpus import catalog, corpus_sources, trees
from tests.corpus.corpus_sources import Source
from tests.corpus.run_config import Run

_GROUPS: Final = ("fast-small", "fast-large", "slow-small", "slow-large")  # by size and time
_PIN: Final = "=="  # a `corpus` group entry pinned to one version
_Group: TypeAlias = list[str | dict[str, str]]  # a dependency group: pins, and the groups it includes


def test_the_catalog_expands_sets_and_refuses_a_name_it_hasnt() -> None:
    """A set stands for its corpora, each named once, in order."""
    known: catalog.Catalog = catalog.load()
    assert known.names(["pydantic", catalog.ORIGINAL])[:2] == ["pydantic", "standard library"]
    assert len(known.names([catalog.ORIGINAL, "pip"])) == len(known.sets[catalog.ORIGINAL])
    assert all(name in known.entries for name in known.sets[catalog.ORIGINAL])
    here: catalog.Entry = known.entry(str(Path(__file__).parent))
    assert (here.name, here.suite, known.names([here.path])) == ("corpus", None, [here.path])
    assert known.entry("pip") is known.entries["pip"]
    with pytest.raises(ValueError, match="'numpy' is no directory, and no corpus or set"):
        _ = known.names(["numpy"])


def test_the_tiers_hold_each_other_and_the_groups_split_every_corpus() -> None:
    """`original` within `super` within `mega`, every corpus; each corpus in one group of size and time."""
    known: catalog.Catalog = catalog.load()
    original: list[str] = known.names([catalog.ORIGINAL])
    fast: list[str] = known.names([catalog.SUPER])
    every: list[str] = known.names([catalog.MEGA])
    assert set(original) < set(fast) < set(every) == set(known.entries)
    grouped: list[str] = known.names(list(_GROUPS))
    assert sorted(grouped) == sorted(known.entries)
    assert sum(len(known.names([group])) for group in _GROUPS) == len(grouped)
    assert known.names([catalog.SUPER], [catalog.ORIGINAL]) == [name for name in fast if name not in original]


def test_a_set_that_names_itself_is_refused() -> None:
    """Through another set as well as directly."""
    looped: catalog.Catalog = catalog.Catalog({}, {"a": ["b"], "b": ["a"]})
    with pytest.raises(ValueError, match="names itself, by a > b > a"):
        _ = looped.names(["a"])


def test_a_command_leaves_out_a_corpus_a_set_or_a_run_files(tmp_path: Path) -> None:
    """`--minus NAME`, or `--minus RUN.toml`: that run's corpora."""
    assert runner.commanded(Run(), ["--minus", catalog.ORIGINAL]).minus == (catalog.ORIGINAL,)
    less: Path = tmp_path / "less.toml"
    _ = less.write_text('[corpora]\ninclude = ["pip", "twisted"]\n', encoding="utf-8")
    run: Run = runner.commanded(Run(include=(catalog.SUPER,)), ["--minus", str(less)])
    assert run.minus == ("pip", "twisted")
    known: catalog.Catalog = catalog.load()
    left: list[str] = [name for name in known.names([catalog.SUPER]) if name not in run.minus]
    assert known.names(list(run.include), list(run.minus)) == left
    assert len(left) == len(known.names([catalog.SUPER])) - len(run.minus)


def test_the_standard_library_is_cpythons_source(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Its `Lib`, fetched as an sdist is: not the running Python's, which may lack its tests."""
    entry: catalog.Entry = catalog.load().entry("standard library")
    source: Source = cast("Source", entry.source)
    assert source.url == f"https://www.python.org/ftp/python/{entry.version}/Python-{entry.version}.tar.xz"
    assert source.package == f"Python-{entry.version}/Lib"
    fetched: list[str] = []

    def fetch(name: str, *, sources: dict[str, Source]) -> Path:
        fetched.append(name)
        return tmp_path / sources[name].package

    monkeypatch.setattr(corpus_sources, "fetch", fetch)
    tree: trees.Tree = trees.found(entry)
    assert (tree.root, tree.version, tree.base, fetched) == (
        tmp_path / source.package,
        "3.14.7",
        None,
        [entry.name],
    )
    assert corpus_sources.pinned()["pip"].url.startswith(corpus_sources.FILES)


def test_an_installed_corpus_is_the_version_the_corpus_group_pins() -> None:
    """`pyproject.toml`'s `corpus` group and the catalog name one version of each, the suite's tag too."""
    project: dict[str, dict[str, _Group]] = tomllib.loads(
        (Path(__file__).parents[2] / "pyproject.toml").read_text(encoding="utf-8"),
    )
    pinned: dict[str, str] = dict(
        cast("tuple[str, str]", tuple(each.split(_PIN)))
        for each in project["dependency-groups"]["corpus"]
        if isinstance(each, str) and _PIN in each
    )
    known: catalog.Catalog = catalog.load()
    checked: dict[str, str] = {name: pin for name, pin in pinned.items() if name in known.entries}
    assert set(checked) == {"django", "pandas", "pydantic", "sqlalchemy"}
    assert {name: known.entries[name].version for name in checked} == checked
    tags: dict[str, str] = {name: cast("catalog.Suite", known.entries[name].suite).tag for name in checked}
    assert {
        name: tag.removeprefix("rel_").removeprefix("v").replace("_", ".") for name, tag in tags.items()
    } == checked
