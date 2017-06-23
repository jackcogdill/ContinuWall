# -*- coding: utf-8 -*-

# Compatibility for both Python 2 and 3
# =======================================
from __future__ import absolute_import, print_function
try:
	input = raw_input
except NameError:
	pass
# =======================================

import os.path
import subprocess
import pickle
from colors import color

# Class compatibility for both Python 2 and 3
__metaclass__ = type
class Display:
	def __init__(self, w, h, x, y, mirrored):
		self._w = w
		self._h = h
		self._x = x
		self._y = y
		self.mirrored = mirrored

	def __str__(self):
		return '%sx%s' % (self._w, self._h)

	def getw(self): return self._w
	def geth(self): return self._h
	def getx(self): return self._x
	def gety(self): return self._y
	def setw(self, value): self._w = value
	def seth(self, value): self._h = value
	def setx(self, value): self._x = value
	def sety(self, value): self._y = value

	w = property(fget=getw, fset=setw)
	h = property(fget=geth, fset=seth)
	x = property(fget=getx, fset=setx)
	y = property(fget=gety, fset=sety)

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
	maxh = max([display.h for display in arrangement])
	div = maxh / max_height
	for display in arrangement:
		display.w = int(display.w / div)
		display.h = int(display.h / div)
		display.x = int(display.x / div)
		display.y = int(display.y / div)

	# Draw displays from left to right
	arrangement.sort(key=lambda display: display.x)
	_arrangement.sort(key=lambda display: display.x)

	print_inside = all([len(str(_arrangement[i])) <= arrangement[i].w - 2 for i in range(len(arrangement))])
	if not print_inside:
		print(color('cyan'), end='')
		for display in _arrangement:
			print(display, end=' ')
		print(color('reset'))

	total_lines = max([display.y + display.h for display in arrangement])
	lines = {num : ('', 0) for num in range(total_lines)}
	for index in range(len(arrangement)):
		display = arrangement[index]
		_display = _arrangement[index]

		(w, h, x, y) = (display.w, display.h, display.x, display.y)

		box = {
			'top_left'    : '┌',
			'top_right'   : '┐',
			'bottom_left' : '└',
			'bottom_right': '┘',
			'horiz'       : '─',
			'vert'        : '│'
		}

		# Because python 2 cannot use 'nonlocal' keyword
		outer = { 'index': 0 }

		def prnt_line(text, num):
			current_line = lines[ outer['index'] ]
			current_text = current_line[0]
			current_num  = current_line[1]

			# Multi-layer arrangements overlap with 'x padding' that gets printed
			new_start = (x - 1) * 2
			if (
				current_num > new_start                and
				text.strip() != ''                     and # Only replace with non-whitespace
				current_text[new_start:].strip() == ''     # Only cut off whitespace
			):
				current_text = current_text[:new_start]
				current_num = new_start

			lines[ outer['index'] ] = (current_text + text, current_num + num)
			outer['index'] += 1

		# y offset
		for i in range(y):
			n = (w - 1) * 2
			prnt_line(' ' * n, n)

		# First line
		n = (w - 2) * 2
		prnt_line(box['top_left'] + box['horiz'] * n + box['top_right'], n + 2)

		# Middle lines
		vlines = h - 2
		vmid = int(vlines / 2) + (0 if vlines % 2 == 0 else 1)
		for i in range(vlines):
			text = ''
			n = (w - 2) * 2

			if (print_inside and i + 1 == vmid):
				dims = str(_display)
				text = dims.center(n, ' ')

				if display.mirrored:
					text = text.replace(dims, color(dims, 'yellow', 'black'))
			else:
				text = ' ' * n

			prnt_line(box['vert'] + text + box['vert'], n + 2)

		# Last line
		n = (w - 2) * 2
		prnt_line(box['bottom_left'] + box['horiz'] * n + box['bottom_right'], n + 2)

		# x padding for future displays which go further down
		while outer['index'] < total_lines:
			n = (w - 1) * 2
			prnt_line(' ' * n, n)

	for num, line in lines.items():
		print(line[0])

	if any([display.mirrored for display in arrangement]):
		print('Note: %s displays are mirrored' % color('highlighted', 'yellow', 'black'))

def find():
	# Setup
	# ===================================
	pbuddy = '/usr/libexec/PlistBuddy'
	prefs  = '/Library/Preferences/com.apple.windowserver.plist'

	if not os.path.isfile(pbuddy):
		print(color('Error: could not locate PlistBuddy', 'red'))
		exit(1)

	def test(command):
		# /dev/null
		try:
			from subprocess import DEVNULL
		except ImportError:
			import os
			DEVNULL = open(os.devnull, 'wb')

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
	# ===================================

	print('Will determine your display arrangement:')
	arrangement_index = 0
	found = False
	while True:
		prnt_left = 'print :DisplayAnyUserSets:%d:' % arrangement_index

		if not test('"%s" -c "%s" "%s"' % (pbuddy, prnt_left, prefs)):
			break

		arrangement = []
		print()

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

	return found
