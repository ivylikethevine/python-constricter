# SPDX-License-Identifier: MIT
"""Compare `stdlib_tables.stubs`'s reading of typeshed with `typeshed-client`'s, name by name.

  PYTHONPATH=DIR local/.venv/bin/python -m scratch.typeshed_client_compare [MODULE ...]

`DIR` holds `typeshed-client` (`uv pip install --target DIR --no-deps typeshed-client`): it isn't a
dependency. For each module of the pinned basedpyright's typeshed (or those named) and each of the
12 configurations, it reads the module both ways and counts where they differ: whether the module
exists, the names bound, which are exported, `__all__`, and each name's kind once
`typeshed-client`'s is read as `stubs` would bind it (`_kind`). It prints each difference's count
and its first examples: what a layer over `typeshed-client` would have to settle for the tables to
come out the same.
"""

import ast
import sys
from collections import Counter, defaultdict

import typeshed_client
from typeshed_client import ImportedName, OverloadedName
from typeshed_client.parser import get_dunder_all_from_info, get_import_star_names

from stdlib_tables import stubs
from stdlib_tables.generate import typeshed

_SHOWN = 6


def _ours(binding: stubs.Binding) -> str:
    if isinstance(binding, stubs.Function):
        return f"function*{len(binding.defs)}"
    if isinstance(binding, stubs.Imported):
        return f"imported {binding.module}:{binding.name}"
    if isinstance(binding, stubs.ModuleRef):
        return f"module {binding.module}"
    return type(binding).__name__.lower()


def _assigned(node: ast.AST, name: str) -> str:
    space = stubs.Namespace()
    (getattr(stubs, "assign", None) or stubs._assign)(node, space)  # on typeshed-client's node
    return _ours(space.names[name]) if name in space.names else "unbound"


def _kind(name: str, found: object) -> str:
    """Say what `stubs` would bind for what `typeshed-client` found."""
    if isinstance(found, ImportedName):
        module = ".".join(found.module_name)
        return f"module {module}" if found.name is None else f"imported {module}:{found.name}"
    if isinstance(found, OverloadedName):
        last = found.definitions[-1]
        defs = [
            each
            for each in found.definitions
            if isinstance(each, ast.FunctionDef | ast.AsyncFunctionDef)
            and not any(stubs.decorator_name(d) in stubs._ACCESSORS for d in each.decorator_list)
        ]
        if not isinstance(last, ast.FunctionDef | ast.AsyncFunctionDef):
            return _kind(name, last)
        kept: list[ast.AST] = []
        for each in defs:  # an `@overload` joins the overloads before it; any other starts again
            kept = [*kept, each] if stubs._overload(each) and all(map(stubs._overload, kept)) else [each]
        return f"function*{len(kept)}"
    if isinstance(found, ast.FunctionDef | ast.AsyncFunctionDef):
        return "function*1"
    if isinstance(found, ast.ClassDef):
        return "klass"
    return _assigned(found, name) if isinstance(found, ast.AST) else "unbound"


def main(argv: list[str]) -> int:
    root = typeshed()
    ours = stubs.Stubs(root)
    modules = argv or ours.modules()
    counts: Counter[str] = Counter()
    shown: dict[str, list[str]] = defaultdict(list)

    def differ(what: str, where: str) -> None:
        counts[what] += 1
        if len(shown[what]) < _SHOWN:
            shown[what].append(where)

    for platform, minor in stubs.CONFIGS:
        context = typeshed_client.get_search_context(
            typeshed=root / "stdlib", search_path=[], version=(3, minor), platform=platform,
        )
        for module in modules:
            at = f"{module} ({platform}, 3.{minor})"
            mine = ours.namespace(module, (platform, minor))
            theirs = typeshed_client.get_stub_names(module, search_context=context)
            counts["read"] += 1
            if (mine is None) != (theirs is None):
                differ("exists in one only: " + ("typeshed-client" if mine is None else "stubs"), at)
            if mine is None or theirs is None:
                continue
            names = {name for name in theirs if name != "__all__"}
            for name in sorted(names ^ set(mine.names)):
                differ("name in one only: " + ("typeshed-client" if name in names else "stubs"), f"{at}: {name}")
            for name in sorted(names & set(mine.names)):
                counts["names"] += 1
                bound = mine.names[name]
                if isinstance(bound, stubs.Unknown):
                    differ("unknown to stubs (an undecided condition), bound by typeshed-client", f"{at}: {name}")
                    continue
                kind = _kind(name, theirs[name].ast)
                if kind != _ours(bound):
                    differ("kind", f"{at}: {name}: stubs {_ours(bound)}, typeshed-client {kind}")
                info = theirs[name]
                exported = info.is_exported and (
                    not isinstance(info.ast, ImportedName)
                    or name == (info.ast.name or ".".join(info.ast.module_name))
                )  # `stubs` exports an import only `as` its own name, or by `*`
                if exported != (name in mine.public):
                    differ("exported", f"{at}: {name}: stubs {name in mine.public}, typeshed-client {exported}")
            listed = None
            if "__all__" in theirs:
                given = theirs["__all__"].ast
                listed = (
                    get_import_star_names(".".join(given.module_name), search_context=context)
                    if isinstance(given, ImportedName)  # `from m import __all__`
                    else get_dunder_all_from_info(theirs["__all__"])
                )
            if (None if listed is None else sorted(listed)) != (None if mine.all is None else sorted(mine.all)):
                differ("__all__", at)
    print(f"{counts.pop('read')} readings, {counts.pop('names', 0)} names in both")
    for what, count in counts.most_common():
        print(f"{count:>7}  {what}")
        for where in shown[what]:
            print(f"           {where}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
