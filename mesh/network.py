from typing import Set, List

from rx.subject import Subject

from mesh.generic import GenericNode, GenericMessage
from mesh.network_monitor import NetworkMonitor
from utils.log import Loggable


class Network(Loggable, Subject):
    """
    Holder for mesh network
    """

    def __init__(self):
        self.monitors: List[NetworkMonitor] = []
        self.nodes: Set[GenericNode] = set()
        super().__init__()
        self.subscribe(self._packet_received_from_node)

    def on_next(self, value: GenericMessage) -> None:
        super(Network, self).on_next(value)

    def add_node(self, node: GenericNode) -> None:
        assert node not in self.nodes, f"[{self}] Node already added to Network"
        node.network = self
        self.nodes.add(node)

    def _packet_received_from_node(self, message: GenericMessage) -> None:
        for node in self.nodes:
            self.logger.debug(f"[{self}] Message received: {message}")
            if node != message.origin:
                self.send_message_to_node(node, message)
            else:

                self.logger.debug(f"[{self}] Message is NOT send to {node}")

    def send_message_to_node(self, target_node: GenericNode, message: GenericMessage):
        self.logger.debug(f"[{self}] Message is send to {target_node}")
        for m in self.monitors:
            m.save_action(message, target_node)
            print(m._history)
        target_node.on_next(message)

    def __str__(self):
        return f"{self.__class__.__name__}"

    def register_monitor(self, network_monitor: NetworkMonitor):
        self.monitors.append(network_monitor)

    def delete_monitor(self, network_monitor):
        self.monitors.remove(network_monitor)

