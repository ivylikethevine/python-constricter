"""`--fix` for a plain class's variables across its line: one type in every class that binds it.

A class variable's type is invariant, so a base's and its overrides' are joined (`classvars.joined`);
and a class under a metaclass or decorator that reads no annotations (`source.inert`) is plain too.
"""

import ast
import textwrap
from pathlib import Path
from typing import Final, TypeAlias

from constricter import Checks, Offence, check_source
from constricter.fix.index import plain, project
from constricter.fix.values import classvars
from constricter.source import inert

# Each offence's fix and whether it's a guess, by its line.
_Fixed: TypeAlias = dict[int, tuple[str, str | None]]
_ALL: Final = Checks(all_scopes=True)
LINE: Final = """
class Lexer:
    priority = 0
    name = None
    flag = True
    mixed = 1
    aliases = ("a",)


class Sub(Lexer):
    priority = 0.5
    name = "sub"
    mixed = "a"
    aliases = ("b", "c")


class Leaf(Sub):
    priority = 2
"""


def _fixed(source: str) -> _Fixed:
    found: list[Offence] = check_source(textwrap.dedent(source), checks=_ALL)
    return {o.line: (o.name, o.fix) for o in found}


def _class(source: str) -> ast.ClassDef:
    node: ast.stmt = ast.parse(source).body[0]
    assert isinstance(node, ast.ClassDef)
    return node


def _index(tmp_path: Path, files: dict[str, str]) -> project.Index:
    paths: list[Path] = []
    name: str
    source: str
    for name, source in files.items():
        path: Path = tmp_path / name
        path.parent.mkdir(parents=True, exist_ok=True)
        _ = path.write_text(textwrap.dedent(source), encoding="utf-8")
        paths.append(path)
    return plain.settled(project.index(paths))


def test_a_variable_takes_the_type_every_class_in_its_line_binds_it_to() -> None:
    """The widest number, `None` with a type, a tuple of any length; types that differ left as they are."""
    assert _fixed(LINE) == {
        3: ("priority", "float"),
        4: ("name", "str | None"),
        5: ("flag", "bool"),
        6: ("mixed", "int"),
        7: ("aliases", "tuple[str, ...]"),
        11: ("priority", "float"),
        12: ("name", "str | None"),
        13: ("mixed", "str"),
        14: ("aliases", "tuple[str, ...]"),
        18: ("priority", "float"),
    }


def test_the_join_spans_the_checked_files_and_a_class_of_several_bases(tmp_path: Path) -> None:
    """A base in one file, its overrides in another; two bases a class takes both of are joined there."""
    catalog: project.Index = _index(
        tmp_path,
        {
            "pkg/__init__.py": "",
            "pkg/base.py": """
                class Lexer:
                    priority = 0
                    name = None


                class Other:
                    priority = 1.5
            """,
            "pkg/subs.py": """
                from .base import Lexer, Other


                class Sub(Lexer):
                    name = "sub"


                class Both(Lexer, Other):
                    pass
            """,
        },
    )
    assert catalog.modules["pkg.base"].members == {
        "Lexer": {"priority": "float", "name": "str | None"},
        "Other": {"priority": "float"},
    }
    assert catalog.modules["pkg.subs"].members == {"Sub": {"name": "str | None"}}


MARKED: Final = """
import functools


class LexerMeta(type):
    def __new__(mcs, name, bases, namespace):
        if "analyse" in namespace:
            namespace["analyse"] = staticmethod(namespace["analyse"])
        return type.__new__(mcs, name, bases, namespace)


class RegexMeta(LexerMeta):
    pass


class FieldsMeta(type):
    def __new__(mcs, name, bases, namespace):
        namespace["fields"] = namespace.get("__annotations__", {})
        return type.__new__(mcs, name, bases, namespace)


def register(cls):
    return cls


def named(label):
    def decorator(cls):
        cls.label = label
        return cls

    return decorator


def wrapped(cls):
    return make(cls)


def deconstructible(*args, path=None):
    def decorator(klass):
        klass.path = path
        return klass

    if not args:
        return decorator
    return decorator(*args)


class Lexer(metaclass=RegexMeta):
    priority = 0


class Model(metaclass=FieldsMeta):
    table = "rows"


@register
@named("x")
@functools.total_ordering
class Registered:
    kind = "a"


@wrapped
class Wrapped:
    size = 3


@deconstructible
class Validator:
    message = "bad"


@register
class Built(make()):
    built = 1


@register
class Mixed:
    value = 1


class Other(Mixed):
    value = "a"
"""


