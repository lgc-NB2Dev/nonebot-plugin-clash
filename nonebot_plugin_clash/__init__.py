from nonebot.plugin import PluginMetadata, inherit_supported_adapters, require

require("nonebot_plugin_alconna")
require("nonebot_plugin_htmlrender")

from . import __main__ as __main__  # noqa: E402
from .config import ConfigModel, config  # noqa: E402

__version__ = "0.1.0"
__plugin_meta__ = PluginMetadata(
    name="Clash",
    description="在 NoneBot 中控制你的 Clash",
    usage=(
        f"指令{'（仅超级用户可用）' if config.clash_need_superuser else ''}：\n"
        "- clash概览\n"
        "    > 简介：获取当前 Clash 的运行状态概览\n"
        "- clash日志\n"
        "    > 简介：获取已记录的 Clash 日志\n"
        "- clash清空日志\n"
        "    > 简介：清空 Clash 日志记录\n"
    ),
    type="application",
    homepage="https://github.com/lgc-NB2Dev/nonebot-plugin-clash",
    config=ConfigModel,
    supported_adapters=inherit_supported_adapters("nonebot_plugin_alconna"),
    extra={"License": "MIT", "Author": "LgCookie"},
)
