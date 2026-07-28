from enum import IntEnum, StrEnum


class HTTPMethod(StrEnum):
    GET = "GET"
    """Transfer a current representation of the target resource."""
    
    HEAD = "HEAD"
    """Same as GET, but only transfer the status line and header section."""
    
    POST = "POST"
    """Perform resource-specific processing on the request payload."""
    
    PUT = "PUT"
    """Replace all current representations of the target resource with the request payload."""
    
    DELETE = "DELETE"
    """Remove all current representations of the target resource."""
    
    CONNECT = "CONNECT"
    """Establish a tunnel to the server identified by the target resource."""
    
    OPTIONS = "OPTIONS"
    """Describe the communication options for the target resource."""
    
    TRACE = "TRACE"
    """Perform a message loop-back test along the path to the target resource."""
    
    QUERY = "QUERY"
    """Initiate a query on the target resource using the request payload
    
    Unlike POST, QUERY is safe and idempotent: it can be cached,
    retried, and repeated without side effects.
    """


# https://datatracker.ietf.org/doc/html/rfc7231#section-6.2.1
class HTTPStatus(IntEnum):
    CONTINUE = 100
    SWITCHING_PROTOCOL = 101

    OK = 200
    CREATED = 201
    ACCEPTED = 202
    NON_AUTHORITATIVE_INFORMATION = 203
    NO_CONTENT = 204
    RESET_CONTENT = 205
    PARTIAL_CONTENT = 206

    MULTIPLE_CHOICES = 300
    MOVED_PERMANENTLY = 301
    FOUND = 302
    SEE_OTHER = 303
    NOT_MODIFIED = 304
    USE_PROXY = 305
    TEMPORARY_REDIRECT = 307

    BAD_REQUEST = 400
    UNAUTHORIZED = 401
    PAYMENT_REQUIRED = 402
    FORBIDDEN = 403
    NOT_FOUND = 404
    METHOD_NOT_ALLOWED = 405
    NOT_ACCEPTABLE = 406
    PROXY_AUTHENTICATION_REQUIRED = 407
    REQUEST_TIMEOUT = 408
    CONFLICT = 409
    GONE = 410
    LENGTH_REQUIRED = 411
    PRECONDITION_FAILED = 412
    PAYLOAD_TOO_LARGE = 413
    URI_TOO_LONG = 414
    UNSUPPORTED_MEDIA_TYPE = 415
    RANGE_NOT_SATISFIABLE = 416
    EXPECTATION_FAILED = 417
    UPGRADE_REQUIRED = 426

    INTERNAL_SERVER_ERROR = 500
    NOT_IMPLEMENTED = 501
    BAD_GATEWAY = 502
    SERVICE_UNAVAILABLE = 503
    GATEWAY_TIMEOUT = 504
    HTTP_VERSION_NOT_SUPPORTED = 505

    def __bytes__(self, value: int) -> bytes:
       return bytes(value) 
    