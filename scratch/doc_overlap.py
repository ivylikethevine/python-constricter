"""List the passages two docs both tell, for giving each fact one home.

  local/.venv/bin/python -m scratch.doc_overlap [--words N] [--top N] [--numbers] DOC DOC [DOC ...]

Runs of at least `--words` words (8) that a later doc repeats from an earlier one, case and markup
left out: each with both docs' lines. Biggest first, `--top` of them (40), after each pair's total;
`--numbers` keeps those holding a number, a measurement told twice.
"""

import argparse
import re
from collections import Counter
from pathlib import Path

_WORD = re.compile(r"[\w.,+%-]+")


def _words(path: Path) -> list[tuple[str, int]]:
    return [
        (match.group().lower().strip(".,"), number)
        for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1)
        for match in _WORD.finditer(line)
    ]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("docs", nargs="+", type=Path)
    parser.add_argument("--words", type=int, default=8)
    parser.add_argument("--top", type=int, default=40)
    parser.add_argument(
        "--numbers", action="store_true", help="only runs holding a number: a measurement told twice"
    )
    args = parser.parse_args()
    size = args.words
    runs: list[tuple[int, str, int, str, int, str]] = []
    totals: Counter[tuple[str, str]] = Counter()
    for later, doc in enumerate(args.docs):
        words = _words(doc)
        for earlier in args.docs[:later]:
            first = _words(earlier)
            starts: dict[tuple[str, ...], list[int]] = {}
            for at in range(len(first) - size + 1):
                starts.setdefault(tuple(w for w, _ in first[at : at + size]), []).append(at)
            at = 0
            while at <= len(words) - size:
                found = starts.get(tuple(w for w, _ in words[at : at + size]), [])
                if not found:
                    at += 1
                    continue
                best = 0
                where = found[0]
                for start in found:
                    length = size
                    while (
                        start + length < len(first)
                        and at + length < len(words)
                        and first[start + length][0] == words[at + length][0]
                    ):
                        length += 1
                    if length > best:
                        best, where = length, start
                text = " ".join(w for w, _ in words[at : at + best])
                if not args.numbers or re.search(r"\d", text):
                    runs.append((best, earlier.name, first[where][1], doc.name, words[at][1], text))
                    totals[earlier.name, doc.name] += best
                at += best
    for pair, total in totals.most_common():
        print(f"{pair[0]} and {pair[1]}: {total} words")
    for length, one, line, other, place, text in sorted(runs, reverse=True)[: args.top]:
        print(f"{length:>5} {one}:{line} {other}:{place} {text[:160]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
