import time
from typing import List

import matplotlib.pyplot as plt


class Line:
    def __init__(self, x, y):
        self.alpha = 0.01
        self.color = 'black'
        self.x = x
        self.y = y


class PropertyAx(type):
    def __init__(cls, *args, **kwargs):
        super().__init__(*args, **kwargs)
        cls._ax = None

    @property
    def ax(cls):
        if cls._ax is None:
            cls._ax = plt.axes(projection='rectilinear')
        return cls._ax


class Plot(metaclass=PropertyAx):

    @classmethod
    def plot_points(cls, x, y, **kwargs):
        cls.ax.scatter(x, y,  cmap='Greens')
        plt.show(block=False)

    @classmethod
    def plot_lines(cls, lines: List[Line]):
        for line in lines:
            # time.sleep(0.5)
            cls.ax.plot(line.x, line.y, line.color, alpha=line.alpha)

