from pypaint.mixins  import *
from pypaint.path    import path

import math

class shape(TransformMixin, ColorMixin):
    def __init__(self, **kwargs):
        ColorMixin.__init__(self, **kwargs)
        
    def rectangle(self, x, y, width, height, roundness=0.0, **kwargs):
        r = path(**kwargs)
        r.moveto(x, y)
        r.rellineto(width, 0)
        r.rellineto(0, height)
        r.rellineto(-width, 0)
        r.rellineto(0, -height)
        return r

    def arrow(self, x, y, width=100, type=NORMAL, **kwargs):
        if type == NORMAL:
            head = width * .4
            tail = width * .2
            
            p = path(**kwargs)
            p.moveto(x, y)
            p.lineto(x-head, y+head)
            p.lineto(x-head, y+tail)
            p.lineto(x-width, y+tail)
            p.lineto(x-width, y-tail)
            p.lineto(x-head, y-tail)
            p.lineto(x-head, y-head)
            p.lineto(x, y)
            p.closepath()
            return p
        elif type == FORTYFIVE:
            head = .3
            tail = 1 + head
            
            p = path(**kwargs)
            p.moveto(x, y)
            p.lineto(x, y+width*(1-head))
            p.lineto(x-width*head, y+width)
            p.lineto(x-width*head, y+width*tail*.4)
            p.lineto(x-width*tail*.6, y+width)
            p.lineto(x-width, y+width*tail*.6)
            p.lineto(x-width*tail*.4, y+width*head)
            p.lineto(x-width, y+width*head)
            p.lineto(x-width*(1-head), y)
            p.lineto(x, y)
            return p
        else:
          raise Exception("arrow: available types for arrow() ",
                          "are NORMAL and FORTYFIVE\n")



    def oval(self, x, y, width, height, **kwargs):
        r = path(**kwargs)
        r.ellipse(x, y, width, height)
        return r

    def ellipse(self, x, y, width, height, **kwargs):
        r = Path(**kwargs)
        r.ellipse(x, y, width, height)
        return r

    def circle(self, x, y, diameter):
        self.ellipse(x, y, diameter, diameter)

    def line(self, x1, y1, x2, y2):
        r = path()
        r.line(x1, y1, x2, y2)
        return r

    def star(self, startx, starty, points=20, outer=100, inner=50):
        Path = path()
        Path.moveto(startx, starty + outer)

        for i in range(1, int(2 * points)):
            angle = i * math.pi / points
            x = math.sin(angle)
            y = math.cos(angle)
            if i % 2:
                radius = inner
            else:
                radius = outer
            x = startx + radius * x
            y = starty + radius * y
            Path.lineto(x, y)

        Path.closepath()
        return Path
