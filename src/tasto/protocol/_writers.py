from tasto.protocol.api.receive import ReceiveBufferContract
from tasto.protocol.api.writers import WriterStrategy
from tasto.protocol.http11._abnf import CRLF
from tasto.protocol.http11._events import ChunkBody, Request, Response, Status


class _ContentLengthWriter(WriterStrategy):
    def __init__(self, buffer: ReceiveBufferContract) -> None:
        self.buffer = buffer

    def __call__(self, chunk_size: int, chunk: ChunkBody) -> None:
        # self.declared_size = chunk_size

        self.buffer.put_data(chunk.data[:chunk_size])

    def eom(self) -> None:
        pass


class _TransferEncodingChunkedWriter(WriterStrategy):
    def __init__(self, buffer: ReceiveBufferContract) -> None:
        self.buffer = buffer

    def __call__(self, chunk_size: int, chunk: ChunkBody) -> None:
        chunk_body = chunk.data[:chunk_size]

        if not chunk_body:
            return

        self.buffer.put_data(f"{chunk_size:x}\r\n".encode())

        if chunk_size > 0:
            self.buffer.put_data(chunk_body)

        self.buffer.put_data(b"\r\n")

    def eom(self) -> None:
        self.buffer.put_data(b"0\r\n\r\n")


# TODO: https://www.rfc-editor.org/info/rfc9112/#section-11.1
class HTTPMessageWriterStrategy(WriterStrategy):
    def __init__(self, buffer: ReceiveBufferContract) -> None:
        self.buffer = buffer

        self._internal_writer = None

    def _get_headers(self, headers: list[tuple[str, str]]) -> bytes:
        result = ""
        for header in headers:
            key, value = header

            result += f"{key.lower()}: {value}{CRLF}"

        result += CRLF
        return result.encode()

    def write_status_line(self, status: Status) -> None:
        self.buffer.put_data(
            b"%b %b %b\r\n"
            % (
                status.version,
                status.number,
                status.message,
            )
        )

    def write_request_line(self, request: Request) -> None:
        self.buffer.put_data(
            b"%b %b %b\r\n"
            % (request.method, request.uri.path_and_query, request.http_version)
        )

    def write_headers(self, headers: list[tuple[str, str]]) -> None:
        self.buffer.put_data(self._get_headers(headers))

    def write_request(self, request: Request) -> None:
        self.write_request_line(request)
        self.write_headers(request.headers)

    def write_chunk(
        self,
        writer: _ContentLengthWriter | _TransferEncodingChunkedWriter,
        chunk_size: int,
        chunk: ChunkBody,
    ) -> None:
        writer(chunk_size, chunk)

    def write_response(self, response: Response) -> None:
        if any(h[0].lower() == "transfer-encoding" for h in response.headers):
            self._internal_writer = _TransferEncodingChunkedWriter(self.buffer)
        else:
            self._internal_writer = _ContentLengthWriter(self.buffer)

        self.write_status_line(response.status)
        self.write_headers(response.headers)

        for chunk in response.chunks:
            self.write_chunk(self._internal_writer, len(chunk.data), chunk)

        self.eom()

    def eom(self) -> None:
        if self._internal_writer is not None:
            self._internal_writer.eom()
