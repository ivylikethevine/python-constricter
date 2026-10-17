# SPDX-License-Identifier: MIT
"""What a name in a stub refers to, across the installed modules the index holds (`Resolver`).

An alias, a class or a type variable, where it's declared, a class's bases in order, and what a
call's name refers to through its module's imports; `stub_signatures.Reader` reads signatures with
it.
"""

import ast
import builtins
from collections.abc import Iterator, Mapping
from typing import Final, TypeAlias

from constricter.fix.core.known import Origin
from constricter.fix.index import project
from constricter.fix.index.modules import Module
from constricter.fix.index.stubs import classnames
from constricter.fix.index.stubs.atoms import (
    BUILTINS_MODULE,
    CLASS,
    VAR,
    Atom,
    Scope,
    atom_path,
    parse_text,
)
from constricter.fix.index.stubs.declared import Alias, Class, Declarations, Variable

ARG: Final = "arg"
_BUILTINS: Final = frozenset(dir(builtins))
ALIAS_DEPTH: Final = 20  # aliases followed before giving up
_UNFOLLOWED: Final = "?"  # a lineage's base that can't be followed


Resolved: TypeAlias = Atom | tuple[Alias, Scope, Origin]


def call_origin(modules: Mapping[str, Module], target: Module, callee: str) -> Origin | None:
    """Find what a call's name refers to: `f`, `np.empty`, `pkg.util.f` through the module's imports.

    A package's attribute, re-exported from anywhere (`numpy.empty`), not just what it defines.

    Returns:
      Its origin, or `None`.

    """
    head: str
    parts: list[str]
    head, *parts = callee.split(".")
    origin: Origin | None = classnames.as_module(modules, target.names.get(head))
    part: str
    for part in parts:
        if origin is None or origin[1] is not None:
            return None
        submodule: str = f"{origin[0]}.{part}"
        origin = (submodule, None) if submodule in modules else (origin[0], part)
    return origin


class Resolver:
    """Resolves a stub's names across `modules` (see the module docstring)."""

    def __init__(self, modules: Mapping[str, Module]) -> None:
        """Resolve in `modules`."""
        self.modules: Mapping[str, Module] = modules

    def resolve(self, expr: ast.Name | ast.Attribute, scope: Scope) -> Resolved | None:
        """Resolve a name an annotation uses: a type parameter, a class, an alias, a type variable.

        Returns:
          It as an atom (`arg`: a parameter an alias's argument binds), or an alias with the scope
          its value is read in; or `None` if it's none of them.

        """
        origin: Origin | None
        if isinstance(expr, ast.Name) and expr.id in scope.params:
            param: str | tuple[ast.expr, Scope] | None = scope.params[expr.id]
            if isinstance(param, tuple):
                return Atom(ARG, name=ast.unparse(param[0]), scope=param[1])
            return Atom(VAR, name=expr.id, bound=param, scope=scope)
        if (origin := self._origin(expr, scope.module)) is None or origin[1] is None:
            return None
        origin = project.canonical_origin(self.modules, origin)
        defining: Module | None = self.modules.get(origin[0])
        if defining is None or not defining.reads(origin[1]):
            return Atom(CLASS, origin=origin)
        return self._declared(defining, origin)

    def resolved_base(self, base: str, module: Module) -> Resolved | None:
        """Resolve a base `module`'s class names, as written there (`Base`, `pkg.Base[T]`).

        Returns:
          What it refers to, or `None` for a base that isn't a name.

        """
        parsed: ast.expr = parse_text(base)
        parsed = parsed.value if isinstance(parsed, ast.Subscript) else parsed
        return (
            self.resolve(parsed, Scope(module, {}, module.name))
            if isinstance(parsed, ast.Name | ast.Attribute)
            else None
        )

    def lineage(self, origin: Origin, hops: int) -> Iterator[str]:
        """Walk an installed class and its ancestors, depth first (see `Methods.lineage`).

        Yields:
          Where each is defined (`numpy.float64`), then `?` if a base can't be followed.

        """
        yield f"{origin[0]}.{origin[1]}"
        module: Module = self.modules[origin[0]]
        klass: Class | None
        # No class: a checked file's protocol, or one its module defines twice (attrs's `AttrsInstance_`).
        if module.declared is None or (klass := module.declared.classes.get(origin[1] or "")) is None:
            yield _UNFOLLOWED
            return
        base: str
        for base in klass.bases:
            resolved: Resolved | None = self.resolved_base(base, module)
            if not isinstance(resolved, Atom) or resolved.kind != CLASS:
                yield _UNFOLLOWED
            elif resolved.module is None:
                yield atom_path(resolved)
            elif hops < ALIAS_DEPTH:
                yield from self.lineage(resolved.origin, hops + 1)
            else:  # a cycle of bases
                yield _UNFOLLOWED

    def is_class(self, target: Module, name: str) -> bool:
        """Check whether a dotted name the module writes (`np.float64`) is an installed class or its alias.

        Returns:
          Whether it is.

        """
        origin: Origin | None = call_origin(self.modules, target, name)
        resolved: Resolved | None = (
            None
            if origin is None or origin[1] is None
            else self._declared_of(project.canonical_origin(self.modules, origin))
        )
        if resolved is not None and not isinstance(resolved, Atom):  # an alias: of a class?
            value: ast.expr = parse_text(resolved[0].value)
            base: ast.expr = value.value if isinstance(value, ast.Subscript) else value
            resolved = self.resolve(base, resolved[1]) if isinstance(base, ast.Name | ast.Attribute) else None
        return isinstance(resolved, Atom) and resolved.kind == CLASS and resolved.module is not None

    def _declared_of(self, origin: Origin) -> Resolved | None:
        defining: Module | None = self.modules.get(origin[0])
        return None if defining is None or not defining.reads(origin[1]) else self._declared(defining, origin)

    @staticmethod
    def _declared(module: Module, origin: Origin) -> Resolved | None:
        """Read what an installed module defines under `origin`'s name: an alias, a type variable, a class.

        Returns:
          It, or `None` for anything else (a function, a variable).

        """
        name: str = origin[1] or ""
        declared: Declarations | None = module.typing
        own: Scope = Scope(module, {}, module.name)
        if declared is not None and name in declared.aliases:
            return declared.aliases[name], own, origin
        variable: Variable | None
        if (variable := None if declared is None else declared.variables.get(name)) is not None:
            return Atom(VAR, name=name, bound=variable.bound, scope=own, constrained=variable.constrained)
        if (
            name in module.classes
            or name in module.generics
            or (declared is not None and name in declared.protocols)
        ):
            return Atom(CLASS, origin=origin, module=module)
        return None

    def _origin(self, expr: ast.Name | ast.Attribute, module: Module) -> Origin | None:
        """Find what a (dotted) name refers to in `module`: an import, its own, or a builtin.

        Returns:
          Its origin (a module's: `(name, None)`), or `None`.

        """
        if isinstance(expr, ast.Name):
            declared: Declarations | None = module.typing
            return (
                ((module.name, expr.id) if declared is not None and expr.id in declared.aliases else None)
                or module.names.get(expr.id)
                or module.guarded.get(expr.id)
                or ((BUILTINS_MODULE, expr.id) if expr.id in _BUILTINS else None)
            )
        if not isinstance(expr.value, ast.Name | ast.Attribute):
            return None
        base: Origin | None
        if (base := self._origin(expr.value, module)) is None:
            return None
        if base[1] is None:  # a module's attribute, or its submodule
            submodule: str = f"{base[0]}.{expr.attr}"
            return (submodule, None) if submodule in self.modules else (base[0], expr.attr)
        return None
