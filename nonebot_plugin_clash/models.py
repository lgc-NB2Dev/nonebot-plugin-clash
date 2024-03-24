import time
from dataclasses import dataclass, field
from typing import Generic, List, Optional, TypeVar

from nonebot.compat import PYDANTIC_V2
from pydantic import BaseModel, ConfigDict, Field

from .utils import camel_case

T = TypeVar("T")


class CamelAliasModel(BaseModel):
    if PYDANTIC_V2:
        model_config = ConfigDict(alias_generator=camel_case)
    else:

        class Config:
            alias_generator = camel_case


@dataclass
class WsData(Generic[T]):
    data: T
    time: float = field(default_factory=time.time)


class TrafficData(BaseModel):
    up: int
    down: int


class ConnectionMetadata(CamelAliasModel):
    network: str
    connection_type: str = Field(alias="type")
    source_ip: str = Field(alias="sourceIP")
    destination_ip: str = Field(alias="destinationIP")
    source_port: str
    destination_port: str
    host: str
    dns_mode: str
    process_path: str
    special_proxy: str

    inbound_ip: Optional[str] = Field(None, alias="inboundIP")
    inbound_name: Optional[str] = None
    inbound_port: Optional[str] = None
    inbound_user: Optional[str] = None
    process: Optional[str] = None
    remote_destination: Optional[str] = None
    sniff_host: Optional[str] = None
    special_rules: Optional[str] = None
    # uid: Optional[str] = None


class Connection(CamelAliasModel):
    chains: List[str]
    download: int
    connection_id: str = Field(alias="id")
    metadata: ConnectionMetadata
    rule: str
    rule_payload: str
    start: str
    upload: int


class ConnectionsData(CamelAliasModel):
    download_total: int
    upload_total: int
    connections: Optional[List[Connection]] = None
    memory: Optional[int] = None


class MemoryData(BaseModel):
    in_use: int = Field(alias="inuse")
    os_limit: int = Field(alias="oslimit")


class Version(BaseModel):
    version: str
    meta: bool = False


class LogData(BaseModel):
    level: str = Field(alias="type")
    payload: str


API_RETURN_MODEL_MAP = {
    "version": Version,
}
