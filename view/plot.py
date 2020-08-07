import enum
import logging
from collections import defaultdict
from typing import List, Tuple, Dict
from matplotlib import pyplot as plt
import numpy as np
from matplotlib.axes import Axes
from matplotlib.lines import Line2D
from matplotlib.widgets import Slider

from mesh.message import GenericMessageReceivedReport


class Line:
    def __init__(self, timestamp, x, y):
        self.timestamp = timestamp
        self.alpha = 0.02
        self.color = 'black'
        self.x = x
        self.y = y


class MeshPlotMode(enum.Enum):
    ALL_MESSAGES = 1
    ONLY_FIRST = 2
    BAR_RECEIVED = 3


class Plot:
    MAX = 100
    slider_min: Slider = None
    slider_max: Slider = None
    timestamp_min: float = float("inf")
    timestamp_max: float = 0.0
    line_cache = []

    def __init__(self, nrows=1, ncols=1, sharex=False, sharey=False):
        self.fig, self.ax = plt.subplots(**{
            "nrows": nrows,
            "ncols": ncols,
            "sharex": sharex,
            "sharey": sharey
        })

        self.add_slider()
        plt.show(block=False)

    def add_slider(self):
        plt.subplots_adjust(bottom=0.2)
        self.slider_min = Slider(plt.axes([0.15, 0.1, 0.65, 0.03]), 'MIN', 0, 100, valinit=0, valstep=1)
        self.slider_min.on_changed(self.update_lines)
        self.slider_max = Slider(plt.axes([0.15, 0.05, 0.65, 0.03]), 'MAX', 0, 100, valinit=100, valstep=1)
        self.slider_max.on_changed(self.update_lines)

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
        for line in lines:
            line_key = (tuple(line.x), tuple(line.y))
            drawn_line, = ax.plot(line.x, line.y, line.color, alpha=alpha if alpha else line.alpha)
            self.add_arrow(drawn_line)
            self.line_cache.append((line.timestamp, drawn_line, drawn_line.get_alpha()))
            self.timestamp_min = line.timestamp if line.timestamp < self.timestamp_min else self.timestamp_min
            self.timestamp_max = line.timestamp if line.timestamp > self.timestamp_max else self.timestamp_max
        # self.fig.canvas.draw_idle()

    def update_lines(self, _):
        timestamp_step = (self.timestamp_max - self.timestamp_min) / 100
        logging.info(f"{timestamp_step}")
        logging.info(f"{self.timestamp_min} + {self.slider_min.val * timestamp_step}")
        logging.info(f"{self.timestamp_min} + {self.slider_max.val * timestamp_step}")
        min_timestamp = self.timestamp_min + self.slider_min.val * timestamp_step
        max_timestamp = self.timestamp_min + self.slider_max.val * timestamp_step
        logging.info(f"Calculated min:[{min_timestamp}] and max:[{max_timestamp}] ")
        all_time = []
        for timestamp, line, alpha in self.line_cache:
            line: Line2D
            all_time.append(timestamp)

            if timestamp > max_timestamp or timestamp < min_timestamp:
                line.set_alpha(0)
            else:
                line.set_alpha(alpha)

            # logging.info(f"timestamp:{all_time}")
        self.fig.canvas.draw_idle()

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
                entry.timestamp,
                [entry.source_position.x, entry.target_position.x],
                [entry.source_position.y, entry.target_position.y]
            ))
        return out
