# Compatibility for both Python 2 and 3
# -------------------------------------
from __future__ import absolute_import, print_function
try:
	input = raw_input
except NameError:
	pass
# -------------------------------------


# Imports
import os.path
import subprocess
from displays import Display
import pickle
from colors import color

pbuddy = '/usr/libexec/PlistBuddy'
prefs  = '/Library/Preferences/com.apple.windowserver.plist'

if not os.path.isfile(pbuddy):
	print('Error: could not locate PlistBuddy')
	exit(1)

# /dev/null
try:
	from subprocess import DEVNULL
except ImportError:
	import os
	DEVNULL = open(os.devnull, 'wb')

def test(command):
	try:
		subprocess.check_call(
			command,
			stdout=DEVNULL,
			stderr=DEVNULL,
			shell=True
		)
	except subprocess.CalledProcessError:
		return False

	return True

def print_arrangement(_arrangement, max_height=12):
	# Make a copy of the array to keep the originals intact
	arrangement = [Display(d.w, d.h, d.x, d.y) for d in _arrangement]
#====================================================================================
	# print('Before:')
	# for display in arrangement:
	# 	print('(%d, %d)' % (display.x, display.y))

	minx = min([display.x for display in arrangement])
	miny = min([display.y for display in arrangement])
	newx = 0 if minx == 0 else -minx
	newy = 0 if miny == 0 else -miny
	for display in arrangement:
		display.x += newx
		display.y += newy

	# print('After:')
	# for display in arrangement:
	# 	print('(%d, %d)' % (display.x, display.y))
#====================================================================================
	# print('Before:')
	# for display in arrangement:
	# 	print('(%d, %d, %d, %d)' % (display.w, display.h, display.x, display.y))

	maxh = max([display.y + display.h for display in arrangement])
	div = maxh / max_height

	for display in arrangement:
		display.w = int(display.w / div)
		display.h = int(display.h / div)
		display.x = int(display.x / div)
		display.y = int(display.y / div)

	# print('After:')
	# for display in arrangement:
	# 	print('(%d, %d, %d, %d)' % (display.w, display.h, display.x, display.y))
#====================================================================================
	# Draw displays from left to right
	arrangement.sort(key=lambda display: display.x)

	print(color('cyan'))
	for display in _arrangement:
		print(display, end=' ')
	print(color('reset'))

	total_lines = max([display.y + display.h for display in arrangement])
	lines = {line:'' for line in range(total_lines)}
	for display in arrangement:
		(w, h, x, y) = (display.w, display.h, display.x, display.y)

		top_left     = u'\u250c'
		top_right    = u'\u2510'
		bottom_left  = u'\u2514'
		bottom_right = u'\u2518'
		horiz        = u'\u2500'
		vert         = u'\u2502'

		# Because python 2 cannot use 'nonlocal' keyword
		outer = { 'index': 0 }

		def prnt_line(str):
			lines[ outer['index'] ] += str
			outer['index'] += 1

		# y offset
		for i in range(y):
			prnt_line(' ' * (w - 1) * 2)
		# First line
		prnt_line(top_left + horiz * (w - 2) * 2 + top_right)
		# Middle lines
		for i in range(h - 2):
			prnt_line(vert + ' ' * (w - 2) * 2 + vert)
		# Last line
		prnt_line(bottom_left + horiz * (w - 2) * 2 + bottom_right)
		# x padding for future displays which go further down
		while outer['index'] < total_lines:
			prnt_line(' ' * (w - 1) * 2)
	for num, text in lines.items():
		print(text)

	if [display.x for display in arrangement].count(0) > 1:
		print(color('Note: this arrangement may be mirrored', 'yellow'))

def main():
	arrangement_index = 0
	found = False
	while True:
		prnt_left = 'print :DisplayAnyUserSets:%d:' % arrangement_index

		if not test('"%s" -c "%s" "%s"' % (pbuddy, prnt_left, prefs)):
			break

		# subprocess.call('clear', shell=True)
		print()

		arrangement = []

		display = 0
		while test('"%s" -c "%s%d" "%s"' % (pbuddy, prnt_left, display, prefs)):
			display_attr = lambda attr: int(
				subprocess.check_output(
					'"%s" -c "%s%d:%s" "%s"' % (pbuddy, prnt_left, display, attr, prefs),
					universal_newlines=True,
					shell=True
				).rstrip()
			)

			width   = display_attr('Width')
			height  = display_attr('Height')
			originX = display_attr('OriginX')
			originY = display_attr('OriginY')

			arrangement.append(Display(width, height, originX, originY))

			display += 1

		print_arrangement(arrangement)

		print()
		read = input('Is this your display arrangement? [y/N] ')
		if read and read in 'yY':
			found = True
			fname = '.display_arrangement'
			try:
				with open(fname, 'wb') as file:
					pickle.dump(arrangement, file, protocol=2)
					print(color('Successfully recorded!', 'green'))
			except Exception:
				print(color('Error storing display arrangement data in "%s"' % fname, 'red'))
			break

		arrangement_index += 1

	if not found:
		print(color('No display arrangement chosen. Nothing recorded.', 'red'))

# Run program
main()

# More testing
# subprocess.call('clear', shell=True)
# print('Arrangement at work:')
# print()

# arrangement = [
# 	Display(1920, 1200, 0, 0),
# 	Display(1920, 1200, -1920, 0),
# 	Display(1440, 900, 1920, 300)
# ]

# print_arrangement(arrangement)
