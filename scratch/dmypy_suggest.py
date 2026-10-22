"""Measure `dmypy suggest`'s signatures as a hint source for `--fix`, on a sample of each corpus.

  local/.venv/bin/python -m scratch.dmypy_suggest [CORPUS ...] [--sample N] [--daemons K] [--seed S]

Outside a sandbox: mypy's daemon talks over a unix socket. CORPUS is any of `CORPORA` (all five by
default). Each is copied twice under `local/scratch/dmypy/<corpus>/` (`plain`, `suggested`), and
`--sample` functions (all where fewer) are drawn at random from its top-level functions and methods
with an unannotated parameter or return. `--daemons` workers (default: CPUs less two) each run a
mypy daemon on one corpus's `suggested` copy and ask it `dmypy suggest` for that corpus's functions
until none are left, then take another corpus's; a worker starts a daemon only while the memory
free stays above `_RESERVE` and that corpus's largest daemon yet (or `_GUESS`), and starts it
again where a suggestion stopped it. Then, a corpus at a time, it writes what was suggested where
nothing is written (not a bare `Any`), quoted, with the modules a type names imported under
`if TYPE_CHECKING:`; fixes copies of both with `--fix` and `--fix --unsafe-fixes`
(`corpus_table.fixed_copy`, under `local/corpus-table/dmypy-*`; `CORPUS_JOBS`, 8 unless given);
and counts basedpyright's errors on each, by file, rule and message. Prints, per corpus, the
functions asked, what was written, the seconds per function, the daemons' memory, the fixes on each
copy (and gained, scaled to every function), and the errors the signatures bring. A summary goes to
`local/scratch/dmypy/<corpus>/summary.json`.
"""

import argparse
import ast
import builtins
import collections
import importlib.metadata
import importlib.util
import io
import json
import os
import queue
import random
import re
import shutil
import subprocess
import sys
import threading
import time
import tokenize
import typing
from dataclasses import dataclass, field
from functools import partial
from pathlib import Path

import psutil

os.environ.setdefault("CORPUS_JOBS", "8")

from tests.corpus import corpus_table  # noqa: E402  (reads CORPUS_JOBS on import)

ROOT = Path(__file__).resolve().parents[1]
VENV = ROOT / "local" / ".venv"
OUT = ROOT / "local" / "scratch" / "dmypy"
_SITE = VENV / "lib" / f"python{sys.version_info.major}.{sys.version_info.minor}" / "site-packages"
_SOURCES = ROOT / "local" / "corpus-sources"
# Each corpus: its source, the name its copy's package takes, and its version (an installed one's
# from its metadata). Not the standard library: mypy won't check a module named `typing` as the user's.
CORPORA: dict[str, tuple[Path, str, str]] = {
    **{name: (_SITE / name, name, importlib.metadata.version(name)) for name in ("pydantic", "django", "sqlalchemy", "pandas")},
    "pip": (_SOURCES / "pip-20.3.4" / "pip-20.3.4" / "src" / "pip", "pip", "20.3.4"),
}
_GIB = 2**30
_RESERVE = 6 * _GIB  # memory left free, whatever the daemons hold
_GUESS = 4 * _GIB  # a daemon's memory before one on its corpus has been measured
_DOTTED = re.compile(r"[A-Za-z_]\w*(?:\.[A-Za-z_]\w*)*")
_TYPING = "_dmypy_typing"


@dataclass
class Corpus:
    name: str
    base: Path  # OUT/<name>
    package: str
    version: str
    asked: "queue.Queue[tuple[Path, int]]" = field(default_factory=queue.Queue)
    wanted: int = 0
    sampled: int = 0
    answers: dict[tuple[Path, int], dict | str] = field(default_factory=dict)
    seconds: list[float] = field(default_factory=list)
    peak: int = 0
    restarts: int = 0
    daemons: int = 0
    running: int = 0

    @property
    def suggested(self) -> Path:
        return self.base / "suggested"

    @property
    def plain(self) -> Path:
        return self.base / "plain"


def _copy(source: Path, root: Path, package: str) -> None:
    if root.exists():
        assert OUT in root.parents, root
        shutil.rmtree(root)
    shutil.copytree(source, root / package, ignore=shutil.ignore_patterns("__pycache__"))


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


def _parsed(path: Path) -> ast.Module | None:
    try:
        return ast.parse(path.read_bytes())
    except (SyntaxError, ValueError):
        return None


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


