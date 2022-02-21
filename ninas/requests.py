from ninas.network import NetworkBasePayload, PAYLOAD_REQUEST_MASK, payloadMustContain, dictToBytes


# Requests identifiers.
REQ_HELLO_SERVER = PAYLOAD_REQUEST_MASK + 10
REQ_HELLO_CLIENT = PAYLOAD_REQUEST_MASK + 11


# Base request class used for
# every network requests.
class Request(NetworkBasePayload):

     # Get a correspondence dictionnary
     # between network payload type and
     # a class name.
    @staticmethod
    def classIdentifierCorrespondence(): 
        return {
            REQ_HELLO_SERVER: HelloServerRequest,
            REQ_HELLO_CLIENT: HelloClientRequest
        }


# Request made from the NINAS server to
# another NINAS server to request a new
# connection.
class HelloServerRequest(Request):
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
        payloadMustContain(values, ['server_domain_name'])
        
        return HelloServerRequest(socket, values['server_domain_name'])

    # Convert the class attributes to 
    # bytes to be sent over the network.
    def serialize(self):
        return dictToBytes({
            'type': REQ_HELLO_SERVER,
            'server_domain_name': self.server_domain_name
        })


# Request made from a NINAS client to a
# NINAS server to request a new connection.
class HelloClientRequest(HelloServerRequest):
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
        payloadMustContain(values, [
            'server_domain_name', 'client_domain_name'
        ])

        return HelloClientRequest(socket, values['server_domain_name'], values['client_domain_name'])

    # Convert the class attributes to 
    # bytes to be sent over the network.
    def serialize(self):
        return dictToBytes({
            'type': REQ_HELLO_CLIENT,
            'server_domain_name': self.server_domain_name,
            'client_domain_name': self.client_domain_name
        })
