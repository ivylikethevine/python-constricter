"""Count a run's checker hints that widen string literals to `str`, and the errors near them.

  local/.venv/bin/python -m scripts.scratch.literal_hints corpus-runs/mega-11-17-2026-1924

A checker hints `x = "a" if c else how` (`how: Literal["b", "c"]`) as `Literal["a", "b", "c"]`, and
`hinted` widens it to `str`; passed on where a parameter takes only some strings, `str` is an error
(narwhals' `_how`, then `pl.concat(..., how=_how)`). Reads the run's `infer-union` guesses
(`archive.GUESSES`): each whose kinds name a checker, annotated `str`, whose statement's value can
be a string literal (a constant, or one an `if` expression, `or`, `and` or a parenthesis gives).
Its source is read from the corpus's checkout under `local/corpus-suites/` or its sources under
`local/corpus-sources/`. For each: whether the name is passed to a call in its scope, the errors
blamed on it, and the hinted steps' new errors blamed on another fix of its file within 15 lines
after it (where an error at the call is blamed on the call's own binding). Prints the counts by
corpus, then each one with an error. Seconds on 16CPU/60GB.

  local/.venv/bin/python -m scripts.scratch.literal_hints FOLDER --store

also reads the hint store (`~/.cache/constricter/hints`) for every checker hint of `str` a checker
showed as string literals alone (`Literal["a", "b"]`): those a refusal of such a hint would
withdraw, and the errors blamed on them. About two minutes for the store's 2.7 GB.
"""

import ast
import json
import re
import sys
from collections import Counter
from dataclasses import dataclass
from functools import cache
from pathlib import Path
from typing import cast

from tests.corpus import archive

LOCAL = Path(__file__).resolve().parents[2] / "local"
TREES = (LOCAL / "corpus-suites", LOCAL / "corpus-sources")
SUFFIXES = ("-traced", "-run0", "-types", "")
NEAR = 15  # lines after a hint where an error blamed on another fix may be its
STORE = Path.home() / ".cache" / "constricter" / "hints"  # every checker's hints, by file
STORE_FLAG = "--store"  # also match the run's hints of `str` to what the store shows
STRINGS = re.compile(r"Literal\[(?:'[^']*'|\"[^\"]*\")(?:, (?:'[^']*'|\"[^\"]*\"))*\]")  # strings alone


@dataclass(frozen=True)
class Widened:
    """A checker's hint of `str` for a value that can be a string literal."""

    package: str
    path: str
    line: int
    name: str
    kinds: str
    errors: int
    passed: bool
    near: tuple[str, ...]


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
                if (not suffix and not root.is_dir()) or not (root / path).is_file():
                    continue
                return root
    return None


@cache
def parsed(file: Path) -> ast.Module | None:
    """Parse `file`, once.

    Returns:
      Its tree, or None where it doesn't parse.

    """
    try:
        return ast.parse(file.read_bytes())
    except (SyntaxError, ValueError, OSError):
        return None


def literal(value: ast.expr) -> bool:
    """Check whether `value` can be a string literal.

    Returns:
      Whether it is one, or an `if` expression, `or` or `and` can give one.

    """
    if isinstance(value, ast.Constant):
        return isinstance(value.value, str)
    if isinstance(value, ast.IfExp):
        return literal(value.body) or literal(value.orelse)
    if isinstance(value, ast.BoolOp):
        return any(literal(each) for each in value.values)
    return False


def place(module: ast.Module, line: int, name: str) -> tuple[ast.expr, ast.AST] | None:
    """Find the value the statement at `line` binds to `name`, and its scope.

    Returns:
      Them, or None for another kind of statement.

    """
    scopes: list[ast.AST] = [module]
    while scopes:
        scope: ast.AST = scopes.pop()
        node: ast.AST
        for node in ast.walk(scope):
            if node is not scope and isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef):
                if node.lineno <= line <= (node.end_lineno or node.lineno):
                    scopes.append(node)
                continue
            if (
                isinstance(node, ast.Assign)
                and node.lineno == line
                and any(isinstance(target, ast.Name) and target.id == name for target in node.targets)
            ):
                return node.value, scope
    return None


