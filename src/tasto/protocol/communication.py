from collections import deque
from typing import final

from tasto.protocol._readers import HTTPMessageReaderStrategy
from tasto.protocol._state import CommunicationState, Role
from tasto.protocol._writers import HTTPMessageWriterStrategy
from tasto.protocol.api.buffer import ReceiveBufferContract
from tasto.protocol.api.events import Event
from tasto.protocol.http11._buffer import Buffer
from tasto.protocol.http11._events import Data, MessageEnd, Request, Response


@final
class Communication:
    def __init__(self, role: Role) -> None:
        self._role = role
        self._state = CommunicationState(self._role)
        self._events: deque[Event] = deque()

        self._writer_buffer: ReceiveBufferContract = Buffer()
        self._reader_buffer: ReceiveBufferContract = Buffer()

        self._writer = HTTPMessageWriterStrategy(self._writer_buffer)
        self._reader = HTTPMessageReaderStrategy(self._reader_buffer)

    def next_event(self) -> Event | None:
        if not self._events:
            return None

        return self._events.popleft()

    def create_message(self, event: Event) -> bytes:
        self._state.transition(event)
        self._events.append(event)

        if isinstance(event, Request):
            self._writer.write_request(event)

        elif isinstance(event, Response):
            self._writer.write_response(event)

        elif isinstance(event, Data):
            self._writer.write_chunk(
                chunk_size=len(event.data),
                chunk=event,
            )

        elif isinstance(event, MessageEnd):
            self._writer.write_eom()

        return self._writer_buffer.consume()
