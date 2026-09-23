# SPDX-License-Identifier: MIT
"""The language server protocol's wire format, as `--infer-with`'s connections speak it (see `hints`).

Each message is framed by headers and a blank line, then `Content-Length` bytes of JSON. A hint's
type is its label after its `:`; basedpyright is asked for variable types only.
"""

import json
from typing import IO, Final, NamedTuple, TypeAlias, cast

Json: TypeAlias = dict[str, "Json"] | list["Json"] | str | int | float | bool | None
Object: TypeAlias = dict[str, Json]
_HEADER_END: Final = b"\r\n"
_LENGTH: Final = "content-length"
_TYPE_HINT: Final = 1  # `InlayHintKind.Type`
# Only variable types: argument names and return types are hints too, but nothing here.
_BASEDPYRIGHT_SECTION: Final = "basedpyright.analysis"
_BASEDPYRIGHT: Final[Object] = {
    "inlayHints": {
        "variableTypes": True,
        "callArgumentNames": False,
        "functionReturnTypes": False,
        "genericTypes": False,
    },
}


class Server(NamedTuple):
    """A checker's language server: how it's started, and how many are worth running at once.

    Its executable, the arguments that start it over stdio, and the most of it to run (up to
    `MAX_SERVERS`; one for a checker that works in parallel itself).
    """

    executable: str
    args: tuple[str, ...]
    most: int


MAX_SERVERS: Final = 4  # a checker's, at most: each holds its own copy of the program it checks
SERVERS: Final = {
    # One thread each: more servers check more at once (sqlalchemy's hints: 10.8s with one, 7.2s with four).
    "basedpyright": Server("basedpyright-langserver", ("--stdio",), MAX_SERVERS),
    # Parallel already: more servers only repeat its work (sqlalchemy's: 0.9s with one, 0.7s with four).
    "ty": Server("ty", ("server",), 1),
}


class HintError(Exception):
    """The type checker couldn't be started, or failed to answer."""


def write(stream: IO[bytes], data: bytes) -> None:
    """Write `data` to `stream`, and flush it: the server reads it now."""
    _ = stream.write(data)
    stream.flush()


def settings(section: Json) -> Json:
    """Answer a `workspace/configuration` item: only basedpyright's inlay hints are set.

    Returns:
      The section's settings, or `None` for the server's defaults.

    """
    return _BASEDPYRIGHT if section == _BASEDPYRIGHT_SECTION else None


def label(hint: Object) -> str | None:
    """Read a variable-type hint's type: its label (a string, or parts joined) after its `:`.

    Returns:
      The type's text, or `None` for any other hint (a parameter's name, a return type).

    """
    raw: Json = hint.get("label")
    text: str = (
        raw
        if isinstance(raw, str)
        else "".join(str(cast("Object", part).get("value", "")) for part in cast("list[Json]", raw or []))
    )
    if hint.get("kind", _TYPE_HINT) != _TYPE_HINT or not text.startswith(":"):
        return None
    return text[1:].strip() or None


def message(stream: IO[bytes]) -> Object | None:
    """Read one framed message: headers, a blank line, then `Content-Length` bytes of JSON.

    Returns:
      It, or `None` at the end of the stream (or a frame without a length).

    """
    headers: dict[str, str] = {}
    line: bytes
    for line in iter(stream.readline, b""):
        if line == _HEADER_END:
            break
        name: str
        _separator: str
        value: str
        name, _separator, value = line.decode("ascii").partition(":")
        headers[name.strip().lower()] = value.strip()
    if _LENGTH not in headers:
        return None
    body: bytes = stream.read(int(headers[_LENGTH]))
    try:
        return cast("Object", json.loads(body))
    except ValueError:  # cut off: the server died in the middle of it
        return None
