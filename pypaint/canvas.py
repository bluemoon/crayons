from pypaint.shape        import shape
from pypaint.mixins       import *
from pypaint.types.canvas import *
from pypaint.types.color  import Color
from pypaint.shape        import shape

class Canvas(CanvasMixin):
    def __init__(self, width=None, height=None, backend=PILCanvas, gtk_draw=False):
        CanvasMixin.__init__(self, width, height)
        self.backend = backend(width, height, gtk=gtk_draw)
        self.width  = width
        self.height = height
        self.gtk_draw = gtk_draw
        self.instant_draw = True

    def add(self, object):
        if self.instant_draw:
            self.backend.draw(stack=[object])
        else:
            self.data.append(object)

    def draw(self):
        self.backend.draw(stack=self.data)

    def show(self):
        self.backend.show()

    def save(self, filename, file_ext):
        self.backend.save(filename, file_ext)

    @property
    def width(self):
        return self.width


    @property
    def height(self):
        return self.height

    def background(self):
        s = shape()
        rect = s.rectangle(0, 0, self.width, self.height)
        return rect
    
    def gtk(self):
        return self.backend.gtk()

    def obstacles(self):
        for x in self.data:
            yield x

    def radial_gradient(self, colors=[Color(0.05, 0.06, 0.0), Color(0.18, 0.23, 0.28, 1.00)], x=-150, y=-150, radius=900, steps=200):
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
            Shape = shape()
            oval = Shape.oval(x+i, y+i, radius-i*2, radius-i*2)  
            oval.fill_color = _step(colors, i, steps)
            self.add(oval)
