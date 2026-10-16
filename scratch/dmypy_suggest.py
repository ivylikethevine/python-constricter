# SPDX-License-Identifier: MIT
"""Measure `dmypy suggest`'s signatures as a hint source for `--fix`, on pydantic.

  local/.venv/bin/python -m scratch.dmypy_suggest [--limit N]

Outside a sandbox: mypy's daemon talks over a unix socket. Copies the installed pydantic twice under
`local/scratch/dmypy/` (`plain`, `suggested`). In `suggested` it asks `dmypy suggest` for each
top-level function and method with an unannotated parameter or return, and writes what it suggests
where nothing is written (not a bare `Any`), quoted, with the modules a type names imported under
`if TYPE_CHECKING:`; `--limit` asks for the first N functions alone. Then it fixes copies of both
with `--fix` and with `--fix --unsafe-fixes` (`corpus_table.fixed_copy`, under
`local/corpus-table/dmypy-*`), and counts basedpyright's errors on each, by file, rule and message.
Prints the functions asked, the parameters and returns written, the seconds per function, the
fixes on each copy, and the errors each copy's signatures bring. `CORPUS_JOBS` sets `--fix`'s
workers (4 unless given).
"""

import argparse
import ast
import builtins
import collections
import importlib.util
import io
import json
import os
import re
import shutil
import subprocess
import sys
import time
import tokenize
from functools import partial
from pathlib import Path

os.environ.setdefault("CORPUS_JOBS", "4")

from tests.corpus import corpus_table  # noqa: E402  (reads CORPUS_JOBS on import)

ROOT = Path(__file__).resolve().parents[1]
VENV = ROOT / "local" / ".venv"
OUT = ROOT / "local" / "scratch" / "dmypy"
VERSION = "2.13.5"
_DOTTED = re.compile(r"[A-Za-z_]\w*(?:\.[A-Za-z_]\w*)*")
_TYPING = "_dmypy_typing"


def _installed() -> Path:
    spec = importlib.util.find_spec("pydantic")
    assert spec is not None and spec.origin is not None
    return Path(spec.origin).parent


def _copy(label: str) -> Path:
    """A fresh copy of pydantic at `OUT/<label>/pydantic`; its parent is the project root."""
    root = OUT / label
    if root.exists():
        assert root.parent == OUT, root
        shutil.rmtree(root)
    shutil.copytree(_installed(), root / "pydantic", ignore=shutil.ignore_patterns("__pycache__"))
    return root


def _wanted(tree: ast.Module) -> list[tuple[ast.FunctionDef | ast.AsyncFunctionDef, bool]]:
    """Top-level functions and methods (any class depth) with something unannotated; and whether a method."""
    found: list[tuple[ast.FunctionDef | ast.AsyncFunctionDef, bool]] = []

    def visit(body: list[ast.stmt], in_class: bool) -> None:
        for node in body:
            if isinstance(node, ast.ClassDef):
                visit(node.body, True)
            elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                names = {ast.unparse(d).rsplit(".", 1)[-1] for d in node.decorator_list}
                if "overload" in names:
                    continue
                if any(p.annotation is None for p in _params(node, in_class)) or node.returns is None:
                    found.append((node, in_class))
            elif isinstance(node, (ast.If, ast.Try)):
                visit(node.body, in_class)
                visit(getattr(node, "orelse", []), in_class)

    visit(tree.body, False)
    return found


def _params(node: ast.FunctionDef | ast.AsyncFunctionDef, method: bool) -> list[ast.arg]:
    """Its parameters in mypy's order, a method's first left out unless it's a static method."""
    a = node.args
    every = [*a.posonlyargs, *a.args, *([a.vararg] if a.vararg else []), *a.kwonlyargs, *([a.kwarg] if a.kwarg else [])]
    static = any(ast.unparse(d).endswith("staticmethod") for d in node.decorator_list)
    return every[1:] if method and not static and every else every


def _module_names(tree: ast.Module) -> set[str]:
    names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            names.update((a.asname or a.name).split(".")[0] for a in node.names)
        elif isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
            names.add(node.name)
        elif isinstance(node, ast.Name) and isinstance(node.ctx, ast.Store):
            names.add(node.id)
    return names


def _is_module(dotted: str, copy: Path) -> bool:
    if dotted.split(".")[0] == "pydantic":
        base = copy.parent / Path(*dotted.split("."))
        return base.with_suffix(".py").exists() or (base / "__init__.py").exists()
    try:
        return importlib.util.find_spec(dotted) is not None
    except (ImportError, ValueError):
        return False


