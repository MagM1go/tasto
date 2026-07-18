from enum import StrEnum


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
    