def _is_module(dotted: str, project: Path, package: str) -> bool:
    parts = dotted.split(".")
    if parts[0] == package or (project / package / parts[0]).exists():
        base = project / package if parts[0] != package else project
        here = base / Path(*parts)
        if here.with_suffix(".py").exists() or (here / "__init__.py").exists():
            return True
    try:
        return importlib.util.find_spec(dotted) is not None
    except (ImportError, ValueError):
        return False


def _spelled(text: str, local: set[str], project: Path, package: str) -> tuple[str, set[str]] | None:
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
            if name in local or hasattr(builtins, name) or name == "None":
                out.append(name)
            elif hasattr(typing, name):
                out.append(f"{_TYPING}.{name}")
            else:
                return None
            continue
        module = next(
            (".".join(parts[:i]) for i in range(len(parts) - 1, 0, -1) if _is_module(".".join(parts[:i]), project, package)),
            None,
        )
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


class _Daemon:
    """One mypy daemon on a corpus's `suggested` copy, with a status file and cache of its own."""

    def __init__(self, corpus: Corpus, number: int) -> None:
        self.corpus = corpus
        self.status = corpus.suggested / f".dmypy-{number}.json"
        self.cache = corpus.suggested / f".mypy-cache-{number}"
        self.command = [str(VENV / "bin" / "dmypy"), "--status-file", str(self.status)]
        self.pid: int | None = None

    def start(self) -> None:
        options = ["--python-executable", str(VENV / "bin" / "python"), "--cache-dir", str(self.cache)]
        subprocess.run([*self.command, "start", "--", *options], cwd=self.corpus.suggested, check=True, capture_output=True)
        self.pid = json.loads(self.status.read_text())["pid"]
        checking = subprocess.Popen(
            [*self.command, "check", self.corpus.package],
            cwd=self.corpus.suggested,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        while checking.poll() is None:
            self.measure()
            time.sleep(1)

    def measure(self) -> None:
        try:
            rss = psutil.Process(self.pid).memory_info().rss if self.pid else 0
        except psutil.Error:
            return
        self.corpus.peak = max(self.corpus.peak, rss)

    def alive(self) -> bool:
        return self.status.exists() and self.pid is not None and psutil.pid_exists(self.pid)

    def suggest(self, path: Path, line: int) -> tuple[dict | str, float]:
        start = time.perf_counter()
        done = subprocess.run(
            [*self.command, "suggest", "--json", f"{path.relative_to(self.corpus.suggested)}:{line}"],
            cwd=self.corpus.suggested,
            capture_output=True,
            text=True,
            check=False,
        )
        took = time.perf_counter() - start
        self.measure()
        try:
            return json.loads(done.stdout)[0]["signature"], took
        except (json.JSONDecodeError, IndexError, KeyError, TypeError):
            last = (done.stdout + done.stderr).strip().splitlines()[-1:] or ["no output"]
            return re.sub(r"[0-9]+", "N", last[0])[:90], took

    def stop(self) -> None:
        subprocess.run([*self.command, "stop"], cwd=self.corpus.suggested, check=False, capture_output=True)
        if self.pid and psutil.pid_exists(self.pid):
            try:
                psutil.Process(self.pid).kill()
            except psutil.Error:
                pass


class _Pool:
    """The workers: each takes the corpus with the most functions left for each daemon on it."""

    def __init__(self, corpora: list[Corpus], workers: int) -> None:
        self.corpora = corpora
        self.workers = workers
        self.lock = threading.Lock()
        self.numbers = collections.Counter[str]()

    def _next(self) -> tuple[Corpus, int] | None:
        with self.lock:
            left = [c for c in self.corpora if not c.asked.empty()]
            if not left:
                return None
            chosen = max(left, key=lambda c: c.asked.qsize() / (c.running + 1))
            chosen.running += 1
            self.numbers[chosen.name] += 1
            return chosen, self.numbers[chosen.name]

    def _room(self, corpus: Corpus) -> None:
        """Wait until another daemon on `corpus` fits in the memory free."""
        while psutil.virtual_memory().available < _RESERVE + (corpus.peak or _GUESS):
            time.sleep(5)

    def work(self) -> None:
        while (chosen := self._next()) is not None:
            corpus, number = chosen
            daemon = _Daemon(corpus, number)
            try:
                self._room(corpus)
                daemon.start()
                corpus.daemons += 1
                while True:
                    try:
                        path, line = corpus.asked.get_nowait()
                    except queue.Empty:
                        break
                    answer, took = daemon.suggest(path, line)
                    corpus.answers[path, line] = answer
                    corpus.seconds.append(took)
                    if not daemon.alive():  # the suggestion stopped it
                        corpus.restarts += 1
                        daemon.stop()
                        self._room(corpus)
                        daemon.start()
            finally:
                daemon.stop()
                with self.lock:
                    corpus.running -= 1

    def run(self) -> None:
        threads = [threading.Thread(target=self.work, daemon=True) for _ in range(self.workers)]
        for thread in threads:
            thread.start()
            time.sleep(20)  # the daemons' starts spread out, so the memory each takes shows first
        report = threading.Thread(target=self._report, daemon=True)
        report.start()
        for thread in threads:
            thread.join()

    def _report(self) -> None:
        while any(not c.asked.empty() or c.running for c in self.corpora):
            time.sleep(60)
            free = psutil.virtual_memory().available / _GIB
            print(
                f"{time.strftime('%H:%M')} free {free:.1f} GB; "
                + "; ".join(f"{c.name} {len(c.answers)}/{c.sampled} ({c.running} running)" for c in self.corpora),
                flush=True,
            )


def _write(corpus: Corpus) -> collections.Counter[str]:
    """Write what was suggested into the `suggested` copy: what it did, counted."""
    counts: collections.Counter[str] = collections.Counter()
    by_file: dict[Path, list[tuple[int, dict | str]]] = collections.defaultdict(list)
    for (path, line), answer in corpus.answers.items():
        by_file[path].append((line, answer))
    for path, answers in sorted(by_file.items()):
        source = path.read_bytes().decode("utf-8", errors="surrogateescape")
        tree = _parsed(path)
        if tree is None:
            continue
        lines = source.splitlines(keepends=True)
        local = _module_names(tree)
        nodes = {node.lineno: (node, method) for node, method in _wanted(tree)}
        edits: list[tuple[int, int, str]] = []
        imports: set[str] = set()
        for line, signature in answers:
            if isinstance(signature, str):
                counts[f"no suggestion: {signature}"] += 1
                continue
            node, method = nodes[line]
            params = _params(node, method)
            types: list[str] = signature["arg_types"]
            if len(types) != len(params):
                counts["arity differs"] += 1
                continue
            for param, text in zip(params, types):
                if param.annotation is not None:
                    continue
                text = text.lstrip("*")
                counts["parameters unannotated"] += 1
                spelled = None if text == "Any" else _spelled(text, local, corpus.suggested, corpus.package)
                if spelled is None:
                    counts["parameters left (Any or unresolved)"] += 1
                    continue
                edits.append((param.end_lineno or param.lineno, param.end_col_offset or 0, f": {_quoted(spelled[0])}"))
                imports |= spelled[1]
                counts["parameters written"] += 1
            if node.returns is None:
                counts["returns unannotated"] += 1
                text = signature["return_type"]
                spelled = None if text == "Any" else _spelled(text, local, corpus.suggested, corpus.package)
                if spelled is None:
                    counts["returns left (Any or unresolved)"] += 1
                else:
                    edits.append((*_closing(lines, node), f" -> {_quoted(spelled[0])}"))
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
        path.write_bytes(new.encode("utf-8", errors="surrogateescape"))
        counts["files written"] += 1
    return counts


def _errors(project: Path, package: str) -> collections.Counter[tuple[str, str, str]]:
    """basedpyright's errors at `project` (its `package`), by file, rule and message."""
    config = {"venvPath": str(ROOT / "local"), "venv": ".venv", "typeCheckingMode": "standard", "include": [package]}
    (project / "pyrightconfig.json").write_text(json.dumps(config), encoding="utf-8")
    done = subprocess.run(
        [str(VENV / "bin" / "basedpyright"), "--project", str(project), "--outputjson"],
        capture_output=True,
        text=True,
        check=False,
    )
    try:
        found = json.loads(done.stdout)["generalDiagnostics"]
    except (json.JSONDecodeError, KeyError):
        print(f"  basedpyright gave no report at {project}: {done.stderr.strip()[-200:]}")
        return collections.Counter()
    return collections.Counter(
        (str(Path(d["file"]).relative_to(project)), d.get("rule", ""), re.sub(r"\s+", " ", d["message"]))
        for d in found
        if d["severity"] == "error"
    )


def _measured(corpus: Corpus) -> None:
    """Write the signatures, then count fixes and errors on both copies, and print it."""
    counts = _write(corpus)
    seconds = sorted(corpus.seconds)
    median = seconds[len(seconds) // 2] if seconds else 0.0
    print(f"\n== {corpus.name}: {corpus.wanted} functions with something unannotated, {corpus.sampled} asked")
    print(
        f"  {sum(seconds):.0f}s of suggestions, {sum(seconds) / max(len(seconds), 1):.1f}s each (median {median:.1f}s),"
        f" {corpus.daemons} daemons, {corpus.restarts} restarts, {corpus.peak / _GIB:.1f} GB at most each",
        flush=True,
    )
    for name, count in sorted(counts.items()):
        print(f"  {name}: {count}")
    run = partial(corpus_table._run, sys.executable)
    summary: dict[str, object] = {
        "wanted": corpus.wanted,
        "sampled": corpus.sampled,
        "seconds": seconds,
        "counts": counts,
        "peak": corpus.peak,
    }
    errors: dict[str, collections.Counter[tuple[str, str, str]]] = {}
    fixes: dict[str, int | None] = {}
    for label, root in (("plain", corpus.plain), ("suggested", corpus.suggested)):
        measured = corpus_table.Corpus(corpus.name, corpus.version, root / corpus.package)
        errors[label] = _errors(root, corpus.package)
        for kind, options in (("fixed", ()), ("guessed", ("--unsafe-fixes",))):
            under = f"dmypy-{corpus.name.replace(' ', '-')}-{label}-{kind}"
            fixed = corpus_table.fixed_copy(measured, under, options, run, second=False)
            fixes[f"{label} {kind}"] = fixed.fixed
            errors[f"{label} {kind}"] = _errors(corpus_table.WORK / under, corpus.package)
            print(f"  {label} --fix{' --unsafe-fixes' if options else ''}: {fixed.fixed} fixes, typed {fixed.typed}", flush=True)
    scale = corpus.wanted / max(corpus.sampled, 1)
    for kind in ("fixed", "guessed"):
        plain, suggested = fixes[f"plain {kind}"], fixes[f"suggested {kind}"]
        if plain is not None and suggested is not None:
            print(f"  {kind}: {suggested - plain} gained by the sample, about {(suggested - plain) * scale:.0f} for every function")
    print(f"  basedpyright errors: {', '.join(f'{k} {sum(v.values())}' for k, v in errors.items())}")
    new_errors: dict[str, int] = {}
    for kind in ("", " fixed", " guessed"):
        new = errors[f"suggested{kind}"] - errors[f"plain{kind}"]
        new_errors[kind.strip() or "unfixed"] = sum(new.values())
        print(f"  new errors, suggested{kind} over plain{kind}: {sum(new.values())}")
        for (file, rule, message), n in new.most_common(6):
            print(f"    {n} {file} {rule}: {message[:140]}")
    summary |= {"fixes": fixes, "new errors": new_errors}
    (corpus.base / "summary.json").write_text(json.dumps(summary, indent=1, default=str), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("corpora", nargs="*", default=list(CORPORA), choices=list(CORPORA))
    parser.add_argument("--sample", type=int, default=500)
    parser.add_argument("--daemons", type=int, default=max(1, (os.cpu_count() or 2) - 2))
    parser.add_argument("--seed", type=int, default=1)
    args = parser.parse_args()
    corpora: list[Corpus] = []
    for name in args.corpora:
        source, package, version = CORPORA[name]
        corpus = Corpus(name, OUT / name.replace(" ", "-"), package, version)
        _copy(source, corpus.plain, package)
        _copy(source, corpus.suggested, package)
        every = [
            (path, node.lineno)
            for path in sorted((corpus.suggested / package).rglob("*.py"))
            if (tree := _parsed(path)) is not None
            for node, _ in _wanted(tree)
        ]
        chosen = random.Random(args.seed).sample(every, min(args.sample, len(every)))
        for each in chosen:
            corpus.asked.put(each)
        corpus.wanted, corpus.sampled = len(every), len(chosen)
        corpora.append(corpus)
        print(f"{name}: {len(every)} functions, {len(chosen)} sampled", flush=True)
    start = time.perf_counter()
    _Pool(corpora, args.daemons).run()
    print(f"suggestions done in {(time.perf_counter() - start) / 60:.1f} minutes", flush=True)
    for corpus in corpora:
        _measured(corpus)


if __name__ == "__main__":
    main()
