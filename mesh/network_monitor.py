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
        out.append(Line(
            [entry.source.x, entry.target.x],
            [entry.source.y, entry.target.y],
            [entry.source.z, entry.target.z],
        ))
    return out


def dump_history(history: List[GenericMessageReceivedReport]):
    import csv
    with open('history.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([
            "Source_x",
            "Source_y",
            "Source_z",
            "target_x",
            "target_y",
            "target_z",
            "data"
        ])
        for entry in history:
            writer.writerow([
                entry.source.x,
                entry.source.y,
                entry.source.z,
                entry.target.x,
                entry.target.y,
                entry.target.z,
                entry.data
            ])
