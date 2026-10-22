"""Move modules into a subpackage, and retarget every import and dotted mention of them.

  local/.venv/bin/python -m scratch.move_modules OLD.PACKAGE NEW.PACKAGE MODULE[=NEWNAME] ...
  local/.venv/bin/python -m scratch.move_modules constricter.cli constricter.cli.lsp hints guard
  local/.venv/bin/python -m scratch.move_modules constricter.fix.index constricter.fix.index.stubs \\
      stubbed stub_names=names

Each MODULE's file is moved by `git mv` into NEW.PACKAGE (made with an `__init__.py` if it's new),
renamed where `=NEWNAME` says. In the repository's Python files (constricter, stdlib_tables, tests,
scratch, hatch_build.py), `from OLD.PACKAGE import a, b` is split, the moved names imported from
NEW.PACKAGE (`as` the old name, where renamed, so uses through the module still hold), and every
dotted mention `OLD.PACKAGE.MODULE` (an import, an `importlib` or `monkeypatch` string, a
docstring) becomes `NEW.PACKAGE.NEWNAME`. Then ruff sorts each changed file's imports and formats
it. Path forms (`constricter/cli/hints.py` in pyproject.toml or the docs) and the tests' own files
are left for a hand edit: it prints what it changed and the mentions it saw outside Python files.
"""

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUFF = ROOT / "local" / ".venv" / "bin" / "ruff"
SEARCHED = ("constricter", "stdlib_tables", "tests", "scratch")
OTHERS = ("pyproject.toml", "docs", ".github", "README.md")


def files() -> list[Path]:
    """The repository's Python files."""
    found = [path for top in SEARCHED for path in sorted((ROOT / top).rglob("*.py"))]
    return [*found, ROOT / "hatch_build.py"]


def main(argv: list[str]) -> int:
    old, new, *specs = argv
    moving = {spec.partition("=")[0]: spec.partition("=")[2] or spec.partition("=")[0] for spec in specs}
    new_dir = ROOT.joinpath(*new.split("."))
    new_dir.mkdir(exist_ok=True)
    init = new_dir / "__init__.py"
    if not init.exists():
        init.write_text(f'"""{new}."""\n', encoding="utf-8")
        subprocess.run(["git", "add", str(init)], check=True, cwd=ROOT)
    for name, renamed in moving.items():
        source = ROOT.joinpath(*old.split(".")) / f"{name}.py"
        subprocess.run(["git", "mv", str(source), str(new_dir / f"{renamed}.py")], check=True, cwd=ROOT)
    # `from OLD import a, b as c`: the moved names from NEW, the rest as they were.
    from_old = re.compile(rf"^(?P<indent>[ \t]*)from {re.escape(old)} import (?P<names>[^\n(]+)$", re.MULTILINE)
    # The same over lines, in brackets: `from OLD import (\n    a,\n    b,\n)`.
    from_old_bracketed = re.compile(
        rf"^(?P<indent>[ \t]*)from {re.escape(old)} import \((?P<names>[^)]*)\)$", re.MULTILINE
    )
    # A dotted mention of a moved module, however used.
    dotted = re.compile(rf"\b{re.escape(old)}\.({'|'.join(map(re.escape, moving))})\b")
    changed: list[Path] = []
    for path in files():
        text = path.read_text(encoding="utf-8")

        def split(match: re.Match[str]) -> str:
            names = [part.strip() for part in match.group("names").split(",") if part.strip()]
            kept = [part for part in names if part.split(" as ")[0] not in moving]
            moved = []
            for part in names:
                bare, _, alias = part.partition(" as ")
                if bare in moving:
                    renamed = moving[bare]
                    moved.append(renamed if renamed == bare and not alias else f"{renamed} as {alias or bare}")
            lines = []
            if kept:
                lines.append(f"{match.group('indent')}from {old} import {', '.join(kept)}")
            if moved:
                lines.append(f"{match.group('indent')}from {new} import {', '.join(moved)}")
            return "\n".join(lines)

        rewritten = from_old.sub(split, text)
        rewritten = from_old_bracketed.sub(split, rewritten)
        rewritten = dotted.sub(lambda m: f"{new}.{moving[m.group(1)]}", rewritten)
        if rewritten != text:
            path.write_text(rewritten, encoding="utf-8")
            changed.append(path)
    if changed:
        subprocess.run([str(RUFF), "check", "--select", "I", "--fix", "-q", *map(str, changed)], check=False, cwd=ROOT)
        subprocess.run([str(RUFF), "format", "-q", *map(str, changed)], check=False, cwd=ROOT)
    print(f"moved {len(moving)} modules; rewrote {len(changed)} files")
    path_form = re.compile(rf"{old.replace('.', '/')}/({'|'.join(map(re.escape, moving))})\.py")
    for top in OTHERS:
        for path in [ROOT / top] if (ROOT / top).is_file() else sorted((ROOT / top).rglob("*")):
            if path.is_file() and path.suffix in {".toml", ".md", ".yml", ".yaml"}:
                for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
                    if path_form.search(line) or dotted.search(line):
                        print(f"  mention: {path.relative_to(ROOT)}:{number}: {line.strip()[:100]}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
