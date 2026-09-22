from dataclasses import dataclass

from tasto.protocol.api.events import Event
from tasto.protocol.semantics import HTTPMethod


@dataclass(frozen=True, slots=True)
class Header(Event):
    key: bytes
    value: bytes


@dataclass(frozen=True, slots=True)
class _BaseInformation(Event):
    headers: list[list[tuple[str, str]]]
    http_version: str


@dataclass(frozen=True, slots=True)
class Request(_BaseInformation):
    method: str | HTTPMethod
    target: str


@dataclass(frozen=True, slots=True)
class Waiting: ...


@dataclass(frozen=True, slots=True)
class Data(Event):
    data: bytes


@dataclass(frozen=True, slots=True)
class MessageEnd(Event):
    pass


@dataclass(frozen=True, slots=True)
class ConnectionClosed:
    pass


@dataclass(frozen=True, slots=True)
class InformationResponse(_BaseInformation):
    pass


@dataclass(frozen=True, slots=True)
class Response(_BaseInformation):
    http_status: str
    message: str


@dataclass(frozen=True, slots=True)
class _NeedMore:
    pass


NEED_DATA = _NeedMore()
WAITING = Waiting()
