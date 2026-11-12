"""Measure what django-stubs' mypy plugin types of the bindings `--fix` leaves on django's own test apps.

  local/.venv/bin/python -m scratch.plugin_types VENV WORK [APP ...]

VENV: an environment with `django`, `django-stubs` and `mypy` (`uv pip install`: none is a
dependency here), django's version the corpus's. WORK: a folder to write in. Copies each APP of the
django corpus's `tests/` (a default dozen with models and queries) into WORK with a settings module
installing them, checks the copy at `suffocate` with `--unsafe-fixes` in one process, and after each
plain assignment left with no fix writes `reveal_type(NAME)`. mypy then reads the copy three times,
checking unannotated bodies: with django-stubs and its plugin, with the stubs alone, and with
neither (django's source). Prints, of those bindings, how many each reading reveals as a type with
no `Any` in it, the commonest such types, and how many only the plugin types. About a minute, 1
worker on 16CPU/60GB.
"""

import ast
import json
import re
import shutil
import subprocess
import sys
from collections import Counter
from pathlib import Path

from tests.corpus import catalog, trees

APPS = (
    "basic",
    "queries",
    "aggregation",
    "lookup",
    "many_to_one",
    "many_to_many",
    "one_to_one",
    "select_related",
    "ordering",
    "annotations",
    "update",
    "custom_managers",
)
SETTINGS = """SECRET_KEY = "x"
DATABASES = {{"default": {{"ENGINE": "django.db.backends.sqlite3", "NAME": ":memory:"}}}}
DEFAULT_AUTO_FIELD = "django.db.models.AutoField"
USE_TZ = False
INSTALLED_APPS = ["django.contrib.contenttypes", "django.contrib.auth", {apps}]
"""
CONFIG = """[mypy]
check_untyped_defs = True
ignore_missing_imports = True
{plugin}
[mypy.plugins.django-stubs]
django_settings_module = plugin_settings
"""
REVEALED = re.compile(r'^(?P<path>[^:]+):(?P<line>\d+): note: Revealed type is "(?P<type>.*)"$')


def unfixed(work: Path, apps: list[str]) -> dict[tuple[str, int], str]:
    ran = subprocess.run(
        [
            sys.executable,
            "-m",
            "constricter",
            "--format=json",
            "--unsafe-fixes",
            "--all-scopes",
            "--level=suffocate",
            "--jobs=1",
            *apps,
        ],
        cwd=work,
        capture_output=True,
        text=True,
        check=False,
    )
    found = {}
    for offence in json.loads(ran.stdout):
        if offence["code"] == "LVA001" and offence["fix"] is None:
            name = offence["message"].split("'")[1]
            found[offence["path"], offence["line"]] = name  # as given: relative to `work`
    return found


def revealing(work: Path, bindings: dict[tuple[str, int], str]) -> dict[tuple[str, int], tuple[str, int]]:
    """Write `reveal_type(NAME)` after each plain assignment among `bindings`; say where each landed."""
    placed = {}
    by_path: dict[str, dict[int, str]] = {}
    for (path, line), name in bindings.items():
        by_path.setdefault(path, {})[line] = name
    for path, lines in by_path.items():
        source = (work / path).read_text(encoding="utf-8")
        text = source.splitlines()
        inserts = []
        for node in ast.walk(ast.parse(source)):
            if not isinstance(node, ast.Assign) or len(node.targets) != 1:
                continue
            target = node.targets[0]
            if isinstance(target, ast.Name) and lines.get(node.lineno) == target.id:
                inserts.append((node.end_lineno or node.lineno, node.col_offset, node.lineno, target.id))
        for added, (end, indent, line, name) in enumerate(sorted(inserts)):
            text.insert(end + added, f"{' ' * indent}reveal_type({name})")
            placed[path, end + added + 1] = (name, line)
        (work / path).write_text("\n".join(text) + "\n", encoding="utf-8")
    return placed


def revealed(venv: Path, work: Path, apps: list[str], reading: str) -> dict[tuple[str, int], str]:
    plugin = "plugins = mypy_django_plugin.main" if reading == "plugin" else ""
    (work / "mypy.ini").write_text(CONFIG.format(plugin=plugin), encoding="utf-8")
    stubs = venv.glob("lib/python*/site-packages/django-stubs")
    hidden = (
        [each.rename(each.with_name("django-stubs.off")) for each in stubs] if reading == "source" else []
    )
    try:
        ran = subprocess.run(
            [
                str(venv / "bin" / "python"),
                "-m",
                "mypy",
                "--no-incremental",
                "--config-file",
                "mypy.ini",
                *apps,
            ],
            cwd=work,
            capture_output=True,
            text=True,
            check=False,
        )
    finally:
        for each in hidden:
            each.rename(each.with_name("django-stubs"))
    (work / f"mypy-{reading}.txt").write_text(ran.stdout + ran.stderr, encoding="utf-8")
    found = {}
    for line in ran.stdout.splitlines():
        if match := REVEALED.match(line):
            found[match["path"], int(match["line"])] = match["type"]
    return found


def main() -> int:
    venv, work, *apps = sys.argv[1:]
    apps = apps or list(APPS)
    root = trees.found(catalog.load().entries["django"], settle=False).root.parent
    out = Path(work)
    shutil.rmtree(out, ignore_errors=True)
    out.mkdir(parents=True)
    for app in apps:
        shutil.copytree(root / "tests" / app, out / app)
    (out / "plugin_settings.py").write_text(
        SETTINGS.format(apps=", ".join(f'"{app}"' for app in apps)), encoding="utf-8"
    )
    bindings = unfixed(out, apps)
    placed = revealing(out, bindings)
    print(f"{len(apps)} apps: {len(bindings)} bindings with no fix, {len(placed)} of them a plain assignment")
    typed: dict[str, dict[tuple[str, int], str]] = {}
    for reading in ("plugin", "stubs", "source"):
        got = revealed(Path(venv).resolve(), out, apps, reading)
        typed[reading] = {key: kind for key, kind in got.items() if key in placed and "Any" not in kind}
        print(f"-- {reading}: {len(got)} revealed, {len(typed[reading])} with no `Any`")
    only = {key: kind for key, kind in typed["plugin"].items() if key not in typed["stubs"]}
    print(f"only with the plugin: {len(only)}")
    for kind, count in Counter(re.sub(r"\b\w+(\.\w+)+\.", "", kind) for kind in only.values()).most_common(
        15
    ):
        print(f"  {count:5}  {kind}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
