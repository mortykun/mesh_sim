from mesh.generic import GenericNode


class Network:
    """
    Holder for mesh network
    """

    def __init__(self):
        self.nodes = set()

    def add_node(self, node: GenericNode):
        assert node not in self.nodes, "Node already added to Network"
        self.nodes.add(node)
