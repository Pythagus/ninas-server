import sys
import colorama
from colorama.initialise import colorama_text
import tempfile
import os
from ninas.requests import HelloServerRequest, MailUsersRequest, MailPayloadRequest
from ninas.responses import HelloServerResponse, MailUsersResponse
from ninas.utils import NinasRuntimeError
from ninas.security import EmailAddress
from ninas.network import NetworkTools
from ninas import console
import socket
import time
import sys



colorama.init()

print("\n\n")
print("     ███╗   ██╗██╗███╗   ██╗ █████╗ ███████╗     ██████╗██╗     ██╗███████╗███╗   ██╗████████╗")
print("     ████╗  ██║██║████╗  ██║██╔══██╗██╔════╝    ██╔════╝██║     ██║██╔════╝████╗  ██║╚══██╔══╝")
print("     ██╔██╗ ██║██║██╔██╗ ██║███████║███████╗    ██║     ██║     ██║█████╗  ██╔██╗ ██║   ██║   ")
print("     ██║╚██╗██║██║██║╚██╗██║██╔══██║╚════██║    ██║     ██║     ██║██╔══╝  ██║╚██╗██║   ██║   ")
print("     ██║ ╚████║██║██║ ╚████║██║  ██║███████║    ╚██████╗███████╗██║███████╗██║ ╚████║   ██║   ")
print("     ╚═╝  ╚═══╝╚═╝╚═╝  ╚═══╝╚═╝  ╚═╝╚══════╝     ╚═════╝╚══════╝╚═╝╚══════╝╚═╝  ╚═══╝   ╚═╝  \n\n ")


LINE_START = "\t>>> "

print(colorama.Fore.BLUE + LINE_START + "Created by Damien Molina, Maud Pennetier and Elies Tali with " + colorama.Fore.MAGENTA + "💝\n")


print(colorama.Fore.RED + LINE_START + "You are logged as elies@dmolina.fr.")

dst_email_addr = input(colorama.Fore.YELLOW +LINE_START +  "Destination email adress : " + colorama.Fore.RESET)
subject = input(colorama.Fore.YELLOW + LINE_START + "Subject of the mail : " + colorama.Fore.RESET)

print(colorama.Fore.YELLOW + LINE_START + "Content of the mail (Ctrl-D to save it.): " + colorama.Fore.RESET)


file_name = ""
with tempfile.NamedTemporaryFile(delete=False) as f:
    file_name = f.name
    while True:
        try:
            line = input("\t")
            f.write(bytes(line + "\n", 'utf-8'))
        except EOFError:
            print("ctrl d merde")
            break


port = sys.argv[1]
status = os.system("python3 client.py " + port + " " + dst_email_addr + " '" + subject + "' " + file_name)


if status == 0:
    print(colorama.Fore.BLUE + LINE_START + "Thank you for using our mail service, see you !")
else:
    print("Something went wrong")


