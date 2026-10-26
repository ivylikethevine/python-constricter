"""Where a checked module's names come from: a relative import resolved (`origins.absolute`)."""

from constricter.fix.index.origins import absolute


def test_a_relative_import_climbs_the_package_and_no_further() -> None:
    """As Python resolves it; one past the top package names no module, as Python refuses it."""
    within: list[str] = [
        absolute("pkg.sub.mod", "other", 1, is_package=False),
        absolute("pkg.sub.mod", "other", 2, is_package=False),
        absolute("pkg.sub", None, 1, is_package=True),
        absolute("pkg.sub.mod", "x", 0, is_package=False),
    ]
    assert within == ["pkg.sub.other", "pkg.other", "pkg.sub", "x"]
    beyond: list[str] = [
        absolute("pkg.sub.mod", "other", 3, is_package=False),
        absolute("a.b.c.d", "e", 5, is_package=False),
    ]
    assert beyond == ["...other", ".....e"]
