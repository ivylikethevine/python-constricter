"""`--fix` checking a file again where a fix imports a checked file's class it reads the members of."""

from pathlib import Path
from typing import Final

from constricter.cli import command as cli
from constricter.fix.index import crossed, project

_CLASS: Final = 'class TextIO:\n    encoding: str = "x"\n\n\nclass Other:\n    other: str = "x"\n'
_USE: Final = """
import tokenize


def f(p):
    with tokenize.open(p) as g:
        e = g.encoding
"""
_USE_FIXED: Final = "        e: str = g.encoding\n"


def test_a_fix_importing_a_class_types_what_the_file_reads_of_it_in_the_same_run(tmp_path: Path) -> None:
    """`g: TextIO`, from the standard-library tables: its members known only once the file spells it."""
    _ = (tmp_path / "typing.py").write_text(_CLASS, encoding="utf-8")
    use: Path = tmp_path / "use.py"
    _ = use.write_text(_USE, encoding="utf-8")
    _ = cli.main(["--fix", "-q", "--jobs=1", str(tmp_path)])
    assert _USE_FIXED in use.read_text(encoding="utf-8")


def test_what_a_file_reads_of_an_imported_class_is_told_by_its_members(tmp_path: Path) -> None:
    """Of a checked file's class alone, by a `from` import; nothing for a file the index doesn't have."""
    _ = (tmp_path / "typing.py").write_text(_CLASS, encoding="utf-8")
    use: Path = tmp_path / "use.py"
    _ = use.write_text(_USE, encoding="utf-8")
    catalog: project.Index = project.index(sorted(tmp_path.glob("*.py")))
    assert crossed.reads_imported(catalog, use, ("from typing import TextIO",))
    assert not crossed.reads_imported(catalog, use, ("from typing import Other",))
    assert not crossed.reads_imported(catalog, use, ("from os import path", "import typing"))
    assert not crossed.reads_imported(catalog, tmp_path / "missing.py", ("from typing import TextIO",))
