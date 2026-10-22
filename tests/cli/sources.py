"""Sources the command's tests check, and writing one: shared by its test modules."""

import textwrap
from pathlib import Path
from typing import Final

BROKEN: Final = """
def broken(items: list[int]) -> None:
    plain = 1
    other = 2  # noqa: LVA001
    third = 3  # noqa
    fourth = 4  # noqa: E501
    for loop in items:
        pass
    for hushed in items:  # noqa: LVA002
        pass
"""
PLAIN: Final = "local variable 'plain' is not annotated where it's first bound"
DEMO_CODES: Final = ("LVA001", "LVA001", "LVA002")
DEMO: Final = "def f(items: list[int]) -> None:\n  a = 1\n  b = []\n  for c in items:\n    pass\n"


def written(path: Path, source: str) -> Path:
    """Write `source`, dedented, to `path`, its directories made first.

    Returns:
      The path.

    """
    path.parent.mkdir(parents=True, exist_ok=True)
    _ = path.write_text(textwrap.dedent(source), encoding="utf-8", newline="\n")
    return path


# A language server, behaving as each test asks it to.
FAKE_SERVER: Final = Path(__file__).with_name("fake_server.py")
