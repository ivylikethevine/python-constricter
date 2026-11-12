"""Say what each `self.method()` binding with no fix waits on: what the method's `return`s give.

  local/.venv/bin/python -m scripts.scratch.method_returns RUN_FOLDER [--samples N] [--corpus NAME ...]

Reads each corpus's census rows from the run's records (`census.rows.jsonl`: every binding, its
shape, whether it has a fix) and the corpus's source as the run checked it. For each binding of
shape `call: self.method()` with no fix it finds the method by syntax (the binding's class's own,
or a base's in the file) and sorts each `return`'s value: a display or a constant, a parameter, a
local (by the local's own census row: with a fix, or without and why), a call by what's called, an
attribute or a subscript of `self`, and so on; a tuple by its parts. Prints the bindings by where
the method is, then by what its `return`s wait on (every blocker named, and the bindings that wait
on one kind alone, which typing that kind would reach), with `--samples` of each, a corpus's first,
and for a method that declares its return or is decorated, the commonest of those. Syntax and the
census alone: nothing is checked again. About 20 seconds for a mega run's 55 corpora, 1 worker on
16CPU/60GB.
"""

import ast
import json
import sys
import warnings
from collections import Counter, defaultdict
from pathlib import Path

from tests.corpus import catalog, trees

SHAPE = "call: self.method()"
OWN = frozenset({"cls", "type(self)", "self.__class__"})
TYPED = "typed"
PASSED = frozenset(
    {"staticmethod", "classmethod", "final", "abstractmethod", "override"}
)  # a `def` all the same
Func = ast.FunctionDef | ast.AsyncFunctionDef
warnings.simplefilter("ignore", SyntaxWarning)  # the corpora's own escapes


def arguments(args: list[str], flag: str) -> list[str]:
    return [args[at + 1] for at, each in enumerate(args[:-1]) if each == flag]


