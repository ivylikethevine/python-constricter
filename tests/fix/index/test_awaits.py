# SPDX-License-Identifier: MIT
"""`--fix` for `await` of a checked file's `async def`: a method's, and another file's function's."""

import textwrap
from pathlib import Path
from typing import Final

from constricter import Offence, check_source
from constricter.cli import command as cli
from constricter.cli import schedule
from constricter.fix.core.known import Returns
from constricter.fix.index import awaits, order, project, sides

_LOCAL: Final = """
class Client:
    async def fetch(self) -> bytes:
        return b""

    async def loose(self):
        return 1

    def plain(self) -> int:
        return 1


class Sub(Client):
    async def size(self) -> int:
        data = await self.fetch()
        return len(data)


class Quiet(Client):
    def fetch(self) -> str:
        return ""


async def use(client: Client, sub: Sub, quiet: Quiet, maybe: Client | None, unknown) -> None:
    data = await client.fetch()
    inherited = await sub.fetch()
    size = await sub.size()
    narrowed = await maybe.fetch()
    made = await Client().fetch()
    pending = client.fetch()
    loose = await client.loose()
    plain = await client.plain()
    hidden = await quiet.fetch()
    lost = await unknown.fetch()
"""
_BASE: Final = """
from typing import Self


class Base:
    @classmethod
    def make(cls) -> Self:
        return cls()

    @classmethod
    def plain(cls) -> "Base":
        return cls()

    @staticmethod
    def count() -> int:
        return 1

    async def fetch(self) -> bytes:
        return b""


async def load(url: str) -> "Base":
    return Base()


def sync(url: str) -> str:
    return url
"""
_INIT: Final = "from pkg.base import load as reexported\n"
_MAIN: Final = """
import pkg
import pkg.base as b
from pkg.base import Base, load, sync


class Sub(Base):
    async def run(self) -> None:
        own = await self.fetch()


class Deep(Sub):
    @staticmethod
    def count() -> str:
        return ""


class Other(Deep):
    pass


class Solo:
    pass


class Kid(Solo):
    pass


async def use(base: Base, load_local) -> None:
    got = await base.fetch()
    text = await load("u")
    again = await b.load("u")
    through = await pkg.reexported("u")
    wrong = await sync("u")
    made = Sub.make()
    plain = Sub.plain()
    count = Sub.count()
    deep = Deep.make()
    hidden = Deep.count()
    other = Other.count()
    direct = Base.make()
    kid = Kid.make()
"""


def test_awaiting_a_method_gives_its_declared_return() -> None:
    """The class's own `async def`'s, or a base's; nothing unawaited, or of a plain method."""
    fixes: dict[str, tuple[str | None, bool]] = {
        o.name: (o.fix, o.unsafe) for o in check_source(textwrap.dedent(_LOCAL))
    }
    assert fixes == {
        "data": ("bytes", False),
        "inherited": ("bytes", False),
        "size": ("int", False),
        "narrowed": ("bytes", False),
        "made": ("bytes", True),  # of a guessed receiver
        "loose": ("int", True),  # nothing declared: by its `return`s, as a method's are
        **dict.fromkeys(("pending", "plain", "hidden", "lost"), (None, False)),
    }
    kinds: dict[str, frozenset[str]] = {
        o.name: o.edit.kinds for o in check_source(textwrap.dedent(_LOCAL)) if o.edit is not None
    }
    assert kinds["data"] == {"await", "method"}


