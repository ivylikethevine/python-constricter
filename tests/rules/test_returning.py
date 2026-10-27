"""LVA014 (opt-in): a plain function that declares no return type, fixed by what its `return`s give."""

import ast
import textwrap
from typing import Final, TypeAlias

from constricter import Checks, Offence, check_source, check_tree
from constricter.fix.core import fixes
from constricter.fix.core.known import Hints, Offered, Outside
from constricter.offences import Edit, Fix, FixPolicy

UNANNOTATED_RETURN: Final = "LVA014"
_ON: Final = Checks(returns=True)
_Guessed: TypeAlias = tuple[str | None, bool, frozenset[str]]  # a fix, whether a guess, and its kinds
_BOTH: Final = frozenset({"constructor", "returned"})
_ONE: Final = frozenset({"returned"})
# The headers the fixes write: before the `:` that ends each, past a lambda's; `fail` has no fix.
_HEADERS: Final = (
    "def size(items: list[str]) -> int:\n",
    "def log(message: str) -> None:\n",
    "    pick=lambda pair: pair[0],\n) -> str:\n",
    "async def fetch() -> int:\n",
    "    def width(self) -> int:\n",
    "def fail(message: str):\n",
)
SOURCE: Final = """
import functools


def count(items: list[str]) -> int:
    return len(items)


def size(items: list[str]):
    return len(items)


def log(message: str):
    print(message)
    if not message:
        return


def fail(message: str):
    raise ValueError(message)


def todo():
    ...


def wrapped(
    key: str = "a:b",
    pick=lambda pair: pair[0],
):
    return key


def echo(value):
    return value


def outer():
    def inner():
        return 1

    return inner


async def fetch():
    return 1


@functools.cache
def cached():
    return 1


class Box:
    def width(self):
        return 3

    def show(self):
        print(self)


def make():
    return Box()
"""


def _found(source: str = SOURCE, checks: Checks = _ON) -> dict[str, Offence]:
    found: list[Offence] = check_source(textwrap.dedent(source), checks=checks)
    return {o.name: o for o in found if o.code == UNANNOTATED_RETURN}


def test_a_function_with_no_return_type_is_reported_only_where_selected() -> None:
    """Off by default, as LVA012 and LVA013 are; a decorated one isn't plain, an annotated one declares it."""
    assert not [o for o in check_source(textwrap.dedent(SOURCE)) if o.code == UNANNOTATED_RETURN]
    assert set(_found()) == {
        "size",
        "log",
        "fail",
        "todo",
        "wrapped",
        "echo",
        "outer",
        "fetch",
        "width",
        "show",
        "make",
    }


def test_its_fix_is_what_its_returns_give() -> None:
    """Certain for a module's function, a guess for a method; `None` for one that returns nothing."""
    found: dict[str, Offence] = _found()
    fixed: dict[str, tuple[str | None, bool]] = {
        name: (o.fix, o.unsafe) for name, o in found.items() if o.edit is not None
    }
    assert fixed == {
        "size": ("int", False),
        "log": ("None", False),
        "wrapped": ("str", False),
        "fetch": ("int", False),
        "width": ("int", True),
        "show": ("None", True),
        "make": ("Box", True),  # its `return`'s value is a guess (`constructor`)
    }
    # One that only raises, a stub, and values nothing typed (an unannotated parameter, a function) have none.
    assert all(found[name].edit is None for name in ("fail", "todo", "echo", "outer"))


def test_a_guessed_return_rests_on_its_guess_and_is_trusted_as_one() -> None:
    """`make`'s fix rests on `constructor` and `returned`: trusted both, it's certain; one alone, a guess."""
    found: dict[str, Offence] = _found()
    assert found["make"].edit is not None
    assert found["make"].edit.kinds == {"constructor", "returned"}
    assert found["width"].edit is not None
    assert found["width"].edit.kinds == {"returned"}
    trusted: dict[str, Offence] = _found(checks=Checks(returns=True, fixes=FixPolicy(unsafe_select=_BOTH)))
    assert (trusted["make"].unsafe, trusted["width"].unsafe) == (False, False)
    partly: dict[str, Offence] = _found(checks=Checks(returns=True, fixes=FixPolicy(unsafe_select=_ONE)))
    assert (partly["make"].unsafe, partly["width"].unsafe) == (True, False)


