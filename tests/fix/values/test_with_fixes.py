# SPDX-License-Identifier: MIT
"""`--fix` for a `with` statement's target: what the context manager's `__enter__` returns."""

import ast
import textwrap
from typing import Final, TypeAlias

import pytest

from constricter import Offence, check_source
from constricter.fix.core import fixes
from constricter.fix.values import entered

_Fixes: TypeAlias = dict[str, tuple[str | None, bool]]
_STDLIB: Final = """
import contextlib
import io
import shelve
import socket
import subprocess
import tempfile
import threading
import zipfile


def f(p: str, z: zipfile.ZipFile, proc: subprocess.Popen[str], tmp: tempfile.TemporaryDirectory[str]) -> None:
    with zipfile.ZipFile(p) as made:
        pass
    with z as same, z:
        pass
    with socket.socket() as sock:
        pass
    with tmp as folder:
        pass
    with proc as started:
        pass
    with io.StringIO(p) as text:
        pass
    with threading.Condition() as held:
        pass
    with contextlib.suppress(OSError) as nothing:
        pass
    with unknown(p) as other:
        pass
    with z as (first, second):
        pass
    with shelve.open(p) as shelf:
        pass
"""
_PROJECT: Final = """
import contextlib
from collections.abc import Generator, Iterable, Iterator
from contextlib import contextmanager
from typing import Any, Self, TypeVar

T = TypeVar("T")


class Node:
    def __enter__(self) -> Self:
        return self


class Lock:
    def __enter__(self) -> bool:
        return True


@contextmanager
def opened(path: str) -> Iterator[Node]:
    yield Node()


@contextlib.contextmanager
def counted() -> Generator[int, None, None]:
    yield 1


@contextmanager
def listed() -> Iterable[list[str]]:
    yield []


@contextmanager
def silent() -> Iterator[None]:
    yield


@contextmanager
def vague() -> Iterator[Any]:
    yield 1


@contextmanager
def generic(value: T) -> Iterator[T]:
    yield value


@contextmanager
def undeclared():
    yield 1


@contextmanager
def other() -> list[int]:
    return []


@contextmanager
@staticmethod
def twice() -> Iterator[int]:
    yield 1


@contextmanager
def again() -> Iterator[int]:
    yield 1


def again() -> Iterator[int]:
    yield 1


@contextmanager
async def later() -> Iterator[int]:
    yield 1


def f(node: Node, lock: Lock, shadowed: int) -> None:
    with node as same:
        pass
    with Node() as made:
        pass
    with lock as held:
        pass
    with opened("p") as yielded:
        pass
    with counted() as count, listed() as names:
        pass
    with silent() as a, vague() as b, generic(1) as c, undeclared() as d, other() as e:
        pass
    with twice() as g, again() as h, later() as i:
        pass
    counted = shadowed
    with counted() as local:
        pass


async def g(node: Node) -> None:
    async with node as later:
        pass
"""

_TESTS: Final = """
import subprocess
import tarfile
import tempfile
import unittest
import warnings


class Case(unittest.TestCase):
    def test(self, path: str) -> None:
        with self.assertRaises(ValueError) as raised:
            pass
        with self.assertRaisesRegex(OSError, "k") as matched:
            pass
        with self.assertWarns(UserWarning) as warned:
            pass
        with self.assertRaises((OSError, ValueError)) as either:
            pass
        error = raised.exception
        with tempfile.TemporaryDirectory() as folder:
            pass
        with tempfile.NamedTemporaryFile() as binary:
            pass
        with tempfile.NamedTemporaryFile("w") as text:
            pass
        with tarfile.open(path) as archive:
            pass
        with warnings.catch_warnings(record=True) as caught:
            pass
        with warnings.catch_warnings() as quiet:
            pass
        with subprocess.Popen([path], text=True) as proc:
            pass
        same = self.addCleanup(print)


def f(KeyError, case: unittest.TestCase):
    with case.assertRaises(KeyError) as shadowed:
        pass
"""

