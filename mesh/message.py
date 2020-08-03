from lahja import BaseEvent

from utils.space import Position


class GenericMessageEvent(BaseEvent):
    """
    Holder for generic message used by mesh nodes to communicate with each other
    Movements of this messages will be main interest of this project
    """

    source_position: Position = None
    attrs_to_copy = ["source_position"]

    def __init__(self, data):
        super().__init__()
        self.data: NetworkPDU = data

    def __str__(self):
        return f"{self.__class__.__name__}[d='{self.data}';origin={self.source_position}]"

    def __repr__(self):
        return str(self)

    def __eq__(self, other):
        return self.data == other.data and self.source_position == other.source_position

    def copy(self, new_message_type: type = None):
        if new_message_type is None:
            m = self.__class__(self.data)
        else:
            m = new_message_type(self.data)
        for attr in self.attrs_to_copy:
            setattr(m, attr, getattr(self, attr))
        return m


class GenericMessageOutgoingEvent(GenericMessageEvent):
    pass


class GenericMessageReceivedReport(GenericMessageEvent):
    target_position = None

    timestamp = None
    accepted = False
    reporter = None

    def __str__(self):
        return super().__str__() + f"[target={self.target_position}]"

    def __eq__(self, other):
        return super().__eq__(other) and self.target_position == other.target_position


class NetworkPDU:

    def __init__(self):
        """
        IVI           1 Least significant bit of IV Index
        NID           7 Value derived from the NetKey used to identify the Encryption Key and Privacy Key used to secure this PDU
        CTL           1 Network Control
        TTL           7 Time To Live
        SEQ           24 Sequence Number
        SRC           16 Source Address
        DST           16 Destination Address
        TransportPDU  8 to 128 Transport Protocol Data Unit
        NetMIC        32 or 64 Message Integrity Check for Network
        """
        self.ivi = None
        self.nid = None
        self.ctl = None
        self.ttl = None
        self.seq = None
        self.src = None
        self.dest = None
        self.transport_pdu = None
        self.net_mic = None

    def __str__(self):
        return f"NetPDU[{self.src}->{self.dest}][SEQ:{self.seq}][TTL:{self.ttl}][Data:{self.transport_pdu}]"

    def __repr__(self):
        return self.__str__()
