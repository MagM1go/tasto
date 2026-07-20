from dataclasses import dataclass, field

from tasto.protocol.uri.schemes import SCHEME_TO_PORT, Schemes
from tasto.protocol._exceptions import MalformedAuthority, MalformedURI, UnsupportedScheme

from tasto.protocol.uri._abnf import RFC3986_URI_REGEX

# https://datatracker.ietf.org/doc/html/rfc3986#section-3
@dataclass(frozen=True, slots=True, kw_only=True)
class Authority:
    user_information: str | None = field(default=None)
    host: str
    port: int

    def __str__(self) -> str:
        if self.user_information:
            return f"{self.user_information}@{self.host}:{self.port}"

        return f"{self.host}:{self.port}"

# TODO:
#   - IPv6 support;
#   - Fully support for RFC 3986, Section 3: https://datatracker.ietf.org/doc/html/rfc3986#section-3
#   - Include Path and Query to the URI
class URI:
    _SLASH = "/"

    def __init__(self, scheme: str | Schemes, authority: str | Authority, path: str = _SLASH, query: str | None = None) -> None:
        self.scheme = scheme.lower()

        available = ", ".join(m.value for m in Schemes)
        if not self.scheme or not self.scheme.strip():
            raise MalformedURI(f"Choose scheme. Available: {available}")
            
        if self.scheme not in Schemes:
            raise UnsupportedScheme(f"Unknown scheme: {self.scheme.upper()}. Available: {available}")

        self.authority: Authority = self._build_authority(authority)

        self.path = path
        self.query = query

    def __str__(self) -> str:
        path_str = self.path if self.path != self._SLASH else ""

        result = f"{self.scheme}://{self.authority}{path_str}"
        if self.query:
            result += f"?{self.query}"

        return result

    def __repr__(self) -> str:
        return f"URI(scheme={self.scheme}, authority={self.authority}, path={self.path}, query={self.query})"

    def _build_authority(self, authority: str | Authority) -> Authority:
        if isinstance(authority, Authority):
            return authority

        if "@" in authority:
            user_information, host_and_port = authority.split("@", 1)
        else:
            user_information, host_and_port = None, authority

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


def parse_uri_from_string(uri: str | URI) -> URI:
    if isinstance(uri, URI):
        return uri

    url = RFC3986_URI_REGEX.match(uri)
    if not url:
        raise MalformedURI(f"Wrong URI: {uri}")

    scheme, authority, path, query = (
        url.group(2) or "",
        url.group(4) or "",
        url.group(5) or "",
        url.group(7)
    )
    return URI(
        scheme=scheme,
        authority=authority,
        path=path,
        query=query
    )
