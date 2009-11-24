from pypaint.context          import *
from pypaint.utils.p_random   import random

ctx = Context(width=300, height=300)
#ctx.size(100, 200)
#ctx.background(1, 1, 1)
from math import sin, cos, tan, log10

ctx.background(0)

cX = random(1,10)
cY = random(1,10)

x = 200
y = 54

ctx.fontsize(10)

for i in range(278):
    x += cos(cY)*10
    y += log10(cX)*1.85 + sin(cX) * 5

    ctx.fill(random()-0.4, 0.8, 0.8, random())

    s = 10 + cos(cX)*15
    ctx.oval(x-s/2, y-s/2, s, s)
    # Try the next line instead of the previous one to see how
    # you can use other primitives.
    #star(x-s/2,y-s/2, random(5,10), inner=2+s*0.1,outer=10+s*0.1)

    cX += random(0.25)
    cY += random(0.25)


ctx.save('temp.png')
