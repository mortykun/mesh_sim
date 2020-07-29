import logging
from time import time
from typing import List

from mesh.message import GenericMessageEvent, GenericMessageReceivedReport
from view.plot import Line


class NetworkAction:

    def __init__(self, action: GenericMessageReceivedReport):
        timestamp: int = int(time())
        action: GenericMessageEvent = action


def get_messages_lines(history: List[GenericMessageReceivedReport]):
    out = list()
    for entry in history:
        print(entry)
        out.append(Line(
            [entry.source.x, entry.target.x],
            [entry.source.y, entry.target.y],
            [entry.source.z, entry.target.z],
        ))
    return out
