from ninas.lists import BlackList, RequestList, WhiteList
from simple_term_menu import TerminalMenu
from colorama import Fore, Back, Style
from ninas import security
from ninas import console
from ninas import errors
from ninas.imap import MailRetriever
from ninas.utils import MailInfo
import tempfile
import shutil
import sys
import datetime
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

MAIN_OPTIONS = ["Write an email", "Check incoming requests", "Manage whitelist", "Manage blacklist", "Go to your email box", "Log out"]
WHITELIST_OPTIONS = ["Display your whitelist", "Add to the whitelist", "Remove from the whitelist", "Go to main menu"]
BLACKLIST_OPTIONS = ["Display your blacklist", "Add to the blacklist", "Remove from the blacklist", "Go to main menu"]
MAIL_BOX_OPTIONS = ["Check your mailbox", "Check your sent emails", "Go to main menu"]

# OPTIONS IDEXES

WRITE_MAIL = 0
REQUESTS = 1
WHITELIST = 2
BLACKLIST = 3
EMAIL_BOX = 4
LOG_OUT = 5

DISPLAY_LIST = 0
ADD_LIST = 1
REMOVE_LIST = 2

CHECK_MAILBOX = 0
CHECK_SENTMAILS = 1


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
def displayOptions(options, text_to_show=None, multiple_choice=False):
    if text_to_show != None:
        menu_title(text_to_show)
    if not multiple_choice:
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

# Displays the payload and info of the mail stored in file
def displayMail(mail):
    if mail.flag != []:
        print(Fore.RED + console.BLANK_LINE_START + "⚠ This mail has the following security flags : " + Back.YELLOW + ",".join(mail.flag) + Back.RESET + ", be careful !" + Fore.RESET)
    print(Fore.YELLOW +  console.BLANK_LINE_START  + "FROM : " + Fore.RESET + mail.fullSrcAddr())
    print(Fore.YELLOW +  console.BLANK_LINE_START  +"TO : " + Fore.RESET +mail.fullDstAddr())
    print(Fore.YELLOW +  console.BLANK_LINE_START  +"SENT AT : " + Fore.RESET +str(datetime.datetime.fromtimestamp(int(float(mail.sent_date)))))
    if (mail.received_date != None):
        print(Fore.YELLOW +  console.BLANK_LINE_START  + "RECEIVED AT " + Fore.RESET +str(datetime.datetime.fromtimestamp(int(float(mail.received_date)))))
    print(Fore.YELLOW +  console.BLANK_LINE_START  +"CONTENT : " + Fore.RESET)
    print(str(mail.getPayload()))
    print(center(Back.BLUE + " " * int(TERM_WIDTH *0.7) + Back.RESET))
    print()

def getMailName(mail):
    if mail.flag == None:
        return mail.fullSrcAddr()  +" -- " +mail.subject + " -- " +str(datetime.datetime.fromtimestamp(int(float(mail.sent_date))))
    else:
        return  mail.fullSrcAddr()  + " -- " + mail.subject +  " -- " + str(datetime.datetime.fromtimestamp(int(float(mail.sent_date)))) +  " -- " +"⚠SECURITY_FLAGS"





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


        ninas_port = sys.argv[1]
        imap_port  = sys.argv[2]
        status = os.system("python3 client.py " + ninas_port + " " + imap_port + " " + src_email_addr + " " + dst_email_addr + " '" + subject + "' " + file_name)

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
                indexes = displayOptions(my_list.arr, multiple_choice=True)
                if indexes != None:
                    for i in indexes:
                        my_list.remove(array[i])
                    my_list.save()
                    print(Fore.CYAN + console.BLANK_LINE_START + "Users succesfully removed from your " + name)
            print()

    # Open the mail box
    elif option == EMAIL_BOX:
        option = displayOptions(MAIL_BOX_OPTIONS, "Mailbox Menu")

        retriever = MailRetriever(src_email_addr)
        try:
            retriever.start(8001)
        except Exception as e:
            retriever.clean()
            console.error(e)
            sys.exit(e.args[0])

        # Check the mails received
        if option  == CHECK_MAILBOX:
            section_title("Mailbox")

            mailbox = []
            mailbox_options = []
            for filename in os.listdir(retriever.folder):
                if filename.endswith('.mail'):
                    mailbox.append(MailInfo.fromFile(retriever.folder + "/" + filename))
                    mailbox_options.append(getMailName(mailbox[-1]))
            if mailbox == []:
                print(console.BLANK_LINE_START + "Empty mailbox")
            else:
                indexes = displayOptions(mailbox_options, "Choose the mails you want to open", multiple_choice=True)
                if indexes != None:
                    for i in indexes:
                        displayMail(mailbox[i])

        # Check the mails sent
        elif option == CHECK_SENTMAILS:
            section_title("Sent mailbox")

            mailbox = []
            mailbox_options = []
            if os.path.isdir(retriever.folder + "/sent"):
                for filename in os.listdir(retriever.folder + "/sent"):
                    if filename.endswith('.mail'):
                        mailbox.append(MailInfo.fromFile(retriever.folder + "/sent/" + filename))
                        mailbox_options.append(getMailName(mailbox[-1]))
                console.debug(mailbox_options)
                indexes = displayOptions(mailbox_options, "Choose the mails you want to open", multiple_choice=True)
                if indexes != None:
                    for i in indexes:
                        displayMail(mailbox[i])
            else:
                print(console.BLANK_LINE_START + "Empty sent mailbox")
              
print(Fore.BLUE + console.LINE_START + "Thank you for using our mail service, see you !\n" + Fore.RESET)
