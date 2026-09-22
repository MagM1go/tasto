# First of all, we want to:
# - find first \r\n or \r\n\r\n
# - read at-most-N bytes of data
# 
# reading until first blank line is found or no CRLF found
# blank line is like \n\r\n<no data>\r\n
# 
# That's buffer so we need to remove cosumed data, keep it in mind

from typing import Protocol


class ReceiveBufferContract(Protocol):
    def feed(self, data: bytes | bytearray) -> None:
        """Feeds buffer"""
        ...
        
    def read_until_crlf(self) -> bytearray | None:
        """Finding for the first CRLF"""
        ...

    def read_at_most(self, count: int) -> bytearray | None:
        """Read exactly `count` bytes"""
        ...

    def read_lines(self) -> list[bytearray]:
        """Read all lines from buffer"""
        ...
