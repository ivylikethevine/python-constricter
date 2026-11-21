"""Which fix a type checker's new error is about: the fix it's blamed on, in a fixed copy of a file.

The fix whose name the error's expression reads: an argument a checker names (mypy's `Argument
"how" to "concat"`, `Argument 2 to "f"`, Pyright's `parameter "time_unit"`), passed as a bare name
in a call on the error's line, is blamed on that name's fix before it in its scope, not on the fix
of the name the line binds (`result = pl.concat(items, how=_how)`, `_how: str` the cause). Else the
fix on its line, preferring one whose name its message quotes; else the nearest fix before it in
its scope of a name its line or its message has, one whose annotation holds a type the message
quotes first (`params: dict[str, int | float]` for `target has type "int | float"`, over the
`name: str` before it on the line `params[name] = param`); else the module's last fix of such a
name (a global it reads).
"""

import ast
import re
from collections.abc import Sequence
from typing import Final, NamedTuple


class Complaint(NamedTuple):
    """One type checker error: its file (relative to the checkout), its line, and its message."""

    path: str
    line: int
    message: str


class Fix(NamedTuple):
    """One fix `--format=json` reports: where, the name, its annotation, and what decided it."""

    path: str
    line: int
    name: str
    annotation: str
    kinds: str  # its mechanisms, joined by `+`
    unsafe: bool
    likely: bool = False  # a guess `--likely` applies
    imports: tuple[str, ...] = ()  # the import statements it adds


class Fixed(NamedTuple):
    """A fixed file: its lines, each's original line, those a fix wrote, and each original line's scope."""

    lines: list[str]
    origins: list[int]
    edited: frozenset[int]
    scopes: list[int]


_QUOTED: Final = re.compile(r"""["'`]([A-Za-z_]\w*)["'`]""")
_NAME: Final = re.compile(r"[A-Za-z_]\w*")
_TYPES: Final = re.compile(r'"([^"]+)"')  # the types a checker's message quotes (`has type "int | float"`)
# The argument an error is about, and the function it's passed to (`None`: any call on the line):
# mypy's by keyword or position (from 1), Pyright's by its parameter, passed by keyword.
_ARGUMENTS: Final = (
    re.compile(r'^Argument "(?P<keyword>\w+)" to "(?P<function>[\w.]+)"'),
    re.compile(r'^Argument (?P<position>\d+) to "(?P<function>[\w.]+)"'),
    re.compile(r'cannot be assigned to parameter "(?P<keyword>\w+)"'),
)


def scopes(source: str) -> list[int]:
    """Map each line of a file to the function, lambda or class it's in.

    Returns:
      The first line of each line's innermost one (0: the module), the first at index 1; all 0 if
      the file doesn't parse.

    """
    found: list[int] = [0] * (source.count("\n") + 2)
    try:
        tree: ast.Module = ast.parse(source)
    except SyntaxError:
        return found
    node: ast.AST
    for node in ast.walk(tree):  # breadth first: an inner scope overwrites its outer one
        if isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef | ast.Lambda | ast.ClassDef):
            line: int
            for line in range(node.lineno, (node.end_lineno or node.lineno) + 1):
                found[line] = node.lineno
    return found


def blamed(complaint: Complaint, file: Fixed, fixes: list[Fix]) -> Fix | None:
    """Return the fix a new error is about, if one can be told (see the module's docstring).

    Returns:
      The fix, or None.

    """
    origin: int = file.origins[complaint.line] if complaint.line < len(file.origins) else 0
    text: str = file.lines[complaint.line - 1] if complaint.line <= len(file.lines) else ""
    scope: int = file.scopes[origin] if origin < len(file.scopes) else -1
    read: str | None = argument(complaint, file.lines)
    passed: list[Fix] = [fix for fix in fixes if fix.name == read and fix.line < len(file.scopes)]
    earlier: list[Fix] = [fix for fix in passed if fix.line < origin and file.scopes[fix.line] == scope] or [
        fix for fix in passed if not file.scopes[fix.line]
    ]
    if earlier:
        return max(earlier, key=lambda fix: fix.line)
    names: set[str] = set(_QUOTED.findall(complaint.message)) | set(_NAME.findall(text))
    here: list[Fix] = sorted(
        (fix for fix in fixes if fix.line == origin),
        key=lambda fix: fix.name not in names,
    )
    if here:
        return here[0]
    named: list[Fix] = [fix for fix in fixes if fix.name in names and fix.line < len(file.scopes)]
    candidates: list[Fix] = [
        fix for fix in named if fix.line < origin and file.scopes[fix.line] == scope
    ] or [fix for fix in named if not file.scopes[fix.line]]
    quoted: list[str] = _TYPES.findall(complaint.message)
    return (
        max(candidates, key=lambda fix: (any(each in fix.annotation for each in quoted), fix.line))
        if candidates
        else None
    )


def argument(complaint: Complaint, lines: Sequence[str]) -> str | None:
    """Name what an error about an argument reads: the bare name passed as it, in a call on its line.

    `lines`: the fixed file's. The innermost such call, to the function the message names (by its
    last part: `"DataFrame.join"`, `join`), or any where it names none (Pyright's `__init__` is the
    class's call).

    Returns:
      The name; `None` where the message names no argument, no call on the line passes it, or it
      isn't passed as a bare name.

    """
    matches: list[re.Match[str] | None] = [pattern.search(complaint.message) for pattern in _ARGUMENTS]
    found: re.Match[str] | None
    if (found := next((each for each in matches if each is not None), None)) is None:
        return None
    named: dict[str, str | None] = found.groupdict()
    function: str | None = (named.get("function") or "").rpartition(".")[2] or None
    try:
        tree: ast.Module = ast.parse("\n".join(lines))
    except SyntaxError:
        return None
    calls: list[ast.Call] = sorted(
        (
            node
            for node in ast.walk(tree)
            if isinstance(node, ast.Call)
            and node.lineno <= complaint.line <= (node.end_lineno or node.lineno)
            and function in {None, "__init__", _called(node)}
        ),
        key=lambda call: (call.end_lineno or call.lineno) - call.lineno,
    )
    call: ast.Call
    passed: ast.expr | None
    for call in calls:
        if (passed := _passed(call, named.get("keyword"), named.get("position"))) is not None:
            return passed.id if isinstance(passed, ast.Name) else None
    return None


def _called(call: ast.Call) -> str | None:
    """Name the function a call calls, by its last part: `f`, `pl.concat`'s `concat`.

    Returns:
      It; `None` for any other callee (a call's result, a subscript).

    """
    name: str
    match call.func:
        case ast.Name(id=name) | ast.Attribute(attr=name):
            return name
        case _:
            return None


def _passed(call: ast.Call, keyword: str | None, position: str | None) -> ast.expr | None:
    """Find the argument a call passes by `keyword`, or at `position` (from 1, as text).

    Returns:
      Its expression; `None` where the call passes none such, or unpacks what comes before it.

    """
    if keyword is not None:
        return next((each.value for each in call.keywords if each.arg == keyword), None)
    index: int = int(position or 0) - 1
    before: list[ast.expr] = call.args[: index + 1]
    if not 0 <= index < len(call.args) or any(isinstance(each, ast.Starred) for each in before):
        return None
    return call.args[index]
