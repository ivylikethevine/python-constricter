"""`--fix` for calls into a checked tree's stub with no source beside it: a compiled module's."""

import sys
import textwrap
from pathlib import Path
from typing import Final

import pytest

from constricter.cli import command as cli
from constricter.fix.index import project
from constricter.fix.index.stubs import installed, lone

# A package with a compiled module's stub, a stub-only subpackage, a module with its own stub, and
# a top-level stub beside it.
TREE: Final = {
    "pkg/__init__.py": "",
    "pkg/_fast.pyi": """
        class Grid: ...

        def count(items: list[int]) -> int: ...
        def grid() -> Grid: ...
    """,
    "pkg/ext/__init__.pyi": "from pkg.ext.inner import deep as deep\n",
    "pkg/ext/inner.pyi": "def deep() -> bytes: ...\n",
    "pkg/both.py": "def both():\n    return 1\n",
    "pkg/both.pyi": "def both() -> int: ...\n",
    "pkg/core.py": """
        import top
        from pkg import _fast, ext
        from pkg._fast import count

        from . import _fast as quick


        def run():
            a = _fast.count([1])
            b = count([])
            c = quick.grid()
            d = ext.deep()
            e = top.high()
            return a, b, c, d, e
    """,
    "top.pyi": "def high() -> float: ...\n",
}
FIXED: Final = (
    "    a: int = _fast.count([1])\n",
    "    b: int = count([])\n",
    "    c: _fast.Grid = quick.grid()\n",  # its class, through a name the file imports the module by
    "    d: bytes = ext.deep()\n",  # a stub-only subpackage's, through what it re-exports
    "    e: float = top.high()\n",  # a top-level stub's, beside the package
)


def _tree(root: Path, files: dict[str, str]) -> Path:
    name: str
    text: str
    for name, text in files.items():
        path: Path = root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        _ = path.write_text(textwrap.dedent(text), encoding="utf-8", newline="\n")
    return root


def test_calls_into_a_checked_trees_lone_stub_are_typed(tmp_path: Path) -> None:
    """By its declared returns, as an installed package's stub types them; the stub is left as it was."""
    root: Path = _tree(tmp_path / "project", TREE)
    assert cli.main(["--fix", "-q", str(root)]) == cli.EXIT_CLEAN  # every binding fixed
    fixed: str = (root / "pkg" / "core.py").read_text(encoding="utf-8")
    assert all(line in fixed for line in FIXED), fixed
    assert all(
        (root / name).read_text(encoding="utf-8") == textwrap.dedent(text)
        for name, text in TREE.items()
        if name.endswith(".pyi")
    )


def test_the_trees_stub_comes_before_an_installed_one(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The package installed too, at another version: the checked tree's stub is the one read."""
    site: Path = _tree(
        tmp_path / "site",
        {
            "pkg/py.typed": "",
            "pkg/__init__.py": "",
            "pkg/_fast.pyi": "def count(items: list[int]) -> str: ...\n",
        },
    )
    monkeypatch.setattr(sys, "path", [str(site), *sys.path])
    root: Path = _tree(tmp_path / "project", TREE)
    assert cli.main(["--fix", "-q", str(root)]) == cli.EXIT_CLEAN  # every binding fixed
    assert FIXED[0] in (root / "pkg" / "core.py").read_text(encoding="utf-8")


def test_a_lone_stub_is_found_under_the_checked_package_above_it(tmp_path: Path) -> None:
    """Under the nearest checked module above it, a package; never beside a source, or under a module."""
    root: Path = _tree(
        tmp_path / "project",
        {
            **TREE,
            "pkg/left/__init__.py": "",  # a package the check leaves out: its stub isn't alone
            "pkg/left/__init__.pyi": "",
            "bare/only.py": "",  # no package: a top-level module, its folder a root
            "bare/beside.pyi": "",
        },
    )
    paths: list[Path] = [root / "pkg" / "__init__.py", root / "pkg" / "core.py", root / "bare" / "only.py"]
    catalog: project.Index = project.index(paths)
    tops: tuple[Path, ...] = lone.roots(catalog.modules)
    assert tops == (root.resolve(), (root / "bare").resolve())

    def within(name: str) -> Path | None:
        return lone.within(catalog.modules, tops, name)

    assert within("pkg._fast") == root.resolve() / "pkg" / "_fast.pyi"
    assert within("pkg.ext") == root.resolve() / "pkg" / "ext" / "__init__.pyi"
    assert within("pkg.ext.inner") == root.resolve() / "pkg" / "ext" / "inner.pyi"
    assert within("top") == root.resolve() / "top.pyi"
    assert within("beside") == root.resolve() / "bare" / "beside.pyi"
    assert within("pkg.both") is None  # its own stub: `both.py` is beside it
    assert within("pkg.left") is None
    assert within("pkg.core.run") is None  # under a module: a name of it
    assert within("pkg.missing") is None
    assert within("nowhere.at.all") is None
    with_stubs: project.Index = installed.with_installed(catalog, ())
    assert with_stubs.modules["pkg._fast"].installed
    again: tuple[Path, ...] = lone.roots(with_stubs.modules)  # a stub read has no folder: it's no root
    assert again == tops
    assert lone.within(with_stubs.modules, again, "pkg._fast.count") is None  # under a stub read: its name
