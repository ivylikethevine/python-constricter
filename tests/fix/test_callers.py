# SPDX-License-Identifier: MIT
"""`--fix` for unannotated parameters: typed by what every call in the checked files passes, as guesses."""

import textwrap
from pathlib import Path
from typing import Final

import pytest

from constricter.cli import command as cli
from constricter.fix import callers, project
from constricter.fix.known import Call, Observed

LIB: Final = """
def greet(name, times):
    line = name.upper()
    count = times * 2
    return line, count


def twice(n):
    doubled = n + n
    return doubled


def keyed(a, *, b=1):
    total = a + b
    return total


def rebinds(value):
    copy = value
    value = None
    return copy, value


def escapes(x):
    y = x
    return y


def mixed(p, q):
    r = p
    s = q
    return r, s


def later(k):
    def later(k):
        inner = k
        return inner

    outer = k
    return outer, later


class Holder:
    def method(self, m):
        kept = m
        return kept
"""
APP: Final = """
from lib import greet, twice, keyed, rebinds, escapes, mixed, later
import lib


def main(flag: bool, maybe: int | None, twice=None):
    greet("a", 1)
    lib.greet(name="b", times=3)
    twice(1)
    lib.twice("x")
    keyed(2)
    rebinds(3)
    callbacks = [escapes]
    escapes(4)
    mixed(1, maybe)
    mixed(flag, maybe)
    later(1.5)
    return callbacks


LATER = later(2.5)
"""
UNTYPED: Final = (
    "    total = a + b\n",  # one call leaves `b` to its default
    "    copy = value\n",  # the function binds its parameter again
    "    y = x\n",  # it escapes, as a callback
    "    s = q\n",  # an `int | None`: a union
    "        inner = k\n",  # a nested function's
    "        kept = m\n",  # a method's
)

LINE: Final = "    line: str = name.upper()\n"
COUNT: Final = "    count: int = times * 2\n"
OUTER: Final = "    outer: float = k\n"
DOUBLED: Final = "    doubled: str = n + n\n"
DISAGREED: Final = "    r = p\n"
DIFFED: Final = "+    line: str = name.upper()\n"
UNFIXED: Final = "    line = name.upper()\n"
TYPED_W: Final = "    w: int = v\n"
UNTYPED_W: Final = "    w = v\n"


def _write(root: Path, name: str, source: str) -> Path:
    path: Path = root / name
    _ = path.write_text(textwrap.dedent(source), encoding="utf-8")
    return path


def test_parameters_every_call_passes_one_type_type_the_function(tmp_path: Path) -> None:
    """As guesses: applied with `--unsafe-fixes`, or `--unsafe-fix-select callers`, never without."""
    lib: Path = _write(tmp_path, "lib.py", LIB)
    _ = _write(tmp_path, "app.py", APP)
    _ = cli.main(["--diff", "-q", str(tmp_path)])
    _ = cli.main(["--fix", "-q", "--unsafe-fix-select", "callers", str(tmp_path)])
    fixed: str = lib.read_text(encoding="utf-8")
    assert LINE in fixed
    assert COUNT in fixed
    assert OUTER in fixed
    assert DOUBLED in fixed  # `twice(1)` in `main` calls its parameter
    assert all(line in fixed for line in UNTYPED), fixed


def test_arguments_that_disagree_or_are_unknown_type_nothing(tmp_path: Path) -> None:
    """`mixed(1, ...)` and `mixed(flag, ...)`: `int` and `bool` disagree."""
    lib: Path = _write(tmp_path, "lib.py", LIB)
    _ = _write(tmp_path, "app.py", APP)
    _ = cli.main(["--fix", "-q", "--unsafe-fixes", str(tmp_path)])
    assert DISAGREED in lib.read_text(encoding="utf-8")


