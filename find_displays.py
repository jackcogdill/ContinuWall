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
	arrangement = [Display(d.w, d.h, d.x, d.y, d.mirrored) for d in _arrangement]

	# Make all coordinates positive for printing
	minx = min([display.x for display in arrangement])
	miny = min([display.y for display in arrangement])
	newx = 0 if minx == 0 else -minx
	newy = 0 if miny == 0 else -miny
	for display in arrangement:
		display.x += newx
		display.y += newy

	# Scale down dimensions to display in terminal
	maxh = max([display.y + display.h for display in arrangement])
	div = maxh / max_height
	for display in arrangement:
		display.w = int(display.w / div)
		display.h = int(display.h / div)
		display.x = int(display.x / div)
		display.y = int(display.y / div)

	# Draw displays from left to right
	arrangement.sort(key=lambda display: display.x)

	print(color('cyan'))
	# Dimensions also same order
	_arrangement.sort(key=lambda display: display.x)
	for display in _arrangement:
		print(display, end=' ')
	print(color('reset'))

	total_lines = max([display.y + display.h for display in arrangement])
	lines = {line:'' for line in range(total_lines)}
	for display in arrangement:
		(w, h, x, y) = (display.w, display.h, display.x, display.y)

		box = {
			'top_left'    : u'\u250c',
			'top_right'   : u'\u2510',
			'bottom_left' : u'\u2514',
			'bottom_right': u'\u2518',
			'horiz'       : u'\u2500',
			'vert'        : u'\u2502'
		}

		if display.mirrored:
			for key, val in box.items():
				box[key] = color(val, 'yellow')

		# Because python 2 cannot use 'nonlocal' keyword
		outer = { 'index': 0 }

		def prnt_line(str):
			lines[ outer['index'] ] += str
			outer['index'] += 1

		# y offset
		for i in range(y):
			prnt_line(' ' * (w - 1) * 2)
		# First line
		prnt_line(box['top_left'] + box['horiz'] * (w - 2) * 2 + box['top_right'])
		# Middle lines
		for i in range(h - 2):
			prnt_line(box['vert'] + ' ' * (w - 2) * 2 + box['vert'])
		# Last line
		prnt_line(box['bottom_left'] + box['horiz'] * (w - 2) * 2 + box['bottom_right'])
		# x padding for future displays which go further down
		while outer['index'] < total_lines:
			prnt_line(' ' * (w - 1) * 2)
	for num, text in lines.items():
		print(text)

	if any([display.mirrored for display in arrangement]):
		print('Note: yellow displays are mirrored')

def main():
	arrangement_index = 0
	found = False
	while True:
		prnt_left = 'print :DisplayAnyUserSets:%d:' % arrangement_index

		if not test('"%s" -c "%s" "%s"' % (pbuddy, prnt_left, prefs)):
			break

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

			mirrored = display_attr('Mirrored') == 1
			prefix = '' if mirrored else 'Unmirrored'

			width   = display_attr(prefix + 'Width')
			height  = display_attr(prefix + 'Height')
			originX = display_attr(prefix + 'OriginX')
			originY = display_attr(prefix + 'OriginY')

			arrangement.append(Display(width, height, originX, originY, mirrored))

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
