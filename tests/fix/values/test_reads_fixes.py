# SPDX-License-Identifier: MIT
"""`--fix` for what's read of an unannotated parameter whose members read are one class's of the module's."""

import ast
import textwrap
from pathlib import Path
from typing import Final, TypeAlias

from constricter import Checks, FixPolicy, Offence, check_source
from constricter.cli import command as cli
from constricter.fix.core.known import Classes, Outside
from constricter.fix.values import reads

# Each offence's fix and whether it's a guess.
_Fixed: TypeAlias = dict[str, tuple[str | None, bool]]
_READS: Final = FixPolicy(unsafe_select=frozenset({"reads"}))
SHOWN: Final = "    shown: list[str] = row.cells()\n"
WIDE: Final = "    wide: int = row.width\n"
SOURCE: Final = """
class Reader:
    size: int = 0
    '''A reader.'''

    def __init__(self):
        self.name = "r"

    def chunk(self) -> bytes:
        return b""


class Sized:
    size: int = 1


def use(reader, n, probed, typed: Reader):
    a = reader.name
    b = reader.chunk()
    c = reader.size
    d = n.size
    if isinstance(probed, Reader):
        pass
    e = probed.name
    f = probed.chunk()
    g = typed.name
    return a, b, c, d, e, f, g
"""


def _fixed(checks: Checks | None = None, source: str = SOURCE) -> _Fixed:
    found: list[Offence] = check_source(textwrap.dedent(source), checks=checks or Checks())
    return {o.name: (o.fix, o.unsafe) for o in found if len(o.name) == 1}


def test_a_parameter_is_typed_by_what_is_read_of_it() -> None:
    """Two members read of a parameter, one module class's alone: what's read of it is typed, as guesses."""
    assert _fixed() == {
        "a": ("str", True),
        "b": ("bytes", True),
        "c": ("int", True),
        "d": (None, False),  # one member read fits both classes
        "e": (None, False),  # probed: it's expected to be more than one type
        "f": (None, False),
        "g": ("str", True),  # `assigned`'s guess alone
    }


def test_trusted_reads_are_certain() -> None:
    """`unsafe-fix-select = ["reads"]` makes them certain, where they rest on nothing else."""
    trusted: _Fixed = _fixed(Checks(fixes=_READS))
    assert (trusted["a"], trusted["c"]) == (("str", True), ("int", False))


def test_a_shadowed_or_rebound_name_is_not_typed() -> None:
    """A class a name of the function shadows isn't the module's; a parameter it binds again isn't typed."""
    source: str = """
    class Reader:
        def __init__(self):
            self.name = "r"

        def chunk(self) -> bytes:
            return b""


    def shadowed(reader, Reader):
        a = reader.name
        b = reader.chunk()


    def rebound(reader):
        c = reader.name
        d = reader.chunk()
        reader = None
    """
    assert _fixed(source=source) == dict.fromkeys("abcd", (None, False))


def test_members_elsewhere_are_not_one_class() -> None:
    """Members two unrelated module classes have, or a builtin type or a stdlib class, aren't one's."""
    source: str = """
    class Stack:
        def append(self, item) -> None: ...
        def pop(self) -> int: ...


    class File:
        def read_text(self) -> str: ...
        stem: str = ""


    class Left:
        def run(self) -> int: ...
        def stop(self) -> int: ...


    class Right:
        def run(self) -> int: ...
        def stop(self) -> int: ...


    def use(stack, path, side):
        a = stack.pop()
        stack.append(1)
        b = path.read_text()
        c = path.stem
        d = side.run()
        e = side.stop()
    """
    assert _fixed(source=source) == dict.fromkeys("abcde", (None, False))


def test_a_base_is_taken_over_the_classes_inheriting_from_it() -> None:
    """Members a module class has, and others inheriting from it: that class's; a cycle of bases has none."""
    source: str = """
    class Machine:
        def run(self) -> int: ...
        def stop(self) -> str: ...


    class Fast(Machine):
        pass


    class Faster(Fast, Machine):
        pass


    class Loop(Cycle):
        def spin(self) -> int: ...
        def halt(self) -> int: ...


    class Cycle(Loop):
        pass


    def use(machine, looped):
        a = machine.run()
        b = machine.stop()
        c = looped.spin()
        d = looped.halt()
    """
    assert _fixed(source=source) == {
        "a": ("int", True),
        "b": ("str", True),
        "c": (None, False),
        "d": (None, False),
    }


