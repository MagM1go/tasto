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
    authority="google.com"
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



comm = Communication(CLIENT)

sock.sendall(comm.create_message(Request("GET", "https://google.com", headers=[("Host", "www.google.com")])))
comm.signal_my_message_end()

while True:
  comm.receive(sock.recv(4096))
  
  while True:
    event = comm.next_event()

    if isinstance(event, MessageEnd):
      break

    # либо ожидаем полную сборку ответа
    if isinstance(event, Response):
      print(event.status)
      print(event.chunks[0].data)
      print(event.headers[0].name, event.headers[0].value)
      break

    # либо получаем каждый ивент по очереди
    if isinstance(event, Status):
      print(event.number, event.message)
      continue

    elif isinstance(event, Header):
      print(event.name, event.value)
      continue

    else:
      # значит вернулось None, а значит ивентов не будэ
      break
  
  break