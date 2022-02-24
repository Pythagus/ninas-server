from ninas.responses import HelloServerResponse, MailPayloadResponse, MailUsersResponse, ErrorResponse
from ninas.requests import HelloServerRequest, MailUsersRequest, MailPayloadRequest, CriticalError
from ninas.utils import NinasRuntimeError, MailInfo
from ninas.network import NetworkTools
from ninas import console
import socketserver
import threading
import sys


# Current server data.
HOST, PORT = "server.host", int(sys.argv[1])


# Base threaded server class.
class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer): pass


# Main class used to handle
# every incoming payload like
# requests and responses. This
# is thread-programming
class ThreadedTCPRequestHandler(socketserver.BaseRequestHandler):
    def handle(self):

        mail = MailInfo()
        print("CONNECTION FROM : " + str(self.client_address))

        while True:
            obj = NetworkTools.receiveNetworkObject(self.request)
            obj_type = type(obj)
            
            # Try to handle the network object.
            try:
                obj.handle(mail)
            except CriticalError as e:
                console.warn(e)
                ErrorResponse(obj.socket, e.type, e.message).send()
                break
            except NinasRuntimeError as e:
                console.warn(e)
                break
            
            # The client first contact.
            if obj_type == HelloServerRequest:
                HelloServerResponse(obj.socket).send()
            elif obj_type == MailUsersRequest:
                MailUsersResponse(obj.socket).send()
            elif obj_type == MailPayloadRequest:
                MailPayloadResponse(obj.socket).send()
                break

            # TODO : create blacklists/whitelists, check after the MAIL FROM
            # TODO : Check the signature of the mail
        
        print("Closing server...")
        self.request.close()



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
    while True: pass
