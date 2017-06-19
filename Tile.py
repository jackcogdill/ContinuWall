# Compatibility for both Python 2 and 3
# =======================================
from __future__ import absolute_import, print_function
try:
	input = raw_input
except NameError:
	pass
# =======================================


# Imports
import pickle
import displays
from colors import color

arrangement = None
data = '.display_arrangement'

def load_data(fname):
	def load():
		try:
			with open(fname, 'rb') as file:
				global arrangement
				arrangement = pickle.load(file)
				return True
		except FileNotFoundError:
			return False

	success = load()

	if success:
		print(color('Successfully loaded arrangement!', 'green'))
	elif displays.find():
		success = load()

	return success

def main():
	if not load_data(data):
		print('Could not determine display arrangement.')
		exit(0)

	print('Your display:')
	displays.print_arrangement(arrangement)

# Run
main()
