import asyncio as aio
from contextlib import suppress
from functools import partial
from typing import TYPE_CHECKING, Any, Callable, Generic, Optional, Type, TypeVar

from httpx import AsyncClient
from nonebot import get_driver, logger
from pydantic.main import BaseModel
from websockets.legacy.client import Connect, WebSocketClientProtocol
from yarl import URL

from .config import config
from .models import (
    API_RETURN_MODEL_MAP,
    ConnectionsData,
    LogData,
    MemoryData,
    TrafficData,
    Version,
    WsData,
)
from .utils import SizedList

driver = get_driver()


TM = TypeVar("TM", bound=BaseModel)

RECONNECT_INTERVAL = 3


class ClashAPIWs(Generic[TM]):
    def __init__(
        self,
        model: Type[TM],
        base_url: str,
        path: str,
        secret: Optional[str] = None,
        params: Optional[dict[str, Any]] = None,
        data_size: int = 150,
    ) -> None:
        self.url = URL(base_url) / path
        self.url = self.url.with_scheme(
            "wss" if self.url.scheme == "https" else "ws",
        )
        self.model = model
        self.secret = secret
        self.params = params or {}

        self.data = SizedList[WsData[TM]](size=data_size)
        self._task: Optional[aio.Task] = None
        self._ws: Optional[WebSocketClientProtocol] = None

    @property
    def connected(self) -> bool:
        return bool(self._ws and self._ws.open)

    async def connect(self) -> None:
        self._task = aio.create_task(self._loop())

    async def disconnect(self) -> None:
        if not self._task:
            return
        self._task.cancel()
        self._task = None
        self._ws = None

    async def _loop(self) -> None:
        params = self.params.copy()
        if self.secret:
            params["token"] = self.secret
        url = str(self.url.with_query(**params))
        connect = Connect(url, ping_interval=None)
        while True:
            try:
                async with connect as ws:
                    self._ws = ws
                    logger.debug(f"Connected to {self.url}")
                    while ws.open:
                        data = await ws.recv()
                        try:
                            self.data.append(WsData(self.model.parse_raw(data)))
                        except Exception:
                            logger.exception(f"Error when parsing ws data {data}")
            except Exception:
                logger.exception(f"Error when processing ws connection {self.url}")

            self._ws = None
            # self.data.clear()
            logger.error(
                f"Lost connection to {self.url}, "
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
        headers = {"Authorization": f"Bearer {self.secret}"} if self.secret else None
        async with AsyncClient(base_url=str(self.url)) as cli:
            logger.debug(f"Calling API {path}")
            resp = await cli.get(
                path,
                headers=headers,
                timeout=config.api_timeout,
                params=kwargs,
            )
            resp.raise_for_status()

        if path in API_RETURN_MODEL_MAP:
            return API_RETURN_MODEL_MAP[path].parse_raw(resp.text)
        with suppress(Exception):
            return resp.json()
        with suppress(Exception):
            return resp.text
        return resp.content


class ClashController:
    def __init__(self, url: str, secret: Optional[str] = None) -> None:
        self.url = url
        self.secret = secret

        self.version: Optional[Version] = None
        self.api = ClashAPI(url, secret)
        self.traffic_ws = ClashAPIWs(
            TrafficData,
            url,
            "traffic",
            secret,
            data_size=config.clash_chart_width,
        )
        self.connections_ws = ClashAPIWs(
            ConnectionsData,
            url,
            "connections",
            secret,
            data_size=config.clash_chart_width,
        )
        self.logs_ws = ClashAPIWs(
            LogData,
            url,
            "logs",
            secret,
            params={"level": config.clash_log_level},
            data_size=config.clash_log_count,
        )
        self.memory_ws = ClashAPIWs(
            MemoryData,
            url,
            "memory",
            secret,
            data_size=config.clash_chart_width,
        )

    @property
    def is_meta(self) -> bool:
        if not self.version:
            raise ValueError("Please call prepare() first")
        return self.version.meta

    @property
    def connected(self) -> bool:
        return (
            self.traffic_ws.connected
            and self.connections_ws.connected
            and self.logs_ws.connected
            and (self.memory_ws.connected if self.is_meta else True)
        )

    @property
    def has_data(self) -> bool:
        return bool(
            self.traffic_ws.data
            and self.connections_ws.data
            and (self.memory_ws.data if self.is_meta else True),
        )

    async def prepare(self) -> None:
        version = await self.api.version()
        self.version = version
        coroutines = [
            self.traffic_ws.connect(),
            self.connections_ws.connect(),
            self.logs_ws.connect(),
        ]
        if version.meta:
            coroutines.append(self.memory_ws.connect())
        await aio.gather(*coroutines)

    async def close(self) -> None:
        self.version = None
        await aio.gather(
            self.connections_ws.disconnect(),
            self.traffic_ws.disconnect(),
            self.logs_ws.disconnect(),
            self.memory_ws.disconnect(),
        )


controller = ClashController(config.clash_controller_url, config.clash_secret)


@driver.on_startup
async def _():
    async def wait_connect() -> None:
        while not controller.connected:
            await aio.sleep(0)

    await controller.prepare()
    await aio.wait_for(wait_connect(), timeout=config.api_timeout)
    logger.opt(colors=True).success(f"<g>Connected to</g> <y>{controller.url}</y>")


@driver.on_shutdown
async def _():
    await controller.close()
