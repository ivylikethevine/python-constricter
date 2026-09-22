# SPDX-License-Identifier: MIT
"""Value flow (constricter.flow): each name's values over its lifetime, against its declared type."""

import ast
import textwrap

import pytest

from constricter.checker import Checks, value_flow
from constricter.flow import DEFAULT_PARENTS, Finding, Hierarchy, Kind, augmented, members


def _found(source: str) -> list[tuple[str, Kind, str]]:
    return [(f.name, f.kind, f.detail) for f in value_flow(textwrap.dedent(source))]


@pytest.mark.parametrize(
    ("annotation", "expected"),
    [
        ("int", {"int"}),
        ("int | None", {"int", "None"}),
        ("Optional[int]", {"int", "None"}),
        ("typing.Optional[str]", {"str", "None"}),
        ("Union[int, str]", {"int", "str"}),
        ("Union[int]", {"int"}),
        ("'int | str'", {"int", "str"}),
        ("List[int]", {"list[int]"}),
        ("typing.Dict[str, int]", {"dict[str, int]"}),
        ("Set", {"set"}),
        ("typing.Callable", {"Callable"}),
        ("os.PathLike[str]", {"os.PathLike[str]"}),
        ("None", {"None"}),
    ],
)
def test_members_split_and_normalise_a_union(annotation: str, expected: set[str]) -> None:
    """Every spelling of a union splits into the same members; `typing` aliases read as builtins."""
    assert members(annotation) == frozenset(expected)


@pytest.mark.parametrize("annotation", ["int |", "Optional['not valid(']", "Union[int, 'x y']"])
def test_members_of_an_unreadable_annotation_are_unknown(annotation: str) -> None:
    """An annotation (or a string part of one) that doesn't parse can't be compared."""
    assert members(annotation) is None


def test_the_default_hierarchy_is_the_numeric_tower() -> None:
    """`bool` fits `int`, `int` fits `float`, `float` fits `complex`, and never the other way."""
    tower: Hierarchy = Hierarchy(DEFAULT_PARENTS)
    assert tower.wider("bool") == {"int", "float", "complex"}
    assert tower.fits("int", "complex")
    assert not tower.fits("float", "int")
    assert tower.fits("str", "object")
    assert tower.simplified(["bool", "int", "str"]) == {"int", "str"}


def test_a_cycle_in_the_hierarchy_ends() -> None:
    """Types that are each other's parents (only a custom hierarchy could say so) still resolve."""
    cycle: Hierarchy = Hierarchy({"A": ["B"], "B": ["A"]})
    assert cycle.wider("A") == {"B"}


def test_a_modules_classes_join_the_hierarchy_under_their_named_bases() -> None:
    """A class is narrower than each base it names; an attribute base (`abc.ABC`) isn't followed."""
    tree: ast.Module = ast.parse("class Base: ...\nclass Child(Base): ...\nclass Other(abc.ABC): ...\n")
    hierarchy: Hierarchy = Hierarchy.for_module(tree)
    assert hierarchy.fits("Child", "Base")
    assert hierarchy.wider("Other") == frozenset()


@pytest.mark.parametrize(
    ("op", "operand", "expected"),
    [
        (ast.Div(), "int", "float"),
        (ast.Div(), "complex", "complex"),
        (ast.Div(), "str", None),
        (ast.Add(), "str", "str"),
        (ast.Mod(), None, None),
        (ast.Pow(), "int", None),  # `2 ** -1` is a float
    ],
)
def test_augmented_assignments(op: ast.operator, operand: str | None, expected: str | None) -> None:
    """What `x op= operand` can bind, besides `x`'s own type."""
    assert augmented(op, operand) == expected


def test_a_declared_type_every_value_fits_a_narrower_one_of() -> None:
    """LVA008: only ever an `int`, though declared `float` (`+=` keeps it one)."""
    source: str = """
    def f() -> None:
        total: float = 0
        total += 1
        total = 2
    """
    assert _found(source) == [("total", Kind.NARROWABLE, "int")]


def test_a_value_that_doesnt_fit_the_declared_type() -> None:
    """LVA009 at the value, whether or not the name's other values are known; no narrowing claim."""
    source: str = """
    def f(count: int) -> None:
        count = "done"
        count = g()
    """
    assert value_flow(textwrap.dedent(source)) == [Finding(3, 4, "count", Kind.CONFLICT, "str")]


def test_a_declared_union_member_no_value_uses() -> None:
    """LVA010 per unused member; what's left narrowing further is LVA008 as well."""
    source: str = """
    def f() -> None:
        label: int | str = 3
        label = 4
        ratio: float | bytes | None = None
        ratio = 1
    """
    assert _found(source) == [
        ("label", Kind.UNUSED_MEMBER, "str"),
        ("ratio", Kind.NARROWABLE, "int | None"),
        ("ratio", Kind.UNUSED_MEMBER, "bytes"),
    ]


def test_a_union_every_member_of_which_is_used_is_left_alone() -> None:
    """`X | None` holding both is ordinary Optional use."""
    source: str = """
    def f() -> None:
        maybe: int | None = None
        maybe = 3
    """
    assert _found(source) == []


