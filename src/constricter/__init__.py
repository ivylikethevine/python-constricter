"""Every local variable annotated where it's first bound."""

from importlib.metadata import PackageNotFoundError, version

from constricter.checker import CODE, Offence, check_source, check_tree

try:
    __version__: str = version("python-constricter")
except PackageNotFoundError:  # uninstalled source tree
    __version__ = "0.0.0"

__all__ = ["CODE", "Offence", "__version__", "check_source", "check_tree"]
