"""Hold what a run binds to the annotations its source declares: `python -m constricter.trace --check`.

A `Witness` records as a `Recorder` does. As a statement of a recorded function ends, each name it
bound that the function declares (a parameter's annotation, or a local's `name: T`) is held to that
annotation; as the function returns, or a generator is suspended, each annotated parameter is
(not a `*args`' or a `**kwargs`'), and what it returns to its `-> T` (not a generator's or a
coroutine's). An annotation is
evaluated where its function runs, once: its module's names and the frame's, then the names the
module imports for type checking alone, imported for it.

`holds` says whether a value is what an annotation names: an instance of its class, or of one of a
union's. A builtin container is held to its annotation's arguments too, by its first elements
(`_elements`); any other subscripted class to the class alone; a protocol `isinstance` can't check
to its members' names. It can't tell (`None`) of an annotation that can't be evaluated there, a
type variable with no bound, a value that's a test's mock, a `SimpleNamespace`, an in-memory file
where `io`'s or `typing`'s file class is named (`_in_memory`) or of a class a test module defines
(`_stand_in`; a package's `pytest` plugin module is one), and of an annotation that names such a
class: a module's name a test has patched, as the annotation was evaluated. `typing`'s file
classes, which nothing is an instance of, take any value that reads, writes and closes. A class
made again, by a function at each call or by a module imported anew, is the annotation's class
where its module and its qualified name are (`_redefined`).

Each process counts, for each binding and annotation, how many times the value fit, didn't, and
couldn't be told (`FIT`, `DIFFER`, `UNKNOWN`), `_MOST` times at most, and writes them beside its
trace; `report` reads them all and lists each binding a value differed from.
"""

import ast
import collections
import collections.abc
import contextlib
import io
import itertools
import json
import types
import typing
from collections.abc import Iterable, Iterator, Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from types import CodeType, FrameType
from typing import Final, TypeAlias, cast
from unittest import mock

from constricter import recording
from constricter.overrides import override

CODE: Final = "LVA016"  # what `report` lists a differing binding under
FIT: Final = 0
DIFFER: Final = 1
UNKNOWN: Final = 2
VERDICTS: Final = ".verdicts"  # the suffix of what a process writes its verdicts to, beside its trace
_MOST: Final = 50  # how many times one binding is judged against one annotation
_TOLD: Final = 3  # how many of a binding's differing values are told of, the first
# What an annotation's class takes besides its own instances: a number's narrower numbers.
_TAKEN: Final = {
    float: (int, float),
    complex: (int, float, complex),
}
# What `typing`'s file classes, which nothing is an instance of, take: a value that reads, writes
# and closes (`tempfile.NamedTemporaryFile`'s wrapper, which is no `io.IOBase`); see `_file_class`.
_FILE_METHODS: Final = ("read", "write", "close")
# An in-memory file: a test's stand-in for the file an annotation names (`open`'s `TextIOWrapper`,
# `typing.IO`).
_IN_MEMORY: Final = (io.StringIO, io.BytesIO)
_FILE_MODULES: Final = frozenset({"io", "_io", "typing"})
UNSET: Final = object()  # an annotation that couldn't be evaluated
# What a test passes in a value's place: a mock, and `mock.sentinel`'s named objects.
_STAND_INS: Final = (mock.NonCallableMock, type(cast("object", mock.sentinel.witness)))
_FIRST: Final = 100  # how many of an ordered container's elements are held to its annotation's arguments
# The containers read without running anything of the value's own: these classes themselves, no subclass.
_SETS: Final = (set, frozenset)
_SEQUENCES: Final = (list, collections.deque)
_MAPPINGS: Final = (dict, collections.defaultdict, collections.OrderedDict)
_TUPLES: Final = (tuple,)
_PAIR: Final = 2  # a mapping's arguments: its keys' type and its values'
_ALIASED: Final = "__value__"  # where a `type` statement's alias keeps what it names
_MEMBERS: Final = "__protocol_attrs__"  # where a protocol keeps its members' names (Python 3.12)
_PROTOCOL: Final = "_is_protocol"  # what `typing` marks a protocol class with
# What `typing` reads a protocol's members' names with, where it has it.
_attributes: Final = cast(
    "collections.abc.Callable[[type], set[str]] | None",
    getattr(typing, "_get_protocol_attrs", None),
)
# A test module's name, by any of its parts: pytest's and unittest's ways of naming them, and a
# package's pytest plugin (`pdm.pytest`), whose classes stand in for the package's own.
_TESTS: Final = frozenset({"test", "tests", "testing", "conftest", "pytest"})
_CALLABLE: Final = collections.abc.Callable
# What makes a union: `X | Y`, and `Union[X, Y]` where that's another thing (before Python 3.14).
_UNIONS: Final = frozenset({types.UnionType, cast("object", vars(typing)["Union"])})
_GUARD: Final = "TYPE_CHECKING"  # what a module tests to import a name for type checking alone
_BLOCKS: Final = (ast.stmt, ast.excepthandler, ast.match_case)  # what holds statements
# A binding and its annotation: its file's path, the line and column it's bound at, its name, the text.
Key: TypeAlias = tuple[str, int, int, str, str]
_Judged: TypeAlias = list[str | int | list[int] | list[str]]  # a key, its counts, what differed
_Counted: TypeAlias = tuple[list[int], list[str]]  # a key's counts in every process, and what differed