_AWAITED: Final = """
import asyncio


async def serve(reader: asyncio.StreamReader, lock: asyncio.Lock, cmd):
    line = await reader.readline()
    proc = await asyncio.create_subprocess_exec(cmd)
    out = await proc.communicate()
    held = await lock.acquire()
    server = await asyncio.start_server(serve, "h", 1)
    async with asyncio.TaskGroup() as group:
        pass
    async with asyncio.timeout(1) as limit:
        pass
    async with lock as nothing:
        pass
    async with server as serving:
        pass
    unknown = await cmd.run()
    waited = await cmd
    async with cmd as other:
        pass
    async with group as (first, second):
        pass
    pending = reader.readline()
"""

_TASKS: Final = """
import asyncio


async def fetch(url: str) -> bytes:
    return b""


async def count() -> int:
    return 1


async def untyped():
    return object()


async def main(reader: asyncio.StreamReader, loop: asyncio.AbstractEventLoop) -> None:
    task = asyncio.create_task(fetch("u"))
    line = asyncio.create_task(reader.readline())
    unknown = asyncio.create_task(untyped())
    both = asyncio.gather(fetch("u"), count())
    looped = loop.create_task(count())
    async with asyncio.TaskGroup() as group:
        grouped = group.create_task(fetch("u"))
    done = await asyncio.gather(fetch("u"), count())
    waited = await asyncio.wait_for(count(), 1)
    made = await asyncio.create_task(count())
    slept = await asyncio.sleep(1, "done")
    pair = await asyncio.open_connection("h", 1)
    other = await loop.sock_accept(reader)
    held = await task
    kept = await both
    lost = await unknown
    read = await reader


def run(loop: asyncio.AbstractEventLoop) -> None:
    result = asyncio.run(fetch("u"))
    number = loop.run_until_complete(count())
"""


def _fixes(source: str) -> _Fixes:
    """Check `source`.

    Returns:
      Each untyped name's fix, and whether it's a guess.

    """
    return {o.name: (o.fix, o.unsafe) for o in check_source(textwrap.dedent(source))}


def test_a_standard_library_managers_target_is_what_it_enters() -> None:
    """A manager that returns itself gives its own type, arguments and all; another, what it declares."""
    assert _fixes(_STDLIB) == {
        "made": ("zipfile.ZipFile", False),
        "same": ("zipfile.ZipFile", False),
        "sock": ("socket.socket", False),
        "folder": ("str", False),
        "started": ("subprocess.Popen[str]", False),
        "text": ("io.StringIO", False),
        "held": ("bool", False),
        "nothing": (None, False),
        "other": (None, False),
        "first": (None, False),
        "second": (None, False),
        "shelf": (None, False),  # a `Shelf` of what isn't known: not written bare
    }


def test_a_managers_arguments_decide_what_it_enters() -> None:
    """A test case's `assertRaises`, a constructor whose overloads declare its instance, `tarfile.open`.

    A class passed as an argument binds a `type[_E]`'s `_E`: a builtin one too, unless the module
    binds the name.
    """
    assert _fixes(_TESTS) == {
        "raised": ("_AssertRaisesContext[ValueError]", False),
        "matched": ("_AssertRaisesContext[OSError]", False),
        "warned": ("_AssertWarnsContext", False),
        "either": (None, False),  # a tuple of classes: no one type
        "error": ("ValueError", False),
        "folder": ("str", False),
        "binary": ("tempfile._TemporaryFileWrapper[bytes]", False),
        "text": ("tempfile._TemporaryFileWrapper[str]", False),
        "archive": ("tarfile.TarFile", False),
        "caught": ("list[warnings.WarningMessage]", False),
        "quiet": (None, False),  # it enters as `None`
        "proc": ("subprocess.Popen[str]", False),
        "same": (None, False),
        "shadowed": (None, False),  # the module's own `KeyError`, a parameter
    }


def test_a_library_coroutine_awaited_gives_what_it_declares() -> None:
    """A standard-library `async def` awaited: a function's, a method's, an `async with`'s `__aenter__`."""
    assert _fixes(_AWAITED) == {
        "line": ("bytes", False),
        "proc": ("Process", False),
        "out": ("tuple[bytes, bytes]", False),
        "held": ("bool", False),
        "server": ("asyncio.Server", False),
        "group": ("asyncio.TaskGroup", False),
        "limit": ("asyncio.Timeout", False),
        "nothing": (None, False),  # a lock enters as `None`
        "serving": ("asyncio.Server", False),
        **dict.fromkeys(("unknown", "waited", "other", "first", "second"), (None, False)),
        "pending": (None, False),  # not awaited: a coroutine
    }


