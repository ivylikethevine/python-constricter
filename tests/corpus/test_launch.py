"""A fix's copy of a corpus: the checkers `--infer-with` starts read the copy's settings and environment."""

import os
import shlex
import venv
from pathlib import Path
from types import SimpleNamespace
from typing import Final

import pytest

from constricter.cli.lsp import protocol
from tests.corpus import catalog, checker_settings, corpus_suite, launch
from tests.corpus.run_config import CHECKERS, DEV
from tests.corpus.trees import Tree

_PYREFLY: Final = "pyrefly.toml"
_PYRIGHT: Final = "pyrightconfig.json"
_TY: Final = "ty.toml"
_EVERY: Final = [_PYRIGHT, _PYREFLY, _TY]
_PROJECT: Final = "pyproject.toml"
_WINDOWS: Final = "nt"  # `os.name`'s
_OWN: Final = "[rules]\n"  # a checkout's own settings for ty
_EMPTY: Final = "{}\n"  # an empty `pyrightconfig.json`
# Settings above a copy, as this project's are above a run's: each checker sent to another environment.
_ABOVE: Final = """\
[tool.pyrefly]
python-interpreter-path = "elsewhere/bin/python"

[tool.ty.environment]
python = "elsewhere"
"""
_ABOVE_PYRIGHT: Final = '{"venvPath": ".", "venv": "elsewhere"}\n'
# A package only the copy's environment has, and a call of it no fix types without a checker's hint.
_PACKAGE: Final = "class Thing:\n    pass\n\n\ndef make() -> Thing:\n    return Thing()\n"
_CALLING: Final = (
    "import onlythere\n\n\ndef made():\n    thing = (lambda: onlythere.make())()\n    return thing\n"
)
_HINTED: Final = "+    thing: onlythere.Thing = (lambda: onlythere.make())()\n"


@pytest.mark.parametrize(
    ("project", "written"),
    [
        (None, _EVERY),
        ("[tool.mypy]\nstrict = true\n", _EVERY),
        ('[tool.pyright]\ntypeCheckingMode = "basic"\n\n[tool.ty.rules]\n', [_PYREFLY]),
        ("[tool.basedpyright]\n\n[tool.pyrefly]\n", [_TY]),
        ("[tool\n", _EVERY),
        ("tool = 1\n", _EVERY),
    ],
    ids=[
        "none",
        "another tool's",
        "Pyright's and ty's",
        "basedpyright's and pyrefly's",
        "unparsed",
        "no table",
    ],
)
def test_a_checker_with_no_settings_of_its_own_is_given_empty_ones(
    tmp_path: Path,
    project: str | None,
    written: list[str],
) -> None:
    """By the `pyproject.toml`'s tables, a table under a tool's too; once: its own file is left as it is."""
    if project is not None:
        _ = (tmp_path / _PROJECT).write_text(project, encoding="utf-8")
    assert checker_settings.own(tmp_path) == written
    assert [(tmp_path / name).read_text(encoding="utf-8") for name in written if name != _PYRIGHT] == [
        "" for name in written if name != _PYRIGHT
    ]
    assert not checker_settings.own(tmp_path)


def test_a_copy_keeps_its_checkouts_settings_and_is_given_the_rest(tmp_path: Path) -> None:
    """A checkout's files are copied as they are; an sdist's copy, which has none, is given every one."""
    checkout: Path = tmp_path / "checkout"
    (checkout / "pkg").mkdir(parents=True)
    _ = (checkout / "pkg" / "__init__.py").write_text("", encoding="utf-8")
    _ = (checkout / _PROJECT).write_text("[tool.pyright]\n", encoding="utf-8")
    _ = (checkout / _TY).write_text(_OWN, encoding="utf-8")
    where: launch.Place = launch.copied(Tree("pkg", "1", checkout / "pkg", checkout), tmp_path / "copy")[0]
    assert sorted(path.name for path in where.cwd.iterdir()) == ["pkg", _PROJECT, _PYREFLY, _TY]
    assert (where.cwd / _TY).read_text(encoding="utf-8") == _OWN
    where = launch.copied(Tree("pkg", "1", checkout / "pkg"), tmp_path / "sdist")[0]
    assert sorted(path.name for path in where.cwd.iterdir()) == ["pkg", *sorted(_EVERY)]
    assert (where.cwd / _PYRIGHT).read_text(encoding="utf-8") == _EMPTY


