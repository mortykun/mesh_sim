"""
    This experiment will present flood of messages from one node to other node.
    All nodes will have possibility to pass messages of given id/source only once
    source will not change on each hop

"""
import random
import time
from multiprocessing import Manager

from mesh.network import Network
from mesh.network_monitor import get_messages_lines
from mesh.node_implementation import NodeWithPositionCache
from utils.space import Position
from view.plot import Plot

manager = Manager()
history = manager.list()
origin_node = NodeWithPositionCache(Position(0, 0, 0))
network = Network()

network.add_node(origin_node)
for i in range(1, 10):
    network.add_node(NodeWithPositionCache(Position(i, random.randint(1, 9), random.randint(1, 9))))

target_node = NodeWithPositionCache(Position(10, 10, 10))
network.add_node(target_node)
points = network.get_nodes_map()
network.start(history)
time.sleep(120)
network.stop()
print(history)

Plot.plot_points(*points)
Plot.plot_lines(get_messages_lines(history))
input("STOP")
