# SPDX-License-Identifier: MIT
"""Generate the standard-library tables: `python -m stdlib_tables` (see `stdlib_tables.generate`)."""

import sys

from stdlib_tables.generate import main

sys.exit(main(sys.argv[1:]))
