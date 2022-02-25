from ninas.error import NinasRuntimeError
from ninas import console
import json    
    

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
        'src_server_domain_name', 'src_domain_name', 'dst_domain_name' ,'src_user_name', 'dst_user_name', 
        'sent_date', 'received_date', 'subject', 'payload'
    ]

    # Updates the value of an attribute 
    # which name is in "key"
    def setAttr(self, key, value):
        setattr(self, key, value)
        
    # Get the full client source email address.
    def fullSrcAddr(self):
        return self.src_user_name + "@" + self.src_domain_name
        
    # Get the full client destination email address.
    def fullDstAddr(self):
        return self.dst_user_name + "@" + self.dst_domain_name

    #Prints the info that we have in the mail so far
    def debug(self):
        for attr in self.__slots__:
            try:
                value = getattr(self, attr)
                console.debug("MAIL " + attr + " " + str(value))
            except AttributeError:
                pass
