"""
    This experiment will present flood of messages from one node to other node.
    All nodes will have possibility to pass messages of given id/source only once
    source will not change on each hop

"""
import random

from mesh.generic import GenericNode, GenericMessage
from mesh.network import Network
from mesh.network_monitor import NetworkMonitor
from mesh.node import NodeWithCache
from utils.space import Position
from view.plot import Plot

origin_node = NodeWithCache(Position(0, 0, 0))
network = Network()
monitor = NetworkMonitor()
network.register_monitor(monitor)

network.add_node(origin_node)
for i in range(1, 10):
    network.add_node(NodeWithCache(Position(i, random.randint(1, 99), random.randint(1, 99))))

target_node = NodeWithCache(Position(100, 100, 100))
network.add_node(target_node)

origin_node.on_next(GenericMessage("dummy"))
points = network.get_nodes_map()
Plot.plot_points(*points)
lines = monitor.get_messages_lines()
Plot.plot_lines(lines)
