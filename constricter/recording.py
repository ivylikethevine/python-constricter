# SPDX-License-Identifier: MIT
"""What `python -m constricter.trace` records: the types a run binds its functions' locals to.

A `Recorder` is told each line a function of a file under its root arrives at, and notes the type
of each name the statement it left binds: an assignment's, a loop's or a `with`'s targets, a
`:=`'s. A statement that ends 20 times with nothing new is no longer looked at, nor a function that
returns 20 times so; a statement an exception ends says nothing. What it found is a trace: each
file by its SHA-256, each binding by its line and name, so a file edited since has none, and a copy
of it has them all.

A value is spelled as its annotation: `None`, a builtin scalar, a builtin container or one of
`collections`' by its first elements' types (`list[int]`, `dict[str, Row | None]`), a tuple by its
parts' one type (`tuple[int, ...]`) or part by part, a class as `type[C]`, anything else by its
class, written `module:Class` (`module:Outer.Inner`, for one defined in another). A generic class's
instance has its arguments where it was made with them (`Box[int]()`), or where the class is a
builtin container of its own type variables (`class Stack(list[T])`), by its elements. What can't
be spelled is `?`, which leaves its name untyped: a container of more than three types or nested
past two levels, a mock, a class defined in a function. An empty container says nothing. None of
a value's own code runs to spell it: what it holds is read as it's stored, not asked for.
"""

import ast
import builtins
import collections
import hashlib
import inspect
import itertools
import json
import sys
from collections.abc import Iterable, Iterator, Mapping
from dataclasses import dataclass, field
from pathlib import Path
from types import CodeType, FrameType, ModuleType
from typing import Final, TypeAlias, TypedDict, TypeVar, cast, get_args, get_origin

VERSION: Final = 2  # the file's format
UNKNOWN: Final = "?"  # a value that can't be spelled
NONE: Final = "None"
SEPARATOR: Final = ":"  # between a class's module and its name
_DOT: Final = "."  # between a class's name and that of one defined in it
_SEQUENCES: Final = frozenset({list, set, frozenset, collections.deque, collections.Counter})
_TUPLES: Final = frozenset({tuple})
_MAPPINGS: Final = frozenset({dict, collections.defaultdict, collections.OrderedDict})
# The classes a path is on one platform, as the one written for any.
_PATHS: Final = {
    "PosixPath": "Path",
    "WindowsPath": "Path",
    "PurePosixPath": "PurePath",
    "PureWindowsPath": "PurePath",
}
_PATHLIB: Final = "pathlib"
_BUILTINS: Final = "builtins"
_MOCK: Final = "unittest.mock"
_SAMPLE: Final = 20  # how many of a container's elements are looked at
_DEPTH: Final = 2  # how deep a container's elements are spelled
_MEMBERS: Final = 3  # how many types a container's elements may have
_LENGTH: Final = 4  # the longest tuple spelled part by part
_IDLE: Final = 20  # how many times with nothing new end a statement's recording, or a function's
_INSTALLED: Final = "site-packages"
_MODULE: Final = "<module>"  # the name of a module body's code
# A function that returns to its caller more than once, each a `return` to `sys.settrace`: `inspect`'s
# `CO_GENERATOR`, `CO_COROUTINE`, `CO_ITERABLE_COROUTINE` and `CO_ASYNC_GENERATOR`.
_SUSPENDS: Final = 0x20 | 0x80 | 0x100 | 0x200
_Def: TypeAlias = ast.FunctionDef | ast.AsyncFunctionDef
SCOPES: Final = (  # what has names of its own
    ast.FunctionDef,
    ast.AsyncFunctionDef,
    ast.ClassDef,
    ast.Lambda,
    ast.ListComp,
    ast.SetComp,
    ast.DictComp,
    ast.GeneratorExp,
)
_BLOCKS: Final = (ast.stmt, ast.excepthandler, ast.match_case)  # what holds statements
_Held: TypeAlias = dict[int, dict[str, set[str]]]  # each binding's spellings, by its line and name
Bindings: TypeAlias = dict[str, dict[str, list[str]]]  # a file's, as they're written
_Form: TypeAlias = object  # what a generic class is declared with: an alias (`list[T]`), a type variable
_Member: TypeAlias = object  # what a module's name is, or a class's


class Entry(TypedDict):
    """A trace's file: its path under the root, and each binding's spellings by its line, then its name."""

    path: str
    bindings: Bindings


