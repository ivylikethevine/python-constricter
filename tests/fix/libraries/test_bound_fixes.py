# SPDX-License-Identifier: MIT
"""`--fix` for what a bound type variable and a generic class's coroutine give, by typeshed's stubs."""

import textwrap
from typing import Final

from constricter import check_source

_BOUND: Final = """
import ast
import contextlib
import dataclasses
import socket


class Conn:
    def close(self) -> None: ...


def use(sock: socket.socket, conn: Conn, node: ast.Name, unknown) -> None:
    closing = contextlib.closing(conn)
    with contextlib.closing(sock) as entered:
        pass
    with closing as again:
        pass
    copied = dataclasses.replace(conn)
    placed = ast.copy_location(node, node)
    number = contextlib.closing(1)
    lost = contextlib.closing(unknown)
    with contextlib.closing(unknown) as nothing:
        pass
"""
_AWAITED: Final = """
import asyncio


class Item:
    pass


async def work(queue: asyncio.Queue[Item], bare: asyncio.Queue, unknown) -> None:
    item = await queue.get()
    now = queue.get_nowait()
    pending = queue.get()
    untyped = await bare.get()
    lost = await unknown.get()
"""


def test_a_lone_signatures_bound_type_variable_is_its_argument() -> None:
    """Whatever the bound, with no other signature to choose: not a builtin scalar its bound refuses."""
    assert {o.name: o.fix for o in check_source(textwrap.dedent(_BOUND))} == {
        "closing": "contextlib.closing[Conn]",
        "entered": "socket.socket",  # by `AbstractContextManager`'s first argument
        "again": "Conn",
        "copied": "Conn",
        "placed": "ast.Name",
        **dict.fromkeys(("number", "lost", "nothing")),
    }


def test_a_generic_classes_coroutine_is_typed_by_its_receiver() -> None:
    """Awaited, what its declared return gives the receiver's arguments; nothing unawaited, or bare."""
    assert {o.name: o.fix for o in check_source(textwrap.dedent(_AWAITED))} == {
        "item": "Item",
        "now": "Item",
        **dict.fromkeys(("pending", "untyped", "lost")),
    }
