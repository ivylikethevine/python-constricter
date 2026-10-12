# SPDX-License-Identifier: MIT
"""Count what `--fix` still can't type in each corpus, and why: the numbers docs/ROADMAP.md quotes.

  local/.venv/bin/python -m tests.corpus.corpus_untyped                    # every corpus, as Markdown
  local/.venv/bin/python -m tests.corpus.corpus_untyped --top 60           # more categories per table
  local/.venv/bin/python -m tests.corpus.corpus_untyped --rows rows.jsonl  # and every binding, one a line

The corpora are `tests/corpus/corpus_table.py`'s. Each is checked by this checkout at `suffocate`
with `all-scopes` (`--format=json`), and every untyped binding it reports (LVA001, LVA002, LVA004)
is classified from the source: the statement that binds it (`assign`, `unpack`, `loop`, `with`,
`walrus`, ...), the shape of its value (`call: self.method()`, `attr: chained`, `empty list`, ...),
its scope, whether its function declares anything (a module's or class's body counts as annotated
when its file does), whether `--fix` offers a fix (and whether only as a guess), and, for a call or
attribute reached through an import, what it resolves to (`os.path.join`) and where that comes
from: the standard library, the corpus's own package, or a third-party one.

It prints, as Markdown: each corpus's untyped bindings, those with no fix at all, and how many of
those are in functions with no annotations; the commonest shapes with no fix in annotated
functions, in unannotated ones, and at module level; the groups the roadmap's items are sized by;
and calls through an import, by where it comes from. Files that don't parse as
Python 3 (Twisted's Python 2) are left out, their count on standard error.
"""

import argparse
import ast
import json
import re
import subprocess  # runs this checkout's constricter on each corpus
import sys
import tokenize
import warnings
from collections import Counter
from collections.abc import Callable, Iterable, Mapping, Sequence
from pathlib import Path
from typing import Final, NamedTuple, TextIO, TypeAlias, cast

from tests.corpus.corpus_table import ALL_SCOPES, WORK, Corpus, corpora
from tests.corpus.untyped_shapes import Module, Names, binding_of, declares, names_in, origin_of, shape

_Json: TypeAlias = "str | int | bool | list[_Json] | dict[str, _Json] | None"
_Result: TypeAlias = dict[str, _Json]
_Scopes: TypeAlias = ast.FunctionDef | ast.AsyncFunctionDef | ast.Lambda
_Groups: TypeAlias = Mapping[str, frozenset[str]]  # each group's label, and the shapes in it
_Section: TypeAlias = tuple[str, list[str]]  # a heading, and the lines under it

_CODES: Final = frozenset({"LVA001", "LVA002", "LVA004"})
# How this checkout's constricter checks each corpus (its warnings about the corpus's own code, off).
_CHECK: Final = ("-W", "ignore", "-m", "constricter", "--format=json", "--level=suffocate")
_NAME: Final = re.compile(r"'([^']+)'")
_FUNCTION: Final = "function"
_MODULE: Final = "module"
_NOT_A_NAME: Final = "other (not a Name store)"
_UNKNOWN: Final = "?"
_STDLIB_ORIGIN: Final = "stdlib"
_OWN: Final = "own package"
_THIRD_PARTY: Final = "third-party"
_MODULE_CALL: Final = "call: module.func()"
_TOP: Final = 30
_TOP_MODULES: Final = 8
_SOURCE_WIDTH: Final = 120  # how much of a value's source a row keeps
_COMPREHENSIONS: Final = (ast.ListComp, ast.SetComp, ast.DictComp, ast.GeneratorExp)
# A call to a name an import binds: `f()` after `from m import f`, or `f.g()`.
_IMPORTS: Final = frozenset({"call: imported function", "call: imported class", "call: imported.attr()"})
# The groups the roadmap's items are sized by, each a set of shapes (whatever the statement).
_GROUPS: Final[_Groups] = {
    "`self.x` read": frozenset({"attr: self.x"}),
    "`self.method()` call": frozenset({"call: self.method()"}),
    "Chained `.method()` call": frozenset({"call: chained .method()"}),
    "Call to an imported function or class": _IMPORTS,
    "`module.func()` call": frozenset({_MODULE_CALL}),
    "`getattr(...)`": frozenset({"call: builtin getattr()"}),
    "Empty container": frozenset({"empty list", "empty dict", "empty set"}),
    "Comprehension of unknown elements": frozenset(
        {f"{kind.__name__} (unknown elements)" for kind in _COMPREHENSIONS},
    ),
}