def test_a_diff_is_the_second_rounds(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """Checked again knowing its parameters, a file's diff is the later round's, whole."""
    _ = _write(tmp_path, "lib.py", LIB)
    _ = _write(tmp_path, "app.py", APP)
    _ = cli.main(["--diff", "--unsafe-fixes", str(tmp_path)])
    assert DIFFED in capsys.readouterr().out


def test_modules_of_one_name_arent_checked_again(tmp_path: Path) -> None:
    """Which of two `lib`s a call calls can't be told."""
    (tmp_path / "a").mkdir()
    (tmp_path / "b").mkdir()
    lib: Path = _write(tmp_path / "a", "lib.py", LIB)
    _ = _write(tmp_path / "b", "lib.py", LIB)
    _ = _write(tmp_path / "a", "app.py", APP)
    _ = cli.main(["--fix", "-q", "--unsafe-fixes", str(tmp_path)])
    assert UNFIXED in lib.read_text(encoding="utf-8")


def test_calls_bind_as_python_binds_them() -> None:
    """Too many arguments, an unknown keyword, one bound twice, or unpacking: nothing is typed."""
    params: tuple[tuple[str, str, bool, bool], ...] = (("a", "p", False, False), ("b", "e", False, False))
    catalog: project.Index = project.indexed([project.Module("m", {}, {}, open={"f": params})])
    typed: callers.Parameters = {"f": {"a": ("int", frozenset()), "b": ("str", frozenset())}}

    def found(*calls: Call) -> dict[str, callers.Parameters]:
        return callers.parameters([Observed({("m", "f"): calls})], catalog)

    known: tuple[str, frozenset[str]] = ("int", frozenset())
    text: tuple[str, frozenset[str]] = ("str", frozenset())
    guessed: tuple[str, frozenset[str]] = ("int", frozenset({"returned"}))
    assert found(Call((known,), (("b", text),))) == {"m": typed}
    assert not found(Call((known, text, known)))
    assert not found(Call((known,), (("c", text),)))
    assert not found(Call((known, text), (("b", text),)))
    assert not found(Call(unpacked=True))
    assert found(Call((known, None)), Call((guessed, None))) == {"m": {"f": {"a": guessed}}}
    assert not callers.parameters([Observed({("gone", "f"): (Call((known,)),)})], catalog)


def test_a_call_elsewhere_than_a_function_is_typed_by_its_value_alone(tmp_path: Path) -> None:
    """A module's own call, a class body's, a lambda's: a literal is known, a name isn't."""
    lib: Path = _write(tmp_path, "lib.py", "def f(v):\n    w = v\n    return w\n")
    _ = _write(
        tmp_path,
        "app.py",
        "from lib import f\n\nX = f(1)\n\n\nclass C:\n    Y = f(2)\n    g = lambda: f(3)\n",
    )
    _ = cli.main(["--fix", "-q", "--unsafe-fixes", str(tmp_path)])
    assert TYPED_W in lib.read_text(encoding="utf-8")
    _ = _write(tmp_path, "app.py", "from lib import f\n\nX = 1\nY = f(X)\n")
    lib = _write(tmp_path, "lib.py", "def f(v):\n    w = v\n    return w\n")
    _ = cli.main(["--fix", "-q", "--unsafe-fixes", str(tmp_path)])
    assert UNTYPED_W in lib.read_text(encoding="utf-8")


TWO: Final = "def f(v):\n    w = v\n    return w\n\n\ndef g(v):\n    w = v\n    return w\n"
BOXED: Final = """
from lib import f, g


class Box:
    pass


def run(box: Box, list):
    f(box)
    g([1])
"""
UNPACKING: Final = """
from lib import f


def run(args: list[int]):
    def inner():
        return f(1)

    f(*args)
    return inner
"""


def test_only_builtin_types_from_a_module_that_doesnt_rebind_them_count(tmp_path: Path) -> None:
    """Another's class may mean nothing in the callee's module; a rebound `list` isn't the builtin."""
    lib: Path = _write(tmp_path, "lib.py", TWO)
    _ = _write(tmp_path, "app.py", BOXED)
    _ = cli.main(["--fix", "-q", "--unsafe-fixes", str(tmp_path)])
    assert lib.read_text(encoding="utf-8") == TWO


def test_an_unpacking_call_types_nothing(tmp_path: Path) -> None:
    """`f(*args)` can't be matched; a function inside the caller is its own; module and class bodies too."""
    lib: Path = _write(tmp_path, "lib.py", "def f(v):\n    w = v\n    return w\n")
    _ = _write(tmp_path, "app.py", UNPACKING)
    _ = cli.main(["--fix", "-q", "--unsafe-fixes", "--all-scopes", str(tmp_path)])
    assert UNTYPED_W in lib.read_text(encoding="utf-8")
