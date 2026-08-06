from tasto.protocol._exceptions import InvalidSize
from tasto.protocol.api import ReceiveBufferContract
from tasto.protocol.api.readers import ReaderStrategy
from tasto.protocol.http11._events import Data, Request, Response, Waiting


class _HeaderReader(ReaderStrategy):
    def __init__(self, buffer: ReceiveBufferContract) -> None:
        self.buffer: ReceiveBufferContract = buffer

    def __call__(self) -> list[tuple[str, str]]:
        headers: list[tuple[str, str]] = []

        while True:
            header = self.buffer.read_until_crlf()

            if header == b"":
                break

            key, value = header.decode().strip().split(":", 1)
            headers.append((key.strip().lower(), value.strip()))

        return headers


class _ContentLengthReader(ReaderStrategy):
    def __init__(self, length: int, buffer: ReceiveBufferContract) -> None:
        self.buffer: ReceiveBufferContract = buffer
        self.length: int = length

    def read(self) -> Data:
        if data := self.buffer.read_at_most(self.length):
            return Data(data=data)

        raise InvalidSize()


class _TransferEncodingChunked(ReaderStrategy):
    def __init__(self, buffer: ReceiveBufferContract) -> None:
        self.buffer: ReceiveBufferContract = buffer

    def read_chunk(self, size: int) -> Data | Waiting:
        chunk_data = self.buffer.read_at_most(size)

        if chunk_data is None:
            raise InvalidSize("Invalid chunk body")

        if len(chunk_data) < size or len(chunk_data) > size:
            raise InvalidSize("Chunk size != len(chunk data)")

        return Data(data=chunk_data)


class HTTPMessageReaderStrategy(ReaderStrategy):
    def __init__(self, buffer: ReceiveBufferContract) -> None:
        self._buffer: ReceiveBufferContract = buffer

    def read_request(self) -> Request:
        request_line = self._buffer.read_until_crlf()
        method, target, version = request_line.decode().strip().split(" ")
        headers = _HeaderReader(self._buffer)()

        return Request(
            method=method, target=target, headers=headers, http_version=version
        )

    def read_response(self) -> Response:
        status_line = self._buffer.read_until_crlf()
        version, status, message = status_line.decode().strip().split(" ")
        headers = _HeaderReader(self._buffer)()

        return Response(
            http_status=status,
            message=message,
            http_version=version,
            headers=headers,
        )

    def read_full(self, length: int) -> Data:
        return _ContentLengthReader(length, self._buffer).read()

    def read_chunk(self, size: int) -> Data | Waiting:
        return _TransferEncodingChunked(self._buffer).read_chunk(size)
