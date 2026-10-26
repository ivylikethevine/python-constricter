"""Run CI's per-file linters on the Python files changed since a commit (default `HEAD`), untracked ones too.

  local/.venv/bin/python -m scratch.lint_changed [COMMIT] [--root DIR]

`--root` lints another checkout (a worktree) with this venv's tools. Runs ruff (check and
format), flake8 in one process (its parallel mode fails in a sandbox), pylint, mypy, basedpyright,
constricter at its strictest, and import-linter over the whole package; prints each tool's
output and ends with the tools that failed.
"""

import subprocess
import sys
from pathlib import Path

_BIN = Path(sys.executable).parent


def changed(root: Path, since: str) -> list[str]:
    """List the changed and untracked `.py` files under `root` that still exist."""
    listed = subprocess.run(
        ["git", "-C", str(root), "diff", "--name-only", since, "--", "*.py"],
        capture_output=True,
        text=True,
        check=True,
    ).stdout.split()
    listed += subprocess.run(
        ["git", "-C", str(root), "ls-files", "--others", "--exclude-standard", "--", "*.py"],
        capture_output=True,
        text=True,
        check=True,
    ).stdout.split()
    return sorted(path for path in set(listed) if (root / path).is_file() and not path.startswith("scratch/"))


def main(argv: list[str]) -> int:
    root = Path(argv[argv.index("--root") + 1]) if "--root" in argv else Path.cwd()
    rest = [arg for at, arg in enumerate(argv) if arg != "--root" and (at == 0 or argv[at - 1] != "--root")]
    files = changed(root, rest[0] if rest else "HEAD")
    if not files:
        print("no changed Python files")
        return 0
    package = [path for path in files if path.startswith("constricter/")]
    tools = {
        "ruff check": [_BIN / "ruff", "check", *files],
        "ruff format": [_BIN / "ruff", "format", "--check", *files],
        "flake8": [_BIN / "flake8", "-j1", *files],
        "pylint": [_BIN / "pylint", "--score=n", *files],
        "mypy": [_BIN / "mypy", *files],
        "basedpyright": [_BIN / "basedpyright", *files],
        "constricter": [_BIN / "python", "-m", "constricter", "--level=suffocate", "--all-scopes", *files],
    }
    if package:
        tools["lint-imports"] = [_BIN / "lint-imports", "--cache-dir", "local/.import_linter_cache"]
    failed = []
    for name, command in tools.items():
        done = subprocess.run(
            [str(part) for part in command], cwd=root, capture_output=True, text=True, check=False
        )
        said = (done.stdout + done.stderr).strip()
        print(f"== {name}: {'ok' if done.returncode == 0 else 'FAILED'}")
        if done.returncode:
            failed.append(name)
            print(said)
    print(f"{len(files)} files; failed: {', '.join(failed) or 'none'}")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
