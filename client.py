from ninas.responses import HelloServerResponse
from ninas.requests import HelloServerRequest, MailFromRequest
from ninas.utils import NinasRuntimeError
from ninas.network import NetworkTools
from ninas import console
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
    obj = NetworkTools.receiveNetworkObject(sock)
    obj_type = type(obj)
    
    # Try to handle the network object.
    try:
        obj.handle()
    except NinasRuntimeError as e:
        console.warn(e)
        obj.close()
    
    # The client first contact response.
    if obj_type == HelloServerResponse:
        MailFromRequest(sock, "elies", "dmolina.fr").send()