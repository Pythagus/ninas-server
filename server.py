from os import confstr_names
from ninas.responses import HelloServerResponse, HelloResponse ,MailPayloadResponse, MailUsersResponse, ErrorResponse
from ninas.requests import HelloRequest, HelloServerRequest, MailUsersRequest, MailPayloadRequest
from ninas.errors import CriticalError, NinasRuntimeError
from ninas.network import NetworkTools
from ninas.utils import MailInfo
from ninas.checks import Check
from ninas import console
import socketserver
import threading
import sys
import socket
import ssl

# Current server data.
HOST, PORT = sys.argv[1], int(sys.argv[2])

# Base threaded server class.
class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer): 
    def __init__(self, server_address, RequestHandlerClass):

        super().__init__(server_address, RequestHandlerClass, False)

        context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        context.verify_mode = ssl.CERT_REQUIRED
        context.load_cert_chain('./keys/' + HOST + '/cert.pem', './keys/' + HOST + '/key.pem')
        context.load_verify_locations(cafile = './keys/demoCA/cacert.pem')

        self.socket = context.wrap_socket(self.socket, server_side=True)
        self.socket.bind((HOST, PORT))
        self.socket.listen(5)





# Main class used to handle
# every incoming payload like
# requests and responses. This
# is thread-programming
class ThreadedTCPRequestHandler(socketserver.BaseRequestHandler):
    def handle(self):

        mail = MailInfo()
        is_connexion_finished = False
        self.sock = self.request

        print("CONNECTION FROM : " + str(self.client_address))

        while not is_connexion_finished:

            obj, obj_type = self.handlePacket(mail)

            if obj == None:
                console.error("Error during communication, reset connexion")
                break

            # TODO : create blacklists/whitelists, check after the MAIL FROM

            # TODO : Check the signature of the mail
        
            is_connexion_finished = self.processPacket(mail, obj, obj_type)

            # TODO : create another domain name to be able to send mails in both directions


        print("Closing server...")
        self.request.close()

    # Called to connect to the dst NINAS
    # server when client has finished
    def connectToServer(self, mail):
        mail.setAttr('src_server_domain_name', HOST)

        context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        context.load_cert_chain('./keys/' + HOST + '/cert.pem', './keys/' + HOST + '/key.pem')
        context.load_verify_locations(cafile = './keys/demoCA/cacert.pem')

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
        ssock = context.wrap_socket(sock,server_side=False,server_hostname='server.host')
        ssock.bind((HOST, 0))
        try:
            ssock.connect(('server.host', PORT))
        except ssl.SSLCertVerificationError as e:
            console.error("Error while establishing TLS connexion" + str(e))

        self.sock = ssock

        hello = HelloServerRequest(self.sock, "ninas.client.host", "dmolina.fr")
        hello.send()




    # Handle incoming network packets
    def handlePacket(self, mail):
        try:
            obj = NetworkTools.receiveNetworkObject(self.sock)
            obj_type = type(obj)
        except ConnectionResetError as e:
            console.warn("Connection reset by peer")
            return None, None
        
        # Try to handle the network object.
        try:
            obj.handle(mail)
        except CriticalError as e:
            console.warn(e)
            ErrorResponse(obj.socket, e.type, e.message).send()
            return None, None
        except NinasRuntimeError as e:
            console.warn(e)
            return None, None
        except ssl.CertificateError as e:
            console.warn(e)
            return None, None
        return obj, obj_type


    # Process the packets and send the next ones
    def processPacket(self, mail, obj, obj_type):

        # Server as a dst  server
        if obj_type == HelloServerRequest:
            HelloServerResponse(obj.socket).send()

        # Server as an src server
        elif obj_type == HelloServerResponse:
            MailUsersRequest(obj.socket, "elies", mail.dst_user_name, mail.dst_domain_name).send()

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
            return True

        return False




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
