from collections import deque
from typing import final

from tasto.protocol._state import IdleState
from tasto.protocol.api.buffer import ReceiveBufferContract
from tasto.protocol.api.events import Event
from tasto.protocol.api.state import State
from tasto.protocol.http11._buffer import Buffer
from tasto.protocol.http11._events import Data, MessageEnd, Request
from tasto.protocol.role import Role


@final
class Communication:
    def __init__(self, role: Role) -> None:
        self._state: State = IdleState()

        self._role = role
        self._events: deque[Event] = deque()

        self._receive_buffer: ReceiveBufferContract = Buffer()

        self._previous_state: State | None = None
        self._start_new_state_cycle = False

    def next_event(self) -> Event | None:
        if not self._events:
            return None

        return self._events.popleft()

    def send(self, event: Event) -> bytes:
        self._state.switch(event)  # pyright: ignore[reportUnusedCallResult]

        # build bytes
        data = ""
        if isinstance(event, Request):
            data += f"{event.method} {event.target} HTTP/{event.http_version}\r\n"

            for header in event.headers:
                key, value = header

                data += f"{key.strip().lower()}: {value.strip()}\r\n"

            data += "\r\n"

        elif isinstance(event, Data):
            data += event.data.decode("utf8") + "\r\n"
            
        return data.encode("ascii")

    def feed(self, data: bytes) -> Event:
        self._receive_buffer.feed(data)

        