def holds(value: object, hint: object) -> bool | None:
    """Check whether `value` is what the evaluated annotation `hint` says.

    Returns:
      Whether it is; `None` where that can't be told.

    """
    if hint is typing.Any or hint is object:
        return True
    if isinstance(value, _STAND_INS):  # a test's stand-in: it says nothing of the annotation
        return None
    if hint is None or hint is types.NoneType:
        return value is None
    return _held(value, hint, typing.get_origin(hint), typing.get_args(hint))


def _held(value: object, hint: object, origin: object, args: tuple[object, ...]) -> bool | None:
    """Check `value` against `hint`, by what it subscripts (`origin`: `None` for no subscript) with `args`.

    Returns:
      As `holds` does.

    """
    if origin in _UNIONS:
        found: list[bool | None] = [holds(value, each) for each in args]
        return True if True in found else None if None in found else False
    if origin is typing.Annotated or origin is typing.Final or origin is typing.ClassVar:
        return holds(value, args[0]) if args else None
    if origin is typing.Literal:
        return value in args
    if origin is type:
        return isinstance(value, type)
    if origin is _CALLABLE:
        return callable(value)
    found_class: bool | None = _instance(value, hint if origin is None else origin)
    return _elements(value, origin, args) if found_class and origin is not None else found_class


def _elements(value: object, origin: object, args: tuple[object, ...]) -> bool | None:
    """Check a builtin container's elements against its annotation's arguments, `value` being of its class.

    Its first `_FIRST`, in its order; a set's every one, whose order is no two runs'. A tuple's
    parts one by one, where the annotation has them so. Not another class's (a subclass may run its
    own code as it's read), nor one whose arguments aren't its elements' types.

    Returns:
      Whether they all are; `None` where one can't be told and none isn't, `True` for a container
      this doesn't read.

    """
    found: list[bool | None]
    if (
        type(value) in _TUPLES and origin is tuple and args[-1:] != (Ellipsis,)
    ):  # `tuple[()]` has no arguments
        if len(cast("tuple[object, ...]", value)) != len(args):
            return False
        found = list(itertools.starmap(holds, zip(cast("tuple[object, ...]", value), args, strict=True)))
    elif type(value) in _MAPPINGS and len(args) == _PAIR:
        found = [
            holds(each, arg)
            for pair in itertools.islice(cast("dict[object, object]", value).items(), _FIRST)
            for each, arg in zip(pair, args, strict=True)
        ]
    elif (
        (type(value) in _SEQUENCES or type(value) in _SETS or type(value) in _TUPLES)
        and args
        and args[1:] in {(), (Ellipsis,)}
    ):
        most: int = len(cast("collections.abc.Sized", value)) if type(value) in _SETS else _FIRST
        found = [
            holds(each, args[0])
            for each in itertools.islice(cast("collections.abc.Iterable[object]", value), most)
        ]
    else:
        return True
    return False if False in found else None if None in found else True