def _spelled(text: str, local: set[str], copy: Path) -> tuple[str, set[str]] | None:
    """`text` with each name resolvable here, and the modules to import; `None` if one isn't."""
    imports: set[str] = set()
    out: list[str] = []
    at = 0
    for match in _DOTTED.finditer(text):
        name = match.group()
        out.append(text[at : match.start()])
        at = match.end()
        parts = name.split(".")
        if len(parts) == 1:
            if name in local or hasattr(builtins, name) or name in {"None"}:
                out.append(name)
            elif hasattr(__import__("typing"), name):
                out.append(f"{_TYPING}.{name}")
            else:
                return None
            continue
        module = next((".".join(parts[:i]) for i in range(len(parts) - 1, 0, -1) if _is_module(".".join(parts[:i]), copy)), None)
        if module is None:
            if parts[0] in local:
                out.append(name)
                continue
            return None
        imports.add(module)
        out.append(name)
    out.append(text[at:])
    return "".join(out), imports


def _quoted(text: str) -> str:
    return repr(text) if '"' in text else f'"{text}"'


def _closing(lines: list[str], node: ast.FunctionDef | ast.AsyncFunctionDef) -> tuple[int, int]:
    """Where the parameter list's `)` ends: (line, column), 1-based line."""
    source = "".join(lines[node.lineno - 1 :])
    depth = 0
    seen = False
    for token in tokenize.generate_tokens(io.StringIO(source).readline):
        if token.type == tokenize.OP and token.string == "(":
            depth += 1
            seen = True
        elif token.type == tokenize.OP and token.string == ")":
            depth -= 1
            if seen and depth == 0:
                return node.lineno + token.end[0] - 1, token.end[1]
    raise ValueError(node.name)


def _suggest(root: Path, target: str) -> tuple[dict | list[str], float]:
    start = time.perf_counter()
    done = subprocess.run(
        [str(VENV / "bin" / "dmypy"), "--status-file", str(root / ".dmypy.json"), "suggest", "--json", target],
        cwd=root,
        capture_output=True,
        text=True,
        check=False,
    )
    took = time.perf_counter() - start
    try:
        return json.loads(done.stdout)[0]["signature"], took
    except (json.JSONDecodeError, IndexError, KeyError, TypeError):
        return (done.stdout + done.stderr).strip().splitlines()[-1:] or ["no output"], took


