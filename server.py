from ninas.responses import HelloServerResponse, MailFromResponse
from ninas.requests import HelloServerRequest, MailFromRequest
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
            except NinasRuntimeError as e:
                console.warn(e)
                obj.close()
            
            # The client first contact.
            if obj_type == HelloServerRequest:
                HelloServerResponse(obj.socket).send()
            elif obj_type == MailFromRequest:
                mail.debug()
                MailFromResponse(obj.socket).send()
                # TODO : Send a MailFromResponse

            # TODO : create blacklists/whitelists, check after the MAIL FROM
            # TODO : Send the mail
            # TODO : Check the signature of the mail



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
