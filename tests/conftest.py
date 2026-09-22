# SPDX-License-Identifier: MIT
"""Test collection: the fuzz tests need hypothesmith, which the `test` group leaves out."""

import importlib.util

collect_ignore: list[str] = [] if importlib.util.find_spec("hypothesmith") else ["test_fuzz.py"]
