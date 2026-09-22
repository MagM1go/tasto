from collections import deque
from typing import final

from tasto.protocol._state import CommunicationState
from tasto.protocol.api.buffer import ReceiveBufferContract
from tasto.protocol.api.events import Event
from tasto.protocol.http11._buffer import Buffer
from tasto.protocol.http11._events import (
    Data,
    MessageEnd,
    Request,
    Response,
    Waiting,
)
from tasto.protocol.role import Role


@final
class Communication:
    def __init__(self, role: Role) -> None:
        self._role = role
        self._state = CommunicationState(self._role)
        self._events: deque[Event] = deque()

        self._receive_buffer: ReceiveBufferContract = Buffer()

    def next_event(self) -> Event | None:
        if not self._events:
            return None

        return self._events.popleft()

    def send(self, event: Event) -> bytes:
        self._state.transition(event)

        
