from ninas.network import createNetworkInstance, NetworkPacket, receiveBytes
from ninas.requests import HelloServerRequest
import socket
import json
import sys

# Create the socket.
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.bind(('client.host', 0)) # For development purpose only
sock.connect(('server.host', int(sys.argv[1])))

# Create and send the request.
hello = HelloServerRequest(sock, "ninas.client.host", "dmolina.fr")
hello.send()


while True:
    buf  = receiveBytes(sock, NetworkPacket.SIZE_LENGTH, b"")
    size = int(buf)
    buf  = receiveBytes(sock, size, buf)

    packet = NetworkPacket.unserialize(buf)

    response = createNetworkInstance(sock, json.loads(packet.payload))

    print(response)
    response.handle()

hello.close()
