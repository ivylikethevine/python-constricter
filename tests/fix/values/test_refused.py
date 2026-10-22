"""Why a call has no fix: the reason `--format=json` gives (`unfixed`), for the corpus census."""

import textwrap

from constricter import Checks, check_source
from constricter.fix.values.refused import REASONS

_SOURCE: str = """
import json
import os

import requests
from typing import Any

def helper(x):
    return x

def vague() -> Any: ...

class Box:
    def sized(self) -> int:
        return 1

def f(param, box: Box, callback) -> None:
    untyped = helper(1)
    receiver = param.load()
    member = box.missing()
    library = json.loads("{}")
    imported = requests.get("url")
    local = callback()
    vaguer = vague()
    other = (lambda: 1)()
    typed = box.sized()
    joined = os.path.join("a", "b")
    listed = [param]
"""


def test_a_call_with_no_fix_says_why() -> None:
    """Each reason, by what the call is; none for a fixed binding, or a value that isn't a call."""
    found: dict[str, str] = {
        o.name: o.unfixed for o in check_source(textwrap.dedent(_SOURCE), checks=Checks())
    }
    assert found == {
        "untyped": "untyped",
        "receiver": "receiver",
        "member": "member",
        "library": "library",
        "imported": "imported",
        "local": "local",
        "vaguer": "vague",
        "other": "other",
        "typed": "",
        "joined": "",
        "listed": "",
    }
    assert set(found.values()) - {""} <= set(REASONS)
