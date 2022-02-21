import colorama


class Console(object):

    @staticmethod
    def error(message, code=42):
        print(colorama.Fore.COLOR_RED + message + colorama.Fore.RESET)
        exit(code)