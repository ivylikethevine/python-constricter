# SPDX-License-Identifier: MIT
"""What `constricter.fix.index.stubbed` has read of the installed modules, kept from one file to the next."""

from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import Final, TypeAlias

from constricter.fix.core.known import Origin
from constricter.fix.core.signatures import Accepts, Expansion, ReadSignature
from constricter.fix.index.classnames import Packaged
from constricter.fix.index.modules import Module

# An alias of an installed generic class: the class, the alias's expansion, and each installed class
# its pattern names, by its path there and where it's defined.
Expanded: TypeAlias = tuple[Origin, Expansion, tuple[tuple[str, Origin], ...]]
# A parameter's annotation as it was asked about: its module, the module read for, its text, and
# the type parameters in scope, each with its bound.
Asked: TypeAlias = tuple[str, str, str, tuple[tuple[str, str | None], ...]]


@dataclass
class Memo:
    """What's read of the installed modules, for as long as the index has the same ones.

    Each installed function's signatures, each package's classes and aliases (see
    `classnames.classes`), each class's lineage and methods (see `Methods`), each class's methods by
    name, the names of those it has, its bases' included, and each alias's expansion. The index
    changes as files are checked, the installed modules in it don't.
    """

    installed: frozenset[int] = frozenset()  # the installed modules read, by identity
    modules: Mapping[str, Module] | None = None  # the index they were last compared with
    read: dict[tuple[str, str], tuple[ReadSignature, ...]] = field(
        default_factory=dict[tuple[str, str], "tuple[ReadSignature, ...]"],
    )
    packages: dict[tuple[str, bool], Packaged] = field(
        default_factory=dict[tuple[str, bool], "Packaged"],
    )
    lines: dict[Origin, tuple[str, ...]] = field(default_factory=dict[Origin, "tuple[str, ...]"])
    methods: dict[tuple[Origin, str], tuple[ReadSignature, ...]] = field(
        default_factory=dict[tuple[Origin, str], "tuple[ReadSignature, ...]"],
    )
    names: dict[Origin, frozenset[str]] = field(default_factory=dict[Origin, frozenset[str]])
    expansions: dict[Origin, Expanded | None] = field(default_factory=dict[Origin, "Expanded | None"])
    accepts: dict[Asked, Accepts] = field(default_factory=dict["Asked", Accepts])

    def of(self, modules: Mapping[str, Module]) -> "Memo":
        """Keep what's read for as long as `modules` has the same installed ones.

        Returns:
          This memo, emptied if they've changed.

        """
        if modules is self.modules:  # asked of the same index again and again: compared once
            return self
        self.modules = modules
        installed: frozenset[int] = frozenset(id(module) for module in modules.values() if module.installed)
        if installed != self.installed:
            self.installed = installed
            self.read = {}
            self.packages = {}
            self.lines = {}
            self.methods = {}
            self.names = {}
            self.expansions = {}
            self.accepts = {}
        return self


MEMO: Final = Memo()
