from typing import Protocol, runtime_checkable


@runtime_checkable
class Event(Protocol):
    __slots__: tuple[str, ...] = ()
