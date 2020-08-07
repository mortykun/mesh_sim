"""
    This experiment will present flood of messages from one node to other node.
    All nodes will have possibility to pass messages of given id/source only once
    source will not change on each hop

"""
import logging
import random
from datetime import datetime

from mesh.network import Network
from mesh.common import dump_history
from mesh.node.base import MeshNodeAsync
from mesh.node.with_cache import NodeWithPositionCache
from utils.space import Position
from view.plot import Plot, MeshPlotMode


RANGE = 15
NODE_COUNT = 25
SIMULATION_TIME = 20
MeshNodeAsync.ADDR_MAX = NODE_COUNT+1
SEND_SCHEDULE = [(3, NODE_COUNT), (10, NODE_COUNT), (10, NODE_COUNT)]
SEED = datetime.now()

network = Network(RANGE)
network.add_node(NodeWithPositionCache(Position(0, 0), addr=0, send_schedule=SEND_SCHEDULE))
network.add_node(NodeWithPositionCache(Position(NODE_COUNT, NODE_COUNT), addr=NODE_COUNT))
random.seed(SEED)
for i in range(1, NODE_COUNT):
    network.add_node(NodeWithPositionCache(Position(i, random.randint(1, NODE_COUNT-1))))

network.run_for(SIMULATION_TIME)


plot = Plot(2, 2)
plot.draw((0, 0), MeshPlotMode.ONLY_FIRST, network)
plot.draw((0, 1), MeshPlotMode.ALL_MESSAGES, network)
plot.draw((1, 0), MeshPlotMode.BAR_RECEIVED, network)

dump_history(network.network_history)
logging.critical(f"SEED USED to generate network: `{SEED}`")
input("STOP")
