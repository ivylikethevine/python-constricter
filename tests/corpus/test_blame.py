"""The fix a new type error is blamed on: the one whose name the argument it names reads, first."""

from typing import Final

from tests.corpus import blame

_SOURCE: Final = """LIMIT = 3


def concat(items, how, flag):
    _how = "horizontal" if flag else how
    result = join(items, how=_how)
    total = add(items, _how)
    shown = show(*items, _how)
    width = measure(len(items) + LIMIT)
    other = measure(width=LIMIT)
    return result, total, shown, other
"""
_PATH: Final = "m.py"


def _fixed(source: str = _SOURCE) -> blame.Fixed:
    """Read `source` as a fixed file no fix moved a line of.

    Returns:
      It.

    """
    lines: list[str] = source.splitlines()
    return blame.Fixed(lines, list(range(len(lines) + 2)), frozenset(), blame.scopes(source))


def _fix(line: int, name: str) -> blame.Fix:
    return blame.Fix(_PATH, line, name, "str", "checker", unsafe=True)


_LIMIT: Final = _fix(1, "LIMIT")
_HOW: Final = _fix(5, "_how")
_RESULT: Final = _fix(6, "result")
_TOTAL: Final = _fix(7, "total")
_SHOWN: Final = _fix(8, "shown")
_WIDTH: Final = _fix(9, "width")
_FIXES: Final = [_LIMIT, _HOW, _RESULT, _TOTAL, _SHOWN, _WIDTH, _fix(10, "other")]


def _blamed(line: int, message: str) -> blame.Fix | None:
    """Blame an error on `line` with `message` on one of `_FIXES`.

    Returns:
      The fix, if any.

    """
    return blame.blamed(blame.Complaint(_PATH, line, message), _fixed(), _FIXES)


def test_an_argument_mypy_names_is_blamed_on_the_fix_of_the_name_passed() -> None:
    """By keyword or position, not on the fix of the name the line binds (narwhals' `_how`)."""
    assert _blamed(6, 'Argument "how" to "join" has incompatible type "str"') == _HOW
    assert _blamed(7, 'Argument 2 to "add" has incompatible type "str"') == _HOW
    assert _blamed(6, 'Argument "how" to "Frame.join" has incompatible type "str"') == _HOW  # its last part
    # The module's own fix, where it's a global the function reads.
    assert _blamed(10, 'Argument "width" to "measure" has incompatible type "str"') == _LIMIT


def test_an_argument_pyright_names_is_blamed_by_its_parameter_passed_by_keyword() -> None:
    """In any call on the line: Pyright names a constructor's call `__init__`."""
    message: str = (
        'Argument of type "str" cannot be assigned to parameter "how" of type "Literal[1]" in function'
    )
    assert _blamed(6, f'{message} "__init__"') == _HOW
    assert _blamed(6, message) == _HOW


def test_an_argument_no_fixed_bare_name_is_passed_as_is_blamed_on_the_line() -> None:
    """An expression, an argument after an unpacking, another function's, or one the call lacks."""
    assert _blamed(9, 'Argument 1 to "measure" has incompatible type "int"') == _WIDTH
    assert _blamed(8, 'Argument 2 to "show" has incompatible type "str"') == _SHOWN
    assert _blamed(6, 'Argument "how" to "split" has incompatible type "str"') == _RESULT
    assert _blamed(6, 'Argument "into" to "join" has incompatible type "str"') == _RESULT
    assert _blamed(7, 'Argument 9 to "add" has incompatible type "str"') == _TOTAL
    assert _blamed(6, 'Incompatible types in assignment (expression has type "str")') == _RESULT


def test_an_argument_in_a_file_that_doesnt_parse_reads_nothing() -> None:
    """The fixed file as it is: blamed on its line, as any other error."""
    broken: str = _SOURCE.replace("def concat(items, how, flag):", "def concat(items, how, flag)")
    complaint: blame.Complaint = blame.Complaint(_PATH, 6, 'Argument "how" to "join" has')
    assert blame.argument(complaint, broken.splitlines()) is None
    assert blame.argument(complaint, _SOURCE.splitlines()) == _HOW.name
    assert blame.argument(complaint._replace(message="Name is not defined"), _SOURCE.splitlines()) is None
