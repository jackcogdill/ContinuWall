esc = '\033'
reset = '%s[0;m' % esc
default = reset
colors = {
	'red':    '%s[0;31m' % esc,
	'green':  '%s[0;32m' % esc,
	'yellow': '%s[0;33m' % esc,
	'blue':   '%s[0;34m' % esc,
	'cyan':   '%s[0;36m' % esc,
	'reset':  reset
}

def color(string, name=None):
	# Only return the color (no reset) or reset itself
	if name is None:
		return colors.get(string, default)
	# Sandwich the string in between the color and reset
	else:
		return '%s%s%s' % (
			colors.get(name, default),
			string,
			reset
		)
