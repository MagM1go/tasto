from dataclasses import dataclass

from tasto.protocol.api.events import Event
from tasto.protocol.semantics import HTTPMethod, HTTPStatus
from tasto.protocol.uri.uri import URI


@dataclass(frozen=True, slots=True)
class Request(Event):
    method: str | HTTPMethod
    uri: URI
    headers: list[tuple[str, str]]

    http_version: str = "HTTP/1.1"


@dataclass(frozen=True, slots=True)
class Finish(Event):
    pass


@dataclass(frozen=True, slots=True)
class Status(Event):
    version: bytes
    number: bytes | HTTPStatus
    message: bytes


@dataclass(frozen=True, slots=True)
class Header(Event):
    name: str
    value: str


@dataclass(frozen=True, slots=True)
class FinishHeaderSection(Event):
    pass


@dataclass(frozen=True, slots=True)
class HexChunkSize(Event):
    value: str


@dataclass(frozen=True, slots=True)
class ChunkBody(Event):
    data: bytes


@dataclass(frozen=True, slots=True)
class MessageBodyEnd(Event):
    pass


@dataclass(frozen=True, slots=True)
class MessageEnd(Event):
    pass


@dataclass(frozen=True, slots=True)
class Response(Event):
    status: Status
    headers: list[tuple[str, str]]
    chunks: list[ChunkBody]
