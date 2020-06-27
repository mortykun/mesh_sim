from typing import Optional

import pytest

from mesh.message import GenericMessageEvent
from mesh.node import MeshNode
from mesh.network import Network
from utils.space import Position


@pytest.fixture
def rand_pos() -> Position:
    from random import randrange
    return Position(randrange(-20, 20, 1), randrange(-20, 20, 1), randrange(-20, 20, 1))


@pytest.fixture
def network():
    from mesh.network import Network
    return Network()


def test_network_is_created_with_one_node(network: Network, rand_pos: Position):
    node = MeshNode(rand_pos)
    network.add_node(node)
    assert node in network.nodes
    assert network.nodes


def test_network_will_register_node_on_same_position(network: Network, rand_pos: Position):
    node1 = MeshNode(rand_pos)
    node2 = MeshNode(rand_pos)
    network.add_node(node1)
    network.add_node(node2)
    assert len(network.nodes) == 2


def test_network_is_subscribable(network: Network, rand_pos: Position):
    received_message = None
    expected_message = GenericMessageEvent("Some message", origin=rand_pos)

    def on_message_received(_message):
        nonlocal received_message
        received_message = _message

    network.subscribe(on_message_received)
    network.on_next(expected_message)
    assert expected_message == received_message


def test_network_will_pass_message_to_another_node(network: Network):
    origin_node = MeshNode(Position(0, 0, 0))
    test_node = MeshNode(Position(3, 2, 1))
    test_node._send_messages = False
    network.add_node(origin_node)
    network.add_node(test_node)
    received_message: Optional[GenericMessageEvent] = None

    def on_message_received(_message):
        nonlocal received_message
        received_message = _message

    test_node.incoming_message_queue.subscribe(on_next=on_message_received)
    origin_node.send_to_network(GenericMessageEvent(data="test_data"))

    assert received_message
    assert received_message.data == "test_data"
