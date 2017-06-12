class Display:
	def __init__(self, w, h, x, y):
		self._w = w
		self._h = h
		self._x = x
		self._y = y

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
