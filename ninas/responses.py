from ninas.network import NetworkBasePayload, PAYLOAD_RESPONSE_MASK
from ninas.utils import NList
from ninas import console


# Responses identifiers.
RES_HELLO_SERVER = PAYLOAD_RESPONSE_MASK + 10
RES_MAIL_USERS   = PAYLOAD_RESPONSE_MASK + 20


# Base response class used for every
# network response.
class Response(NetworkBasePayload):

     # Get a correspondence dictionnary
     # between network payload type and
     # a class name.
    @staticmethod
    def classIdentifierCorrespondence(): 
        return {
            RES_HELLO_SERVER: HelloServerResponse,
            RES_MAIL_USERS: MailUsersResponse
        }


# Base empty response.
class EmptyResponse(Response):
    __slots__ = ['type']

    # Initialize the response with the type.
    def __init__(self, socket, type):
        super().__init__(socket)
        self.type = type
        
    # Handle the current request.
    def handle(self): 
        console.debug("Handling " + self.__class__.__name__)

    # Convert the class attributes to 
    # bytes to be sent over the network.
    def serialize(self):
        return NList({
            'type': self.type,
        }).toBytes()

    # Convert bytes to current class
    # attributes.
    @staticmethod
    def unserialize(socket, values):
        NList(values).mustContainKeys('type')
        
        class_names = Response.classIdentifierCorrespondence()
        
        type = values['type']
        if type in class_names:
            return class_names[type](socket)
        
        return None

        
# Response sent after the first client
# contact request.
class HelloServerResponse(EmptyResponse):
    def __init__(self, socket):
        super().__init__(socket, RES_HELLO_SERVER)


# Send an empty response to acknowledge
# the MAIL_USERS request.
class MailUsersResponse(EmptyResponse):
    def __init__(self, socket):
        super().__init__(socket, RES_MAIL_USERS)
