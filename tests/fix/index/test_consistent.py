# SPDX-License-Identifier: MIT
"""`--fix` for a bare parameter by its name: the type the checked files annotate it with everywhere else."""

import ast
import textwrap
from collections.abc import Iterable
from pathlib import Path
from typing import Final

from constricter.cli import command as cli
from constricter.fix.index import annotated, consistent, project
from constricter.fix.index.modules import Index, Module

HTTP: Final = "class Request:\n    def path(self) -> str:\n        return ''\n"
VIEWS: Final = """
from pkg.http import Request


def show(request: Request, n: int) -> None:
    pass


def edit(request: "Request", *, n: int = 0) -> None:
    def inner(request: Request) -> None:
        pass
"""
MORE: Final = """
from pkg import http


def other(request: http.Request, n: str) -> None:
    pass
"""
PLAIN: Final = """
def handle(request, n):
    p = request.path()
    r = request
    m = n


def later(request=None):
    r = request


def again(request):
    request = 1
    r = request


def test_it(request):
    t = request
"""
FIXED: Final = (
    "if TYPE_CHECKING:\n    from pkg.http import Request\n",
    "    p: str = request.path()\n",
    "    r: Request = request\n",
)
CLASH: Final = "from typing import TypeVar as Request\n\n\ndef f(request):\n    pass\n"
UNFIXED: Final = (
    "    m = n\n",  # `int` once and `str` once: no agreement
    "def later(request=None):\n    r = request\n",  # a default says what it holds
    "    request = 1\n",
    "    t = request\n",  # pytest's `request`, by its name
)


def _write(root: Path, name: str, source: str) -> Path:
    path: Path = root / name
    path.parent.mkdir(parents=True, exist_ok=True)
    _ = path.write_text(textwrap.dedent(source), encoding="utf-8", newline="\n")
    return path


def _project(root: Path) -> Path:
    """Write a package annotating `request` alike three times, by two spellings, and a file leaving it bare.

    Returns:
      The file leaving it bare.

    """
    _ = _write(root, "pkg/__init__.py", "")
    _ = _write(root, "pkg/http.py", HTTP)
    _ = _write(root, "pkg/views.py", VIEWS)
    _ = _write(root, "pkg/more.py", MORE)
    return _write(root, "pkg/plain.py", PLAIN)


def test_a_bare_parameter_takes_the_type_its_name_is_annotated_with_elsewhere(tmp_path: Path) -> None:
    """A guess, by the commonest spelling, imported for type checking; not a parameter with a default."""
    plain: Path = _project(tmp_path)
    _ = cli.main(["--fix", "-q", str(tmp_path)])
    assert FIXED[2] not in plain.read_text(encoding="utf-8")
    _ = cli.main(["--fix", "-q", "--unsafe-fixes", str(tmp_path)])
    fixed: str = plain.read_text(encoding="utf-8")
    assert all(line in fixed for line in (*FIXED, *UNFIXED)), fixed


def test_agreement_is_kept_on_the_index(tmp_path: Path) -> None:
    """Worked out once for every file that asks."""
    plain: Path = _project(tmp_path)
    catalog: Index = project.index(sorted(tmp_path.rglob("*.py")))
    found: dict[str, tuple[str, str]] = {"request": ("pkg.views", "Request")}
    assert consistent.agreed(catalog) == found
    assert catalog.memo is not None
    assert catalog.memo.named == found
    catalog.memo.named = {}
    assert not consistent.visible(catalog, plain, {})


def test_a_file_the_index_doesnt_have_takes_nothing(tmp_path: Path) -> None:
    """A notebook, a file not among those checked, or one whose module's name another file has.

    Nor one that can't write the type: its name means something else there.
    """
    plain: Path = _project(tmp_path)
    catalog: Index = project.index(sorted(tmp_path.rglob("*.py")))
    assert not consistent.visible(catalog, tmp_path / "notes.ipynb", {})
    assert not consistent.visible(catalog, tmp_path / "other.py", {})
    assert consistent.visible(catalog, plain, {}) == {"request": ("Request", frozenset({"named"}))}
    clash: Path = _write(tmp_path, "pkg/clash.py", CLASH)
    assert not consistent.visible(project.index(sorted(tmp_path.rglob("*.py"))), clash, {})
    _ = _write(tmp_path, "other/pkg/__init__.py", "")
    _ = _write(tmp_path, "other/pkg/plain.py", "")
    repeated: Index = project.index(sorted(tmp_path.rglob("*.py")))
    assert not consistent.visible(repeated, plain, {})


def _module(
    name: str,
    annotations: dict[str, tuple[str, ...]],
    *,
    bare: Iterable[str] = (),
    installed: bool = False,
) -> Module:
    names: dict[str, tuple[str, str | None]] = {
        "Frame": ("frames", "Frame"),
        "fr": ("frames", None),
        "Any": ("typing", "Any"),
    }
    return Module(
        name=name,
        returns={},
        names=names,
        annotated=annotations,
        bare=frozenset(bare),
        installed=installed,
    )


def _agreed(*modules: Module) -> dict[str, tuple[str, str]]:
    bare: Module = _module("bare", {}, bare=frozenset({"df", "x", "anything", "rare", "local", "mixed"}))
    catalog: Index = Index({module.name: module for module in (*modules, bare)}, [])
    return dict(consistent.agreed(catalog))


def test_only_a_name_annotated_alike_three_times_and_saying_something_agrees() -> None:
    """By what each name refers to; not one of no known origin, nor `Any`; nor an installed module's."""
    one: Module = _module(
        "a",
        {
            "df": ("Frame", "fr.Frame"),
            "x": ("int",),
            "anything": ("Any", "Any", "Any"),
            "rare": ("Frame", "Frame"),
            "local": ("Inner", "Inner", "Inner"),
            "mixed": ("Frame", "Frame", "int"),
            "unwanted": ("int", "int", "int"),
        },
    )
    two: Module = _module("b", {"df": ("list[Frame]",), "x": ("int", "int")})
    three: Module = _module("c", {"df": ("Frame",)})
    installed: Module = _module("d", {"rare": ("Frame",)}, installed=True)
    assert _agreed(one, three, installed) == {"df": ("a", "Frame")}
    assert _agreed(one, two, three) == {"x": ("a", "int")}


def test_a_name_is_annotated_by_its_functions_parameters() -> None:
    """Not `self`, `*args`, a local, nor a string that doesn't parse."""
    tree: ast.Module = ast.parse(
        textwrap.dedent(
            """
            class C:
                def m(self, a: int, b, /, c: "list[int]", *args: int, d=1, e, f: "no (", **kw: int):
                    self.x: int = 1
                    g: str = ""

                    def inner(h: bytes, i=2, *, j, k=3):
                        g: str = ""
            """,
        ),
    )
    assert annotated.annotations(tree) == {"a": ("int",), "c": ("list[int]",), "h": ("bytes",)}
    assert annotated.bare(tree) == frozenset({"b", "e", "j"})
