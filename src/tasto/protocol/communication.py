import collections

from tasto.protocol.api.events import Event
from tasto.protocol.http11._events import EndOfMessage
from tasto.protocol._exceptions import NoEOM


class _StateMachine:
    def __init__(self) -> None:
        self._event_queue: collections.deque[Event] = collections.deque()

    def send(self, event: Event) -> None:
        self._event_queue.append(event)

    def next_event(self) -> Event | None:
        if len(self._event_queue) == 0:
            return None

        if not isinstance(self._event_queue[-1], EndOfMessage):
            raise NoEOM("Event queue has not End Of Message Event")

        return self._event_queue.popleft()


class Communication:
    def __init__(self) -> None:
        self._state = _StateMachine()

    def send(self, event: Event) -> bytes:
        ...
