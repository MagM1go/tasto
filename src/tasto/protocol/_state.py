from enum import StrEnum
from typing import final

from tasto.protocol.api.events import Event
from tasto.protocol.http11._events import (
    ConnectionClosed,
    Data,
    InformationResponse,
    MessageEnd,
    Request,
    Response,
)
from tasto.protocol.role import Role


class State(StrEnum):
    IDLE = "idle"
    SEND_BODY = "send_body"
    SEND_RESPONSE = "send_response"
    RESPONSE_RECEIVED = "response_received"
    MUST_CLOSE = "must_close"
    CLOSE_CONNECTION = "close_connection"
    DONE = "done"


CLIENT_STATES = {
    State.IDLE: {Request: State.SEND_BODY, ConnectionClosed: State.CLOSE_CONNECTION},
    State.SEND_BODY: {Data: State.SEND_BODY, MessageEnd: State.DONE},
    State.DONE: {ConnectionClosed: State.CLOSE_CONNECTION},
    State.MUST_CLOSE: {ConnectionClosed: State.CLOSE_CONNECTION},
    State.CLOSE_CONNECTION: {ConnectionClosed: State.CLOSE_CONNECTION},
}

SERVER_STATES = {
    State.IDLE: {ConnectionClosed: State.CLOSE_CONNECTION, Response: State.SEND_BODY},
    State.SEND_RESPONSE: {
        InformationResponse: State.SEND_RESPONSE,
        Response: State.SEND_BODY,
    },
    State.SEND_BODY: {Data: State.SEND_BODY, MessageEnd: State.DONE},
    State.DONE: {ConnectionClosed: State.CLOSE_CONNECTION},
    State.MUST_CLOSE: {ConnectionClosed: State.CLOSE_CONNECTION},
    State.CLOSE_CONNECTION: {ConnectionClosed: State.CLOSE_CONNECTION},
}

STATES = {Role.CLIENT: CLIENT_STATES, Role.SERVER: SERVER_STATES}


@final
class CommunicationState:
    def __init__(self, role: Role) -> None:
        self._keep_alive = True
        self._current_states: dict[Role, State] = {
            Role.CLIENT: State.IDLE,
            Role.SERVER: State.IDLE,
        }

        self._role = role

    @property
    def keep_alive(self) -> bool:
        return self._keep_alive

    @property
    def current(self) -> State:
        return self._current_states[self._role]

    def transition(self, event: Event) -> None:
        event = type(event)

        if not self._keep_alive:
            for role in Role:
                if self._current_states[role] == State.DONE:
                    self._current_states[role] = State.MUST_CLOSE

        current_state_for_role = STATES[self._role][self._current_states[self._role]]
        self._current_states[self._role] = current_state_for_role[event]  # type: ignore[index] # pyright: ignore[reportArgumentType]
    