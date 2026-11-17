"""List the stored hints `offers` drops for naming another thing than the file binds the name to.

  local/.venv/bin/python -m scripts.scratch.misbound_hints CHECKOUT PACKAGE

CHECKOUT is a corpus's checkout (`local/corpus-suites/httpx-0.28.1`), whose `.venv` holds the
packages its checkers read; PACKAGE the folder under it that is indexed (`httpx`, `lib/sqlalchemy`).
Every hint the store (`~/.cache/constricter/hints`) holds for a file there, of every checker and
round, is judged once as `offers.vetted` judges it: dropped where what it shows writes bare a name
the file binds to a module, or one its edits import from where another class is defined, and its
edit's own text does too (`offers._misbound`). Prints the count, then each one dropped: its file,
place, what it shows, its edit's text and imports. Reads the store alone; about a minute for
sqlalchemy on 16CPU/60GB.
"""

import json
import os
import sys
from pathlib import Path

ROOT = Path(sys.argv[1]).resolve()
os.environ["VIRTUAL_ENV"] = str(ROOT / ".venv")  # what `installed.search_path` reads

from constricter.fix.core.known import Offered  # noqa: E402
from constricter.fix.index import offers, project  # noqa: E402
from constricter.fix.index.modules import PACKAGE  # noqa: E402
from constricter.fix.index.stubs import installed  # noqa: E402

STORE = Path.home() / ".cache" / "constricter" / "hints"


def main() -> None:
    paths = sorted((ROOT / sys.argv[2]).rglob("*.py"))
    catalog = installed.with_installed(project.index(paths), installed.search_path())
    relative = {str(path.relative_to(ROOT)): path for path in paths}
    seen = set()
    dropped = []
    for entry in STORE.glob("*.json"):
        for stored, hints in json.loads(entry.read_text()).get("found", {}).items():
            name = next((each for each in relative if stored == each or stored.endswith("/" + each)), None)
            if name is None:
                continue
            path = relative[name]
            module = (project.module_name(path), path.stem == PACKAGE)
            target = catalog.modules.get(module[0])
            bound = {} if target is None else {**target.guarded, **target.names}
            for where, value in hints.items():
                key = json.dumps([name, where, value])
                if key in seen:
                    continue
                seen.add(key)
                edit = None if value[1] is None else Offered(value[1], tuple(value[2] or ()))
                imports = () if edit is None else edit.imports
                if offers._misbound(catalog, module, bound, value[0], imports) and (  # noqa: SLF001
                    edit is None or offers._misbound(catalog, module, bound, edit.text, imports)  # noqa: SLF001
                ):
                    dropped.append(f"{name}:{where} {value[0]!r} {value[1]!r} {value[2]}")
    print(f"{len(seen)} distinct stored hints, {len(dropped)} dropped")
    for line in sorted(dropped):
        print(line)


if __name__ == "__main__":
    main()
