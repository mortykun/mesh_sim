import pytest
from rx.subject import Subject
from typing import Optional

from mesh.generic import GenericNode, GenericMessage
from mesh.node import NodeWithCache
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

    assert received_message.data == sent_message.data


def test_node_is_subscribable_via_network(rand_pos):
    sent_message = GenericMessage("some")
    received_message: GenericMessage = None

    def save_message(packet):
        nonlocal received_message
        received_message = packet

    node = GenericNode(rand_pos)
    node.subscribe(save_message)
    node.on_next(sent_message)
    assert received_message.data == sent_message.data


def test_message_origin_is_correct():
    test_message = GenericMessage("some")
    origin_node = GenericNode(Position(0, 0, 0))
    test_node = GenericNode(Position(1, 2, 3))

    received_message: Optional[GenericMessage] = None

    def save_message(packet):
        nonlocal received_message
        received_message = packet

    test_node.incoming_message_queue.subscribe(save_message)
    test_message.origin = origin_node
    test_node.on_next(test_message)
    assert received_message.origin == origin_node


def test_node_with_cache_can_receive_first_message():
    test_node = NodeWithCache(Position(0, 0, 0))
    dummy_node = GenericNode(Position(1, 1, 1))
    received_message = None

    def save_message(packet):
        nonlocal received_message
        received_message = packet

    test_node.subscribe(lambda m: print(f"FOOO:{m}"))
    test_node.subscribe(save_message)
    message = GenericMessage("data")
    message.origin = dummy_node
    test_node.on_next(message)
    assert received_message == message


def test_node_with_cache_will_drop_second_message():
    test_node = NodeWithCache(Position(0, 0, 0))
    received_message = None

    def save_message(packet):
        nonlocal received_message
        received_message = packet

    test_node.subscribe(save_message)
    message = GenericMessage("data")
    message.origin = test_node
    test_node.on_next(message)
    received_message = None
    test_node.on_next(message)
    assert received_message is None