class Found(TypedDict):
    """A trace, as it's written.

    The format's version; each file by its SHA-256; and each recorded module's file's SHA-256, by
    the name the run knew it by (`__main__`, for what it ran).
    """

    version: int
    files: dict[str, Entry]
    modules: dict[str, str]


def spelled(value: object, depth: int = _DEPTH) -> str | None:
    """Spell `value`'s type as an annotation (see the module's docstring).

    Returns:
      It; `UNKNOWN` for one that can't be spelled; `None` for one that says nothing (an empty
      container, or one of them).

    """
    if value is None:
        return NONE
    if type(value) in _TUPLES:
        return _tuple(cast("tuple[object, ...]", value), depth)
    if type(value) in _SEQUENCES | _MAPPINGS:
        return _container(named(type(value)), _parts(value, type(value)), depth)
    if issubclass(type(value), type):  # not `isinstance`, which asks the value its `__class__`
        return UNKNOWN if named(cast("type", value)) == UNKNOWN else f"type[{named(cast('type', value))}]"
    return _instance(value, type(value), depth)


def _held(holder: object, name: str) -> _Member:
    """Read what a module or a class holds itself under `name`, as it's stored.

    Not by `getattr`, which a module's `__getattr__` answers with code of the run's own (a lazy
    import), and a class's bases too.

    Returns:
      It; `None` for a name it doesn't hold, or a `holder` that's neither.

    """
    if issubclass(type(holder), (ModuleType, type)):
        return cast("Mapping[str, object]", vars(holder)).get(name)
    return None


def _parts(value: object, kind: type) -> tuple[Iterable[object], ...]:
    """List the values each type argument of a container of class `kind` is spelled by.

    Returns:
      A sequence's elements; a mapping's keys, and its values.

    """
    if kind in _SEQUENCES:
        return (cast("Iterable[object]", value),)
    return (cast("Iterable[object]", value), cast("Mapping[object, object]", value).values())


def _instance(value: object, cls: type, depth: int) -> str | None:
    """Spell an instance by its class `cls`, a generic one with its arguments where they can be told.

    Returns:
      It (see `spelled`); a generic class bare where they can't.

    """
    text: str = named(cls)
    # What `Box[int]()` leaves on what it makes.
    made: _Form = cast("_Form", inspect.getattr_static(value, "__orig_class__", None))
    arguments: list[str] = [
        named(argument) if isinstance(argument, type) else UNKNOWN
        for argument in cast("tuple[_Form, ...]", get_args(made))
    ]
    if get_origin(made) is cls and UNKNOWN not in {text, *arguments}:
        return f"{text}[{', '.join(arguments)}]"
    declared: tuple[_Form, ...] = cast("tuple[_Form, ...]", _held(cls, "__parameters__") or ())
    base: _Form
    for base in cast("tuple[_Form, ...]", _held(cls, "__orig_bases__") or ()):
        kind: _Form = cast("_Form", get_origin(base))
        own: tuple[_Form, ...] = get_args(base)
        if (
            text != UNKNOWN
            and isinstance(kind, type)
            and kind in _SEQUENCES | _MAPPINGS
            and all(isinstance(each, TypeVar) for each in own)
            and declared in {(), own}
        ):
            return _container(text, _parts(value, kind), depth)
    return text


def named(cls: type) -> str:
    """Name a class as an annotation would: a builtin bare, another as `module:Class`.

    Returns:
      It; `UNKNOWN` for one no annotation can name (a function's, a nested one, a mock).

    """
    module: str = cls.__module__
    name: str = cls.__qualname__
    if module == _BUILTINS:
        return name if _held(builtins, name) is cls else UNKNOWN
    if module.startswith(_MOCK) or not all(part.isidentifier() for part in name.split(_DOT)):
        return UNKNOWN
    if _DOT in name and _reached(module, name) is not cls:  # a class in another, by another name
        return UNKNOWN
    if _held(collections, name) is cls:  # wherever it's defined
        return f"{collections.__name__}{SEPARATOR}{name}"
    if module.partition(".")[0] == _PATHLIB:
        return f"{_PATHLIB}{SEPARATOR}{_PATHS.get(name, name)}"
    # A private module's class, as the public one of its name has it (`_io`'s, in `io`).
    public: str = module.lstrip("_")
    return f"{public if _reached(public, name) is cls else module}{SEPARATOR}{name}"