def test_a_runs_path_starts_with_its_environments_python_alone(tmp_path: Path) -> None:
    """Then this Python's directory, where the checkers are: not the environment's own, with its tools."""
    place: launch.Place = launch.Place(tmp_path, tmp_path / "pkg", tmp_path / "env")
    tools: str = str(Path(launch.python(DEV)).parent)
    assert launch.environment(place)["PATH"].split(os.pathsep)[0] == tools  # no Python there: not installed
    python: Path = tmp_path / "env" / "bin" / "python"
    python.parent.mkdir(parents=True)
    _ = python.write_text("", encoding="utf-8")
    _ = (python.parent / "ty").write_text("", encoding="utf-8")
    first: str
    second: str
    first, second = launch.environment(place)["PATH"].split(os.pathsep)[:2]
    assert second == tools
    assert sorted(path.name for path in Path(first).iterdir()) == ["python", "python3"]
    assert f"exec {shlex.quote(str(python))} " in (Path(first) / "python3").read_text(encoding="utf-8")
    assert launch.environment(place)["PATH"].split(os.pathsep)[0] == first  # as it is: not written again
    assert launch.environment(place._replace(environment=None))["PATH"].split(os.pathsep)[0] == tools


def test_a_corpus_with_no_checkout_is_given_an_environment_once(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A venv, then what it requires; again only when that changes, or a command failed."""
    ran: list[list[str]] = []
    status: list[int] = [0]

    def completed(args: list[str], cwd: Path) -> SimpleNamespace:
        ran.append(args[1:])
        (cwd / ".venv").mkdir(exist_ok=True)
        return SimpleNamespace(returncode=status[0], stdout="", stderr="no such package")

    monkeypatch.setattr(corpus_suite, "_completed", completed)
    assert corpus_suite.own_environment(tmp_path, ()) == tmp_path / ".venv"
    assert ran == [list(catalog.VENV)]
    assert corpus_suite.own_environment(tmp_path, ()) == tmp_path / ".venv"
    assert len(ran) == 1
    _ = corpus_suite.own_environment(tmp_path, ("pkg==1", "other"))
    assert ran[1:] == [list(catalog.VENV), ["pip", "install", "-q", "pkg==1", "other"]]
    status[0] = 1
    with pytest.raises(RuntimeError, match="no such package"):
        _ = corpus_suite.own_environment(tmp_path, ("pkg==2",))
    status[0] = 0
    _ = corpus_suite.own_environment(tmp_path, ("pkg==2",))
    assert ran[-1] == ["pip", "install", "-q", "pkg==2"]


@pytest.mark.skipif(os.name == _WINDOWS, reason="a suite's environment is laid out as POSIX's")
@pytest.mark.parametrize("checker", CHECKERS)
def test_a_checker_in_a_copy_reads_its_settings_and_its_environments_packages(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    checker: str,
) -> None:
    """The real thing, under a project whose settings name another environment, as a run's copy is.

    The hint is of a type only the copy's environment holds: a checker reading the settings above,
    or asking the Python first on this process's path, doesn't know it.
    """
    if not protocol.runs(checker):
        pytest.skip(f"{checker} isn't installed")
    above: Path = tmp_path / "above"
    checkout: Path = above / "checkout"
    (checkout / "pkg").mkdir(parents=True)
    _ = (above / _PROJECT).write_text(_ABOVE, encoding="utf-8")
    _ = (above / _PYRIGHT).write_text(_ABOVE_PYRIGHT, encoding="utf-8")
    _ = (checkout / _PROJECT).write_text("[tool.mypy]\nstrict = true\n", encoding="utf-8")
    _ = (checkout / "pkg" / "calling.py").write_text(_CALLING, encoding="utf-8")
    venv.create(above / "elsewhere", symlinks=True)
    venv.create(checkout / ".venv", symlinks=True)
    package: Path = next((checkout / ".venv" / "lib").glob("*/site-packages")) / "onlythere"
    package.mkdir(parents=True)
    _ = (package / "__init__.py").write_text(_PACKAGE, encoding="utf-8")
    monkeypatch.setenv("XDG_CACHE_HOME", str(tmp_path / "cache"))
    tree: Tree = Tree("pkg", "1", checkout / "pkg", checkout, checkout / ".venv")
    where: launch.Place = launch.copied(tree, above / "copy")[0]
    ran: launch.Ran = launch.run(DEV, where, ["--diff", "--unsafe-fixes", f"--infer-with={checker}"], 1)
    assert _HINTED in ran.output, ran.errors
