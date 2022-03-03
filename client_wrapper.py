from colorama import Fore, Back, Style
from ninas.lists import BlackList, RequestList, WhiteList
from ninas import security
from ninas import console
from ninas import errors
from simple_term_menu import TerminalMenu
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


#Menu options

MAIN_OPTIONS = ["Write an email", "Check incoming requests", "Manage whitelist", "Manage blacklist", "Log out"]
WHITELIST_OPTIONS = ["Display your whitelist", "Add to the whitelist", "Remove from the whitelist", "Go to main menu"]
BLACKLIST_OPTIONS = ["Display your blacklist", "Add to the blacklist", "Remove from the blacklist", "Go to main menu"]

# OPTIONS IDEXES

WRITE_MAIL = 0
REQUESTS = 1
WHITELIST = 2
BLACKLIST = 3
LOG_OUT = 4

DISPLAY_LIST = 0
ADD_LIST = 1
REMOVE_LIST = 2


# Get the required padding to center a text.
def getPadding(el):
    return int(.5 * (TERM_WIDTH - el))

# Center the text adding spaces.
def center(message):
    return " " * getPadding(len(message)) + message

# Display a section title.
def section_title(title):
    print(Back.YELLOW + Fore.BLACK + " " + title + " " + Back.RESET + Fore.RESET)

def menu_title(title):
    print(Back.GREEN + Fore.BLACK + " " + title + " " + Back.RESET + Fore.RESET)

#Display options and returns the choice
def displayOptions(options, text_to_show=None, multiple_choise=False):
    if text_to_show != None:
        menu_title(text_to_show)
    if not multiple_choise:
        terminal_menu = TerminalMenu(options)
    else:
        terminal_menu = TerminalMenu(options, multi_select=True, show_multi_select_hint=True, multi_select_empty_ok=True, multi_select_select_on_accept=False)
    index = terminal_menu.show()
    print()
    return index


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
    

# Ask an email address to the user.
def ask_email(message):
    addr = console.ask(message)
    
    try:
        security.EmailAddress.assertValidAddress(addr)
    except errors.CriticalError as e:
        console.error(e)
        console.error("Aborting.\n")
        sys.exit(42)
        
    return addr


# Ask for the destination email address.
src_email_addr = ask_email("Your email address")
print()

# Check whether the user exists on the server.
try:
    security.EmailAddress.assertUserExists(src_email_addr)
except errors.CriticalError as e:
    console.error(e)
    console.error("Aborting.\n")
    sys.exit(42)

option = 0

while option != LOG_OUT:

    # Open the main menu
    option = displayOptions(MAIN_OPTIONS, "What do you want to do today, " + src_email_addr + " ?")


    if option == REQUESTS:
        # Ask for requests.
        section_title("Requests")
        request = RequestList(src_email_addr)

        if request.isEmpty():
            print(console.BLANK_LINE_START + "No requests.")
        else:
            request.ask()
            request.save()

        print()

    elif option == WRITE_MAIL:
        # Write an email.
        section_title("Write an email")

        # Ask for the destination email address.
        dst_email_addr = ask_email("Destination email adress")

        subject = console.ask("Subject of the mail")

        print(Fore.YELLOW + console.LINE_START + "Content of the mail (Ctrl-D to save it.): " + Fore.RESET)


        file_name = ""
        with tempfile.NamedTemporaryFile(delete=False) as f:
            file_name = f.name
            while True:
                try:
                    line = input(console.BLANK_LINE_START)
                    f.write(bytes(line + "\n", 'utf-8'))
                except EOFError:
                    break


        port = sys.argv[1]
        status = os.system("python3 client.py " + port + " " + src_email_addr + " " + dst_email_addr + " '" + subject + "' " + file_name)

        if status == 0:
            print(Fore.BLUE + console.LINE_START + "No problems detected while sending your mail, congrats !")
        else:
            console.error("An error occurred.")

    # Whitelist and blacklist management
    elif option == WHITELIST or option == BLACKLIST:

        if option == WHITELIST:
            name = "Whitelist"
            my_list = WhiteList(src_email_addr)
            # Open the menu for my_list
            option = displayOptions(WHITELIST_OPTIONS, name + " Menu")

        else :
            name = "Blacklist"
            my_list = BlackList(src_email_addr)
            # Open the menu for the list
            option = displayOptions(BLACKLIST_OPTIONS, name + " Menu")


        # Display the my_list
        if option == DISPLAY_LIST:

            section_title(name + " display")
            if my_list.isEmpty():
                print(console.BLANK_LINE_START + "Empty " + name)
            else:
                for email in my_list.arr:
                    print(console.BLANK_LINE_START + "⦿ " + email)
            print()

        elif option == ADD_LIST:
            # Add a user to our my_list
            section_title("Add to " + name)
            user = console.ask("Who do you want to add to your " + name)
            try:
                security.EmailAddress.assertValidAddress(user)
                if user != "":
                    my_list.add(user)
                    my_list.save()
                    print(Fore.CYAN + console.BLANK_LINE_START + user + " added to your " + name)

            except errors.CriticalError as e:
                console.warn(e)
                console.warn("This address in not a valid email address")

                print()

        elif option == REMOVE_LIST:
            # Remove one a multiple users from the my_list
            if my_list.isEmpty():
                section_title("Remove from " + name)
                print(console.BLANK_LINE_START + "Empty " + name)
            else:
                array = my_list.arr.copy()
                section_title("Remove from " + name)
                indexes = displayOptions(my_list.arr, multiple_choise=True)
                if indexes != None:
                    for i in indexes:
                        my_list.remove(array[i])
                    my_list.save()
                    print(Fore.CYAN + console.BLANK_LINE_START + "Users succesfully removed from your " + name)
            print()



print(Fore.BLUE + console.LINE_START + "Thank you for using our mail service, see you !\n" + Fore.RESET)
