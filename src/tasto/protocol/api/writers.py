from typing import Protocol


class WriterStrategy(Protocol):
    def write_eom(self) -> None: ...
