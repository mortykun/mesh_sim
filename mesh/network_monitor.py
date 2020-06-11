from time import time
from typing import NamedTuple, List

from mesh.generic import GenericMessage, GenericNode
from utils.space import Position


class NetworkAction(NamedTuple):
    timestamp: int
    message: GenericMessage
    destination: GenericNode


class NetworkMonitor:
    """
        Monitor network, store network messages history and present it in readable format

    """
    def __init__(self):
        self._history: List[NetworkAction] = []

    def save_action(self, action: GenericMessage, destination: GenericNode):
        self._history.append(NetworkAction(int(time()), action, destination))

    def __getitem__(self, item) -> NetworkAction:
        return self._history[item]

    def append(self, __object: NetworkAction):
        self._history.append(__object)

    def __len__(self):
        return len(self._history)
