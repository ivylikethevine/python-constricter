# SPDX-License-Identifier: MIT
"""Record the types a run binds its functions' locals to, for `--fix --infer-from` to read.

  python -m constricter.trace [--output FILE] [--root DIR] (-m MODULE | SCRIPT) [ARG ...]

Runs the module or script as `python` would (`-m pytest`), and each time a function defined in a
file under DIR (default: the working directory; nothing installed there) returns or yields, notes
the type of each local it holds. At exit it writes them to FILE (default: `constricter-trace.json`)
by each file's SHA-256, so a file edited since has none, and a copy of it has them all.

A value is spelled as its annotation: `None`, a builtin scalar, a builtin container or one of
`collections`' by its first elements' types (`list[int]`, `dict[str, Row | None]`), a tuple by its
parts' one type (`tuple[int, ...]`) or part by part, a class as `type[C]`, anything else by its
class, written `module:Class`. What can't be spelled is `?`, which leaves its name untyped: a
container of more than three types or nested past two levels, a mock, a class defined in a function
or in another class. An empty container says nothing.

Only this thread and those `threading` starts are recorded, not a child process (pytest-xdist's
workers). A function that returns 20 times with nothing new is no longer looked at.
"""

import argparse
import builtins
import collections
import hashlib
import itertools
import json
import runpy
import sys
import threading
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass, field
from pathlib import Path
from types import CodeType, FrameType
from typing import Final, TypeAlias, cast

VERSION: Final = 1  # the file's format
DEFAULT: Final = "constricter-trace.json"
UNKNOWN: Final = "?"  # a value that can't be spelled
NONE: Final = "None"
SEPARATOR: Final = ":"  # between a class's module and its name
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
_IDLE: Final = 20  # how many returns with nothing new end a function's recording
_INSTALLED: Final = "site-packages"
_RETURN: Final = "return"
_OPTIONS: Final = frozenset({"--output", "--root"})
_MODULE: Final = "-m"
_MAIN: Final = "__main__"
_Held: TypeAlias = dict[str, list[str]]  # a function's locals' spellings, by name


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
    if type(value) in _SEQUENCES:
        return _container(type(value), (cast("Iterable[object]", value),), depth)
    if type(value) in _MAPPINGS:
        return _container(
            type(value),
            (cast("Iterable[object]", value), cast("Mapping[object, object]", value).values()),
            depth,
        )
    if isinstance(value, type):
        return UNKNOWN if named(value) == UNKNOWN else f"type[{named(value)}]"
    return named(type(value))


def named(cls: type) -> str:
    """Name a class as an annotation would: a builtin bare, another as `module:Class`.

    Returns:
      It; `UNKNOWN` for one no annotation can name (a function's, a nested one, a mock).

    """
    module: str = cls.__module__
    name: str = cls.__qualname__
    if module == _BUILTINS:
        return name if cast("type | None", getattr(builtins, name, None)) is cls else UNKNOWN
    if not name.isidentifier() or module.startswith(_MOCK):
        return UNKNOWN
    if cast("type | None", getattr(collections, name, None)) is cls:  # wherever it's defined
        return f"{collections.__name__}{SEPARATOR}{name}"
    if module.partition(".")[0] == _PATHLIB:
        return f"{_PATHLIB}{SEPARATOR}{_PATHS.get(name, name)}"
    # A private module's class, as the public one of its name has it (`_io`'s, in `io`).
    public: str = module.lstrip("_")
    exported: bool = cast("type | None", getattr(sys.modules.get(public), name, None)) is cls
    return f"{public if exported else module}{SEPARATOR}{name}"


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


def _container(kind: type, parts: tuple[Iterable[object], ...], depth: int) -> str | None:
    """Spell a container of class `kind` by each of its type arguments' values (`parts`).

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
    return f"{named(kind)}[{', '.join(cast('list[str]', arguments))}]"


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


@dataclass
class _Function:
    """What one function's locals have held, by name; and how many returns in a row added nothing."""

    held: dict[str, set[str]] = field(default_factory=dict[str, set[str]])
    idle: int = 0


