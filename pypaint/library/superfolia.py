import sys
import os
sys.path.append(os.getcwd()) 

import supershape

from math import sqrt
from math import sin, cos, radians

from pypaint.context        import Context
from pypaint.types.color    import Color
from pypaint.utils.p_random import random

ctx = Context(width=600, height=600)

def radial_gradient(colors, x, y, radius, steps=200):
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
    for i in range(depth * random(10, 20)):
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
 

if __name__ == "__main__":
    radial_gradient(
        [Color(0.05, 0.06, 0.0), Color(0.125, 0.150, 0.0)],
        -150, -150,
        radius=900
    )

    root(300, 300, angle=-90, depth=8)
    ctx.save('test_images/superfolia.png')
