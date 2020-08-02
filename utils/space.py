import math


class Position:
    """Representation of physical position in 2D space"""

    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y

    def __str__(self):
        return f"[{self.x};{self.y}]"

    def __hash__(self):
        return abs(hash(str(self))) % (10 ** 8)

    def __eq__(self, other):
        if type(other) == type(self):
            return self.x == other.x and self.y == other.y
        else:
            return False

    def __sub__(self, other):
        x = self.x - other.x
        y = self.y - other.y
        return math.sqrt(math.pow(x, 2) + math.pow(y, 2))
