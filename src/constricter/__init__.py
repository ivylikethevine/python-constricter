# SPDX-License-Identifier: MIT
"""Every local variable typed where it's first bound."""

from constricter.checker import (
    COMMENT_TYPED_TARGET,
    DEFAULT_CHECKS,
    LEVELS,
    MISMATCHED_TYPE,
    NESTED_TYPE,
    NESTING,
    REDUNDANT_TYPE,
    UNANNOTATED,
    UNANNOTATED_MEMBER,
    UNTYPED_TARGET,
    VAGUE_TYPE,
    Checks,
    Coverage,
    Level,
    Offence,
    annotation_coverage,
    check_source,
    check_tree,
)

__version__ = "0.2.3"
__all__ = [
    "COMMENT_TYPED_TARGET",
    "DEFAULT_CHECKS",
    "LEVELS",
    "MISMATCHED_TYPE",
    "NESTED_TYPE",
    "NESTING",
    "REDUNDANT_TYPE",
    "UNANNOTATED",
    "UNANNOTATED_MEMBER",
    "UNTYPED_TARGET",
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
