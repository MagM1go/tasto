from tasto.protocol.api.events import Event
from tasto.protocol.semantics import HTTPMethod


class Request(Event):
    def __init__(self, method: str | HTTPMethod, uri: str, ) -> None:
        self.method = method
        self.uri = uri

class Data(Event): ...

class EndOfMessage(Event): ...
