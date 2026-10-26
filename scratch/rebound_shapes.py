"""Count a run's `rebound` guesses by two shapes of the later binding, to size a rule before writing it.

  local/.venv/bin/python -m scratch.rebound_shapes corpus-runs/0.4.0-rc.2-10-17-2026-0417

For each `rebound` guess in the run's `guesses.jsonl`, finds the package's source under
`local/mega-corpora/sources` or `local/super-corpora/sources`, and the guessed name's function, and
says whether a later plain assignment to it is: past the end of the `for` loop whose target the first
binding is (`reused`: the name taken for something else), or inside an `if` that tests the name for
`None` or falsity when the fix holds `None` (`filled`). Prints each shape's guesses, those blamed
for an error, and the witness's held/differed counts, with samples.
"""

import ast
import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "local"


def _source(package: str, path: str) -> Path | None:
    for base in (ROOT / "mega-corpora" / "sources", ROOT / "super-corpora" / "sources"):
        for found in base.glob(f"{package}-*/*/{path}"):
            return found
    return None


def _function(tree: ast.AST, line: int) -> ast.AST:
    best: ast.AST = tree
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef) and node.lineno <= line <= (node.end_lineno or 0):
            if best is tree or node.lineno >= best.lineno:
                best = node
    return best


def _tests(test: ast.expr, name: str) -> bool:
    match test:
        case ast.UnaryOp(op=ast.Not(), operand=ast.Name(id=found)):
            return found == name
        case ast.Compare(left=ast.Name(id=found), ops=[ast.Is() | ast.Eq()], comparators=[ast.Constant(value=None)]):
            return found == name
        case ast.BoolOp(values=values):
            return any(_tests(each, name) for each in values)
        case _:
            return False


def shapes(scope: ast.AST, name: str, line: int, optional: bool) -> set[str]:
    loops = [node for node in ast.walk(scope) if isinstance(node, ast.For | ast.AsyncFor) and node.lineno == line
             and any(isinstance(each, ast.Name) and each.id == name for each in ast.walk(node.target))]
    later = [node for node in ast.walk(scope) if isinstance(node, ast.Assign) and node.lineno > line
             and any(isinstance(each, ast.Name) and each.id == name for each in node.targets)]
    found: set[str] = set()
    for loop in loops:
        if any(each.lineno > (loop.end_lineno or 0) for each in later):
            found.add("reused")
    if optional:
        for node in ast.walk(scope):
            if isinstance(node, ast.If) and _tests(node.test, name) and any(
                node.lineno < each.lineno <= (node.end_lineno or 0) for each in later
            ):
                found.add("filled")
    return found


def main() -> int:
    folder = Path(sys.argv[1])
    counts: Counter[str] = Counter()
    errored: Counter[str] = Counter()
    held: Counter[str] = Counter()
    differed: Counter[str] = Counter()
    samples: dict[str, list[str]] = {}
    trees: dict[Path, ast.AST] = {}
    for line in (folder / "guesses.jsonl").open(encoding="utf-8"):
        guess = json.loads(line)
        if "rebound" not in guess["kinds"].split("+"):
            continue
        counts["rebound"] += 1
        source = _source(guess["package"], guess["path"])
        if source is None:
            counts["no source"] += 1
            continue
        if source not in trees:
            trees[source] = ast.parse(source.read_text(encoding="utf-8"))
        for shape in shapes(_function(trees[source], guess["line"]), guess["name"], guess["line"], "None" in guess["annotation"]):
            counts[shape] += 1
            errored[shape] += guess["errors"] > 0
            verdict = guess["verdict"] or [0, 0, 0]
            held[shape] += verdict[0]
            differed[shape] += verdict[1]
            samples.setdefault(shape, []).append(f"{guess['package']} {guess['path']}:{guess['line']} {guess['name']}: {guess['annotation']} errors={guess['errors']} verdict={verdict}")
    print(dict(counts))
    for shape in ("reused", "filled"):
        print(f"{shape}: {counts[shape]} guesses, {errored[shape]} blamed for an error, witness held {held[shape]} differed {differed[shape]}")
        for sample in samples.get(shape, [])[:12]:
            print("   ", sample)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