def _reached(module: str, name: str) -> _Member:
    """Find what an imported module's `name` is: `Outer.Inner`, an attribute of its `Outer`.

    Returns:
      It, or `None`.

    """
    found: _Member = sys.modules.get(module)
    part: str
    for part in name.split(_DOT):
        found = _held(found, part)
    return found


def _joined(values: Iterable[object], depth: int) -> str | None:
    """Spell the types of the first of `values` as one type, a union of up to `_MEMBERS`.

    Returns:
      It; `UNKNOWN` for more types than that, or any that is; `None` for none, or any saying nothing.

    """
    found: set[str | None] = {spelled(value, depth) for value in itertools.islice(values, _SAMPLE)}
    if not found or None in found:
        return None
    types: list[str] = sorted(cast("set[str]", found), key=lambda text: (text == NONE, text))
    return UNKNOWN if UNKNOWN in types or len(types) > _MEMBERS else " | ".join(types)


def _container(kind: str, parts: tuple[Iterable[object], ...], depth: int) -> str | None:
    """Spell a container of the class spelled `kind` by each of its type arguments' values (`parts`).

    Returns:
      It (see `spelled`).

    """
    if not depth:
        return UNKNOWN
    arguments: list[str | None] = [_joined(part, depth - 1) for part in parts]
    if None in arguments:
        return None
    if UNKNOWN in arguments:
        return UNKNOWN
    return f"{kind}[{', '.join(cast('list[str]', arguments))}]"


def _tuple(value: tuple[object, ...], depth: int) -> str | None:
    """Spell a tuple: by its parts' one type, of any length, or part by part up to `_LENGTH` long.

    Returns:
      It (see `spelled`); nothing for an empty one, which any tuple's type takes.

    """
    if not value or not depth:
        return UNKNOWN if value else None
    parts: list[str | None] = [spelled(part, depth - 1) for part in value[:_SAMPLE]]
    if None in parts:
        return None
    if UNKNOWN in parts or (len(set(parts)) > 1 and len(value) > _LENGTH):
        return UNKNOWN
    spellings: list[str] = cast("list[str]", parts)
    return f"tuple[{spellings[0]}, ...]" if len(set(parts)) == 1 else f"tuple[{', '.join(spellings)}]"


@dataclass(eq=False)
class _Statement:
    """The names a statement binds, each with its line; and how many times in a row it added nothing."""

    stores: list[tuple[int, str]] = field(default_factory=list[tuple[int, str]])
    idle: int = 0


@dataclass
class _File:
    """A file under the root: its path there, its SHA-256, its functions' plans and what was noted."""

    path: Path
    digest: str
    plans: dict[int, dict[int, _Statement]]  # see `_plans`
    held: _Held = field(default_factory=dict[int, dict[str, set[str]]])


@dataclass
class _Function:
    """A function recorded: the statement each line is of, and how many returns in a row added nothing."""

    file: _File
    lines: dict[int, _Statement]
    idle: int = 0
    fresh: bool = False  # whether anything was added since it last returned


def _plans(tree: ast.Module) -> dict[int, dict[int, _Statement]]:
    """Plan each function of a module: the statement each of its lines is of, where it binds a name.

    Returns:
      Each function's lines' statements, by its first line (its first decorator's).

    """
    return {
        min([node.lineno, *(decorator.lineno for decorator in node.decorator_list)]): _planned(node)
        for node in ast.walk(tree)
        if isinstance(node, _Def)
    }


def _planned(function: _Def) -> dict[int, _Statement]:
    """Plan a function: its own statements that bind names, each under every line it evaluates on.

    A compound statement is what it evaluates itself (`for x in xs:`, not its body). Statements
    that share a line are one.

    Returns:
      Each line's statement.

    """
    lines: dict[int, _Statement] = {}
    statement: ast.stmt
    for statement in _statements(function):
        evaluated: list[ast.AST] = list(_evaluated(statement))
        stores: list[tuple[int, str]] = [
            (node.lineno, node.id)
            for node in evaluated
            if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Store)
        ]
        if stores:
            last: int = max(
                node.end_lineno or node.lineno for node in evaluated if isinstance(node, ast.expr)
            )
            planned: _Statement = lines.setdefault(statement.lineno, _Statement())
            planned.stores.extend(stores)
            line: int
            for line in range(statement.lineno, last + 1):
                _ = lines.setdefault(line, planned)
    return lines


