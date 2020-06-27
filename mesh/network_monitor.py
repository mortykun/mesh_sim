from time import time
from typing import NamedTuple, List

from mesh.message import GenericMessageEvent
from mesh.node import MeshNode
from utils.space import Position
from view.plot import Line


class NetworkAction(NamedTuple):
    timestamp: int
    message: GenericMessageEvent
    origin: MeshNode
    destination: MeshNode


class NetworkMonitor:
    """
        Monitor network, store network messages history and present it in readable format

    """
    def __init__(self):
        self._history: List[NetworkAction] = []

    def save_action(self, action: GenericMessageEvent, destination: MeshNode):
        self._history.append(NetworkAction(int(time()), action, action.origin, destination))

    def __getitem__(self, item) -> NetworkAction:
        return self._history[item]

    def append(self, __object: NetworkAction):
        self._history.append(__object)

    def __len__(self):
        return len(self._history)

    def get_messages_lines(self):
        out = list()

        for entry in self._history:
            out.append(Line(
                [entry.message.origin.position.x, entry.destination.position.x],
                [entry.message.origin.position.y, entry.destination.position.y],
                [entry.message.origin.position.z, entry.destination.position.z],
            ))
        return out
