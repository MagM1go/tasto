from typing import override

from tasto.protocol.api.buffer import ReceiveBufferContract
from tasto.protocol.api.writers import WriterStrategy
from tasto.protocol.http11._abnf import CRLF
from tasto.protocol.http11._events import Data, Request, Response


class _ContentLengthWriter(WriterStrategy):
    def __init__(self, buffer: ReceiveBufferContract) -> None:
        self.buffer: ReceiveBufferContract = buffer

    def __call__(self, chunk_size: int, chunk: Data) -> None:
        self.buffer.put_data(chunk.data[:chunk_size])

    @override
    def write_eom(self) -> None:
        pass


class _TransferEncodingChunkedWriter(WriterStrategy):
    def __init__(self, buffer: ReceiveBufferContract) -> None:
        self.buffer: ReceiveBufferContract = buffer

    def __call__(self, chunk_size: int, chunk: Data) -> None:
        chunk_body = chunk.data[:chunk_size]

        if not chunk_body:
            return

        self.buffer.put_data(f"{chunk_size:x}\r\n".encode())
        self.buffer.put_data(chunk_body)
        self.buffer.put_data(b"\r\n")

    @override
    def write_eom(self) -> None:
        self.buffer.put_data(b"0\r\n\r\n")


# TODO: https://www.rfc-editor.org/info/rfc9112/#section-11.1
class HTTPMessageWriterStrategy(WriterStrategy):
    def __init__(self, buffer: ReceiveBufferContract) -> None:
        self.buffer: ReceiveBufferContract = buffer

        self._internal_writer: _TransferEncodingChunkedWriter | _ContentLengthWriter = (
            _ContentLengthWriter(self.buffer)
        )

    def _get_headers(self, headers: list[tuple[str, str]]) -> bytes:
        grouped_headers: dict[str, list[str]] = {}
        set_cookies: list[str] = []

        for key, value in headers:
            key_lower = key.lower()

            if key_lower == "set-cookie":
                set_cookies.append(value)
            else:
                grouped_headers.setdefault(key_lower, []).append(value)

        lines: list[str] = []
        for key, values in grouped_headers.items():
            lines.append(f"{key}: {', '.join(values)}")

        for value in set_cookies:
            lines.append(f"set-cookie: {value}")

        result = "".join(f"{line}{CRLF}" for line in lines) + CRLF
        return result.encode()

    def write_status_line(self, http_version: str, status: str, message: str) -> None:
        self.buffer.put_data(
            b"%b %b %b\r\n"
            % (
                http_version.encode(),
                status.encode(),
                message.encode(),
            )
        )

    def write_request_line(self, request: Request) -> None:
        self.buffer.put_data(
            b"%b %b %b\r\n"
            % (
                request.method.encode(),
                request.target.encode(),
                request.http_version.encode(),
            )
        )

    def write_headers(self, headers: list[tuple[str, str]]) -> None:
        self.buffer.put_data(self._get_headers(headers))

    def predict_writer_strategy(self, headers: list[tuple[str, str]]) -> None:
        if any(h[0].lower() == "transfer-encoding" for h in headers):
            self._internal_writer = _TransferEncodingChunkedWriter(self.buffer)
        else:
            self._internal_writer = _ContentLengthWriter(self.buffer)

    def write_request(self, request: Request) -> None:
        self.write_request_line(request)
        self.write_headers(request.headers)

    # если придут слишком большие хедеры а окно получения будет меньше, то будет бабах. Та же история с status_line
    def write_response(self, response: Response) -> None:
        self.predict_writer_strategy(response.headers)
        self.write_status_line(
            response.http_version, response.http_status, response.message
        )
        self.write_headers(response.headers)

    def write_chunk(
        self,
        chunk_size: int,
        chunk: Data,
    ) -> None:
        self._internal_writer(chunk_size, chunk)

    @override
    def write_eom(self) -> None:
        self._internal_writer.write_eom()
