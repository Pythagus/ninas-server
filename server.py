from ninas.responses import HelloServerResponse, HelloResponse, MailPayloadResponse, MailUsersResponse
from ninas.requests import HelloRequest, HelloServerRequest, MailUsersRequest, MailPayloadRequest
from ninas.connection import ClientConnection, Server
from ninas import console
import sys


# Current server data.
HOST, PORT = sys.argv[1], int(sys.argv[2])


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
            connection.start(PORT)

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
ninas_server = Server(HOST, PORT, ninas_handler)
ninas_server.start()


try:
    while True: pass
# Handling Ctrl+C on terminal.
except KeyboardInterrupt:
    print()
    console.debug("Stopping NINAS server")
    ninas_server.stop()
    sys.exit(0)