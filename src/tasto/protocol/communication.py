import collections
from enum import StrEnum

from tasto.protocol.api.events import Event
from tasto.protocol.http11._events import Data, EndOfMessage, Request


class CommunicationRole(StrEnum):
    CLIENT = "client"
    SERVER = "server"


class _ConnectionState(StrEnum):
    IDLE = "idle"
    SEND_BODY = "send_body"
    DONE = "done"
    MUST_CLOSE = "must_close"
    CLOSED = "closed"


STATES: dict[tuple[_ConnectionState, type[Event]], _ConnectionState] = {
    (_ConnectionState.IDLE, Request): _ConnectionState.SEND_BODY,
    (_ConnectionState.SEND_BODY, Data): _ConnectionState.SEND_BODY,
    (_ConnectionState.SEND_BODY, EndOfMessage): _ConnectionState.DONE,
}


class _StateMachine:
    def __init__(self) -> None:
        self._state: _ConnectionState = _ConnectionState.IDLE

        self._event_queue: collections.deque[Event] = collections.deque()

    def send(self, event: Event) -> None:
        self.transition(event)
        self._event_queue.append(event)

    def transition(self, event: Event) -> None:
        key = (self._state, type(event))
        self._state = STATES[key]


class Communication:
    def __init__(self, role: CommunicationRole) -> None:
        self._client_state = _StateMachine()
        self._server_state = _StateMachine()

        self._role = role

    def _to_bytes(self, data: str) -> bytes:
        return data.encode("ascii")

    def send(self, event: Event) -> bytes:
        if self._role == CommunicationRole.CLIENT:
            self._client_state.send(event)

        elif self._role == CommunicationRole.SERVER:
            # response...
            ...

        if isinstance(event, Request):
            return b"%b / HTTP/1.1\r\n%b" % (
                self._to_bytes(event.method),
                event.headers._to_bytes() if event.headers else b"",
            )
        elif isinstance(event, Data):
            return event.data
        elif isinstance(event, EndOfMessage):
            return b""

        raise RuntimeError("Unknown event")
