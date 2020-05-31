import pytest
from rx.subject import Subject

from mesh.generic import GenericNode, GenericMessage
from utils.space import Position


@pytest.fixture
def rand_pos() -> Position:
    from random import randrange
    return Position(randrange(-20, 20, 1), randrange(-20, 20, 1), randrange(-20, 20, 1))


def test_node_is_subscribable(rand_pos):
    sent_message = GenericMessage("food")
    received_message = None

    def save_message(packet):
        nonlocal received_message
        received_message = packet

    network = Subject()
    node = GenericNode(rand_pos)
    node.network = network

    network.subscribe(save_message)
    node.on_next(sent_message)  # node will send message back to network

    assert received_message == sent_message


def test_node_is_subscribable_via_network(rand_pos):
    sent_message = GenericMessage("some")
    received_message = None

    def save_message(packet):
        nonlocal received_message
        received_message = packet

    node = GenericNode(rand_pos)
    node.subscribe(save_message)
    node.on_next(sent_message)
    assert received_message == sent_message
