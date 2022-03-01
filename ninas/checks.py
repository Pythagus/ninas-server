from lzma import CHECK_UNKNOWN
from typing_extensions import Self
from ninas.utils import NList, MailInfo
import json
import re
from ninas import console

# list path
BLACKLIST = "/home/maud/Documents/nina/ninas-server/samples/maud@microsoft.org/blacklist.json"
WHITELIST = "/home/maud/Documents/nina/ninas-server/samples/maud@microsoft.org/whitelist.json"


class Check():
    
    # Check if the mail address is in the blacklist file
    # True if present
    def checkBlacklist(mail_addr):
        blacklist = open(BLACKLIST, 'r').read()
        if (len(re.findall(mail_addr, blacklist)) != 0):
            inBlacklist = True
            console.warn("User is not blacklisted")
        else :
            console.warn("Dangerous user")
            inBlacklist = False
        return inBlacklist

    # Check if the mail_addr is in the whitelist file
    # True if present
    def checkWhitelist(mail_addr):
        whitelist = open(WHITELIST, 'r').read()
        if (len(re.findall(mail_addr, whitelist)) != 0):
            inWhitelist = True
            console.warn("User is whitelisted")
        else :
            console.warn("User is not whitelisted")
            inWhitelist = False
        return inWhitelist


    # Combine CheckWhitelist and CheckBlacklist
    def completeCheck(mail_addr):
        if Self.checkWhitelist(mail_addr):
            console.warn("User is whitelisted")
        else : 
            console.warn("User is not whitelisted")
            if Self.checkBlacklist(mail_addr): 
                console.warn("Dangerous user")