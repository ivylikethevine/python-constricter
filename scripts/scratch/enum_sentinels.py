"""Count a run's checker hints that type a name bound to an enum member as the enum.

  local/.venv/bin/python -m scripts.scratch.enum_sentinels corpus-runs/mega-11-17-2026-1924

Reads the run's `infer-union` guesses (every checker's hints, `archive.GUESSES`), finds each one
whose kinds name a checker and whose statement binds `NAME = E.member` with the hint `E` (a
sentinel: typed so, it loses its literal, and pyright no longer narrows `x is NAME`). Its source
is read from the corpus's checkout under `local/corpus-suites/` or its sources under
`local/corpus-sources/`; `E` counts as an enum where a class of that name in the tree has a base
naming `Enum` or `Flag`. Prints each such hint, with the comparisons the tree makes against the
name (`is`, `is not`, `==`, `!=`) and the errors blamed on it, then the new errors of the run's
hinted steps whose message names `Literal[E.member]` for one of them, blamed or not. Corpora whose
tree isn't found are listed. Seconds on 16CPU/60GB.
"""

import ast
import json
import re
import sys
from collections import Counter
from dataclasses import dataclass
from functools import cache
from pathlib import Path

from tests.corpus import archive
from tests.corpus.run_config import directory

LOCAL = Path(__file__).resolve().parents[2] / "local"
TREES = (LOCAL / "corpus-suites", LOCAL / "corpus-sources")
SUFFIXES = ("-traced", "-run0", "-types", "")
ENUM_BASE = re.compile(r"\b\w*(Enum|Flag)\b")


@dataclass(frozen=True)
class Sentinel:
    package: str
    path: str
    line: int
    name: str
    annotation: str
    member: str
    enum: bool
    kinds: str
    errors: int
    compared: int
    scope: str
    bindings: int


def tree(package: str, path: str) -> Path | None:
    """Find the tree holding `path` for `package`: a checkout, else unpacked sources.

    Returns:
      Its root, or None.

    """
    folder: Path
    for folder in TREES:
        suffix: str
        for suffix in SUFFIXES:
            root: Path
            for root in sorted(folder.glob(f"{package}-*{suffix}")):
                if suffix == "" and not root.is_dir():
                    continue
                if (root / path).is_file():
                    return root
    return None


@cache
def parsed(file: Path) -> ast.Module | None:
    try:
        return ast.parse(file.read_bytes())
    except (SyntaxError, ValueError, OSError):
        return None


def bound(module: ast.Module, line: int, name: str) -> tuple[ast.expr, str] | None:
    """Find the value the statement at `line` binds to `name`, and the scope it's in.

    Returns:
      It and `module`, `class` or `function`, or None for another kind of statement.

    """
    scopes: list[tuple[ast.AST, str]] = [(module, "module")]
    while scopes:
        scope: ast.AST
        kind: str
        scope, kind = scopes.pop()
        child: ast.AST
        for child in ast.walk(scope) if kind == "function" else ast.iter_child_nodes(scope):
            if isinstance(child, ast.Assign) and child.lineno == line:
                if any(isinstance(target, ast.Name) and target.id == name for target in child.targets):
                    return child.value, kind
            elif kind != "function" and isinstance(child, ast.ClassDef):
                scopes.append((child, "class"))
            elif kind != "function" and isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                scopes.append((child, "function"))
            elif kind != "function" and isinstance(child, (ast.If, ast.Try, ast.With, ast.For, ast.While)):
                scopes.append((child, kind))
    return None


def bindings(root: Path, path: str, name: str) -> int:
    """Count the statements of the module at `path` binding `name` at its top level.

    Returns:
      Their number.

    """
    module: ast.Module | None = parsed(root / path)
    if module is None:
        return 0
    count: int = 0
    node: ast.stmt
    for node in module.body:
        targets: list[ast.expr] = (
            node.targets
            if isinstance(node, ast.Assign)
            else [node.target]
            if isinstance(node, (ast.AnnAssign, ast.AugAssign))
            else []
        )
        count += sum(1 for target in targets if isinstance(target, ast.Name) and target.id == name)
    return count


@cache
def enums(root: Path) -> frozenset[str]:
    """Name every class in `root` with a base naming `Enum` or `Flag`.

    Returns:
      Their names.

    """
    found: set[str] = set()
    file: Path
    for file in root.rglob("*.py"):
        if ".venv" in file.parts:
            continue
        module: ast.Module | None = parsed(file)
        if module is None:
            continue
        node: ast.AST
        for node in ast.walk(module):
            if isinstance(node, ast.ClassDef) and any(
                ENUM_BASE.search(ast.unparse(base)) for base in node.bases
            ):
                found.add(node.name)
    return frozenset(found)


def compared(root: Path, name: str) -> int:
    """Count the comparisons in `root` against `name`: `is`, `is not`, `==`, `!=`.

    Returns:
      Their number.

    """
    count: int = 0
    file: Path
    for file in root.rglob("*.py"):
        if ".venv" in file.parts:
            continue
        module: ast.Module | None = parsed(file)
        if module is None:
            continue
        node: ast.AST
        for node in ast.walk(module):
            if isinstance(node, ast.Compare):
                sides: list[ast.expr] = [node.left, *node.comparators]
                ops: list[ast.cmpop] = node.ops
                if any(isinstance(op, (ast.Is, ast.IsNot, ast.Eq, ast.NotEq)) for op in ops) and any(
                    (isinstance(side, ast.Name) and side.id == name)
                    or (isinstance(side, ast.Attribute) and side.attr == name)
                    for side in sides
                ):
                    count += 1
    return count


