from ninas.requests import HelloRequest, MailUsersRequest, MailPayloadRequest
from ninas.responses import HelloResponse, MailUsersResponse
from ninas.connection import ClientConnection, HandlingLoop
from ninas.security import EmailAddress
import time
import sys

NINAS_PORT = int(sys.argv[1])
IMAP_PORT  = int(sys.argv[2])

# Get the source email address.
src_email = sys.argv[3]
EmailAddress.assertValidAddress(src_email)
src_user_name, src_domain_name = src_email.split("@")

# Get the destination email address.
dst_email = sys.argv[4]
EmailAddress.assertValidAddress(dst_email)
dst_user_name, dst_domain_name = dst_email.split("@")

# Get the other command line parameters.
subject        = sys.argv[5]
mail_file_name = sys.argv[6]

# Create the connection.
connection = ClientConnection(src_email + '/keys', 'client.host')
connection.start(NINAS_PORT)

# Create and send the HELLO request.
HelloRequest(connection.socket, src_domain_name).send()

# Handle the network object after their
# internal handle() method.
def handler(obj, obj_type):
    # The client first contact response.
    if obj_type == HelloResponse:
        MailUsersRequest(obj.socket, src_user_name, dst_user_name, dst_domain_name).send()
        
    # A simple ACK response after users data sent.
    elif obj_type == MailUsersResponse:
        MailPayloadRequest(obj.socket, subject, time.time(), mail_file_name).send()
        return False

    return True

HandlingLoop(handler).fromSocket(connection.socket).run()
