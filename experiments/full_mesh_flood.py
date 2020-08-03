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
from mesh.network_monitor import dump_history
from mesh.node_implementation import NodeWithPositionCache
from utils.space import Position
from view.plot import Plot, MeshPlotMode

manager = Manager()
history = manager.list()
network = Network(30)

network.add_node(NodeWithPositionCache(Position(0, 0), addr=0, send_schedule=[(3, 100)]))
network.add_node(NodeWithPositionCache(Position(100, 100), addr=100))
seed = datetime.now()
# seed = 10
random.seed(seed)
for i in range(1, 50):
    network.add_node(NodeWithPositionCache(Position(i * 2, random.randint(1, 99))))

network.start(history)
time.sleep(10)
network.stop()

plot = Plot(2, 2)
plot.draw((0, 0), MeshPlotMode.ONLY_FIRST, network, history)
plot.draw((0, 1), MeshPlotMode.ALL_MESSAGES, network, history)

dump_history(history)
logging.critical(f"SEED USED to generate network: `{seed}`")
input("STOP")
