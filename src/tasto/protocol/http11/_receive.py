from tasto.protocol.api import ReceiveBufferContract
from tasto.protocol.http11._abnf import CRLF


class _ReceiveBuffer(ReceiveBufferContract):    
    def __init__(self) -> None:
        self._buffer = bytearray()

    @property
    def buffer(self) -> bytearray:
        return self._buffer

    @buffer.setter
    def buffer(self) -> None:
        raise NotImplementedError()
        
    def put_data(self, data: bytes | bytearray) -> None:
        self._buffer += data

    def read_at_most(self, byte_count: int) -> bytes | None:
        data_chunk = self._buffer[:byte_count]
        if not data_chunk:
            return

        self._buffer = self._buffer[byte_count:]
        return bytes(data_chunk)

    def read_until_crlf(self) -> bytes | None:
        if CRLF not in self._buffer:
            return 

        line, buffer = self._buffer.split(CRLF, 1)
        self._buffer = buffer
        return bytes(line)
