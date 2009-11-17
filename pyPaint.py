import util

from PIL               import Image
from types.transform   import Transform
from types.canvas      import PILCanvas, BezierPath
from types.color       import Color

from defaults          import *
from math              import *
from aggdraw           import *

class Context:
    def __init__ (self, inputscript=None, targetfilename=None, canvas=None, gtkmode=False, ns=None, width=None, height=None):
        self.inputscript    = inputscript
        self.targetfilename = targetfilename

        # init internal path container
        self._path = None
        self._autoclosepath = True

        self.color_range = 1.
        self.color_mode = RGB

        self._fillcolor = self.color(.2)
        self._strokecolor = None
        self._strokewidth = 1.0

        self._transform = Transform()
        self._transformmode = CENTER
        self.transform_stack = []

        self._font     = "Verdana"
        self._fontsize = 10
        self._align    = LEFT
        self._lineheight = 1

        self.vars = []
        self._oldvars = self.vars
        self.namespace = {}

        self.framerate = 30
        self.FRAME = 0

        self.screen_ratio = None

        if width and height:
            self.WIDTH  = width
            self.HEIGHT = height
        else:
            self.WIDTH  = DEFAULT_WIDTH
            self.HEIGHT = DEFAULT_HEIGHT

        if canvas:
            self.canvas = canvas
        else:
            self.canvas = PILCanvas(width=self.WIDTH, height=self.HEIGHT)

        # from nodebox
        if ns is None:
            ns = {}
            self._ns = ns


    def snapshot(self, filename=None):
        pass

    def save(self, filename=None):
        #self.canvas.flush()
        self.canvas.draw()
        self.canvas.output(filename, "PNG")
        self.canvas.show()
    
    def size(self, width, height):
        self.WIDTH  = width
        self.HEIGHT = height
        self._ns["WIDTH"] = width
        self._ns["HEIGHT"] = height
    
    def image(self, path, x, y, width=None, height=None, alpha=1.0, data=None, draw=True, **kwargs):
        '''Draws a image form path, in x,y and resize it to width, height dimensions.
        '''
        r = self.Image(path, x, y, width, height, alpha, data, **kwargs)
        if draw:
            self.canvas.add(r)

        return r

    def imagesize(self, path):
        img = Image.open(path)
        return img.size

    def rect(self, x, y, width, height, roundness=0.0, draw=True, **kwargs):
        '''
        Draws a rectangle with top left corner at (x,y)
        The roundness variable sets rounded corners.
        '''
        r = self.BezierPath(**kwargs)
        r.rect(x, y, width, height)

        if draw:
            self.canvas.add(r)

        return r

    def rectmode(self, mode=None):
        if mode in (self.CORNER, self.CENTER, self.CORNERS):
            self.rectmode = mode
            return self.rectmode
        elif mode is None:
            return self.rectmode
        else:
            raise Exception("rectmode: invalid input")

    def oval(self, x, y, width, height, draw=True, **kwargs):
        '''Draws an ellipse starting from (x,y) -  ovals and ellipses are not the same'''
        r = self.BezierPath(**kwargs)
        r.ellipse(x, y, width, height)

        if draw:
            self.canvas.add(r)

        return r

    def ellipse(self, x, y, width, height, draw=True, **kwargs):
        '''Draws an ellipse starting from (x,y)'''
        r = self.BezierPath(**kwargs)
        r.ellipse(x, y, width, height)

        if draw:
            self.canvas.add(r)

        return r

    def circle(self, x, y, diameter):
        self.ellipse(x, y, diameter, diameter)

    def line(self, x1, y1, x2, y2, draw=True):
        '''Draws a line from (x1,y1) to (x2,y2)'''
        r = self.BezierPath()
        r.line(x1, y1, x2, y2)

        if draw:
            self.canvas.add(r)

        return r

    def star(self, startx, starty, points=20, outer=100, inner=50):
        '''Draws a star.

        Taken from Nodebox.
        '''
        self.beginpath()
        self.moveto(startx, starty + outer)

        for i in range(1, int(2 * points)):
            angle = i * pi / points
            x = sin(angle)
            y = cos(angle)
            if i % 2:
                radius = inner
            else:
                radius = outer
            x = startx + radius * x
            y = starty + radius * y
            self.lineto(x, y)

        self.endpath()

    def beginpath(self, x=None, y=None):
        self._path = self.BezierPath()

        if x and y:
            self._path.moveto(x,y)
        self._path.closed = False

        # if we have arguments, do a moveto too
        if x is not None and y is not None:
            self._path.moveto(x,y)

    def moveto(self, x, y):
        if self._path is None:
            ## self.beginpath()
            raise Exception("No current path. Use beginpath() first.")
        self._path.moveto(x,y)

    def lineto(self, x, y):
        if self._path is None:
            raise Exception("No current path. Use beginpath() first.")
        self._path.lineto(x, y)

    def curveto(self, x1, y1, x2, y2, x3, y3):
        if self._path is None:
            raise Exception("No current path. Use beginpath() first.")
        self._path.curveto(x1, y1, x2, y2, x3, y3)

    def arc(self, x, y, radius, angle1, angle2):
        if self._path is None:
            raise Exception("No current path. Use beginpath() first.")
        self._path.arc(x, y, radius, angle1, angle2)

    def closepath(self):
        if self._path is None:
            raise Exception("No current path. Use beginpath() first.")
        if not self._path.closed:
            self._path.closepath()
            self._path.closed = True

    def endpath(self, draw=True):
        if self._path is None:
            raise Exception("No current path. Use beginpath() first.")

        if self._autoclosepath:
            self._path.closepath()

        p = self._path

        if draw:
            self.canvas.add(p)
            self._path = None

        return p

    def drawpath(self, path):
        if isinstance(path, BezierPath):
            p = self.BezierPath(path)
            self.canvas.add(p)
        elif isinstance(path, Image):
            self.canvas.add(path)

    def drawimage(self, image):
        self.canvas.add(image)

    def autoclosepath(self, close=True):
        self._autoclosepath = close
    
    def rotate(self, *arguments):
        pass

    def relmoveto(self, x, y):
        '''Move relatively to the last point.'''
        if self._path is None:
            raise Exception("No current path. Use beginpath() first.")
        self._path.relmoveto(x,y)

    def rellineto(self, x, y):
        '''Draw a line using relative coordinates.'''
        if self._path is None:
            raise Exception("No current path. Use beginpath() first.")
        self._path.rellineto(x,y)

    def relcurveto(self, h1x, h1y, h2x, h2y, x, y):
        '''Draws a curve relatively to the last point.
        '''
        if self._path is None:
            raise Exception("No current path. Use beginpath() first.")
        self._path.relcurveto(x,y)

    def findpath(self, points, curvature=1.0):
        """Constructs a path between the given list of points.

        Interpolates the list of points and determines
        a smooth bezier path betweem them.

        The curvature parameter offers some control on
        how separate segments are stitched together:
        from straight angles to smooth curves.
        Curvature is only useful if the path has more than  three points.
        """

        # The list of points consists of Point objects,
        # but it shouldn't crash on something straightforward
        # as someone supplying a list of (x,y)-tuples.

        for i, pt in enumerate(points):
            if type(pt) == TupleType:
                points[i] = Point(pt[0], pt[1])

        if len(points) == 0: return None
        if len(points) == 1:
            path = self.BezierPath(None)
            path.moveto(points[0].x, points[0].y)
            return path
        if len(points) == 2:
            path = self.BezierPath(None)
            path.moveto(points[0].x, points[0].y)
            path.lineto(points[1].x, points[1].y)
            return path

        # Zero curvature means straight lines.

        curvature = max(0, min(1, curvature))
        if curvature == 0:
            path = self.BezierPath(None)
            path.moveto(points[0].x, points[0].y)
            for i in range(len(points)):
                path.lineto(points[i].x, points[i].y)
            return path

        curvature = 4 + (1.0-curvature)*40

        dx = {0: 0, len(points)-1: 0}
        dy = {0: 0, len(points)-1: 0}
        bi = {1: -0.25}
        ax = {1: (points[2].x-points[0].x-dx[0]) / 4}
        ay = {1: (points[2].y-points[0].y-dy[0]) / 4}

        for i in range(2, len(points)-1):
            bi[i] = -1 / (curvature + bi[i-1])
            ax[i] = -(points[i+1].x-points[i-1].x-ax[i-1]) * bi[i]
            ay[i] = -(points[i+1].y-points[i-1].y-ay[i-1]) * bi[i]

        r = range(1, len(points)-1)
        r.reverse()
        for i in r:
            dx[i] = ax[i] + dx[i+1] * bi[i]
            dy[i] = ay[i] + dy[i+1] * bi[i]

        path = self.BezierPath(None)
        path.moveto(points[0].x, points[0].y)
        for i in range(len(points)-1):
            path.curveto(points[i].x + dx[i],
                         points[i].y + dy[i],
                         points[i+1].x - dx[i+1],
                         points[i+1].y - dy[i+1],
                         points[i+1].x,
                         points[i+1].y)

        return path

    def beginclip(self,path):
        #self.canvas._context.save()
        p = self.ClippingPath(path)
        self.canvas.add(p)
        return p


    def endclip(self):
        p = self.RestoreCtx()
        self.canvas.add(p)
        
    def fill(self,*args):
        '''Sets a fill color, applying it to new paths.'''
        self._fillcolor = self.color(*args)
        return self._fillcolor

    def nofill(self):
        ''' Stop applying fills to new paths.'''
        self._fillcolor = None

    def stroke(self, *args):
        '''Set a stroke color, applying it to new paths.'''
        self._strokecolor = self.color(*args)
        return self._strokecolor

    def nostroke(self):
        ''' Stop applying strokes to new paths.'''
        self._strokecolor = None

    def strokewidth(self, w=None):
        '''Set the stroke width.'''
        if w is not None:
            self._strokewidth = w
        else:
            return self._strokewidth

    def background(self,*args):
        '''Set the background colour.'''
        r = self.BezierPath()
        r.rect(0, 0, self.WIDTH, self.HEIGHT)
        r.fill = self.color(*args)
        self.canvas.add(r)

    def _makeInstance(self, clazz, args, kwargs):
        """Creates an instance of a class defined in this document.
           This method sets the context of the object to the current context."""
        inst = clazz(self, *args, **kwargs)
        return inst

    def RestoreCtx(self, *args, **kwargs):
        return self._makeInstance(RestoreCtx, args, kwargs)

    def BezierPath(self, *args, **kwargs):
        return self._makeInstance(BezierPath, args, kwargs)

    def ClippingPath(self, *args, **kwargs):
        return self._makeInstance(ClippingPath, args, kwargs)

    def Rect(self, *args, **kwargs):
        return self._makeInstance(Rect, args, kwargs)

    def Oval(self, *args, **kwargs):
        return self._makeInstance(Oval, args, kwargs)

    def Ellipse(self, *args, **kwargs):
        return self._makeInstance(Ellipse, args, kwargs)

    def Color(self, *args, **kwargs):
        return self._makeInstance(Color, args, kwargs)

    def Image(self, *args, **kwargs):
        return self._makeInstance(Image, args, kwargs)

    def Text(self, *args, **kwargs):
        return self._makeInstance(Text, args, kwargs)

    def color(self, *args):
        return Color(mode=self.color_mode, color_range=self.color_range, *args)

    def Height(self):
        return self.HEIGHT
    def Width(self):
        return self.WIDTH
