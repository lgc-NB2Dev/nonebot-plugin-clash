import asyncio as aio
import json
from contextlib import suppress
from functools import partial
from typing import TYPE_CHECKING, Any, Callable, Generic, Optional, Type, TypeVar

from nonebot import get_driver, logger
from nonebot.drivers import HTTPClientMixin, Request, WebSocketClientMixin
from nonebot.exception import NetworkError
from pydantic.main import BaseModel
from yarl import URL

from .config import config
from .models import (
    API_RETURN_MODEL_MAP,
    ConnectionsData,
    MemoryData,
    TrafficData,
    Version,
    WsData,
)
from .utils import SizedList

driver = get_driver()

if not (
    isinstance(driver, WebSocketClientMixin) and isinstance(driver, HTTPClientMixin)
):
    raise TypeError(
        "This plugin requires a Forward driver that supports to be used as a WebSocket client and HTTP client!\n"
        "本插件需要使用支持作为 WebSocket 客户端 和 HTTP 客户端 使用的 Forward 类型 驱动器！",
    )


TM = TypeVar("TM", bound=BaseModel)

RECONNECT_INTERVAL = 5
CHART_SIZE = 150


class ClashAPIWs(Generic[TM]):
    def __init__(
        self,
        model: Type[TM],
        base_url: str,
        path: str,
        secret: Optional[str] = None,
    ) -> None:
        self.url = URL(base_url) / path
        self.url = self.url.with_scheme(
            "wss" if self.url.scheme == "https" else "ws",
        )
        self.model = model
        self.secret = secret

        self.data = SizedList[WsData[TM]](size=CHART_SIZE)
        self._task: Optional[aio.Task] = None

    @property
    def connected(self) -> bool:
        return bool(self._task and (not self._task.done()))

    async def connect(self) -> None:
        self._task = aio.create_task(self._loop())

    async def disconnect(self) -> None:
        if self._task:
            self._task.cancel()
            with suppress(aio.CancelledError):
                await self._task
            self._task = None

    async def _loop(self) -> None:
        if TYPE_CHECKING:
            assert isinstance(driver, WebSocketClientMixin)

        params = {"token": self.secret} if self.secret else None
        request = Request("GET", self.url, params=params, timeout=config.api_timeout)
        while True:
            try:
                async with driver.websocket(request) as ws:
                    logger.debug(f"Connected to {self.url}")
                    while True:
                        data = await ws.receive_text()
                        self.data.append(WsData(self.model.parse_raw(data)))
            except Exception:
                logger.opt(exception=True).warning(
                    f"Error when processing connection to {self.url}, "
                    f"retrying in {RECONNECT_INTERVAL} seconds...",
                )
            await aio.sleep(RECONNECT_INTERVAL)


class ClashAPI:
    def __init__(self, url: str, secret: Optional[str] = None) -> None:
        self.url = URL(url)
        if not self.url.scheme.startswith("http"):
            self.url = self.url.with_scheme("http")
        self.secret = secret

    if TYPE_CHECKING:

        async def version(self) -> Version:
            ...

    def __getattr__(self, name: str) -> Callable[..., Any]:
        if not name.startswith("_"):
            return partial(self._call_api, name)
        return object.__getattribute__(self, name)

    async def _call_api(self, path: str, **kwargs) -> Any:
        if TYPE_CHECKING:
            assert isinstance(driver, HTTPClientMixin)

        headers = {"Authorization": f"Bearer {self.secret}"} if self.secret else None
        request = Request(
            "GET",
            self.url / path,
            headers=headers,
            timeout=config.api_timeout,
            params=kwargs,
        )

        logger.debug(f"Calling API: {request}")
        try:
            response = await driver.request(request)
        except Exception as e:
            raise NetworkError("HTTP request failed") from e

        if (response.status_code // 100) != 2:
            raise NetworkError(
                "Clash API returned unexpected status code: "
                f"{response.status_code=}, {response.content=}",
            )
        if not response.content:
            raise NetworkError("Clash API returned empty response")

        if path in API_RETURN_MODEL_MAP:
            return API_RETURN_MODEL_MAP[path].parse_raw(response.content)
        with suppress(Exception):
            return json.loads(response.content)
        return response.content


class ClashController:
    def __init__(self, url: str, secret: Optional[str] = None) -> None:
        self.url = url
        self.secret = secret

        self.api = ClashAPI(url, secret)
        self.traffic_ws = ClashAPIWs(
            TrafficData,
            url,
            "traffic",
            secret,
        )
        self.connections_ws = ClashAPIWs(
            ConnectionsData,
            url,
            "connections",
            secret,
        )
        self.memory_ws = ClashAPIWs(
            MemoryData,
            url,
            "memory",
            secret,
        )

        self.version: Optional[Version] = None

    @property
    def connected(self) -> bool:
        return (
            self.traffic_ws.connected
            and self.connections_ws.connected
            and (
                self.memory_ws.connected
                if (self.version and self.version.meta)
                else True
            )
        )

    async def prepare(self) -> None:
        version = await self.api.version()
        self.version = version
        coroutines = [
            self.traffic_ws.connect(),
            self.connections_ws.connect(),
        ]
        if version.meta:
            coroutines.append(self.memory_ws.connect())
        await aio.gather(*coroutines)

    async def close(self) -> None:
        self.version = None
        await aio.gather(
            self.connections_ws.disconnect(),
            self.traffic_ws.disconnect(),
            self.memory_ws.disconnect(),
        )


controller = ClashController(config.clash_controller_url, config.clash_secret)


@driver.on_startup
async def _():
    async def connect():
        await controller.prepare()
        while not controller.connected:
            await aio.sleep(0)
        logger.opt(colors=True).success(f"<g>Connected to</g> <y>{controller.url}</y>")

    aio.create_task(connect())


@driver.on_shutdown
async def _():
    await controller.close()
