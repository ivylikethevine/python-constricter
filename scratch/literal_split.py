"""Count a run's certain fixes on a `str` literal's `split()`, which typeshed types `list[LiteralString]`.

    local/.venv/bin/python -m scratch.literal_split corpus-runs/mega-11-06-2026-0949 [--show]

Reads each corpus's `records/<corpus>/<version>/fix-certain.fixes.jsonl` for the fixes annotated
`list[...]` whose kinds include `literal` and `method`, and the original line of each from
`fix-certain.patch` (the line the fix replaced). A line whose value is `"...".split()`,
`rsplit()` or `splitlines()` on a `str` literal, every argument a `str` literal or `None`, takes
typeshed's `LiteralString` overload, which basedpyright holds invariant against the `list[str]`
written. Prints the count per corpus, the other `literal+method` list fixes and the lines that
don't parse alone (a literal spanning lines), each counted; `--show` lists every one.
"""

import argparse
import ast
import json
import re
from collections import Counter
from pathlib import Path

_METHODS = frozenset({"split", "rsplit", "splitlines"})
_HUNK = re.compile(r"^@@ -(\d+)(?:,\d+)? \+\d+(?:,\d+)? @@")


def _removed(patch: Path) -> dict[tuple[str, int], str]:
    """Each line a patch removes, by its file (as `---` names it, less `a/`) and original line."""
    removed: dict[tuple[str, int], str] = {}
    path: str = ""
    old: int = 0
    for line in patch.read_text(encoding="utf-8", errors="replace").splitlines():
        if line.startswith("--- "):
            path = line[4:].split("\t")[0].removeprefix("a/")
        elif line.startswith("+++ "):
            continue
        elif hunk := _HUNK.match(line):
            old = int(hunk[1])
        elif line.startswith("-"):
            removed[path, old] = line[1:]
            old += 1
        elif line.startswith(" "):
            old += 1
    return removed


def _literal(node: ast.expr) -> bool:
    return isinstance(node, ast.Constant) and (node.value is None or isinstance(node.value, str))


def _shape(text: str) -> str:
    """`split` for a literal receiver's split, `other` for any other value, `unparsed` past one line."""
    try:
        tree: ast.Module = ast.parse(text.strip())
    except SyntaxError:
        return "unparsed"
    statement: ast.stmt | None = tree.body[0] if tree.body else None
    value: ast.expr | None = statement.value if isinstance(statement, (ast.Assign, ast.AnnAssign)) else None
    if (
        isinstance(value, ast.Call)
        and isinstance(value.func, ast.Attribute)
        and value.func.attr in _METHODS
        and isinstance(value.func.value, ast.Constant)
        and isinstance(value.func.value.value, str)
        and all(_literal(each) for each in value.args)
        and all(_literal(each.value) for each in value.keywords)
    ):
        return "split"
    return "other"


def _path_in_patch(path: str, removed: dict[tuple[str, int], str], line: int) -> str | None:
    """The removed line at `line` of the file whose patch path ends with the fix's path."""
    for (patched, number), text in removed.items():
        if number == line and (patched == path or patched.endswith("/" + path)):
            return text
    return None


def main() -> None:
    """Print the counts, per corpus and in all."""
    parser: argparse.ArgumentParser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("run", type=Path)
    parser.add_argument("--show", action="store_true", help="list every fix counted")
    arguments: argparse.Namespace = parser.parse_args()
    totals: Counter[str] = Counter()
    certain: int = 0
    for fixes in sorted(arguments.run.glob("records/*/*/fix-certain.fixes.jsonl")):
        corpus: str = fixes.parent.parent.name
        removed: dict[tuple[str, int], str] = _removed(fixes.with_name("fix-certain.patch"))
        counts: Counter[str] = Counter()
        for row in map(json.loads, fixes.read_text(encoding="utf-8").splitlines()):
            certain += 1
            kinds: set[str] = set(row["kinds"])
            if not row["annotation"].startswith("list[") or "method" not in kinds:
                continue
            text: str | None = _path_in_patch(row["path"], removed, row["line"])
            shape: str = "missing" if text is None else _shape(text)
            counts[shape] += 1
            if arguments.show:
                print(
                    f"{shape:9} {corpus}/{row['path']}:{row['line']} {row['annotation']}: {(text or '').strip()}"
                )
        if counts:
            print(f"{corpus:20} " + "  ".join(f"{shape} {counts[shape]:4}" for shape in sorted(counts)))
        totals.update(counts)
    print(f"{'all':20} " + "  ".join(f"{shape} {totals[shape]:4}" for shape in sorted(totals)))
    print(f"of {certain} certain fixes")


if __name__ == "__main__":
    main()
