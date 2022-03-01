from ninas.security import SPF, EmailAddress, getNinasServerAddress
from ninas.network import NetworkBasePayload, PAYLOAD_REQUEST_MASK
from ninas.lists import BlackList, BlackListedError, RequestList
from ninas.utils import MailFormatter, NList, MailInfo
from ninas import console
import socketserver
import time
import ssl


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


# Request made from the NINAS client to
# a NINAS server to request a new
# connection.
class HelloRequest(Request):
    __slots__ = [
        'client_domain_name'
    ]

    # Initialize the request instance.
    def __init__(self, socket, client_domain_name):
        super().__init__(socket)

        self.client_domain_name = client_domain_name

    # Convert bytes to current class
    # attributes.
    @staticmethod
    def unserialize(socket, values):
        NList(values).mustContainKeys('client_domain_name')
        
        return HelloRequest(socket, values['client_domain_name'])

    # Convert the class attributes to 
    # bytes to be sent over the network.
    def serialize(self):
        return NList({
            'type': REQ_HELLO_CLIENT,
            'client_domain_name': self.client_domain_name
        }).toBytes()

    def handle(self, mail):
        mail.setAttr('server_to_server_com', False)
        mail.setAttr('src_domain_name', self.client_domain_name)






# Request made from a NINAS client to a
# NINAS server to request a new connection.
class HelloServerRequest(HelloRequest):
    __slots__ = [
        'client_domain_name', 'server_domain_name'
    ]

    # Initialize the request instance.
    def __init__(self, socket, server_domain_name, client_domain_name):
        super().__init__(socket, server_domain_name)

        self.client_domain_name = client_domain_name
        self.server_domain_name = server_domain_name

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
        
        server_name = getNinasServerAddress(self.server_domain_name)
        mail.setAttr('server_to_server_com', True)

        # If the domain name doesn't match the
        # server name, we need to verify the SPF
        # field in the DNS records.
        if server_name != self.client_domain_name:
            SPF.check(self.client_domain_name, self.ip_addr_dst)
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
        self.dst_user_name   = dst_user_name
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

        # Set the mail received info.
        mail.setAttr('src_user_name', self.src_user_name)
        mail.setAttr('dst_user_name', self.dst_user_name)
        mail.setAttr('dst_domain_name', self.dst_domain_name)
        
        # Check the addresses validity.
        EmailAddress.assertValidAddress(mail.fullSrcAddr())
        EmailAddress.assertValidAddress(mail.fullDstAddr())
    
        # Check whether the user exists or not.
        if mail.server_to_server_com:
            EmailAddress.assertUserExists(mail.fullDstAddr())
            # TODO : create blacklists/whitelists, check after the MAIL FROM
            # whitelist first
            src_addr = MailInfo.fullSrcAddr(mail)
            dst_addr = MailInfo.fullDstAddr(mail)
            
            if BlackList(dst_addr).contains(src_addr):
                raise BlackListedError(src_addr + " is currently blacklisted by " + dst_addr)
        else:
            EmailAddress.assertUserExists(mail.fullSrcAddr())
            
            #Check if the user's certificate matchs its identitity
            ssl.match_hostname(self.socket.getpeercert(), mail.fullSrcAddr())

        #Check to see if the client cer

        # TODO : check for the blacklist


# Request to send the mail to the server
class MailPayloadRequest(Request):
    __slots__ = [
        'sent_date', 'subject', 'payload_file_name', 'payload'
    ]

    def __init__(self, socket, subject, sent_date, payload_file_name=None, payload=None):
        super().__init__(socket)
        
        self.subject = subject
        self.payload_file_name = payload_file_name
        self.sent_date = sent_date
        self.payload = payload


    # Convert the class attributes to 
    # bytes to be sent over the network.
    def serialize(self):
        # Get the mail content.

        if self.payload == None:
            with open(self.payload_file_name, "r") as f:
                self.payload = f.read()

        return NList({
            'type': REQ_MAIL_PAYLOAD,
            'subject': self.subject,
            'sent_date': self.sent_date,
            'payload': self.payload,
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
        mail.setAttr('payload', self.payload)
        
        
        #MailFormatter.save(mail, self.payload)
        
        # Prepare the destination file.
        if mail.server_to_server_com:
            self.payload_file_name = "samples/" + mail.fullDstAddr() + "/mails/" + mail.fullSrcAddr() + "_" + str(mail.sent_date) + ".mail"
        else:
            self.payload_file_name = "samples/" + mail.fullSrcAddr() + "/mails/" + mail.fullDstAddr() + "_" + str(mail.sent_date) + ".mail"
        
        # Put the email content into the file.
        with open(self.payload_file_name, 'w') as f:
            f.write("FROM: " + mail.fullSrcAddr() + "\n")
            f.write("TO: " + mail.fullDstAddr() + "\n")
            f.write("SUBJECT: " + mail.subject + "\n")
            f.write("SENT DATE: " + str(mail.sent_date) + "\n")
            f.write("RECEIVED DATE: " + str(mail.received_date) + "\n")
            f.write("CONTENT:\n")
            f.write(self.payload)
