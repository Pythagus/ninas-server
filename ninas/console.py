from colorama import Fore
from sys import stderr


DEBUG = True


# Display an error message.
def error(message):
    print(Fore.RED + str(message) + Fore.RESET, file=stderr)

# Display a warning message.
def warn(message):
    print(Fore.YELLOW + str(message) + Fore.RESET)

# Print a message only if the
# debug mode is enabled.
def debug(message):
    if DEBUG:
        print(str(message))
