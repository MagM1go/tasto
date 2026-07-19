from dataclasses import dataclass

from tasto.protocol.api.events import Event
from tasto.protocol.semantics import HTTPMethod
from tasto.protocol.uri.uri import URI, parse_uri_from_string


@dataclass(init=False, frozen=True, slots=True)
class Request(Event):    
    method: str | HTTPMethod
    uri: str | URI

    def __init__(self, method: str | HTTPMethod, uri: str | URI) -> None:
        object.__setattr__(self, "method", method)
        object.__setattr__(self, "uri", parse_uri_from_string(uri))


@dataclass(frozen=True, slots=True, init=False)
class Data(Event):
    data: bytes
    is_last_chunk: bool


class Waiting(Event): ...


class EndOfMessage(Event): ...
