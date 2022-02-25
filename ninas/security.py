from ninas.error import CriticalError, Err
from ninas import console
import dns.resolver
import re


class Address(object):
    SERVER_ADDR_START = 'ninas.'
    
    # Check whether the given NINAS server
    # address is valid.
    @staticmethod
    def getNinasServer(address):
        if not address.startswith(Address.SERVER_ADDR_START):
            raise MalformedNinasAddressError(
                "NINAS server address must start with '" + Address.SERVER_ADDR_START + "'"
            )

        return address[len(Address.SERVER_ADDR_START):]
    
    # Check whether the given email address
    # is valid.
    @staticmethod
    def checkEmailAddress(address):
        # TODO
        pass


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


# Exception raised when no valid
# SPF records were found in the
# DNS records.
class InvalidNinasSpfError(CriticalError): ...

# The given address is not NINAS-like.
class MalformedNinasAddressError(CriticalError): ...