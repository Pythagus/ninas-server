from ninas.errors import NinasRuntimeError
from ninas import console
import json
import os


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
        'server_to_server_com', 'src_server_domain_name', 'src_domain_name', 'dst_domain_name' ,'src_user_name', 'dst_user_name', 
        'sent_date', 'received_date', 'subject', 'payload'
    ]

    # Updates the value of an attribute 
    # which name is in "key"
    def setAttr(self, key, value):
        setattr(self, key, value)
        
    # Get the full client source email address.
    def fullSrcAddr(self):
        return MailFormatter.fullAddress(self.src_user_name, self.src_domain_name)
        
    # Get the full client destination email address.
    def fullDstAddr(self):
        return MailFormatter.fullAddress(self.dst_user_name, self.dst_domain_name)

    #Prints the info that we have in the mail so far
    def debug(self):
        for attr in self.__slots__:
            try:
                value = getattr(self, attr)
                console.debug("MAIL " + attr + " " + str(value))
            except AttributeError:
                pass


# Helper used to format the mail file
# saving and add a name convention.
class MailFormatter(object):        
    # Join the user name and the domain name.   
    @staticmethod
    def fullAddress(user_name, domain):
        return user_name + "@" + domain
        
    # Get the path of a given file_name.
    @staticmethod    
    def path(email_addr, file_name):
        return "samples/" + email_addr + "/" + file_name
     
    # Determine whether the given file name
    # belongs to the given email address.   
    @staticmethod
    def fileIsFrom(file_name, email_addr):
        return file_name.startswith(email_addr)
    
    # Get all the files belonging to the given
    # email address.
    @staticmethod
    def filesFrom(user_addr, email_addr, folder=''):
        entries = os.scandir(MailFormatter.path(user_addr, folder))
        
        files = []
        for entry in entries:
            if MailFormatter.fileIsFrom(entry.name, email_addr):
                files.append(entry.name)
                
        return files