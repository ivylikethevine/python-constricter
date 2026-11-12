"""Print the `sdist` table `tests/corpus/corpora.toml` pins for each package, from PyPI.

  python3 -I scripts/scratch/corpus_pins.py NAME[==VERSION] ...

For each: the version (the latest, or the one given), its sdist's `where`, `archive` and `sha256`,
its upload time (to keep to releases at least two weeks old) and its GitHub links. The `package`
directory and the suite are read from the sdist and the repository's CI by hand.
"""

import json
import sys
import urllib.request

FILES = "https://files.pythonhosted.org/packages/"

for spec in sys.argv[1:]:
    with urllib.request.urlopen(f"https://pypi.org/pypi/{spec.replace('==', '/')}/json") as response:
        data = json.load(response)
    info = data["info"]
    links = {key: url for key, url in (info.get("project_urls") or {}).items() if "github" in url}
    print(f"== {info['name']} {info['version']} (requires Python {info.get('requires_python')})")
    for each in data["urls"]:
        if each["packagetype"] == "sdist":
            where, _, archive = each["url"].removeprefix(FILES).rpartition("/")
            print(f'where = "{where}"\narchive = "{archive}"\nsha256 = "{each["digests"]["sha256"]}"')
            print(f"uploaded {each['upload_time']}")
    print(f"links {links}")