def test_members() -> None:
    """A class's members: what its body binds, what its methods set on `self`, and its module bases'."""
    tree: ast.Module = ast.parse(
        textwrap.dedent(
            """
            import abc


            class Twice:
                pass


            class Twice:
                pass


            class Base(abc.ABC, Child):
                kept = 1
                one, two = 1, 2
                self_attr: int
                other.attr: int = 1
                pass

                @staticmethod
                def bare():
                    other.ignored = 1

                async def run(self, other):
                    self.ran = True
                    other.missed = 1
                    self.ran.deep = 1

                class Inner:
                    inner_only = 1


            class Child(Base):
                child = 1


            class Grandchild(Child, Base):
                pass
            """,
        ),
    )
    found: dict[str, reads.Members] = reads.members(tree)
    names: frozenset[str] = frozenset({"kept", "self_attr", "bare", "run", "ran", "Inner", "child"})
    assert found == {
        "Base": reads.Members(names, frozenset({"Child"})),
        "Child": reads.Members(names, frozenset({"Base"})),
        "Grandchild": reads.Members(names, frozenset({"Base", "Child"})),
    }


def test_typed_reads_only_named_members() -> None:
    """A dunder read is the object's, not its class's; a probe through `hasattr` counts as one."""
    tree: ast.Module = ast.parse("p.__class__; p.go; p.halt; q.go; q.halt; hasattr(q, 'go'); hasattr(1, 'x')")
    classes: dict[str, reads.Members] = {
        "Machine": reads.Members(frozenset({"go", "halt", "__class__"}), frozenset()),
    }
    assert reads.typed(ast.walk(tree), ["p", "q"], classes) == {"p": "Machine"}


def test_a_class_another_checked_file_defines() -> None:
    """A class the file imports from another checked file, by its typed members and one spelling of it."""
    source: str = """
    import pkg.types as t
    from pkg.types import Row


    class Local:
        def run(self) -> int: ...
        def stop(self) -> int: ...


    def use(row, t, other, local):
        a = row.cells()
        b = row.width
        c = other.spin()
        d = other.halt()
        e = local.run()
        f = local.stop()


    def spun(other):
        g = other.spin()
        h = other.halt()
    """
    imported: Classes = Classes(
        {"Row": {"width": "int"}, "t.Row": {"width": "int"}},
        {
            "Row": {"cells": "list[str]"},
            "t.Row": {"cells": "list[str]"},
            "t.Other": {"spin": "int", "halt": "str"},
            "t.Twin": {"run": "int", "stop": "int"},
        },
    )
    outside: Outside = Outside(classes=imported, same=(frozenset({"Row", "t.Row"}), frozenset({"t.Gone"})))
    found: list[Offence] = check_source(textwrap.dedent(source), outside=outside)
    assert {o.name: (o.fix, o.unsafe) for o in found if len(o.name) == 1} == {
        "a": ("list[str]", True),
        "b": ("int", True),
        "c": (None, False),  # the parameter `t` shadows the module `t.Other` is spelled through
        "d": (None, False),
        "e": (None, False),  # `Local` and `t.Twin` both have them
        "f": (None, False),
        "g": ("int", True),
        "h": ("str", True),
    }


def test_the_cli_types_by_another_files_class(tmp_path: Path) -> None:
    """Checked with the file defining it, a class it imports types what's read of a parameter."""
    _ = (tmp_path / "rows.py").write_text(
        textwrap.dedent(
            """
            class Row:
                width: int = 0

                def cells(self) -> list[str]:
                    return []
            """,
        ),
        encoding="utf-8",
    )
    app: Path = tmp_path / "app.py"
    _ = app.write_text(
        "from rows import Row\n\n\ndef show(row):\n    shown = row.cells()\n    wide = row.width\n",
        encoding="utf-8",
    )
    _ = cli.main(["--fix", "-q", "--unsafe-fix-select", "reads", str(tmp_path)])
    fixed: str = app.read_text(encoding="utf-8")
    assert SHOWN in fixed
    assert WIDE in fixed
