from colorama import Fore
from sys import stderr


DEBUG = True


def error(message):
    print(Fore.RED + str(message) + Fore.RESET, file=stderr)

# Display a warning message and
# stop the process.
def warn(message):
    print(Fore.YELLOW + str(message) + Fore.RESET)

# Print a message only if the
# debug mode is enabled.
def debug(message):
    if DEBUG:
        print(message)
