import asyncio
import multiprocessing
from multiprocessing.context import Process
from typing import Set, List

from lahja import AsyncioEndpoint, ConnectionConfig

from mesh.common import BusConnected
from mesh.message import GenericMessageEvent, GenericMessageOutgoingEvent, GenericMessageReceivedReport
from mesh.node import MeshNodeAsync
from utils.log import Loggable
from utils.space import Position


class Network(BusConnected, Loggable):
    """
    Holder for mesh network
    """

    def __init__(self, node_range):
        self.nodes: Set[MeshNodeAsync] = set()
        self.processes: List[Process] = []

        self.kill_switch: multiprocessing.Value[int] = multiprocessing.Value("i", 0)
        self.network_process = None
        self.range = node_range
        super().__init__()

    def add_node(self, node: MeshNodeAsync) -> None:
        assert node not in self.nodes, f"[{self}] Node already added to Network"
        node.network = self
        self.nodes.add(node)

    async def run_network(self, network_history):
        async with AsyncioEndpoint.serve(ConnectionConfig.from_name("network")) as self.network_bus:
            self.logger.info("Network started")
            self.network_bus.subscribe(GenericMessageOutgoingEvent, self.send_to_all_nodes)
            self.network_bus.subscribe(GenericMessageReceivedReport, self.notify_monitor(network_history))
            self.logger.info("Network subscribed to all messages")
            while not self.kill_switch.value:
                await asyncio.sleep(0)
            self.logger.info("Network turned off")

    async def send_to_all_nodes(self, message: GenericMessageEvent):
        self.logger.info(f"Network received : {message}")
        await self.network_bus.broadcast(message.copy(new_message_type=GenericMessageEvent))

    def start_bare_network(self, network_history):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.run_network(network_history=network_history))

    def __str__(self):
        return f"{self.__class__.__name__}"

    @staticmethod
    def notify_monitor(history_handler: List):
        def _notify(message: GenericMessageReceivedReport):
            history_handler.append(message)
        return _notify

    def did_i_hear_this_message(self, origin_node: Position, destination_node: Position) -> bool:
        """
        :param origin_node: ADDR of node that 'physically' send message
        :param destination_node: ADDR of node that 'physically' recived message
        :return:
        """
        is_reachable = abs(origin_node - destination_node) < self.range
        self.logger.debug(f"Message reached ? [{is_reachable}]")
        return is_reachable

    def get_nodes_map(self):
        x = []
        y = []
        for n in self.nodes:
            x.append(n.position.x)
            y.append(n.position.y)
        return x, y

    def start(self, network_history):
        p_net = multiprocessing.Process(target=self.start_bare_network, args=(network_history,))
        p_net.daemon = False
        self.network_process = p_net

        for node in self.nodes:
            _p_node = multiprocessing.Process(target=node.start_single)
            self.processes.append(_p_node)

        self.network_process.start()
        for p in self.processes:
            p.start()

    def stop(self):
        for n in self.nodes:
            n.kill_switch.value = 1
        for p in self.processes:
            p.join()

        self.kill_switch.value = 1
        self.network_process.join()
