# SPDX-License-Identifier: MIT
"""Move top-level definitions out of a module into a new sibling module.

  local/.venv/bin/python -m scratch.split_module SOURCE NEW DOCSTRING_FILE NAME [NAME ...] [--as OLD=NEW ...] [--ignore NAME ...]

SOURCE is a module's path (`constricter/fix/index/stubbed.py`), NEW the new module's path beside it
or elsewhere, DOCSTRING_FILE a file holding the new module's docstring (its text alone, no quotes;
`-` adds to NEW, a module already there: SOURCE's imports after its own, the definitions at its end),
and each NAME a top-level name of SOURCE to move. Each NAME's statement moves with the comments
right above it, in SOURCE's order, under SOURCE's imports (the unused then pruned by ruff). It
refuses when what moves reads a name of SOURCE's that stays: move that too, or choose another cut.

A moved private name SOURCE still reads becomes public (`_Reader` to `Reader`, or what `--as`
names), in both modules, outside attribute access (`self._x` is left alone), and SOURCE imports what
it reads of NEW; what NEW reads of SOURCE's is imported back the same way, unless both read each
other (a cycle: refused), but for the names `--ignore` gives (one the moved code is to take as a
parameter instead, by hand). A public name no local or parameter of SOURCE may have already. It
prints each line elsewhere in the repository (code, tests, docs) that names SOURCE's module with a
moved name, for a hand edit. Then ruff fixes the imports and formats both. Edits files in place: run
it on a clean tree, so `git diff` shows the move. See `scratch.module_outline` for choosing names.
"""

import ast
import re
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUFF = ROOT / "local" / ".venv" / "bin" / "ruff"
SEARCHED = ("constricter", "stdlib_tables", "tests", "docs", "scratch", "hatch_build.py", "pyproject.toml")


def bound(node: ast.stmt) -> list[str]:
    """The names a top-level statement binds."""
    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
        return [node.name]
    if isinstance(node, ast.Assign):
        return [n.id for target in node.targets for n in ast.walk(target) if isinstance(n, ast.Name)]
    if isinstance(node, (ast.AnnAssign, ast.AugAssign)) and isinstance(node.target, ast.Name):
        return [node.target.id]
    if isinstance(node, getattr(ast, "TypeAlias", ())):
        return [node.name.id]
    return []


def read_names(node: ast.AST) -> set[str]:
    """Every bare name a statement reads, and every string that could be a forward reference."""
    found = {n.id for n in ast.walk(node) if isinstance(n, ast.Name)}
    for each in ast.walk(node):
        if isinstance(each, ast.Constant) and isinstance(each.value, str):
            try:
                annotation = ast.parse(each.value.strip(), mode="eval")
            except SyntaxError:
                continue
            found |= {n.id for n in ast.walk(annotation) if isinstance(n, ast.Name)}
    return found


def module_of(path: Path) -> str:
    """The dotted module a path is."""
    return ".".join(path.resolve().relative_to(ROOT).with_suffix("").parts)


def rename(text: str, renames: dict[str, str]) -> str:
    """Rename each name outside attribute access."""
    for old, new in renames.items():
        text = re.sub(rf"(?<![.\w]){re.escape(old)}\b", new, text)
    return text


def local_names(tree: ast.AST) -> set[str]:
    """Every parameter's name and every name a function binds: what a public name mustn't be."""
    found: set[str] = set()
    for func in ast.walk(tree):
        if isinstance(func, (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda)):
            found |= {arg.arg for arg in ast.walk(func.args) if isinstance(arg, ast.arg)}
            found |= {n.id for n in ast.walk(func) if isinstance(n, ast.Name) and isinstance(n.ctx, ast.Store)}
    return found


