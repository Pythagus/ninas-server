from ninas.responses import HelloServerResponse, HelloResponse, MailPayloadResponse, MailUsersResponse
from ninas.requests import HelloRequest, HelloServerRequest, MailUsersRequest, MailPayloadRequest
from ninas.connection import ClientConnection, ServerConnection, HandlingLoop
from ninas.utils import MailInfo
from ninas import console
import socketserver
import threading
import sys


# Current server data.
HOST, PORT = sys.argv[1], int(sys.argv[2])


# Main class used to handle
# every incoming payload like
# requests and responses. This
# is thread-programming
class ThreadedTCPRequestHandler(socketserver.BaseRequestHandler):
    def handle(self):
        console.debug("Connection from " + str(self.client_address))
        
        mail = MailInfo()
        self.loop = HandlingLoop(self.handler, mail, True).fromSocket(self.request)
        self.loop.run()
        # TODO : Check the signature of the mail
        # TODO : create another domain name to be able to send mails in both directions

    # Called to connect to the dst NINAS
    # server when client has finished
    def connectToServer(self, mail):
        mail.setAttr('src_server_domain_name', HOST)
        
        # Create the connection.
        connection = ClientConnection('keys/' + HOST, 'server.host', password='tata')
        connection.bind(HOST)
        connection.start(PORT)

        self.request = connection.socket
        self.loop.fromSocket(self.request)

        # Send the first request.
        HelloServerRequest(self.request, "ninas." + HOST, mail.src_domain_name).send()

    # Handle the network object after their
    # internal handle() method.
    def handler(self, obj, obj_type, mail):
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
        
        elif obj_type == MailPayloadRequest:
            MailPayloadResponse(obj.socket).send()
            
            if not mail.server_to_server_com:
                self.connectToServer(mail)
                obj.socket.close()
        
        elif obj_type == MailUsersResponse:
            MailPayloadRequest(obj.socket, mail.subject, mail.sent_date, payload=mail.payload).send()
        
        elif obj_type == MailPayloadResponse:
            return False

        return True


# Base threaded server class.
class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer): 
    def __init__(self, server_address, RequestHandlerClass):
        super().__init__(server_address, RequestHandlerClass, False)
        
        connection = ServerConnection('keys/' + HOST, password='tata')
        connection.start(self.socket, HOST, PORT, 5)
        self.socket = connection.socket


# Create the server
with ThreadedTCPServer((HOST, PORT), ThreadedTCPRequestHandler) as server:
    ip, port = server.server_address

    # Start a thread with the server
    # That thread will then start one more thread for each request
    server_thread = threading.Thread(target=server.serve_forever)
    
    # Exit the server thread when the main thread terminates
    server_thread.daemon = True
    server_thread.start()
    
    print("Server loop running in thread:", server_thread.name)
    print()
    
    try:
        while True: pass
    # Handling Ctrl+C on terminal.
    except KeyboardInterrupt:
        print()
        console.debug("Stopping NINAS server")
        server.server_close()
        sys.exit(0)