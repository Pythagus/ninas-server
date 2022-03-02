from colorama import Fore, Back, Style
from ninas import security
from ninas import console
from ninas import errors
import tempfile
import shutil
import sys
import os

ASCII_ART = [
    "███╗   ██╗██╗███╗   ██╗ █████╗ ███████╗     ██████╗██╗     ██╗███████╗███╗   ██╗████████╗",
    "████╗  ██║██║████╗  ██║██╔══██╗██╔════╝    ██╔════╝██║     ██║██╔════╝████╗  ██║╚══██╔══╝",
    "██╔██╗ ██║██║██╔██╗ ██║███████║███████╗    ██║     ██║     ██║█████╗  ██╔██╗ ██║   ██║   ",
    "██║╚██╗██║██║██║╚██╗██║██╔══██║╚════██║    ██║     ██║     ██║██╔══╝  ██║╚██╗██║   ██║   ",
    "██║ ╚████║██║██║ ╚████║██║  ██║███████║    ╚██████╗███████╗██║███████╗██║ ╚████║   ██║   ",
    "╚═╝  ╚═══╝╚═╝╚═╝  ╚═══╝╚═╝  ╚═╝╚══════╝     ╚═════╝╚══════╝╚═╝╚══════╝╚═╝  ╚═══╝   ╚═╝   ",
]

# Get the max width.
# All the lines have the same width.
ASCII_ART_WIDTH = len(ASCII_ART[0])

# Get the terminal width.
TERM_WIDTH = shutil.get_terminal_size().columns

# Every line start with this variable.
LINE_START = "  >>> "

# Get the required padding to center a text.
def getPadding(el):
    return int(.5 * (TERM_WIDTH - el))

# Center the text adding spaces.
def center(message):
    return " " * getPadding(len(message)) + message

# Ask something to the user.
def ask(message):
    return input(Fore.YELLOW + LINE_START + message + ": " + Fore.RESET)

# Display a section title.
def section_title(title):
    print(Back.YELLOW + Fore.BLACK + " " + title + " " + Back.RESET + Fore.RESET)

# If the terminal is large enough.
if ASCII_ART_WIDTH <= TERM_WIDTH:
    # Spaces padding.
    padding = getPadding(ASCII_ART_WIDTH)
    
    # Add the padding to the ASCII ART.
    ASCII_ART = ["{}{}".format(" " * padding, line) for line in ASCII_ART]
    
# Else, we print a smaller title.
else:
    title   = "NINAS CLIENT"
    padding = getPadding(len(title))
    
    ASCII_ART = [
        Fore.YELLOW + "‾" * TERM_WIDTH,
        Style.BRIGHT + center(title) + Style.RESET_ALL,
        Fore.YELLOW + "_" * TERM_WIDTH + Fore.RESET,
        "\n"
    ]

# Print the ASCII ART.
print("\n")
print("\n".join(ASCII_ART))
print(Fore.BLUE + center("Created by Damien Molina, Maud Pennetier and Elies Tali with 💝") + Fore.RESET)
print("\n")

# Display a warning message on too small terminal.
if ASCII_ART_WIDTH > TERM_WIDTH:
    console.warn("You should use a bigger screen")
    print()

# Logged-in email account.
print("You are logged as " + Fore.GREEN + "elies@dmolina.fr" + Fore.RESET + ".")
print()
section_title("Write an email")

# Ask for the destination email address.
dst_email_addr = ask("Destination email adress")
try:
    security.EmailAddress.assertValidAddress(dst_email_addr)
except errors.CriticalError as e:
    console.error(e)
    console.error("Aborting.\n")
    sys.exit(e.args[0])

subject = ask("Subject of the mail")

print(Fore.YELLOW + LINE_START + "Content of the mail (Ctrl-D to save it.): " + Fore.RESET)


file_name = ""
with tempfile.NamedTemporaryFile(delete=False) as f:
    file_name = f.name
    while True:
        try:
            line = input(" " * len(LINE_START))
            print("LINE = " + line)
            f.write(bytes(line + "\n", 'utf-8'))
        except EOFError:
            break


port = sys.argv[1]
status = os.system("python3 client.py " + port + " " + src_email_addr + " " + dst_email_addr + " '" + subject + "' " + file_name)

if status == 0:
    print(Fore.BLUE + LINE_START + "Thank you for using our mail service, see you !")
else:
    console.error("An error occurred.")
