import sys
import os
sys.path.append(os.getcwd()) 

import supershape

from math import sqrt
from math import sin, cos, radians

from pyPaint import PyPaintContext as Context
from nb_types.new_color import Color
from util_random import random

ctx = Context(width=600, height=600)

def radial_gradient(colors, x, y, radius, steps=300):
    """ Radial gradient using the given list of colors. """
    def _step(colors, i, n):
        l = len(colors)-1
        a = int(1.0*i/n*l)
        a = min(a+0, l)
        b = min(a+1, l)
        base = 1.0 * n/l * a
        d = (i-base) / (n/l)
        r = colors[a].r*(1-d) + colors[b].r*d
        g = colors[a].g*(1-d) + colors[b].g*d
        b = colors[a].b*(1-d) + colors[b].b*d
        return Color(r, g, b)
 
    for i in range(steps):
        ctx.fill(_step(colors, i, steps))
        ctx.oval(x+i, y+i, radius-i*2, radius-i*2)  
 
def root(x, y, angle=0, depth=5, alpha=1.0, decay=0.005):
    """ Recursive root branches to smaller roots.
    """
    w = depth * 6
    for i in range(depth * random(10,20)):
        v = float(depth)/5
        alpha -= i * decay
        alpha = max(0, alpha)
        
        if alpha > 0:
            # Next direction to grow in.,
            # e.g. between -60 and 60 degrees of current heading.
            angle += random(-60, 60)
            dx = x + cos(radians(angle)) * w
            dy = y + sin(radians(angle)) * w
            
            # Oval dropshadow.
            ctx.nostroke()
            ctx.fill(0, 0, 0, alpha*0.25)
            ctx.oval(x-w/6+depth, y-w/6+depth, w/3, w/3)
 
            # Line segment to next position.
            ctx.nofill()
            ctx.stroke(0.8-v*0.25, 0.8, 0.8-v, alpha)
            ctx.strokewidth((depth + 1)*0.5)

            ctx.line(x, y, dx, dy)

            
            # Colored oval.
            ctx.strokewidth((depth+1)*0.25)
            ctx.fill(0.8-v*0.25, 0.8, 0.8-v, alpha*0.5)
            ctx.oval(x-w/6, y-w/6, w/3, w/3)
            
            # Create a branching root.
            if random() > 0.8 and depth > 0:
                root(x, y, angle, depth-1, alpha)
            
            x = dx
            y = dy
    
    # Continue growing at less alpha and depth.
    if depth > 0:
        root(x, y, angle, depth-1, alpha)
 
radial_gradient(
    [Color(0.05, 0.06, 0.0), Color(0.125, 0.150, 0.0)],
    -150, -150,
    radius=900
) 
root(300, 300, angle=-90, depth=6)

def flower(x, y, r): 
    em = 10
    n1 = 1.35
    n2 = -0.8 + random(-0.2)
    n3 = 0.4
    points = 400
    
    w = h = r
    p = supershape.path(ctx, x+20, y+20, w, h, em, n1, n2, n3, points)
    ctx.fill(0,0,0, 0.5)
    ctx.nostroke()
    ctx.drawpath(p)
    
    n = 20
    w = h = r + n
    for i in range(n):
        p = supershape.path(ctx, x, y, w, h, em, n1, n2, n3, points)
        w -= 4
        h -= 4
        d = float(i)/n
        ctx.fill(1, d, d+0.25, 0.1)
        ctx.stroke(1,0,0.2)
        ctx.strokewidth(0.25)
        ctx.drawpath(p)
        
#ctx.nofill()
#ctx.stroke(0)
#x, y = 259, 434
# 
#for i in range(20):
#    ctx.rotate(random(360))
#    flower(200+random(200), 200+random(200), random(10,100-i*4))

ctx.save('')
