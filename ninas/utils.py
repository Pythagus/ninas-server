import json
import socket
from ninas import console

# Base NINAS runtime error.
class NinasRuntimeError(RuntimeError): ...


# Base class to manage NINAS List
# and add useful tools.
class NList(object):
    __slots__ = ['arr']
    
    def __init__(self, arr):
        self.arr = arr
    
    # Raise an error if a required key 
    # is not present in the payload array.
    def mustContainKeys(self, *keys):
        for key in keys:
            if key not in self.arr:
                raise MalformedArrayError("Array must contain '" + str(key) + "' field")

    # Convert the given 
    def toBytes(self, encoding="utf-8"):
        return bytes(json.dumps(self.arr), encoding)


# Exception raised when a malformed
# payload was received.
class MalformedArrayError(NinasRuntimeError): ...


# Stores the info about the mail to be sent
# Gets updated each time the server receives some info
class MailInfo(object):
    __slots__ = [
        'server_domain_name', 'client_domain_name', 'user_name'
    ]

    # Updates the value of an attribute 
    # which name is in "key"
    def setMail(self, key, value):
        setattr(self, key, value)

    #Prints the info that we have in the mail so far
    def debug(self):
        for attr in self.__slots__:
            value = getattr(self, attr)
            if value != None:
                console.debug("MAIL " + attr + " " + str(value))




