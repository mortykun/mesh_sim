import copy
from typing import Dict, Set, Union, Any

from rx import Observable
from rx.subject import Subject

from utils.log import Loggable
from utils.space import Position


class GenericMessage:
    meta: Dict
    _origin = None
    """
    Holder for generic message used by mesh nodes to communicate with each other
    Movements of this messages will be main interest of this project
    """

    def __init__(self, data, size=0, origin=None):
        self.data: Any = data
        self.size: int = size
        self.origin: GenericNode = origin

    @property
    def origin(self):
        return self._origin

    @origin.setter
    def origin(self, value):
        self._origin = value

    def __str__(self):
        return f"{self.__class__.__name__}[d='{self.data}';origin={self.origin}]"


class GenericNode(Loggable):
    """
    Representation of generic mesh message

    It posses 3-dimensional position and some interface for Messages to be send to and from Network
    self.message_queue is Observer and Observable
    """
    INSTANCE_COUNTER: int = 0

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
        self.id = self.__get_next_serial()

        self.incoming_message_queue = Subject()
        self.incoming_message_queue.subscribe(
            on_next=lambda m: self.logger.debug(f"[{self}] Message recived: {m}"))
        self.outgoing_message_queue = self.setup_node_processing()
        self.outgoing_message_queue.subscribe(self.send, on_error=self.emmit_error)

        self._send_messages = True

    @classmethod
    def __get_next_serial(cls):
        """ Generate Unique ID to identify Node [to be treated as HW ID of physical node"""
        cls.INSTANCE_COUNTER += 1
        return cls.INSTANCE_COUNTER

    def setup_node_processing(self) -> Observable:
        """Simulation for processing incoming message before they are send back into associated network"""
        return self.incoming_message_queue.pipe()

    def send(self, message: GenericMessage):
        """ Send message to network """
        new_message = copy.copy(message)
        if self._send_messages:
            new_message.origin = self
            if self.network:
                self.network.on_next(new_message)
            else:
                self.logger.warning(f"Network is not defined for node: {self}")
        else:
            self.logger.info("Message sending turned off for this node")

    def on_next(self, message: GenericMessage):
        """Access point for messages incoming from network"""
        self.incoming_message_queue.on_next(message)

    def subscribe(self, *args, **kwargs):
        self.incoming_message_queue.subscribe(*args, **kwargs)

    @staticmethod
    def emmit_error(err):
        print("Got error: %s" % err)

    def __str__(self):
        return f"{self.__class__.__name__}:{self.id}_at:{self.position}"

    def __repr__(self):
        return self.__str__()

    def __hash__(self):
        return abs(hash(str(self)+str(id(self)))) % (10 ** 8)

    def __eq__(self, other):
        return self.id == other.id


class Network(Loggable, Subject):
    """
    Holder for mesh network
    """

    def __init__(self):
        self.nodes: Set[GenericNode] = set()
        super().__init__()
        self.subscribe(self._packet_received_from_node)

    def on_next(self, value: GenericMessage) -> None:
        super(Network, self).on_next(value)

    def add_node(self, node: GenericNode) -> None:
        assert node not in self.nodes, "Node already added to Network"
        node.network = self
        self.nodes.add(node)

    def _packet_received_from_node(self, message: GenericMessage) -> None:
        self.logger.info(f"[{self}] Message received: {message}")
        for node in self.nodes:
            self.logger.debug(f"[{self}] Node : {node}")
            if node != message.origin:
                self.logger.debug(f"[{self}] Message is send to this node")
                node.on_next(message)
            else:

                self.logger.debug(f"[{self}] Message is NOT send to this node")

    def __str__(self):
        return f"{self.__class__.__name__}"
