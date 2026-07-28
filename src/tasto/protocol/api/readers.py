from typing import Protocol


class ReaderStrategy(Protocol):
    __slots__ = ("buffer",)
