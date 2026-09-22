from tasto.protocol.http11._abnf import request_line_re, status_line_re


def test_request_or_status_line_regexp() -> None:
    request_line = b"GET / HTTP/1.1"
    status_line = b"HTTP/1.1 200 OK"

    assert request_line_re.match(request_line)
    assert status_line_re.match(status_line)