def _statements(node: ast.AST) -> Iterator[ast.stmt]:
    """Walk the statements of a function's own scope, each before those under it.

    Yields:
      Each one: not a function's or a class's definition, nor what's in it.

    """
    child: ast.AST
    for child in ast.iter_child_nodes(node):
        if isinstance(child, ast.stmt) and not isinstance(child, SCOPES):
            yield child
        if isinstance(child, _BLOCKS) and not isinstance(child, SCOPES):
            yield from _statements(child)


def _evaluated(node: ast.AST) -> Iterator[ast.AST]:
    """Walk what a statement evaluates itself: not the statements under it, nor another scope's.

    Yields:
      Each node under `node`.

    """
    child: ast.AST
    for child in ast.iter_child_nodes(node):
        if not isinstance(child, (*_BLOCKS, *SCOPES)):
            yield child
            yield from _evaluated(child)


class Recorder:
    """Notes the types of the names each statement binds, told where each recorded function is."""

    def __init__(self, root: Path) -> None:
        """Record the functions of the files under `root`."""
        self.root: Path = root.resolve()
        # By the code object's id: two alike in two files are equal. None: not one to record.
        self.functions: dict[int, _Function | None] = {}
        self.codes: dict[int, CodeType] = {}  # each one seen, kept so its id stays its own
        self.files: dict[str, _File | None] = {}  # each file under the root that could be read
        self.modules: dict[str, str] = {}  # the SHA-256 of each module a recorded function is in
        # The statement each frame is in, if it binds a name, by the frame's id, with the frame's code.
        self.pending: dict[int, tuple[CodeType, _Statement]] = {}

    def wanted(self, frame: FrameType) -> bool:
        """Check whether `frame`'s function is one to record, still.

        Returns:
          Whether it is.

        """
        return self._function(frame) is not None

    def line(self, frame: FrameType) -> None:
        """Note what the statement `frame` was in bound, as it arrives at another's line."""
        function: _Function | None
        if (function := self._function(frame)) is None:
            return
        statement: _Statement | None = function.lines.get(frame.f_lineno)
        if self.pending.get(id(frame), (None, statement))[1] is not statement:
            self._note(frame, function)
        if statement is not None:
            self.pending[id(frame)] = (frame.f_code, statement)

    def left(self, frame: FrameType) -> None:
        """Note what `frame`'s last statement bound, as its function returns: not as it yields."""
        function: _Function | None = self._function(frame)
        if function is None or frame.f_code.co_flags & _SUSPENDS:
            return
        self._note(frame, function)
        function.idle = 0 if function.fresh else function.idle + 1
        function.fresh = False

    def raised(self, frame: FrameType) -> None:
        """Forget the statement `frame` was in: an exception ended it."""
        _ = self.pending.pop(id(frame), None)

    def _note(self, frame: FrameType, function: _Function) -> None:
        """Add the types of what the statement `frame` was in bound, and forget the statement."""
        code: CodeType | None
        statement: _Statement
        code, statement = self.pending.pop(id(frame), (None, _Statement()))
        if code is not frame.f_code or statement.idle >= _IDLE:  # another frame's, of this one's id
            return
        try:
            new: bool = _noted(function.file.held, statement.stores, frame.f_locals)
        except (AttributeError, LookupError, RuntimeError, TypeError, ValueError):
            # A container another thread changed, or a class that isn't one: its function isn't recorded.
            self.functions[id(code)] = None
            line: int
            name: str
            for line, name in (store for each in function.lines.values() for store in each.stores):
                _ = function.file.held.get(line, {}).pop(name, None)
            return
        statement.idle = 0 if new else statement.idle + 1
        function.fresh = function.fresh or new

    def _function(self, frame: FrameType) -> _Function | None:
        """Find `frame`'s function, if it's one to record: in a file under the root, binding a name.

        Returns:
          It, or `None`: also for one that returned `_IDLE` times with nothing new.

        """
        code: CodeType = frame.f_code
        if id(code) not in self.functions:
            self.codes[id(code)] = code
            if code.co_name == _MODULE:
                _ = self._file(code.co_filename)  # read as it's imported: its functions' calls needn't
            file: _File | None = None if code.co_name.startswith("<") else self._file(code.co_filename)
            lines: dict[int, _Statement] = {} if file is None else file.plans.get(code.co_firstlineno, {})
            self.functions[id(code)] = _Function(file, lines) if file is not None and lines else None
            if file is not None and lines:
                self.modules[str(frame.f_globals.get("__name__"))] = file.digest
        function: _Function | None = self.functions[id(code)]
        return None if function is None or function.idle >= _IDLE else function

    def _file(self, filename: str) -> _File | None:
        """Read the file `filename`, once.

        Returns:
          It, or `None` for a file elsewhere than under the root, installed there (`site-packages`),
          or that can't be read or parsed; or that can't be read now, and is asked for again: the
          program may forbid reading a file where this is called (blockbuster, in an event loop),
          and what it raises then mustn't reach it.

        """
        if filename not in self.files:
            try:
                self.files[filename] = self._under(filename)
            except Exception:  # ruff: ignore[blind-except]  # pylint: disable=broad-exception-caught
                return None
        return self.files[filename]

    def _under(self, filename: str) -> _File | None:
        # `_file`, read from disk: whatever the program raises of that.
        path: Path = Path(filename).resolve()
        under: Path | None = path.relative_to(self.root) if path.is_relative_to(self.root) else None
        return None if under is None or _INSTALLED in under.parts else _read(path, under)

    def found(self) -> Found:
        """Gather what was recorded, as the file holds it.

        Returns:
          The trace: a file's copies as one file, and only the modules it has something of.

        """
        files: dict[str, Entry] = merged(
            {
                "version": VERSION,
                "files": {file.digest: {"path": file.path.as_posix(), "bindings": _written(file.held)}},
                "modules": {},
            }
            for file in self.files.values()
            if file is not None and _written(file.held)
        )["files"]
        return {
            "version": VERSION,
            "files": files,
            "modules": {module: digest for module, digest in self.modules.items() if digest in files},
        }

    def write(self, output: Path) -> None:
        """Write what was recorded to `output`."""
        write(output, self.found())


