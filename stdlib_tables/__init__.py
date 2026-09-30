# SPDX-License-Identifier: MIT
"""The generator of `constricter/fix/tables/`, from typeshed's standard-library stubs (see `generate`).

`constricter`'s own `__init__` loads those tables, so unless it's imported already, the modules of it
the generator uses are imported without it: a checkout has no tables until they're generated.
"""

import sys
from pathlib import Path
from types import ModuleType
from typing import Final

_NAME: Final = "constricter"
_PACKAGE: Final = ModuleType(_NAME)
_PACKAGE.__path__ = [str(Path(__file__).parents[1] / _NAME)]
_ = sys.modules.setdefault(_NAME, _PACKAGE)
