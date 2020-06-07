class Position:
    """Representation of physical position in 3D space"""
    def __init__(self, x: int, y: int, z: int):
        self.x = x
        self.y = y
        self.z = z

    def __str__(self):
        return f"[{self.x};{self.y};{self.z}]"

    def __hash__(self):
        return abs(hash(str(self))) % (10 ** 8)

    def __eq__(self, other):
        if type(other) == type(self):
            return self.x == other.x and self.y == other.y and self.z == other.z
        else:
            return False
