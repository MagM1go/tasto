from typing import Protocol, Self

from tasto.protocol.api.buffer import ReceiveBufferContract
from tasto.protocol.api.events import Event


class State(Protocol):
    def feed(self, buffer: ReceiveBufferContract) -> tuple[Event, "State"]:
        """Pass data for the state"""
        ...
