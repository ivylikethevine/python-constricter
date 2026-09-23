# SPDX-License-Identifier: MIT
"""Standard-library functions whose return type is a builtin one, and how a module names them.

`RETURNS` holds functions that return the same builtin type whatever their arguments; `ANY_STR`
functions return the type of their arguments (`str` in, `str` out; `bytes` in, `bytes` out), so
they're typed only when those are known. A call is matched by the module and name it resolves to
through the module's imports (`origins`), not by how it's spelled, so `import os as o` then
`o.getpid()`, or `from os import getpid`, are the same call, and a `getpid` from anywhere else isn't.
"""

import ast
from collections.abc import Mapping
from typing import Final

_FLOAT: Final = "float"
_INT: Final = "int"
_STR: Final = "str"
_BOOL: Final = "bool"
_BYTES: Final = "bytes"
RETURNS: Final = {
    **dict.fromkeys(
        ["time.time", "time.monotonic", "time.perf_counter", "time.process_time", "time.thread_time"],
        _FLOAT,
    ),
    **dict.fromkeys(
        ["time.time_ns", "time.monotonic_ns", "time.perf_counter_ns", "time.process_time_ns"],
        _INT,
    ),
    **dict.fromkeys(["time.ctime", "time.asctime", "time.strftime"], _STR),
    **dict.fromkeys(["os.getpid", "os.getppid", "os.open", "os.dup"], _INT),
    **dict.fromkeys(["os.getcwd", "os.getlogin", "os.fsdecode"], _STR),
    **dict.fromkeys(["os.getcwdb", "os.urandom", "os.fsencode"], _BYTES),
    **dict.fromkeys(
        ["os.path.exists", "os.path.isfile", "os.path.isdir", "os.path.isabs", "os.path.islink"],
        _BOOL,
    ),
    "os.path.getsize": _INT,
    **dict.fromkeys(["os.path.getmtime", "os.path.getatime", "os.path.getctime"], _FLOAT),
    **dict.fromkeys(["textwrap.dedent", "textwrap.indent", "textwrap.fill", "textwrap.shorten"], _STR),
    "textwrap.wrap": "list[str]",
    **dict.fromkeys(["shlex.quote", "shlex.join"], _STR),
    "shlex.split": "list[str]",
    "json.dumps": _STR,
    "struct.pack": _BYTES,
    "struct.calcsize": _INT,
    **dict.fromkeys(["random.random", "random.uniform"], _FLOAT),
    **dict.fromkeys(["random.randint", "random.randrange", "random.getrandbits"], _INT),
    **dict.fromkeys(
        [
            "math.floor",
            "math.ceil",
            "math.gcd",
            "math.lcm",
            "math.isqrt",
            "math.factorial",
            "math.comb",
            "math.perm",
        ],
        _INT,
    ),
    **dict.fromkeys(
        ["math.sqrt", "math.log", "math.log2", "math.log10", "math.exp", "math.fsum", "math.hypot"],
        _FLOAT,
    ),
    **dict.fromkeys(["math.isclose", "math.isnan", "math.isinf", "math.isfinite"], _BOOL),
    **dict.fromkeys(
        # Not `sys.getrefcount`: CPython's own, missing on PyPy.
        ["sys.getrecursionlimit", "sys.getsizeof", "sys.getswitchinterval"],
        _INT,
    ),
    **dict.fromkeys(["sys.intern", "sys.getdefaultencoding", "sys.getfilesystemencoding"], _STR),
    **dict.fromkeys(
        [
            "platform.system",
            "platform.machine",
            "platform.node",
            "platform.release",
            "platform.version",
            "platform.python_version",
            "platform.platform",
        ],
        _STR,
    ),
    "socket.gethostname": _STR,
    "getpass.getuser": _STR,
    **dict.fromkeys(
        [
            "base64.b64encode",
            "base64.b64decode",
            "base64.urlsafe_b64encode",
            "base64.urlsafe_b64decode",
            "binascii.hexlify",
            "binascii.unhexlify",
            "binascii.b2a_base64",
            "zlib.compress",
            "zlib.decompress",
        ],
        _BYTES,
    ),
    **dict.fromkeys(["binascii.crc32", "zlib.crc32", "zlib.adler32"], _INT),
    **dict.fromkeys(
        [
            "string.capwords",
            "html.escape",
            "html.unescape",
            "urllib.parse.quote",
            "urllib.parse.quote_plus",
            "urllib.parse.unquote",
            "urllib.parse.unquote_plus",
            "urllib.parse.urlencode",
            "inspect.cleandoc",
            "inspect.getsource",
            "locale.getpreferredencoding",
        ],
        _STR,
    ),
    **dict.fromkeys(
        [
            "keyword.iskeyword",
            "inspect.isclass",
            "inspect.isfunction",
            "inspect.ismethod",
            "inspect.ismodule",
            "inspect.iscoroutinefunction",
            "inspect.isgeneratorfunction",
        ],
        _BOOL,
    ),
}
# Functions returning the type of their arguments (`AnyStr`): `str` if they're all `str`, `bytes`
# if all `bytes`.
ANY_STR: Final = frozenset(
    {
        "os.path.join",
        "os.path.basename",
        "os.path.dirname",
        "os.path.abspath",
        "os.path.normpath",
        "os.path.normcase",
        "os.path.realpath",
        "os.path.expanduser",
        "os.path.expandvars",
        "os.path.relpath",
        "re.escape",
    },
)
# An environment lookup: `os.environ.get(k)` or `os.getenv(k)` is `str | None`, with a `str` default
# it's `str`.
ENVIRONMENT: Final = frozenset({"os.environ.get", "os.getenv"})
KNOWN: Final = frozenset({*RETURNS, *ANY_STR, *ENVIRONMENT})  # every function the tables type
_TABLE_MODULES: Final = frozenset(
    {name.rsplit(".", 1)[0] for name in {*RETURNS, *ANY_STR, *ENVIRONMENT}}
    | {name.split(".", 1)[0] for name in {*RETURNS, *ANY_STR, *ENVIRONMENT}},
)


