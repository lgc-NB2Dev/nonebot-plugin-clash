from typing import Literal, Optional
from typing_extensions import Annotated

from nonebot import get_plugin_config
from pydantic import AnyUrl, BaseModel

LogLevelType = Literal["debug", "info", "warn", "error"]


class ConfigModel(BaseModel):
    api_timeout: Optional[float]

    clash_controller_url: Annotated[str, AnyUrl]
    clash_secret: Optional[str] = None
    clash_need_superuser: bool = True
    clash_chart_width: int = 150
    clash_log_level: LogLevelType = "info"
    clash_log_count: int = 50
    clash_image_width: int = 600


config = get_plugin_config(ConfigModel)
