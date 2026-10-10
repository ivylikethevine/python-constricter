# SPDX-License-Identifier: MIT
"""Sum up what `scratch.guess_census` wrote: each guess mechanism's count, blamed errors and run-time record.

  local/.venv/bin/python -m scratch.guess_report                # the tables
  local/.venv/bin/python -m scratch.guess_report --differ KIND  # the guesses of KIND a run contradicts
  local/.venv/bin/python -m scratch.guess_report --blamed KIND  # those a type checker blames
  local/.venv/bin/python -m scratch.guess_report --likely       # the sets that pass `LIKELY.md`'s bars

A guess's kinds are its mechanisms, joined by `+`. A table by the whole set, then one by each
mechanism in it (a guess counts under each of its own). For each: the guesses, those in packages
whose own type checker ran, the errors blamed on them and how many guesses they're blamed on; then
those whose binding a traced test run reached, split into the ones every type seen fits and the
ones some type seen doesn't.

"Fits" is by name: each type seen is a member of the annotation's union, by its class's last name
(`pandas.core.frame:DataFrame` fits `DataFrame`), a builtin's subclass or protocol a member allows
(`bool` an `int`, a `list` a `Sequence`), or anything where the annotation has `Any` or `object`.
A subclass the annotation's class allows (a `MultiIndex` for an `Index`) and an alias (`CoreSchema`
for a `dict`) count as not fitting: read `--differ` before believing a low share.
"""

import json
import re
import sys
from collections import defaultdict
from pathlib import Path

OUT = Path(__file__).resolve().parents[1] / "local" / "scratch" / "guesses"
ANYTHING = {"Any", "object"}
# What a builtin seen at run time also is, to an annotation.
ALSO = {
    "bool": {"int", "float", "complex"},
    "int": {"float", "complex"},
    "float": {"complex"},
    "list": {"Sequence", "MutableSequence", "Collection", "Iterable", "Reversible"},
    "tuple": {"Sequence", "Collection", "Iterable", "Reversible"},
    "str": {"Sequence", "Collection", "Iterable"},
    "bytes": {"Sequence", "Collection", "Iterable"},
    "range": {"Sequence", "Collection", "Iterable"},
    "dict": {"Mapping", "MutableMapping", "Collection", "Iterable"},
    "OrderedDict": {"dict", "Mapping", "MutableMapping", "Collection", "Iterable"},
    "defaultdict": {"dict", "Mapping", "MutableMapping", "Collection", "Iterable"},
    "Counter": {"dict", "Mapping", "MutableMapping", "Collection", "Iterable"},
    "set": {"AbstractSet", "MutableSet", "Collection", "Iterable"},
    "frozenset": {"AbstractSet", "Collection", "Iterable"},
    "function": {"Callable"},
    "method": {"Callable"},
    "builtin_function_or_method": {"Callable"},
    "partial": {"Callable"},
    "type": {"Callable"},
    "generator": {"Iterator", "Iterable", "Generator"},
    "NoneType": {"None"},
}
NAME = re.compile(r"[A-Za-z_][\w.]*")


def members(annotation: str) -> set[str]:
    """The last names of an annotation's top-level union members."""
    text = annotation.strip("\"'")
    found = set()
    depth = 0
    start = 0
    for at, char in enumerate(text + "|"):
        if char in "[(":
            depth += 1
        elif char in "])":
            depth -= 1
        elif char == "|" and not depth:
            head = NAME.match(text[start:at].strip().strip("\"'"))
            if head:
                found.add(head[0].rpartition(".")[2])
            start = at + 1
    return found


def head(spelling: str) -> str:
    """The last name of a type seen at run time: `m:Outer.Inner[int]` is `Inner`."""
    return spelling.partition("[")[0].rpartition(":")[2].rpartition(".")[2]


def fits(annotation: str, seen: list[str]) -> bool:
    allowed = members(annotation)
    if allowed & ANYTHING:
        return True
    return all(({name} | ALSO.get(name, set())) & allowed for name in map(head, seen))


