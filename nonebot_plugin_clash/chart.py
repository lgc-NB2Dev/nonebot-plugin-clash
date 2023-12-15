from datetime import datetime
from functools import partial
from io import BytesIO
from typing import Any, Callable, List

from matplotlib import pyplot
from matplotlib.axes import Axes
from matplotlib.figure import Figure

from .models import MemoryData, TrafficData, WsData
from .utils import auto_convert_unit

MULTIPLIER = 2
CHART_W = 760
CHART_H = 400

UP_COLOR = "#db4d6d"
UP_BG_COLOR = "#db4d6d80"
DOWN_COLOR = "#51a8dd"
DOWN_BG_COLOR = "#51a8dd80"
GRID_COLOR = "#555"
MAX_TEXT_COLOR = "#ccc"
LEGEND_BBOX = (0.5, 1.1)


def get_figure() -> Figure:
    figure = pyplot.figure()
    figure.set_dpi(figure.dpi * MULTIPLIER)
    figure.set_size_inches(
        CHART_W * MULTIPLIER / figure.dpi,
        CHART_H * MULTIPLIER / figure.dpi,
    )
    return figure


def save_figure(figure: Figure) -> bytes:
    figure.tight_layout(pad=0)
    bio = BytesIO()
    figure.savefig(bio, transparent=True, format="png")
    return bio.getvalue()


def byte_unit_formatter(v: float, _, **kwargs) -> str:
    return auto_convert_unit(v, **kwargs)


def timestamp_formatter(t: float, _) -> str:
    return datetime.fromtimestamp(t).strftime("%H:%M:%S")


def ax_draw_plot(
    ax: Axes,
    y_data: List[float],
    x_data: List[int],
    label: str,
    color: str,
    bg_color: str,
):
    ax.fill_between(y_data, 0, x_data, color=bg_color)  # type: ignore
    ax.plot(y_data, x_data, label=label, color=color)


def ax_draw_max_label(ax: Axes, x_start: float, y_value: float, label: str):
    ax.axhline(y_value, color=MAX_TEXT_COLOR, linewidth=1, linestyle="--")
    ax.annotate(
        label,
        (x_start, y_value),
        xytext=(5, -5),
        textcoords="offset pixels",
        color=MAX_TEXT_COLOR,
        ha="left",
        va="top",
    )


def ax_draw_last_time(ax: Axes, time: float):
    ax.annotate(
        timestamp_formatter(time, None),
        (time, 0),
        color=MAX_TEXT_COLOR,
        ha="right",
        va="bottom",
    )


def ax_settings(ax: Axes, y_formatter: Callable[[Any, Any], str]):
    ax.legend(
        loc="upper center",
        ncols=2,
        bbox_to_anchor=LEGEND_BBOX,
        labelcolor=GRID_COLOR,
        framealpha=0,
    )
    ax.tick_params(colors=GRID_COLOR)
    ax.grid(color=GRID_COLOR, linewidth=1, linestyle="--")
    ax.spines[:].set_color("#0000")
    ax.margins(0)
    ax.xaxis.set_major_formatter(timestamp_formatter)
    ax.yaxis.set_major_formatter(y_formatter)


async def render_traffic_chart(data: List[WsData[TrafficData]]) -> bytes:
    figure = get_figure()
    ax = figure.add_subplot()

    times = [d.time for d in data]
    upload = [d.data.up for d in data]
    download = [d.data.down for d in data]
    ax_draw_plot(ax, times, upload, "Upload", UP_COLOR, UP_BG_COLOR)
    ax_draw_plot(ax, times, download, "Download", DOWN_COLOR, DOWN_BG_COLOR)

    up_max = max(upload)
    ax_draw_max_label(
        ax,
        times[0],
        up_max,
        f"Ul Max {auto_convert_unit(up_max, suffix='/s')}",
    )
    down_max = max(download)
    ax_draw_max_label(
        ax,
        times[0],
        down_max,
        f"Dl Max {auto_convert_unit(down_max, suffix='/s')}",
    )
    ax_draw_last_time(ax, times[-1])
    ax_settings(ax, partial(byte_unit_formatter, suffix="/s"))
    return save_figure(figure)


async def render_memory_chart(data: List[WsData[MemoryData]]) -> bytes:
    figure = get_figure()
    ax = figure.add_subplot()

    times = [d.time for d in data]
    mem = [d.data.in_use for d in data]
    ax_draw_plot(ax, times, mem, "Memory", DOWN_COLOR, DOWN_BG_COLOR)

    mem_max = max(mem)
    ax_draw_max_label(
        ax,
        times[0],
        mem_max,
        f"Mem Max {auto_convert_unit(mem_max)}",
    )
    ax_draw_last_time(ax, times[-1])
    ax_settings(ax, byte_unit_formatter)
    return save_figure(figure)
