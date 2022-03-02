from ninas.requests import HelloRequest, MailUsersRequest, MailPayloadRequest
from ninas.responses import HelloResponse, MailUsersResponse
from ninas.utils import NinasRuntimeError
from ninas.security import EmailAddress
from ninas.network import NetworkTools
from ninas import console
import socket
import time
import sys
import ssl

# Get the arguments of the command line
src_email = sys.argv[2]
EmailAddress.assertValidAddress(src_email)
src_user_name , src_domain_name = src_email.split("@")

dst_email = sys.argv[3]
EmailAddress.assertValidAddress(dst_email)
dst_user_name , dst_domain_name = dst_email.split("@")

subject = sys.argv[4]
mail_file_name = sys.argv[5]



context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
context.load_cert_chain('./samples/' + src_email + '/keys/cert.pem', './samples/' + src_email + '/keys/key.pem')
context.load_verify_locations(cafile="./samples/keys/demoCA/cacert.pem")

init_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
sock = context.wrap_socket(init_sock,server_side=False, server_hostname='client.host')
try:
    sock.connect(('client.host', int(sys.argv[1])))
except ssl.SSLCertVerificationError as e:
    console.error("Error while checking server's certificate \n" + str(e))
except Exception as e:
    console.error(e)
    sys.exit(e.args[0])

print(sock.version())



# Create and send the HELLO request.
hello = HelloRequest(sock, src_domain_name)
hello.send()

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
        MailUsersRequest(sock, src_user_name, dst_user_name, dst_domain_name).send()
    elif obj_type == MailUsersResponse:
        MailPayloadRequest(sock, subject, time.time(), mail_file_name).send()
        break


print("Closing client...")
sock.close()
