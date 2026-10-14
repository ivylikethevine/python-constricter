# SPDX-License-Identifier: MIT
"""Fetch the corpora that can't be installed as dependencies, from pinned, hash-checked sdists.

  local/.venv/bin/python tests/corpus/corpus_sources.py twisted       # prints the checked directory
  local/.venv/bin/python tests/corpus/corpus_sources.py --describe    # each: name, version, directory

`corpora.toml` pins them (`pinned`): each corpus's `sdist` table. Each is downloaded once into
`local/corpus-sources/`, its SHA-256 checked, unpacked there (with
tarfile's `data` filter: nothing outside the directory, no links or devices), and its package
directory printed. Python 3 can't parse all of Twisted's or pip's, which is the point: that's
legacy code as it's found, and the command must report such files, not crash on them. The standard
library's is CPython's source release, whose `Lib` has the tests a prebuilt Python leaves out.
"""

import hashlib
import sys
import tarfile
import tomllib
import urllib.request
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import IO, Final, NamedTuple, TypeAlias, cast


class Source(NamedTuple):
    """One pinned sdist: its version, where it is, its SHA-256, and the directory to check in it."""

    version: str
    url: str
    sha256: str
    package: str  # relative to the unpacked sdist


WORK: Final = Path(__file__).resolve().parents[2] / "local" / "corpus-sources"
CATALOG: Final = Path(__file__).with_name("corpora.toml")
FILES: Final = "https://files.pythonhosted.org/packages"  # PyPI's file host, which a `where` is under
_SDIST: Final = "sdist"
_Table: TypeAlias = dict[str, object]  # a table of the catalog, as `tomllib` reads it


def pinned(among: str | None = None) -> dict[str, Source]:
    """Read the sdists `corpora.toml` pins: every corpus's that has one, or those of the set `among`.

    Returns:
      Each by its corpus's name.

    """
    file: IO[bytes]
    with CATALOG.open("rb") as file:
        catalog: _Table = tomllib.load(file)
    entries: dict[str, _Table] = cast("dict[str, _Table]", catalog["corpus"])
    names: list[str] = cast("dict[str, list[str]]", catalog["sets"])[among] if among else list(entries)
    found: dict[str, Source] = {}
    name: str
    for name in names:
        entry: _Table = entries[name]
        if _SDIST in entry:
            sdist: dict[str, str] = cast("dict[str, str]", entry[_SDIST])
            found[name] = Source(
                str(entry["version"]),
                sdist.get("url") or f"{FILES}/{sdist['where']}/{sdist['archive']}",
                sdist["sha256"],
                sdist["package"],
            )
    return found


# The seven corpora's: the standard library's, and Twisted's and pip's last lines for Python 2.
SOURCES: Final = pinned("seven")


def fetch(name: str, work: Path = WORK, sources: Mapping[str, Source] | None = None) -> Path:
    """Download (once), check and unpack source `name` of `sources` (default: `SOURCES`), under `work`.

    Returns:
      Its package directory.

    Raises:
      ValueError: the download's SHA-256 isn't the pinned one.

    """
    source: Source = (SOURCES if sources is None else sources)[name]
    root: Path = work / f"{name}-{source.version}"
    package: Path = root / source.package
    if package.is_dir():
        return package
    archive: Path = work / source.url.rsplit("/", 1)[1]
    if not archive.exists():
        work.mkdir(parents=True, exist_ok=True)
        _ = urllib.request.urlretrieve(source.url, archive)  # a pinned https URL
    digest: str
    if (digest := hashlib.sha256(archive.read_bytes()).hexdigest()) != source.sha256:
        archive.unlink()
        message: str = f"{archive.name}: SHA-256 {digest}, not the pinned {source.sha256}"
        raise ValueError(message)
    tar: tarfile.TarFile
    with tarfile.open(archive) as tar:
        tar.extractall(root, filter="data")
    return package


_DESCRIBE: Final = "--describe"


def main(argv: Sequence[str]) -> int:
    """Fetch each source named (default: all) and print its package directory.

    With `--describe`, each line is its name, version and directory, tab-separated (for
    `corpus_table.corpora`, which runs this rather than import it: it's read as a script too, not from
    the `tests` package).

    Returns:
      0.

    """
    names: list[str] = [arg for arg in argv if arg != _DESCRIBE] or list(SOURCES)
    name: str
    for name in names:
        where: Path = fetch(name)
        line: str = f"{name}\t{SOURCES[name].version}\t{where}" if _DESCRIBE in argv else str(where)
        _ = sys.stdout.write(f"{line}\n")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
