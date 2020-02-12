from typing import Dict, Set, Union

from rx import Observable
from rx.subject import Subject

from utils.log import Loggable
from utils.space import Position


class GenericMessage:
    meta: Dict
    """
    Holder for generic message used by mesh nodes to communicate with each other
    Movements of this messages will be main interest of this project
    """

    def __init__(self, data, size=0, origin=None):
        self.data = data
        self.size = size
        self.origin = origin


class GenericNode(Loggable):
    """
    Representation of generic mesh message

    It posses 3-dimensional position and some interface for Messages to be send to and from Network
    self.message_queue is Observer and Observable
    """

    def __init__(self, position: Position, rssi: int = -100, ):
        """
        :param position:
        :param rssi: ranging from -100 to -50 in bDm
        """
        super(GenericNode, self).__init__()
        assert -100 <= rssi <= -50, f"rssi should be in [-100, -50 ] range, but {rssi=} given"

        self.network: Union[Network, None] = None
        self.position = position
        self.rssi = rssi

        self.incoming_message_queue = Subject()
        self.outgoing_message_queue = self.setup_node_processing()
        self.outgoing_message_queue.subscribe(self.send, on_error=self.emmit_error)

    def setup_node_processing(self) -> Observable:
        """Simulation for processing incoming message before they are send back into associated network"""
        return self.incoming_message_queue.pipe()

    def send(self, message: GenericMessage):
        """ Send message to network """
        message.origin = self.position
        if self.network:
            self.network.on_next(message)
        else:
            self.logger.warn(f"Network is not defined for node: {self}")

    def on_next(self, message: GenericMessage):
        """Access point for messages incoming from network"""
        self.incoming_message_queue.on_next(message)

    def subscribe(self, *args, **kwargs):
        self.incoming_message_queue.subscribe(*args, **kwargs)

    @staticmethod
    def emmit_error(err):
        print("Got error: %s" % err)


class Network(Subject):
    """
    Holder for mesh network
    """

    def __init__(self):
        self.nodes: Set[GenericNode] = set()
        super(Network, self).__init__()
        self.subscribe(self._packet_received_from_node)

    def on_next(self, value: GenericMessage) -> None:
        super(Network, self).on_next(value)

    def add_node(self, node: GenericNode) -> None:
        assert node not in self.nodes, "Node already added to Network"
        node.network = self
        self.nodes.add(node)

    def _packet_received_from_node(self, message: GenericMessage) -> None:
        pass
