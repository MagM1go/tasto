import re

request_line_re = re.compile(br"^([A-Z]+)\s+([^\s]+)\s+HTTP/(\d\.\d)\r?$")
status_line_re = re.compile(br"^HTTP/(\d(?:\.\d+)?)[ \t]+(\d{3})(?:[ \t]+([^\r\n]*))?\r?$")
