from typing import Optional

from lahja import EndpointAPI


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
