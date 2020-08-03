"""
    This experiment will present flood of messages from one node to other node.
    All nodes will have possibility to pass messages of given id/source only once
    source will not change on each hop

"""
import logging
import random
import time
from datetime import datetime
from multiprocessing import Manager

from mesh.network import Network
from mesh.network_monitor import get_messages_lines, dump_history
from mesh.node_implementation import NodeWithPositionCache
from utils.space import Position
from view.plot import Plot

manager = Manager()
history = manager.list()
network = Network(30)

network.add_node(NodeWithPositionCache(Position(0, 0), addr=0, send_schedule=[(3, 100)]))
network.add_node(NodeWithPositionCache(Position(100, 100), addr=100))
# network.add_node(NodeWithPositionCache(Position(50, 50)))
seed = datetime.now()
random.seed(seed)
for i in range(1, 100):
    network.add_node(NodeWithPositionCache(Position(i, random.randint(1, 99))))

points = network.get_nodes_map()
network.start(history)
time.sleep(10)
network.stop()
# print(history)

Plot.plot_points(*points)
Plot.plot_lines(get_messages_lines(history))
dump_history(history)
logging.critical(f"SEED USED to generate network: `{seed}`")
input("STOP")