class Recorder:
    """A profile function (`sys.setprofile`) noting each returning function's locals' types."""

    def __init__(self, root: Path) -> None:
        """Record the functions of the files under `root`."""
        self.root: Path = root.resolve()
        # By the code object's id: two alike in two files are equal. None: not one to record.
        self.functions: dict[int, _Function | None] = {}
        self.codes: dict[int, CodeType] = {}  # each one seen, kept so its id stays its own
        self.files: dict[str, Path | None] = {}  # each file's path under the root, if it's there
        self.modules: dict[str, str] = {}  # the file of each module a recorded function is in

    def __call__(self, frame: FrameType, event: str, _arg: object) -> None:
        """Note the types of `frame`'s locals as its function returns or yields."""
        if event != _RETURN:
            return
        code: CodeType = frame.f_code
        if id(code) not in self.functions:
            self.codes[id(code)] = code
            self.functions[id(code)] = _Function() if self._wanted(code) else None
            self.modules[str(frame.f_globals.get("__name__"))] = code.co_filename
        function: _Function | None = self.functions[id(code)]
        if function is None or function.idle >= _IDLE:
            return
        try:
            function.idle = (
                0
                if _noted(
                    function.held,
                    (*code.co_varnames, *code.co_cellvars),
                    cast("Mapping[str, object]", frame.f_locals),
                )
                else function.idle + 1
            )
        except (AttributeError, LookupError, RuntimeError, TypeError, ValueError):
            # A container another thread changed, or a class that isn't one: its function isn't recorded.
            self.functions[id(code)] = None

    def _wanted(self, code: CodeType) -> bool:
        """Check whether `code` is a function's, in a file under the root that isn't installed there.

        Returns:
          Whether it is.

        """
        return self._under(code.co_filename) is not None and not code.co_name.startswith("<")

    def _under(self, filename: str) -> Path | None:
        """Find the file `filename`'s path under the root.

        Returns:
          It, or `None` for a file elsewhere, or installed there (`site-packages`).

        """
        if filename not in self.files:
            path: Path = Path(filename).resolve()
            under: Path | None = path.relative_to(self.root) if path.is_relative_to(self.root) else None
            self.files[filename] = None if under is None or _INSTALLED in under.parts else under
        return self.files[filename]

    def found(self) -> dict[str, object]:
        """Gather what was recorded, as the file holds it.

        Returns:
          The format's version; each file by its SHA-256, with its path under the root and each
          function's locals' spellings by its first line; and each recorded module's file's
          SHA-256, by the name the run knew it by (`__main__`, for what it ran).

        """
        digests: dict[str, str | None] = {}
        paths: dict[str, str] = {}
        functions: dict[str, dict[str, _Held]] = {}
        at: int
        function: _Function | None
        for at, function in self.functions.items():
            code: CodeType = self.codes[at]
            digest: str | None = _digest(code.co_filename, digests)
            path: Path | None = self._under(code.co_filename)
            if digest is None or path is None or function is None:
                continue
            _ = paths.setdefault(digest, path.as_posix())
            merged: _Held = functions.setdefault(digest, {}).setdefault(str(code.co_firstlineno), {})
            merged.update(
                {
                    name: sorted({*merged.get(name, ()), *types})
                    for name, types in function.held.items()
                    if types
                },
            )
        return {
            "version": VERSION,
            "files": {
                digest: {
                    "path": paths[digest],
                    "functions": {line: held for line, held in found.items() if held},
                }
                for digest, found in functions.items()
            },
            "modules": {
                module: _digest(filename, digests)
                for module, filename in self.modules.items()
                if _digest(filename, digests) in functions
            },
        }

    def write(self, output: Path) -> None:
        """Write what was recorded to `output`."""
        _ = output.write_text(json.dumps(self.found(), sort_keys=True) + "\n", encoding="utf-8")


def _noted(held: dict[str, set[str]], names: Iterable[str], values: Mapping[str, object]) -> bool:
    """Add the types of the locals `names` that a frame holds (`values`) to `held`.

    Returns:
      Whether any is new.

    """
    new: bool = False
    name: str
    for name in names:
        if name in values and name.isidentifier():  # not a compiler's or a test runner's own
            text: str | None = spelled(values[name])
            if text is not None and text not in held.setdefault(name, set()):
                held[name].add(text)
                new = True
    return new


def _digest(filename: str, digests: dict[str, str | None]) -> str | None:
    """Hash the file `filename` as `--infer-from` will (kept in `digests`).

    Returns:
      Its SHA-256, or `None` for one that can't be read.

    """
    if filename not in digests:
        try:
            digests[filename] = hashlib.sha256(Path(filename).read_bytes()).hexdigest()
        except OSError:
            digests[filename] = None
    return digests[filename]


def _split(args: Sequence[str]) -> tuple[list[str], list[str]]:
    """Split the command line where what's to run starts: at `-m`, or the first word that's no option's.

    Returns:
      This command's options, and the module or script with its arguments.

    """
    valued: bool = False
    at: int
    arg: str
    for at, arg in enumerate(args):
        if valued or arg in _OPTIONS:
            valued = not valued
        elif arg == _MODULE or not arg.startswith("-"):
            return list(args[:at]), list(args[at:])
    return list(args), []


def _run(name: str, *, module: bool) -> None:
    """Run the module or the script `name`, as `python` would."""
    if module:
        _ = runpy.run_module(name, run_name=_MAIN, alter_sys=True)
    else:
        sys.path[0] = str(Path(name).resolve().parent)
        _ = runpy.run_path(name, run_name=_MAIN)


def main(argv: Sequence[str] | None = None) -> int:
    """Run the module or script named on the command line, recording its functions' locals' types.

    Returns:
      0: the exit status, where what ran doesn't exit itself.

    """
    parser: argparse.ArgumentParser = argparse.ArgumentParser(
        prog="python -m constricter.trace",
        usage="%(prog)s [--output FILE] [--root DIR] (-m MODULE | SCRIPT) [ARG ...]",
        description="Record the types a run binds its functions' locals to, for `constricter --infer-from`.",
    )
    _ = parser.add_argument(
        "--output",
        type=Path,
        default=Path(DEFAULT),
        metavar="FILE",
        help="where to write",
    )
    _ = parser.add_argument("--root", type=Path, default=Path(), metavar="DIR", help="whose files to record")
    own: list[str]
    target: list[str]
    own, target = _split(sys.argv[1:] if argv is None else argv)
    args: argparse.Namespace = parser.parse_args(own)
    module: int = int(target[:1] == [_MODULE])
    if len(target) <= module:
        parser.error("nothing to run: name a script, or a module after -m")
    name: str = target[module]
    sys.argv = [name, *target[module:][1:]]
    recorder: Recorder = Recorder(cast("Path", args.root))
    threading.setprofile(recorder)
    sys.setprofile(recorder)
    try:
        _run(name, module=bool(module))
    finally:
        sys.setprofile(None)
        threading.setprofile(None)
        recorder.write(cast("Path", args.output))
    return 0


if __name__ == "__main__":
    sys.exit(main())
