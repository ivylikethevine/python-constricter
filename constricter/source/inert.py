"""Class decorators and metaclasses that leave a class body's annotations unread: its class can be plain.

An annotation in a class body makes the variable more than its type only where something reads it: a
dataclass's decorator, a model's metaclass, `typing.get_type_hints`. So a decorator whose every
`return` gives its one parameter back (`return cls`), or a factory's every `return` such a decorator
it defines (django's `deconstructible`); or a metaclass under `type` or `abc.ABCMeta` alone, or
another such; whose text names nothing that reads annotations (`READERS`), leaves a plain class plain
(see `constricter.fix.values.classvars`). So do `functools.total_ordering`, `typing.final` and
`abc.ABCMeta`. A metaclass that rewrites a variable's value in the class's namespace isn't seen by
its text: a class variable's fix is a guess (`member`).
"""

import ast
from collections import Counter
from collections.abc import Mapping
from typing import Final

from constricter.source.annotations import dotted
from constricter.source.syntax import import_bindings, own_returns

_METACLASS_KEYWORD: Final = "metaclass"
METACLASS: Final = f"{_METACLASS_KEYWORD}="  # before a metaclass's name, as `marks` spells it
_CALLED: Final = "()"  # after a decorator's, for one called to decorate
_TYPE: Final = "type"
# What reads a class's annotations, or makes it of its fields: a name, an attribute or a string.
READERS: Final = frozenset(
    {
        "__annotations__",
        "__annotate__",
        "__dataclass_fields__",
        "annotationlib",
        "attr",
        "attrs",
        "dataclass",
        "dataclass_transform",
        "dataclasses",
        "get_annotations",
        "get_type_hints",
        "NamedTuple",
        "TypedDict",
    },
)
# The standard library's, by their origins.
_DECORATORS: Final = frozenset({"functools.total_ordering", "typing.final", "typing_extensions.final"})
_METACLASSES: Final = frozenset({"abc.ABCMeta"})


def marks(node: ast.ClassDef) -> tuple[str, ...] | None:
    """Spell a class's decorators and its metaclass, each a name or a call of one, as written.

    Returns:
      Them (`deconstructible`, `register()`, `metaclass=LexerMeta`); `None` if it has another keyword,
      or one that's anything else.

    """
    found: list[str] = []
    keyword: ast.keyword
    name: str | None
    for keyword in node.keywords:
        if keyword.arg != _METACLASS_KEYWORD or (name := dotted(keyword.value)) is None:
            return None
        found.append(f"{METACLASS}{name}")
    decorator: ast.expr
    for decorator in node.decorator_list:
        called: bool = isinstance(decorator, ast.Call)
        if (name := dotted(decorator.func if isinstance(decorator, ast.Call) else decorator)) is None:
            return None
        found.append(f"{name}{_CALLED}" if called else name)
    return tuple(found)


def inert(tree: ast.Module) -> frozenset[str]:
    """Find the module's own decorators and metaclasses that leave a class plain (see the module docstring).

    Each defined once; a metaclass with no keyword or decorator, under `type`, `abc.ABCMeta` or
    another of the module's such, as the module imports them.

    Returns:
      Their names.

    """
    counts: Counter[str] = Counter(
        stmt.name
        for stmt in tree.body
        if isinstance(stmt, ast.FunctionDef | ast.AsyncFunctionDef | ast.ClassDef)
    )
    origins: dict[str, str] = {name: origin for name, origin, _ in import_bindings(tree.body)}
    found: set[str] = {
        stmt.name
        for stmt in tree.body
        if isinstance(stmt, ast.FunctionDef)
        and counts[stmt.name] == 1
        and _hands_back(stmt)
        and not _reads(stmt)
    }
    pending: list[ast.ClassDef] = [
        stmt
        for stmt in tree.body
        if isinstance(stmt, ast.ClassDef)
        and counts[stmt.name] == 1
        and stmt.bases
        and not (stmt.keywords or stmt.decorator_list)
        and not _reads(stmt)
    ]
    for _ in list(pending):  # each pass takes one more, or ends
        more: list[ast.ClassDef] = [
            stmt for stmt in pending if all(_meta_base(base, found, origins) for base in stmt.bases)
        ]
        if not more:
            break
        found.update(stmt.name for stmt in more)
        pending = [stmt for stmt in pending if stmt not in more]
    return frozenset(found)


def judged(mark: str, local: frozenset[str], origins: Mapping[str, str]) -> bool | None:
    """Say whether a class's mark (see `marks`) leaves it plain, as far as its module sees.

    `local`: the module's own such (see `inert`); `origins`: what its imports bind, dotted.

    Returns:
      Whether it does; `None` for one it can't tell of (one it imports from another file), which
      only the index can follow.

    """
    meta: bool = mark.startswith(METACLASS)
    name: str = mark.removeprefix(METACLASS).removesuffix(_CALLED)
    first: str
    rest: str
    first, _, rest = name.partition(".")
    if first not in origins and ((not rest and first in local) or (meta and name == _TYPE)):
        return True
    origin: str = f"{origins[first]}.{rest}" if rest and first in origins else origins.get(first, "")
    return True if origin in (_METACLASSES if meta else _DECORATORS) else None


def _meta_base(base: ast.expr, found: set[str], origins: Mapping[str, str]) -> bool:
    name: str | None
    if (name := dotted(base)) is None:
        return False
    first: str
    rest: str
    first, _, rest = name.partition(".")
    if first not in origins:
        return not rest and (first in found or first == _TYPE)
    origin: str = f"{origins[first]}.{rest}" if rest else origins[first]
    return origin in _METACLASSES


def _hands_back(func: ast.FunctionDef) -> bool:
    """Check whether a function gives back the class it decorates: as a decorator, or a factory of one.

    Every `return` of its own gives back one of its parameters, or one of its own nested functions
    that does, or that function's call (`return decorator(*args)`, as it decorates bare); and it has
    one.

    Returns:
      Whether it does.

    """
    returns: list[ast.Return]
    if not (returns := own_returns(func.body)):
        return False
    args: ast.arguments = func.args
    params: set[str] = {arg.arg for arg in (*args.posonlyargs, *args.args)}
    nested: set[str] = {
        stmt.name for stmt in func.body if isinstance(stmt, ast.FunctionDef) and _hands_back(stmt)
    }
    value: ast.expr | None
    name: str
    for value in (stmt.value for stmt in returns):
        match value:
            case ast.Name(id=name) if name in params or name in nested:
                pass
            case ast.Call(func=ast.Name(id=name)) if name in nested:
                pass
            case _:
                return False
    return True


def _reads(node: ast.stmt) -> bool:
    """Check whether a definition's text names anything that reads annotations (see `READERS`).

    Returns:
      Whether it does.

    """
    return any(
        (isinstance(each, ast.Name) and each.id in READERS)
        or (isinstance(each, ast.Attribute) and each.attr in READERS)
        or (isinstance(each, ast.Constant) and isinstance(each.value, str) and each.value in READERS)
        for each in ast.walk(node)
    )
