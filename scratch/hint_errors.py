"""The new type errors a corpus run's hinted fixes caused, grouped for reading by cause.

  local/.venv/bin/python -m scratch.hint_errors corpus-runs/0.4.0-rc.2-10-17-2026-0417
  local/.venv/bin/python -m scratch.hint_errors FOLDER --step infer-pyrefly --corpus pandas --samples 5

Reads each `records/<corpus>/<version>/types-<step>.json` the run wrote for a hinted fix
(`infer-basedpyright`, `infer-ty`, `infer-pyrefly`, `infer-trace`), following one that was implied by
another step's identical patch, and for each new error notes its checker's code (`[arg-type]`,
`(reportAttributeAccessIssue)`), the fix blamed and its kinds. Prints the counts by step, by corpus
and by code, then the distinct blamed fixes (a fix blamed for several errors once) by code with
samples: each one's corpus, path, line, name, annotation and message. Writes every error as JSON
lines to `local/scratch/hint-errors/<folder>.jsonl`, for grouping by hand.
"""

import argparse
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

OUT = Path(__file__).resolve().parents[1] / "local" / "scratch" / "hint-errors"
STEPS = ("infer-basedpyright", "infer-ty", "infer-pyrefly", "infer-trace")
_CODE = re.compile(r"\[([a-z-]+)\]\s*$|\((report\w+)\)\s*$")


def _code(message: str) -> str:
    found = _CODE.search(message)
    return next((group for group in found.groups() if group), "?") if found else "?"


def errors(folder: Path, steps: tuple[str, ...]) -> list[dict]:
    found = []
    for version in sorted((folder / "records").glob("*/*")):
        for step in steps:
            path = version / f"types-{step}.json"
            if not path.exists():
                continue
            record = json.loads(path.read_text(encoding="utf-8"))
            implied = record.get("implied")
            if implied:
                record = json.loads((version / f"types-{implied}.json").read_text(encoding="utf-8"))
            for new in record.get("new", []):
                fix = new.get("fix") or {}
                found.append({
                    "corpus": version.parent.name, "step": step, "implied": implied, "code": _code(new["message"]),
                    "kind": new.get("kind"), "path": new["path"], "line": new["line"], "name": fix.get("name"),
                    "fixed": fix.get("line"), "annotation": fix.get("annotation"), "message": new["message"],
                })
    return found


def main() -> int:
    parser = argparse.ArgumentParser(description=(__doc__ or "").splitlines()[0])
    parser.add_argument("folder", type=Path)
    parser.add_argument("--step", action="append", choices=STEPS)
    parser.add_argument("--corpus", action="append")
    parser.add_argument("--samples", type=int, default=3)
    args = parser.parse_args()
    found = [each for each in errors(args.folder, tuple(args.step or STEPS)) if not args.corpus or each["corpus"] in args.corpus]
    OUT.mkdir(parents=True, exist_ok=True)
    with (OUT / f"{args.folder.name}.jsonl").open("w", encoding="utf-8") as handle:
        handle.writelines(json.dumps(each) + "\n" for each in found)
    for key in ("step", "corpus", "code", "kind"):
        print(f"by {key}:", ", ".join(f"{name} {count}" for name, count in Counter(each[key] for each in found).most_common(25)))
    fixes: dict[str, dict[tuple, list[dict]]] = defaultdict(dict)
    for each in found:
        fixes[each["code"]].setdefault((each["corpus"], each["path"], each["fixed"], each["name"], each["annotation"]), []).append(each)
    print()
    for code, blamed in sorted(fixes.items(), key=lambda item: -len(item[1])):
        steps = Counter(error["step"] for errors_ in blamed.values() for error in errors_)
        print(f"== {code}: {len(blamed)} fixes, {sum(map(len, blamed.values()))} errors ({', '.join(f'{s} {n}' for s, n in steps.items())})")
        for (corpus, path, fixed, name, annotation), errors_ in list(blamed.items())[: args.samples]:
            print(f"   {corpus} {path}:{fixed} {name}: {annotation}  [{errors_[0]['kind']}] x{len(errors_)}")
            print(f"      {errors_[0]['line']}: {errors_[0]['message'][:200]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
