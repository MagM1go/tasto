from tasto.protocol._exceptions import CRLFNotFound
from tasto.protocol.api import ReceiveBufferContract
from tasto.protocol.http11._abnf import CRLF


class _ReceiveBuffer(ReceiveBufferContract):
    def __init__(self) -> None:
        self._crlf = CRLF.encode()
        self._buffer = bytearray()

    @property
    def buffer(self) -> bytearray:
        return self._buffer

    @buffer.setter
    def buffer(self) -> None:
        raise NotImplementedError()

    def is_empty(self) -> bool:
        return not self._buffer

    # TODO:
    #   - Clear wrong CRLFs;
    #   - Fix LF problem
    #   - And um whole https://www.rfc-editor.org/info/rfc9112/#section-11 ...
    #
    # !!!!!!!!!!!! THIS IS JUST PROOF OF WORK PURPOSES NOT PROD READY !!!!!!!!!!!!
    def put_data(self, data: bytes) -> None:
        # if not data.endswith(2 * CRLF):
        #     data += 2 * CRLF

        self._buffer += data

    def read_at_most(self, byte_count: int) -> bytes | None:
        data_chunk = self._buffer[:byte_count]
        if not data_chunk:
            return

        self._buffer = self._buffer[byte_count:]
        return bytes(data_chunk)

    def read_until_crlf(self) -> bytes | None:
        if self._crlf not in self._buffer:
            return

        line, buffer = self._buffer.split(self._crlf, 1)
        self._buffer = buffer
        return bytes(line)

    def read_eom(self) -> None:
        if self.read_at_most(2) != CRLF:
            raise CRLFNotFound()
