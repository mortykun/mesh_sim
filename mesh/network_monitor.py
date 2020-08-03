import logging
from time import time
from typing import List

from mesh.message import GenericMessageEvent, GenericMessageReceivedReport
from view.plot import Line


class NetworkAction:

    def __init__(self, action: GenericMessageReceivedReport):
        timestamp: int = int(time())
        action: GenericMessageEvent = action



def dump_history(history: List[GenericMessageReceivedReport]):
    import csv
    with open('history.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([
            "timestamp",
            "Source_x",
            "Source_y",
            "target_x",
            "target_y",
            "data"
        ])
        for entry in history:
            writer.writerow([
                entry.timestamp,
                entry.source_position.x,
                entry.source_position.y,
                entry.target_position.x,
                entry.target_position.y,
                entry.data
            ])