def rows() -> list[dict]:
    found = []
    for path in sorted(OUT.glob("*.jsonl")):
        with open(path, encoding="utf-8") as file:
            found.extend(json.loads(line) for line in file)
    return found


def table(title: str, groups: dict[str, list[dict]], least: int) -> None:
    print(f"\n{title}\n")
    print("| Kind | Guesses | Packages | Checked | Blamed errors | Guesses blamed | Per 100 | Seen | Fit | Differ |")
    print("| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |")
    for kind, each in sorted(groups.items(), key=lambda item: -len(item[1])):
        if len(each) < least:
            continue
        checked = [row for row in each if row["checked"]]
        blamed = [row for row in checked if row["errors"]]
        seen = [row for row in each if row["seen"]]
        fit = sum(fits(row["annotation"], row["seen"]) for row in seen)
        rate = f"{100 * len(blamed) / len(checked):.2f}" if checked else "-"
        print(
            f"| `{kind}` | {len(each):,} | {len({row['package'] for row in each})} | {len(checked):,} | "
            f"{sum(row['errors'] for row in blamed)} | {len(blamed)} | {rate} | {len(seen):,} | {fit:,} | "
            f"{len(seen) - fit} |",
        )


def listed(kind: str, flag: str) -> None:
    for row in rows():
        if not row["unsafe"] or kind not in (row["kinds"], *row["kinds"].split("+")):
            continue
        differs = bool(row["seen"]) and not fits(row["annotation"], row["seen"])
        if (flag == "--differ" and differs) or (flag == "--blamed" and row["errors"]):
            print(
                f"{row['package']} {row['path']}:{row['line']} {row['name']}: {row['annotation']} "
                f"[{row['kinds']}] errors={row['errors']} seen={row['seen']}",
            )


SEEN = 20  # the bindings a traced run must have reached
FIT = 0.88  # the share of them that must fit: what certain fixes reach, by name
BLAMED = 0.1  # the most guesses blamed by a type checker, per 100 checked


def likely(groups: dict[str, list[dict]]) -> dict[str, list[dict]]:
    """The whole sets that pass the three bars."""
    found = {}
    for kind, each in groups.items():
        checked = [row for row in each if row["checked"]]
        seen = [row for row in each if row["seen"]]
        fit = sum(fits(row["annotation"], row["seen"]) for row in seen)
        blamed = sum(bool(row["errors"]) for row in checked)
        if len(seen) >= SEEN and fit > FIT * len(seen) and (not checked or 100 * blamed < BLAMED * len(checked)):
            found[kind] = each
    return found


def main(argv: list[str]) -> int:
    if argv == ["--likely"]:
        whole: dict[str, list[dict]] = defaultdict(list)
        guesses = [row for row in rows() if row["unsafe"]]
        for row in guesses:
            whole[row["kinds"]].append(row)
        passing = likely(whole)
        table("Likely: the whole sets that pass", passing, 0)
        count = sum(map(len, passing.values()))
        print(f"\n{len(passing)} sets, {count:,} of {len(guesses):,} guesses ({100 * count / len(guesses):.1f}%)\n")
        for kind in sorted(passing):
            print("    frozenset({" + ", ".join(f'"{each}"' for each in kind.split("+")) + "}),")
        return 0
    if argv:
        listed(argv[1], argv[0])
        return 0
    every = rows()
    guesses = [row for row in every if row["unsafe"]]
    certain = [row for row in every if not row["unsafe"]]
    print(f"{len(every):,} fixes in {len({row['package'] for row in every})} packages: {len(guesses):,} guesses")
    table("Certain fixes, all together", {"(certain)": certain}, 0)
    whole: dict[str, list[dict]] = defaultdict(list)
    each: dict[str, list[dict]] = defaultdict(list)
    for row in guesses:
        whole[row["kinds"]].append(row)
        for kind in row["kinds"].split("+"):
            each[kind].append(row)
    table("Guesses, by each mechanism in the set", each, 1)
    table("Guesses, by the whole set (20 or more)", whole, 20)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
