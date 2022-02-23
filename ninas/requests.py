from ninas.network import NetworkBasePayload, NetworkStringInterface, PAYLOAD_REQUEST_MASK
from ninas.utils import NList, NinasRuntimeError
from ninas import console
import socketserver
import dns.resolver
import re


# Requests identifiers.
REQ_HELLO_SERVER = PAYLOAD_REQUEST_MASK + 10
REQ_HELLO_CLIENT = PAYLOAD_REQUEST_MASK + 11
REQ_MAIL_FROM    = PAYLOAD_REQUEST_MASK + 20


# Base request class used for
# every network requests.
class Request(NetworkBasePayload, socketserver.BaseRequestHandler):

     # Get a correspondence dictionnary
     # between network payload type and
     # a class name.
    @staticmethod
    def classIdentifierCorrespondence(): 
        return {
            REQ_HELLO_CLIENT: HelloRequest,
            REQ_HELLO_SERVER: HelloServerRequest,
            REQ_MAIL_FROM: MailFromRequest,
        }


# Request made from the NINAS server to
# another NINAS server to request a new
# connection.
class HelloRequest(Request):
    __slots__ = [
        'server_domain_name'
    ]

    # Initialize the request instance.
    def __init__(self, socket, server_domain_name):
        super().__init__(socket)

        self.server_domain_name = server_domain_name

    # Convert bytes to current class
    # attributes.
    @staticmethod
    def unserialize(socket, values):
        NList(values).mustContainKeys('server_domain_name')
        
        return HelloRequest(socket, values['server_domain_name'])

    # Convert the class attributes to 
    # bytes to be sent over the network.
    def serialize(self):
        return NList({
            'type': REQ_HELLO_CLIENT,
            'server_domain_name': self.server_domain_name
        }).toBytes()


# Request made from a NINAS client to a
# NINAS server to request a new connection.
class HelloServerRequest(HelloRequest):
    __slots__ = [
        'client_domain_name'
    ]

    # Initialize the request instance.
    def __init__(self, socket, server_domain_name, client_domain_name):
        super().__init__(socket, server_domain_name)

        self.client_domain_name = client_domain_name

    # Convert bytes to current class
    # attributes.
    @staticmethod
    def unserialize(socket, values):
        NList(values).mustContainKeys('server_domain_name', 'client_domain_name')

        return HelloServerRequest(socket, 
            values['server_domain_name'].lower(), 
            values['client_domain_name'].lower()
        )

    # Handle the current request.
    def handle(self):
        console.debug("Handling HelloServerRequest")
        
        if not self.server_domain_name.startswith(NetworkStringInterface.NINAS_ADDR_START):
            raise MalformedNinasAddressError(
                "NINAS server address must be like '" + NetworkStringInterface.NINAS_ADDR_START + ".domain.ext'"
            )

        server_name = self.server_domain_name[len(NetworkStringInterface.NINAS_ADDR_START):]

        # If the domain name doesn't match the
        # server name, we need to verify the SPF
        # field in the DNS records.
        if server_name != self.client_domain_name:
            console.debug("   Checking SPF records for " + str(self.client_domain_name) + "...")
            
            # Check the NINAS.spf entry if there's any.
            answers = dns.resolver.query(self.client_domain_name, 'TXT')

            ip4 = []
            ip6 = []
            for _record in answers:
                # Remove the '"' from the DNS record.
                record = str(_record)[1:-1]

                # If It's a NINAS.spf record.
                if str(record).startswith(NetworkStringInterface.NINAS_SPF_VALUE):
                    # Check ip6 field.
                    ip6_field = re.findall('ip6=[0-9:a-fA-F]+', record)
                    if len(ip6_field) > 0:
                        ip6.append(ip6_field[0][len('ip6='):])
                        
                    # Check ip4 field.
                    ip4_field = re.findall('ip4=[0-9.]+', record)
                    if len(ip4_field) > 0:
                        ip4.append(ip4_field[0][len('ip4='):])

            # If no matching IP was found.
            if self.ip_addr_dst not in ip4 and self.ip_addr_dst not in ip6:
                raise InvalidNinasSpfError(self.socket)
            
            console.debug("   SPF checked!")

    # Convert the class attributes to 
    # bytes to be sent over the network.
    def serialize(self):
        return NList({
            'type': REQ_HELLO_SERVER,
            'server_domain_name': self.server_domain_name,
            'client_domain_name': self.client_domain_name
        }).toBytes()


# The client send the MAIL FROM to
# notify the server who is sending an
# email to one of its users.
class MailFromRequest(Request):
    __slots__ = [
        'user_name', 'domain_name'
    ]

    # Initialize the request instance.
    def __init__(self, socket, user_name, domain_name):
        super().__init__(socket)

        self.user_name   = user_name
        self.domain_name = domain_name
        
    # Convert bytes to current class
    # attributes.
    @staticmethod
    def unserialize(socket, values):
        NList(values).mustContainKeys('user_name', 'domain_name')

        return MailFromRequest(socket, 
            values['user_name'].lower(), 
            values['domain_name'].lower()
        )

    # Convert the class attributes to 
    # bytes to be sent over the network.
    def serialize(self):
        return NList({
            'type': REQ_MAIL_FROM,
            'user_name': self.user_name,
            'domain_name': self.domain_name
        }).toBytes()
        
    # Handle the current request.
    def handle(self):
        console.debug("Handling MailFromRequest")
        console.warn("HANDLE MAIL FROM")
        # TODO : check whether the received domain name was previously authorized
        # TODO : attach the user_name and the domain_name to the socket to retrieve them
        #        when the mail will be sent over this same socket.


# Exception raised when no valid
# SPF records were found in the
# DNS records.
class InvalidNinasSpfError(NinasRuntimeError): 
    __slots__ = [
        'socket'
    ]

    def __init__(self, socket, *args: object):
        super().__init__(*args)
        self.socket = socket


class MalformedNinasAddressError(NinasRuntimeError): ...
