from ninas.errors import CriticalError
from ninas.network import NetworkTools
from ninas.utils import MailInfo
from ninas import responses
from ninas import console
import socketserver
import threading
import socket
import sys
import ssl



# Root folder for keys and certificates.
_ROOT = 'samples'


class HandlingLoop(object):
    __slots__ = ['tcp_handler', 'responder', 'mail', 'socket', 'respond_on_critical_error']
    
    # Create the looper.
    def __init__(self, responder, mail=None, respond_on_critical_error=False, tcp_handler=None):
        self.responder   = responder
        self.mail        = mail
        self.tcp_handler = tcp_handler
        self.respond_on_critical_error = respond_on_critical_error
        
    # Set the socket.
    def fromSocket(self, socket):
        self.socket = socket
        
        return self
    
    # Start the loop.
    def run(self):
        continue_connection = True
        
        while continue_connection:
            obj = NetworkTools.receiveNetworkObject(self.socket)
            
            try:
                obj.handle(self.mail)
                continue_connection = self.responder(obj, type(obj), mail=self.mail, tcp_handler=self.tcp_handler)
            except Exception as e:
                e_type = type(e)
                console.warn(
                    "Connection reset by peer" if e_type == ConnectionResetError else e
                )
                
                if self.respond_on_critical_error and (e_type == CriticalError):
                    responses.ErrorResponse(obj.socket, e.type, e.message).send()
                
                break
            
        console.debug("Closing connection...")
        self.socket.close()


# TODO find another way to solve server.py ThreadedTCPRequestHandler error in connectToServer() method
"""
def endless_handling_loop(_socket, responder, mail=None, respond_on_critical_error=False):
    continue_connection = True
        
    while continue_connection:
        obj = NetworkTools.receiveNetworkObject(_socket)
        
        try:
            obj.handle(mail)
            continue_connection = responder(obj, type(obj), mail)
        except Exception as e:
            e_type = type(e)
            console.warn(
                "Connection reset by peer" if e_type == ConnectionResetError else e
            )
            
            if respond_on_critical_error and (e_type == CriticalError):
                responses.ErrorResponse(obj.socket, e.type, e.message).send()
            
            break
        
    console.debug("Closing connection...")
    _socket.close()
"""


# Global connection creator.
class Connection(object):
    __slots__ = ['context', 'socket']
    
    def __init__(self, type, auth_folder, password=None):
        # Base folder for authentication.
        base = _ROOT + '/' + auth_folder + '/'
        
        # Create the SSL context.
        self.context = ssl.SSLContext(type)
        self.context.load_cert_chain(base + 'cert.pem', base + 'key.pem', password=password)
        self.context.load_verify_locations(cafile = _ROOT + '/keys/demoCA/cacert.pem')


# Client connection creator.
class ClientConnection(Connection):
    __slots__ = ['server_name']
    
    # Initialize the client connection.
    def __init__(self, auth_folder, server_name, password=None):
        super().__init__(ssl.PROTOCOL_TLS_CLIENT, auth_folder, password)
        
        # Store properties.
        self.server_name = server_name
        
        # Create the socket.
        _socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
        self.socket = self.context.wrap_socket(_socket, server_side=False, server_hostname=self.server_name)
        
    # Bind the socket to the host.
    def bind(self, host, port=0):
        self.socket.bind((host, port))
        
    # Start to connect to the given server name.
    def start(self, port):
        try:
            self.socket.connect((self.server_name, port))
        except ssl.SSLCertVerificationError as e:
            console.error("Error while checking server's certificate: \n" + str(e))
        except Exception as e:
            console.error(e)
            sys.exit(e.args[0])


# Server connection creator.        
class ServerConnection(Connection):
    # Initialize the server connection.
    def __init__(self, auth_folder, password=None):
        super().__init__(ssl.PROTOCOL_TLS_SERVER, auth_folder, password)
        
        self.context.verify_mode = ssl.CERT_REQUIRED
        
    # Start the server listening.
    def start(self, socket, server_name, port, max_connection):
        self.socket = self.context.wrap_socket(socket, server_side=True)
        
        try:
            self.socket.bind((server_name, port))
        except Exception as e:
            console.error("(" + server_name + ", " + str(port) + ") : " + str(e))
            sys.exit(e.args[0])
            
        self.socket.listen(max_connection)


# Main class used to handle
# every incoming payload like
# requests and responses. This
# is thread-programming
class ThreadedTCPRequestHandler(socketserver.BaseRequestHandler):
    def handle(self):
        console.debug("Connection from " + str(self.client_address))
        
        mail = MailInfo()
        self.loop = HandlingLoop(self.server.handler, mail, True, tcp_handler=self).fromSocket(self.request)
        self.loop.run()


# Base threaded server class.
class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer): 
    __slots__ = ['handler']
    
    def __init__(self, host, port, RequestHandlerClass):
        super().__init__((host, port), RequestHandlerClass, False)
        
        connection = ServerConnection('keys/' + host, password='tata')
        connection.start(self.socket, host, port, 5)
        self.socket = connection.socket


# The main server instance.
class Server(object):
    __slots__ = ['host', 'port', 'handler', 'server']
    
    # Initialize the server instance.
    def __init__(self, host, port, handler):
        self.host = host
        self.port = port 
        self.handler = handler
        
    # Start the server instance.
    def start(self):
        self.server = ThreadedTCPServer(self.host, self.port, ThreadedTCPRequestHandler)
        self.server.handler = self.handler
        
        # Start a thread with the server.
        # That thread will then start one more thread for each request.
        server_thread = threading.Thread(target=self.server.serve_forever)
        
        # Exit the server thread when the main thread terminates.
        server_thread.daemon = True
        server_thread.start()
        
    # Stop the server instance.
    def stop(self):
        # The server object will close the server thread.
        self.server.server_close()