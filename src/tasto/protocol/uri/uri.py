from dataclasses import dataclass, field

from tasto.protocol.uri.schemes import SCHEME_TO_PORT, Schemes
from tasto.protocol._exceptions import MalformedAuthority, UnsupportedScheme

# https://datatracker.ietf.org/doc/html/rfc3986#section-3
@dataclass(frozen=True, slots=True, kw_only=True)
class Authority:
    user_information: str | None = field(default=None)
    host: str
    port: int

    def __repr__(self) -> str:
        if self.user_information:
            return f"{self.user_information}@{self.host}:{self.port}"

        return f"{self.host}:{self.port}"

class URI:
    def __init__(self, scheme: str | Schemes, authority: Authority | str, path: str | None = None, query: str | None = None) -> None:
        self.scheme = scheme.lower()

        if self.scheme not in Schemes:
            raise UnsupportedScheme(f"Unknown scheme: {self.scheme.upper()}. Available: {', '.join(Schemes._member_names_)}")

        self.authority = authority

        if isinstance(self.authority, str):
            self.authority = self._build_authority()

        self.path = path
        self.query = query

    def __repr__(self) -> str:
        return f"URI(scheme={self.scheme}, authority={self.authority})"

    def _build_authority(self) -> Authority:
        if isinstance(self.authority, Authority):
            return self.authority

        if "@" in self.authority:
            user_information, host_and_port = self.authority.split("@", 1)
        else:
            user_information, host_and_port = None, self.authority

        if ":" in host_and_port:
            host, port = host_and_port.split(":")
            try:
                port = int(port)
            except ValueError:
                raise MalformedAuthority(f"Invalid port: {port}")
        else:
            host, port = host_and_port, SCHEME_TO_PORT[self.scheme]

        if not host:
            raise MalformedAuthority("Empty host")

        return Authority(
            user_information=user_information,
            host=host,
            port=port
        )
