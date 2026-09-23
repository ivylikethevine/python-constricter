# SPDX-License-Identifier: MIT
"""Fetch the corpora that can't be installed as dependencies: Python 2 code, from pinned, hash-checked sdists.

  local/.venv/bin/python tests/corpus/corpus_sources.py twisted       # prints the checked directory
  local/.venv/bin/python tests/corpus/corpus_sources.py --describe    # each: name, version, directory

Each is downloaded once into `local/corpus-sources/`, its SHA-256 checked, unpacked there (with
tarfile's `data` filter: nothing outside the directory, no links or devices), and its package
directory printed. Python 3 can't parse all of it, which is the point: that's legacy code as it's
found, and the command must report such files, not crash on them.
"""

import hashlib
import sys
import tarfile
import urllib.request
from collections.abc import Sequence
from pathlib import Path
from typing import Final, NamedTuple


class Source(NamedTuple):
    """One pinned sdist: its version, where it is, its SHA-256, and the directory to check in it."""

    version: str
    url: str
    sha256: str
    package: str  # relative to the unpacked sdist


WORK: Final = Path(__file__).resolve().parents[2] / "local" / "corpus-sources"
SOURCES: Final = {
    # Twisted's last Python 2-only line (MIT): print statements, `except X, e`, tuple parameters and
    # backticks next to 2/3-era code with `__future__` imports; about 1 file in 5 doesn't parse.
    "twisted": Source(
        "12.3.0",
        "https://files.pythonhosted.org/packages/source/T/Twisted/Twisted-12.3.0.tar.bz2",
        "d4d1afcfa7ca40a7da26832cba653851eb147a06bd3f7f6fae89af3d5cd295c6",
        "Twisted-12.3.0/twisted",
    ),
    # The last pip for Python 2 (MIT): 2/3-era code whose `# type:` comments sit in modules importing
    # Python 2 `__future__` features, the path those comments count on automatically. A dependency
    # can't pin it: it would replace the environment's own pip.
    "pip": Source(
        "20.3.4",
        "https://files.pythonhosted.org/packages/source/p/pip/pip-20.3.4.tar.gz",
        "6773934e5f5fc3eaa8c5a44949b5b924fc122daa0a8aa9f80c835b4ca2a543fc",
        "pip-20.3.4/src/pip",
    ),
}


def fetch(name: str, work: Path = WORK) -> Path:
    """Download (once), check and unpack source `name`.

    Returns:
      Its package directory.

    Raises:
      ValueError: the download's SHA-256 isn't the pinned one.

    """
    source: Source = SOURCES[name]
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
    tests/corpus/corpus_table.py, which runs this rather than import it: it runs as a script, not from
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
