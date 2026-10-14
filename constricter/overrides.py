# SPDX-License-Identifier: MIT
"""`typing.override`, which is Python 3.12+, on 3.11 too: what type checkers see, and nothing at run time.

Apart from the modules mypyc compiles, which takes the code under `if TYPE_CHECKING:` for the code
that runs, and so this `else` for code no run reaches.
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing_extensions import override
else:

    def override(func: object) -> object:
        """Mark an override (for type checkers only).

        Returns:
          `func`, unchanged.

        """
        return func


__all__ = ["override"]
