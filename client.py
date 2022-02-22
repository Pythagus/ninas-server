from ninas.requests import HelloServerRequest
from ninas.network import NetworkTools
import socket
import sys

# Create the socket.
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.bind(('client.host', 0)) # For development purpose only
sock.connect(('server.host', int(sys.argv[1])))

# Create and send the HELLO request.
hello = HelloServerRequest(sock, "ninas.client.host", "dmolina.fr")
hello.send()



while True:
    response = NetworkTools.receiveNetworkObject(sock)
    print(response)
    response.handle()

hello.close()
