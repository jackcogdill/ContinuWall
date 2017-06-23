esc = '\033'
reset = '%s[0m' % esc

colors = {
	'black':   '0',
	'red':     '1',
	'green':   '2',
	'yellow':  '3',
	'blue':    '4',
	'magenta': '5',
	'cyan':    '6',
	'white':   '7',
	'reset':   reset
}

def color(string, color_name=None, background=None, bold=False):
	# Only return the color (no reset) or reset itself
	if color_name is None and background is None:
		return colors.get(string)
	# Sandwich the string in between the color and reset
	else:
		prefix = reset

		if string != 'reset':
			fg_color = (
				('3%s' % colors.get(color_name))
				if color_name is not None
				else '0'
			)
			bg_color = (
				('4%s' % colors.get(background))
				if background is not None
				else ''
			)

			prefix = '%s[%s;%sm' % (esc, fg_color, bg_color)

			if bold:
				prefix += '%s[1m' % esc

		return '%s%s%s' % (
			prefix,
			string,
			reset
		)
