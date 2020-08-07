import asyncio
from collections import defaultdict
from time import time
from typing import List, Tuple, Optional

from mesh.message import GenericMessageEvent, GenericMessageOutgoingEvent, NetworkPDU
from mesh.node.base import MeshNodeAsync
from utils.space import Position


class NodeWithPositionCache(MeshNodeAsync):
    """
        Repeated messages from same source will be dropped by this Node
    """
    INIT_TTL = 14

    def __init__(self, position: Position, addr=None,  send_schedule: List[Tuple[float, int]] = None):
        """
        :param position:
        :param addr: requested address for the node
        :param send_schedule: list of tuples (time of message send, requested target)
        """
        super().__init__(position, addr)
        self.send_schedule = [] if send_schedule is None else send_schedule
        self.next_message: Optional[Tuple[float, int]] = None
        self._seq: int = 1
        self._cache = defaultdict(list)

    @property
    def next_seq(self):
        self._seq += 1
        return self._seq

    async def handle_received_message(self, message: GenericMessageEvent) -> None:
        if message.data.ttl >= 2:
            out = message.copy(GenericMessageOutgoingEvent)
            await self.send_to_network(self.network_bus, out)

    def should_process_message(self, message: GenericMessageEvent) -> bool:
        if message.data.src == self.addr:
            return False
        self.logger.debug(f"[{self}] Message received: {message}")
        if message.data.src in self._cache:
            if message.data.seq in self._cache[message.data.src]:
                self.logger.debug(f"[{self}] RPL triggered - Message will be DROPPED: {message}")
                return False
        self._cache[message.data.src].append(message.data.seq)
        self.logger.info(f"[{self}]Message will be processed: {message}")
        return True

    def can_send_message_to_network(self, message: GenericMessageEvent) -> bool:
        return True

    def prepare_message_to_be_send(self, message: GenericMessageEvent) -> GenericMessageEvent:
        return message

    def generate_new_message(self, transport_pdu=None) -> NetworkPDU:
        net_pdu = NetworkPDU()
        net_pdu.src = self.addr
        net_pdu.seq = self.next_seq
        net_pdu.ttl = self.INIT_TTL
        net_pdu.transport_pdu = transport_pdu
        return net_pdu

    async def main_message_tick(self):
        if self.next_message is None:
            try:
                self.next_message = self.send_schedule.pop()
            except IndexError:
                self.next_message = float("inf"), None

        if time() - self.start_time >= self.next_message[0]:
            net_pdu = self.generate_new_message()
            if self.next_message[1] is None:
                raise ValueError(f"Target of the message cannot be `None`")
            net_pdu.dest = self.next_message[1]
            self.logger.debug(f"Message is being send from {self.addr} to {net_pdu.dest}")

            out = GenericMessageOutgoingEvent(net_pdu)
            await self.send_to_network(self.network_bus, out)
            self.next_message = None
        await asyncio.sleep(0)
