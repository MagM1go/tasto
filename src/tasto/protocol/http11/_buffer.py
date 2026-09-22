from typing import final, override

from tasto.protocol.api import ReceiveBufferContract


@final
class Buffer(ReceiveBufferContract):
    def __init__(self) -> None:
        self._bytebuffer = bytearray()

        self._crlf_search_index = 0
        self._crlf_search_for_multiple_index = 0

    def _consume(self, count: int) -> bytearray:
        data = self._bytebuffer[:count]
        del self._bytebuffer[:count]

        return data

    @override
    def feed(self, data: bytes | bytearray) -> None:
        self._bytebuffer += data

    @override
    def read_at_most(self, count: int) -> bytearray | None:
        data = self._consume(count)

        if not data:
            return None

        return data

    @override
    def read_until_crlf(self) -> bytearray | None:
        start_index = max(0, self._crlf_search_index)
        first_crlf_index = self._bytebuffer.find(b"\r\n", start_index - 1)

        if first_crlf_index == -1:
            self._crlf_search_index = len(self._bytebuffer)
            return None

        return self._consume(first_crlf_index + 2)

    @override
    def read_lines(self) -> list[bytearray]:
        lines: list[bytearray] = []

        while (data := self.read_until_crlf()) is not None:
            lines.append(data)

        return lines
