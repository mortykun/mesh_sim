from typing import Dict, Any

from lahja import BaseEvent


class GenericMessageEvent(BaseEvent):
    """
    Holder for generic message used by mesh nodes to communicate with each other
    Movements of this messages will be main interest of this project
    """
    meta: Dict
    origin_id = None
    last_send_from_ = None
    source = None
    target = None
    ttl = 3
    seq = 0

    def __init__(self, data, size=0, origin=None):
        super().__init__()
        self.data: Any = data
        self.size: int = size
        self.origin = origin

    def __str__(self):
        return f"{self.__class__.__name__}[d='{self.data}';origin={self.origin};seq={self.seq}]"

    def __eq__(self, other):
        return self.data == self.data and self.seq == self.seq

    def copy(self, new_message_type: type = None):
        if new_message_type is None:
            m = self.__class__(self.data, self.size, self.origin)
        else:
            m = new_message_type(self.data, self.size, self.origin)
        m.seq = self.seq
        return m


class GenericMessageOutgoingEvent(GenericMessageEvent):
    pass


