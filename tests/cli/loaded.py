# SPDX-License-Identifier: MIT
"""What a `--jobs` worker has imported, asked from inside it: nothing here imports constricter."""

import sys


def imported(name: str) -> bool:
    """Say whether this process has imported the module `name`.

    Returns:
      Whether it has.

    """
    return name in sys.modules