def passed(scope: ast.AST, name: str) -> bool:
    """Check whether `scope` passes `name` to a call, positionally or by keyword.

    Returns:
      Whether it does.

    """
    node: ast.AST
    for node in ast.walk(scope):
        if isinstance(node, ast.Call) and any(
            isinstance(arg, ast.Name) and arg.id == name
            for arg in [*node.args, *(keyword.value for keyword in node.keywords)]
        ):
            return True
    return False


def blamed(folder: Path) -> dict[tuple[str, str], list[tuple[int, str, str, str]]]:
    """Collect the hinted steps' new errors blamed on a fix, by corpus directory and path.

    Returns:
      Each one's blamed fix's line and name, its step and its message.

    """
    found: dict[tuple[str, str], list[tuple[int, str, str, str]]] = {}
    key: tuple[str, str, str]
    record: archive.Record
    for key, record in archive.kept(folder).items():
        if key[2] != "types":
            continue
        fixed: dict[str, dict[str, object]] = record.get("fixed", {})  # type: ignore[assignment]
        step: str
        each: dict[str, object]
        for step, each in fixed.items():
            error: dict[str, object]
            for error in each.get("new", []):  # type: ignore[union-attr]
                fix: dict[str, object] | None = error.get("fix")  # type: ignore[assignment]
                if fix is not None:
                    found.setdefault((key[0], str(error["path"])), []).append(
                        (int(str(fix["line"])), str(fix["name"]), step, str(error["message"])[:120]),
                    )
    return found


def widened(folder: Path) -> tuple[list[Widened], int, set[str]]:
    """Find the run's checker hints of `str` for a value that can be a string literal.

    Returns:
      Them, the checker hints of `str` read, and the packages whose tree wasn't found.

    """
    errors: dict[tuple[str, str], list[tuple[int, str, str, str]]] = blamed(folder)
    found: list[Widened] = []
    read: int = 0
    missing: set[str] = set()
    row: archive.Record
    for row in archive.listed(folder, archive.GUESSES):
        kinds: str = str(row.get("kinds", ""))
        if row.get("fix") != "infer-union" or "checker" not in kinds.split("+") or row["annotation"] != "str":
            continue
        read += 1
        package: str = str(row["package"])
        path: str = str(row["path"])
        root: Path | None = tree(package, path)
        if root is None:
            missing.add(package)
            continue
        module: ast.Module | None = parsed(root / path)
        name: str = str(row["name"])
        line: int = int(str(row["line"]))
        at: tuple[ast.expr, ast.AST] | None = None if module is None else place(module, line, name)
        if at is None or not literal(at[0]):
            continue
        near: tuple[str, ...] = tuple(
            f"{step} blamed on {other}@{fixed}: {message}"
            for fixed, other, step, message in errors.get((package, path), [])
            if line < fixed <= line + NEAR and other != name
        )
        found.append(
            Widened(
                package, path, line, name, kinds, int(str(row.get("errors", 0))), passed(at[1], name), near
            ),
        )
    return found, read, missing


