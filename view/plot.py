import time
from typing import List

from mpl_toolkits import mplot3d
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D


class Line:
    def __init__(self, x, y, z):
        self.alpha = 0.005
        self.color = 'black'
        self.x = x
        self.y = y
        self.z = z


class property_ax(type):
    def __init__(cls, *args, **kwargs):
        super().__init__(*args, **kwargs)
        cls._ax = None

    @property
    def ax(cls):
        if cls._ax is None:
            cls._ax = plt.axes(projection='3d')
        return cls._ax


class Plot(metaclass=property_ax):

    @classmethod
    def plot_points(cls, x, y, z, **kwargs):
        # Data for a three-dimensional line
        cls.ax.scatter3D(x, y, z, cmap='Greens')
        plt.show(block=False)

        # zline = np.linspace(0, 15, 1000)
        # xline = np.sin(zline)
        # yline = np.cos(zline)
        # self.ax.plot3D(xline, yline, zline, 'gray')

    @classmethod
    def plot_lines(cls, lines: List[Line]):
        for line in lines:
            # time.sleep(0.5)
            cls.ax.plot3D(line.x, line.y, line.z, line.color, alpha=line.alpha)

