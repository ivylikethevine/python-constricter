"""Count a run's `copy` guesses that copy a name each arm of one statement binds, and what the witness says.

  local/.venv/bin/python -m scripts.scratch.branch_copies corpus-runs/mega-10-30-2026-0857

For each guess in the run's `guesses.jsonl` whose kinds hold `copy`, finds the package's source under
`local/mega-corpora/sources`, `local/super-corpora/sources` or `local/corpus-sources`, the
assignment at the guess's line and the name it copies (`y = x`: `x`), and reads the function around
it for a statement before the line that binds that name in two or more of its arms (`if`/`elif`/
`else`, `try`/`except`/`else`, `match` cases): the shape where each branch may bind another type,
and the fix takes the last branch's. Prints the `copy` guesses in all and those of that shape, each
split by whether `rebound` is among the kinds, with the witness's told, held and differed counts
and how many are blamed for an error, then samples of the shape. For sizing a join of the branches'
types before writing one.
"""

import ast
import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2] / "local"
BASES = (
    ROOT / "mega-corpora" / "sources",
    ROOT / "super-corpora" / "sources",
    ROOT / "corpus-sources",
    ROOT / "corpus-suites",  # the seven's checkouts; their fixed copies (`-run0`, `-traced`) passed over
)


def _source(package: str, path: str) -> Path | None:
    for base in BASES:
        for pattern in (f"{package}-*/{path}", f"{package}-*/*/{path}"):
            for found in sorted(base.glob(pattern)):
                checkout = found.relative_to(base).parts[0]
                if not any(suffix in checkout for suffix in ("-run", "-traced", "-types")):  # a fixed copy
                    return found
    return None


def _function(tree: ast.Module, line: int) -> ast.Module | ast.FunctionDef | ast.AsyncFunctionDef:
    best: ast.Module | ast.FunctionDef | ast.AsyncFunctionDef = tree
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef) and node.lineno <= line <= (
            node.end_lineno or 0
        ):
            if isinstance(best, ast.Module) or node.lineno >= best.lineno:
                best = node
    return best


def _copied(scope: ast.AST, line: int, name: str) -> str | None:
    """Name what the assignment to `name` at `line` copies, where its value is a bare name."""
    for node in ast.walk(scope):
        if isinstance(node, ast.Assign | ast.AnnAssign) and node.lineno == line:
            targets = node.targets if isinstance(node, ast.Assign) else [node.target]
            if any(isinstance(t, ast.Name) and t.id == name for t in targets) and isinstance(
                node.value, ast.Name
            ):
                return node.value.id
    return None


def _binds(body: list[ast.stmt], name: str) -> bool:
    for stmt in body:
        for node in ast.walk(stmt):
            if isinstance(node, ast.Assign | ast.AnnAssign | ast.AugAssign):
                targets = node.targets if isinstance(node, ast.Assign) else [node.target]
                if any(isinstance(t, ast.Name) and t.id == name for t in targets):
                    return True
    return False


def _arms(stmt: ast.stmt) -> list[list[ast.stmt]]:
    match stmt:
        case ast.If():
            arms = [stmt.body]
            rest = stmt.orelse
            while len(rest) == 1 and isinstance(rest[0], ast.If):
                arms.append(rest[0].body)
                rest = rest[0].orelse
            arms.append(rest)
            return arms
        case ast.Try() | ast.TryStar():
            return [stmt.body, *(h.body for h in stmt.handlers), stmt.orelse]
        case ast.Match():
            return [case.body for case in stmt.cases]
        case _:
            return []


def branched(scope: ast.AST, line: int, name: str) -> bool:
    """Check whether a statement before `line` binds `name` in two or more of its arms."""
    for node in ast.walk(scope):
        if isinstance(node, ast.stmt) and (node.end_lineno or 0) < line:
            arms = _arms(node)
            if sum(_binds(arm, name) for arm in arms) >= 2:
                return True
    return False


def main() -> int:
    folder = Path(sys.argv[1])
    counts: Counter[str] = Counter()
    told: Counter[str] = Counter()
    held: Counter[str] = Counter()
    differed: Counter[str] = Counter()
    errored: Counter[str] = Counter()
    samples: list[str] = []
    trees: dict[Path, ast.Module] = {}
    missing = 0
    for raw in (folder / "guesses.jsonl").open(encoding="utf-8"):
        guess = json.loads(raw)
        kinds = set(guess["kinds"].split("+"))
        if "copy" not in kinds:
            continue
        label = "copy+rebound" if "rebound" in kinds else "copy"
        counts[label] += 1
        source = _source(guess["package"], guess["path"])
        if source is None:
            missing += 1
            continue
        if source not in trees:
            trees[source] = ast.parse(source.read_text(encoding="utf-8", errors="replace"))
        scope = _function(trees[source], guess["line"])
        copied = _copied(scope, guess["line"], guess["name"])
        if copied is None or not branched(scope, guess["line"], copied):
            continue
        key = f"{label} branched"
        counts[key] += 1
        verdict = guess.get("verdict") or [0, 0, 0]
        if verdict[0] or verdict[1]:
            told[key] += 1
            held[key] += verdict[1] == 0
            differed[key] += verdict[1] > 0
        errored[key] += (guess.get("errors") or 0) > 0
        if len(samples) < 12 or verdict[1] > 0 or guess.get("errors"):
            samples.append(
                f"{guess['package']} {guess['path']}:{guess['line']} {guess['name']}: {guess['annotation']}"
                f" [{guess['kinds']}] <- {copied} verdict={verdict} errors={guess.get('errors')}"
            )
    for key in sorted(counts):
        line = f"{key}: {counts[key]}"
        if key in told:
            line += f"; told {told[key]}, held {held[key]}, differed {differed[key]}, errored {errored[key]}"
        print(line)
    print(f"sources missing: {missing}")
    for sample in samples[:40]:
        print(sample)
    return 0


if __name__ == "__main__":
    sys.exit(main())
