"""A body's own nodes, walked whole once and kept for the passes that walk it again."""

import ast
from typing import Final

from constricter.source.syntax import own_nodes

_SOURCE: Final = """
def outer(items):
    total = 0
    for item in items:
        total += item
    def inner():
        return total
    return [inner() for _ in items]
"""
_BODIES: Final = 2000  # more than are kept: the earliest walks are dropped, and walked again


def _body() -> list[ast.stmt]:
    func: ast.stmt = ast.parse(_SOURCE).body[0]
    assert isinstance(func, ast.FunctionDef)
    return func.body


def test_a_body_walked_again_gives_the_same_nodes() -> None:
    """The walk kept, and with parents asked for, each node's, as a walk of its own found them."""
    body: list[ast.stmt] = _body()
    first: list[ast.AST] = list(own_nodes(body))
    assert list(own_nodes(body)) == first
    parents: dict[int, ast.AST] = {}
    assert list(own_nodes(body, parents)) == first
    assert set(parents) == {id(node) for node in first} - {id(stmt) for stmt in body}
    again: dict[int, ast.AST] = {}
    assert list(own_nodes(body, again)) == first
    assert again == parents
    returned: ast.stmt = body[3]
    assert isinstance(returned, ast.Return)
    assert parents[id(returned.value)] is returned
    assert all(not isinstance(node, ast.Return) or node is returned for node in first)  # not `inner`'s
    assert list(own_nodes(body[1:])) == first[first.index(body[1]) :]


def test_a_walk_stopped_early_is_walked_whole_the_next_time() -> None:
    """A walk stopped early (`any`) keeps nothing: the next one walks the body whole."""
    body: list[ast.stmt] = _body()
    assert any(isinstance(node, ast.Assign) for node in own_nodes(body))
    assert list(own_nodes(body)) == list(own_nodes(body, {}))


def test_the_earliest_walks_are_dropped() -> None:
    """Past as many as are kept, a body walked long before is walked again, the same."""
    bodies: list[list[ast.stmt]] = [_body() for _ in range(_BODIES)]
    walks: list[list[ast.AST]] = [list(own_nodes(body)) for body in bodies]
    assert [list(own_nodes(body)) for body in bodies] == walks
    assert walks == [list(own_nodes(body, {})) for body in bodies]
