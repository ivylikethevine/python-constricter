"""Import names from the module they moved to, everywhere: after `scratch.split_module`.

  local/.venv/bin/python -m scratch.retarget_imports OLD.MODULE NEW.MODULE NAME [NAME ...]

Each `from OLD.MODULE import ...` in the repository's Python files (constricter, stdlib_tables,
tests, scratch, hatch_build.py) that names a NAME is split: those names from NEW.MODULE, the rest as
they were. Then ruff sorts each changed file's imports and formats it. A use through the module
(`old.NAME`) isn't rewritten: it's printed, for a hand edit. Edits files in place.
"""

import ast
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUFF = ROOT / "local" / ".venv" / "bin" / "ruff"
SEARCHED = ("constricter", "stdlib_tables", "tests", "scratch")


def files() -> list[Path]:
    """The repository's Python files."""
    found = [path for top in SEARCHED for path in sorted((ROOT / top).rglob("*.py"))]
    return [*found, ROOT / "hatch_build.py"]


def imported(alias: ast.alias) -> str:
    """An import's name as written."""
    return alias.name if alias.asname is None else f"{alias.name} as {alias.asname}"


def main(argv: list[str]) -> int:
    old, new, *names = argv
    moving = set(names)
    short = old.rpartition(".")[2]
    through = re.compile(rf"\b{re.escape(short)}\.({'|'.join(map(re.escape, names))})\b")
    for path in files():
        text = path.read_text(encoding="utf-8")
        if old not in text and short not in text:
            continue
        lines = text.splitlines(keepends=True)
        edits: list[tuple[int, int, str]] = []
        for node in ast.walk(ast.parse(text)):
            if not isinstance(node, ast.ImportFrom) or node.module != old or node.level:
                continue
            moved = [a for a in node.names if a.name in moving]
            if not moved:
                continue
            kept = [a for a in node.names if a.name not in moving]
            indent = re.match(r"\s*", lines[node.lineno - 1]).group(0)
            written = "".join(
                f"{indent}from {module} import {', '.join(imported(a) for a in each)}\n"
                for module, each in ((old, kept), (new, moved))
                if each
            )
            edits.append((node.lineno - 1, node.end_lineno or node.lineno, written))
        if edits:
            for start, end, written in sorted(edits, reverse=True):
                lines[start:end] = [written]
            path.write_text("".join(lines), encoding="utf-8")
            for _ in range(2):  # the imports only annotations use moved under `if TYPE_CHECKING:`, then sorted
                subprocess.run(
                    [RUFF, "check", "--fix", "--unsafe-fixes", "--select", "I001,TC001,TC002,TC003", "--quiet", path],
                    check=False,
                )
            subprocess.run([RUFF, "format", "--quiet", path], check=False)
            print(f"{path.relative_to(ROOT)}: {len(edits)} import(s)")
        for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            if through.search(line):
                print(f"{path.relative_to(ROOT)}:{number}: through the module: {line.strip()}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