def sentinels(folder: Path) -> tuple[list[Sentinel], set[str]]:
    """Find the run's checker hints that type an enum member's name as its enum.

    Returns:
      Them, and the packages whose tree wasn't found.

    """
    found: list[Sentinel] = []
    missing: set[str] = set()
    row: archive.Record
    for row in archive.listed(folder, archive.GUESSES):
        kinds: str = str(row.get("kinds", ""))
        if row.get("fix") != "infer-union" or "checker" not in kinds.split("+"):
            continue
        package: str = str(row["package"])
        path: str = str(row["path"])
        root: Path | None = tree(package, path)
        if root is None:
            missing.add(package)
            continue
        module: ast.Module | None = parsed(root / path)
        name: str = str(row["name"])
        place: tuple[ast.expr, str] | None = (
            None if module is None else bound(module, int(str(row["line"])), name)
        )
        if place is None or not isinstance(place[0], ast.Attribute):
            continue
        value: ast.Attribute = place[0]
        owner: str = ast.unparse(value.value)
        annotation: str = str(row["annotation"])
        if annotation not in {owner, owner.rsplit(".", 1)[-1]}:
            continue
        found.append(
            Sentinel(
                package,
                path,
                int(str(row["line"])),
                name,
                annotation,
                value.attr,
                annotation.rsplit(".", 1)[-1] in enums(root),
                kinds,
                int(str(row.get("errors", 0))),
                compared(root, name),
                place[1],
                bindings(root, path, name) if place[1] == "module" else 0,
            )
        )
    return found, missing


def literal_errors(folder: Path, found: list[Sentinel]) -> list[str]:
    """List the hinted steps' new errors naming one of `found` as a literal.

    Returns:
      Each as `package step path:line kind message`.

    """
    literals: dict[str, set[str]] = {}
    each: Sentinel
    for each in found:
        literals.setdefault(each.package, set()).add(
            f"Literal[{each.annotation.rsplit('.', 1)[-1]}.{each.member}]"
        )
    report: dict[str, object] = json.loads((folder / "report.json").read_text(encoding="utf-8"))
    records: dict[str, dict[str, dict[str, dict[str, object]]]] = report[archive.RECORDS]  # type: ignore[assignment]
    lines: list[str] = []
    corpus: str
    versions: dict[str, dict[str, dict[str, object]]]
    for corpus, versions in records.items():
        wanted: set[str] = literals.get(directory(corpus), set()) | literals.get(corpus, set())
        if not wanted:
            continue
        steps: dict[str, dict[str, object]]
        for steps in versions.values():
            fixed: dict[str, dict[str, object]] = steps.get("types", {}).get("fixed", {})  # type: ignore[assignment]
            step: str
            record: dict[str, object]
            for step, record in fixed.items():
                error: dict[str, object]
                for error in record.get("new", []):  # type: ignore[union-attr]
                    message: str = str(error.get("message", ""))
                    if any(literal in message for literal in wanted):
                        lines.append(
                            f"{corpus} {step} {error['path']}:{error['line']} {error['kind']} {message[:140]}"
                        )
    return lines


def checkers(folder: Path) -> dict[str, str]:
    """Name the type checkers each corpus's suite runs, from the run's `types` records.

    Returns:
      Them joined by `,`, by corpus directory.

    """
    found: dict[str, str] = {}
    key: tuple[str, str, str]
    record: archive.Record
    for key, record in archive.kept(folder).items():
        if key[2] == "types":
            found[key[0]] = ",".join(str(each) for each in record.get("checks", []))  # type: ignore[union-attr]
    return found


def main() -> None:
    folder: Path = Path(sys.argv[1])
    found: list[Sentinel]
    missing: set[str]
    found, missing = sentinels(folder)
    enum: list[Sentinel] = [each for each in found if each.enum]
    print(
        f"{len(found)} checker hints type `NAME = E.member` as `E`; {len(enum)} with `E` an enum, "
        f"in {len({each.package for each in enum})} corpora; {sum(1 for each in enum if each.compared)} "
        f"compared; {sum(each.errors for each in enum)} errors blamed on them"
    )
    print("kinds:", dict(Counter(each.kinds for each in enum)))
    print("scopes:", dict(Counter(each.scope for each in enum)))
    once: list[Sentinel] = [each for each in enum if each.scope == "module" and each.bindings == 1]
    print(
        f"module constants bound once: {len(once)} in {len({each.package for each in once})} corpora, "
        f"{sum(1 for each in once if each.compared)} compared"
    )
    checks: dict[str, str] = checkers(folder)
    each: Sentinel
    for each in sorted(found, key=lambda one: (not one.enum, one.scope, one.package, one.path, one.line)):
        mark: str = "enum" if each.enum else "not-enum?"
        print(
            f"  {mark:9} {each.scope:8} {each.package} {each.path}:{each.line} {each.name}: {each.annotation} "
            f"= .{each.member} [{each.kinds}] bound={each.bindings} compared={each.compared} "
            f"errors={each.errors} checks={checks.get(each.package, '?')}"
        )
    errors: list[str] = literal_errors(folder, enum)
    print(f"{len(errors)} new errors in the hinted steps naming such a literal:")
    line: str
    for line in errors:
        print("  " + line)
    if missing:
        print("tree not found:", ", ".join(sorted(missing)))


if __name__ == "__main__":
    main()
