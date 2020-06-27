from typing import Callable

import pytest

from mesh.message import GenericMessageEvent
from mesh.node import MeshNode
from mesh.network_monitor import NetworkMonitor, NetworkAction
from mesh.network import Network
from utils.space import Position


@pytest.fixture
def network_monitor():
    return NetworkMonitor()


@pytest.fixture
def network():
    return Network()


def test_network_monitor_simple_callback(network_monitor: NetworkMonitor):
    network_monitor.save_action(
        GenericMessageEvent("Some message"),
        MeshNode(Position(1, 1, 1))
    )

    assert network_monitor[0]
    assert isinstance(network_monitor[0], NetworkAction)
    assert network_monitor[0].message.data == "Some message"


def test_network_history_is_saved_for_single_message(network_monitor: NetworkMonitor, network: Network):
    origin_node = MeshNode(Position(0, 0, 0))
    test_node = MeshNode(Position(1, 1, 1))
    test_node._send_messages = False

    network.add_node(origin_node)
    network.add_node(test_node)
    network.register_monitor(network_monitor)

    origin_node.send_to_network(GenericMessageEvent("message"))
    assert len(network_monitor) != 0
    assert network_monitor[0].message.data == "message"
    assert network_monitor[0]


def test_registration_of_monitor(network_monitor: NetworkMonitor, network: Network):
    network.register_monitor(network_monitor)
    assert len(network.monitors) != 0

    network.delete_monitor(network_monitor)
    assert len(network.monitors) == 0


