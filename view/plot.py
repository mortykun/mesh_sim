import time
from typing import List

import matplotlib.pyplot as plt


class Line:
    def __init__(self, x, y, z):
        self.alpha = 0.01
        self.color = 'black'
        self.x = x
        self.y = y
        self.z = z


class PropertyAx(type):
    def __init__(cls, *args, **kwargs):
        super().__init__(*args, **kwargs)
        cls._ax = None

    @property
    def ax(cls):
        if cls._ax is None:
            cls._ax = plt.axes(projection='3d')
        return cls._ax


class Plot(metaclass=PropertyAx):

    @classmethod
    def plot_points(cls, x, y, z, **kwargs):
        cls.ax.scatter3D(x, y, z, cmap='Greens')
        plt.show(block=False)

    @classmethod
    def plot_lines(cls, lines: List[Line]):
        for line in lines:
            # time.sleep(0.5)
            cls.ax.plot3D(line.x, line.y, line.z, line.color, alpha=line.alpha)

