from pypaint.utils.defaults      import *
from pypaint.geometry.transform  import Transform
from pypaint.types.color         import Color
from pypaint.styles              import style

import math


class Grob(object):
    """A GRaphic OBject is the base class for all DrawingPrimitives."""

    def __init__(self, ctx):
        """Initializes this object with the current context."""
        self._ctx = ctx

    def draw(self):
        """Appends the grob to the canvas.
           This will result in a draw later on, when the scene graph is rendered."""
        self._ctx.canvas.append(self)
        
    def copy(self):
        """Returns a deep copy of this grob."""
        raise NotImplementedError, "Copy is not implemented on this Grob class."
        
    def inheritFromContext(self, ignore=()):
        attrs_to_copy = list(self.__class__.stateAttributes)
        [attrs_to_copy.remove(k) for k, v in _STATE_NAMES.items() if v in ignore]
        copy_attrs(self._ctx, self, attrs_to_copy)
        
    def checkKwargs(self, kwargs):
        remaining = [arg for arg in kwargs.keys() if arg not in self.kwargs]
        if remaining:
            raise Exception("Unknown argument(s) '%s'" % ", ".join(remaining))

    checkKwargs = classmethod(checkKwargs)

class TransformMixin(object):
    """Mixin class for transformation support.
    Adds the _transform and _transformmode attributes to the class."""
    transform = None
    def __init__(self):
        self._reset()

    def _reset(self):
        self.transform = Transform()
        self._transformmode = 'center'
    

    
    def _get_transformmode(self):
        return self._transformmode
    def _set_transformmode(self, mode):
        self._transformmode = mode
    transformmode = property(_get_transformmode, _set_transformmode)
        
    def translate(self, x, y):
        self.transform.translate(x, y)
        
    def reset(self):
        self.transform = Transform()

    def rotate(self, degrees=0, radians=0):
        if self._transformmode == 'corner':
            deltax, deltay = self._transform.transformPoint((0, 0))
        elif self._transformmode == 'center':
            deltax, deltay = self._transform.transformPoint(self.center)
            
        if degrees:
            C = math.cos((math.pi/180.0)*degrees)
            S = math.sin((math.pi/180.0)*degrees)

        self.transform *= Transform(C, S, -S, C, deltax-(C*deltax)+(S*deltay),deltay-(S*deltax)-(C*deltay))

    def translate(self, x=0, y=0):
        self.transform *= Transform(dx=x, dy=y)

    def scale(self, x=1, y=None):
        self.transform.scale(x,y)

    def skew(self, x=0, y=0):
        self.transform.skew(x,y)

    def point(self, point):
        return self.transform.transformPoint(point)

    def matrix_with_center(self):
        pass

class ColorMixin(object):
    """Mixin class for color support.
    Adds the _fillcolor, _strokecolor and _strokewidth attributes to the class."""
    def __init__(self, *args, **kwargs):
        try:
            self._fillcolor = Color(kwargs['fill'], mode='rgb', color_range=1)
        except KeyError:
            self._fillcolor = None
        try:
            self._strokecolor = Color(kwargs['stroke'], mode='rgb', color_range=1)
        except KeyError:
            self._strokecolor = None

        self._strokewidth = kwargs.get('strokewidth', 1.0)
        
    
    def _get_fill(self):
        if self._fillcolor:
            return self._fillcolor
        else:
            print self._fillcolor

    def _set_fill(self, *args):
        if len(args) == 1 and isinstance(args[0], tuple):
            self._fillcolor = Color(*args[0])
        elif len(args) == 1 and isinstance(args[0], Color):
            self._fillcolor = args[0]
        else:
            self._fillcolor = Color(*args)
    
    fill_color = property(_get_fill, _set_fill)

    def s_color(self, *args):
        if len(args) == 1 and isinstance(args[0], tuple):
            self._strokecolor = Color(*args[0])
        elif len(args) == 1 and isinstance(args[0], Color):
            self._strokecolor = args[0]
        else:
            self._strokecolor = Color(*args)

    def _get_stroke(self):
        return self._strokecolor

    def _set_stroke(self, *args):
        if len(args) == 1 and isinstance(args[0], tuple):
            self._strokecolor = Color(*args[0])
        elif len(args) == 1 and isinstance(args[0], Color):
            self._strokecolor = args[0]
        else:
            self._strokecolor = Color(*args)
    stroke_color = property(_get_stroke, _set_stroke)
    
    def _get_strokewidth(self):
        return self._strokewidth

    def _set_strokewidth(self, strokewidth):
        self._strokewidth = max(strokewidth, 0.0001)

    stroke_width = property(_get_strokewidth, _set_strokewidth)



class CanvasMixin:
    def __init__(self, width=DEFAULT_WIDTH, height=DEFAULT_HEIGHT):
        self.width  = width
        self.height = height

        self.data = []
        self.font_size = 12

        self.clear()

    def add(self, grob):
        self.data.append(grob)

    def append(self, grob):
        self.data.append(grob)

    def _get_size(self):
        return self.width, self.height

    size = property(_get_size)


    def draw(self, ctx=None):
        pass

    def output(self, filename=None, ext=None):
        pass

    def clear(self):
        self.data = []

class StyleMixin:
    def __init__(self):
        pass

    def apply_style(self, current_style):
        if isinstance(current_style, style):
            pass
            
        

class GeometryMixin:
    def updateBounds(self, bounds, (x, y), min=min, max=max):
        """Return the bounding recangle of rectangle bounds and point (x, y)."""
        xMin, yMin, xMax, yMax = bounds
        return min(xMin, x), min(yMin, y), max(xMax, x), max(yMax, y)

    def quadBounds(self, pt1, pt2, pt3):
        pt1, pt2, pt3 = numpy.array((pt1, pt2, pt3))
        c = pt1
        b = (pt2 - c) * 2.0
        a = pt3 - c - b

        ## calc first derivative
        ax, ay = a * 2
        bx, by = b
        roots = []
        
        if ax != 0:
            roots.append(-bx/ax)
        if ay != 0:
            roots.append(-by/ay)

        points = [a*t*t + b*t + c for t in roots if 0 <= t < 1] + [pt1, pt3]
        xMin, yMin = numpy.minimum.reduce(points)
        xMax, yMax = numpy.maximum.reduce(points)
        return (xMin, yMin, xMax, yMax)

    def cubicBounds(self, pt1, pt2, pt3, pt4):
         pt1, pt2, pt3, pt4 = numpy.array((pt1, pt2, pt3, pt4))
         d = pt1
         c = (pt2 - d) * 3.0
         b = (pt3 - pt2) * 3.0 - c
         a = pt4 - d - c - b
         ax, ay = a * 3.0
         bx, by = b * 2.0
         cx, cy = c
         xRoots = [t for t in solveQuadratic(ax, bx, cx) if 0 <= t < 1]
         yRoots = [t for t in solveQuadratic(ay, by, cy) if 0 <= t < 1]
         roots = xRoots + yRoots
    
         points = [(a*t*t*t + b*t*t + c * t + d) for t in roots] + [pt1, pt4]
         xMin, yMin = numpy.minimum.reduce(points)
         xMax, yMax = numpy.maximum.reduce(points)
         return (xMin, yMin, xMax, yMax)