def test_a_coroutines_call_binds_what_awaiting_it_gives() -> None:
    """An awaitable parameter's variable, by the coroutine passed; a task or a future awaited, its own."""
    assert _fixes(_TASKS) == {
        "task": ("asyncio.Task[bytes]", False),
        "line": ("asyncio.Task[bytes]", False),
        "unknown": (None, False),  # nothing declared: a task of what isn't known
        "both": ("asyncio.Future[tuple[bytes, int]]", False),
        "looped": ("asyncio.Task[int]", False),
        "group": ("asyncio.TaskGroup", False),
        "grouped": ("asyncio.Task[bytes]", False),
        "done": ("tuple[bytes, int]", False),
        "waited": ("int", False),
        "made": ("int", False),
        "slept": ("str", False),
        "pair": ("tuple[asyncio.StreamReader, asyncio.StreamWriter]", False),
        "other": (None, False),
        "held": ("bytes", False),  # a task held in a name, awaited later
        "kept": ("tuple[bytes, int]", False),
        "lost": (None, False),
        "read": (None, False),  # not an awaitable of anything
        "result": ("bytes", False),
        "number": ("int", False),
    }


def test_a_project_managers_target_is_what_it_declares() -> None:
    """A class's declared `__enter__`, or what a `@contextmanager` function declares it yields."""
    assert _fixes(_PROJECT) == {
        "same": ("Node", False),
        "made": ("Node", True),  # a capitalised call, taken to construct a `Node`
        "held": ("bool", False),
        "yielded": ("Node", False),
        "count": ("int", False),
        "names": ("list[str]", False),
        **dict.fromkeys("abcdeghi", (None, False)),
        "counted": ("int", False),
        "local": (None, False),  # a local of that name isn't the function
        "later": (None, False),  # `__aenter__`'s return is awaited: not read
    }


def test_the_target_is_declared_before_the_statement() -> None:
    """As `open`'s is: on a line of its own, at the statement's indentation."""
    source: str = textwrap.dedent(
        """\
        import zipfile
        def f(p: str) -> None:
            with zipfile.ZipFile(p) as z, open(p) as t:
                pass
        """,
    )
    offences: list[Offence] = check_source(source)
    fixed: str = "".join(fixes.apply(source.splitlines(keepends=True), offences))
    expected: str = (
        "import zipfile\n"
        "from io import TextIOWrapper\n"
        "def f(p: str) -> None:\n"
        "    z: zipfile.ZipFile\n"
        "    t: TextIOWrapper\n"
        "    with zipfile.ZipFile(p) as z, open(p) as t:\n"
        "        pass\n"
    )
    assert fixed == expected


@pytest.mark.parametrize(
    ("returns", "yielded"),
    [
        ("Iterator[int]", "int"),
        ("Generator[dict[str, int], None, None]", "dict[str, int]"),
        ("typing.Iterator[Node]", "Node"),
        ("Iterator[()]", None),
        ('Iterator["Node"]', None),  # a string: its meaning isn't read
        ("Iterator", None),
        ("int", None),
    ],
)
def test_a_manager_function_yields_its_iterators_element(returns: str, yielded: str | None) -> None:
    """`Iterator[T]`'s `T`, or a `Generator`'s first argument: nothing else."""
    tree: ast.Module = ast.parse(f"@contextmanager\ndef m() -> {returns}:\n    yield\n")
    assert entered.managers(tree) == ({} if yielded is None else {"m": yielded})


_LATER: Final = """
def extract(path: str) -> None:
    with Archive(path) as archive:
        archive.close()


class Archive:
    def __init__(self, path: str) -> None:
        self.path: str = path

    def __enter__(self):
        return self

    def __exit__(self, *args: object) -> None:
        self.close()

    def close(self) -> None:
        pass
"""


def test_a_manager_defined_after_its_with_is_entered_by_its_returns() -> None:
    """The `with` calls `__enter__`: its function is checked again once that method's `return`s are read."""
    assert _fixes(_LATER) == {"archive": ("Archive", True)}