def _write(path: Path, source: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    _ = path.write_text(textwrap.dedent(source), encoding="utf-8", newline="\n")
    return path


def test_another_files_async_defs_and_class_side_methods_are_typed(tmp_path: Path) -> None:
    """An awaited function's however it's spelled; a class-side method an own class takes from its base."""
    _ = _write(tmp_path / "pkg" / "__init__.py", _INIT)
    _ = _write(tmp_path / "pkg" / "base.py", _BASE)
    main: Path = _write(tmp_path / "main.py", _MAIN)
    catalog: project.Index = project.index(sorted(tmp_path.rglob("*.py")))
    assert awaits.calls(catalog, main, {}) == {"load": "Base", "b.load": "Base", "pkg.reexported": "Base"}
    assert not awaits.calls(catalog, tmp_path / "missing.py", {})
    assert sides.calls(catalog, main, {})[0] == {
        "Sub.make": "Sub",  # its `Self`
        "Sub.plain": "Base",
        "Sub.count": "int",
        "Deep.make": "Deep",  # through `Sub`; `Deep.count` is the file's own
        "Base.make": "Base",
    }
    found: list[Offence] = check_source(
        main.read_text(encoding="utf-8"),
        outside=schedule.outside(catalog, main, {}),
    )
    assert {o.name: o.fix for o in found} == {
        "own": "bytes",
        "got": "bytes",
        "text": "Base",
        "again": "Base",
        "through": "Base",
        "wrong": None,
        "made": "Sub",
        "plain": "Base",
        "count": "int",
        "deep": "Deep",
        "hidden": "str",
        "other": "str",
        "direct": "Base",
        "kid": None,  # no base of its line is another file's
    }


_LOOSE: Final = """
import asyncio


async def count(url):
    return 1


async def made(url):
    return Client()


async def silent(url):
    await asyncio.sleep(1)


async def ticks(url):
    yield 1


async def declared(url) -> bytes:
    return b""


class Client:
    async def size(self):
        return 1.5

    async def me(self):
        return self

    def plain(self):
        return 1


class Sub(Client):
    pass


async def use(client: Client, sub: Sub, unknown, count_local) -> None:
    a = await count("u")
    b = await made("u")
    c = await silent("u")
    d = await ticks("u")
    e = await client.size()
    f = await sub.size()
    g = await sub.me()
    h = await unknown.size()
    i = await client.plain()
    j = count("u")
    k = asyncio.ensure_future(count("u"))
    m = asyncio.ensure_future(k)
    n = await asyncio.ensure_future(declared("u"))
    o = asyncio.ensure_future(unknown)
    p = await client.missing()
"""


def test_awaiting_an_async_def_declaring_nothing_gives_what_it_returns() -> None:
    """A function's `return`s, certain as a plain function's are; a method's, a guess. Not a generator's."""
    fixes: dict[str, tuple[str | None, bool]] = {
        o.name: (o.fix, o.unsafe) for o in check_source(textwrap.dedent(_LOOSE))
    }
    assert fixes == {
        "a": ("int", False),
        "b": ("Client", True),  # what its `return` rests on
        "e": ("float", True),
        "f": ("float", True),  # its base's
        "k": ("asyncio.Task[int]", False),  # a coroutine's call is no future: the signature taking one
        "m": ("asyncio.Task[int]", False),  # a task is: its own type
        "n": ("bytes", False),
        **dict.fromkeys("cdghijop", (None, False)),
    }
    reasons: dict[str, str] = {
        o.name: o.edit.reason for o in check_source(textwrap.dedent(_LOOSE)) if o.edit is not None
    }
    assert [reasons["a"], reasons["e"]] == [
        "`count`'s `return`s, awaited",
        "`Client.size`'s `return`s, awaited",
    ]


_CLIENT: Final = """
class Row:
    pass


async def load(url):
    return Row()


async def count(url):
    return 1


async def hidden(url):
    class Inner:
        pass

    return [Inner()]


class Client:
    async def size(self):
        return 1
"""
_CALLER: Final = """
from net import client
from net.client import Client, count


async def main(c: Client) -> None:
    a = await client.load("u")
    b = await count("u")
    d = await c.size()
    e = await client.hidden("u")
"""


_SHADOWING: Final = """
from net.client import load

Row = 1


async def main() -> None:
    kept = await load("u")
"""
_UNNAMED: Final = "    kept = await load"  # no way to name its `Row`
_CERTAIN: Final = ("    b: int = await count", "    a = await client.load")
_GUESSED: Final = (
    "    a: client.Row = await client.load",
    "    d: int = await c.size()",
    "    e = await client.hidden",  # a class its function defines: no caller can name it
)


def test_another_files_undeclared_async_def_is_typed_once_its_file_is_checked(tmp_path: Path) -> None:
    """The file awaiting it is checked after it; a guess there is one here."""
    _ = _write(tmp_path / "net" / "__init__.py", "")
    defining: Path = _write(tmp_path / "net" / "client.py", _CLIENT)
    caller: Path = _write(tmp_path / "net" / "caller.py", _CALLER)
    shadowing: Path = _write(tmp_path / "net" / "shadowing.py", _SHADOWING)
    paths: list[Path] = sorted(tmp_path.rglob("*.py"))
    catalog: project.Index = project.index(paths)
    assert awaits.needs(catalog, catalog.modules["net.caller"]) == {"net.client"}
    assert not awaits.needs(catalog, catalog.modules["net.client"])
    assert awaits.returned(catalog, caller, {}, Returns()) == Returns()  # nothing checked yet
    assert awaits.returned(catalog, tmp_path / "missing.py", {}, Returns()) == Returns()
    plan: order.Plan = order.plan(catalog, paths)
    assert plan.components.index([paths.index(caller)]) > plan.components.index([paths.index(defining)])
    assert cli.main(["--fix", "-q", "--jobs=1", str(tmp_path)]) == 1
    fixed: str = caller.read_text(encoding="utf-8")
    assert all(line in fixed for line in _CERTAIN), fixed
    _ = cli.main(["--fix", "-q", "--unsafe-fixes", "--jobs=1", str(tmp_path)])
    fixed = caller.read_text(encoding="utf-8")
    assert all(line in fixed for line in _GUESSED), fixed
    assert _UNNAMED in shadowing.read_text(encoding="utf-8")
