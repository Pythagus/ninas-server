from ninas.errors import CriticalError
from ninas.network import NetworkTools
from ninas import responses
from ninas import console
import socket
import sys
import ssl


# Root folder for keys and certificates.
_ROOT = 'samples'


class HandlingLoop(object):
    __slots__ = ['responder', 'mail', 'socket', 'respond_on_critical_error']
    
    # Create the looper.
    def __init__(self, responder, mail=None, respond_on_critical_error=False):
        self.responder = responder
        self.mail      = mail
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
                continue_connection = self.responder(obj, type(obj), self.mail)
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
        self.socket.bind((server_name, port))
        self.socket.listen(max_connection)
