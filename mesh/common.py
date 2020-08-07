from typing import Optional, List

from lahja import EndpointAPI

from mesh.message import GenericMessageReceivedReport


class BusConnected:
    _network_bus: Optional[EndpointAPI] = None

    @property
    def network_bus(self):
        if self._network_bus is not None:
            return self._network_bus
        else:
            raise AttributeError("Network endpoint is not connected")

    @network_bus.setter
    def network_bus(self, value: EndpointAPI):
        self._network_bus = value


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