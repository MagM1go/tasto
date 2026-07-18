from tasto.protocol.uri.schemes import Schemes


class URI:
    def __init__(self, scheme: str | Schemes, authority: str) -> None:
        self.__class__