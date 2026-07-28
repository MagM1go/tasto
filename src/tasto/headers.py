"""
наверное будет по-другому... я тут играюсь
"""

from collections.abc import Iterator

from tasto.protocol.http11._abnf import CRLF


class Header:
    def __init__(self, *, name: str | None = None, value: str) -> None:
        self._key = name or self.__class__.__name__
        self._value = value

        self._pairs: list[tuple[str, str]] = [(self._key, self._value)]

    @classmethod
    def _from_pairs(cls, pairs: list[tuple[str, str]]) -> "Header":
        new = cls.__new__(cls)
        new._key = pairs[0][0]
        new._value = pairs[0][1]
        new._pairs = pairs

        return new

    def __add__(self, other: "Header") -> "Header":
        return self._from_pairs(self._pairs + other._pairs)

    def get_from_pair(self, name: str) -> Iterator[str]:
        return (value.strip() for key, value in self._pairs if key.lower() == name.lower())

    def first(self, name: str) -> str | None:
        try:
            return next(self.get_from_pair(name), None)
        except StopIteration:
            return

    def as_bytes(self) -> bytes:
        return CRLF.join([f"{key}: {value}".strip() for key, value in self._pairs]).encode()


class Host(Header): ...


class UserAgent(Header):
    def __init__(self, value: str) -> None:
        super().__init__(name="User-Agent", value=value)


class SetCookie(Header):
    def __init__(self, value: str) -> None:
        super().__init__(name="Set-Cookie", value=value)
