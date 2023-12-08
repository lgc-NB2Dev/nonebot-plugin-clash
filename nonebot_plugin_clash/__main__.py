from typing import Awaitable, Callable, Type

from nonebot import logger, on_command
from nonebot.matcher import Matcher
from nonebot_plugin_alconna.uniseg import Image, UniMessage

from .clash import ClashController, controller
from .render import render_summary

ImageRendererType = Callable[[ClashController], Awaitable[bytes]]


def create_image_handler(func: ImageRendererType):
    async def handler(matcher: Matcher):
        if not controller.connected:
            await matcher.finish("Clash 连接状态异常")
        if not controller.has_data:
            await matcher.finish("暂无数据，请稍等一会")

        try:
            img = await func(controller)
        except Exception:
            logger.exception("Failed to render summary")
            await matcher.finish("渲染图片失败，请检查后台输出")

        await UniMessage(Image(raw=img)).send()

    return handler


def register_image_command(
    func: ImageRendererType,
    *cmd: str,
    **kwargs,
) -> Type[Matcher]:
    first, *rest = cmd
    matcher = on_command(first, aliases=set(rest), **kwargs)
    matcher.handle()(create_image_handler(func))
    return matcher


register_image_command(render_summary, "clash概览")
