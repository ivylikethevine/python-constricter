"""Every local variable annotated where it's first bound: a flake8 plugin, a pylint plugin and a
standalone command, all running the one check in `constricter.checker`."""

from importlib.metadata import PackageNotFoundError, version

from constricter.checker import CODE, Offence, check_source, check_tree

try:
    __version__: str = version("python-constricter")
except PackageNotFoundError:  # running from a source tree that isn't installed
    __version__ = "0.0.0"

__all__ = ["CODE", "Offence", "__version__", "check_source", "check_tree"]
