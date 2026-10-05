# SPDX-License-Identifier: MIT
"""`--fix` for a test's parameters: typed by the pytest fixtures it names and `parametrize`'s literals."""

import textwrap
from pathlib import Path
from typing import Final

from constricter import Offence, check_source
from constricter.cli import command as cli
from constricter.fix.index import fixtures, project

FRAME: Final = """
class Frame:
    def copy(self) -> "Frame":
        return self

    def size(self) -> int:
        return 0
"""
ROOT_CONFTEST: Final = """
from collections.abc import Iterator

import pytest

from pkg.frame import Frame


@pytest.fixture
def float_frame() -> Frame:
    return Frame()


@pytest.fixture()
def made():
    return Frame()


@pytest.fixture
def opened() -> Iterator[Frame]:
    yield Frame()


@pytest.fixture
def lazy() -> Iterator[Frame]:
    return iter([Frame()])


@pytest.fixture
def odd() -> Frame:
    yield Frame()


@pytest.fixture
def unknown(request):
    return request.param


@pytest.fixture
def shadowed() -> int:
    return 1


@pytest.fixture
def hidden() -> int:
    return 1
"""
NEAR_CONFTEST: Final = """
import pytest


@pytest.fixture
def shadowed() -> str:
    return "a"


@pytest.fixture
def hidden(request):
    return request.param
"""
TESTS: Final = """
import pytest

from pkg.frame import Frame


@pytest.fixture
def own() -> bytes:
    return b""


def test_copy(float_frame, made, opened, lazy, odd, unknown, request):
    result = float_frame.copy()
    other = made
    n = opened.size()
    kept = lazy
    o = odd
    u = unknown
    r = request


def test_nearest(shadowed, hidden, own):
    s = shadowed
    h = hidden
    b = own


@pytest.fixture
def derived(shadowed):
    d = shadowed
    return d


def helper(shadowed):
    x = shadowed
"""
FIXED: Final = (
    "    result: Frame = float_frame.copy()\n",
    "    other: Frame = made\n",  # by its `return`s
    "    n: int = opened.size()\n",  # a generator's: what it yields
    "    kept: Iterator[Frame] = lazy\n",  # not a generator: what it says
    "    s: str = shadowed\n",  # the nearer `conftest.py`'s
    "    b: bytes = own\n",  # the module's own
    "    d: str = shadowed\n",  # a fixture takes fixtures too
)
UNFIXED: Final = (
    "    o = odd\n",  # a generator declaring something else
    "    u = unknown\n",
    "    r = request\n",  # pytest's own
    "    h = hidden\n",  # the nearer one, of no known type, is the one taken
    "    x = shadowed\n",  # not a test, nor a fixture
)

PLAIN_FIXED: Final = (
    "    from pkg.frame import Frame\n",
    "    result: Frame = float_frame\n",
    "    copy = float_frame.copy()\n",
)
CLASHING: Final = "    result = float_frame\n"


def _write(root: Path, name: str, source: str) -> Path:
    path: Path = root / name
    path.parent.mkdir(parents=True, exist_ok=True)
    _ = path.write_text(textwrap.dedent(source), encoding="utf-8", newline="\n")
    return path


def _project(root: Path) -> Path:
    """Write a package with a `conftest.py`, and a package of tests with its own.

    Returns:
      The tests' file.

    """
    _ = _write(root, "pkg/__init__.py", "")
    _ = _write(root, "pkg/frame.py", FRAME)
    _ = _write(root, "pkg/conftest.py", ROOT_CONFTEST)
    _ = _write(root, "pkg/tests/__init__.py", "")
    _ = _write(root, "pkg/tests/conftest.py", NEAR_CONFTEST)
    return _write(root, "pkg/tests/test_frame.py", TESTS)


