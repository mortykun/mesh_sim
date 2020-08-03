import enum
import logging
from collections import defaultdict
from typing import List, Tuple, Dict
from matplotlib import pyplot as plt
import numpy as np
from matplotlib.axes import Axes
from matplotlib.lines import Line2D

from mesh.message import GenericMessageReceivedReport


class Line:
    def __init__(self, x, y):
        self.alpha = 0.02
        self.color = 'black'
        self.x = x
        self.y = y


class MeshPlotMode(enum.Enum):
    ALL_MESSAGES = 1
    ONLY_FIRST = 2
    BAR_RECEIVED = 3


class Plot:

    def __init__(self, nrows=1, ncols=1, sharex=False, sharey=False):
        fig, self.ax = plt.subplots(**{
            "nrows": nrows,
            "ncols": ncols,
            "sharex": sharex,
            "sharey": sharey
        })

    def draw(self, plot: Tuple, mode: MeshPlotMode, network):
        ax: Axes = self.ax[plot]
        if mode is MeshPlotMode.ALL_MESSAGES:
            self.plot_points(ax, *network.get_nodes_map())
            self.plot_lines(ax, self.get_messages_lines(network.network_history))
        elif mode is MeshPlotMode.ONLY_FIRST:
            self.plot_points(ax, *network.get_nodes_map())
            self.plot_lines(ax, self.get_messages_lines(network.network_history, only_first=True), alpha=0.3)
        elif mode is MeshPlotMode.BAR_RECEIVED:
            self.plot_bars(ax, *self.get_bar_received(network.network_history))
        else:
            raise ValueError(f"Only `ALL_MESSAGES` or `ONLY_FIRST` are supported modes")

    @staticmethod
    def plot_bars(ax, addressees, heights):
        ax.bar(addressees, heights, tick_label=[f"_{v}" for v in addressees])

    @staticmethod
    def plot_points(ax: Axes, x, y, names, **kwargs):
        ax.scatter(x, y, cmap='Greens')
        for i, txt in enumerate(names):
            ax.annotate(txt, (x[i], y[i]))
        plt.show(block=False)

    def plot_lines(self, ax: Axes, lines: List[Line], alpha=None):
        line_cache: Dict[Tuple, Line2D] = {}
        for line in lines:
            line_key = (tuple(line.x), tuple(line.y))
            if line_key not in line_cache.keys():
                drawn_line, = ax.plot(line.x, line.y, line.color, alpha=alpha if alpha else line.alpha)
                self.add_arrow(drawn_line)
                line_cache[line_key] = drawn_line
            else:
                current_alpha = line_cache[line_key].get_alpha()
                line_cache[line_key].set_alpha(current_alpha + line.alpha)

    @staticmethod
    def get_bar_received(history: List[GenericMessageReceivedReport]):
        count = defaultdict(int)

        for entry in history:
            count[entry.reporter] += 1

        return zip(*count.items())

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

    @staticmethod
    def get_messages_lines(history: List[GenericMessageReceivedReport], only_first=False):
        out = list()
        for entry in history:
            if only_first and not entry.accepted:
                continue
            out.append(Line(
                [entry.source_position.x, entry.target_position.x],
                [entry.source_position.y, entry.target_position.y]
            ))
        return out