class Module:
    def __init__(self, path: Path, rows: list[dict]) -> None:
        self.tree = ast.parse(path.read_bytes())
        self.rows: dict[str, list[dict]] = defaultdict(list)
        for row in rows:
            self.rows[row["name"]].append(row)
        self.classes: dict[str, ast.ClassDef] = {}
        self.inside: list[tuple[int, int, ast.ClassDef]] = []
        self.functions = {
            node.name: node
            for node in self.tree.body
            if isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef)
        }
        for node in ast.walk(self.tree):
            if isinstance(node, ast.ClassDef):
                self.classes.setdefault(node.name, node)
                self.inside.append((node.lineno, node.end_lineno or node.lineno, node))

    def owner(self, line: int) -> ast.ClassDef | None:
        within = [each for each in self.inside if each[0] <= line <= each[1]]
        return max(within, key=lambda each: each[0])[2] if within else None

    def method(self, owner: ast.ClassDef, name: str, seen: frozenset[str] = frozenset()) -> Func | str:
        for stmt in owner.body:
            if isinstance(stmt, ast.FunctionDef | ast.AsyncFunctionDef) and stmt.name == name:
                return stmt
            targets = (
                stmt.targets
                if isinstance(stmt, ast.Assign)
                else [stmt.target]
                if isinstance(stmt, ast.AnnAssign)
                else []
            )
            if any(isinstance(target, ast.Name) and target.id == name for target in targets):
                return "a class attribute, not a `def`"
        for base in owner.bases:
            named = base.id if isinstance(base, ast.Name) else None
            if named in self.classes and named not in seen:
                found = self.method(self.classes[named], name, seen | {owner.name})
                if not isinstance(found, str) or found.startswith("a class attribute"):
                    return found
        return "not in the file: a base elsewhere, or set on the instance"

    def local(self, func: Func, name: str) -> str:
        first, last = func.lineno, func.end_lineno or func.lineno
        rows = [row for row in self.rows.get(name, ()) if first <= row["line"] <= last]
        if not rows:
            return "a local with no census row (declared, or bound by `global`, `del`, an import)"
        without = [row for row in rows if not row["fixed"]]
        if not without:
            return TYPED
        return f"a local with no fix: {without[0]['shape']}" + (
            f" ({without[0]['unfixed']})" if without[0]["unfixed"] else ""
        )

    def value(self, func: Func, value: ast.expr | None) -> list[str]:
        args = func.args
        params = {
            each.arg: each
            for each in (*args.posonlyargs, *args.args, *args.kwonlyargs, args.vararg, args.kwarg)
            if each
        }
        if value is None or isinstance(value, ast.Constant | ast.JoinedStr | ast.Compare):
            return [TYPED]
        if isinstance(value, ast.List | ast.Dict | ast.Set):
            parts = [*getattr(value, "elts", ()), *getattr(value, "keys", ()), *getattr(value, "values", ())]
            if not parts:
                return ["an empty display"]
            constant = all(isinstance(each, ast.Constant) for each in parts)
            return [TYPED] if constant else ["a display of other than constants"]
        if isinstance(value, ast.ListComp | ast.SetComp | ast.DictComp | ast.GeneratorExp):
            return ["a comprehension"]
        if isinstance(value, ast.UnaryOp) and isinstance(value.op, ast.Not):
            return [TYPED]
        if isinstance(value, ast.Tuple):
            parts = sorted({kind for each in value.elts for kind in self.value(func, each)} - {TYPED})
            return [f"a tuple's part: {part}" for part in parts] or [TYPED]
        if isinstance(value, ast.Name):
            if value.id in params:
                first = (*args.posonlyargs, *args.args)[:1]
                if first and first[0].arg == value.id:
                    return ["`self` itself"]
                return [TYPED] if params[value.id].annotation else ["an unannotated parameter"]
            return [self.local(func, value.id)]
        if isinstance(value, ast.Await):
            return [f"awaited: {kind}" for kind in self.value(func, value.value)]
        if isinstance(value, ast.IfExp):
            return sorted({*self.value(func, value.body), *self.value(func, value.orelse)})
        if isinstance(value, ast.BoolOp):
            return sorted({kind for each in value.values for kind in self.value(func, each)})
        if isinstance(value, ast.BinOp):
            return ["arithmetic"]
        if isinstance(value, ast.Call):
            return [self.call(value, params)]
        if isinstance(value, ast.Attribute):
            root = value.value
            return [
                "an attribute of `self`"
                if isinstance(root, ast.Name) and root.id == "self"
                else "an attribute of another value"
            ]
        if isinstance(value, ast.Subscript):
            root = value.value
            own = (
                isinstance(root, ast.Attribute)
                and isinstance(root.value, ast.Name)
                and root.value.id == "self"
            )
            return ["a subscript of an attribute of `self`" if own else "a subscript of another value"]
        return [f"other: {type(value).__name__}"]

    def call(self, call: ast.Call, params: dict[str, ast.arg]) -> str:
        callee = call.func
        spelled = ast.unparse(callee)
        if spelled in OWN:
            return "a call of its own class (`cls(...)`, `type(self)(...)`)"
        if isinstance(callee, ast.Name):
            if callee.id in self.classes:
                return TYPED
            if callee.id in self.functions:
                return (
                    TYPED
                    if self.functions[callee.id].returns
                    else "a call of the module's function, no return declared"
                )
            if callee.id in params or self.rows.get(callee.id):
                return "a call of a local or a parameter"
            return "a call of an imported name or a builtin"
        if isinstance(callee, ast.Attribute):
            root = callee.value
            if isinstance(root, ast.Name) and root.id == "self":
                return "a call of another method of `self`"
            if isinstance(root, ast.Call) and ast.unparse(root.func) == "super":
                return "a call of `super()`'s method"
            if (
                isinstance(root, ast.Attribute)
                and isinstance(root.value, ast.Name)
                and root.value.id == "self"
            ):
                return "a call of a method of an attribute of `self`"
            if isinstance(root, ast.Name):
                if root.id in params:
                    return "a call of a parameter's method"
                return (
                    "a call of a local's method"
                    if self.rows.get(root.id)
                    else "a call of a module's or a class's member"
                )
            return "a call of a method of another value"
        return "a call of a call or a subscript"

    def waits(self, func: Func) -> list[str]:
        if func.returns is not None:
            return ["declares its return (not offered: vague, declined, or its class unknown here)"]
        plain = [each for each in func.decorator_list if ast.unparse(each).split(".")[-1] not in PASSED]
        if plain:
            return ["decorated"]
        returns = []
        yields = False
        todo: list[ast.AST] = list(func.body)
        while todo:
            node = todo.pop()
            if isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef | ast.ClassDef | ast.Lambda):
                continue
            yields = yields or isinstance(node, ast.Yield | ast.YieldFrom)
            if isinstance(node, ast.Return):
                returns.append(node.value)
            todo.extend(ast.iter_child_nodes(node))
        if yields:
            return ["a generator"]
        if not any(each is not None for each in returns):
            return ["returns nothing"]
        found = {kind for each in returns for kind in self.value(func, each)} - {TYPED}
        if not found and not ended(func.body):
            return ["typed `return`s, and an end with none"]
        if not found and any(
            each is None or (isinstance(each, ast.Constant) and each.value is None) for each in returns
        ):
            return ["typed `return`s, and a `return None`"]
        if not found and isinstance(func.body[-1], ast.While):
            return ["typed `return`s, the method ending in a `while True:`"]
        return sorted(found) or ["every `return` typed by its shape or its local's fix"]


