from colorama import Fore, Back
from sys import stderr


# Determine whether the debugging mode
# is enabled.
DEBUG = True


# Every line start with this variable.
LINE_START = "  >>> "


# A blank start line with spaces.
BLANK_LINE_START = " " * len(LINE_START)


# Base console printer.
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


# Ask something to the user.
def ask(message, ending=True, choices=""):
    return input(Fore.YELLOW + LINE_START + message + (": " if ending else "") + Fore.RESET + choices)