def _stood_for(hint: object) -> object:
    """Find what a type variable, a `type` statement's alias or a `NewType` stands for.

    Returns:
      Its bound (`None`: it has none), what it names, or its supertype; `UNSET` for anything else.

    """
    if isinstance(hint, typing.TypeVar):
        return cast("object", hint.__bound__)
    if isinstance(hint, typing.NewType):
        return cast("object", hint.__supertype__)
    return cast("object", getattr(hint, _ALIASED, UNSET))


def _instance(value: object, hint: object) -> bool | None:
    """Check whether `value` is an instance of what `hint` names, itself no subscript or union.

    Returns:
      Whether it is; `None` where that can't be told.

    """
    if _stood_for(hint) is not UNSET:
        return None if _stood_for(hint) is None else holds(value, _stood_for(hint))
    if typing.is_typeddict(hint):
        return isinstance(value, dict)
    if _file_class(hint):
        return all(hasattr(value, name) for name in _FILE_METHODS)
    if not isinstance(hint, type):
        return None
    fit: bool | None
    try:
        fit = isinstance(value, _TAKEN.get(hint, hint)) or _redefined(type(value), hint)
    except TypeError:  # a protocol that isn't checked at run time
        fit = _membered(value, hint)
    return fit if fit is not False or not (_stand_in(type(value)) or _in_memory(type(value), hint)) else None


def _membered(value: object, hint: type) -> bool | None:
    """Look for a protocol's members on `value`, by name: what `isinstance` asks of a checkable one.

    Returns:
      Whether it has them all; `None` for a class that isn't a protocol, or whose members can't be
      read.

    """
    members: set[str] | frozenset[str] | None = cast(
        "set[str] | frozenset[str] | None",
        getattr(hint, _MEMBERS, None),
    )
    if members is None and _attributes is not None and getattr(hint, _PROTOCOL, False):
        members = _attributes(hint)  # before Python 3.12, which keeps them on the class
    return None if members is None else all(hasattr(value, name) for name in members)


def _redefined(kind: type, hint: type) -> bool:
    """Check whether `kind` or a base of it is `hint` made again: by a function, or a module imported anew.

    Returns:
      Whether one has `hint`'s module and qualified name.

    """
    return any(
        (base.__module__, base.__qualname__) == (hint.__module__, hint.__qualname__) for base in kind.__mro__
    )


def _stand_in(kind: type) -> bool:
    """Check whether `kind` is a test's stand-in, which says nothing of the annotation.

    Returns:
      Whether it's `SimpleNamespace`, or a test module's (`_testing`).

    """
    return kind is types.SimpleNamespace or _testing(kind.__module__)


def _file_class(hint: object) -> bool:
    """Check whether `hint` is one of `typing`'s file classes: `IO`, `TextIO` or `BinaryIO`.

    Returns:
      Whether it is.

    """
    return hint is typing.IO or hint is typing.TextIO or hint is typing.BinaryIO


def _in_memory(kind: type, hint: type) -> bool:
    """Check whether `kind` is an in-memory file held to a file class: a test's stand-in for the file.

    Returns:
      Whether it's a `StringIO` or `BytesIO` and `hint` is `io`'s or `typing`'s.

    """
    return issubclass(kind, _IN_MEMORY) and hint.__module__ in _FILE_MODULES


def _testing(module: str) -> bool:
    # Whether a part of a module's name is a test package's, or a test file's (`test_x`, `x_test`).
    return any(
        part in _TESTS or part.startswith("test_") or part.endswith("_test") for part in module.split(".")
    )


def patched(hint: object, module: str) -> bool:
    """Check whether an annotation in `module` names a test's class: a name of the module's a test patched.

    Returns:
      Whether it does, `module` being no test module, whose own annotations name its classes.

    """
    return isinstance(hint, type) and _testing(hint.__module__) and not _testing(module)


def fits(value: object, hint: object) -> bool | None:
    """Hold `value` to `hint`, whatever its class raises of being asked: nothing of it reaches the run.

    Returns:
      As `holds` does; `None` for a `hint` that couldn't be evaluated.

    """
    try:
        return None if hint is UNSET else holds(value, hint)
    except Exception:  # ruff: ignore[blind-except]  # pylint: disable=broad-exception-caught
        return None


