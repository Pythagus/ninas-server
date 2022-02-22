from colorama import Fore

# Display a warning message and
# stop the process.
def warn(message):
    print(Fore.YELLOW + str(message) + Fore.RESET)
    