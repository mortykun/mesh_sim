import pytest

from mesh.generic import GenericNode, Network, GenericMessage
from utils.space import Position


@pytest.fixture
def rand_pos() -> Position:
    from random import randrange
    return Position(randrange(-20, 20, 1), randrange(-20, 20, 1), randrange(-20, 20, 1))


@pytest.fixture
def network():
    from mesh.generic import Network
    return Network()


def test_network_is_created_with_one_node(network: Network, rand_pos: Position):
    node = GenericNode(rand_pos)
    network.add_node(node)
    assert node in network.nodes
    assert network.nodes


def test_network_will_register_node_on_same_position(network: Network, rand_pos: Position):
    node1 = GenericNode(rand_pos)
    node2 = GenericNode(rand_pos)
    network.add_node(node1)
    network.add_node(node2)
    assert len(network.nodes) == 2


def test_network_is_subscribable(network: Network, rand_pos: Position):
    received_message = None
    expected_message = GenericMessage("Some message", origin=rand_pos)

    def on_message_received(_message):
        nonlocal received_message
        received_message = _message

    network.subscribe(on_message_received)
    network.on_next(expected_message)
    assert expected_message == received_message
