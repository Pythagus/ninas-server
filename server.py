from ninas.responses import HelloServerResponse
from ninas.requests import HelloServerRequest, MailFromRequest
from ninas.utils import NinasRuntimeError
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
# is thread-programming.
class ThreadedTCPRequestHandler(socketserver.BaseRequestHandler):
    def handle(self):
        print("CONNECTION FROM : " + str(self.client_address))

        while True:
            obj = NetworkTools.receiveNetworkObject(self.request)
            obj_type = type(obj)
            
            # Try to handle the network object.
            try:
                obj.handle()
            except NinasRuntimeError as e:
                console.warn(e)
                obj.close()
            
            # The client first contact.
            if obj_type == HelloServerRequest:
                HelloServerResponse(obj.socket).send()
            elif obj_type == MailFromRequest:
                print("What should we do after a MailFromRequest ?") # TODO


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
    while True: pass
