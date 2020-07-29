from typing import Dict, Any

from lahja import BaseEvent


class GenericMessageEvent(BaseEvent):
    """
    Holder for generic message used by mesh nodes to communicate with each other
    Movements of this messages will be main interest of this project
    """

    source = None
    target = None

    def __init__(self, data):
        super().__init__()
        self.data: Any = data

    def __str__(self):
        return f"{self.__class__.__name__}[d='{self.data}';origin={self.source};target={self.target}]"

    def __repr__(self):
        return str(self)

    def __eq__(self, other):
        return self.data == other.data and self.source == other.source and self.target == other.target

    def copy(self, new_message_type: type = None):
        if new_message_type is None:
            m = self.__class__(self.data)
        else:
            m = new_message_type(self.data)
        for attr in ["source", "target"]:
            setattr(m, attr, getattr(self, attr))
        return m


class GenericMessageOutgoingEvent(GenericMessageEvent):
    pass


class GenericMessageReceivedReport(GenericMessageEvent):
    pass

