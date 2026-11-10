import abc

from tasto.protocol._exceptions import UnexpectedState
from tasto.protocol.api.buffer import ReceiveBufferContract
from tasto.protocol.api.events import Event


class State(abc.ABC):
    is_available_step: bool

    @abc.abstractmethod
    def switch(self, event: Event) -> "State": ...


    @abc.abstractmethod
    def feed(self, buffer: ReceiveBufferContract) -> tuple[Event, "State"]:
        """Pass data for the state"""
        ...
