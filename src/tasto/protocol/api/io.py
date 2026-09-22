from typing import Protocol


class Writer(Protocol):
    def write_line(self, line: bytes) -> None:
        """Write data line"""
        ...

    def write_eom_line(self) -> None:
        """Writes blank line or something"""
        ...


class Reader(Protocol): ...