def test_a_tests_parameters_are_its_fixtures_values(tmp_path: Path) -> None:
    """As guesses: its module's fixtures, then each `conftest.py`'s above it, the nearest first."""
    tests: Path = _project(tmp_path)
    _ = cli.main(["--fix", "-q", str(tmp_path)])
    assert FIXED[0] not in tests.read_text(encoding="utf-8")
    _ = cli.main(["--fix", "-q", "--unsafe-fixes", str(tmp_path)])
    fixed: str = tests.read_text(encoding="utf-8")
    assert all(line in fixed for line in (*FIXED, *UNFIXED)), fixed


def test_a_fixtures_class_the_file_doesnt_import_is_imported_for_type_checking(tmp_path: Path) -> None:
    """Its methods aren't known there, though: only what the file imports has members."""
    _ = _project(tmp_path)
    source: str = "def test_copy(float_frame):\n    result = float_frame\n    copy = float_frame.copy()\n"
    plain: Path = _write(tmp_path, "pkg/tests/test_plain.py", source)
    _ = cli.main(["--fix", "-q", "--unsafe-fixes", str(tmp_path)])
    fixed: str = plain.read_text(encoding="utf-8")
    assert all(line in fixed for line in PLAIN_FIXED), fixed


def test_a_type_whose_name_the_file_binds_otherwise_is_no_fix(tmp_path: Path) -> None:
    """`Frame` is the test's own class there: the fixture's can't be imported under that name."""
    _ = _project(tmp_path)
    clash: Path = _write(
        tmp_path,
        "pkg/tests/test_clash.py",
        "def test_copy(float_frame):\n    Frame = 1\n    result = float_frame\n",
    )
    _ = cli.main(["--fix", "-q", "--unsafe-fixes", str(tmp_path)])
    assert CLASHING in clash.read_text(encoding="utf-8")


def test_a_file_the_index_doesnt_have_takes_no_fixtures(tmp_path: Path) -> None:
    """A notebook, or a file that isn't among those checked."""
    tests: Path = _project(tmp_path)
    catalog: project.Index = project.index([tests])
    assert fixtures.visible(catalog, tmp_path / "notes.ipynb", {}) == {}
    assert fixtures.visible(catalog, tmp_path / "other.py", {}) == {}
    assert fixtures.visible(catalog, tests, {}) == {"own": ("bytes", frozenset({"fixture"}))}


FLAT_CONFTEST: Final = """
import pytest


@pytest.fixture
def count() -> int:
    return 1


@pytest.fixture
def ratio():
    return 1.5
"""
FLAT_TEST: Final = "def test_it(count, ratio):\n    n = count\n    r = ratio\n"
_COUNT: Final = {"count": ("int", frozenset({"fixture"}))}
FLAT_FIXED: Final = "    n: int = count\n    r: float = ratio\n"  # `ratio`'s, by its `return`


def test_a_lone_conftest_outside_any_package_is_looked_in(tmp_path: Path) -> None:
    """By the tests beside it and a package's under it: not those of a directory it isn't above."""
    _ = _write(tmp_path, "tests/conftest.py", FLAT_CONFTEST)
    beside: Path = _write(tmp_path, "tests/test_beside.py", FLAT_TEST)
    _ = _write(tmp_path, "tests/unit/__init__.py", "")
    under: Path = _write(tmp_path, "tests/unit/test_under.py", FLAT_TEST)
    apart: Path = _write(tmp_path, "other/test_apart.py", FLAT_TEST)
    catalog: project.Index = project.index(sorted(tmp_path.rglob("*.py")))
    assert fixtures.visible(catalog, beside, {}) == _COUNT
    assert fixtures.visible(catalog, under, {}) == _COUNT
    assert fixtures.visible(catalog, apart, {}) == {}
    _ = cli.main(["--fix", "-q", "--unsafe-fixes", str(tmp_path)])
    fixed: str = beside.read_text(encoding="utf-8")
    assert FLAT_FIXED in fixed, fixed


