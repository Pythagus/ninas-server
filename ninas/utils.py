from ninas.errors import NinasRuntimeError
from Levenshtein import distance as lev
from ninas import console
import json
import os
import re


# The mail delimiter in .mail files.
MAIL_ATTR_DELIMITER = ': '


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
        # Internal data.
        'server_to_server_com', 'file_path',
        
        # Mail data.
        'src_server_domain_name', 'src_domain_name', 'dst_domain_name', 'src_user_name', 'dst_user_name', 
        'sent_date', 'received_date', 'subject', 'payload', 'is_requested', 'flag'
    ]

    def __init__(self) :
        self.flag = []

    # Updates the value of an attribute 
    # which name is in "key"
    def setAttr(self, key, value):
        setattr(self, key, value)
        
    # Write the attribute into the file.
    @staticmethod
    def writeFile(fd, key, value):
        fd.write(key + MAIL_ATTR_DELIMITER + str(value) + "\n")
        
    # Get the full client source email address.
    def fullSrcAddr(self):
        return MailFormatter.fullAddress(self.src_user_name, self.src_domain_name)
        
    # Get the full client destination email address.
    def fullDstAddr(self):
        return MailFormatter.fullAddress(self.dst_user_name, self.dst_domain_name)

    # Check the similarities beetween domain names.
    def checkDomainSimilarities(self):
        score = lev(self.src_domain_name, self.dst_domain_name)
        
        if score < 4 and score != 0:
            self.setAttr('flag', self.flag + ['SIMILAR_DOMAIN_NAMES'])
            
    
    # Check if there are URLS in the mail.
    def checkForUrls(self):
        regex = r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))"
        
        if re.findall(regex, self.payload) != []:
            self.setAttr('flag', self.flag + ["URLS_IN_PAYLOAD"])

    # Load the current object with the file data.
    @staticmethod
    def fromFile(file_path):
        with open(file_path, 'r') as f:
            mail = MailInfo()
            mail.file_path = file_path
            
            for _l in f:
                _line = _l.rstrip().split(MAIL_ATTR_DELIMITER)
                keyword = _line[0]
                content = ''.join(_line[1:])
                
                if keyword == 'FROM':
                    mail.src_user_name, mail.src_domain_name = content.split('@')
                elif keyword == 'TO':
                    mail.dst_user_name, mail.dst_domain_name = content.split('@')
                elif keyword == 'SUBJECT':
                    mail.subject = content
                elif keyword == 'SENT DATE':
                    mail.sent_date = content
                elif keyword == 'RECEIVED DATE':
                    mail.received_date = content
                elif keyword == 'CONTENT':
                    # We don't retrieve the payload in that
                    # method. Please use payload().
                    break
                
        return mail
    
    # Get the mail payload from file.
    def getPayload(self):
        if self.file_path is not None:
            with open(self.file_path, 'r') as f:
                is_payload = False
                payload = ""
                
                for line in f:
                    if is_payload:
                        payload += line
                    else:
                        is_payload = line.startswith('CONTENT' + MAIL_ATTR_DELIMITER)
        else:
            console.error("No file path given")
            payload = None
                    
        return payload    


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
        if email_addr is None:
            return "samples/" + file_name
        
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
