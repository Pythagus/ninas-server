from ninas.utils import MalformedArrayError, NinasRuntimeError
from abc import abstractmethod
from ninas import console
import json


# Calculate the network object masks.
PAYLOAD_MASK_RANGE    = 10000
PAYLOAD_REQUEST_MASK  = 10000
PAYLOAD_RESPONSE_MASK = PAYLOAD_REQUEST_MASK + PAYLOAD_MASK_RANGE
PAYLOAD_IMAP_MASK     = PAYLOAD_REQUEST_MASK + PAYLOAD_MASK_RANGE * 2


# Determine whether the given type is from
# the given mask.
def isTypeFromMask(mask, type):
    return mask <= type and type <= mask + PAYLOAD_MASK_RANGE - 1


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
        console.debug("Sending " + self.__class__.__name__)
        packet = NetworkPacket(self.serialize())
        self.socket.send(packet.serialize())

    # Close the established connection.
    def close(self):
        if self.socket is not None:
            self.socket.close()


# Base packet class used to encapsulate
# every network payload.
class NetworkPacket(object):
    SIZE_LENGTH = 64

    __slots__ = ['payload', 'size']

    # Initialize the class instance.
    def __init__(self, payload):
        self.payload = payload
        self.size    = len(payload) + NetworkPacket.SIZE_LENGTH

    # Serialize the network payload.
    def serialize(self):
        size = str(self.size)
        
        # Check whether the packet length is correct.
        if len(size) > NetworkPacket.SIZE_LENGTH:
            # TODO fragment packet if too big
            raise NinasRuntimeError("Packet length too big")
        
        size = ("0" * (NetworkPacket.SIZE_LENGTH - len(size))) + size

        return bytes(size, "utf-8") + self.payload 

    # Retrieve the network packet instance from bytes.
    @staticmethod
    def unserialize(values):
        return NetworkPacket(values[NetworkPacket.SIZE_LENGTH:])


# Class containing the most useful
# network tools.
class NetworkTools(object):

    # Receive exactly size bytes from
    # the given socket and add them to
    # the given buffer.
    @staticmethod
    def receiveBytes(socket, size, buffer):
        while len(buffer) < size:
            buffer += socket.recv(size - len(buffer))

        return buffer

    # Create a network instance from the
    # received payload.
    @staticmethod
    def createNetworkInstance(socket, dictionnary):
        if "type" not in dictionnary:
            raise MalformedArrayError("Field 'type' not found in payload")

        type = int(dictionnary['type'])
        class_correspondences = []
        
        # If the payload is a request.
        if isTypeFromMask(PAYLOAD_REQUEST_MASK, type):
            from ninas.requests import Request
            class_correspondences = Request.classIdentifierCorrespondence()

        # If the payload is a response.
        elif isTypeFromMask(PAYLOAD_RESPONSE_MASK, type):
            from ninas.responses import Response
            class_correspondences = Response.classIdentifierCorrespondence()
            
        # If the payload is an IMAP object.
        elif isTypeFromMask(PAYLOAD_IMAP_MASK, type):
            from ninas.imap import classIdentifierCorrespondence
            class_correspondences = classIdentifierCorrespondence()

        # Else, It's not a known value.
        else:
            raise UnknownPayloadTypeError(type)

        # If the given type doesn't exists
        # in the correspondence array.
        if type not in class_correspondences:
            raise UnknownPayloadTypeError(type)

        # Return the result of the unserialize method.
        return class_correspondences[type].unserialize(socket, dictionnary)

    # Receive a full network object
    # from the given socket.
    @staticmethod
    def receiveNetworkObject(socket):
        # Receive the full packet size.
        buffer = NetworkTools.receiveBytes(socket, NetworkPacket.SIZE_LENGTH, b"")

        # The received size as an integer.
        size = int(buffer)

        # Receive the missing bytes, also
        # known as the packet payload.
        buffer = NetworkTools.receiveBytes(socket, size, buffer)

        # Retrieve the NetworkPacket instance.
        packet = NetworkPacket.unserialize(buffer)

        # Return the network object instance.
        return NetworkTools.createNetworkInstance(socket, json.loads(packet.payload))


# Exception raised when an unknown
# network payload was received.
class UnknownPayloadTypeError(RuntimeError):
    # Initialize the error instance.
    def __init__(self, type):
        super().__init__(self, "Unknown payload type " + str(type))
