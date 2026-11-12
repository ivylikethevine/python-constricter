"""Stop tracking the run folders past `corpus-runs/`'s rule, leaving them on this machine's disk.

  local/.venv/bin/python -m scripts.scratch.retire_runs [--apply]

Kept tracked: each release's folder (`0.4.3-...`, no `-rc`), the latest `mega-*` and the latest
`super-*` by the time in their names. For every other folder with tracked files it prints the folder
and its size; `--apply` adds it to `corpus-runs/.gitignore` and takes its files out of the index
(`git rm --cached`), for the next commit to record. Run it after a mega or super run is kept. The
folders stay on disk, where later runs read them, and in git's history.
"""

import argparse
import re
import subprocess
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RUNS = ROOT / "corpus-runs"
_RELEASE = re.compile(r"^\d+\.\d+\.\d+-\d\d-\d\d-\d{4}-\d{4}$")
_NAMED = re.compile(r"^(mega|super)-(\d\d-\d\d-\d{4}-\d{4})$")


def _latest(folders: set[str]) -> set[str]:
    newest: dict[str, tuple[datetime, str]] = {}
    for folder in folders:
        if (match := _NAMED.match(folder)) is not None:
            when = datetime.strptime(match[2], "%m-%d-%Y-%H%M")  # noqa: DTZ007
            if match[1] not in newest or when > newest[match[1]][0]:
                newest[match[1]] = (when, folder)
    return {folder for _, folder in newest.values()}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true")
    apply = parser.parse_args().apply
    tracked = subprocess.run(
        ["git", "ls-files", "--format=%(objectsize) %(path)", "corpus-runs"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=True,
    ).stdout.splitlines()
    sizes: dict[str, int] = {}
    files: dict[str, list[str]] = {}
    for line in tracked:
        size, path = line.split(" ", 1)
        parts = path.split("/")
        if len(parts) > 2:
            sizes[parts[1]] = sizes.get(parts[1], 0) + int(size)
            files.setdefault(parts[1], []).append(path)
    kept = _latest(set(sizes)) | {folder for folder in sizes if _RELEASE.match(folder)}
    retired = sorted(set(sizes) - kept)
    print(f"kept {sum(sizes[each] for each in kept) / 1e6:.1f} MB: {', '.join(sorted(kept))}")
    for folder in retired:
        print(f"retired {sizes[folder] / 1e6:>6.1f} MB {folder}")
    if apply and retired:
        ignore = RUNS / ".gitignore"
        written = ignore.read_text(encoding="utf-8")
        lines = "".join(f"/{folder}/\n" for folder in retired if f"/{folder}/\n" not in written)
        ignore.write_text(written + lines, encoding="utf-8")
        subprocess.run(
            ["git", "rm", "--cached", "--quiet", "--", *(path for each in retired for path in files[each])],
            cwd=ROOT,
            check=True,
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