def origins(tree: ast.Module) -> dict[str, str]:
    """Map each top-level name the module imports from the standard library to what it is.

    `import os` binds `os` to `os` (and `import os.path` binds `os` too); `import os.path as p`
    binds `p` to `os.path`; `from os import getpid as pid` binds `pid` to `os.getpid`. Only the
    modules the tables name are kept, and a relative import names no module here.

    Returns:
      Each bound name, mapped to its dotted origin.

    """
    found: dict[str, str] = {}
    stmt: ast.stmt
    module: str
    alias: ast.alias
    for stmt in tree.body:
        match stmt:
            case ast.Import():
                for alias in stmt.names:
                    if alias.name.split(".", 1)[0] in _TABLE_MODULES:
                        found[alias.asname or alias.name.split(".", 1)[0]] = (
                            alias.name if alias.asname else alias.name.split(".", 1)[0]
                        )
            case ast.ImportFrom(module=str() as module, level=0) if module in _TABLE_MODULES:
                for alias in stmt.names:
                    found[alias.asname or alias.name] = f"{module}.{alias.name}"
            case _:
                pass
    return found


def resolved(func: ast.expr, bound: Mapping[str, str]) -> str | None:
    """Resolve a callee (`o.path.join`, `getpid`) through the module's imports (`bound`, see `origins`).

    Returns:
      Its dotted origin (`os.path.join`), or `None` if its first name isn't one the module imports.

    """
    name: str
    owner: ast.expr
    attr: str
    match func:
        case ast.Name(id=name) if name in bound:
            return bound[name]
        case ast.Attribute(value=owner, attr=attr):
            found: str | None = resolved(owner, bound)
            return None if found is None else f"{found}.{attr}"
        case _:
            return None
