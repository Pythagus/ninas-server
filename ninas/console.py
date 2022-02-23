from colorama import Fore

DEBUG = True

# Display a warning message and
# stop the process.
def warn(message):
    print(Fore.YELLOW + str(message) + Fore.RESET)

# Print a message only if the
# debug mode is enabled.
def debug(message):
    if DEBUG:
        print(message)
