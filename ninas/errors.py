# Error enumerate object with identifiers.
class Err(object):
    USER_NOT_FOUND        = 404
    DOMAIN_NOT_FOUND      = 405
    DOMAIN_SPF            = 406
    INVALID_NINAS_DOMAIN  = 407
    INVALID_EMAIL_ADDRESS = 408
    TOO_MANY_REQUESTS     = 409
    BLACKLISTED           = 410
    MISSING_FOLDER        = 411
    
# Base NINAS runtime error.
class NinasRuntimeError(RuntimeError): ...

# Critical error stopping the socket.
class CriticalError(NinasRuntimeError): 
    __slots__ = ['type', 'message']
    
    def __init__(self, type, message):
        self.type = type
        self.message = message
        
    # Custom string version of the error.
    def __str__(self):
         return self.message + " (code: " + str(self.type) + ")"
