from collections import deque
from enum import StrEnum

from tasto.protocol.api.events import Event
from tasto.protocol.http11._receive import _ReceiveBuffer

from tasto.protocol.http11._events import ChunkBody, Finish, FinishHeaderSection, Header, HexChunkSize, MessageBodyEnd, MessageEnd, Request, Status


class CommunicationRole(StrEnum):
    CLIENT = "client"
    SERVER = "server"


class _ConnectionState(StrEnum):
    IDLE = "idle"
    SEND_BODY = "send_body"
    WAITING_RESPONSE = "waiting"
    DONE = "done"


STATES: dict[tuple[_ConnectionState, type[Event]], _ConnectionState] = {
    (_ConnectionState.IDLE, Request): _ConnectionState.SEND_BODY,
    (_ConnectionState.SEND_BODY, Finish): _ConnectionState.WAITING_RESPONSE,

    (_ConnectionState.WAITING_RESPONSE, Status): _ConnectionState.WAITING_RESPONSE,
    (_ConnectionState.WAITING_RESPONSE, Header): _ConnectionState.WAITING_RESPONSE,
    (_ConnectionState.WAITING_RESPONSE, FinishHeaderSection): _ConnectionState.WAITING_RESPONSE,
    (_ConnectionState.WAITING_RESPONSE, HexChunkSize): _ConnectionState.WAITING_RESPONSE,
    (_ConnectionState.WAITING_RESPONSE, ChunkBody): _ConnectionState.WAITING_RESPONSE,
    (_ConnectionState.WAITING_RESPONSE, MessageBodyEnd): _ConnectionState.WAITING_RESPONSE,
    (_ConnectionState.WAITING_RESPONSE, MessageEnd): _ConnectionState.DONE
}


class _StateMachine:
    def __init__(self) -> None:
        self._state: _ConnectionState = _ConnectionState.IDLE

    @property
    def state(self) -> _ConnectionState:
        return self._state

    def transition(self, event: Event) -> None:
        key = (self._state, type(event))
        self._state = STATES[key]


class Communication:
    def __init__(self, role: CommunicationRole) -> None:
        self._client_state = _StateMachine()
        self._role = role
        self._receive_buffer = _ReceiveBuffer()

        self._events: deque[Event] = deque()

    @property
    def my_role(self) -> CommunicationRole:
        return self._role

    @property
    def side_role(self) -> CommunicationRole:
        return next(filter(lambda x: x != self.my_role, CommunicationRole))

    def _cleanup(self) -> None:
        self._receive_buffer._buffer = bytearray()

    def create_message(self, event: Event) -> bytes:
        """Builds HTTP message like that:

        - https://www.rfc-editor.org/info/rfc9112/#name-message-format

        Here's a snippet from RFC.
        ```
        HTTP-message   = start-line CRLF
                         *( field-line CRLF )
                         CRLF
                         [ message-body ]
        ```
        """
        self._client_state.transition(event)

        

    def signal_my_message_end(self) -> None:
        self._client_state.transition(Finish())

        
        