def ended(body: list[ast.stmt]) -> bool:
    """Whether a body always leaves by a `return` or a `raise`, as far as its last statement says."""
    last = body[-1]
    if isinstance(last, ast.Return | ast.Raise):
        return True
    if isinstance(last, ast.If):
        return bool(last.orelse) and ended(last.body) and ended(last.orelse)
    if isinstance(last, ast.With | ast.AsyncWith):
        return ended(last.body)
    if isinstance(last, ast.Try):
        return (
            ended(last.finalbody)
            if last.finalbody and ended(last.finalbody)
            else (ended(last.orelse or last.body) and all(ended(handler.body) for handler in last.handlers))
        )
    if isinstance(last, ast.While):
        return isinstance(last.test, ast.Constant) and bool(last.test.value)
    if isinstance(last, ast.Match):
        return all(ended(case.body) for case in last.cases) and any(
            isinstance(case.pattern, ast.MatchAs) and case.pattern.pattern is None and case.guard is None
            for case in last.cases
        )
    return False


def main() -> int:
    folder = Path(sys.argv[1])
    samples = int((arguments(sys.argv, "--samples") or ["3"])[0])
    only = arguments(sys.argv, "--corpus")
    where: Counter[str] = Counter()
    blockers: Counter[str] = Counter()
    alone: Counter[str] = Counter()
    shown: dict[str, list[str]] = defaultdict(list)
    detail: dict[str, Counter[str]] = defaultdict(Counter)
    kinds: Counter[str] = Counter()
    for name, entry in catalog.load().entries.items():
        record = folder / "records" / name.replace(" ", "-")
        found = sorted(record.glob("*/census.rows.jsonl")) or sorted(
            (folder / "records" / name).glob("*/census.rows.jsonl")
        )
        if not found or (only and name not in only):
            continue
        rows = [json.loads(line) for line in found[0].read_text(encoding="utf-8").splitlines()]
        by_path: dict[str, list[dict]] = defaultdict(list)
        for row in rows:
            by_path[row["path"]].append(row)
        root = trees.found(entry, settle=False).root
        modules: dict[str, Module | None] = {}
        for row in rows:
            if row["shape"] != SHAPE or row["fixed"]:
                continue
            kinds[row["binding"]] += 1
            path = row["path"]
            if path not in modules:
                try:
                    modules[path] = Module(root / path, by_path[path])
                except (OSError, SyntaxError, ValueError):
                    modules[path] = None
            module = modules[path]
            method = row["source"].removeprefix("await ").removeprefix("self.").split("(", 1)[0]
            owner = None if module is None else module.owner(row["line"])
            if module is None or owner is None:
                where["unread: no class at the binding's line"] += 1
                continue
            func = module.method(owner, method)
            if isinstance(func, str):
                where[func] += 1
                continue
            where["found: its class's own, or a base's in the file"] += 1
            waits = module.waits(func)
            for kind in waits:
                blockers[kind] += 1
            key = waits[0] if len(waits) == 1 else "more than one kind"
            alone[key] += 1
            told = f"{row['binding']} ({row['unfixed'] or 'no reason'})"
            if func.returns is not None:
                detail[key][f"{told} -> {ast.unparse(func.returns)[:48]}"] += 1
            elif func.decorator_list:
                detail[key][", ".join(ast.unparse(each).split("(")[0] for each in func.decorator_list)] += 1
            elif key.startswith("every"):
                detail[key][told] += 1
            if len(shown[key]) < samples and not any(line.startswith(f"{name}: ") for line in shown[key]):
                shown[key].append(
                    f"{name}: {path}:{row['line']} {row['name']} = {row['source'][:60]}  [{'; '.join(waits)[:110]}]"
                )
    total = sum(where.values())
    print(
        f"{total} `self.method()` bindings with no fix: "
        + ", ".join(f"{kind} {count}" for kind, count in kinds.most_common())
    )
    print("\n-- where the method is")
    for kind, count in where.most_common():
        print(f"{count:6}  {kind}")
    print("\n-- what the found methods' `return`s wait on: bindings with that kind among them")
    for kind, count in blockers.most_common():
        print(f"{count:6}  {kind}")
    print("\n-- bindings waiting on one kind alone")
    for kind, count in alone.most_common():
        print(f"{count:6}  {kind}")
        for line in shown[kind]:
            print(f"          {line}")
        for each, times in detail[kind].most_common(14):
            print(f"        {times:5}  {each}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
