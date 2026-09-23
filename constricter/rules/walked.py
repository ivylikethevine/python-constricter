# SPDX-License-Identifier: MIT
"""One walk of a whole module, shared by every pass over all of it (importing nothing of constricter's)."""

import ast
from functools import lru_cache


@lru_cache(maxsize=4)  # the module being checked: every pass over all of it reads this one walk
def nodes(tree: ast.Module) -> tuple[ast.AST, ...]:
    """Walk a whole module once, for every pass that looks at all of it.

    `ast.walk` is most of a check's time (on the standard library, 57%): eight passes each walking
    every module whole took a quarter of it.

    Returns:
      Every node in it, in `ast.walk`'s order.

    """
    return tuple(ast.walk(tree))