def test_a_traced_runs_return_is_the_fix_where_the_returns_decide_nothing() -> None:
    """A guess (`traced`), for `echo` (returning its parameter), not `size` (its `return`s decide it)."""
    tree: ast.Module = ast.parse(textwrap.dedent(SOURCE))
    starts: dict[str, tuple[int, int]] = {
        node.name: (node.lineno, node.col_offset)
        for node in ast.walk(tree)
        if isinstance(node, ast.FunctionDef)
    }
    seen: dict[tuple[int, int], Offered] = {starts["echo"]: Offered("str"), starts["size"]: Offered("float")}
    outside: Outside = Outside(hints=(Hints("a traced run", kind="traced", returns=seen),))
    found: list[Offence] = check_tree(tree, _ON, lines=textwrap.dedent(SOURCE).splitlines(), outside=outside)
    fixed: dict[str, _Guessed] = {
        o.name: (o.fix, o.unsafe, o.edit.kinds if o.edit else frozenset())
        for o in found
        if o.code == UNANNOTATED_RETURN and o.name in {"echo", "size"}
    }
    assert fixed == {
        "echo": ("str", True, frozenset({"traced"})),
        "size": ("int", False, frozenset({"returned"})),
    }


def test_the_fix_goes_before_the_colon_ending_the_header() -> None:
    """Past a default with a `:` in it, and a parameter's lambda, on the line the header ends on."""
    text: list[str] = textwrap.dedent(SOURCE).splitlines(keepends=True)
    written: str = "".join(fixes.apply(text, list(_found().values())))
    assert all(header in written for header in _HEADERS)


def test_a_class_the_module_imports_is_one_it_can_name() -> None:
    """What its `return`s give names a class it imports: the fix needs no import of its own."""
    source: str = """
    from pathlib import Path


    def here():
        return Path.cwd()


    def parent(p: Path):
        return p.parent
    """
    found: dict[str, Offence] = _found(source)
    assert set(found) == {"here", "parent"}
    assert [found[name].fix for name in ("here", "parent")] == ["Path", "Path"]


def test_a_stub_has_no_fix_and_the_module_binds_what_it_names() -> None:
    """`pass`, a docstring, `raise NotImplementedError` declare nothing; an `if`'s or `try`'s names count."""
    source: str = """
    \"\"\"A module docstring: a statement that binds nothing.\"\"\"
    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from fractions import Fraction
    try:
        from decimal import Decimal
    except ImportError:
        MISSING = True
    else:
        LIMIT: int = 3
    finally:
        DONE = True


    def later():
        pass


    def abstract():
        \"\"\"Not yet.\"\"\"
        raise NotImplementedError


    class Plain:
        size = 1

        def ordered(self):
            return Decimal(1)
    """
    found: dict[str, Offence] = _found(source)
    assert (found["later"].edit, found["abstract"].edit) == (None, None)
    assert [found["ordered"].fix] == ["Decimal"]  # a name the module imports in a `try`


def test_with_no_source_to_read_the_header_isnt_fixed() -> None:
    """A tree checked alone (`check_tree` with no lines) reports it, but can't place the fix."""
    offences: list[Offence] = check_tree(ast.parse("def f():\n    return 1\n"), _ON)
    assert [(o.code, o.edit) for o in offences] == [(UNANNOTATED_RETURN, None)]


def test_a_signature_edit_off_the_headers_colon_is_left_unmade() -> None:
    """Its span must land on the `:`: the text has changed since, so nothing is written."""
    fix: Fix = Fix("int", edit=Edit.SIGNATURE, span=(1, 3))
    offence: Offence = Offence(1, 0, "f", UNANNOTATED_RETURN, fix)
    assert fixes.replacement(["def f():\n"], offence) is None
