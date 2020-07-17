"""
    This experiment will present flood of messages from one node to other node.
    All nodes will have possibility to pass messages of given id/source only once
    source will not change on each hop

"""
import random
import time

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
    network.add_node(NodeWithCache(Position(i, random.randint(1, 9), random.randint(1, 9))))

target_node = NodeWithCache(Position(10, 10, 10))
network.add_node(target_node)
points = network.get_nodes_map()

network.start()
time.sleep(10)
network.stop()
Plot.plot_points(*points)
lines = monitor.get_messages_lines()
Plot.plot_lines(lines)
input("Finished!")
