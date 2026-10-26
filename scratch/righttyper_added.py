"""Take only the annotations RightTyper added where a package had none, onto the package's own source.

  python3 scratch/righttyper_added.py ORIGINAL_DIR ANNOTATED_DIR OUT_DIR

RightTyper (`python -m righttyper --ignore-annotations --output-files --overwrite ...`) rewrites
every signature it saw called, the ones the package annotated included. This keeps each original
file's text and adds, for each function matched by its qualified name (and its place among functions
of that name), the parameter and return annotations the original lacked (not `self` or `cls`'s), and
the imports RightTyper added, under `if TYPE_CHECKING:` at the module's end so nothing new runs.
Files are written to OUT_DIR at their paths under ORIGINAL_DIR; prints what was added.
"""

import ast
import io
import sys
import tokenize
from collections import Counter
from pathlib import Path

Edit = tuple[int, str]  # an offset in the original text, and what's inserted there


def functions(tree: ast.Module) -> dict[tuple[str, int], ast.FunctionDef | ast.AsyncFunctionDef]:
    found: dict[tuple[str, int], ast.FunctionDef | ast.AsyncFunctionDef] = {}
    seen: Counter[str] = Counter()

    def walk(node: ast.AST, prefix: str) -> None:
        for child in ast.iter_child_nodes(node):
            if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                name = f"{prefix}{child.name}"
                found[name, seen[name]] = child
                seen[name] += 1
                walk(child, f"{name}.")
            elif isinstance(child, ast.ClassDef):
                walk(child, f"{prefix}{child.name}.")
            else:
                walk(child, prefix)

    walk(tree, "")
    return found


def offsets(text: str) -> list[int]:
    starts = [0]
    for line in text.splitlines(keepends=True):
        starts.append(starts[-1] + len(line))
    return starts


def header_colon(text: str, starts: list[int], func: ast.FunctionDef | ast.AsyncFunctionDef) -> int:
    """Find the offset of the `:` that ends a def's header, past its parameters' parentheses."""
    begin = starts[func.lineno - 1] + func.col_offset
    depth = 0
    opened = False
    for token in tokenize.generate_tokens(io.StringIO(text[begin:]).readline):
        if token.type == tokenize.OP and token.string in "([{":
            depth += 1
            opened = True
        elif token.type == tokenize.OP and token.string in ")]}":
            depth -= 1
        elif token.type == tokenize.OP and token.string == ":" and depth == 0 and opened:
            row, col = token.start
            return starts[func.lineno - 1 + row - 1] + (col + func.col_offset if row == 1 else col)
    raise ValueError(f"no header end for {func.name} at line {func.lineno}")


def merged(original: str, annotated: str) -> tuple[str, Counter[str]]:
    old_tree, new_tree = ast.parse(original), ast.parse(annotated)
    old, new = functions(old_tree), functions(new_tree)
    starts = offsets(original)
    edits: list[Edit] = []
    counts: Counter[str] = Counter()
    for key, func in old.items():
        other = new.get(key)
        if other is None:
            continue
        theirs = {arg.arg: arg for arg in ast.walk(other.args) if isinstance(arg, ast.arg)}
        for arg in ast.walk(func.args):
            if not isinstance(arg, ast.arg) or arg.annotation is not None or arg.arg in {"self", "cls"}:
                continue
            given = theirs.get(arg.arg)
            if given is not None and given.annotation is not None:
                segment = ast.get_source_segment(annotated, given.annotation)
                edits.append((starts[arg.end_lineno - 1] + arg.end_col_offset, f": {segment}"))
                counts["parameters"] += 1
        if func.returns is None and other.returns is not None:
            segment = ast.get_source_segment(annotated, other.returns)
            edits.append((header_colon(original, starts, func), f" -> {segment}"))
            counts["returns"] += 1
    text = original
    for offset, inserted in sorted(edits, reverse=True):
        text = text[:offset] + inserted + text[offset:]
    had = {ast.unparse(node) for node in old_tree.body if isinstance(node, (ast.Import, ast.ImportFrom))}
    added = [
        ast.unparse(node)
        for node in new_tree.body
        if isinstance(node, (ast.Import, ast.ImportFrom))
        and ast.unparse(node) not in had
        and not (isinstance(node, ast.ImportFrom) and node.module == "__future__")
    ]
    if edits and added:
        lines = "\n".join(f"    {each}" for each in added)
        text = (
            text.rstrip("\n")
            + f"\n\nimport typing as _righttyper\n\nif _righttyper.TYPE_CHECKING:\n{lines}\n"
        )
        counts["imports"] += len(added)
    return text, counts


def main() -> int:
    original, annotated, out = (Path(each) for each in sys.argv[1:4])
    total: Counter[str] = Counter()
    files = 0
    for path in sorted(original.rglob("*.py")):
        relative = path.relative_to(original)
        theirs = annotated / relative
        source = path.read_text(encoding="utf-8")
        text, counts = (
            merged(source, theirs.read_text(encoding="utf-8")) if theirs.exists() else (source, Counter())
        )
        target = out / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        _ = target.write_text(text, encoding="utf-8")
        files += bool(counts)
        total += counts
    print(f"{files} files: {dict(total)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
