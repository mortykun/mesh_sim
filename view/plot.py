import logging
from typing import List
from matplotlib import pyplot as plt
import numpy as np
from matplotlib.lines import Line2D


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
        cls.ax.scatter(x, y, cmap='Greens')
        plt.show(block=False)

    @classmethod
    def plot_lines(cls, lines: List[Line]):
        logging.info(f"Number of mesh messages: {len(lines)}")
        for line in lines:
            line, = cls.ax.plot(line.x, line.y, line.color, alpha=line.alpha)
            cls.add_arrow(line)

    @staticmethod
    def add_arrow(line: Line2D, position=None, size=15, color=None):
        """
        add an arrow to a line.

        line:       Line2D object
        position:   x-position of the arrow. If None, mean of xdata is taken
        size:       size of the arrow in fontsize points
        color:      if None, line color is taken.
        """
        if color is None:
            color = line.get_color()

        alpha = line.get_alpha()
        x_data = line.get_xdata()
        y_data = line.get_ydata()

        if position is None:
            position = x_data.mean()
        # find closest index
        start_ind = np.argmin(np.absolute(x_data - position))
        end_ind = start_ind + 1

        line.axes.annotate('',
                           xytext=(x_data[start_ind], y_data[start_ind]),
                           xy=(x_data[end_ind], y_data[end_ind]),
                           arrowprops=dict(arrowstyle="-|>", color=color, alpha=alpha),
                           size=size
                           )
