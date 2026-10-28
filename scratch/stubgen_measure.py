"""Measure what pyrefly's `stubgen` stubs of a corpus's untyped packages add to `--fix`.

  local/.venv/bin/python -m scratch.stubgen_measure CHECKOUT SOURCE PACKAGE...

CHECKOUT is a suite's checkout under `local/corpus-suites/` (its `.venv` the environment), SOURCE
the directory checked in it (`dask`), each PACKAGE an installed one with no `py.typed`. Each is
stubbed by `pyrefly stubgen` into `local/scratch/stubgen/<checkout>/<package>-stubs/`, a stub-only
package as PEP 561 names one, which the index reads before the package itself. Then the corpus's
fixes are listed twice, as a run's `fix-unsafe` step finds them (`--unsafe-fixes --show-fixes
--all-scopes --no-gitignore`, with no `--fix`, so the checkout is left as it is): as installed, and
with the stubs' directory on `PYTHONPATH`. Prints each stub set's returns (concrete, or `Incomplete`), the fixes
by tier each way, and the fixes only one side has, by the type written; both listings are kept.
One process: `--jobs=1`, inside a sandbox or out.
"""

import collections
import json
import os
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PYTHON = ROOT / "local" / ".venv" / "bin" / "python"
PYREFLY = ROOT / "local" / ".venv" / "bin" / "pyrefly"
_RETURN = re.compile(r"\) -> (.+?): \.\.\.$")
_NAME = re.compile(r"'([^']+)'")  # the name an offence's message quotes


def tier(each: dict[str, object]) -> str:
    """Name a listed fix's tier."""
    fix = each["fix"]
    assert isinstance(fix, dict)
    return "guess" if fix["unsafe"] and not fix["likely"] else "likely" if fix["unsafe"] else "certain"


def stubbed(checkout: Path, packages: list[str]) -> Path:
    """Write each package's stubs, as `<package>-stubs`, in a directory of the checkout's own."""
    out = ROOT / "local" / "scratch" / "stubgen" / checkout.name
    site = next((checkout / ".venv" / "lib").glob("python3*/site-packages"))
    for package in packages:
        target = out / f"{package}-stubs"
        if not target.is_dir():
            command = [str(PYREFLY), "stubgen", str(site / package), "-o", str(target)]
            subprocess.run([*command, "--site-package-path", str(site)], check=True, capture_output=True)
        returns = collections.Counter(
            "Incomplete" if "Incomplete" in found[1] else "concrete"
            for stub in target.rglob("*.pyi")
            for line in stub.read_text(encoding="utf-8").splitlines()
            if (found := _RETURN.search(line)) is not None
        )
        print(f"{package:12} {returns['concrete']:6} concrete returns  {returns['Incomplete']:6} Incomplete")
    return out


def listed(checkout: Path, source: str, stubs: Path | None) -> list[dict[str, object]]:
    """List the corpus's fixes, with the stubs on the path or not."""
    env = {**os.environ, "VIRTUAL_ENV": str(checkout / ".venv")}
    if stubs is not None:
        env["PYTHONPATH"] = str(stubs)
    # No `--fix`: it would write the fixes into the checkout; `--show-fixes` alone lists them.
    options = ["--unsafe-fixes", "--show-fixes", "--format=json", "--all-scopes", "--no-gitignore"]
    command = [str(PYTHON), "-P", "-W", "ignore", "-m", "constricter", *options, "--exit-zero", "--jobs=1"]
    done = subprocess.run(
        [*command, source], cwd=checkout, env=env, capture_output=True, text=True, check=False
    )
    found = [each for each in json.loads(done.stdout) if each.get("fix")]
    label = "stubbed" if stubs is not None else "installed"
    kept = ROOT / "local" / "scratch" / "stubgen" / checkout.name / f"{label}.json"
    kept.parent.mkdir(parents=True, exist_ok=True)
    kept.write_text(json.dumps(found, indent=1), encoding="utf-8")
    return found


def main() -> None:
    checkout, source, packages = Path(sys.argv[1]).resolve(), sys.argv[2], sys.argv[3:]
    stubs = stubbed(checkout, packages)
    sides = {
        label: listed(checkout, source, where) for label, where in (("installed", None), ("stubbed", stubs))
    }
    for label, found in sides.items():
        tiers = collections.Counter(tier(each) for each in found)
        print(f"{label:9} {len(found):6} fixes  " + "  ".join(f"{t} {n}" for t, n in sorted(tiers.items())))

    def keyed(found: list[dict[str, object]]) -> dict[tuple[object, ...], str]:
        named = ((each, _NAME.search(str(each["message"]))) for each in found)
        return {
            (each["path"], each["line"], name[1] if name else ""): f"{each['fix']['annotation']} ({tier(each)})"  # type: ignore[index]
            for each, name in named
        }

    before, after = keyed(sides["installed"]), keyed(sides["stubbed"])
    gained = collections.Counter(after[key] for key in after.keys() - before.keys())
    lost = collections.Counter(before[key] for key in before.keys() - after.keys())
    changed = sum(1 for key in before.keys() & after.keys() if before[key] != after[key])
    print(f"gained {sum(gained.values())}, lost {sum(lost.values())}, changed {changed}")
    print("gained:", gained.most_common(12))
    print("lost:", lost.most_common(6))


if __name__ == "__main__":
    main()
