from typing import Protocol


class WriterStrategy(Protocol):
    def eom(self) -> None: ...
