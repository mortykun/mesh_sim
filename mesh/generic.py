import copy
import time
from typing import Dict, Union, Any

from rx import Observable
from rx.subject import Subject
from rx import operators as ops

from utils.log import Loggable
from utils.space import Position


class GenericMessage:
    """
    Holder for generic message used by mesh nodes to communicate with each other
    Movements of this messages will be main interest of this project
    """
    meta: Dict
    _origin = None
    seq = 0

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
        return f"{self.__class__.__name__}[d='{self.data}';origin={self.origin};seq={self.seq}]"

    def __eq__(self, other):
        return self.data == self.data and self.seq == self.seq


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

        self.network: Union[Subject, None] = None
        self.position = position
        self.rssi = rssi
        self.id = self.__get_next_serial()

        self.incoming_message_queue = Subject()
        self.outgoing_message_queue = self.setup_node_processing()
        self.outgoing_message_queue.subscribe(self.send_to_network, on_error=self.emmit_error)

        self.message_resend_gitter = 20

        self._send_messages = True
        self._seq = 1

    @property
    def next_seq(self):
        self._seq += 1
        return self._seq

    @classmethod
    def __get_next_serial(cls):
        """ Generate Unique ID to identify Node [to be treated as HW ID of physical node"""
        cls.INSTANCE_COUNTER += 1
        return cls.INSTANCE_COUNTER

    def setup_node_processing(self) -> Observable:
        """Simulation for processing incoming message before they are send back into associated network"""
        outgoing_message_queue = Subject()
        self.incoming_message_queue.pipe(
            ops.filter(self.resend_message_to_network),
            ops.map(self.prepare_message_to_be_send)
        ).subscribe(outgoing_message_queue.on_next)
        return outgoing_message_queue

    def resend_message_to_network(self, message: GenericMessage) -> bool:
        """Parse incoming message and check if should it be send further

        :param message: incoming message to be checked
        :return: If this message should be send to next node.
        """
        self.logger.debug(f"[{self}] Message received: {message}")
        if not self._send_messages:
            self.logger.info(f"[{self}] Message sending turned off for this node")
        else:
            time.sleep(self.message_resend_gitter/1000)
        return self._send_messages

    def prepare_message_to_be_send(self, message: GenericMessage) -> GenericMessage:
        new_message = copy.copy(message)
        new_message.origin = self
        if not new_message.seq:
            new_message.seq = self.next_seq
        return new_message

    def send_to_network(self, message: GenericMessage):
        """ Send message to network """
        if self.network:
            self.logger.warning(f"[{self}]Sending message [{message}] to Network")
            self.network.on_next(message)
        else:
            self.logger.warning(f"[{self}]Network is not defined for node: {self}")

    def on_next(self, message: GenericMessage):
        """Access point for messages incoming from network"""
        self.incoming_message_queue.on_next(message)

    def subscribe(self, *args, **kwargs):
        self.outgoing_message_queue.subscribe(*args, **kwargs)

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
        if hasattr(other, "id"):
            return self.id == other.id
        else:
            return False
