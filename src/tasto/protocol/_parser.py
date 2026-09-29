from typing import final

from tasto.protocol.api.buffer import ReceiveBufferContract


@final
class HTTPParser:
    def __init__(self, buffer: ReceiveBufferContract) -> None:
        self._buffer = buffer
