# SPDX-License-Identifier: MIT
"""What a run's records hold, as the runner's tests write them: shared by its test modules."""

from typing import Final

from tests.corpus.pipeline import Record

SHARE: Final = 75  # percent of the machine
USED: Final[Record] = {  # what a step used, in its record
    "seconds": 10.0,
    "cpu": 25.0,
    "memory": 9.5,
    "given": {"cpus": 2, "memory": 5.0},
    "alone": False,
}
