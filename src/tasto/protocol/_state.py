from typing import final, override

from tasto.protocol._exceptions import IllegalStatusLine, MalformedHeader
from tasto.protocol.api.buffer import ReceiveBufferContract
from tasto.protocol.api.events import Event
from tasto.protocol.api.state import State
from tasto.protocol.http11._abnf import status_line_re
from tasto.protocol.http11._events import WAITING, Data, MessageEnd, Response


@final
class ServerStatusLineState(State):
    @override
    def feed(self, buffer: ReceiveBufferContract) -> tuple[Event, State]:
        status_line = buffer.read_until_crlf()
        if not status_line:
            return WAITING, self

        match = status_line_re.match(status_line)
        if not match:
            raise IllegalStatusLine(bytes(status_line))

        message = match[3].decode("latin-1") if match[3] is not None else ""
        return ServerHeaderState(
            http_version=match[1].decode("ascii"),
            http_status=match[2].decode("ascii"),
            message=message,
        ).feed(buffer)


@final
class ServerHeaderState(State):
    def __init__(self, http_version: str, http_status: str, message: str) -> None:
        self._http_version = http_version
        self._http_status = http_status
        self._message = message
        self._headers: list[tuple[str, str]] = []

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
                body_state = (
                    ChunkedBodyState()
                    if self._content_body_type() == "transfer-encoding"
                    else ContentLengthBodyState(self._content_length())
                )
                return (
                    Response(
                        headers=self._headers,
                        http_version=self._http_version,
                        http_status=self._http_status,
                        message=self._message,
                    ),
                    body_state,
                )

            key, separator, value = line[:-2].partition(b":")
            if not separator:
                raise MalformedHeader(bytes(line))

            self._headers.append(
                (key.strip().decode("ascii"), value.strip().decode("latin-1"))
            )

        return WAITING, self


@final
class ContentLengthBodyState(State):
    def __init__(self, length: int) -> None:
        self._remaining_bytes = length

    @override
    def feed(self, buffer: ReceiveBufferContract) -> tuple[Event, State]:
        if self._remaining_bytes == 0:
            return MessageEnd(), DoneState()

        body = buffer.read_at_most(self._remaining_bytes)
        if not body:
            return WAITING, self

        self._remaining_bytes -= len(body)
        return Data(data=bytes(body)), self


@final
class ChunkedBodyState(State):
    def __init__(self) -> None:
        self._remaining_bytes_in_chunk = 0
        self._is_expecting_crlf = False

    @override
    def feed(self, buffer: ReceiveBufferContract) -> tuple[Event, State]:
        if self._is_expecting_crlf:
            crlf = buffer.read_until_crlf()
            if not crlf:
                return WAITING, self

            self._is_expecting_crlf = False

        if self._remaining_bytes_in_chunk == 0:
            chunk_length = buffer.read_until_crlf()
            if not chunk_length:
                return WAITING, self

            hex_size = chunk_length.split(b";")[0].strip()
            try:
                self._remaining_bytes_in_chunk = int(hex_size, base=16)
            except ValueError:
                raise MalformedHeader(bytes(chunk_length))

            if self._remaining_bytes_in_chunk == 0:
                return MessageEnd(), DoneState()

        chunk_data = buffer.read_at_most(self._remaining_bytes_in_chunk)
        if not chunk_data:
            return WAITING, self

        self._remaining_bytes_in_chunk -= len(chunk_data)
        if self._remaining_bytes_in_chunk == 0:
            self._is_expecting_crlf = True

        return Data(data=bytes(chunk_data)), self


@final
class DoneState(State):
    @override
    def feed(self, buffer: ReceiveBufferContract) -> tuple[Event, State]:
        return MessageEnd(), self
