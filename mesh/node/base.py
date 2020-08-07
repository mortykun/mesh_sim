import asyncio
import time
from abc import ABCMeta, abstractmethod
from multiprocessing import Value
from typing import Set, Optional, Dict, List

from lahja import ConnectionConfig, AsyncioEndpoint, EndpointAPI

from mesh.common import BusConnected
from mesh.message import GenericMessageEvent, GenericMessageReceivedReport, GenericMessageOutgoingEvent
from utils.log import Loggable
from utils.space import Position


class MeshNodeAsync(BusConnected, Loggable, metaclass=ABCMeta):
    ASSIGNED_ADDRESSES: Set[int] = set()
    INITIAL_ENDPOINT: ConnectionConfig = None
    ADDR_MIN = 0
    ADDR_MAX = 1000

    nodes_history: Dict[int, List[GenericMessageEvent]]

    def __init__(self, position: Position, addr=None):
        """
        :param position:
        :param addr: requested address for the node
        """
        super().__init__()

        self.start_time = 0
        self.network = None
        self.position = position
        self.addr = self._get_free_address(addr)
        self.bus_config = ConnectionConfig.from_name("network")

        self.kill_switch: Value = Value("i", 0)
        self.nodes_history = {}

    @abstractmethod
    def prepare_message_to_be_send(self, message: GenericMessageEvent) -> GenericMessageEvent:
        """
        Modify message before it is resend to next node
        """
        raise NotImplementedError

    @abstractmethod
    def can_send_message_to_network(self, message: GenericMessageEvent) -> bool:
        """
        Check if message should be re-send to network
        """
        raise NotImplementedError

    @abstractmethod
    async def handle_received_message(self, message: GenericMessageEvent) -> bool:
        """ Do something with received message """
        raise NotImplementedError

    @abstractmethod
    async def main_message_tick(self) -> None:
        """ Main loop of the node operations """
        raise NotImplementedError

    @abstractmethod
    def should_process_message(self, message) -> bool:
        """ Check message if it should be processed or dropped"""
        raise NotImplementedError

    async def run(self, nodes_history):
        self.nodes_history = nodes_history
        self.nodes_history[self.addr] = []
        async with AsyncioEndpoint(f"node_{self.addr}").run() as self.network_bus:
            await self.connect_to_network()
            self.start_time = time.time()
            while not self.kill_switch.value:
                # self.logger.debug(f"[{self}] Kill_switch state: {self.kill_switch.value}")
                await self.main_message_tick()
            self.logger.info(f"Node_{self.addr} killed")
        self.network_bus = None

    async def save_event(self, message: GenericMessageEvent, accepted: bool):
        _message: GenericMessageReceivedReport = message.copy(new_message_type=GenericMessageReceivedReport)
        _message.target_position = self.position
        _message.accepted = accepted
        _message.timestamp = time.time()
        _message.reporter = self.addr
        self.logger.debug(f" Node_{self.addr} is saving event to node history: {_message}")
        node_history = list(self.nodes_history[self.addr])
        node_history.append(_message)
        self.nodes_history[self.addr] = node_history

    async def _handle_received_message(self, message: GenericMessageEvent):
        if self.network.did_i_hear_this_message(message.source_position, self.position):
            message = self.preprocess_received_message(message)
            message_accepted = self.should_process_message(message)
            self.logger.debug(f"Node_{self.addr} received: {message}, "
                              f"{'was accepted' if message_accepted else 'DROPPED'}")
            await self.save_event(message, message_accepted)
            if message_accepted:
                await self.handle_received_message(message)

    async def connect_to_network(self):
        await self.network_bus.connect_to_endpoints(self.bus_config)
        self.network_bus.subscribe(GenericMessageEvent, self._handle_received_message)
        await self.network_bus.wait_until_any_endpoint_subscribed_to(GenericMessageOutgoingEvent)
        self.logger.info(f"Node_{self.addr} connected to network!")

    async def send_to_network(self, client: EndpointAPI, message: GenericMessageOutgoingEvent):
        """ Send message to network """

        assert message is not None
        if not self.network:
            raise EnvironmentError(f"Network is not defined for node: {self}")
        message = self.set_phy_origin_position(message)
        message = self.prepare_message_to_be_send(message)
        if self.can_send_message_to_network(message):
            self.logger.debug(f"Sending message [{message}] to Network")
            await client.broadcast(message)
        else:
            self.logger.debug(f" ...but sending is turned off")

    def set_phy_origin_position(self, message: GenericMessageEvent):
        message.source_position = self.position
        message.target_position = None
        return message

    @staticmethod
    def preprocess_received_message(message: GenericMessageEvent) -> GenericMessageEvent:
        message.data.ttl -= 1
        return message

    def start_single(self, nodes_history):
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(self.run(nodes_history=nodes_history))

    @classmethod
    def _get_free_address(cls, requested_addr: Optional[int] = None):
        """ Generate Unique ID to identify Node [to be treated as Node network address]"""
        if isinstance(requested_addr, int):
            if requested_addr < cls.ADDR_MIN or requested_addr > cls.ADDR_MAX:
                raise ValueError(f"{requested_addr} not in allowed range <{cls.ADDR_MIN};{cls.ADDR_MAX}>")
            if requested_addr in cls.ASSIGNED_ADDRESSES:
                raise ValueError(f"Requested address {requested_addr} already present in the network")
            chosen_address = requested_addr
        elif requested_addr is None:
            available_address = set(range(cls.ADDR_MIN, cls.ADDR_MAX+1)) - cls.ASSIGNED_ADDRESSES
            chosen_address = min(available_address)
        else:
            raise TypeError(f"Requested address of invalid type: {type(requested_addr)}")

        cls.ASSIGNED_ADDRESSES.add(chosen_address)
        return chosen_address

    def __str__(self):
        return f"{self.__class__.__name__}:{self.addr}_at:{self.position}"

    def __repr__(self):
        return self.__str__()

    def __hash__(self):
        return abs(hash(str(self)+str(id(self)))) % (10 ** 8)

    def __eq__(self, other):
        if hasattr(other, "id"):
            return self.addr == other.addr
        return False


