# TODO: Сделать так, чтобы стейт машина работала как стейт-машина, а не пропускала на прошлый шаг.
from typing import final, override

from tasto.protocol._exceptions import IllegalStatusLine, MalformedHeader
from tasto.protocol.api.buffer import ReceiveBufferContract
from tasto.protocol.api.events import Event
from tasto.protocol.api.state import State
from tasto.protocol.http11._abnf import status_line_re
from tasto.protocol.http11._events import WAITING, Data, MessageEnd, Request, Response


@final
class IdleState(State):
    is_available_step = True
    
    @override
    def switch(self, event: Event) -> "State":
        if isinstance(event, Request):
            self.is_available_step = False
            new_state = BodySendState()
            return new_state

        return DoneState()

    @override
    def feed(self, buffer: ReceiveBufferContract) -> tuple[Event, State]: ...


@final
class RequestLineState(State):
    is_available_step = False
    
    @override
    def switch(self, event: Event) -> "State": ...

    @override
    def feed(self, buffer: ReceiveBufferContract) -> tuple[Event, State]:
        request_line = buffer.read_until_crlf()
        if not request_line:
            return WAITING, self

        match = status_line_re.match(request_line)
        if not match:
            raise IllegalStatusLine(bytes(request_line))

        return HeaderState(
            http_version=match[3].decode("ascii"),
            http_status=None,
            message=None,
            target=match[2].decode("ascii"),
            method=match[1].decode("ascii"),
        ).feed(buffer)


@final
class StatusLineState(State):
    is_available_step = False
    
    @override
    def switch(self, event: Event) -> "State": ...

    @override
    def feed(self, buffer: ReceiveBufferContract) -> tuple[Event, State]:
        status_line = buffer.read_until_crlf()
        if not status_line:
            self.is_available_step = True
            return WAITING, self

        match = status_line_re.match(status_line)
        if not match:
            raise IllegalStatusLine(bytes(status_line))

        self.is_available_step = False
        message = match[3].decode("latin-1") if match[3] is not None else ""
        return HeaderState(
            http_version=match[1].decode("ascii"),
            http_status=match[2].decode("ascii"),
            message=message,
            method=None,
            target=None,
        ).feed(buffer)


@final
class HeaderState(State):
    is_available_step = False
    
    @override
    def switch(self, event: Event) -> "State": ...

    def __init__(
        self,
        http_version: str,
        *,
        target: str | None,
        method: str | None,
        http_status: str | None,
        message: str | None,
    ) -> None:
        self._http_version = http_version
        self._http_status = http_status
        self._message = message
        self._method = method
        self._target = target
        self._headers: list[tuple[str, str]] = []

    @property
    def method(self) -> str | None:
        return self._method

    # No
    # Shut up
    # You didn't see that
    def _content_body_type(self) -> str:
        result = "content-length"

        for key, value in self._headers:
            if key.lower() == "transfer-encoding" and value == "chunked":
                result = "transfer-encoding"

        return result

    # And this.
    def _content_length(self) -> int:
        return int(
            next(
                value for key, value in self._headers if key.lower() == "content-length"
            )
        )

    @override
    def feed(self, buffer: ReceiveBufferContract) -> tuple[Event, State]:
        while (line := buffer.read_until_crlf()) is not None:
            if bytes(line) == b"\r\n":
                if self.method is None:
                    body_state = (
                        ChunkedBodyState()
                        if self._content_body_type() == "transfer-encoding"
                        else ContentLengthBodyState(self._content_length())
                    )

                    body_state.is_available_step = True

                    assert self._http_status is not None
                    assert self._message is not None
                    return (
                        Response(
                            headers=self._headers,
                            http_version=self._http_version,
                            http_status=self._http_status,
                            message=self._message,
                        ),
                        body_state,
                    )
                else:
                    assert self._target is not None
                    body_send_state = BodySendState()
                    body_send_state.is_available_step = True

                    return (
                        Request(
                            method=self.method,
                            headers=self._headers,
                            http_version=self._http_version,
                            target=self._target,
                        ),
                        body_send_state,
                    )

            self.is_available_step = True
            key, separator, value = line[:-2].partition(b":")
            if not separator:
                raise MalformedHeader(bytes(line))

            self._headers.append(
                (key.strip().decode("ascii"), value.strip().decode("latin-1"))
            )

        return WAITING, self


@final
class BodySendState(State):
    is_available_step = False

    @override
    def switch(self, event: Event | None) -> "State":
        return StatusLineState()

    @override
    def feed(self, buffer: ReceiveBufferContract) -> tuple[Event, State]:
        return WAITING, self


@final
class ContentLengthBodyState(State):
    is_available_step = False
    
    def __init__(self, length: int) -> None:
        self._remaining_bytes = length

    @override
    def switch(self, event: Event) -> "State": ...

    @override
    def feed(self, buffer: ReceiveBufferContract) -> tuple[Event, State]:
        if self._remaining_bytes == 0:
            self.is_available_step = False
            return MessageEnd(), DoneState()

        body = buffer.read_at_most(self._remaining_bytes)
        if not body:
            self.is_available_step = True
            return WAITING, self

        self._remaining_bytes -= len(body)
        return Data(data=bytes(body)), self


@final
class ChunkedBodyState(State):
    is_available_step = False
    
    def __init__(self) -> None:
        self._remaining_bytes_in_chunk = 0
        self._is_expecting_crlf = False

    @override
    def switch(self, event: Event) -> "State": ...

    @override
    def feed(self, buffer: ReceiveBufferContract) -> tuple[Event, State]:
        if self._is_expecting_crlf:
            crlf = buffer.read_until_crlf()
            if not crlf:
                self.is_available_step = True
                return WAITING, self

            self._is_expecting_crlf = False

        if self._remaining_bytes_in_chunk == 0:
            chunk_length = buffer.read_until_crlf()
            if not chunk_length:
                self.is_available_step = True
                return WAITING, self

            hex_size = chunk_length.split(b";")[0].strip()
            try:
                self._remaining_bytes_in_chunk = int(hex_size, base=16)
            except ValueError:
                raise MalformedHeader(bytes(chunk_length))

            if self._remaining_bytes_in_chunk == 0:
                self.is_available_step = False
                return MessageEnd(), DoneState()

        chunk_data = buffer.read_at_most(self._remaining_bytes_in_chunk)
        if not chunk_data:
            self.is_available_step = True
            return WAITING, self

        self._remaining_bytes_in_chunk -= len(chunk_data)
        if self._remaining_bytes_in_chunk == 0:
            self._is_expecting_crlf = True

        return Data(data=bytes(chunk_data)), self


@final
class DoneState(State):
    is_available_step = False
    
    @override
    def switch(self, event: Event) -> "State": ...

    @override
    def feed(self, buffer: ReceiveBufferContract) -> tuple[Event, State]:
        return WAITING, self
