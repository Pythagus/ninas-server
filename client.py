from ninas.requests import HelloRequest, MailUsersRequest, MailPayloadRequest
from ninas.responses import HelloResponse, MailUsersResponse
from ninas.utils import NinasRuntimeError
from ninas.security import EmailAddress
from ninas.network import NetworkTools
from ninas import console
import socket
import time
import sys



# Create the socket.
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect(('client.host', int(sys.argv[1])))


# Create and send the HELLO request.
hello = HelloRequest(sock, "dmolina.fr")
hello.send()

# Get the arguments of the command line
email = sys.argv[2]
EmailAddress.assertValidAddress(email)
dst_user_name , dst_domain_name = email.split("@")

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
    if obj_type == HelloResponse:
        MailUsersRequest(sock, "elies", dst_user_name, dst_domain_name).send()
    elif obj_type == MailUsersResponse:
        MailPayloadRequest(sock, subject, time.time(), mail_file_name).send()
        break


print("Closing client...")
sock.close()
