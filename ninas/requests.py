from ninas.network import NetworkBasePayload, NetworkStringInterface, PAYLOAD_REQUEST_MASK
from ninas.utils import NList, NinasRuntimeError
from ninas import console
import socketserver
import dns.resolver
import time
import re


# Requests identifiers.
REQ_HELLO_SERVER = PAYLOAD_REQUEST_MASK + 10
REQ_HELLO_CLIENT = PAYLOAD_REQUEST_MASK + 11
REQ_MAIL_USERS   = PAYLOAD_REQUEST_MASK + 20
REQ_MAIL_PAYLOAD = PAYLOAD_REQUEST_MASK + 30


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
            REQ_MAIL_USERS: MailUsersRequest,
            REQ_MAIL_PAYLOAD: MailPayloadRequest
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
    def handle(self, mail):
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

            mail.setAttr('src_domain_name', self.client_domain_name)
            mail.setAttr('src_server_domain_name', self.server_domain_name)

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
class MailUsersRequest(Request):
    __slots__ = [
        'src_user_name', 'dst_user_name', 'dst_domain_name'
    ]

    # Initialize the request instance.
    def __init__(self, socket, src_user_name, dst_user_name, dst_domain_name):
        super().__init__(socket)

        self.src_user_name   = src_user_name
        self.dst_user_name= dst_user_name
        self.dst_domain_name = dst_domain_name
        
    # Convert bytes to current class
    # attributes.
    @staticmethod
    def unserialize(socket, values):
        NList(values).mustContainKeys('src_user_name', 'dst_domain_name', 'dst_user_name')

        return MailUsersRequest(socket, 
            values['src_user_name'].lower(), 
            values['dst_user_name'].lower(), 
            values['dst_domain_name'].lower(), 
        )

    # Convert the class attributes to 
    # bytes to be sent over the network.
    def serialize(self):
        return NList({
            'type': REQ_MAIL_USERS,
            'src_user_name': self.src_user_name,
            'dst_user_name': self.dst_user_name,
            'dst_domain_name': self.dst_domain_name
        }).toBytes()
        
    # Handle the current request.
    def handle(self, mail):
        console.debug("Handling MailUsersRequest")

        mail.setAttr('src_user_name', self.src_user_name)
        mail.setAttr('dst_user_name', self.dst_user_name)
        mail.setAttr('dst_domain_name', self.dst_domain_name)
        # TODO: check for the blacklist


# Request to send the mail to the server
class MailPayloadRequest(Request):
    __slots__ = [
        'sent_date', 'subject', 'payload_file_name', 'payload'
    ]

    def __init__(self, socket, subject, sent_date, payload_file_name=None):
        super().__init__(socket)
        
        self.subject = subject
        self.payload_file_name = payload_file_name
        self.sent_date = sent_date

    # Convert the class attributes to 
    # bytes to be sent over the network.
    def serialize(self):
        # Get the mail content.
        payload = ""
        with open(self.payload_file_name, "r") as f:
            payload = f.read()
        
        return NList({
            'type': REQ_MAIL_PAYLOAD,
            'subject': self.subject,
            'sent_date': self.sent_date,
            'payload': payload,
        }).toBytes()

    # Convert bytes to current class
    # attributes.
    @staticmethod
    def unserialize(socket, values):
        NList(values).mustContainKeys('type', 'subject', 'payload', 'sent_date')

        request = MailPayloadRequest(socket, 
            values['subject'], 
            values['sent_date'], 
        )
        
        request.payload = values['payload']

        return request
    
    # Handle the current request.
    def handle(self, mail):
        console.debug("Handling MailPayloadRequest")
        
        # Update the mail info instance.
        mail.setAttr('subject', self.subject)
        mail.setAttr('sent_date', self.sent_date)
        mail.setAttr('received_date', time.time())
        
        # Prepare the destination file.
        self.payload_file_name = "samples/" + mail.fullDstAddr() + "/mails/" + mail.fullSrcAddr() + "_" + str(mail.sent_date) + ".mail"
        
        # Put the email content into the file.
        with open(self.payload_file_name, 'w') as f:
            f.write("FROM: " + mail.fullSrcAddr() + "\n")
            f.write("TO: " + mail.fullDstAddr() + "\n")
            f.write("SUBJECT: " + mail.subject + "\n")
            f.write("SENT DATE: " + str(mail.sent_date) + "\n")
            f.write("RECEIVED DATE: " + str(mail.received_date) + "\n")
            f.write("CONTENT:\n")
            f.write(self.payload)
        
        
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

