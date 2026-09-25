# SPDX-License-Identifier: MIT
"""The signatures `--fix` matches a call against: the standard library's tables', and installed packages'.

What each parameter takes (`Accepts`) and the signature it's in (`ReadSignature`); see
`constricter.fix.overloads`, which matches them, `constricter.fix.stdlib`, whose tables hold them,
and `constricter.fix.stubbed`, which reads an installed package's.
"""

from typing import Final, NamedTuple, Required, TypeAlias, TypedDict

# `Accepts`' keys for an installed package's parameter (see `constricter.fix.stubbed`): a class passed
# as the argument, and a builtin container.
CLASS_VERDICT: Final = "k"
CLASS_BINDS: Final = "kv"
CONTAINER_VERDICTS: Final = "b"
ELEMENT_VERDICTS: Final = "be"
CONTAINER_BINDS: Final = "bc"

Constant: TypeAlias = bool | int | float | complex | str | bytes | None  # a literal's value


class Accepts(TypedDict, total=False):
    """Which argument types a parameter takes (see `constricter.fix.overloads`).

    `v`: a verdict (`y`, `n`, `?`) per `overloads.SCALARS` type, for an argument that isn't a
    literal; `c`: for a literal not among `lit` (its `Literal[...]` values), where that differs;
    `var`: the type variable the parameter is, and its type, for an argument of each type; or just
    its name, where each binds it to its own type (a `str` literal's `str`). `t`: the type variable
    the parameter is, unbounded, so any argument binds it to its own type (`copy.copy(x)`). `e`, for
    a parameter that is a generic class of one type variable (`Iterable[_T]`): that variable, which
    an argument of a builtin container in `of` (`list[str]`) binds to its type argument at that index.
    `r`: the type variable a callable parameter returns (`Callable[..., _T]`), which a function
    argument binds to its declared return (`functools.partial(helper, 1)`). `k`: for an installed
    package's parameter, a verdict for a class passed as the argument (`dtype=np.float64`), and `kv`
    the type variable it binds to that class (`type[_T]`'s `_T`). `b`: a verdict per builtin container
    argument (`tuple`), and `be`, where the parameter says what its elements must be, a verdict per
    `SCALARS` type for them; `bc`: the bounded type variable a container argument it takes binds.
    """

    v: Required[str]
    c: str
    lit: list[Constant]
    var: str | dict[str, list[str]]
    t: str
    e: str
    of: dict[str, int]
    r: str
    k: str
    kv: str
    b: dict[str, str]
    be: dict[str, str]
    bc: str


# A parameter: its name, kind (`p` positional, `e` either, `k` keyword, `a` `*args`, `w` `**kwargs`),
# whether it has a default, and what it takes (`None`: whatever every signature takes there). The
# tables write one every signature has alike as `"name kind"`, `=` after it if it has a default.
Parameter: TypeAlias = tuple[str, str, bool, Accepts | None]


class ReadSignature(NamedTuple):
    """One signature, read: its parameters in full, its return template, and its `self`'s type arguments."""

    params: tuple[Parameter, ...]
    returns: str | None
    instance: list[str] | None
