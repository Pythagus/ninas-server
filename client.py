from ninas.requests import HelloServerRequest, MailUsersRequest, MailPayloadRequest
from ninas.responses import HelloServerResponse, MailUsersResponse
from ninas.utils import NinasRuntimeError
from ninas.network import NetworkTools
from ninas import console
import socket
import time
import sys



# Create the socket.
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.bind(('client.host', 0)) # For development purpose only
sock.connect(('server.host', int(sys.argv[1])))


# Create and send the HELLO request.
hello = HelloServerRequest(sock, "ninas.client.host", "dmolina.fr")
hello.send()

# Get the arguments of the command line 
dst_user_name , dst_domain_name = sys.argv[2].split("@")
subject = sys.argv[3]
mail_file_name = sys.argv[4]




while True:
    obj = NetworkTools.receiveNetworkObject(sock)
    obj_type = type(obj)
    
    # Try to handle the network object.
    try:
        obj.handle()
    except NinasRuntimeError as e:
        console.warn(e)
        break
    
    # The client first contact response.
    if obj_type == HelloServerResponse:
        MailUsersRequest(sock, "elies", dst_user_name, dst_domain_name).send()
    elif obj_type == MailUsersResponse:
        MailPayloadRequest(sock, subject, time.time(), mail_file_name).send()
        break

print("Closing client...")
sock.close()
