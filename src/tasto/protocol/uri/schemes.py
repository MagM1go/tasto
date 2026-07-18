from enum import StrEnum


class Schemes(StrEnum):
    HTTP = "http"
    HTTPS = "https"

SCHEME_TO_PORT: dict[str, int] = {
    Schemes.HTTP: 80,
    Schemes.HTTPS: 443
}
