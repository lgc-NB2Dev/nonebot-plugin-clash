import base64
from contextlib import asynccontextmanager
from datetime import datetime
from functools import partial
from io import BytesIO
from pathlib import Path
from typing import AsyncIterator, List, Literal

import jinja2
from matplotlib import pyplot
from matplotlib.figure import Figure
from nonebot import logger
from nonebot_plugin_htmlrender import get_new_page
from playwright.async_api import Page, Request, Route
from yarl import URL

from .clash import ClashController
from .models import MemoryData, TrafficData, WsData
from .utils import auto_convert_unit

RES_DIR = Path(__file__).parent / "res"
TEMPLATES_DIR = RES_DIR / "templates"
ROUTE_BASE_URL = "https://clash.nonebot/"

TEMPLATE_ENV = jinja2.Environment(
    loader=jinja2.FileSystemLoader(TEMPLATES_DIR),
    autoescape=jinja2.select_autoescape(),
    enable_async=True,
)
TEMPLATE_ENV.filters["convert_unit"] = auto_convert_unit

CHART_W = 760
CHART_H = 400


async def router(route: Route, request: Request):
    url = URL(request.url)
    url_path = url.path[1:]
    file_path = RES_DIR / url_path
    logger.debug(f"Route {url} to {file_path}")
    if file_path.exists() and file_path.is_file():
        await route.fulfill(body=file_path.read_bytes(), status=200)
        return
    await route.abort()


@asynccontextmanager
async def get_routed_page() -> AsyncIterator[Page]:
    async with get_new_page() as page:
        await page.route(f"{ROUTE_BASE_URL}**", router)
        await page.goto(f"{ROUTE_BASE_URL}index.html")
        yield page


async def screenshot_elem(
    page: Page,
    selector: str,
    image_format: Literal["jpeg", "png"] = "jpeg",
    **kwargs,
) -> bytes:
    elem = await page.wait_for_selector(selector)
    assert elem
    return await elem.screenshot(type=image_format, **kwargs)


def get_figure() -> Figure:
    figure = pyplot.figure()
    figure.set_size_inches(CHART_W / figure.dpi, CHART_H / figure.dpi)
    return figure


def save_figure(figure: Figure) -> bytes:
    bio = BytesIO()
    figure.savefig(bio, transparent=True, format="png")
    return bio.getvalue()


def byte_unit_formatter(v: float, _, **kwargs) -> str:
    return auto_convert_unit(v, **kwargs)


def timestamp_formatter(t: float, _) -> str:
    return datetime.fromtimestamp(t).strftime("%H:%M:%S")


async def render_traffic_chart(data: List[WsData[TrafficData]]) -> bytes:
    up_color = "#db4d6d"
    up_bg_color = "#db4d6d80"
    down_color = "#51a8dd"
    down_bg_color = "#51a8dd80"
    grid_color = "#555"
    max_text_color = "#ccc"
    legend_bbox = (0.5, 1.1)

    figure = get_figure()
    ax = figure.add_subplot()
    times = [d.time for d in data]
    upload = [d.data.up for d in data]
    download = [d.data.down for d in data]
    ax.fill_between(times, 0, upload, color=up_bg_color)  # type: ignore
    ax.plot(times, upload, label="Upload", color=up_color)
    ax.fill_between(times, 0, download, color=down_bg_color)  # type: ignore
    ax.plot(times, download, label="Download", color=down_color)

    up_max = max(upload)
    ax.axhline(up_max, color=max_text_color, linewidth=1, linestyle="--")
    ax.annotate(
        f"Ul Max {auto_convert_unit(up_max, suffix='/s')}",
        (times[0], up_max),
        xytext=(5, -5),
        textcoords="offset pixels",
        color=max_text_color,
        ha="left",
        va="top",
    )

    down_max = max(download)
    ax.axhline(down_max, color=max_text_color, linewidth=1, linestyle="--")
    ax.annotate(
        f"Dl Max {auto_convert_unit(down_max, suffix='/s')}",
        (times[0], down_max),
        xytext=(5, -5),
        textcoords="offset pixels",
        color=max_text_color,
        ha="left",
        va="top",
    )

    ax.annotate(
        timestamp_formatter(times[-1], None),
        (times[-1], 0),
        color=max_text_color,
        ha="right",
        va="bottom",
    )

    ax.legend(
        loc="upper center",
        ncols=2,
        bbox_to_anchor=legend_bbox,
        labelcolor=grid_color,
        framealpha=0,
    )
    ax.tick_params(colors=grid_color)
    ax.grid(color=grid_color, linewidth=1, linestyle="--")
    ax.spines[:].set_color("#0000")
    ax.margins(0)
    ax.xaxis.set_major_formatter(timestamp_formatter)
    ax.yaxis.set_major_formatter(partial(byte_unit_formatter, suffix="/s"))

    figure.tight_layout(pad=0)
    return save_figure(figure)


async def render_memory_chart(data: List[WsData[MemoryData]]) -> bytes:
    mem_color = "#51a8dd"
    mem_bg_color = "#51a8dd80"
    grid_color = "#555"
    max_text_color = "#ccc"
    legend_bbox = (0.5, 1.1)

    figure = get_figure()
    ax = figure.add_subplot()
    times = [d.time for d in data]
    mem = [d.data.in_use for d in data]
    ax.fill_between(times, 0, mem, color=mem_bg_color)  # type: ignore
    ax.plot(times, mem, label="Memory", color=mem_color)

    mem_max = max(mem)
    ax.axhline(mem_max, color=max_text_color, linewidth=1, linestyle="--")
    ax.annotate(
        f"Mem Max {auto_convert_unit(mem_max)}",
        (times[0], mem_max),
        xytext=(5, -5),
        textcoords="offset pixels",
        color=max_text_color,
        ha="left",
        va="top",
    )

    ax.annotate(
        timestamp_formatter(times[-1], None),
        (times[-1], 0),
        color=max_text_color,
        ha="right",
        va="bottom",
    )

    ax.legend(
        loc="upper center",
        bbox_to_anchor=legend_bbox,
        labelcolor=grid_color,
        framealpha=0,
    )
    ax.tick_params(colors=grid_color)
    ax.grid(color=grid_color, linewidth=1, linestyle="--")
    ax.spines[:].set_color("#0000")
    ax.margins(0)
    ax.xaxis.set_major_formatter(timestamp_formatter)
    ax.yaxis.set_major_formatter(byte_unit_formatter)

    figure.tight_layout(pad=0)
    return save_figure(figure)


async def b2url(data: bytes, mime: str = "image/png") -> str:
    b64 = base64.b64encode(data).decode()
    return f"data:{mime};base64,{b64}"


async def render_summary(cc: ClashController) -> bytes:
    assert cc.connected
    template = TEMPLATE_ENV.get_template("summary.html.jinja")
    html = await template.render_async(
        cc=cc,
        traffic_chart=await b2url(await render_traffic_chart(cc.traffic_ws.data)),
        memory_chart=(
            await b2url(await render_memory_chart(cc.memory_ws.data))
            if cc.is_meta
            else None
        ),
    )
    async with get_routed_page() as page:
        await page.set_content(html)
        return await screenshot_elem(page, ".main")
