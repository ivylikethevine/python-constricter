"""`--fix` for calls to unannotated functions whose docstrings name a builtin scalar return (a guess)."""

import ast
import textwrap
from typing import TypeAlias

import pytest

from constricter import Checks, Offence, check_source
from constricter.fix.values.documented import documented

_Fixed: TypeAlias = tuple[str | None, bool, frozenset[str]]  # a fix, whether it's a guess, its kinds

_SOURCE: str = '''
def density(graph):
    """The density.

    Returns
    -------
    d : float
        Edges over pairs.
    """
    return graph.size() / graph.pairs()


def named(graph):
    """The name.

    Returns:
        str: Its name, or nothing.
    """
    return graph.name


def found(graph):
    """The node.

    :rtype: int or None
    """
    return graph.find()


def wrong(graph):
    """Said to be an int.

    Returns
    -------
    int
    """
    return "no"


def bare(graph):
    """Said to be an int, but may give nothing.

    Returns
    -------
    int
    """
    if graph:
        return graph.count()
    return


def decorated_away(graph):
    """Said to be an int.

    Returns
    -------
    int
    """
    return graph.count()


decorated_away = staticmethod(decorated_away)


class Graph:
    def order(self):
        """The nodes.

        Returns
        -------
        int
        """
        return self.count()


def use(graph, other: Graph) -> None:
    d = density(graph)
    name = named(graph)
    node = found(graph)
    no = wrong(graph)
    maybe = bare(graph)
    order = other.order()
'''


def test_a_docstrings_named_return_types_a_call_as_a_guess() -> None:
    """numpydoc, Google-style and Sphinx: where every `return` takes the type, and each gives a value."""
    offences: list[Offence] = check_source(textwrap.dedent(_SOURCE), checks=Checks())
    fixes: dict[str, _Fixed] = {
        o.name: (o.fix, o.unsafe, o.edit.kinds if o.edit else frozenset()) for o in offences
    }
    assert fixes["d"] == ("float", True, frozenset({"documented", "returned"}))
    assert fixes["name"][:2] == ("str", True)
    assert fixes["node"][:2] == ("int | None", True)
    assert fixes["no"][:2] == ("str", False)  # its `return` decides: the docstring isn't read
    assert fixes["maybe"][0] is None  # a `return` of nothing
    assert fixes["order"] == ("int", True, frozenset({"documented", "returned"}))


@pytest.mark.parametrize(
    ("docstring", "expected"),
    [
        ("Returns\n-------\nint\n    The count.", "int"),
        ("Returns\n-------\nn : integer\n    The count.\n\nSee Also\n--------\nother", "int"),
        ("Returns\n-------\nboolean", "bool"),
        ("Returns\n-------\nfloat or None", "float | None"),
        ("Returns\n-------\nNone or string", "str | None"),
        ("Returns\n-------\na : int\nb : str", None),  # a tuple's parts
        ("Returns\n-------\nG : NetworkX graph", None),
        ("Returns\n-------\nlist of int", None),
        ("Returns\n-------\ndict or None", None),
        ("Returns\n-------\n", None),
        ("Doc.\n\nReturns:\n    bool: Whether it is.", "bool"),
        ("Doc.\n\nReturns:\n    The thing.", None),
        (":rtype: ``bytes``", "bytes"),
        ("No section.", None),
        ("Doc.\n\n    Returns\n    -------\n    int\nOutside the section.", "int"),
    ],
)
def test_a_docstrings_return_is_read_as_a_builtin_scalar_alone(docstring: str, expected: str | None) -> None:
    """One entry naming `int`, `float`, `bool`, `str`, `bytes`, `complex` or a long name, or one `or None`."""
    func: ast.stmt = ast.parse(f"def f():\n    {docstring!r}\n    return x\n").body[0]
    assert isinstance(func, ast.FunctionDef)
    assert documented(func, [None]) == expected


@pytest.mark.parametrize(
    ("returned", "expected"),
    [(["int"], "float"), (["bool", None], "float"), (["str"], None), (["None"], None)],
)
def test_a_docstrings_type_takes_what_the_returns_give(
    returned: list[str | None],
    expected: str | None,
) -> None:
    """A `float` takes an `int` and a `bool`; a known `return` of another type refuses it."""
    func: ast.stmt = ast.parse('def f():\n    """D.\n\n    Returns\n    -------\n    float\n    """\n').body[
        0
    ]
    assert isinstance(func, ast.FunctionDef)
    assert documented(func, returned) == expected


_DIVIDED: str = '''
def f(delta, unit):
    """D.

    Returns
    -------
    {named}
    """
    return delta / unit
'''


@pytest.mark.parametrize(("named", "expected"), [("int", None), ("bool or None", None), ("float", "float")])
def test_a_true_division_is_no_documented_integer(named: str, expected: str | None) -> None:
    """`return delta / unit` gives a `float` whatever the docstring says; a `float` it may be."""
    func: ast.stmt = ast.parse(_DIVIDED.format(named=named)).body[0]
    assert isinstance(func, ast.FunctionDef)
    assert documented(func, [None]) == expected


def test_a_function_without_a_docstring_is_not_documented() -> None:
    """Nothing to read."""
    func: ast.stmt = ast.parse("def f():\n    return x\n").body[0]
    assert isinstance(func, ast.FunctionDef)
    assert documented(func, [None]) is None
