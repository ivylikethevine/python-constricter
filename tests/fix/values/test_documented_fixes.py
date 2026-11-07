"""`--fix` for calls to unannotated functions whose docstrings name their return type (a guess)."""

import ast
import textwrap
from pathlib import Path
from typing import TYPE_CHECKING, TypeAlias

import pytest

from constricter import Checks, Offence, check_source
from constricter.cli import command as cli
from constricter.fix.libraries import stdlib
from constricter.fix.values.documented import documented, writable

if TYPE_CHECKING:
    from collections.abc import Callable

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
        ("Returns\n-------\na : int\nb : str", None),  # a tuple's parts, but `return x` is no tuple
        ("Returns\n-------\nG : NetworkX graph", None),
        ("Returns\n-------\nlist of int", "list[int]"),
        ("Returns\n-------\ntuple of strings", "tuple[str, ...]"),
        ("Returns\n-------\nlist of node-like", None),
        ("Returns\n-------\nlist[str] or None", "list[str] | None"),
        ("Returns\n-------\ndict[str, int]", "dict[str, int]"),
        ("Returns\n-------\ndict[str, int | None]", "dict[str, int | None]"),
        ("Returns\n-------\nint or integer", "int"),
        ("Returns\n-------\ndict[str, Any]", None),
        ("Returns\n-------\ndict", None),  # its arguments unknown: vague
        ("Returns\n-------\ndict or None", None),
        ("Returns\n-------\nint, float or None", "int | float | None"),
        ("Returns\n-------\nscalar, Series or DataFrame", None),
        ("Returns\n-------\nNone", None),
        ("Returns\n-------\n", None),
        ("Doc.\n\nReturns:\n    bool: Whether it is.", "bool"),
        ("Doc.\n\nReturns:\n    The thing.", None),
        (":rtype: ``bytes``", "bytes"),
        (":rtype: str | None", "str | None"),
        ("No section.", None),
        ("Doc.\n\n    Returns\n    -------\n    int\nOutside the section.", "int"),
    ],
)
def test_a_docstrings_return_is_read_as_scalars_and_containers(docstring: str, expected: str | None) -> None:
    """Builtin scalars, `None` among others, and a builtin container of them with its arguments."""
    func: ast.stmt = ast.parse(f"def f():\n    {docstring!r}\n    return x\n").body[0]
    assert isinstance(func, ast.FunctionDef)
    assert documented(func, [None]) == expected


_CLASSES: str = "class Graph: ...\nclass Box(Generic[T]): ...\nclass Twice: ...\nclass Twice: ...\n"


@pytest.mark.parametrize(
    ("docstring", "expected"),
    [
        ("Returns\n-------\nGraph", "Graph"),
        ("Returns\n-------\nG : nx.Graph\n    The graph.", "nx.Graph"),
        ("Returns\n-------\nSeries or DataFrame", None),  # the receiver's own kind
        ("Returns\n-------\nint or Graph", None),
        ("Returns\n-------\nGraph or None", "Graph | None"),
        ("Returns\n-------\nlist of Graph", "list[Graph]"),
        ("Returns\n-------\ndict[str, Graph]", "dict[str, Graph]"),
        ("Returns\n-------\ngraph", None),  # no class by that name
        ("Returns\n-------\nBox", None),  # generic: its arguments unknown
        ("Returns\n-------\nTwice", None),  # defined twice
        ("Returns\n-------\nlist of Graphs", "list[Graph]"),
        ("Returns\n-------\nlist of graphs", None),
        ("Returns\n-------\nnx.Graph | None", "nx.Graph | None"),
        ("Returns\n-------\nlist[nx.Graph]", "list[nx.Graph]"),
        ("Returns\n-------\nlist[nx.Digraph]", None),
        ("Returns\n-------\nlist[int, str]", None),
        ("Returns\n-------\ntuple[int, ...]", "tuple[int, ...]"),
        ("Returns\n-------\ntuple[int, Graph]", "tuple[int, Graph]"),
        ("Returns\n-------\nlist[", None),
        ("Returns\n-------\nCallable[[int], str]", None),
        ("Doc.\n\nReturns:\n    nx.Graph: The graph.", "nx.Graph"),
    ],
)
def test_a_docstrings_return_names_a_class_the_module_writes(docstring: str, expected: str | None) -> None:
    """A class the module binds by that name (`writable`), not a generic one."""
    module: ast.Module = ast.parse(f"{_CLASSES}def f():\n    {docstring!r}\n    return x\n")
    func: ast.stmt = module.body[-1]
    assert isinstance(func, ast.FunctionDef)
    named: frozenset[str] = frozenset({"nx.Graph", "Series", "DataFrame"})
    classes: Callable[[str], bool] = writable(module, (named.__contains__,))
    assert documented(func, [None], classes=classes) == expected


_PAIR: str = "D.\n\nReturns\n-------\na : int\nb : str"


@pytest.mark.parametrize(
    ("body", "expected"),
    [
        ("return a, b", "tuple[int, str]"),
        ("if a:\n        return a, b\n    return b, a", "tuple[int, str]"),
        ("return a", None),
        ("return a, b, c", None),
        ("return (*a, b)", None),
    ],
)
def test_several_numpydoc_entries_are_a_tuple_every_return_displays(body: str, expected: str | None) -> None:
    """A numpydoc section lists a tuple's parts as entries; a docstring may list alternatives so too."""
    source: str = f"def f(a, b):\n    {_PAIR!r}\n    {body}\n"
    func: ast.stmt = ast.parse(source).body[0]
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


