from ninas.requests import HelloClientRequest
import socket

# Create the socket.
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect(('localhost', 8090))

# Create and send the request.
hello = HelloClientRequest(sock, "smtp.gmail.com", "enfoiros.org")
hello.send()
hello.close()
