from ninas.errors import CriticalError, Err
from datetime import datetime, timedelta
from ninas.security import EmailAddress
from ninas.utils import MailFormatter
from ninas import console
import json
import time
import os

JSON_INDENT = 4 if console.DEBUG else None 


# Base authorization list.
class AuthorizationList(object):
    __slots__ = ['arr', 'email', 'file_name']
    
    # Initialzie the authorization list.
    def __init__(self, file_name, email=None):
        self.email     = email
        self.file_name = file_name
        
        # Retrieve the list content from the file.
        with open(self._getPath(self.file_name), 'r') as f:
            content = f.read()

        self.arr = self._contentToArray(content)
        self._cleanContent()
    
    # Get the given file's path.
    def _getPath(self, file_name):
        return MailFormatter.path(self.email, file_name)
    
    # Convert the string content to an array.
    def _contentToArray(self, content):
        return content.split('\n')
    
    # Convert the array content to a string.
    def _arrayToContent(self, content):
        return '\n'.join(content)
    
    # Clean up the array value.
    def _cleanContent(self):
        # Remove the empty strings.
        filtered = filter(len, self.arr)
        
        self.arr = list(filtered)
    
    # Determine whether the list contains the
    # given value.
    def contains(self, value):
        return value in self.arr
    
    # Update the request file with the current list.
    def save(self):
        try:
            file_name = self._getPath(self.file_name)
            
            with open(file_name, 'w') as f:
                self._cleanContent()
                f.write(self._arrayToContent(self.arr))
        except Exception as e:
            console.debug(e)
            
    # Add an item to the request list.  
    def add(self, value):
        if not self.contains(value):
            self.arr.append(value)
    
     
# Users' blacklist list.
class BlackList(AuthorizationList):
    # Initialzie the authorization list.
    def __init__(self, email):
        super().__init__("blacklist.txt", email)
    
     
# Server's blacklist list.
class BlackListServer(BlackList):
    # Initialzie the authorization list.
    def __init__(self):
        super().__init__(None)
    
    
# Users' whitelist list.   
class WhiteList(AuthorizationList):
    # Initialzie the authorization list.
    def __init__(self, email):
        super().__init__("whitelist.txt", email)


# Request list to handle connections.
class RequestList(AuthorizationList):
    
    MAX_REQ_EMAILS = 1
    
    # Initialzie the authorization list.
    def __init__(self, email):
        super().__init__("requests.json", email)
      
    # Convert the string content to an array.
    # Override parent method.  
    def _contentToArray(self, content):
        return json.loads(content)
    
    # Convert the array content to a string.
    def _arrayToContent(self, content):
        return json.dumps(content, indent=JSON_INDENT)
    
    # Determine whether the list contains the
    # given value.
    def contains(self, address):
        value = address.get('email') if isinstance(address, dict) else str(address) 
        
        for request in self.arr:
            if request.get('email') == value:
                return True
        
        return False
        
    # Get the list of the requested email files.
    def _requestedEmails(self, email_addr):
        return MailFormatter.filesFrom(self.email, email_addr, folder='mails/requested')
    
    # Add an item to the request list.  
    def add(self, email_addr):
        EmailAddress.assertValidAddress(email_addr)
        
        # Calculate the number of sent emails.
        nbr_emails_received = len(self._requestedEmails(email_addr))
                
        # If too many emails were sent.
        if nbr_emails_received > RequestList.MAX_REQ_EMAILS:
            raise CriticalError(
                Err.TOO_MANY_REQUESTS, "From: " + email_addr
            )
        
        super().add({
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
            