@pytest.mark.parametrize(
    "rebinding",
    [
        "x = g()",  # unknown call
        "x = Box()",  # only a guess: `Box` may be generic
        "x **= 2",  # an operator whose result isn't known
        "for x in []: pass",
        "with g() as x: pass",
        "[x, y] = 1, 2",
        "if (x := 1): pass",
        "import x",
        "def x() -> None: pass",
        "class x: pass",
        "try:\n        pass\n    except ValueError as x:\n        pass",
    ],
)
def test_an_unknown_value_stops_the_narrowing_claims(rebinding: str) -> None:
    """With one value unknown, the name may hold anything its type allows."""
    source: str = f"def f() -> None:\n    x: float = 0\n    {rebinding}\n"
    assert value_flow(source) == []


@pytest.mark.parametrize("keyword", ["global", "nonlocal"])
def test_a_write_from_elsewhere_stops_the_narrowing_claims(keyword: str) -> None:
    """A name another scope can rebind may hold values this one never sees."""
    source: str = f"""
    x: float = 0

    def f() -> None:
        x: float = 0

        def g() -> None:
            {keyword} x
            x = "s"
        g()
    """
    assert _found(source) == []


def test_nothing_is_said_without_a_readable_specific_declared_type() -> None:
    """No annotation, a vague one, an unreadable one, or one that's never bound says nothing."""
    source: str = """
    def f(*args: int, **kwargs: int) -> None:
        a = 1
        b: Any = 1
        c: "int |" = 1
        d: int
        e: object = "x"
    """
    assert _found(source) == []


def test_a_parameter_holds_its_declared_type() -> None:
    """What a caller passes is as wide as the annotation: never narrowable, but a rebinding checks."""
    source: str = """
    def f(size: float, other) -> None:
        size = 1
        other = 2
    """
    assert _found(source) == []


def test_a_module_class_narrows_through_a_function_returning_it() -> None:
    """A certain value of a subclass (a function's declared return) narrows its base's annotation."""
    source: str = """
    class Base: ...
    class Child(Base): ...

    def make() -> Child:
        return Child()

    def f() -> None:
        item: Base = make()
    """
    assert _found(source) == [("item", Kind.NARROWABLE, "Child")]


def test_module_and_class_bodies_are_checked_with_all_scopes() -> None:
    """Value flow follows the same scopes as the rules: module and class bodies with `all-scopes`."""
    source: str = "LIMIT: float = 3\n"
    assert value_flow(source) == []
    assert [f.detail for f in value_flow(source, checks=Checks(all_scopes=True))] == ["int"]


def test_a_builtin_containers_element_types_decide_nothing() -> None:
    """A display's element types follow its declared context: only the container is compared."""
    source: str = """
    def f() -> None:
        flags: tuple[str, ...] = ("-q",)
        flags = ("-v", "-d")
        opts: dict[str, int | str] = {"a": 1}
        items: list[int] = {1}
    """
    assert _found(source) == [("items", Kind.CONFLICT, "set[int]")]


def test_a_copy_of_a_union_typed_name_is_unknown() -> None:
    """`if name is None: raise` may have narrowed `name` before `x = name`: value flow can't tell."""
    source: str = """
    def f(name: str | None) -> None:
        if name is None:
            raise ValueError
        label: str = name
    """
    assert _found(source) == []


def test_names_annotated_only_for_type_checkers_are_skipped() -> None:
    """`if TYPE_CHECKING: x: str` / `else: x = None` is a deliberate difference, set from elsewhere."""
    source: str = """
    import typing

    if typing.TYPE_CHECKING:
        token: str
    else:
        token = None
    """
    assert value_flow(textwrap.dedent(source), checks=Checks(all_scopes=True)) == []


def test_a_class_body_makes_no_narrowing_claim() -> None:
    """Instances rebind a class attribute (`self.x = ...`), out of the class body's sight."""
    source: str = """
    class C:
        limit: float = 0
        name: str = 3
    """
    assert [
        (f.name, f.kind) for f in value_flow(textwrap.dedent(source), checks=Checks(all_scopes=True))
    ] == [
        ("name", Kind.CONFLICT),
    ]


@pytest.mark.parametrize(
    ("annotation", "expected"),
    [
        ("ClassVar[bool]", {"bool"}),
        ("typing.Final[int]", {"int"}),
        ("Annotated[str, 'meta']", {"str"}),
        ("Final", None),
    ],
)
def test_qualifiers_are_unwrapped(annotation: str, expected: set[str] | None) -> None:
    """`ClassVar`, `Final` and `Annotated` wrap the type the values have; a bare qualifier names none."""
    assert members(annotation) == (None if expected is None else frozenset(expected))


def test_only_types_whose_ancestry_is_known_are_compared() -> None:
    """An imported class (or one with an imported base) may be a subclass of anything."""
    source: str = """
    from somewhere import Base

    class Local(Base): ...
    class Plain: ...

    def make() -> Local: ...
    def other() -> Plain: ...

    def f() -> None:
        a: Base = make()
        b: str = make()
        c: str = other()
    """
    assert _found(source) == [("c", Kind.CONFLICT, "Plain")]
    assert Hierarchy.for_module(ast.parse("class A(object): ...\nclass B(A): ...\n")).closed("B")
    assert not Hierarchy.for_module(ast.parse("class A(B): ...\nclass B(A): ...\n")).closed("A")
