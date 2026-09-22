# SPDX-License-Identifier: MIT
"""Fuzzing: generated Python never crashes the checker, and its fixes keep the code valid."""

import ast
import warnings

import hypothesmith
from hypothesis import HealthCheck, given, reject, settings
from hypothesis import strategies as st

from constricter import fixes
from constricter.checker import Offence, check_source
from constricter.noqa import lines

# Generating from the grammar is slow and discards what doesn't compile; that's expected.
FUZZ: settings = settings(
  max_examples=150,
  deadline=None,
  suppress_health_check=[HealthCheck.too_slow, HealthCheck.filter_too_much],
)


def _compiles(source: str) -> bool:
  with warnings.catch_warnings():
    warnings.simplefilter("ignore")  # e.g. invalid escape sequences in generated strings
    try:
      _ = compile(source, "<fuzz>", "exec", dont_inherit=True)
    except (SyntaxError, ValueError):
      return False
  return True


@FUZZ
@given(hypothesmith.from_grammar(), st.tuples(st.booleans(), st.booleans()))
def test_valid_python_never_crashes_the_checker(source: str, flags: tuple[bool, bool]) -> None:
  """Any valid Python is checked without an exception, with any options."""
  if not _compiles(source):
    reject()
  offences: list[Offence] = check_source(source, all_scopes=flags[0], type_comments=flags[1])
  assert offences == sorted(offences)


@FUZZ
@given(hypothesmith.from_grammar())
def test_fixes_keep_the_code_valid(source: str) -> None:
  """Adding every annotation `--fix` offers leaves code that still parses."""
  if not _compiles(source):
    reject()
  fixed: str = "".join(fixes.apply(lines(source), check_source(source, all_scopes=True)))
  _ = ast.parse(fixed)
