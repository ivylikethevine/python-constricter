"""`--fix` for calls to unannotated functions whose docstrings name a builtin scalar return (a guess).

A numpydoc `Returns` section of one entry (`int`, `n : int`), a Google-style `Returns:` whose first
line names the type (`bool: Whether ...`) or a Sphinx `:rtype:` field, naming `int`, `float`,
`bool`, `str`, `bytes` or `complex` (or `integer`, `boolean`, `string`), or one of them `or None`.
Only where every `return` the function has gives a value of no known type or one the named type
takes (`int` for a `float`), no `int` or `bool` where one is a true division (`a / b`), and no
number in a module importing numpy, whose scalars no checker takes for one: a docstring may be
stale, so its type is a guess (`documented`).
"""

import ast
import re
from collections.abc import Iterable
from typing import Final

from constricter.source.syntax import FunctionDef, own_returns

KIND: Final = "documented"  # the guessing mechanism (`FIX_KINDS`)
_SCALARS: Final = {
    "int": "int",
    "integer": "int",
    "float": "float",
    "bool": "bool",
    "boolean": "bool",
    "str": "str",
    "string": "str",
    "bytes": "bytes",
    "complex": "complex",
}
# What a value of each type may be where that's the type named: a `bool` is an `int`, an `int` a `float`.
_TAKES: Final = {
    "int": frozenset({"int", "bool"}),
    "float": frozenset({"float", "int", "bool"}),
    "complex": frozenset({"complex", "float", "int", "bool"}),
    "bool": frozenset({"bool"}),
    "str": frozenset({"str"}),
    "bytes": frozenset({"bytes"}),
    "None": frozenset({"None"}),
}
_NONE: Final = "None"
_INTEGERS: Final = frozenset({"int", "bool"})  # what a true division (`/`) never gives
_NUMBERS: Final = frozenset({"int", "float", "complex", "bool"})  # what a docstring names numpy's scalars
_NUMPY: Final = "numpy"
_OR_NONE: Final = re.compile(r"(?P<type>\w+)\s+or\s+none|none\s+or\s+(?P<other>\w+)")
_NUMPYDOC: Final = re.compile(
    r"^(?P<indent>[ \t]*)Returns[ \t]*\n[ \t]*-{3,}[ \t]*\n(?P<body>(?:.*\n?)*)",
    re.MULTILINE,
)
_GOOGLE: Final = re.compile(r"^[ \t]*Returns?:[ \t]*\n[ \t]+(?P<type>[\w ]+?)[ \t]*:", re.MULTILINE)
_SPHINX: Final = re.compile(r"^[ \t]*:rtype:[ \t]*(?P<type>[^\n]+?)[ \t]*$", re.MULTILINE)
_ENTRY: Final = re.compile(r"(?:\w+[ \t]*:[ \t]*)?(?P<type>[^\n:]+?)[ \t]*")


def documented(func: FunctionDef, returned: Iterable[str | None], *, numpy: bool = False) -> str | None:
    """Type a function by its docstring's named return, where its `return`s allow it.

    `returned`: each `return`'s type, `None` where it isn't known; `numpy`: its module imports numpy
    (see `imports_numpy`), so a number it names may be numpy's (`np.int64`).

    Returns:
      The type (`int`, `str | None`), or `None`: no docstring, no return named, one that isn't a
      builtin scalar, a number where `numpy`, or a `return` of a value it doesn't take.

    """
    docstring: str | None = ast.get_docstring(func)
    named: str | None = None if docstring is None else _named(docstring)
    parts: set[str] = set() if named is None else set(named.split(" | "))
    if named is None or (_INTEGERS & parts and _divides(func)) or (numpy and _NUMBERS & parts):
        return None
    allowed: frozenset[str] = frozenset[str]().union(*(_TAKES[part] for part in named.split(" | ")))
    return named if all(each is None or each in allowed for each in returned) else None


def imports_numpy(module: ast.Module) -> bool:
    """Check whether a module imports numpy or a submodule, at its top level or in a top-level `if` or `try`.

    Returns:
      Whether it does.

    """
    statements: list[ast.stmt] = [*module.body]
    statement: ast.stmt
    for statement in module.body:
        if isinstance(statement, ast.If | ast.Try):
            statements.extend((*statement.body, *statement.orelse))
    return any(
        (isinstance(each, ast.Import) and any(alias.name.partition(".")[0] == _NUMPY for alias in each.names))
        or (
            isinstance(each, ast.ImportFrom)
            and not each.level
            and (each.module or "").partition(".")[0] == _NUMPY
        )
        for each in statements
    )


def _divides(func: FunctionDef) -> bool:
    """Check whether a `return` of the function's gives a true division, which no `int` or `bool` is.

    Returns:
      Whether one does.

    """
    returned: list[ast.expr | None] = [each.value for each in own_returns(func.body)]
    return any(isinstance(value, ast.BinOp) and isinstance(value.op, ast.Div) for value in returned)


def _named(docstring: str) -> str | None:
    """Read the type a docstring names its return as (see the module's docstring).

    Returns:
      It, as an annotation; `None` for none, several (a tuple's parts), or another kind of type.

    """
    found: re.Match[str] | None
    text: str | None = None
    if (found := _NUMPYDOC.search(docstring)) is not None:
        text = _numpydoc(found.group("body"), found.group("indent"))
    elif (found := _GOOGLE.search(docstring)) is not None or (found := _SPHINX.search(docstring)) is not None:
        text = found.group("type")
    return None if text is None else _scalar(text)


def _numpydoc(body: str, indent: str) -> str | None:
    """Read a numpydoc `Returns` section's one entry's type (its description indented under it).

    Returns:
      Its text; `None` where the section lists more than one (a tuple's parts) or none.

    """
    entries: list[str] = []
    line: str
    for line in body.splitlines():
        if not line.strip():
            continue
        if not line.startswith(indent) or line[len(indent) :].startswith((" ", "\t")):
            if not line.startswith(indent):
                break
            continue  # a description line
        if set(line.strip()) <= {"-"}:  # the next section's underline: its heading was the last entry
            _ = entries.pop()
            break
        entries.append(line[len(indent) :])
    if len(entries) != 1:
        return None
    entry: re.Match[str] | None = _ENTRY.fullmatch(entries[0])
    return None if entry is None else entry.group("type")


def _scalar(text: str) -> str | None:
    """Write a docstring's type as an annotation, where it's a builtin scalar or one `or None`.

    Returns:
      It, or `None`.

    """
    words: str
    if (words := " ".join(text.strip().strip("`").lower().split())) in _SCALARS:
        return _SCALARS[words]
    optional: re.Match[str] | None = _OR_NONE.fullmatch(words)
    name: str | None = None if optional is None else optional.group("type") or optional.group("other")
    return None if name not in _SCALARS else f"{_SCALARS[name]} | {_NONE}"
