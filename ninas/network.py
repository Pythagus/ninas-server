from abc import abstractmethod
import json


PAYLOAD_REQUEST_MASK  = 10000
PAYLOAD_RESPONSE_MASK = 20000


# Convert the given JSON data to
# a bytes value.
def dictToBytes(dictionnary, encoding="utf-8"):
    return bytes(json.dumps(dictionnary), encoding)


# Raise an error if a required key 
# is not present in the payload array.
def payloadMustContain(payload, keys):
    for key in keys:
        if key not in payload:
            raise MalformedPayloadError("Payload must contain '" + str(key) + "' field")


# Create a network instance from the
# received payload.
def createNetworkInstance(socket, dictionnary):
    if "type" not in dictionnary:
        raise MalformedPayloadError("Field 'type' not found in payload")

    type = dictionnary['type']
    class_correspondences = []

    # If the payload is a request.
    if type & PAYLOAD_REQUEST_MASK == PAYLOAD_REQUEST_MASK:
        from ninas.requests import Request
        class_correspondences = Request.classIdentifierCorrespondence()

    # If the payload is a response.
    elif type & PAYLOAD_RESPONSE_MASK == PAYLOAD_RESPONSE_MASK:
        from ninas.responses import Response
        class_correspondences = Response.classIdentifierCorrespondence()

    # Else, It's not a known value.
    else:
        raise UnknownPayloadTypeError(type)

    # If the given type doesn't exists
    # in the correspondence array.
    if type not in class_correspondences:
        raise UnknownPayloadTypeError(type)

    # Return the result of the unserialize method.
    return class_correspondences[type].unserialize(socket, dictionnary)


def receiveBytes(socket, size, buf):
    while len(buf) < size:
        buf += socket.recv(size - len(buf))

    return buf


# Exception raised when an unknown
# network payload was received.
class UnknownPayloadTypeError(RuntimeError):
    # Initialize the error instance.
    def __init__(self, type):
        super().__init__(self, "Unknown payload type " + str(type))


# Exception raised when a malformed
# payload was received.
class MalformedPayloadError(RuntimeError): ...


# Base network class used in every
# network objects.
class NetworkBasePayload(object):
    __slots__ = [
        'socket', 'port_dst', 'ip_addr_dst', 'size'
    ]

    # Initialize the network class.
    def __init__(self, socket):
        self.socket = socket
        self.ip_addr_dst, self.port_dst = self.socket.getpeername()

    # Convert the class attributes to 
    # bytes to be sent over the network.
    @abstractmethod
    def serialize(self): raise NotImplementedError

    # Convert an array to current 
    # class attributes.
    @staticmethod
    def unserialize(socket, values): return None

     # Get a correspondence dictionnary
     # between network payload type and
     # a class name.
    @staticmethod
    def classIdentifierCorrespondence(): raise NotImplementedError

     # Handle the current request.
    @abstractmethod
    def handle(self): raise NotImplementedError

    # Send the current class over the
    # network using the serialize method.
    def send(self):
        packet = NetworkPacket(self.serialize())
        self.socket.send(packet.serialize())

    # Close the established connection.
    def close(self):
        if self.socket is not None:
            self.socket.close()


# Base packet class used to encapsulate
# every network payload.
class NetworkPacket(object):
    SIZE_LENGTH = 128

    __slots__ = [
        'payload', 'size'
    ]

    def __init__(self, payload):
        self.payload = payload
        self.size    = len(payload) + NetworkPacket.SIZE_LENGTH

    def serialize(self):
        size = str(self.size)
        size = ("0" * (NetworkPacket.SIZE_LENGTH - len(size))) + size

        return bytes(size, "utf-8") + self.payload 

    @staticmethod
    def unserialize(values):
        return NetworkPacket(values[NetworkPacket.SIZE_LENGTH:])