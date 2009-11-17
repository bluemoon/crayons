from pypaint.utils.defaults      import *
from pypaint.types.transform     import Transform
from pypaint.types.color         import Color

_STATE_NAMES = {
    '_outputmode':    'outputmode',
    '_colorrange':    'colorrange',
    '_fillcolor':     'fill',
    '_strokecolor':   'stroke',
    '_strokewidth':   'strokewidth',
    '_transform':     'transform',
    '_transformmode': 'transformmode',
    '_fontname':      'font',
    '_fontsize':      'fontsize',
    '_align':         'align',
    '_lineheight':    'lineheight',
}

def copy_attr(v):
    if v is None:
        return None
    elif hasattr(v, "copy"):
        return v.copy()
    elif isinstance(v, list):
        return list(v)
    elif isinstance(v, tuple):
        return tuple(v)
    elif isinstance(v, (int, str, unicode, float, bool, long)):
        return v
    else:
        raise Exception("Don't know how to copy '%s'." % v)

def copy_attrs(source, target, attrs):
    for attr in attrs:
        setattr(target, attr, copy_attr(getattr(source, attr)))

class Point(object):
    def __init__(self, *args):
        if len(args) == 2:
            self.x, self.y = args
        elif len(args) == 1:
            self.x, self.y = args[0]
        elif len(args) == 0:
            self.x = self.y = 0.0
        else:
            raise NodeBoxError, "Wrong initializer for Point object"

    def __repr__(self):
        return "Point(x=%.3f, y=%.3f)" % (self.x, self.y)
        
    def __eq__(self, other):
        if other is None: return False
        return self.x == other.x and self.y == other.y
        
    def __ne__(self, other):
        return not self.__eq__(other)

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
    
    def __init__(self):
        self._reset()
        
    def _reset(self):
        self._transform = Transform()
        self._transformmode = CENTER
        
    def _get_transform(self):
        return self._transform
    def _set_transform(self, transform):
        self._transform = Transform(transform)
    transform = property(_get_transform, _set_transform)
    
    def _get_transformmode(self):
        return self._transformmode
    def _set_transformmode(self, mode):
        self._transformmode = mode
    transformmode = property(_get_transformmode, _set_transformmode)
        
    def translate(self, x, y):
        self._transform.translate(x, y)
        
    def reset(self):
        self._transform = Transform()

    def rotate(self, degrees=0, radians=0):
        self._transform.rotate(-degrees,-radians)

    def translate(self, x=0, y=0):
        self._transform.translate(x,y)

    def scale(self, x=1, y=None):
        self._transform.scale(x,y)

    def skew(self, x=0, y=0):
        self._transform.skew(x,y)
        
class ColorMixin(object):
    """Mixin class for color support.
    Adds the _fillcolor, _strokecolor and _strokewidth attributes to the class."""
    def __init__(self, **kwargs):
        try:
            self._fillcolor = Color(kwargs['fill'], mode='rgb', color_range=1)
        except KeyError:
            if self._ctx._fillcolor:
                self._fillcolor = self._ctx._fillcolor.copy()
            else:
                self._fillcolor = None
        
        try:
            self._strokecolor = Color(kwargs['stroke'], mode='rgb', color_range=1)
        except KeyError:
            if self._ctx._strokecolor:
                self._strokecolor = self._ctx._strokecolor.copy()
            else:
                self._strokecolor = None
        self._strokewidth = kwargs.get('strokewidth', 1.0)

    
    def _get_fill(self):
        return self._fillcolor
    def _set_fill(self, *args):
        self._fillcolor = Color(mode='rgb', color_range=1, *args)
    fill = property(_get_fill, _set_fill)

    
    def _get_stroke(self):
        return self._strokecolor
    def _set_stroke(self, *args):
        self._strokecolor = Color(self._ctx, *args)
    stroke = property(_get_stroke, _set_stroke)
    
    def _get_strokewidth(self):
        return self._strokewidth
    def _set_strokewidth(self, strokewidth):
        self._strokewidth = max(strokewidth, 0.0001)
    strokewidth = property(_get_strokewidth, _set_strokewidth)

class RestoreCtx(Grob):
    def __init__(self, ctx, **kwargs):
        self._ctx = ctx

class CanvasMixin:
    def __init__(self, width=DEFAULT_WIDTH, height=DEFAULT_HEIGHT):
        self.width  = width
        self.height = height

        self.grobstack = []
        self.font_size = 12

        self.clear()

    def add(self, grob):
        if not isinstance(grob, Grob):
            raise ("Canvas.add() - wrong argument: expecting a Grob, received %s") % (grob)

        self.grobstack.append(grob)

    def append(self, grob):
        self.add(self, grob)

    def setsurface(self):
        pass

    def get_context(self):
        return self._context

    def get_surface(self):
        return self._surface

    def _get_size(self):
        return self.width, self.height

    size = property(_get_size)

    def append(self, el):
        self._container.append(el)

    def draw(self, ctx=None):
        pass

    def output(self, filename=None, ext=None):
        pass

    def clear(self):
        self.grobstack = []
