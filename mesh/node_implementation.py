import asyncio
from collections import defaultdict
from random import random
from time import time

from mesh.message import GenericMessageEvent, GenericMessageOutgoingEvent
from mesh.node import MeshNodeAsync
from utils.space import Position


class MeshNode(MeshNodeAsync):
    """
    Representation of generic mesh message

    It posses 3-dimensional position and some interface for Messages to be send to and from Network
    self.message_queue is Observer and Observable
    """
    def __init__(self, position: Position):
        super().__init__(position)
        self.message_resend_gitter = 20
        self._seq = 1

        self._send_messages = True
        self.last_message_emitted = time()
        self.timeout = int(random() * 5) + 3

    @property
    def next_seq(self):
        self._seq += 1
        return self._seq

    async def main_message_tick(self):
        if time() - self.last_message_emitted > self.timeout:
            self.last_message_emitted = time()
            self.logger.info(f"Message is being send from node_{self._id}")
            await self.send_to_network(self.network_bus, GenericMessageOutgoingEvent(f"message#{self.next_seq}"))
        else:
            await asyncio.sleep(1)

    def prepare_message_to_be_send(self, message: GenericMessageEvent) -> GenericMessageEvent:
        return message

    def can_send_message_to_network(self, message):
        return self._send_messages

    def handle_received_message(self, message: GenericMessageEvent) -> None:
        pass


class NodeWithPositionCache(MeshNode):
    """
        Repeated messages from same source will be dropped by this Node
    """
    def __init__(self, position: Position):
        super().__init__(position)
        self._cache = defaultdict(list)

    @staticmethod
    def get_seq(message: GenericMessageEvent):
        return int(message.data.split("#")[-1])

    def should_read_message(self, message: GenericMessageEvent) -> bool:
        if not super().can_send_message_to_network(message):
            return False

        if message.source == self.position:
            return False

        self.logger.debug(f"[{self}] Message received: {message}")
        if message.source in self._cache:
            if self.get_seq(message) in self._cache[message.source]:
                self.logger.info(f"[{self}] RPL triggered - Message will be DROPPED: {message}")
                return False
        self._cache[message.source].append(self.get_seq(message))
        self.logger.info(f"[{self}]Message will be re-send: {message}")
        return True

