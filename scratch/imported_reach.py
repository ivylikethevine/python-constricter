"""Count a run's "imported" calls with no fix that two resolution gaps leave untyped.

  local/.venv/bin/python -m scratch.imported_reach RUN_FOLDER

Reads each corpus's `census.rows.jsonl`: a binding with neither a fix nor a guess, its reason
`imported`, with a dotted callee. Two shapes are counted, each resolved against the module files a
corpus's own sources and the installed packages hold (an installed package's stub first, then its
source, then typeshed's stub bundled with basedpyright):

- a submodule bound by `from pkg import sub`, called through (`parser.parse(text)`): the package's
  `__init__` binds `sub` by importing it from itself (`from pkg import sub`, `from . import sub`),
  or not;
- a callable instance (`tz.gettz(name)`): the callee is a module-level name declared as an instance
  (`gettz: _GetTZ`, `gettz = _GetTZ()`) whose class, in the same module, defines `__call__`, by
  whether `__call__` declares a return and whether it's overloaded.

Corpus checkouts are found under `local/corpus-sources/` and `local/mega-corpora/sources/`,
installed packages on the running interpreter's path. Prints both counts, by package.
"""

import ast
import json
import sys
from collections import Counter
from functools import lru_cache
from pathlib import Path

from constricter.fix.index.stubs.installed import bundled, locate, search_path

_ROOT = Path(__file__).resolve().parents[1]
_SOURCES = (_ROOT / "local" / "corpus-sources", _ROOT / "local" / "mega-corpora" / "sources")
_HOPS = 5


@lru_cache(maxsize=None)
def _corpus_base(corpus: str, top: str) -> Path | None:
    """Find the directory holding package `top` in corpus `corpus`'s own checkout."""
    prefix: str = corpus.replace(" ", "-").lower()
    for sources in _SOURCES:
        if not sources.is_dir():
            continue
        for unpacked in sorted(sources.iterdir()):
            if not unpacked.is_dir() or not unpacked.name.lower().startswith(prefix):
                continue
            for base in (unpacked, unpacked / "src", unpacked / "Lib", *unpacked.glob("*/")):
                if (base / top / "__init__.py").is_file() or (base / f"{top}.py").is_file():
                    return base
    return None


def _module_file(base: Path) -> Path | None:
    for path in (
        base / "__init__.pyi",
        base / "__init__.py",
        base.with_suffix(".pyi"),
        base.with_suffix(".py"),
    ):
        if path.is_file():
            return path
    return None


@lru_cache(maxsize=None)
def module_file(name: str, corpus: str) -> Path | None:
    """Find module `name`'s file: the corpus's own, else as `--fix` finds an installed one."""
    top: str = name.split(".", 1)[0]
    base: Path | None = _corpus_base(corpus, top)
    if base is not None and (found := _module_file(base.joinpath(*name.split(".")))) is not None:
        return found
    search: tuple[Path, ...] = tuple(search_path())
    if (found := locate(name, search)) is not None:
        return found
    stub: tuple[Path, bool] | None = bundled(name, search)
    if stub is not None:
        return stub[0]
    return next((f for d in search if (f := _module_file(d.joinpath(*name.split(".")))) is not None), None)


@lru_cache(maxsize=None)
def _tree(path: Path) -> ast.Module | None:
    try:
        return ast.parse(path.read_text(encoding="utf-8", errors="replace"))
    except (SyntaxError, ValueError):
        return None


def _top_level(tree: ast.Module) -> list[ast.stmt]:
    """The module's statements, through `if` and `try` bodies."""
    found: list[ast.stmt] = []
    pending: list[ast.stmt] = list(tree.body)
    while pending:
        stmt: ast.stmt = pending.pop(0)
        found.append(stmt)
        if isinstance(stmt, ast.If):
            pending.extend([*stmt.body, *stmt.orelse])
        elif isinstance(stmt, ast.Try):
            pending.extend(
                [*stmt.body, *stmt.orelse, *stmt.finalbody, *(s for h in stmt.handlers for s in h.body)]
            )
    return found


def _imported_from(stmt: ast.ImportFrom, package: str, is_package: bool) -> str:
    """The absolute module an import names (`from . import x` in a package's `__init__`)."""
    if not stmt.level:
        return stmt.module or ""
    parts: list[str] = package.split(".")
    keep: int = len(parts) - stmt.level + (1 if is_package else 0)
    return ".".join([*parts[:keep], *([stmt.module] if stmt.module else [])])


