from ninas.responses import HelloServerResponse, HelloResponse, MailPayloadResponse, MailUsersResponse
from ninas.requests import HelloRequest, HelloServerRequest, MailUsersRequest, MailPayloadRequest
from ninas.connection import ClientConnection, Server
from ninas.utils import MailInfo
from ninas import console
from ninas import imap
import sys


# Current server data.
HOST, NINAS_PORT, IMAP_PORT = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])


# Handling NINAS server packets.
def ninas_handler(obj, obj_type, mail, tcp_handler):
    # Server as a dst  server
    if obj_type == HelloServerRequest:
        HelloServerResponse(obj.socket).send()

    # Server as an src server
    elif obj_type == HelloServerResponse:
        MailUsersRequest(obj.socket, mail.src_user_name, mail.dst_user_name, mail.dst_domain_name).send()

    # Server to client
    elif obj_type == HelloRequest:
        HelloResponse(obj.socket).send()
        
    # Generic packets
    elif obj_type == MailUsersRequest:
        MailUsersResponse(obj.socket).send()
    
    # Mail's payload sent.
    elif obj_type == MailPayloadRequest:
        MailPayloadResponse(obj.socket).send()
        
        # If It is a connection with a user, send the
        # email to the other NINAS server.
        if not mail.server_to_server_com:
            mail.setAttr('src_server_domain_name', HOST)
        
            # Create the connection.
            connection = ClientConnection('keys/' + HOST, 'server.host', password='tata')
            connection.bind(HOST)
            connection.start(NINAS_PORT)

            # Update the server.
            tcp_handler.request = connection.socket
            tcp_handler.loop.fromSocket(tcp_handler.request)

            # Send the first request.
            HelloServerRequest(tcp_handler.request, "ninas." + HOST, mail.src_domain_name).send()
            
            # Close the previous connection.
            obj.socket.close()
            
    # Mail users acknowledgement.
    elif obj_type == MailUsersResponse:
        MailPayloadRequest(obj.socket, mail.subject, mail.sent_date, payload=mail.payload).send()
    
    # Mail Payload acknowledgment.
    elif obj_type == MailPayloadResponse:
        return False

    return True


# The NINAS server instance.
ninas_server = Server(HOST, NINAS_PORT, ninas_handler, mail=MailInfo())
ninas_server.start()

# The IMAP server instance.
imap_server = Server(HOST, IMAP_PORT, imap.server_handler)
imap_server.start()

# Run the servers indefinitely.
try:
    while True: pass
# Handling Ctrl+C on terminal.
except KeyboardInterrupt: pass

# And then stop the servers if anything happened.
print()
console.debug("Stopping NINAS server")
ninas_server.stop()
console.debug("Stopping IMAP server")
imap_server.stop()
console.debug("Bye!")
sys.exit(0)