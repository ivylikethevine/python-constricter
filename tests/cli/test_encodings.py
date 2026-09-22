# SPDX-License-Identifier: MIT
"""Source in any encoding Python reads: a PEP 263 declaration, a BOM, or UTF-8."""

from pathlib import Path
from typing import Final

import pytest

from constricter.cli import command as cli

LATIN_1: Final = '# -*- coding: latin-1 -*-\ndef f() -> None:\n    x = "café"\n'
KOI8_R: Final = '# -*- encoding: koi8-r -*-\ntest = "Познание"\n'
BOM: Final = b"\xef\xbb\xbfdef f() -> None:\n    z = 1\n"


@pytest.mark.parametrize(
    ("source", "encoding", "fixed"),
    [
        (LATIN_1, "latin-1", LATIN_1.replace("x =", "x: str =")),
        (KOI8_R, "koi8-r", KOI8_R.replace("test =", "test: str =")),
    ],
)
def test_a_declared_encoding_checks_and_fixes_in_it(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
    source: str,
    encoding: str,
    fixed: str,
) -> None:
    """A module in its declared encoding reads as Python reads it, and `--fix` writes it back in it."""
    path: Path = tmp_path / "encoded.py"
    _ = path.write_bytes(source.encode(encoding))
    assert cli.main(["--all-scopes", str(path)]) == cli.EXIT_FOUND
    assert capsys.readouterr().out.startswith(f"{path}:")
    assert cli.main(["--fix", "--all-scopes", "-q", str(path)]) == cli.EXIT_CLEAN
    assert path.read_bytes() == fixed.encode(encoding)


def test_a_bom_is_kept(tmp_path: Path) -> None:
    """A UTF-8 BOM reads as Python reads it, and `--fix` keeps it."""
    path: Path = tmp_path / "bom.py"
    _ = path.write_bytes(BOM)
    assert cli.main(["--fix", "-q", str(path)]) == cli.EXIT_CLEAN
    assert path.read_bytes() == BOM.replace(b"z = 1", b"z: int = 1")


def test_an_unknown_encoding_is_an_error(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """A declaration naming no codec exits 2, as a syntax error does."""
    path: Path = tmp_path / "unknown.py"
    _ = path.write_bytes(b"# -*- coding: uft-8 -*-\nx = 1\n")
    assert cli.main([str(path)]) == cli.EXIT_ERROR
    assert capsys.readouterr().err.startswith(f"{path}: error: unknown encoding: uft-8")


def test_a_fix_the_encoding_cant_hold_leaves_the_file(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """An annotation (here another module's return type) a file's encoding can't hold isn't written.

    The file stays as it was, its offences are all still reported, and the run exits 2.
    """
    _ = (tmp_path / "c.py").write_text("class Ω:\n    pass\n", encoding="utf-8")
    _ = (tmp_path / "a.py").write_text("import c as t\ndef f() -> t.Ω:\n    return t.Ω()\n", encoding="utf-8")
    source: bytes = b"# -*- coding: latin-1 -*-\nimport c as t\nfrom a import f\n"
    source += b"def g() -> None:\n    w = f()\n    v = 1\n"
    path: Path = tmp_path / "b.py"
    _ = path.write_bytes(source)
    assert cli.main(["--fix", str(tmp_path)]) == cli.EXIT_ERROR
    assert path.read_bytes() == source
    out: str
    err: str
    out, err = capsys.readouterr()
    assert (
        err == f"{path}: error: an annotation can't be written in its encoding, iso8859-1; left as it was\n"
    )
    assert out.endswith("Found 2 error(s) and 0 warning(s) in 3 file(s); fixed 0.\n")
