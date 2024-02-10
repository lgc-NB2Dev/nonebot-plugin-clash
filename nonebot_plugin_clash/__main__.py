from typing import Awaitable, Callable, Type

from nonebot import logger, on_command
from nonebot.matcher import Matcher
from nonebot.permission import SUPERUSER
from nonebot_plugin_alconna.uniseg import Image, UniMessage

from .clash import ClashController, controller as main_cc
from .config import config
from .render import render_logs, render_summary

ImageRendererType = Callable[[ClashController], Awaitable[bytes]]

PERM = SUPERUSER if config.clash_need_superuser else None


async def ensure_connected(matcher: Matcher, cc: ClashController):
    if not cc.connected:
        await matcher.finish("Clash 连接状态异常")
    if not cc.has_data:
        await matcher.finish("暂无数据，请稍等一会")


def register_image_command(
    func: ImageRendererType,
    *cmd: str,
    **kwargs,
) -> Type[Matcher]:
    async def handler(matcher: Matcher):
        await ensure_connected(matcher, main_cc)
        try:
            img = await func(main_cc)
        except Exception:
            logger.exception("Failed to render summary")
            await matcher.finish("渲染图片失败，请检查后台输出")
        await UniMessage(Image(raw=img)).send()

    first, *rest = cmd
    matcher = on_command(first, aliases=set(rest), permission=PERM, **kwargs)
    matcher.append_handler(handler)
    return matcher


register_image_command(render_summary, "clash概览")
register_image_command(render_logs, "clash日志")


cmd_clear_logs = on_command("clash清空日志", permission=PERM)


@cmd_clear_logs.handle()
async def handle_clear_logs(matcher: Matcher):
    # await ensure_connected(matcher, main_cc)
    main_cc.logs_ws.data.clear()
    await matcher.finish("日志已清空")
