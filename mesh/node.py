import asyncio
from collections import defaultdict
from multiprocessing import Value
from random import random
from time import time

from lahja import ConnectionConfig, AsyncioEndpoint, EndpointAPI

from mesh.message import GenericMessageEvent, GenericMessageOutgoingEvent
from utils.log import Loggable
from utils.space import Position


class MeshNode(Loggable):
    """
    Representation of generic mesh message

    It posses 3-dimensional position and some interface for Messages to be send to and from Network
    self.message_queue is Observer and Observable
    """
    INSTANCE_COUNTER: int = 0
    INITIAL_ENDPOINT: ConnectionConfig = None

    def __init__(self, position: Position, rssi: int = -100, ):
        """
        :param position:
        :param rssi: ranging from -100 to -50 in bDm
        """
        super(MeshNode, self).__init__()
        assert -100 <= rssi <= -50, f"rssi should be in [-100, -50 ] range, but {rssi=} given"

        self.network = None
        self.position = position
        self.rssi = rssi
        self.address = self.__get_next_unique()

        self.message_resend_gitter = 20

        self._send_messages = True
        self._seq = 1

        self.bus_config = ConnectionConfig.from_name("network")
        self.kill_switch: Value[int] = Value("i", 0)

    @property
    def next_seq(self):
        self._seq += 1
        return self._seq

    @classmethod
    def __get_next_unique(cls):
        """ Generate Unique ID to identify Node [to be treated as HW ID of physical node"""
        cls.INSTANCE_COUNTER += 1
        return cls.INSTANCE_COUNTER

    async def run(self):
        async with AsyncioEndpoint(f"node_{self.address}").run() as client:
            await self.connect_to_network(client)

            while not self.kill_switch.value:
                self.logger.critical(f"[{self}] Kill_switch state: {self.kill_switch.value}")
                await self.main_message_tick(client)
            self.logger.info(f"Node_{self.address} killed")

    async def main_message_tick(self, client):
        timeout = int(random() * 20)
        last_message_emited = time()
        while time() - last_message_emited < timeout:
            await asyncio.sleep(0.1)
        self.logger.info(f"Message is being send from node_{self.address}")
        await self.send_to_network(client, GenericMessageOutgoingEvent("message#"))

    async def connect_to_network(self, client):
        self.logger.info("Node started!")
        await client.connect_to_endpoints(self.bus_config)
        self.logger.info("Node connected to network!")
        client.subscribe(GenericMessageEvent, self.handle_received_message)
        self.logger.info("Node subscribed to network!")
        await client.wait_until_any_endpoint_subscribed_to(GenericMessageOutgoingEvent)

    def handle_received_message(self, message: GenericMessageEvent):
        self.logger.info(f"Node_{self.address} received: {message}")
        if self.network:
            if self.network.monitors:
                for m in self.network.monitors:
                    m.save_action(message, self)

    def prepare_message_to_be_send(self, message: GenericMessageEvent) -> GenericMessageEvent:
        message.origin = self.address
        message.ttl -= 1
        if not message.seq:
            message.seq = self.next_seq
        return message

    def can_send_message_to_network(self, message):
        return message.ttl >= 2

    async def send_to_network(self, client: EndpointAPI, message: GenericMessageEvent):
        """ Send message to network """
        if not self.network:
            raise EnvironmentError(f"[{self}]Network is not defined for node: {self}")
        message = self.prepare_message_to_be_send(message)
        if self.can_send_message_to_network(message):
            self.logger.warning(f"[{self}]Sending message [{message}] to Network")
            await client.broadcast(message)

    def start_single(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.run())

    def __str__(self):
        return f"{self.__class__.__name__}:{self.address}_at:{self.position}"

    def __repr__(self):
        return self.__str__()

    def __hash__(self):
        return abs(hash(str(self)+str(id(self)))) % (10 ** 8)

    def __eq__(self, other):
        if hasattr(other, "id"):
            return self.address == other.address
        return False


class NodeWithCache(MeshNode):
    """
        Repeated messages from same source will be dropped by this Node
    """
    def __init__(self, position: Position):
        super().__init__(position)
        self._cache = defaultdict(list)

    def can_send_message_to_network(self, message: GenericMessageEvent) -> bool:
        if not super(NodeWithCache, self).can_send_message_to_network(message):
            return False

        if message.origin == self:
            return False
        self.logger.debug(f"[{self}] Message received: {message}")
        if message.origin in self._cache:
            if message.seq in self._cache[message.origin]:
                self.logger.info(f"[{self}] RPL triggered - Message will be DROPPED: {message}")
                return False
        self._cache[message.origin].append(message.seq)
        self.logger.info(f"[{self}]Message will be re-send: {message}")
        return True

