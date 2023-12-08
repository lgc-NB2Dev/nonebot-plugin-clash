from contextlib import asynccontextmanager
from pathlib import Path
from typing import AsyncIterator, Literal

import jinja2
from nonebot import logger
from nonebot_plugin_htmlrender import get_new_page
from playwright.async_api import Page, Request, Route
from yarl import URL

from .clash import ClashController

RES_DIR = Path(__file__).parent / "res"
TEMPLATES_DIR = RES_DIR / "templates"
ROUTE_BASE_URL = "https://clash.nonebot/"

TEMPLATE_ENV = jinja2.Environment(
    loader=jinja2.FileSystemLoader(TEMPLATES_DIR),
    autoescape=jinja2.select_autoescape(),
    enable_async=True,
)


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


async def render_summary(controller: ClashController) -> bytes:
    assert controller.connected
    template = TEMPLATE_ENV.get_template("summary.html.jinja")
    html = await template.render_async(c=controller)
    async with get_routed_page() as page:
        await page.set_content(html)
        return await screenshot_elem(page, ".main")


def filter_convert_unit(value: float, round_n: int = 2, suffix: str = "") -> str:
    units = ["B", "KB", "MB", "GB", "TB", "PB"]

    unit = None
    for u in units:
        if value < 1000:
            unit = u
            break
        value /= 1024

    return f"{value:.{round_n}f} {unit or units[-1]}{suffix}"


TEMPLATE_ENV.filters["convert_unit"] = filter_convert_unit