def main() -> None:
    """Print the counts, then each hint with an error blamed on it or near it."""
    folder: Path = Path(sys.argv[1])
    found: list[Widened]
    read: int
    missing: set[str]
    found, read, missing = widened(folder)
    calls: list[Widened] = [each for each in found if each.passed]
    print(
        f"{read} checker hints of `str`; {len(found)} for a value that can be a string literal, on "
        f"{len({each.package for each in found})} corpora; {len(calls)} passed to a call; "
        f"{sum(each.errors for each in found)} errors blamed on them ({sum(each.errors for each in calls)} "
        f"on those passed), {sum(bool(each.near) for each in found)} with an error blamed nearby",
    )
    print("kinds:", dict(Counter(each.kinds for each in found)))
    print("by corpus:", dict(Counter(each.package for each in found).most_common()))
    each: Widened
    for each in sorted(found, key=lambda one: (one.package, one.path, one.line)):
        if each.errors or each.near:
            print(
                f"  {each.package} {each.path}:{each.line} {each.name} [{each.kinds}] "
                f"passed={each.passed} errors={each.errors}",
            )
            note: str
            for note in each.near:
                print(f"      near: {note}")
    if missing:
        print("tree not found:", ", ".join(sorted(missing)))
    if STORE_FLAG in sys.argv:
        stored(folder)


def stored(folder: Path) -> None:
    """Print how many of the run's checker hints of `str` a checker showed as string literals.

    Matches each `infer-union` guess annotated `str` that rests on a checker to the hints the store
    keeps for its file's path and line, any checker's and round's; a hint shown `Literal["a", ...]`
    of strings alone (one `hinted` widens to `str`) counts it. Then the errors blamed on those.
    """
    rows: list[archive.Record] = [
        row
        for row in archive.listed(folder, archive.GUESSES)
        if row.get("fix") == "infer-union"
        and "checker" in str(row.get("kinds", "")).split("+")
        and row["annotation"] == "str"
    ]
    wanted: dict[tuple[str, int], list[archive.Record]] = {}
    row: archive.Record
    for row in rows:
        wanted.setdefault((Path(str(row["path"])).name, int(str(row["line"]))), []).append(row)
    hit: set[int] = set()
    entry: Path
    for entry in STORE.glob("*.json"):
        text: str = entry.read_text(encoding="utf-8")
        if "Literal[" not in text:
            continue
        found: dict[str, dict[str, list[object]]] = json.loads(text).get("found", {})
        path: str
        hints: dict[str, list[object]]
        for path, hints in found.items():
            where: str
            value: list[object]
            for where, value in hints.items():
                candidates: list[archive.Record] = wanted.get(
                    (Path(path).name, int(where.partition(":")[0])), []
                )
                if candidates and STRINGS.fullmatch(str(value[0])):
                    hit.update(
                        id(each)
                        for each in candidates
                        if path == each["path"] or path.endswith("/" + str(each["path"]))
                    )
    literal_rows: list[archive.Record] = [each for each in rows if id(each) in hit]
    blamed_rows: list[archive.Record] = [each for each in literal_rows if int(str(each.get("errors", 0)))]
    print(
        f"store: {len(literal_rows)} of {len(rows)} checker hints of `str` shown as string literals, on "
        f"{len({each['package'] for each in literal_rows})} corpora; {len(blamed_rows)} blamed "
        f"{sum(int(str(each.get('errors', 0))) for each in blamed_rows)} errors",
    )
    print("kinds:", dict(Counter(str(each["kinds"]) for each in literal_rows)))
    verdicts: list[list[int]] = [cast("list[int]", each["verdict"]) for each in literal_rows]
    print(
        "held by a traced run:",
        sum(1 for verdict in verdicts if verdict[0]),
        "differed:",
        sum(1 for verdict in verdicts if verdict[1]),
    )
    calls: int = 0
    for row in literal_rows:
        root: Path | None = tree(str(row["package"]), str(row["path"]))
        module: ast.Module | None = None if root is None else parsed(root / str(row["path"]))
        at: tuple[ast.expr, ast.AST] | None = (
            None if module is None else place(module, int(str(row["line"])), str(row["name"]))
        )
        calls += at is not None and passed(at[1], str(row["name"]))
    print(f"passed to a call in their scope: {calls}")
    for row in blamed_rows:
        print(
            f"  {row['package']} {row['path']}:{row['line']} {row['name']} [{row['kinds']}] errors={row['errors']}"
        )


if __name__ == "__main__":
    main()
