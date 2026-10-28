"""Compare what stub packages, and pyrefly's generated stubs, add to a corpus's `--unsafe-fixes`.

  local/.venv/bin/python -m scratch.stubs_measure CHECKOUT SOURCE PACKAGE=STUBS...

CHECKOUT is a suite's checkout under `local/corpus-suites/` (its `.venv` the environment), SOURCE
the directory checked in it (`dask`). Each PACKAGE=STUBS names a package and a directory holding
its stub package (`pandas=local/scratch/stubs/pandas-stubs`, as `uv pip install --no-deps --target`
leaves one). The fixes are listed as a run's `fix-unsafe` step finds them (`--unsafe-fixes
--show-fixes --all-scopes --no-gitignore`, no `--fix`, so the checkout is left as it is): as
installed; with each stub package alone on `PYTHONPATH`; with pyrefly's `stubgen` stubs of each
package alone, where it's installed without `py.typed`; and with every stub package at once. No
environment changes. For each, the fixes by tier, and those gained and lost against the installed
listing, the commonest types first. Each listing is kept under `local/scratch/stubs-measure/`. One
process: `--jobs=1`, inside a sandbox or out.
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
OUT = ROOT / "local" / "scratch" / "stubs-measure"
_NAME = re.compile(r"'([^']+)'")  # the name an offence's message quotes
_Listing = dict[tuple[object, ...], tuple[str, str]]  # each fix's binding: its type and tier


def _tier(fix: dict[str, object]) -> str:
    return "guess" if fix["unsafe"] and not fix["likely"] else "likely" if fix["unsafe"] else "certain"


def listed(checkout: Path, source: str, label: str, path: list[Path]) -> _Listing:
    """List the corpus's fixes with `path` on `PYTHONPATH`, keeping the listing."""
    env = {**os.environ, "VIRTUAL_ENV": str(checkout / ".venv")}
    if path:
        env["PYTHONPATH"] = os.pathsep.join(str(each) for each in path)
    else:
        env.pop("PYTHONPATH", None)
    options = ["--unsafe-fixes", "--show-fixes", "--format=json", "--all-scopes", "--no-gitignore"]
    command = [str(PYTHON), "-P", "-W", "ignore", "-m", "constricter", *options, "--exit-zero", "--jobs=1"]
    done = subprocess.run(
        [*command, source], cwd=checkout, env=env, capture_output=True, text=True, check=True
    )
    found = [each for each in json.loads(done.stdout) if each.get("fix")]
    kept = OUT / checkout.name / f"{label}.json"
    kept.parent.mkdir(parents=True, exist_ok=True)
    kept.write_text(json.dumps(found, indent=1), encoding="utf-8")
    listing: _Listing = {}
    for each in found:
        name = _NAME.search(str(each["message"]))
        listing[(each["path"], each["line"], name[1] if name else "")] = (
            each["fix"]["annotation"],
            _tier(each["fix"]),
        )
    return listing


def generated(checkout: Path, package: str) -> Path | None:
    """Write pyrefly's stubs of an installed package with no `py.typed` as `<package>-stubs`.

    Returns: the directory to put on the path; `None` where the package isn't installed or is typed.
    """
    site = next((checkout / ".venv" / "lib").glob("python3*/site-packages"))
    if not (site / package).is_dir() or (site / package / "py.typed").exists():
        return None
    where = OUT / checkout.name / "pyrefly" / package
    target = where / f"{package}-stubs"
    if not target.is_dir():
        command = [str(PYREFLY), "stubgen", str(site / package), "-o", str(target)]
        subprocess.run([*command, "--site-package-path", str(site)], check=True, capture_output=True)
    return where


def main() -> None:
    checkout, source = Path(sys.argv[1]).resolve(), sys.argv[2]
    stubs: dict[str, Path] = {}
    for each in sys.argv[3:]:
        package, _, where = each.partition("=")
        stubs[package] = Path(where).resolve()
    sets: dict[str, list[Path]] = {"installed": []}
    for package, where in stubs.items():
        sets[f"{package}-stubs"] = [where]
        made = generated(checkout, package)
        if made is not None:
            sets[f"{package}-pyrefly"] = [made]
    if len(stubs) > 1:
        sets["every stub package"] = list(stubs.values())
    base = listed(checkout, source, "installed", [])
    print(f"{checkout.name}, {source}")
    print(
        f"{'set':22} {'fixes':>6} {'certain':>7} {'likely':>6} {'guess':>6} {'gained':>6} {'lost':>5} {'changed':>7}"
    )
    for label, path in sets.items():
        found = base if label == "installed" else listed(checkout, source, label, path)
        tiers = collections.Counter(tier for _, tier in found.values())
        gained = collections.Counter(
            f"{found[key][0]} ({found[key][1]})" for key in found.keys() - base.keys()
        )
        lost = collections.Counter(f"{base[key][0]} ({base[key][1]})" for key in base.keys() - found.keys())
        changed = sum(1 for key in found.keys() & base.keys() if found[key] != base[key])
        print(
            f"{label:22} {len(found):6} {tiers['certain']:7} {tiers['likely']:6} {tiers['guess']:6}"
            f" {sum(gained.values()):6} {sum(lost.values()):5} {changed:7}",
        )
        if gained or lost:
            print("    gained:", ", ".join(f"{kind} {count}" for kind, count in gained.most_common(6)))
            print("    lost:  ", ", ".join(f"{kind} {count}" for kind, count in lost.most_common(4)))


if __name__ == "__main__":
    main()
