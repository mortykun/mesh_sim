import pytest

from mesh.generic import GenericNode
from utils.space import Position


@pytest.fixture
def rand_pos() -> Position:
    from random import randrange
    return Position(randrange(-20, 20, 1), randrange(-20, 20, 1), randrange(-20, 20, 1))


def test_node_is_subscribable(rand_pos):
    node = GenericNode(rand_pos)
