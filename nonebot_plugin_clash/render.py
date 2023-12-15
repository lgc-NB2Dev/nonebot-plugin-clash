from contextlib import asynccontextmanager
from functools import partial
from pathlib import Path
from typing import AsyncIterator, Literal

import jinja2
from nonebot import logger
from nonebot_plugin_htmlrender import get_new_page
from playwright.async_api import Page, Request, Route
from yarl import URL

from .chart import render_memory_chart, render_traffic_chart
from .clash import ClashController
from .config import config
from .utils import auto_convert_unit, b2url, format_timestamp

RES_DIR = Path(__file__).parent / "res"
TEMPLATES_DIR = RES_DIR / "templates"
ROUTE_BASE_URL = "https://clash.nonebot/"

TEMPLATE_ENV = jinja2.Environment(
    loader=jinja2.FileSystemLoader(TEMPLATES_DIR),
    autoescape=jinja2.select_autoescape(),
    enable_async=True,
)
TEMPLATE_ENV.filters["convert_unit"] = auto_convert_unit
TEMPLATE_ENV.filters["format_timestamp"] = format_timestamp


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


async def generic_render(cc: ClashController, template_name: str, **kwargs) -> bytes:
    assert cc.connected
    template = TEMPLATE_ENV.get_template(template_name)
    html = await template.render_async(cc=cc, config=config, **kwargs)
    async with get_routed_page() as page:
        await page.set_content(html)
        return await screenshot_elem(page, ".main")


async def render_summary(cc: ClashController) -> bytes:
    return await generic_render(
        cc,
        "summary.html.jinja",
        traffic_chart=await b2url(await render_traffic_chart(cc.traffic_ws.data)),
        memory_chart=(
            await b2url(await render_memory_chart(cc.memory_ws.data))
            if cc.is_meta
            else None
        ),
    )


render_logs = partial(generic_render, template_name="logs.html.jinja")
