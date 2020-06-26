
from collections import defaultdict
from mesh.generic import GenericNode, GenericMessage
from utils.space import Position


class NodeWithCache(GenericNode):
    """
        Repeated messages from same source will be dropped by this Node
    """
    def __init__(self, position: Position):
        super().__init__(position)
        self._cache = defaultdict(list)

    def resend_message_to_network(self, message: GenericMessage) -> bool:
        self.logger.debug(f"[{self}] Message received: {message}")
        if message.origin in self._cache:
            if message.seq in self._cache[message.origin]:
                self.logger.info(f"[{self}] RPL triggered - Message will be DROPPED: {message}")
                return False
        self._cache[message.origin].append(message.seq)
        self.logger.info(f"[{self}]Message will be re-send: {message}")
        return True

