import asyncio
from abc import ABCMeta, abstractmethod
from multiprocessing import Value

from lahja import ConnectionConfig, AsyncioEndpoint, EndpointAPI

from mesh.common import BusConnected
from mesh.message import GenericMessageEvent, GenericMessageReceivedReport, GenericMessageOutgoingEvent
from utils.log import Loggable
from utils.space import Position


class MeshNodeAsync(BusConnected, Loggable, metaclass=ABCMeta):
    INSTANCE_COUNTER: int = 0
    INITIAL_ENDPOINT: ConnectionConfig = None

    def __init__(self, position: Position, rssi: int = -100, ):
        """
        :param position:
        :param rssi: ranging from -100 to -50 in bDm
        """
        super().__init__()

        self.network = None
        self.position = position
        self._id = self.__get_next_unique()
        self.bus_config = ConnectionConfig.from_name("network")

        self.kill_switch: Value = Value("i", 0)

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
    def handle_received_message(self, message: GenericMessageEvent) -> bool:
        """ Do something with received message """
        raise NotImplementedError

    @abstractmethod
    def main_message_tick(self) -> None:
        """ Main loop of the node operations """
        raise NotImplementedError

    async def run(self):
        async with AsyncioEndpoint(f"node_{self._id}").run() as self.network_bus:
            await self.connect_to_network()
            while not self.kill_switch.value:
                self.logger.debug(f"[{self}] Kill_switch state: {self.kill_switch.value}")
                await self.main_message_tick()
            self.logger.info(f"Node_{self._id} killed")
        self.network_bus = None

    async def emit_event_to_save(self, message: GenericMessageEvent):
        _message: GenericMessageReceivedReport = message.copy(new_message_type=GenericMessageReceivedReport)
        _message.target = self.position
        await self.network_bus.broadcast(_message)

    async def _handle_received_message(self, message: GenericMessageEvent):
        self.logger.debug(f"Node_{self._id} received: {message}")
        await self.emit_event_to_save(message)
        self.handle_received_message(message)

    async def connect_to_network(self):
        self.logger.info("Node started!")
        await self.network_bus.connect_to_endpoints(self.bus_config)
        self.logger.info("Node connected to network!")
        self.network_bus.subscribe(GenericMessageEvent, self._handle_received_message)
        self.logger.info("Node subscribed to network!")
        await self.network_bus.wait_until_any_endpoint_subscribed_to(GenericMessageOutgoingEvent)

    async def send_to_network(self, client: EndpointAPI, message: GenericMessageEvent):
        """ Send message to network """
        if not self.network:
            raise EnvironmentError(f"Network is not defined for node: {self}")
        message = self.set_origin_position(message)
        message = self.prepare_message_to_be_send(message)
        if self.can_send_message_to_network(message):
            self.logger.debug(f"Sending message [{message}] to Network")
            await client.broadcast(message)
        else:
            self.logger.debug(f" ...but sending is turned off")

    def set_origin_position(self, message: GenericMessageEvent):
        message.source = self.position
        message.target = None
        return message

    def start_single(self):
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(self.run())

    @classmethod
    def __get_next_unique(cls):
        """ Generate Unique ID to identify Node [to be treated as HW ID of physical node"""
        cls.INSTANCE_COUNTER += 1
        return cls.INSTANCE_COUNTER

    def __str__(self):
        return f"{self.__class__.__name__}:{self._id}_at:{self.position}"

    def __repr__(self):
        return self.__str__()

    def __hash__(self):
        return abs(hash(str(self)+str(id(self)))) % (10 ** 8)

    def __eq__(self, other):
        if hasattr(other, "id"):
            return self._id == other._id
        return False