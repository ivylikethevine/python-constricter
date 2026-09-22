# SPDX-License-Identifier: MIT
"""`python -m constricter`."""

import sys

from constricter.cli import main

if __name__ == "__main__":  # not when `--jobs` workers import it
    sys.exit(main())