def kind_of(value: object) -> str:
    """Name `value`'s class, as the trace spells it where it can, whatever the value raises of it.

    Returns:
      It: `module:qualified.name`; `?` where it can't be read.

    """
    try:
        named: str = f"{type(value).__module__}:{type(value).__qualname__}"
    except Exception:  # ruff: ignore[blind-except]  # pylint: disable=broad-exception-caught
        return "?"
    return named


def module_of(frame: FrameType) -> str:
    """Name the module `frame` runs in.

    Returns:
      Its name; `""` where its globals have none.

    """
    return str(cast("object", frame.f_globals.get("__name__", "")))


def read(text: object, scope: dict[str, object], local: dict[str, object]) -> object:
    """Evaluate `text`, an annotation, among `scope`'s and `local`'s names; a quoted one's text too.

    Returns:
      What it names; `text` itself if it isn't text.

    """
    if not isinstance(text, str):
        return text
    return read(_named(text, scope, local), scope, local)


def _named(text: str, scope: dict[str, object], local: dict[str, object]) -> object:
    # What the expression `text` gives there.
    return cast(
        "object",
        eval(text, scope, local),  # ruff: ignore[suspicious-eval-usage]  # pylint: disable=eval-used
    )


@dataclass(frozen=True)
class _Declared:
    """What a function declares: its names' annotations, where each is bound, and its return's."""

    names: Mapping[str, str]  # each annotated parameter's and local's annotation, as written
    parameters: Mapping[str, tuple[int, int]]  # each annotated parameter's line and column
    columns: Mapping[tuple[int, str], int]  # each store's column, by its line and name
    returns: str | None  # the annotation after `->`
    guarded: tuple[str, ...]  # the module's imports for type checking alone, as statements


def _declarations(tree: ast.Module) -> dict[int, _Declared]:
    """Read what each function of a module declares.

    Returns:
      Each one's, by its first line (its first decorator's), as a recorder's plans are.

    """
    guarded: tuple[str, ...] = tuple(
        ast.unparse(each)
        for stmt in tree.body
        if isinstance(stmt, ast.If) and ast.unparse(stmt.test).rsplit(".", 1)[-1] == _GUARD
        for each in stmt.body
        if isinstance(each, ast.Import | ast.ImportFrom)
    )
    return {
        min([node.lineno, *(decorator.lineno for decorator in node.decorator_list)]): _declared(node, guarded)
        for node in ast.walk(tree)
        if isinstance(node, recording.Def)
    }


def _declared(function: recording.Def, guarded: tuple[str, ...]) -> _Declared:
    """Read what one function declares: its parameters' annotations, then its own statements'.

    Returns:
      It.

    """
    given: ast.arguments = function.args
    names: dict[str, str] = {}
    parameters: dict[str, tuple[int, int]] = {}
    columns: dict[tuple[int, str], int] = {}
    arg: ast.arg
    for arg in (*given.posonlyargs, *given.args, *given.kwonlyargs):
        if arg.annotation is not None:
            names[arg.arg] = _written(arg.annotation)
            parameters[arg.arg] = (arg.lineno, arg.col_offset + 1)
    statement: ast.stmt
    for statement in recording.statements(function):
        if isinstance(statement, ast.AnnAssign) and isinstance(statement.target, ast.Name):
            _ = names.setdefault(statement.target.id, _written(statement.annotation))
        node: ast.AST
        for node in _evaluated(statement):
            if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Store):
                _ = columns.setdefault((node.lineno, node.id), node.col_offset + 1)
    returns: str | None = None if function.returns is None else _written(function.returns)
    return _Declared(names, parameters, columns, returns, guarded)


def _written(annotation: ast.expr) -> str:
    """Write an annotation as its source has it: a quoted one's text.

    Returns:
      It.

    """
    quoted: bool = isinstance(annotation, ast.Constant) and isinstance(annotation.value, str)
    return cast("str", cast("ast.Constant", annotation).value) if quoted else ast.unparse(annotation)


def _evaluated(node: ast.AST) -> Iterator[ast.AST]:
    """Walk what a statement evaluates itself: not the statements under it, nor another scope's.

    Yields:
      Each node under `node`.

    """
    child: ast.AST
    for child in ast.iter_child_nodes(node):
        if not isinstance(child, (*_BLOCKS, *recording.SCOPES)):
            yield child
            yield from _evaluated(child)


