# type: ignore
# ruff: noqa
import ssl
import socket

# Tasto HTTP Protocol API
import tasto.headers as headers
import tasto.protocol as protocol

context = ssl.create_default_context()
sock = context.wrap_socket(
  socket.create_connection(("google.com", 443)), 
  server_hostname="google.com"
)

comm = protocol.Communication()
print(comm.messages.validate_header("GET / HTTP/1.1")) # True

# Sends an event; class Request(Event): ...
request_event = protocol.Request(
  method="GET", 
  uri=protocol.URI(
    scheme=protocol.Schemes.HTTPS,
    authority="google.com:443"
  ),
  headers=[headers.Header("Host", "google.com"), headers.Header("Connection", "close")]
)
sock.sendall(comm.send(request_event))

eof_event = protocol.EndOfMessage()
sock.sendall(comm.send(eof_event))

def wait_needed_event() -> protocol.Event:
  while True:
    event = comm.wait_event()

    if isinstance(event, protocol.Waiting):
      comm.put_data(sock.recv(4096))
      continue

    return event


while True:
  event = wait_needed_event()  
  print("received: ", event)
  if isinstance(event, protocol.EndOfMessage):
    break

sock.close()    