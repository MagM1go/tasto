from typing import override


class cistr(str):
    """Case-insensitive strings"""

    @override
    def __eq__(self, value: object, /) -> bool:
        if isinstance(value, str):
            return self.casefold() == value.casefold()

        return super().__eq__(value)

    @override
    def __contains__(self, key: object, /) -> bool:
        if isinstance(key, str):
            return key.lower() in self.lower()

        return key in self
