from ninas.utils import NList, MailFormatter
from ninas.errors import CriticalError, Err
from datetime import datetime, timedelta
from ninas import console
import dns.resolver
import json
import time
import re
import os

# TODO update request handle to add a check.


# Starting subdomain of a NINAS server.
SERVER_ADDR_START = 'ninas.'


# Check whether the given NINAS server
# address is valid.
def getNinasServerAddress(address):
    if not address.startswith(SERVER_ADDR_START):
        raise MalformedAddressError(
            Err.INVALID_NINAS_DOMAIN, "NINAS server address must start with '" + SERVER_ADDR_START + "'"
        )

    return address[len(SERVER_ADDR_START):]


# Email address class utilities.
class EmailAddress(object):
    
    # Check whether the user exists
    # in the file system.
    @staticmethod
    def assertUserExists(email):
        user_directory = "samples/" + email
        if not os.path.isdir(user_directory):
            raise CriticalError(
                Err.USER_NOT_FOUND, "User " + email + " not found"
            )
    
    # Check whether the given email address
    # is valid.
    @staticmethod
    def assertValidAddress(address):
        if not re.match('^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$', address):
            raise MalformedAddressError(
                Err.INVALID_EMAIL_ADDRESS, "Invalid email address " + address
            )
            

# Manage the SPF records in the DNS.
class SPF(object):
    
    # The head value in the DNS.
    SPF_VALUE = 'v=NINAS.spf'
    
    # Check whether the SPF field in the domain 
    # DNS server matches the given socket IP.
    @staticmethod
    def check(domain, ip_addr):
        console.debug("   Checking SPF records for " + str(domain) + "...")
        
        # Check the NINAS.spf entry if there's any.
        try:
            answers = dns.resolver.query(domain, 'TXT')
        except:
            raise InvalidNinasSpfError(Err.DOMAIN_NOT_FOUND, "Cannot get " + domain + " DNS records")
        
        ip4 = []
        ip6 = []
        for _record in answers:
            # Remove the '"' from the DNS record.
            record = str(_record)[1:-1]

            # If It's a NINAS.spf record.
            if str(record).startswith(SPF.SPF_VALUE):
                # Check ip6 field.
                ip6_field = re.findall('ip6=[0-9:a-fA-F]+', record)
                if len(ip6_field) > 0:
                    ip6.append(ip6_field[0][len('ip6='):])
                    
                # Check ip4 field.
                ip4_field = re.findall('ip4=[0-9.]+', record)
                if len(ip4_field) > 0:
                    ip4.append(ip4_field[0][len('ip4='):])

        # If no matching IP was found.
        if ip_addr not in ip4 and ip_addr not in ip6:
            raise InvalidNinasSpfError(Err.DOMAIN_SPF, "IP address " + ip_addr + " not allowed to manage " + domain)
        
        console.debug("   SPF checked!")


# Manage the email authorizations for
# the given user.
class Authorization(object):
    __slots__ = [
        'email', 'blacklist', 'whitelist', 'requests'
    ]
    
    # Initialize the authorization helper
    # for the given email address.
    def __init__(self, email):
        self.email = email
        
        # Retrieve the class data for the user. 
        self.requests  = AuthorizationRequestList(self, "requests")
        #self.blacklist = # TODO Cast to Blacklist object
        #self.whitelist = # TODO Cast to Whitelist object
        
    # Retrieve the data from the given file type.
    def retrieveFromFile(self, type):
        data = NList.jsonFromFile(
            MailFormatter.path(self.email, type + ".json")
        )
        
        if data is None:
            raise AuthorizationDataError(type, self.email)
        
        return data

    # Save the lists into their own files.
    def save(self):
        self.requests.saveFile()
        

# Representation of the requests as a list.
class AuthorizationRequestList(object):
    __slots__ = ['arr', 'auth', 'file_name']
    
    MAX_REQ_EMAILS = 1
    
    def __init__(self, authorization, file_name):
        self.file_name = file_name
        self.auth      = authorization
        self.arr       = authorization.retrieveFromFile(file_name)
    
    # Ask every requests to the user.
    def ask(self):
        oldest_date = datetime.now() - timedelta(days=30)
        
        # We can't iterate using a for loop.
        # Thanks Python ! :(
        while self.arr:
            request = self.arr[0]
            email = request.get('email')
            
            # If the request is not too old.
            if not (datetime.fromtimestamp(request.get('timestamp')) < oldest_date):
                # TODO make a console function
                val = input(email + " wants to contact you. Do you? [y/N] ")
                
                if val.lower() in ["y", "yes"]:
                    # TODO add to whitelist
                    # TODO ask for duration
                    print("OK")
                else:
                    # TODO add to blacklist
                    # TODO ask for duration
                    print("NOT OK")
                    self.remove(email)
            else:
                console.debug("Request from " + email + " too old")
                
            # In every case, delete the record.
            self.arr.pop(0)
           
    # Determine whether the given email address
    # already exists in the list. 
    def contains(self, addr):
        for request in self.arr:
            if request.get('email') == addr:
                return True
        
        return False
    
    # Get the list of the requested email files.
    def _requestedEmails(self, email_addr):
        return MailFormatter.filesFrom(self.auth.email, email_addr, folder='mails/requested')
          
    # Add an item to the request list.  
    def add(self, email_addr):
        EmailAddress.assertValidAddress(email_addr)
        
        # Calculate the number of sent emails.
        nbr_emails_received = len(self._requestedEmails(email_addr))
                
        # If too many emails were sent.
        if nbr_emails_received > AuthorizationRequestList.MAX_REQ_EMAILS:
            raise TooManyRequestError()
        
        # If a request already exists, don't do anything.
        if not self.contains(email_addr):
            self.arr.append({
                "email": email_addr,
                "timestamp": time.time()
            })
    
    # Remove the request from the given email address.
    # That doesn't remove the request in the JSON file
    # which is handled by the self.ask() method. 
    def remove(self, email_addr):
        files = self._requestedEmails(email_addr)
                
        for file in files:
            os.remove(
                MailFormatter.path(self.auth.email, "mails/requested/" + file)
            )
    
    # Update the request file with the current list.
    def saveFile(self):
        try:
            file_name = MailFormatter.path(
                self.auth.email, self.file_name + '.json'
            )
            with open(file_name, 'w') as f:
                f.write(json.dumps(self))
        except Exception as e:
            console.debug(e)
            
        
# Exception raised when the Authorization class
# couldn't retrieve sensible data regarding
# the given user.    
class AuthorizationDataError(CriticalError):
    def __init__(self, data, user):
        super().__init__(self, "Cannot retrieve " + data + " for user " + user)


# Exception raised when no valid
# SPF records were found in the
# DNS records.
class InvalidNinasSpfError(CriticalError): ...


# The given address is not NINAS-like.
class MalformedAddressError(CriticalError): ...


# Exception raised when a user sent too 
# many emails to someone didn't accepted
# his request before.
class TooManyRequestError(CriticalError): ...
