from pyPaint import *


ctx = Context(width=300, height=300)
#ctx.size(100, 200)
#ctx.background(1, 1, 1)

ctx.nofill()
ctx.strokewidth(0.5)
ctx.stroke(1, 0.0, 0.4)
ctx.rect(100, 10, 30, 10)

ctx.line(1, 2, 4, 5)

ctx.beginpath()
ctx.curveto(0, 60, 40, 100, 100, 100)
ctx.endpath()

ctx.star(100, 100)
ctx.save('temp.png')
