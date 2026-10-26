"""Hold a run's `infer-union` fixes to the types its traced tests saw, by name, a set of mechanisms at a time.

  local/.venv/bin/python scratch/agreed_seen.py RUN_FOLDER [--min 20]

The witness judges only `fix-unsafe`'s fixes (`traced.verdicts.jsonl`), so the union's own, the
`agreed` sets among them, have no verdict. This joins each corpus's `infer-union.fixes.jsonl` with
`traced.seen.jsonl` by path, line and name, and calls a fix held where every type the trace saw is
named in its annotation (a subscript's class alone, a union's members each, `Optional`, `Self` and
the like read as anything), differing where one isn't, untold where the trace saw nothing or only
`?`. By name alone, a subclass or a protocol differs where the witness would find it holds, so a
tier's certain fixes are printed first: what a set's share is to be read against.
"""

import ast
import json
import sys
from collections import defaultdict
from pathlib import Path

_ANY = {"Any", "object", "Self", "TypeVar", "Incomplete", "Final", "ClassVar"}
_EVERY = {"Union", "Literal"}  # each argument admitted
_FIRST = {"Final", "ClassVar", "Annotated"}  # the first argument alone


def names(annotation: str) -> set[str] | None:
    """The class names an annotation admits: a subscript's base, a union's members; `None` for anything."""
    try:
        tree: ast.expr = ast.parse(annotation, mode="eval").body
    except SyntaxError:
        return None
    found: set[str] = set()

    def walk(node: ast.expr) -> bool:
        if isinstance(node, ast.BinOp) and isinstance(node.op, ast.BitOr):
            return walk(node.left) and walk(node.right)
        if isinstance(node, ast.Constant):
            found.add("None" if node.value is None else type(node.value).__name__)
            return True
        if isinstance(node, ast.Subscript):
            base: str = ast.unparse(node.value).rsplit(".", 1)[-1]
            parts: list[ast.expr] = node.slice.elts if isinstance(node.slice, ast.Tuple) else [node.slice]
            if base == "Optional":
                found.add("None")
                return walk(parts[0])
            if base in _EVERY:
                return all(walk(part) for part in parts)
            if base in _FIRST:
                return walk(parts[0])
            found.add(base)
            return True
        name: str = ast.unparse(node).rsplit(".", 1)[-1]
        if name in _ANY:
            return False
        found.add(name)
        return True

    return found if walk(tree) else None


def judged(annotation: str, seen: list[str]) -> str:
    """`held`, `differed` or `untold`, by name."""
    # The trace names a class `module:qualified.name`, a builtin bare, a generic with its arguments.
    told: list[str] = [
        one.split("[", 1)[0].rsplit(":", 1)[-1].rsplit(".", 1)[-1] for one in seen if one != "?"
    ]
    if not told:
        return "untold"
    admitted: set[str] | None = names(annotation)
    if admitted is None:
        return "held"
    return "held" if all(one in admitted for one in told) else "differed"


def main(argv: list[str]) -> int:
    run: Path = Path(argv[0])
    least: int = int(argv[argv.index("--min") + 1]) if "--min" in argv else 20
    counts: dict[tuple[str, str], dict[str, int]] = defaultdict(lambda: defaultdict(int))
    for fixes in sorted(run.glob("records/*/*/infer-union.fixes.jsonl")):
        seen_path: Path = fixes.with_name("traced.seen.jsonl")
        if not seen_path.exists():
            continue
        seen: dict[tuple[str, int, str], list[str]] = {}
        for line in seen_path.read_text(encoding="utf-8").splitlines():
            row = json.loads(line)
            seen[row["path"], row["line"], row["name"]] = row["seen"]
        for line in fixes.read_text(encoding="utf-8").splitlines():
            fix = json.loads(line)
            key = (fix["tier"], "+".join(fix["kinds"]))
            found: list[str] | None = seen.get((fix["path"], fix["line"], fix["name"]))
            verdict: str = "unseen" if found is None else judged(fix["annotation"], found)
            counts[key]["fixes"] += 1
            counts[key][verdict] += 1
    print("| Tier | Mechanisms | Fixes | Told | Held | Share |")
    print("| --- | --- | ---: | ---: | ---: | ---: |")
    for tier in ("certain", "likely", "guess"):
        rows = [(kinds, each) for (one, kinds), each in counts.items() if one == tier]
        total = defaultdict(int)
        for _, each in rows:
            for field, count in each.items():
                total[field] += count
        told = total["held"] + total["differed"]
        if total["fixes"]:
            print(
                f"| {tier} | (all) | {total['fixes']:,} | {told:,} | {total['held']:,} | {total['held'] / told:.1%} |"
                if told
                else f"| {tier} | (all) | {total['fixes']:,} | 0 | 0 | - |"
            )
        for kinds, each in sorted(rows, key=lambda item: -item[1]["fixes"]):
            told = each["held"] + each["differed"]
            if tier != "certain" and told >= least:
                print(
                    f"| {tier} | `{kinds}` | {each['fixes']:,} | {told:,} | {each['held']:,} | {each['held'] / told:.1%} |"
                )
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
