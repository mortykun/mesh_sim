import asyncio
import multiprocessing
from multiprocessing.context import Process
from typing import Set, List

from lahja import AsyncioEndpoint, ConnectionConfig

from mesh.message import GenericMessageEvent, GenericMessageOutgoingEvent
from mesh.node import MeshNode
from mesh.network_monitor import NetworkMonitor
from utils.log import Loggable


class Network(Loggable):
    """
    Holder for mesh network
    """

    def __init__(self):
        self.monitors: List[NetworkMonitor] = []
        self.nodes: Set[MeshNode] = set()
        self.processes: List[Process] = []

        self.kill_switch: bool = False
        super().__init__()

    def add_node(self, node: MeshNode) -> None:
        assert node not in self.nodes, f"[{self}] Node already added to Network"
        node.network = self
        self.nodes.add(node)

    async def run_network(self):
        async with AsyncioEndpoint.serve(ConnectionConfig.from_name("network")) as server:
            self.logger.info("Network started")
            server.subscribe(GenericMessageOutgoingEvent, lambda event: self.send_to_all_nodes(server, event))
            self.logger.info("Network subscribed to all messages")
            while not self.kill_switch:
                await asyncio.sleep(0)
            self.logger.info("Network turned off")

    def send_to_all_nodes(self, active_endpoint: AsyncioEndpoint, message: GenericMessageEvent):
        self.logger.info(f"{message.origin}")
        self.logger.info(f"Network received : {message}")

        active_endpoint.broadcast_nowait(message.copy(new_message_type=GenericMessageEvent))

    def start_bare_network(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.run_network())

    def __str__(self):
        return f"{self.__class__.__name__}"

    def register_monitor(self, network_monitor: NetworkMonitor):
        self.monitors.append(network_monitor)
        # FixMe - add network monitor observer for all events :3

    def delete_monitor(self, network_monitor):
        self.monitors.remove(network_monitor)

    def get_nodes_map(self):
        x = []
        y = []
        z = []
        for n in self.nodes:
            x.append(n.position.x)
            y.append(n.position.y)
            z.append(n.position.z)
        return x, y, z

    def start(self):
        # multiprocessing.set_start_method("spawn")
        p_net = multiprocessing.Process(target=self.start_bare_network)
        self.processes.append(p_net)

        for node in self.nodes:
            _p_node = multiprocessing.Process(target=node.start_single)
            self.processes.append(_p_node)

        for p in self.processes:
            p.start()

    def stop(self):
        self.kill_switch = True
        for n in self.nodes:
            n.kill_switch = True

