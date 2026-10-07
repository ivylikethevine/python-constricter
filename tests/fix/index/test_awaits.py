# SPDX-License-Identifier: MIT
"""`--fix` for `await` of a checked file's `async def`: a method's, and another file's function's."""

import textwrap
from pathlib import Path
from typing import Final

from constricter import Offence, check_source
from constricter.cli import schedule
from constricter.fix.index import awaits, project, sides

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
    """The class's own `async def`'s, or a base's; nothing unawaited, undeclared, or of a plain method."""
    fixes: dict[str, tuple[str | None, bool]] = {
        o.name: (o.fix, o.unsafe) for o in check_source(textwrap.dedent(_LOCAL))
    }
    assert fixes == {
        "data": ("bytes", False),
        "inherited": ("bytes", False),
        "size": ("int", False),
        "narrowed": ("bytes", False),
        "made": ("bytes", True),  # of a guessed receiver
        **dict.fromkeys(("pending", "loose", "plain", "hidden", "lost"), (None, False)),
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
