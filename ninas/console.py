from colorama import Fore, Back
from sys import stderr


# Determine whether the debugging mode
# is enabled.
DEBUG = True

def _print(message, slug="", back="", fore="", file=None):
    print(back + fore + slug + Back.RESET + Fore.RESET + (" " if len(slug) > 0 else "") + str(message), file=file)


# Display an error message.
def error(message):
    _print(message, " ERROR ", Back.RED, "", stderr)

# Display a warning message.
def warn(message):
    _print(message, " WARNING ", Back.YELLOW, Fore.BLACK)

# Print a message only if the
# debug mode is enabled.
def debug(message):
    if DEBUG:
        _print(message, " DEBUG ", Back.BLUE, Fore.BLACK)