class Witness(recording.Recorder):
    """A recorder that holds what a function binds, and returns, to what it declares of them."""

    def __init__(self, root: Path) -> None:
        """Record the functions of the files under `root`, and judge what they declare."""
        super().__init__(root)
        self.hints: dict[Key, object] = {}  # each annotation, evaluated; `UNSET`: it can't be
        self.verdicts: dict[Key, list[int]] = {}  # each key's counts: fit, differing, unknown
        self.differed: dict[Key, list[str]] = {}  # the first values that differed, as the trace spells them
        self.read: dict[str, dict[int, _Declared]] = {}  # each file's functions' declarations
        # What each function declares, by its id, kept with it (`None`: nothing).
        self.declared: dict[int, tuple[recording.Function, _Declared | None]] = {}

    @override
    def ended(self, frame: FrameType, function: recording.Function) -> None:
        """Judge what the statement `frame` was in bound, as it ends; then note it."""
        declared: _Declared | None = self._declared(frame, function)
        pending: tuple[CodeType, recording.Statement] | None = self.pending.get(id(frame))
        if declared is not None and pending is not None and pending[0] is frame.f_code:
            path: str = function.file.path.as_posix()
            line: int
            name: str
            for line, name in pending[1].stores:
                if name in declared.names and name in frame.f_locals:
                    key: Key = (path, line, declared.columns.get((line, name), 1), name, declared.names[name])
                    self._weighed(frame, key, cast("object", frame.f_locals[name]), declared)
        super().ended(frame, function)

    @override
    def left(
        self,
        frame: FrameType,
        *,
        finished: bool = False,
        returned: bool = False,
        value: object = None,
    ) -> bool:
        """Judge `frame`'s parameters and what it returns, as its function returns; then note them.

        Returns:
          Whether `frame`'s function is one to record, still.

        """
        function: recording.Function | None = self._function(frame)
        suspends: bool = bool(frame.f_code.co_flags & recording.SUSPENDS)
        declared: _Declared | None = None if function is None else self._declared(frame, function)
        if function is not None and declared is not None:
            path: str = function.file.path.as_posix()
            name: str
            place: tuple[int, int]
            for name, place in declared.parameters.items():
                if name in frame.f_locals:
                    key: Key = (path, *place, name, declared.names[name])
                    self._weighed(frame, key, cast("object", frame.f_locals[name]), declared)
            if returned and not suspends and declared.returns is not None:
                at: Key = (path, frame.f_lineno, 1, recording.RETURN, declared.returns)
                self._weighed(frame, at, value, declared)
        return super().left(frame, finished=finished, returned=returned, value=value)

    def _declared(self, frame: FrameType, function: recording.Function) -> _Declared | None:
        """Find what `frame`'s function declares, read once a function, its file once.

        Returns:
          It; `None` for a function that declares nothing, or whose file can't be read again.

        """
        if id(function) not in self.declared:
            path: str
            if (path := function.file.path.as_posix()) not in self.read:
                try:
                    self.read[path] = _declarations(ast.parse((self.root / function.file.path).read_bytes()))
                except (OSError, SyntaxError, ValueError):
                    self.read[path] = {}
            found: _Declared | None = self.read[path].get(frame.f_code.co_firstlineno)
            told: bool = found is not None and bool(found.names or found.returns)
            self.declared[id(function)] = (function, found if told else None)
        return self.declared[id(function)][1]

    def _weighed(self, frame: FrameType, key: Key, value: object, declared: _Declared) -> None:
        """Hold `value`, what `key`'s name is bound to in `frame`, to its annotation: count the verdict."""
        if sum(self.verdicts.get(key, ())) >= _MOST:
            return
        if key not in self.hints:
            self.hints[key] = evaluated(key[4], frame, declared.guarded)
        found: bool | None = fits(value, self.hints[key])
        if patched(self.hints[key], module_of(frame)):  # evaluated again once the test's done
            found = None
            del self.hints[key]
        self.verdicts.setdefault(key, [0, 0, 0])[UNKNOWN if found is None else FIT if found else DIFFER] += 1
        told: list[str] = self.differed.setdefault(key, [])
        if found is False and len(told) < _TOLD and seen(value) not in told:
            told.append(seen(value))

    @override
    def write(self, output: Path) -> None:
        """Write what was recorded to `output`, and this process's verdicts beside it."""
        super().write(output)
        _ = output.with_suffix(VERDICTS).write_text(json.dumps(self.judged()), encoding="utf-8")

    def judged(self) -> list[_Judged]:
        """List this process's verdicts, as they're written.

        Returns:
          Each key, then its counts, then what differed.

        """
        return [[*key, counts, self.differed.get(key, [])] for key, counts in self.verdicts.items()]


