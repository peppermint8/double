#! /usr/bin/env python
# -*- coding: utf-8 -*-



# ====================================================================== Colors

# standard colors
BLACK = "\033[1;30m"
RED   = "\033[1;31m"
GREEN = "\033[1;32m"
YELLOW = "\033[1;33m"
BLUE  = "\033[1;34m"
PINK = "\033[1;35m"
CYAN  = "\033[1;36m"
WHITE = "\033[1;37m"

# colors - 256 color mode
#https://www.ditig.com/256-colors-cheat-sheet
# FORMAT = "\033[38;5;--> color code <--m"
ORANGE = "\033[38;5;208m"
PURPLE = "\033[38;5;99m"
DEEP_PURPLE = "\033[38;5;57m"
BROWN = "\033[38;5;130m"
YELLOW_LT = "\033[38;5;191m"
ICE_BLUE = "\033[38;5;111m"
LIME_GREEN = "\033[38;5;48m"
STEEL_BLUE = "\033[38;5;147m"
GRAY = "\033[38;5;248m"
GREY = GRAY

BOLD    = "\033[;1m"
REVERSE = "\033[;7m"
RESET = "\033[m" # reset to normal


# MSG settings
MSG_OK =   "[ {} OK {} ]".format(GREEN, RESET)
MSG_PASS = "[ {}PASS{} ]".format(LIME_GREEN, RESET)
MSG_WARN = "[ {}WARN{} ]".format(YELLOW, RESET)
MSG_FAIL = "[ {}FAIL{} ]".format(RED, RESET)