_NUMPY: str = '''
{imports}


def f(raw):
    """D.

    Returns
    -------
    {named}
    """
    return raw.read()


def use(raw) -> None:
    n = f(raw)
'''


@pytest.mark.parametrize(
    ("imports", "named", "expected"),
    [
        ("import numpy as np", "int", None),
        ("from numpy import linalg", "float or None", None),
        ("try:\n    import numpy.ma\nexcept ImportError:\n    pass", "bool", None),
        ("import numpy as np", "str", "str"),
        ("import numbers", "int", "int"),
    ],
)
def test_a_module_importing_numpy_has_no_documented_number(
    imports: str,
    named: str,
    expected: str | None,
) -> None:
    """A numpy scalar (`np.int64`) is no `int` to a checker, and its docstrings may mean one."""
    offences: list[Offence] = check_source(_NUMPY.format(imports=imports, named=named), checks=Checks())
    assert {o.name: o.fix for o in offences}["n"] == expected


def test_a_function_without_a_docstring_is_not_documented() -> None:
    """Nothing to read."""
    func: ast.stmt = ast.parse("def f():\n    return x\n").body[0]
    assert isinstance(func, ast.FunctionDef)
    assert documented(func, [None]) is None


_GIVES_NONE: str = '''
def f(items):
    """D.

    Returns
    -------
    {named}
    """
    for item in items:
        if item:
            return item * 2
    return None
'''


@pytest.mark.parametrize(("named", "expected"), [("int", None), ("int or None", "int | None")])
def test_a_return_of_none_refuses_a_documented_type_without_it(named: str, expected: str | None) -> None:
    """As nibabel's `find_private_section`: `element_start : int`, then `return None` where none is found."""
    func: ast.stmt = ast.parse(_GIVES_NONE.format(named=named)).body[0]
    assert isinstance(func, ast.FunctionDef)
    assert documented(func, [None, None]) == expected


_MAYBE_GRAPH: str = "D.\n\nReturns\n-------\nGraph or None"


@pytest.mark.parametrize(
    ("returned", "expected"),
    [
        (["Graph"], "Graph | None"),
        (["Graph | None"], "Graph | None"),
        (["Tree"], None),
        (["Graph | None | Tree"], None),
    ],
)
def test_a_class_takes_its_own_return_alone(returned: list[str | None], expected: str | None) -> None:
    """A known `return` of another class refuses it: a subclass isn't read."""
    module: ast.Module = ast.parse(f"class Graph: ...\ndef f():\n    {_MAYBE_GRAPH!r}\n")
    func: ast.stmt = module.body[-1]
    assert isinstance(func, ast.FunctionDef)
    assert documented(func, returned, classes=writable(module)) == expected


_UNNAMED: frozenset[str] = frozenset({"OrderedDict", "dt.MINYEAR"})  # generic, and a constant


def test_the_standard_librarys_classes_are_spelled_as_imported() -> None:
    """A class its import names, or one of a module it imports; not one missing its type arguments."""
    names: frozenset[str] = stdlib.class_names(
        {"dt": "datetime", "Decimal": "decimal.Decimal", "OrderedDict": "collections.OrderedDict"},
    )
    assert {"dt.datetime", "dt.timedelta", "Decimal"} <= names
    assert not names & _UNNAMED


_SHAPES: str = """
from typing import Generic, TypeVar

T = TypeVar("T")


class Plain:
    pass


class Box(Generic[T]):
    pass
"""
_MAKERS: str = '''
import datetime as dt
from collections import OrderedDict

from pkg.shapes import Box, Plain


def plain(spec):
    """P.

    Returns
    -------
    Plain
    """
    return spec.build()


def box(spec):
    """B.

    Returns
    -------
    Box
    """
    return spec.build()


def when(spec):
    """W.

    Returns
    -------
    dt.datetime
    """
    return spec.build()


def ordered(spec):
    """O.

    Returns
    -------
    OrderedDict
    """
    return spec.build()
'''
_CALLS: str = """
from pkg.makers import box, ordered, plain, when


def run(spec) -> None:
    p = plain(spec)
    b = box(spec)
    w = when(spec)
    o = ordered(spec)
"""


_TYPED: tuple[str, ...] = ("fix 'p': `Plain`", "fix 'w': `dt.datetime`")
_LEFT: tuple[str, ...] = ("fix 'b'", "fix 'o'")


@pytest.mark.xdist_group("jobs")
@pytest.mark.parametrize("jobs", ["1", "2"])
def test_a_class_another_file_imports_is_named_by_a_docstring(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
    jobs: str,
) -> None:
    """Typed in the calling file too, by any number of jobs; no generic class, nor one wanting arguments."""
    (tmp_path / "pkg").mkdir()
    name: str
    source: str
    for name, source in (("__init__", ""), ("shapes", _SHAPES), ("makers", _MAKERS), ("calls", _CALLS)):
        _ = (tmp_path / "pkg" / f"{name}.py").write_text(textwrap.dedent(source), encoding="utf-8")
    arguments: list[str] = ["--show-fixes", "--unsafe-fixes", "-q", f"--jobs={jobs}", str(tmp_path / "pkg")]
    assert cli.main(arguments) == cli.EXIT_FOUND
    shown: str = capsys.readouterr().out
    assert all(line in shown for line in _TYPED)
    assert not any(line in shown for line in _LEFT)
