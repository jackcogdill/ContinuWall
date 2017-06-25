# Compatibility for both Python 2 and 3
# =======================================
from __future__ import absolute_import, print_function
__metaclass__ = type
try:
    input = raw_input
except NameError:
    pass
# =======================================


# Imports
import pickle
import displays
from ANSI import color
import sys
import os

ARRANGEMENT = None

def load_data():
    def load():
        try:
            with open(displays.DATA_FILE, 'rb') as file:
                global ARRANGEMENT
                ARRANGEMENT = pickle.load(file)
                return True
        except IOError:
            return False

    success = load()

    if success:
        print(color('Successfully loaded!', 'green'))
    elif displays.find():
        success = load()

    return success

def main():
    prog = sys.argv[0]
    usage = (
'''Welcome to image tile manager.
Split image(s) into tiles for each of your displays.

Usage: {0} <images>

Other options:
    {0} help                 display this help
    {0} <images>             split image(s) tiles
    {0} <prefix> <images>    specify a prefix for the tiles
    {0} config               change your preferred arrangement
    {0} clean                remove tiles
    {0} clean <prefix>       remove tiles with specific prefix'''
    ).format(prog)

    num_args = len(sys.argv)
    if num_args == 1:
        print(usage)
        exit(0)

    command = sys.argv[1]
    if command == 'help':
        print(usage)
        exit(0)
    elif command == 'config':
        try:
            os.remove(displays.DATA_FILE)
        except OSError:
            pass
        displays.find()
        exit(0)
    # elif command == 'clean':
    #     if num_args == 2:
    #     elif num_args == 3:
    #     else:
    #         print(usage)
    #         exit(0)

    if not load_data():
        print('Could not determine display arrangement.')
        exit(0)

    print('Using arrangement:')
    displays.print_arrangement(ARRANGEMENT)

# Run
main()