def test_a_class_under_a_metaclass_or_decorator_that_reads_no_annotations_is_plain() -> None:
    """One under `type`, or that gives back its class; not one that reads `__annotations__`, nor a wrapper."""
    tree: ast.Module = ast.parse(textwrap.dedent(MARKED))
    assert inert.inert(tree) == {"LexerMeta", "RegexMeta", "register", "named", "deconstructible"}
    assert classvars.marked(tree) == {
        "Lexer": ("metaclass=RegexMeta",),
        "Model": ("metaclass=FieldsMeta",),
        "Registered": ("register", "named()", "functools.total_ordering"),
        "Wrapped": ("wrapped",),
        "Validator": ("deconstructible",),
        "Mixed": ("register",),
    }
    plain_now: frozenset[str] = classvars.plain(tree, classvars.imported(tree))
    assert plain_now == {"Lexer", "Registered", "Validator", "Mixed", "Other"}
    assert classvars.plain(tree, classvars.imported(tree), marked_too=False) == frozenset()
    # `Mixed`'s `value` and `Other`'s fit no one type: under marks alone, neither is typed.
    assert {name: fix for name, fix in _fixed(MARKED).values() if fix} == {
        "priority": "int",
        "kind": "str",
        "message": "str",
    }


def test_a_mark_is_read_where_its_module_says() -> None:
    """The module's own, the standard library's, `type`; another file's is the index's to follow."""
    assert inert.judged("metaclass=type", frozenset(), {})
    assert inert.judged("total_ordering", frozenset(), {"total_ordering": "functools.total_ordering"})
    assert inert.judged("metaclass=ABCMeta", frozenset(), {"ABCMeta": "abc.ABCMeta"})
    assert inert.judged("register", frozenset({"register"}), {})
    assert inert.judged("register", frozenset(), {"register": "pkg.util.register"}) is None
    assert inert.judged("dataclass", frozenset(), {"dataclass": "dataclasses.dataclass"}) is None
    assert inert.marks(_class("@a.b(1)\nclass C(metaclass=M): pass\n")) == ("metaclass=M", "a.b()")
    assert inert.marks(_class("@f()()\nclass C: pass\n")) is None
    assert inert.marks(_class("class C(total=False): pass\n")) is None


def test_another_files_inert_decorator_leaves_a_class_plain(tmp_path: Path) -> None:
    """Followed through the import to the checked file that defines it, and its re-export."""
    catalog: project.Index = _index(
        tmp_path,
        {
            "pkg/__init__.py": "from .util import register\n",
            "pkg/util.py": """
                def register(cls):
                    return cls


                def fields(cls):
                    cls.names = list(cls.__annotations__)
                    return cls
            """,
            "rows.py": """
                from pkg import register
                from pkg.util import fields


                @register
                class Row:
                    many = True


                @fields
                class Record:
                    count = 1
            """,
        },
    )
    assert catalog.modules["pkg.util"].inert == {"register"}
    assert catalog.modules["rows"].plain == {"Row"}
    assert catalog.modules["rows"].members["Row"] == {"many": "bool"}


def test_the_index_reads_a_mark_its_module_or_nothing_says_of(tmp_path: Path) -> None:
    """A metaclass the module defines, or `type`, as the file reads it; not a decorator no import binds."""
    catalog: project.Index = _index(
        tmp_path,
        {
            "lexers.py": """
                class Meta(type):
                    pass


                class Lexer(metaclass=Meta):
                    priority = 0


                @undefined
                class Odd:
                    odd = 1


                class Typed(metaclass=type):
                    typed = 1
            """,
        },
    )
    assert catalog.modules["lexers"].plain == {"Lexer", "Typed"}
    assert catalog.modules["lexers"].members == {
        "Lexer": {"priority": "int"},
        "Odd": {"odd": "int"},
        "Typed": {"typed": "int"},
    }


SHADOWED: Final = """
def register(cls):
    return cls


@register
class Element:
    labelled = True
    rendered = False


class Column(Element):
    @property
    def labelled(self):
        return False


class Base:
    lookup = None
    shown = None


class Exact(Base):
    lookup = "exact"

    def shown(self):
        return True


class Like(Base):
    lookup = "like"
"""


def test_a_newly_typed_variable_a_class_in_its_line_defines_is_left_alone() -> None:
    """A property or method of its name would be an incompatible override of the annotation.

    A variable of a class plain by its marks alone, or bound to `None`, which the join alone types;
    the classes beside the one that defines it keep theirs.
    """
    assert {line: fix for line, fix in _fixed(SHADOWED).items() if fix[1]} == {
        9: ("rendered", "bool"),
        19: ("lookup", "str | None"),
        24: ("lookup", "str | None"),
        31: ("lookup", "str | None"),
    }
    tree: ast.Module = ast.parse(textwrap.dedent(SHADOWED))
    assert classvars.defined(tree) == {"Column": {"labelled"}, "Exact": {"shown"}}
