"""Run corpus packages' tests as released and after `--fix --unsafe-fixes` with every `fix-widen` kind.

  local/.venv/bin/python -m scratch.widen_suites [SUITE ...] [--keep]

Each of the seven corpora's suites (default: all), with that one fixed run; it exits 1 if a fixed
run's outcome isn't its released one's. `--keep` also keeps each fixed run's test output and diff in
`local/scratch/widen/`, for a suite that differs. Outside a sandbox.
"""

import subprocess
import sys
from pathlib import Path

from tests.corpus import corpus_suite

OUT = Path(__file__).resolve().parents[1] / "local" / "scratch" / "widen"
WIDEN = ("--unsafe-fixes", "--fix-widen=all")


def fixed(root: Path, suite: corpus_suite.Suite, *extra: str) -> str:
    """Reset the checkout's source and `--fix` it with `extra`, at `suffocate` with every scope.

    Returns the size of the change, as `git diff --shortstat` puts it.
    """
    corpus_suite.reset(root, suite)
    constricter = str(Path(sys.executable).with_name("constricter"))
    command = [constricter, "--fix", *extra, "--level=suffocate", "--all-scopes", "--jobs=0", suite.source]
    subprocess.run(command, cwd=root, capture_output=True, check=False)
    return subprocess.run(
        ["git", "diff", "--shortstat"], cwd=root, capture_output=True, text=True, check=False
    ).stdout.strip()


def main(args: list[str]) -> int:
    keep = "--keep" in args
    names = [arg for arg in args if arg != "--keep"]
    same = True
    for name in names or corpus_suite.SUITES:
        suite = corpus_suite.SUITES[name]
        root = corpus_suite.checkout(name, suite)
        corpus_suite.reset(root, suite)
        released = corpus_suite.tested(root, suite, None, None)
        print(f"{name} {suite.tag}: released: {released.counts}", flush=True)
        change = fixed(root, suite, *WIDEN)
        kept = None
        if keep:
            OUT.mkdir(parents=True, exist_ok=True)
            kept = OUT / f"{name}-widened.txt"
            diff = subprocess.run(
                ["git", "diff"], cwd=root, capture_output=True, text=True, check=False
            ).stdout
            (OUT / f"{name}-suite.diff").write_text(diff, encoding="utf-8")
        outcome = corpus_suite.tested(root, suite, kept, None)
        print(
            f"  widened ({change}): {outcome.counts}: {'same' if outcome == released else 'DIFFERENT'}",
            flush=True,
        )
        for test in sorted(outcome.failed ^ released.failed):
            print(f"    {'now fails' if test in outcome.failed else 'now passes'}: {test}", flush=True)
        same = same and outcome == released
        corpus_suite.reset(root, suite)
    return 0 if same else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