def test_one_of_several_conftests_outside_a_package_is_not(tmp_path: Path) -> None:
    """Nor are any, by a test whose module's name another file has: neither can be told from the other."""
    _ = _write(tmp_path, "tests/conftest.py", FLAT_CONFTEST)
    _ = _write(tmp_path, "more/conftest.py", FLAT_CONFTEST)
    beside: Path = _write(tmp_path, "tests/test_beside.py", FLAT_TEST)
    catalog: project.Index = project.index(sorted(tmp_path.rglob("*.py")))
    assert fixtures.visible(catalog, beside, {}) == {}
    _ = _write(tmp_path, "more/conftest.py", "")
    _ = (tmp_path / "more" / "conftest.py").rename(tmp_path / "more" / "test_beside.py")
    catalog = project.index(sorted(tmp_path.rglob("*.py")))
    assert fixtures.visible(catalog, beside, {}) == {}


def _fixes(source: str) -> list[tuple[str, str | None]]:
    """Check `source`, alone.

    Returns:
      Each offence's name and fix.

    """
    offences: list[Offence] = check_source(textwrap.dedent(source))
    return [(o.name, o.fix) for o in offences]


def test_parametrize_types_a_name_it_gives_literals_of_one_type() -> None:
    """One name or several, however they're written; not a name the test annotates or binds again."""
    source: str = """
    import pytest


    @pytest.mark.parametrize("n", [1, 2])
    @pytest.mark.parametrize("s, flag", [("a", True), ("b", False)])
    @pytest.mark.parametrize(("x", "y"), [(1.5, None), (2.5, None)])
    @pytest.mark.parametrize(["again", "typed"], [(1, 2), (3, 4)])
    def test_cases(n, s, flag, x, y, again, typed: int):
        a = n
        b = s
        c = flag
        d = x
        e = y
        again = 0
        f = again
        g = typed
    """
    assert _fixes(source) == [
        ("a", "int"),
        ("b", "str"),
        ("c", "bool"),
        ("d", "float"),
        ("e", None),  # `None` alone says nothing
        ("f", "int"),  # by its own `again = 0`
        ("g", "int"),
    ]


def test_pytests_own_tmp_path_is_a_path() -> None:
    """In a test or a fixture: not where `parametrize` gives the name, nor in a helper."""
    source: str = """
    import pytest


    def test_reads(tmp_path):
        a = tmp_path / "x"
        b = a.read_text()


    @pytest.fixture
    def written(tmp_path):
        c = tmp_path.parent
        return c


    @pytest.mark.parametrize("tmp_path", [1, 2])
    def test_given(tmp_path):
        d = tmp_path


    def helper(tmp_path):
        e = tmp_path.parent
    """
    assert _fixes(source) == [("a", "Path"), ("b", "str"), ("c", "Path"), ("d", "int"), ("e", None)]


def test_tmp_path_is_no_fix_where_the_module_cant_name_a_path() -> None:
    """`Path` and `pathlib` both bound to something else: nothing to write its type with."""
    source: str = """
    Path = pathlib = None


    def test_reads(tmp_path):
        a = tmp_path.parent
    """
    assert _fixes(source) == [("a", None)]


def test_parametrize_types_nothing_it_doesnt_write_out() -> None:
    """Values of two types or none known, a row of another length, or names and cases held elsewhere."""
    source: str = """
    import pytest

    CASES = [1, 2]
    NAMES = "n"


    @pytest.mark.parametrize("mixed", [1, "a"])
    @pytest.mark.parametrize("made", [object(), object()])
    @pytest.mark.parametrize("p, q", [(1, 2), 3, (4, 5, 6)])
    @pytest.mark.parametrize("held", CASES)
    @pytest.mark.parametrize(NAMES, [1, 2])
    @pytest.mark.parametrize(("k", NAMES), [(1, 2)])
    @pytest.mark.skip
    @pytest.mark.usefixtures("other")
    def test_cases(mixed, made, p, q, held, n, k):
        a = mixed
        b = made
        c = p
        d = held
        e = n
        f = k


    @pytest.mark.parametrize("n", [1, 2])
    def helper(n):
        g = n
    """
    assert _fixes(source) == [(name, None) for name in "abcdefg"]
