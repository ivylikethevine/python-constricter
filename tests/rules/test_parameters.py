"""LVA015 (opt-in): a parameter with no annotation, fixed by what typed it for the function's check."""

import textwrap
from pathlib import Path
from typing import Final

import pytest

from constricter.cli import command as cli
from constricter.offences import UNANNOTATED_PARAMETER

LIB: Final = """
class Holder:
    def method(self, m):
        return m

    @staticmethod
    def make(cls, n=1):
        return n

    @classmethod
    def build(cls, k, *rest, **named):
        return k


def twice(n):
    return n + n


def keyed(a, *, b=1):
    return a + b


def rebinds(value):
    value = None
    return value


def typed(x: int, y: "str", z=1):
    return x
"""
APP: Final = """
from lib import keyed, twice


def run() -> None:
    d = twice(1)
    e = twice(2)
    k = keyed("a", b="b")
"""
# What `--fix --unsafe-fixes --extend-select LVA015` writes in `lib.py`, and what it leaves.
# Both codes' fixes at once: a signature is written whole (see `signatures`), the returns by `returned`.
_TWICE: Final = "def twice(n: int) -> int:\n"
_KEYED: Final = "def keyed(a: str, *, b: str = 1) -> str:\n"
_LEFT: Final = ("def rebinds(value):\n", "    def method(self, m):\n", "    def make(cls, n=1):\n")
_CALLED: Final = "    d: int = twice(1)\n"
_BARE: Final = "def twice(n):\n"
_COUNT: Final = "def count() -> int:\n"
_SPREAD: Final = "def spread(n, *rest):\n"


def _written(root: Path) -> tuple[Path, Path]:
    lib: Path = root / "lib.py"
    app: Path = root / "app.py"
    _ = lib.write_text(textwrap.dedent(LIB), encoding="utf-8", newline="\n")
    _ = app.write_text(textwrap.dedent(APP), encoding="utf-8", newline="\n")
    return lib, app


def test_every_unannotated_parameter_but_a_receiver_is_reported(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Not `self` or `cls` (a static method's first parameter is no receiver), nor `*rest` or `**named`."""
    lib: Path
    lib, _ = _written(tmp_path)
    assert cli.main(["-q", "--extend-select=LVA015", str(lib)]) == cli.EXIT_FOUND
    reported: list[str] = [
        line.rpartition("'")[0].rpartition("'")[2]
        for line in capsys.readouterr().out.splitlines()
        if UNANNOTATED_PARAMETER in line
    ]
    assert reported == ["m", "cls", "n", "k", "n", "a", "b", "value", "z"]


@pytest.mark.parametrize(
    ("args", "reported"),
    [
        ([], False),
        (["--select=LVA0"], False),  # a prefix never selects an opt-in code
        (["--extend-select=LVA012"], False),  # nor does another opt-in code
        (["--max"], False),  # ruff's ANN001 again: left to it
        (["--extend-select=LVA015"], True),
    ],
)
def test_the_command_reports_it_only_when_named(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
    args: list[str],
    reported: bool,  # ruff: ignore[boolean-type-hint-positional-argument]  # a parameter pytest fills in
) -> None:
    """`--select` or `--extend-select` must name LVA015 in full; it's an error from `strict`."""
    path: Path = tmp_path / "f.py"
    _ = path.write_text("def f(n):\n    return n\n", encoding="utf-8")
    assert cli.main(["-q", *args, str(path)]) == (cli.EXIT_FOUND if reported else cli.EXIT_CLEAN)
    assert (f"error: {UNANNOTATED_PARAMETER}" in capsys.readouterr().out) == reported


def test_its_fix_is_what_every_call_passes_as_a_guess(tmp_path: Path) -> None:
    """Written with `--unsafe-fixes`, a default spaced after it; never for a parameter bound again."""
    lib: Path
    lib, _ = _written(tmp_path)
    codes: str = "--extend-select=LVA014,LVA015"
    assert cli.main(["--fix", "-q", codes, str(tmp_path)]) == cli.EXIT_FOUND
    assert _TWICE not in lib.read_text(encoding="utf-8")  # a guess: not without `--unsafe-fixes`
    assert cli.main(["--fix", "--unsafe-fixes", "-q", codes, str(tmp_path)]) == cli.EXIT_FOUND
    fixed: str = lib.read_text(encoding="utf-8")
    assert _TWICE in fixed
    assert _KEYED in fixed
    assert all(line in fixed for line in _LEFT), fixed


def test_a_written_signature_reaches_its_callers_in_the_same_run(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """`callers` trusted, `twice` is signed `(n: int) -> int` and `d = twice(1)` typed certain, in one run."""
    lib: Path
    app: Path
    lib, app = _written(tmp_path)
    args: list[str] = ["--fix", "-q", "--unsafe-fix-select=callers", "--extend-select=LVA014,LVA015"]
    assert cli.main([*args, str(tmp_path)]) == cli.EXIT_FOUND
    assert _TWICE in lib.read_text(encoding="utf-8")
    assert _CALLED in app.read_text(encoding="utf-8")
    _ = capsys.readouterr()
    assert cli.main(["--diff", *args[1:], str(tmp_path)]) == cli.EXIT_CLEAN  # a second pass is left nothing
    assert not capsys.readouterr().out


def test_a_signature_is_written_whole_or_not_at_all(tmp_path: Path) -> None:
    """A return alone on bare parameters, or one parameter among bare ones, is no fix (`signatures`)."""
    lib: Path = tmp_path / "lib.py"
    source: str = "def twice(n):\n    return n + n\n\n\ndef spread(n, *rest):\n    return n\n\n\n"
    _ = lib.write_text(source + "def count():\n    return 1\n", encoding="utf-8")
    app: Path = tmp_path / "app.py"
    _ = app.write_text(
        "from lib import spread, twice\n\n\ndef run() -> None:\n    twice(1)\n    spread(2, 3)\n",
        encoding="utf-8",
    )
    _ = cli.main(["--fix", "--unsafe-fixes", "-q", "--extend-select=LVA014", str(tmp_path)])
    assert _BARE in lib.read_text(encoding="utf-8")  # its parameter bare: no return alone
    assert _COUNT in lib.read_text(encoding="utf-8")
    _ = cli.main(["--fix", "--unsafe-fixes", "-q", "--extend-select=LVA014,LVA015", str(tmp_path)])
    fixed: str = lib.read_text(encoding="utf-8")
    assert _TWICE in fixed
    assert _SPREAD in fixed  # `*rest` has no fix: nothing written


def test_explain_says_it_is_opt_in(capsys: pytest.CaptureFixture[str]) -> None:
    """`--explain LVA015` says it's only reported when selected."""
    with pytest.raises(SystemExit):
        _ = cli.main(["--explain", UNANNOTATED_PARAMETER])
    assert capsys.readouterr().out.endswith("suffocate: error (only when selected)\n")