def _write(root: Path, limit: int | None) -> collections.Counter[str]:
    """Write `dmypy suggest`'s signatures into the copy at `root`: what it did, counted."""
    dmypy = [str(VENV / "bin" / "dmypy"), "--status-file", str(root / ".dmypy.json")]
    counts: collections.Counter[str] = collections.Counter()
    start = time.perf_counter()

    def started() -> None:
        subprocess.run([*dmypy, "start", "--", "--python-executable", str(VENV / "bin" / "python")], cwd=root, check=True, capture_output=True)
        subprocess.run([*dmypy, "check", "pydantic"], cwd=root, check=False, capture_output=True)

    started()
    print(f"daemon started and checked: {time.perf_counter() - start:.1f}s")
    asked = 0
    seconds = 0.0
    try:
        for path in sorted((root / "pydantic").rglob("*.py")):
            source = path.read_text(encoding="utf-8")
            try:
                tree = ast.parse(source)
            except SyntaxError:
                continue
            lines = source.splitlines(keepends=True)
            local = _module_names(tree)
            edits: list[tuple[int, int, str]] = []
            imports: set[str] = set()
            for node, method in _wanted(tree):
                if limit is not None and asked >= limit:
                    break
                asked += 1
                signature, took = _suggest(root, f"{path.relative_to(root)}:{node.lineno}")
                seconds += took
                if not (root / ".dmypy.json").exists():  # the suggestion crashed the daemon
                    counts["daemon restarts"] += 1
                    started()
                if isinstance(signature, list):
                    counts[f"no suggestion: {re.sub(r'[0-9]+', 'N', signature[0])[:90]}"] += 1
                    continue
                params = _params(node, method)
                types: list[str] = signature["arg_types"]
                if len(types) != len(params):
                    counts["arity differs"] += 1
                    continue
                for param, text in zip(params, types):
                    if param.annotation is not None:
                        continue
                    text = text.lstrip("*")
                    spelled = None if text == "Any" else _spelled(text, local, root / "pydantic")
                    counts["parameters unannotated"] += 1
                    if spelled is None:
                        counts["parameters left (Any or unresolved)"] += 1
                        continue
                    edits.append((param.end_lineno or param.lineno, param.end_col_offset or 0, f": {_quoted(spelled[0])}"))
                    imports |= spelled[1]
                    counts["parameters written"] += 1
                if node.returns is None:
                    counts["returns unannotated"] += 1
                    text = signature["return_type"]
                    spelled = None if text == "Any" else _spelled(text, local, root / "pydantic")
                    if spelled is None:
                        counts["returns left (Any or unresolved)"] += 1
                    else:
                        line, column = _closing(lines, node)
                        edits.append((line, column, f" -> {_quoted(spelled[0])}"))
                        imports |= spelled[1]
                        counts["returns written"] += 1
                        counts["returns written None"] += spelled[0] == "None"
            if not edits:
                continue
            for line, column, text in sorted(edits, reverse=True):
                lines[line - 1] = lines[line - 1][:column] + text + lines[line - 1][column:]
            block = [f"import typing as {_TYPING}\n", f"if {_TYPING}.TYPE_CHECKING:\n"]
            block += [f"    import {module}\n" for module in sorted(imports)] or ["    pass\n"]
            first = next(
                (
                    stmt
                    for at, stmt in enumerate(tree.body)
                    if not (at == 0 and isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Constant))
                    and not (isinstance(stmt, ast.ImportFrom) and stmt.module == "__future__")
                ),
                None,
            )
            where = (first.lineno - 1) if first is not None else len(lines)
            new = "".join(lines[:where] + block + lines[where:])
            try:
                ast.parse(new)
            except SyntaxError:
                counts["files left (would not parse)"] += 1
                continue
            path.write_text(new, encoding="utf-8")
            counts["files written"] += 1
    finally:
        subprocess.run([*dmypy, "stop"], cwd=root, check=False, capture_output=True)
    counts["functions asked"] = asked
    print(f"dmypy suggest: {asked} functions, {seconds:.1f}s, {seconds / max(asked, 1):.2f}s each")
    return counts


def _errors(project: Path) -> collections.Counter[tuple[str, str, str]]:
    """basedpyright's errors at `project` (its `pydantic`), by file, rule and message."""
    (project / "pyrightconfig.json").write_text(
        json.dumps({"venvPath": str(ROOT / "local"), "venv": ".venv", "typeCheckingMode": "standard", "include": ["pydantic"]}),
        encoding="utf-8",
    )
    done = subprocess.run([str(VENV / "bin" / "basedpyright"), "--project", str(project), "--outputjson"], capture_output=True, text=True, check=False)
    found = json.loads(done.stdout)["generalDiagnostics"]
    return collections.Counter(
        (str(Path(d["file"]).relative_to(project)), d.get("rule", ""), re.sub(r"\s+", " ", d["message"]))
        for d in found
        if d["severity"] == "error"
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int)
    limit: int | None = parser.parse_args().limit
    plain = _copy("plain")
    suggested = _copy("suggested")
    for name, count in sorted(_write(suggested, limit).items()):
        print(f"  {name}: {count}")
    run = partial(corpus_table._run, sys.executable)
    errors: dict[str, collections.Counter[tuple[str, str, str]]] = {}
    for label, root in (("plain", plain), ("suggested", suggested)):
        corpus = corpus_table.Corpus("pydantic", VERSION, root / "pydantic")
        errors[label] = _errors(root)
        for kind, options in (("fixed", ()), ("guessed", ("--unsafe-fixes",))):
            under = f"dmypy-{label}-{kind}"
            fixed = corpus_table.fixed_copy(corpus, under, options, run, second=False)
            errors[f"{label} {kind}"] = _errors(corpus_table.WORK / under)
            print(f"{label} --fix{' --unsafe-fixes' if options else ''}: {fixed.fixed} fixes, typed {fixed.typed}")
    print(f"basedpyright errors: {', '.join(f'{k} {sum(v.values())}' for k, v in errors.items())}")
    for kind in ("", " fixed", " guessed"):
        new = errors[f"suggested{kind}"] - errors[f"plain{kind}"]
        print(f"new errors, suggested{kind} over plain{kind}: {sum(new.values())}")
        for (file, rule, message), n in new.most_common(8):
            print(f"  {n} {file} {rule}: {message[:140]}")


if __name__ == "__main__":
    main()
