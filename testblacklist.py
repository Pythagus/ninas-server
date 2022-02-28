from ninas.checks import Check
import sys

test = str(sys.argv[1])
Check.checkBlacklist(test)