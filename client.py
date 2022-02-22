from ninas.requests import HelloClientRequest
import socket
import sys

# Create the socket.
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#sock.bind(('client.host', 0)) # For development purpose only
sock.connect(('server.host', int(sys.argv[1])))

# Create and send the request.
hello = HelloClientRequest(sock, "ninas.client.host", "dmolina.fr")
hello.send()

while True: pass

hello.close()
