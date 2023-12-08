from typing import Optional

from nonebot import get_driver
from pydantic import AnyUrl, BaseModel


class ConfigModel(BaseModel):
    api_timeout: Optional[float]

    clash_controller_url: AnyUrl
    clash_secret: Optional[str] = None
    clash_need_superuser: bool = True


config: ConfigModel = ConfigModel.parse_obj(get_driver().config)
