# SPDX-License-Identifier: MIT
"""Every local variable typed where it's first bound."""

from constricter.checker import (
  COMMENT_TYPED_TARGET,
  LEVELS,
  NESTED_TYPE,
  NESTING,
  UNANNOTATED,
  UNANNOTATED_MEMBER,
  UNTYPED_TARGET,
  VAGUE_TYPE,
  Coverage,
  Level,
  Offence,
  annotation_coverage,
  check_source,
  check_tree,
)

__version__ = "0.2.0"
__all__ = [
  "COMMENT_TYPED_TARGET",
  "LEVELS",
  "NESTED_TYPE",
  "NESTING",
  "UNANNOTATED",
  "UNANNOTATED_MEMBER",
  "UNTYPED_TARGET",
  "VAGUE_TYPE",
  "Coverage",
  "Level",
  "Offence",
  "__version__",
  "annotation_coverage",
  "check_source",
  "check_tree",
]
