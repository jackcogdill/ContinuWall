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

ARRANGEMENT = None

def load_data(fname):
    def load():
        try:
            with open(fname, 'rb') as file:
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
    if not load_data(displays.DATA_FILE):
        print('Could not determine display arrangement.')
        exit(0)

    print('Using arrangement:')
    displays.print_arrangement(ARRANGEMENT)

# Run
main()