class Binding(NamedTuple):
    """One untyped binding, classified: what `--rows` writes a line of."""

    corpus: str
    path: str  # relative to the corpus's root
    line: int
    name: str
    code: str
    fixed: bool  # `--fix` offers a fix, certain or a guess
    unsafe: bool  # only as a guess
    scope: str  # `function`, `class`, `module`, or `?` when it isn't a plain name's binding
    annotated: bool  # its function declares something (a body outside one: its file does)
    binding: str  # the statement that binds it
    shape: str  # its value's
    dotted: str  # what a call or attribute resolves to through an import (`os.path.join`), or ""
    origin: str  # where that comes from: `stdlib`, `own package`, `third-party`, or ""
    source: str  # the value's source, cut short


def _read(path: Path) -> ast.Module | None:
    """Parse a file as the check did, with type comments if they parse.

    Returns:
      Its tree, or `None` if it doesn't parse as Python 3 (or can't be read).

    """
    try:
        source: str = _source(path)
    except (SyntaxError, UnicodeDecodeError, OSError):
        return None
    return _parsed(source, type_comments=True) or _parsed(source, type_comments=False)


def _parsed(source: str, *, type_comments: bool) -> ast.Module | None:
    """Parse source quietly: an old file's invalid escape sequences only warn.

    Returns:
      Its tree, or `None` if it doesn't parse.

    """
    with warnings.catch_warnings(action="ignore"):
        try:
            return ast.parse(source, type_comments=type_comments)
        except SyntaxError:
            return None


def _source(path: Path) -> str:
    """Read a file's source in the encoding it declares (PEP 263, or a BOM).

    Returns:
      It.

    """
    file: TextIO
    with tokenize.open(path) as file:
        return file.read()


class _File(NamedTuple):
    """One parsed file of a corpus, and what's needed to classify its untyped bindings."""

    corpus: Corpus
    path: Path
    module: Module
    stores: Mapping[tuple[int, int, str], ast.Name]  # each name's first store, by line and column (from 1)


def _file(corpus: Corpus, path: Path) -> _File | None:
    """Read one file of a corpus.

    Returns:
      It, or `None` if it doesn't parse.

    """
    tree: ast.Module | None
    if (tree := _read(path)) is None:
        return None
    stores: dict[tuple[int, int, str], ast.Name] = {}
    node: ast.AST
    for node in ast.walk(tree):
        if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Store):
            _ = stores.setdefault((node.lineno, node.col_offset + 1, node.id), node)
    return _File(corpus, path, Module(tree), stores)


class _Description(NamedTuple):
    """`Binding`'s fields from `scope` on: how one binding was classified."""

    scope: str
    annotated: bool
    binding: str
    shape: str
    dotted: str
    origin: str
    source: str


def _classified(file: _File, result: _Result, scopes: dict[int, tuple[str, bool, Names]]) -> Binding:
    """Classify one untyped binding the check reported in `file`.

    `scopes` caches each scope's kind, whether it's annotated, and its names, by the scope's `id`.

    Returns:
      It.

    """
    found: re.Match[str] | None = _NAME.search(str(result["message"]))
    name: str = found.group(1) if found else _UNKNOWN
    fix: _Result | None = cast("_Result | None", result["fix"])
    line: int = cast("int", result["line"])
    node: ast.Name | None = file.stores.get((line, cast("int", result["column"]), name))
    described: _Description = (
        _Description(_UNKNOWN, file.module.annotated, _NOT_A_NAME, "-", "", "", "")
        if node is None
        else _described(node, file, scopes)
    )
    return Binding(
        file.corpus.name,
        str(file.path.relative_to(file.corpus.root)),
        line,
        name,
        str(result["code"]),
        fix is not None,
        fix is not None and bool(fix["unsafe"]),
        *described,
    )


def _described(
    node: ast.Name,
    file: _File,
    scopes: dict[int, tuple[str, bool, Names]],
) -> _Description:
    """Describe the binding of `node`: its scope, statement, value and what that resolves to.

    Returns:
      It.

    """
    scope: ast.AST | None = file.module.scope(node)
    if id(scope) not in scopes:
        scopes[id(scope)] = _scope(scope, file.module)
    kind: str
    annotated: bool
    names: Names
    kind, annotated, names = scopes[id(scope)]
    binding: str
    value: ast.expr | None
    binding, value = binding_of(node, file.module)
    value_shape: str
    dotted: str
    value_shape, dotted = shape(value, names)
    return _Description(
        kind,
        annotated,
        binding,
        value_shape,
        dotted,
        origin_of(dotted, file.corpus.name) if dotted else "",
        "" if value is None else ast.unparse(value)[:_SOURCE_WIDTH],
    )


def _scope(scope: ast.AST | None, module: Module) -> tuple[str, bool, Names]:
    """Describe a scope: its kind, whether it's annotated, and what a name in it can mean.

    Returns:
      `function` (and whether it declares anything), `class` or `module` (and whether its file
      does), and its names.

    """
    if isinstance(scope, _Scopes):
        return _FUNCTION, declares(scope), names_in(scope, module)
    kind: str = "class" if isinstance(scope, ast.ClassDef) else _MODULE
    return kind, module.annotated, Names(module, {}, frozenset())


