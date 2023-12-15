import time
from dataclasses import dataclass, field
from typing import Generic, List, Optional, TypeVar

from pydantic import BaseModel, Field
from pydantic.main import ModelMetaclass

from .utils import camel_case

T = TypeVar("T")


class CamelAliasModelMeta(ModelMetaclass):
    def __new__(mcs, name, bases, namespace, **kwargs):  # noqa: N804
        kwargs["alias_generator"] = camel_case
        return super().__new__(mcs, name, bases, namespace, **kwargs)


@dataclass
class WsData(Generic[T]):
    data: T
    time: float = field(default_factory=time.time)


class TrafficData(BaseModel):
    up: int
    down: int


class ConnectionMetadata(BaseModel, metaclass=CamelAliasModelMeta):
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
    inbound_name: Optional[str]
    inbound_port: Optional[str]
    inbound_user: Optional[str]
    process: Optional[str]
    remote_destination: Optional[str]
    sniff_host: Optional[str]
    special_rules: Optional[str]
    uid: Optional[str]


class Connection(BaseModel, metaclass=CamelAliasModelMeta):
    chains: List[str]
    download: int
    connection_id: str = Field(alias="id")
    metadata: ConnectionMetadata
    rule: str
    rule_payload: str
    start: str
    upload: int


class ConnectionsData(BaseModel, metaclass=CamelAliasModelMeta):
    connections: List[Connection]
    download_total: int
    upload_total: int
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
