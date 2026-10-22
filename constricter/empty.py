"""An empty mapping nothing can change: a record's default, where a `{}` is a dict every record shares."""

from collections.abc import Iterator, Mapping
from typing import NoReturn, TypeVar

from constricter.overrides import override

_K = TypeVar("_K")
_V = TypeVar("_V")


class Empty(Mapping[_K, _V]):
    """A mapping of nothing, read-only, equal to `{}`, and pickled as itself: workers are sent records."""

    __slots__: tuple[()] = ()

    @override
    def __getitem__(self, key: _K) -> NoReturn:
        """Find nothing.

        Raises:
          KeyError: always.

        """
        raise KeyError(key)

    @override
    def __iter__(self) -> Iterator[_K]:
        """Yield nothing.

        Returns:
          An empty iterator.

        """
        return iter(())

    @override
    def __len__(self) -> int:
        """Count nothing.

        Returns:
          0.

        """
        return 0

    @override
    def __reduce__(self) -> "tuple[type[Empty[_K, _V]], tuple[()]]":
        """Pickle as a new empty mapping.

        Returns:
          How.

        """
        return Empty, ()

    @override
    def __repr__(self) -> str:
        """Write it as it's made.

        Returns:
          `Empty()`.

        """
        return "Empty()"