def evaluated(text: str, frame: FrameType, guarded: Sequence[str]) -> object:
    """Evaluate an annotation where its function runs, with `guarded` imported for it if a name's missing.

    Returns:
      What it names, or `UNSET` where it can't be evaluated there.

    """
    try:
        return read(text, dict(frame.f_globals), dict(frame.f_locals))
    except NameError:
        pass
    except Exception:  # ruff: ignore[blind-except]  # pylint: disable=broad-exception-caught
        return UNSET
    try:
        return read(text, _imported(dict(frame.f_globals), guarded), dict(frame.f_locals))
    except Exception:  # ruff: ignore[blind-except]  # pylint: disable=broad-exception-caught
        return UNSET


def _imported(scope: dict[str, object], imports: Sequence[str]) -> dict[str, object]:
    """Run those of `imports` that can be among `scope`'s names, a copy of a module's.

    Returns:
      `scope`.

    """
    statement: str
    for statement in imports:
        # A name that can't be imported is one the annotation may not need.
        with contextlib.suppress(Exception):
            exec(statement, scope)  # ruff: ignore[exec-builtin]  # pylint: disable=exec-used
    return scope


def seen(value: object) -> str:
    """Spell `value`'s type as a report gives it: as the trace does where it can, else its class.

    Returns:
      It, a class by its module and name (`pkg.mod.Name`).

    """
    try:
        spelled: str | None = recording.spelled(value)
    except Exception:  # ruff: ignore[blind-except]  # pylint: disable=broad-exception-caught
        spelled = None
    known: bool = spelled is not None and spelled != recording.UNKNOWN
    return (cast("str", spelled) if known else kind_of(value)).replace(recording.SEPARATOR, ".")


def gathered(parts: Path, own: Iterable[_Judged]) -> dict[Key, _Counted]:
    """Join a run's processes' verdicts: `own`, and what the others wrote under `parts`.

    Returns:
      Each key's counts in them all, and the first values that differed; not a part that can't be
      read (a process killed as it wrote).

    """
    found: dict[Key, _Counted] = {}
    every: list[_Judged] = list(own)
    path: Path
    for path in sorted(parts.glob(f"*{VERDICTS}")):
        try:
            every += cast("list[_Judged]", json.loads(path.read_text(encoding="utf-8")))
        except ValueError:
            continue
    judged: _Judged
    for judged in every:
        key: Key = cast("Key", tuple(judged[:5]))
        counts: list[int]
        told: list[str]
        counts, told = found.setdefault(key, ([0, 0, 0], []))
        counts[:] = [had + more for had, more in zip(counts, cast("list[int]", judged[5]), strict=True)]
        told += [each for each in cast("list[str]", judged[6]) if each not in told and len(told) < _TOLD]
    return found


def report(found: Mapping[Key, tuple[Sequence[int], Sequence[str]]]) -> list[str]:
    """List each binding a run's value differed from its annotation, as `constricter` lists an offence.

    Returns:
      A line each, in the files' order, then one counting what was held.

    """
    lines: list[str] = []
    key: Key
    for key in sorted(found):
        if found[key][0][DIFFER]:
            kinds: str = ", ".join(f"`{each}`" for each in found[key][1])
            what: str = (
                f"a function annotated to return `{key[4]}` returned"
                if key[3] == recording.RETURN
                else f"'{key[3]}', annotated `{key[4]}`, was bound to"
            )
            lines.append(f"{key[0]}:{key[1]}:{key[2]}: error: {CODE} {what} {kinds} in a traced run")
    untold: int = sum(1 for counts, _ in found.values() if not counts[FIT] and not counts[DIFFER])
    held: str = f"{len(found)} annotated bindings held to a run's values"
    return [*lines, f"{held}: {len(lines)} differed, {untold} couldn't be told"]
