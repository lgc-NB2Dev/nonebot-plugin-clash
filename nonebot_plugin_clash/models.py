import time
from dataclasses import dataclass, field
from typing import Generic, List, Optional, TypeVar

from pydantic.main import BaseModel, Field, ModelMetaclass

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
    destination_ip: str
    destination_port: str
    dns_mode: str
    host: str
    inbound_ip: str
    inbound_name: str
    inbound_port: str
    inbound_user: str
    network: str
    process: str
    process_path: str
    remote_destination: str
    sniff_host: str
    source_ip: str
    source_port: str
    special_proxy: str
    special_rules: str
    connection_type: str = Field(alias="type")
    uid: int


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


API_RETURN_MODEL_MAP = {
    "version": Version,
}