def census(corpus: Corpus, output: str | None = None) -> tuple[list[Binding], int]:
    """Check one corpus with this checkout and classify every untyped binding it reports.

    `output`: such a check's, where the caller made it (`--format=json`, at `suffocate`).

    Returns:
      The bindings, and how many reported ones were in files that don't parse (left out).

    """
    # From `WORK`, where no `pyproject.toml` configures it. It exits 2, saying why, for a file it
    # can't read (the standard library's tests have some; Twisted's Python 2): the report has the rest.
    if output is None:
        output = subprocess.run(
            [sys.executable, *_CHECK, *ALL_SCOPES, str(corpus.root)],
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            check=False,
            cwd=WORK,
            encoding="utf-8",
        ).stdout
    results: list[_Result] = [
        result for result in cast("list[_Result]", json.loads(output or "[]")) if result["code"] in _CODES
    ]
    by_path: dict[str, list[_Result]] = {}
    result: _Result
    for result in results:
        by_path.setdefault(str(result["path"]), []).append(result)
    bindings: list[Binding] = []
    unparsed: int = 0
    path: str
    reported: list[_Result]
    for path, reported in sorted(by_path.items()):
        file: _File | None
        if (file := _file(corpus, Path(path))) is None:
            unparsed += len(reported)
            continue
        scopes: dict[int, tuple[str, bool, Names]] = {}
        bindings.extend(_classified(file, one, scopes) for one in reported)
    return bindings, unparsed


def _share(part: int, whole: int) -> str:
    """Write `part` with its percentage of `whole`.

    Returns:
      It, as `1,234 (5.6%)`.

    """
    return f"{part:,} ({part / whole:.1%})" if whole else f"{part:,}"


def _table(header: Sequence[str], rows: Iterable[Sequence[str]]) -> list[str]:
    """Lay a table out as Markdown, its first column left-aligned and the rest right-aligned.

    Returns:
      Its lines.

    """
    every: list[Sequence[str]] = [header, *rows]
    widths: list[int] = [max(3, *(len(row[i]) for row in every)) for i in range(len(header))]

    def line(row: Sequence[str]) -> str:
        return (
            "| "
            + " | ".join(
                cell.ljust(widths[i]) if not i else cell.rjust(widths[i]) for i, cell in enumerate(row)
            )
            + " |"
        )

    separator: list[str] = ["-" * widths[0], *("-" * (w - 1) + ":" for w in widths[1:])]
    return [line(header), "| " + " | ".join(separator) + " |", *(line(row) for row in every[1:])]


def _ranked(counts: Counter[str], top: int) -> list[tuple[str, int]]:
    """Rank counts, largest first, ties by name, so the tables don't vary from run to run.

    Returns:
      The first `top`.

    """
    return sorted(counts.items(), key=lambda item: (-item[1], item[0]))[:top]


def _totals(bindings: Sequence[Binding], corpora_seen: Sequence[str]) -> list[str]:
    """Tabulate each corpus's untyped bindings, those with no fix, and those in unannotated functions.

    Returns:
      The table's lines.

    """

    def row(name: str, of: Sequence[Binding]) -> list[str]:
        missed: list[Binding] = [b for b in of if not b.fixed]
        bare: int = sum(b.scope == _FUNCTION and not b.annotated for b in missed)
        return [name, f"{len(of):,}", _share(len(missed), len(of)), _share(bare, len(missed))]

    return _table(
        ["Corpus", "Untyped", "No fix", "No fix, in a function with no annotations"],
        [
            *(row(name, [b for b in bindings if b.corpus == name]) for name in corpora_seen),
            row("**Total**", bindings),
        ],
    )


def _shapes(missed: Sequence[Binding], keep: Callable[[Binding], bool], top: int) -> list[str]:
    """Tabulate the commonest `binding: shape` among the bindings with no fix that `keep` selects.

    Returns:
      The table's lines, headed by how many there are.

    """
    counts: Counter[str] = Counter(f"{b.binding}: {b.shape}" for b in missed if keep(b))
    total: int = counts.total()
    return [
        f"{total:,} bindings; the {min(top, len(counts))} commonest shapes:",
        "",
        *_table(
            ["Binding: value", "Count", "Share"],
            [[key, f"{count:,}", f"{count / total:.1%}"] for key, count in _ranked(counts, top)],
        ),
    ]