def self_bound(package: str, sub: str, corpus: str) -> bool | None:
    """Whether `package`'s `__init__` binds `sub` by importing it from itself; `None` if unread."""
    path: Path | None = module_file(package, corpus)
    tree: ast.Module | None = None if path is None else _tree(path)
    if tree is None or path is None:
        return None
    is_package: bool = path.stem == "__init__"
    for stmt in _top_level(tree):
        if isinstance(stmt, ast.ImportFrom) and any(
            (a.asname or a.name) == sub and a.name == sub for a in stmt.names
        ):
            if _imported_from(stmt, package, is_package) == package:
                return True
    return False


def _class_of(stmt: ast.stmt, name: str) -> str | None:
    """The class a module-level statement declares `name` an instance of."""
    if isinstance(stmt, ast.AnnAssign) and isinstance(stmt.target, ast.Name) and stmt.target.id == name:
        return stmt.annotation.id if isinstance(stmt.annotation, ast.Name) else None
    if (
        isinstance(stmt, ast.Assign)
        and any(isinstance(t, ast.Name) and t.id == name for t in stmt.targets)
        and isinstance(stmt.value, ast.Call)
        and isinstance(stmt.value.func, ast.Name)
    ):
        return stmt.value.func.id
    return None


def callable_instance(dotted: str, corpus: str) -> str | None:
    """Say how a callee is a callable instance: "plain", "overloaded" or "no return"; `None` if it isn't."""
    module: str
    name: str
    module, _, name = dotted.rpartition(".")
    for _ in range(_HOPS):
        path: Path | None = module_file(module, corpus) if module else None
        tree: ast.Module | None = None if path is None else _tree(path)
        if tree is None or path is None:
            return None
        stmts: list[ast.stmt] = _top_level(tree)
        onward: tuple[str, str] | None = None
        for stmt in stmts:
            if (klass := _class_of(stmt, name)) is not None:
                return _call_kind(stmts, klass)
            if isinstance(stmt, ast.ImportFrom):
                for alias in stmt.names:
                    if (alias.asname or alias.name) == name:
                        onward = (_imported_from(stmt, module, path.stem == "__init__"), alias.name)
        if onward is None:
            return None
        module, name = onward
    return None


def _call_kind(stmts: list[ast.stmt], klass: str) -> str | None:
    for stmt in stmts:
        if isinstance(stmt, ast.ClassDef) and stmt.name == klass:
            calls: list[ast.FunctionDef | ast.AsyncFunctionDef] = [
                each
                for each in stmt.body
                if isinstance(each, ast.FunctionDef | ast.AsyncFunctionDef) and each.name == "__call__"
            ]
            if not calls:
                return None
            if len(calls) > 1:
                return "overloaded"
            return "plain" if calls[0].returns is not None else "no return"
    return None


def main(argv: list[str]) -> int:
    run: Path = Path(argv[0])
    submodules: Counter[tuple[str, str]] = Counter()
    instances: Counter[tuple[str, str]] = Counter()
    rows: int = 0
    for path in sorted(run.glob("records/*/*/census.rows.jsonl")):
        for line in path.read_text(encoding="utf-8").splitlines():
            row = json.loads(line)
            if row["fixed"] or row["unsafe"] or row["unfixed"] != "imported" or not row["dotted"]:
                continue
            rows += 1
            source: str = row["source"].removeprefix("await ")
            try:
                node: ast.expr = ast.parse(source, mode="eval").body
            except SyntaxError:
                continue
            if not isinstance(node, ast.Call):
                continue
            callee: list[str] = ast.unparse(node.func).split(".")
            dotted: list[str] = row["dotted"].split(".")
            if len(callee) >= 2 and callee[0] != dotted[0] and callee[0] in dotted[1:-1]:
                at: int = dotted.index(callee[0])
                package: str = ".".join(dotted[:at])
                bound: bool | None = self_bound(package, callee[0], row["corpus"])
                verdict: str = {True: "self-bound", False: "not self-bound", None: "unread"}[bound]
                submodules[verdict, f"{package}.{callee[0]}"] += 1
            kind: str | None = callable_instance(row["dotted"], row["corpus"])
            if kind is not None:
                instances[kind, row["dotted"]] += 1
    print(f"{rows:,} imported bindings with no fix\n")
    for title, counts in (
        ("Submodule by `from pkg import sub`", submodules),
        ("Callable instance", instances),
    ):
        totals: Counter[str] = Counter()
        for (verdict, _), count in counts.items():
            totals[verdict] += count
        print(f"{title}: " + ", ".join(f"{verdict} {count:,}" for verdict, count in totals.most_common()))
        print("| Kind | Callee | Bindings |\n| --- | --- | ---: |")
        for (verdict, name), count in counts.most_common(25):
            print(f"| {verdict} | {name} | {count:,} |")
        print()
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