def main(argv: list[str]) -> int:
    chosen: dict[str, str] = {}  # `--as OLD=NEW`: a public name chosen for a moved private one
    ignored: set[str] = set()  # `--ignore NAME`: a name of SOURCE's the moved code will be given instead
    while "--ignore" in argv:
        at = argv.index("--ignore")
        ignored.add(argv[at + 1])
        del argv[at : at + 2]
    while "--as" in argv:
        at = argv.index("--as")
        old, _, new_name = argv[at + 1].partition("=")
        chosen[old] = new_name
        del argv[at : at + 2]
    source, new, docstring_file, *names = argv
    source_path, new_path = Path(source), Path(new)
    if new_path.exists() and docstring_file != "-":
        sys.exit(f"{new_path} exists: pass `-` as DOCSTRING_FILE to add to it")
    text = source_path.read_text(encoding="utf-8")
    lines = text.splitlines(keepends=True)
    tree = ast.parse(text)
    spans: dict[str, tuple[int, int]] = {}  # each name's statement's lines, 0-based, end exclusive
    nodes: dict[str, ast.stmt] = {}
    imports: list[str] = []
    last_import = 0
    for node in tree.body:
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            imports.append("".join(lines[node.lineno - 1 : node.end_lineno]))
            last_import = node.end_lineno or node.lineno
            continue
        start = min([node.lineno, *(d.lineno for d in getattr(node, "decorator_list", []))]) - 1
        while start > 0 and lines[start - 1].lstrip().startswith("#"):
            start -= 1
        for name in bound(node):
            spans[name] = (start, node.end_lineno or node.lineno)
            nodes[name] = node
    missing = [name for name in names if name not in spans]
    if missing:
        sys.exit(f"not top-level names of {source_path}: {missing}")
    moved = set(names)
    statements = {id(nodes[name]): spans[name] for name in moved}
    staying = {name for name in spans if id(nodes[name]) not in statements}
    needs = {name: read_names(nodes[name]) & staying - ignored for name in moved}
    back = sorted(set().union(*needs.values()))  # what NEW imports from SOURCE
    remaining_reads: set[str] = set()
    for name in staying:
        remaining_reads |= read_names(nodes[name])
    tail = tree.body[-1]
    if not bound(tail) and not isinstance(tail, (ast.Import, ast.ImportFrom)):
        remaining_reads |= read_names(tail)  # `if __name__ == "__main__":`
    exported = sorted(name for name in moved & remaining_reads)
    if back and exported:
        for name, read in sorted(needs.items()):
            if read:
                print(f"{name} reads what stays: {', '.join(sorted(read))}")
        print(f"and what stays reads {', '.join(exported)}: an import cycle")
        return 1
    renames = {
        name: chosen.get(name, name.lstrip("_"))
        for name in (*exported, *back)
        if name.startswith("_") and not name.startswith("__")
    }
    clash = [new for new in renames.values() if new in spans]
    if clash:
        sys.exit(f"public names already taken in {source_path}: {clash}")
    taken_there: set[str] = set()
    if docstring_file == "-":
        there = ast.parse(new_path.read_text(encoding="utf-8"))
        taken_there = local_names(there) | {name for node in there.body for name in bound(node)}
        if moved & taken_there or set(renames.values()) & taken_there:
            sys.exit(f"names {new_path} binds already: {sorted((moved | set(renames.values())) & taken_there)}")
    shadowed = sorted(new for new in renames.values() if new in local_names(tree) | taken_there)
    if shadowed:
        sys.exit(f"public names a local or parameter of {source_path} has: {shadowed}; choose others with --as")
    cut = sorted(set(statements.values()))
    if cut[0][0] < last_import:
        sys.exit("a moved statement is above an import: move it by hand")
    blocks: list[tuple[int, int]] = []  # statements next to each other (blank lines apart) kept together
    for start, end in cut:
        if blocks and not "".join(lines[blocks[-1][1] : start]).strip():
            blocks[-1] = (blocks[-1][0], end)
        else:
            blocks.append((start, end))
    body = "\n\n".join("".join(lines[start:end]).rstrip("\n") + "\n" for start, end in blocks)
    gone = {index for start, end in cut for index in range(start, end)}
    kept = "".join(line for index, line in enumerate(lines) if index not in gone)
    new_module = module_of(new_path)
    if exported:
        imported = ", ".join(sorted(renames.get(name, name) for name in exported))
        kept_lines = kept.splitlines(keepends=True)
        # The source's last import ends at the same line: nothing above it was cut.
        kept_lines.insert(last_import, f"from {new_module} import {imported}\n")
        kept = "".join(kept_lines)
    header = lines[0] if lines[0].startswith("# SPDX") else ""
    docstring = "" if docstring_file == "-" else Path(docstring_file).read_text(encoding="utf-8").strip()
    back_import = f"from {module_of(source_path)} import {', '.join(sorted(renames.get(n, n) for n in back))}\n"
    if docstring_file == "-":  # added to NEW: SOURCE's imports after its own, the definitions at its end
        existing = new_path.read_text(encoding="utf-8")
        existing_lines = existing.splitlines(keepends=True)
        own = [n for n in ast.parse(existing).body if isinstance(n, (ast.Import, ast.ImportFrom))]
        at = own[-1].end_lineno if own else 0
        own_module = f"from {module_of(new_path)} import "
        added = [each for each in imports if not each.startswith(own_module)]  # no import of NEW itself
        existing_lines.insert(at, "".join(added) + (back_import if back else ""))
        created = "".join(existing_lines).rstrip("\n") + "\n\n\n" + body
    else:
        created = f'{header}"""{docstring}\n"""\n\n{"".join(imports)}{back_import if back else ""}\n\n{body}'
    backup = Path(tempfile.gettempdir()) / f"{source_path.name}.before-split"
    backup.write_text(text, encoding="utf-8")
    print(f"{source_path} as it was: {backup}")
    source_path.write_text(rename(kept, renames), encoding="utf-8")
    new_path.write_text(rename(created, renames), encoding="utf-8")
    for path in (source_path, new_path):
        for _ in range(2):  # the imports moved under `if TYPE_CHECKING:`, then sorted
            subprocess.run(
                [RUFF, "check", "--fix", "--unsafe-fixes", "--select", "F401,I001,TC001,TC002,TC003", "--quiet", path],
                check=False,
            )
        subprocess.run([RUFF, "format", "--quiet", path], check=False)
    print(f"moved {len(moved)} names; public now: {renames or 'none'}; {source_path} imports {exported}")
    print(f"{new_path} imports from {source_path}: {back}")
    module = module_of(source_path)
    short = module.rpartition(".")[2]
    pattern = re.compile(
        rf"(?:{re.escape(module)}|\b{re.escape(short)})\.({'|'.join(map(re.escape, moved))})\b"
        rf"|from {re.escape(module)} import .*\b({'|'.join(map(re.escape, moved))})\b",
    )
    found = subprocess.run(
        ["git", "-C", str(ROOT), "grep", "-n", "-E", pattern.pattern.replace("(?:", "("), "--", *SEARCHED],
        capture_output=True,
        text=True,
        check=False,
    ).stdout
    if found:
        print("references elsewhere:\n" + found)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
