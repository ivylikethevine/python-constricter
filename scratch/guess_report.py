# SPDX-License-Identifier: MIT
"""Sum up what `scratch.guess_census` wrote: each guess mechanism's count, blamed errors and run-time record.

  local/.venv/bin/python -m scratch.guess_report                # the tables
  local/.venv/bin/python -m scratch.guess_report --differ KIND  # the guesses of KIND a value differed from
  local/.venv/bin/python -m scratch.guess_report --blamed KIND  # those a type checker blames
  local/.venv/bin/python -m scratch.guess_report --likely       # the sets that pass `LIKELY.md`'s bars

A guess's kinds are its mechanisms, joined by `+`. A table by the whole set, then one by each
mechanism in it (a guess counts under each of its own). For each: the guesses, those in packages
whose own type checker ran, the errors blamed on them and how many guesses they're blamed on; then
those a traced test bound to a value that could be held to the annotation (told), those whose every
such value was an instance of what it says (held), and those one of whose values wasn't (differed).
The certain fixes' row comes first: what a guess's share is read against.
"""

import json
import sys
from collections import defaultdict
from pathlib import Path

OUT = Path(__file__).resolve().parents[1] / "local" / "scratch" / "guesses"
TOLD = 20  # the bindings a traced run must have told of
HELD = 0.95  # the share of them that must have held
BLAMED = 0.1  # the most guesses blamed by a type checker, per 100 checked


def rows() -> list[dict]:
    found = []
    for path in sorted(OUT.glob("*.jsonl")):
        with open(path, encoding="utf-8") as file:
            # A file an older census wrote has no verdicts: its package's newest run kept no fixes.
            found.extend(row for row in map(json.loads, file) if "verdict" in row)
    return found


def told(row: dict) -> bool:
    return bool(row["verdict"][0] or row["verdict"][1])


def held(row: dict) -> bool:
    return bool(row["verdict"][0]) and not row["verdict"][1]


def table(title: str, groups: dict[str, list[dict]], least: int) -> None:
    print(f"\n{title}\n")
    print(
        "| Kind | Guesses | Packages | Checked | Blamed errors | Guesses blamed | Per 100 "
        "| Told | Held | Share | Differed |",
    )
    print("| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |")
    for kind, each in sorted(groups.items(), key=lambda item: -len(item[1])):
        if len(each) < least:
            continue
        checked = [row for row in each if row["checked"]]
        blamed = [row for row in checked if row["errors"]]
        judged = [row for row in each if told(row)]
        fit = sum(held(row) for row in judged)
        rate = f"{100 * len(blamed) / len(checked):.2f}" if checked else "-"
        share = f"{fit / len(judged):.1%}" if judged else "-"
        print(
            f"| `{kind}` | {len(each):,} | {len({row['package'] for row in each})} | {len(checked):,} | "
            f"{sum(row['errors'] for row in blamed)} | {len(blamed)} | {rate} | {len(judged):,} | {fit:,} | "
            f"{share} | {len(judged) - fit} |",
        )


def listed(kind: str, flag: str) -> None:
    for row in rows():
        if not row["unsafe"] or kind not in (row["kinds"], *row["kinds"].split("+")):
            continue
        if (flag == "--differ" and row["verdict"][1]) or (flag == "--blamed" and row["errors"]):
            print(
                f"{row['package']} {row['path']}:{row['line']} {row['name']}: {row['annotation']} "
                f"[{row['kinds']}] errors={row['errors']} verdict={row['verdict']} seen={row['seen']}",
            )


def likely(groups: dict[str, list[dict]]) -> dict[str, list[dict]]:
    """The whole sets that pass the three bars."""
    found = {}
    for kind, each in groups.items():
        checked = [row for row in each if row["checked"]]
        judged = [row for row in each if told(row)]
        fit = sum(held(row) for row in judged)
        blamed = sum(bool(row["errors"]) for row in checked)
        if len(judged) >= TOLD and fit > HELD * len(judged) and (not checked or 100 * blamed < BLAMED * len(checked)):
            found[kind] = each
    return found


def main(argv: list[str]) -> int:
    every = rows()
    guesses = [row for row in every if row["unsafe"]]
    whole: dict[str, list[dict]] = defaultdict(list)
    each: dict[str, list[dict]] = defaultdict(list)
    for row in guesses:
        whole[row["kinds"]].append(row)
        for kind in row["kinds"].split("+"):
            each[kind].append(row)
    if argv == ["--likely"]:
        passing = likely(whole)
        table("Likely: the whole sets that pass", passing, 0)
        count = sum(map(len, passing.values()))
        print(f"\n{len(passing)} sets, {count:,} of {len(guesses):,} guesses ({100 * count / len(guesses):.1f}%)\n")
        for kind in sorted(passing):
            print("    frozenset({" + ", ".join(f'"{one}"' for one in kind.split("+")) + "}),")
        return 0
    if argv:
        listed(argv[1], argv[0])
        return 0
    print(f"{len(every):,} fixes in {len({row['package'] for row in every})} packages: {len(guesses):,} guesses")
    table("Certain fixes, all together", {"(certain)": [row for row in every if not row["unsafe"]]}, 0)
    tiers = {"likely": [row for row in guesses if row["likely"]], "other": [row for row in guesses if not row["likely"]]}
    table("Guesses, by tier", tiers, 0)
    table("Guesses, by each mechanism in the set", each, 1)
    table("Guesses, by the whole set (20 or more)", whole, 20)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
