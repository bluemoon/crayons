from pyPaint import *

ctx = PyPaintContext()
#ctx.size(100, 200)
#ctx.background(1, 1, 1)

#ctx.nofill()
#ctx.strokewidth(0.5)
#ctx.stroke(0.3, 0.0, 0.4)
ctx.rect(10, 10, 30, 10)

ctx.line(1, 2, 4, 5)
ctx.line(4, 2, 4, 5)

ctx.beginpath()
ctx.curveto(0, 60, 40, 100, 100, 100)
ctx.endpath()

ctx.star(10, 10)
ctx.save('temp.png')
