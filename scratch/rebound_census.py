"""Count a tree's `rebound` guesses by what binds the name again: an augmented assignment, or not.

  local/.venv/bin/python -m scratch.rebound_census REPORT.json ROOT

REPORT.json is `constricter --format=json --unsafe-fixes --level=suffocate --all-scopes ROOT`'s
output (ROOT the tree it checked, its paths as the report has them). For each fix whose kinds hold
`rebound`, the function around it is read for a later binding of the name by an augmented
assignment (`factor *= other`): prints how many guesses have one, how many don't, and each with
one, as `path:line name: annotation`. For sizing a rule that withholds a guess a later augmented
assignment of an unknown operand would make wrong.
"""

import ast
import json
import sys
from pathlib import Path

REBOUND = "rebound"


def _function_around(tree: ast.Module, line: int) -> ast.FunctionDef | ast.AsyncFunctionDef | None:
    found = None
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.lineno <= line <= (node.end_lineno or 0):
            if found is None or node.lineno >= found.lineno:
                found = node
    return found


def _augmented_later(function: ast.AST, name: str, line: int) -> bool:
    return any(
        isinstance(node, ast.AugAssign)
        and isinstance(node.target, ast.Name)
        and node.target.id == name
        and node.lineno > line
        for node in ast.walk(function)
    )


def main() -> None:
    report = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    root = Path(sys.argv[2])
    trees: dict[str, ast.Module] = {}
    augmented: list[str] = []
    plain = 0
    for row in report:
        fix = row.get("fix")
        if not fix or REBOUND not in fix["kinds"]:
            continue
        path = row["path"]
        if path not in trees:
            trees[path] = ast.parse(Path(path).read_text(encoding="utf-8"))
        name = row["message"].split("'")[1]
        function = _function_around(trees[path], row["line"])
        if function is not None and _augmented_later(function, name, row["line"]):
            augmented.append(f"{Path(path).relative_to(root)}:{row['line']} {name}: {fix['annotation']}")
        else:
            plain += 1
    print(f"rebound guesses: {plain + len(augmented)}; with a later augmented assignment: {len(augmented)}")
    for each in augmented:
        print("  " + each)


if __name__ == "__main__":
    main()
