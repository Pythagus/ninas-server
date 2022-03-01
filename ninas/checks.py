import re
from ninas import console
from ninas.utils import MailFormatter


class Check():
    
    # Get the given file's path.
    @staticmethod
    def _getPath(email_addr, file_name):
        return MailFormatter.path(email_addr, file_name)
    
    # Check if the mail address is in the blacklist file
    # True if present
    def checkBlacklist(src_addr, dst_addr):
        blacklist = open(Check._getPath(dst_addr, "blacklist.json"), 'r').read()
        
        if (len(re.findall(src_addr, blacklist)) != 0):
            inBlacklist = True
            console.warn("User is not blacklisted")
        else :
            console.warn("Dangerous user")
            inBlacklist = False
        return inBlacklist

    # Check if the mail_addr is in the whitelist file
    # True if present
    @staticmethod
    def checkWhitelist(src_addr, dst_addr):
        whitelist = open(Check._getPath(dst_addr, "whitelist.json"), 'r').read()
        
        if (len(re.findall(src_addr, whitelist)) != 0):
            inWhitelist = True
            console.warn("User is whitelisted")
        else :
            console.warn("User is not whitelisted")
            inWhitelist = False
        return inWhitelist