def _groups(missed: Sequence[Binding]) -> list[str]:
    """Tabulate the groups the roadmap's items are sized by, whatever statement binds them.

    Returns:
      The table's lines.

    """
    rows: list[list[str]] = []
    label: str
    shapes: frozenset[str]
    for label, shapes in _GROUPS.items():
        members: list[Binding] = [b for b in missed if b.shape in shapes]
        in_annotated: int = sum(b.scope == _FUNCTION and b.annotated for b in members)
        rows.append([label, f"{len(members):,}", f"{in_annotated:,}"])
    return _table(["No fix, by what the value is", "All", "In annotated functions"], rows)


def _origins(calls: Sequence[Binding]) -> list[str]:
    """Tabulate calls through an import by where the import comes from, and which modules.

    Returns:
      The table's lines.

    """
    rows: list[list[str]] = []
    origin: str
    for origin in (_STDLIB_ORIGIN, _OWN, _THIRD_PARTY):
        mine: list[Binding] = [b for b in calls if b.origin == origin]
        # A third-party package by its top level; anything else by the module itself.
        modules: Counter[str] = Counter(
            b.dotted.split(".", 1)[0] if origin == _THIRD_PARTY else b.dotted.rsplit(".", 1)[0] for b in mine
        )
        common: str = ", ".join(f"`{name}` {count:,}" for name, count in _ranked(modules, _TOP_MODULES))
        rows.append([origin, f"{len(mine):,}", common])
    return _table(["Module from", "Calls", "Commonest modules"], rows)


def _imports(missed: Sequence[Binding], top: int) -> list[str]:
    """Tabulate the calls with no fix that go through an import, by where it comes from.

    Returns:
      The lines: `module.func()` calls, calls to an imported name, then the standard library's
      commonest functions among both.

    """
    through_modules: list[Binding] = [b for b in missed if b.shape == _MODULE_CALL]
    through_names: list[Binding] = [b for b in missed if b.shape in _IMPORTS]
    functions: Counter[str] = Counter(
        b.dotted for b in (*through_modules, *through_names) if b.origin == _STDLIB_ORIGIN
    )
    return [
        "Through a module an `import` binds (`os.path.join(...)`, `np.array(...)`):",
        "",
        *_origins(through_modules),
        "",
        "Through a name imported from a module (`join(...)` after `from os.path import join`):",
        "",
        *_origins(through_names),
        "",
        "The standard library's commonest functions among both:",
        "",
        *_table(
            ["Function", "Calls"],
            [[f"`{name}`", f"{count:,}"] for name, count in _ranked(functions, top)],
        ),
    ]


def report(bindings: Sequence[Binding], corpora_seen: Sequence[str], top: int = _TOP) -> str:
    """Write the census as Markdown.

    Returns:
      Its sections, each a heading and a table.

    """
    missed: list[Binding] = [b for b in bindings if not b.fixed]
    sections: list[_Section] = [
        ("Untyped bindings, and those `--fix` offers nothing for", _totals(bindings, corpora_seen)),
        (
            "No fix, in functions that declare something",
            _shapes(missed, lambda b: b.scope == _FUNCTION and b.annotated, top),
        ),
        (
            "No fix, in functions that declare nothing",
            _shapes(missed, lambda b: b.scope == _FUNCTION and not b.annotated, top),
        ),
        ("No fix, in a module's body", _shapes(missed, lambda b: b.scope == _MODULE, top)),
        ("No fix, by group", _groups(missed)),
        ("Calls with no fix through an import, by where it comes from", _imports(missed, top)),
    ]
    return "\n".join(f"## {heading}\n\n" + "\n".join(lines) + "\n" for heading, lines in sections)


def main(argv: Sequence[str] | None = None) -> int:
    """Take the census of every corpus and print it (writing every binding, with `--rows`).

    Returns:
      0.

    """
    parser: argparse.ArgumentParser = argparse.ArgumentParser(description="What `--fix` can't type, and why.")
    _ = parser.add_argument("--top", type=int, default=_TOP, help="categories per table (30)")
    _ = parser.add_argument("--rows", type=Path, help="also write every binding to this file, as JSON lines")
    options: argparse.Namespace = parser.parse_args(argv)
    WORK.mkdir(parents=True, exist_ok=True)
    bindings: list[Binding] = []
    seen: list[str] = []
    corpus: Corpus
    for corpus in corpora():
        found: list[Binding]
        unparsed: int
        found, unparsed = census(corpus)
        bindings.extend(found)
        seen.append(corpus.name)
        _ = sys.stderr.write(
            f"{corpus.name}: {len(found):,} untyped ({unparsed:,} in files that don't parse)\n",
        )
    rows: Path | None
    if (rows := cast("Path | None", options.rows)) is not None:
        _ = rows.write_text("".join(json.dumps(b._asdict()) + "\n" for b in bindings), encoding="utf-8")
    _ = sys.stdout.write(report(bindings, seen, cast("int", options.top)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
