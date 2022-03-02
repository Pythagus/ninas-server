import colorama
import tempfile
import sys
import os


print("\n\n")
print("     ███╗   ██╗██╗███╗   ██╗ █████╗ ███████╗     ██████╗██╗     ██╗███████╗███╗   ██╗████████╗")
print("     ████╗  ██║██║████╗  ██║██╔══██╗██╔════╝    ██╔════╝██║     ██║██╔════╝████╗  ██║╚══██╔══╝")
print("     ██╔██╗ ██║██║██╔██╗ ██║███████║███████╗    ██║     ██║     ██║█████╗  ██╔██╗ ██║   ██║   ")
print("     ██║╚██╗██║██║██║╚██╗██║██╔══██║╚════██║    ██║     ██║     ██║██╔══╝  ██║╚██╗██║   ██║   ")
print("     ██║ ╚████║██║██║ ╚████║██║  ██║███████║    ╚██████╗███████╗██║███████╗██║ ╚████║   ██║   ")
print("     ╚═╝  ╚═══╝╚═╝╚═╝  ╚═══╝╚═╝  ╚═╝╚══════╝     ╚═════╝╚══════╝╚═╝╚══════╝╚═╝  ╚═══╝   ╚═╝  \n\n ")


LINE_START = "\t>>> "

print(colorama.Fore.BLUE + LINE_START + "Created by Damien Molina, Maud Pennetier and Elies Tali with " + colorama.Fore.MAGENTA + "💝\n")


src_email_addr = input(colorama.Fore.YELLOW +LINE_START +  "Source email adress : " + colorama.Fore.RESET)
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
            break


port = sys.argv[1]
status = os.system("python3 client.py " + port + " " + src_email_addr + " " + dst_email_addr + " '" + subject + "' " + file_name)


if status == 0:
    print(colorama.Fore.BLUE + LINE_START + "Thank you for using our mail service, see you !")
else:
    print("Something went wrong")


