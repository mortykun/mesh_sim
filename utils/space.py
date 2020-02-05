class Position:

    def __init__(self, x: int, y: int, z: int):
        self.x = x
        self.y = y
        self.z = z

    def __str__(self):
        return f"Position[{self.x=}{self.y=}{self.z=}"

    def __hash__(self):
        return abs(hash(str(self))) % (10 ** 8)
