from typing import Dict

from utils.space import Position


class GenericMessage:
    meta: Dict
    """
    Holder for generic message used by mesh nodes to communicate with each other
    Movements of this messages will be main interest of this project
    """

    def __init__(self, data, size):
        self.data = data
        self.size = size


class GenericNode:
    """
    Representation of generic mesh mesh

    It posses 3-dimensional position and some interface for Messages to be send to and from Network
    """

    def __init__(self, position: Position, rssi: int = -100):
        """
        :param position:
        :param rssi: ranging from -100 to -50 in bDm
        """
        assert -100 <= rssi <= -50, f"rssi should be in [-100, -50 ] range, but {rssi=} given"

        self.position = position
        self.rssi = rssi

    def send(self, message: GenericMessage):
        raise NotImplementedError()

    def receive(self, message: GenericMessage):
        raise NotImplementedError()

    def __hash__(self):
        return hash(self.position)
