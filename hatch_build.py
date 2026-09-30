# SPDX-License-Identifier: MIT
"""Hatchling's build hook: generate the standard-library tables where they're missing or stale.

They aren't tracked (see `stdlib_tables.generate`). A build from a checkout generates them, and asks
for the basedpyright version `uv.lock` pins to read typeshed's stubs from; one from an sdist, which
carries them, asks for nothing.
"""

import importlib
import sys
from collections.abc import Callable
from typing import TYPE_CHECKING, Protocol, cast

from hatchling.builders.config import BuilderConfig
from hatchling.builders.hooks.plugin.interface import BuildHookInterface

if TYPE_CHECKING:
    from typing_extensions import override  # `typing.override` is 3.12+
else:

    def override(func: object) -> object:
        """Mark an override (for type checkers only).

        Returns:
          `func`.

        """
        return func


class _Generator(Protocol):  # pylint: disable=too-few-public-methods  # a module's functions
    """What the hook uses of `stdlib_tables.generate`."""

    STUBS: str
    current: Callable[[], bool]  # whether the tables are all there, and current
    pinned: Callable[[], str]  # the basedpyright version the tables are read from
    ensure: Callable[[], bool]  # generate the tables if they're missing or stale


def _typed(generator: object) -> _Generator:
    """Type the generator's module by what the hook uses of it.

    Returns:
      It.

    """
    return cast("_Generator", generator)


class TablesHook(BuildHookInterface[BuilderConfig]):
    """Generate the tables before a build, and ask for basedpyright only when it must."""

    def _generator(self) -> _Generator:
        """Import `stdlib_tables.generate` from the project being built.

        Returns:
          It.

        """
        if self.root not in sys.path:
            sys.path.insert(0, self.root)
        return _typed(importlib.import_module("stdlib_tables.generate"))

    @override
    def dependencies(self) -> list[str]:
        """Ask for the pinned basedpyright, if the tables must be generated.

        Returns:
          It, or nothing.

        """
        generator: _Generator = self._generator()
        return [] if generator.current() else [f"{generator.STUBS}=={generator.pinned()}"]

    @override
    def initialize(self, version: str, build_data: dict[str, object]) -> None:
        """Generate the tables, if they're missing or stale."""
        _ = self._generator().ensure()
