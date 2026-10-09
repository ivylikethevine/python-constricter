# SPDX-License-Identifier: MIT
"""The signatures `--fix` matches a call against: the standard library's tables', and installed packages'.

What each parameter takes (`Accepts`), and a signature as the tables hold it (`Signature`) and as
it's matched (`ReadSignature`); see `constricter.fix.libraries.overloads`, which matches them,
`constricter.fix.libraries.stdlib`, whose tables hold them, and `constricter.fix.index.stubbed`,
which reads an installed package's.
"""

from typing import Final, NamedTuple, NotRequired, Required, TypeAlias, TypedDict

# `Accepts`' keys for an installed package's parameter (see `constricter.fix.index.stubbed`): a class passed
# as the argument, and a builtin container.
# Before a path, an `async def`'s entry for `overloads.chosen`; before a method's name in
# `method_overloads`, an `async def` method's: its signatures' returns are what awaiting a call gives.
AWAIT: Final = "await "
CLASS_VERDICT: Final = "k"
CLASS_BINDS: Final = "kv"
CLASS_BOUNDED: Final = "kb"
CONTAINER_VERDICTS: Final = "b"
ELEMENT_VERDICTS: Final = "be"
CONTAINER_BINDS: Final = "bc"
OWN: Final = "own"
OWN_ELEMENTS: Final = "own_e"
FUTURE_BINDS: Final = "f"

Constant: TypeAlias = bool | int | float | complex | str | bytes | None  # a literal's value


class Accepts(TypedDict, total=False):
    """Which argument types a parameter takes (see `constricter.fix.libraries.overloads`).

    `v`: a verdict (`y`, `n`, `?`) per `overloads.SCALARS` type, for an argument that isn't a
    literal; `c`: for a literal not among `lit` (its `Literal[...]` values), where that differs;
    `var`: the type variable the parameter is, and its type, for an argument of each type; or just
    its name, where each binds it to its own type (a `str` literal's `str`). `t`: the type variable
    the parameter is, unbounded, so any argument binds it to its own type (`copy.copy(x)`). `e`, for
    a parameter that is a generic class of one type variable (`Iterable[_T]`): that variable, which
    an argument of a builtin container in `of` (`list[str]`) binds to its type argument at that index.
    `r`: the type variable a callable parameter returns (`Callable[..., _T]`), which a function
    argument binds to its declared return (`functools.partial(helper, 1)`). `w`: the type variable
    an awaitable parameter gives awaited (`Coroutine[Any, Any, _T]`), which a coroutine's call binds
    to what awaiting it gives (`asyncio.run(main())`). `k`: for an installed
    package's parameter, a verdict for a class passed as the argument (`dtype=np.float64`), `kv`
    the type variable it binds to that class (`type[_T]`'s `_T`), and `kb` whether that variable
    is bounded: a builtin class may be outside its bound, and another signature's to take. `b`: a
    verdict per builtin container argument (`tuple`), and `be`, where the parameter says what its
    elements must be, a verdict per `SCALARS` type for them; `bc`: the bounded type variable a
    container argument it takes binds. `f`: the type variable the parameter is, bounded by a future
    (`asyncio.ensure_future`'s `_FT`), which a future or a task binds to its type, and no
    coroutine's call does.
    `own`: for a checked file's parameter that takes nothing but checked files' classes, their paths,
    which an argument's class is matched against by its lineage; `own_e`: those a builtin sequence's
    or set's elements must be, for one that takes iterables of them (see `index.own_types`).
    """

    v: Required[str]
    c: str
    lit: list[Constant]
    var: str | dict[str, list[str]]
    t: str
    e: str
    of: dict[str, int]
    r: str
    w: str
    k: str
    kv: str
    kb: bool
    b: dict[str, str]
    be: dict[str, str]
    bc: str
    f: str
    own: list[str]
    own_e: list[str]


# A parameter: its name, kind (`p` positional, `e` either, `k` keyword, `a` `*args`, `w` `**kwargs`),
# whether it has a default, and what it takes (`None`: whatever every signature takes there). The
# tables write one every signature has alike as `"name kind"`, `=` after it if it has a default.
Parameter: TypeAlias = tuple[str, str, bool, Accepts | None]


class Signature(TypedDict):
    """One signature of a function whose arguments decide its type: its parameters, and its return.

    The return is a template (see `constricter.fix.libraries.overloads`), or `None` if `--fix` can't write it.
    `self`: for a generic class's method declaring its instance's type (`self: Pattern[str]`), the
    type arguments that instance must have. `takes`: for an operator's method (`__add__`), its one
    operand's type as a template, or `None` if `--fix` can't write it.
    """

    params: list[Parameter | str]
    returns: str | None
    self: NotRequired[list[str]]
    takes: NotRequired[str | None]


Variant: TypeAlias = list[Signature]  # one configuration's signatures, in order


class ReadSignature(NamedTuple):
    """One signature, read: its parameters in full, its return template, and its `self`'s type arguments."""

    params: tuple[Parameter, ...]
    returns: str | None
    instance: list[str] | None
    # An installed class's method declaring its `self`: the type its receiver must have, as a pattern
    # (classes by where they're defined, `typing.Any` for anything, type variables bare), and those
    # variables' bounds, likewise (see `constricter.fix.index.stubbed`).
    receiver: str | None = None
    bounds: tuple[tuple[str, str], ...] = ()


class Expansion(NamedTuple):
    """A public alias of an installed generic class (`npt.NDArray`), as a receiver's type is written.

    `params`: its own type parameters, renamed apart from any a method names (`_alias0`), which the
    receiver's type arguments bind; `receiver`: what it stands for, as a pattern naming them (see
    `ReadSignature.receiver`); `templates`: the class's type parameters, each with a template naming
    them (`np.dtype[_alias0]`), where one can be written.
    """

    params: tuple[str, ...]
    receiver: str
    templates: tuple[tuple[str, str], ...]
