from ninas.network import NetworkBasePayload, NetworkStringInterface, PAYLOAD_REQUEST_MASK
from ninas.responses import HelloServerResponse
from ninas.utils import NList
import socketserver
import dns.resolver
import re


# Requests identifiers.
REQ_HELLO_SERVER = PAYLOAD_REQUEST_MASK + 10
REQ_HELLO_CLIENT = PAYLOAD_REQUEST_MASK + 11


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
            REQ_HELLO_SERVER: HelloServerRequest
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
        if not self.server_domain_name.startswith(NetworkStringInterface.NINAS_ADDR_START):
            raise MalformedNinasAddressError(
                "NINAS server address must be like '" + NetworkStringInterface.NINAS_ADDR_START + ".domain.ext'"
            )

        server_name = self.server_domain_name[len(NetworkStringInterface.NINAS_ADDR_START):]

        # If the domain name doesn't match the
        # server name, we need to verify the SPF
        # field in the DNS records.
        if server_name != self.client_domain_name:
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

            print("SPF CHECKED!")
            response = HelloServerResponse(self.socket)
            response.send()
                    

    # Convert the class attributes to 
    # bytes to be sent over the network.
    def serialize(self):
        return NList({
            'type': REQ_HELLO_SERVER,
            'server_domain_name': self.server_domain_name,
            'client_domain_name': self.client_domain_name
        }).toBytes()


# Exception raised when no valid
# SPF records were found in the
# DNS records.
class InvalidNinasSpfError(RuntimeError): 
    __slots__ = [
        'socket'
    ]

    def __init__(self, socket, *args: object):
        super().__init__(*args)
        self.socket = socket


class MalformedNinasAddressError(RuntimeError): ...
