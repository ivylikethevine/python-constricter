# SPDX-License-Identifier: MIT
"""Every local variable typed where it's first bound."""

from constricter.offences import (
    COMMENT_TYPED_TARGET,
    DEFAULT_CHECKS,
    LEVELS,
    LONG_TUPLE,
    MAX_LENGTH,
    MISMATCHED_TYPE,
    NARROWABLE_TYPE,
    NESTED_TYPE,
    NESTING,
    REDUNDANT_TYPE,
    UNANNOTATED,
    UNANNOTATED_MEMBER,
    UNTYPED_TARGET,
    UNUSED_UNION_MEMBER,
    VAGUE_TYPE,
    Checks,
    Level,
    Offence,
)
from constricter.rules.checker import Coverage, annotation_coverage, check_source, check_tree

__version__ = "0.2.3"
__all__ = [
    "COMMENT_TYPED_TARGET",
    "DEFAULT_CHECKS",
    "LEVELS",
    "LONG_TUPLE",
    "MAX_LENGTH",
    "MISMATCHED_TYPE",
    "NARROWABLE_TYPE",
    "NESTED_TYPE",
    "NESTING",
    "REDUNDANT_TYPE",
    "UNANNOTATED",
    "UNANNOTATED_MEMBER",
    "UNTYPED_TARGET",
    "UNUSED_UNION_MEMBER",
    "VAGUE_TYPE",
    "Checks",
    "Coverage",
    "Level",
    "Offence",
    "__version__",
    "annotation_coverage",
    "check_source",
    "check_tree",
]