def _written(held: _Held) -> Bindings:
    """Write a file's bindings as a trace holds them.

    Returns:
      Each one's spellings, sorted, by its line, then its name: not one with none.

    """
    return {
        str(line): {name: sorted(types) for name, types in names.items() if types}
        for line, names in held.items()
        if any(names.values())
    }


def merged(traces: Iterable[Found]) -> Found:
    """Join the traces of one run's processes.

    Returns:
      One trace: each binding with its spellings in them all, each file under the first path it has.

    """
    files: dict[str, Entry] = {}
    modules: dict[str, str] = {}
    found: Found
    for found in traces:
        modules.update(found["modules"])
        digest: str
        entry: Entry
        for digest, entry in found["files"].items():
            kept: Entry = files.setdefault(digest, {"path": entry["path"], "bindings": {}})
            line: str
            names: dict[str, list[str]]
            for line, names in entry["bindings"].items():
                held: dict[str, list[str]] = kept["bindings"].setdefault(line, {})
                held.update({name: sorted({*held.get(name, ()), *types}) for name, types in names.items()})
    return {"version": VERSION, "files": files, "modules": modules}


def write(output: Path, found: Found) -> None:
    """Write the trace `found` to `output`."""
    _ = output.write_text(json.dumps(found, sort_keys=True) + "\n", encoding="utf-8")


def _noted(held: _Held, stores: Iterable[tuple[int, str]], values: Mapping[str, object]) -> bool:
    """Add to `held` the types of the names of `stores` that a frame holds (`values`).

    Returns:
      Whether any is new.

    """
    new: bool = False
    line: int
    name: str
    for line, name in stores:
        if name in values:
            text: str | None = spelled(values[name])
            types: set[str] = held.setdefault(line, {}).setdefault(name, set())
            if text is not None and text not in types:
                types.add(text)
                new = True
    return new


def _read(path: Path, under: Path) -> _File | None:
    """Read the file at `path`, `under` the root: hashed as `--infer-from` will, and planned.

    Returns:
      It, or `None` for one that can't be read or parsed.

    """
    try:
        source: bytes = path.read_bytes()
    except OSError:
        return None
    try:
        plans: dict[int, dict[int, _Statement]] = _plans(ast.parse(source))
    except (SyntaxError, ValueError):
        return None
    return _File(under, hashlib.sha256(source).hexdigest(), plans)
