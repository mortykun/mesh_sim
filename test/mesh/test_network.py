import pytest
from hamcrest import assert_that, has_length

from mesh.generic import GenericNode
from utils.space import Position


@pytest.fixture
def network():
    from mesh.network import Network
    return Network()


def test_network_is_created_with_one_node(network):
    node = GenericNode(Position(1, 0, 2))
    network.add_node(node)
    assert node in network.nodes


def test_network_will_register_node_on_same_position(network):
    node1 = GenericNode(Position(1, 0, 2))
    node2 = GenericNode(Position(1, 0, 2))
    network.add_node(node1)
    network.add_node(node2)
    assert_that(network.nodes, has_length(2))
