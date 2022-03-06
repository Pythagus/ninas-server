from ninas.network import NetworkBasePayload, PAYLOAD_IMAP_MASK
from ninas.connection import ClientConnection, HandlingLoop
from ninas.utils import MailFormatter, NList
from ninas.security import EmailAddress
from ninas import console
import tempfile
import shutil
import os


# Network objects identifiers.
IMAP_RETRIEVE_REQ = PAYLOAD_IMAP_MASK + 1
IMAP_RETRIEVE_RES = PAYLOAD_IMAP_MASK + 2


# Folders that are excluded from the
# mail retrieving.
__EXCLUDED_FOLDERS = ['requested']


# Get a correspondence dictionnary
# between network payload type and
# a class name.
def classIdentifierCorrespondence(): 
    return {
        IMAP_RETRIEVE_REQ: ImapRetrieveEmailsRequest,
        IMAP_RETRIEVE_RES: ImapRetrieveEmailResponse,
    }


# Handling the IMAP server incoming packets.
def server_handler(obj, obj_type, tcp_handler):
    # Retrieving emails request.
    if obj_type == ImapRetrieveEmailsRequest:
        # Send as many ImapRetrieveEmailsResponse as there are
        # emails in the user's mailbox. That's not optimal.
        mail_folder = MailFormatter.path(obj.email_address, 'mails')
        
        # Retrieve first, and then iterate to send.
        file_list = []
        
        # Retrieving all the emails.
        for root, dirs, files in os.walk(mail_folder):
            folder = root.split('/')[-1]
            
            if folder not in __EXCLUDED_FOLDERS:
                for file in files:
                    if file.endswith(".mail"):
                        file_list.append(folder + '/' + file)
            
        # Iterate again to send the responses.
        index = 0
        for file_path in file_list:
            with open(mail_folder + '/' + file_path, 'r') as f:
                response = ImapRetrieveEmailResponse(obj.socket, file_path, f.read(), index == len(file_list) - 1)
            
            response.send()
            index += 1  
        
    return False
    

# Request to retrieve all the user's emails.
class ImapRetrieveEmailsRequest(NetworkBasePayload):
    __slots__ = ['email_address']
    
    # Initialize the IMAP retrieving request.
    def __init__(self, socket, email_address):
        super().__init__(socket)
        
        self.email_address = email_address
        
    # Convert the class attributes to 
    # bytes to be sent over the network.
    def serialize(self):
        return NList({
            'type': IMAP_RETRIEVE_REQ,
            'email_address': self.email_address
        }).toBytes()

    # Convert an array to current 
    # class attributes.
    @staticmethod
    def unserialize(socket, values):
        NList(values).mustContainKeys('email_address')
        
        return ImapRetrieveEmailsRequest(socket, values['email_address'])

    # Handle the current request.
    def handle(self):
        console.debug("Handling ImapRetrieveEmailsRequest")
        
        # Check email validity.
        EmailAddress.assertValidAddress(self.email_address)
        EmailAddress.assertUserExists(self.email_address)
        
       
# Response after a retrieving request.
# This response is containing an email.
class ImapRetrieveEmailResponse(NetworkBasePayload):
    __slots__ = ['file_path', 'is_last', 'payload']
    
    # Initialize the IMAP retrieving response.
    def __init__(self, socket, file_path, payload, is_last):
        super().__init__(socket)
        
        self.file_path = file_path
        self.payload   = payload
        self.is_last   = is_last
        
    # Convert the class attributes to 
    # bytes to be sent over the network.
    def serialize(self):
        return NList({
            'type': IMAP_RETRIEVE_RES,
            'file_path': self.file_path,
            'payload': self.payload,
            'is_last': self.is_last
        }).toBytes()

    # Convert an array to current 
    # class attributes.
    @staticmethod
    def unserialize(socket, values):
        NList(values).mustContainKeys('file_path', 'is_last', 'payload')
        
        return ImapRetrieveEmailResponse(socket, values['file_path'], values['payload'], values['is_last'])

    # Handle the current request.
    def handle(self, retriever):
        console.debug("Handling ImapRetrieveEmailResponse : " + str(self.file_path))
        
        folders = self.file_path.split('/')[:-1]
        path    = retriever.folder + '/'
        
        # Create the folders if not already existing.
        for folder in folders:
            path += folder + '/'
            
            if not os.path.isdir(path):
                os.mkdir(path)
        
        with open(retriever.folder + '/' + self.file_path, 'w') as f:
            f.write(self.payload)
            

# Class used to retrieve the user's emails.
class MailRetriever(object):
    __slots__ = ['email_addr', 'folder']
    
    # Make a new retriever instance.
    def __init__(self, email_addr):
        self.email_addr = email_addr
        
    # Handle the incoming network packets.
    def __retrievingHandler(self, obj, obj_type):
        if obj_type == ImapRetrieveEmailResponse:
            return not obj.is_last
        
        console.warn("Wierd response from the server. Wanted ImapRetrieveEmailResponse, got " + str(obj_type) + ".")
        console.warn("Aborting.")
        return False
    
    # Start retrieving emails.
    def start(self, imap_port):
        # Check the email address validity.
        EmailAddress.assertValidAddress(self.email_addr)
        
        # Create a temporary folder to put the emails.
        self.folder = tempfile.mkdtemp()
        console.debug("IMAP: files stored at " + str(self.folder))
        
        connection = ClientConnection(self.email_addr + "/keys", "client.host")
        try:
            connection.start(imap_port)
            ImapRetrieveEmailsRequest(connection.socket, self.email_addr).send()
            HandlingLoop(self.__retrievingHandler, mail_retriever=self).fromSocket(connection.socket).run()       
        except BaseException as e:
            connection.close()
            self.clean()
            raise e  
     
    # Clean the file system.   
    def clean(self):
        if self.folder is not None:
            shutil.rmtree(self.folder)          
