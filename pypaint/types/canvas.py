from pypaint.interfaces.PIL.helper  import PILHelper
from pypaint.interfaces.PIL.context import PILContext
from pypaint.interfaces.PIL.path    import PathWrap
from pypaint.types.transform        import Transform
from pypaint.types.text             import Text
from pypaint.types.paths            import ClippingPath
from pypaint.utils.defaults         import *
from pypaint.types.mixins           import *
from pypaint.utils.util             import *
from pypaint                        import ft2

from PIL      import Image
from uuid     import uuid4
from aggdraw  import *

import os


class PILCanvas(CanvasMixin):
    def __init__(self, width=None, height=None):
        CanvasMixin.__init__(self, width, height)
        
        self.canvas      = Image.new("RGB", (width, height), "white")
        self.AGG_canvas  = Draw(self.canvas)
        self.helper      = PILHelper()
        self.context     = PILContext()
        
        self.AGG_canvas.setantialias(True)

    def show(self, *arguments):
        self.AGG_canvas.flush()
        self.canvas.show()

    def draw(self, ctx=None):
        if not ctx:
            ctx = self.context

        ## Draws things
        while not self.grobStack.empty():
            (priority, item) = self.grobStack.get()

            if isinstance(item, ClippingPath):
                deltax, deltay = item.center
                m = item._transform.getMatrixWCenter(deltax, deltay, item._transformmode)
                self.drawclip(item, ctx)

            elif isinstance(item, RestoreCtx):
                ctx.restore()
            else:
                if isinstance(item, BezierPath):
                    deltax, deltay = item.center
                    m = item._transform.getMatrixWCenter(deltax, deltay, item._transformmode)
                    self.AGG_canvas.settransform(tuple(m))
                    self.drawpath(item, ctx)

                elif isinstance(item, Text):
                    x, y = item.metrics[0:2]
                    deltax, deltay = item.center
                    m = item._transform.getMatrixWCenter(deltax, deltay-item.baseline, item._transformmode)
                    #ctx.transform(m)
                    #ctx.translate(item.x, item.y - item.baseline)
                    self.AGG_canvas.settransform(tuple(m))

                    self.draw_text(item, ctx)

                elif isinstance(item, Image):
                    deltax, deltay = item.center
                    m = item._transform.getMatrixWCenter(deltax, deltay, item._transformmode)
                    ctx.transform(m)
                    self.drawimage(item, ctx)

            self.grobStack.task_done()

    def draw_text(self, text, ctx=None):
        font = Font(0.8, text._fontfile, size=text._fontsize)
        self.AGG_canvas.text((text.x, text.y), text.text, font)
        self.AGG_canvas.flush()

    def drawclip(self, path, ctx=None):
        '''Passes the path to a Cairo context.'''
        if not isinstance(path, ClippingPath):
            raise Exception("drawpath(): Expecting a ClippingPath, got %s" % path)

        if not ctx:
            ctx = self._context

        for element in path.data:
            cmd = element[0]
            values = element[1:]

            # apply cairo context commands
            if cmd == MOVETO:
                ctx.move_to(*values)
            elif cmd == LINETO:
                ctx.line_to(*values)
            elif cmd == CURVETO:
                ctx.curve_to(*values)
            elif cmd == RLINETO:
                ctx.rel_line_to(*values)
            elif cmd == RCURVETO:
                ctx.rel_curve_to(*values)
            elif cmd == CLOSE:
                ctx.close_path()
            elif cmd == ELLIPSE:
                x, y, w, h = values
                ctx.save()
                ctx.translate (x + w / 2., y + h / 2.)
                ctx.scale (w / 2., h / 2.)
                ctx.arc (0., 0., 1., 0., 2 * pi)
                ctx.restore()

            else:
                raise Exception("PathElement(): error parsing path element command (got '%s')" % cmd)

        ctx.restore()
        ctx.clip()
    
    def drawpath(self, path, ctx=None):
        strokeWidth = None
        strokeColor = None
        ellipse     = False

        if not isinstance(path, BezierPath):
            raise Exception("drawpath(): Expecting a BezierPath, got %s" % (path))

        if not ctx:
            ctx = self._context
        
        if isinstance(path.path, PathWrap):
            path.path.initPath()
            nPath = path.path.path
        else:
            return

        for element in path.data:
            cmd    = element[0]
            values = element[1:]

            if cmd == MOVETO:
                nPath.moveto(*values)

            elif cmd == LINETO:
                nPath.lineto(*values)

            elif cmd == CURVETO:
                nPath.curveto(*values)

            elif cmd == RLINETO:
                nPath.rlineto(*values)

            elif cmd == RCURVETO:
                nPath.rcurveto(*values)

            elif cmd == ARC:
                nPath.curveto(*values)

            elif cmd == CLOSE:
                nPath.close()

            elif cmd == ELLIPSE:
                x, y, w, h = values

                k = 0.5522847498    
                nPath.moveto(x, y+h/2)
                nPath.curveto(x, y+(1-k)*h/2, x+(1-k)*w/2, y, x+w/2, y)
                nPath.curveto(x+(1+k)*w/2, y, x+w, y+(1-k)*h/2, x+w, y+h/2)
                nPath.curveto(x+w, y+(1+k)*h/2, x+(1+k)*w/2, y+h,x+w/2, y+h)
                nPath.curveto(x+(1-k)*w/2, y+h, x, y+(1+k)*h/2, x, y+h/2)
                nPath.close()
                
                ## ctx.translate(x + w / 2., y + h / 2.)
                ## ctx.scale (w / 2., h / 2.)
                ## ctx.arc (0., 0., 1., 0., 2 * pi)
                ## ctx.restore()
            else:
                raise Exception("PathElement(): error parsing path element command (got '%s')" % cmd)

        arguments = self.buildPenBrush(path, templateArgs=nPath)
        self.AGG_canvas.path(*arguments)
        self.AGG_canvas.flush()

    def buildPenBrush(self, path, templateArgs=None):
        if templateArgs:
            PathArgs      = [templateArgs]
        else:
            PathArgs      = []

        PenArguments  = []
        PenDict       = {}
        brush         = None

        if path._fillcolor:
            (R, G, B, A) = self.helper.decToRgba(path._fillcolor)
            color = (R, G, B)
            brush = Brush(color, opacity=A)

        if path._strokecolor:
            (R, G, B, A) = self.helper.decToRgba(path._strokecolor)
            PenDict["color"]   = (R, G, B)
            PenDict["opacity"] = A
            
        if path._strokewidth:
            PenDict["width"] = path._strokewidth

        if PenDict.has_key("color"):
            PathArgs.append(Pen(**PenDict))
        if brush:
            PathArgs.append(brush)
        
        
        arguments = tuple(PathArgs)
        return arguments

class BezierPath(Grob, TransformMixin, ColorMixin):
    stateAttributes = ('_fillcolor', '_strokecolor', '_strokewidth', '_transform', '_transformmode')
    kwargs = ('fill', 'stroke', 'strokewidth')
    
    def __init__(self, ctx, path=None, **kwargs):
        self._ctx = ctx

        super(BezierPath, self).__init__(ctx)
        TransformMixin.__init__(self)
        ColorMixin.__init__(self, **kwargs)

        if self._ctx:
            copy_attrs(self._ctx, self, self.stateAttributes)

        if path is None:
            self._path = PathWrap()
        else:
            self._path = path
       
        if path is None:
            self.data = []
        
        elif isinstance(path, (tuple,list)):
            ## list of path elements
            self.data = []
            for element in path:
                self.append(element)

        elif isinstance(path, BezierPath):
            self.data = path.data
            copy_attrs(path, self, self.stateAttributes)

        else:
            raise Exception("Don't know what to do with %s." % path)

        self.closed = False

    def _get_path(self):
        return self._path

    path = property(_get_path)

    def __getitem__(self, index):
        return self.data[index]

    def __iter__(self):
        for i in range(len(self.data)):
            yield self.data[i]

    def __len__(self):
        return len(self.data)

    def copy(self):
        p = self.__class__(self._ctx, self)
        copy_attrs(self._ctx, p, self.stateAttributes)
        return p



    ### Path methods ###
    def moveto(self, x, y):
        self.data.append(PathElement(MOVETO, x, y))

    def lineto(self, x, y):
        self.data.append(PathElement(LINETO, x, y))

    def curveto(self, c1x, c1y, c2x, c2y, x, y):
        self.data.append(PathElement(CURVETO, c1x, c1y, c2x, c2y, x, y))

    def relmoveto(self, x, y):
        self.data.append(PathElement(RMOVETO, x, y))

    def rellineto(self, x, y):
        self.data.append(PathElement(RLINETO, x, y))

    def relcurveto(self, c1x, c1y, c2x, c2y, x, y):
        self.data.append(PathElement(RCURVETO, c1x, c1y, c2x, c2y, x, y))

    def arc(self, x, y, radius, angle1, angle2):
        self.data.append(PathElement(ARC, x, y, radius, angle1, angle2))

    def closepath(self):
        self.data.append(PathElement(CLOSE))
        self.closed = True

    def ellipse(self,x,y,w,h):
        self.data.append(PathElement(ELLIPSE, x, y, w, h))
        self.closepath()

    def rect(self, x, y, w, h):
        self.moveto(x, y)
        self.rellineto(w, 0)
        self.rellineto(0, h)
        self.rellineto(-w, 0)
        #self.closepath()
        self.rellineto(0, -h)

    def setlinewidth(self, width):
        self.linewidth = width

    def line(self, x1, y1, x2, y2):
        self.moveto(x1, y1)
        self.lineto(x2, y2)

    def _get_bounds(self):
        '''
        Returns the path's bounding box. Note that this doesn't
        take transforms into account.
        '''

        X, Y  = 0, 0

        X_set = []
        Y_set = []

        for element in self.data:
            cmd    = element[0]
            values = element[1:]

            if cmd == MOVETO:
                X = values[0]
                Y = values[1]

            elif cmd == LINETO:
                X1, Y1 = values

                X_set.append(X)
                Y_set.append(Y)
                X_set.append(X1)
                Y_set.append(Y1)

            elif cmd == CURVETO:
                X1, Y1, X2, Y2, X3, Y3 = values

                X_set.append(X)
                Y_set.append(Y)
                X_set.append(X1)
                Y_set.append(Y1)
                X_set.append(X2)
                Y_set.append(Y2)
                X_set.append(X3)
                Y_set.append(Y3)


            elif cmd == RLINETO:
                X1, Y1 = values
                X_set.append(X)
                Y_set.append(Y)
                X_set.append(X+X1)
                Y_set.append(Y+Y1)


            elif cmd == RCURVETO:
                X1, Y1, X2, Y2, X3, Y3 = values
                X_set.append(X)
                Y_set.append(Y)
                X_set.append(X+X1)
                Y_set.append(Y+Y1)
                X_set.append(X+X2)
                Y_set.append(Y+Y2)
                X_set.append(X+X3)
                Y_set.append(Y+Y3)

            elif cmd == ELLIPSE:
                X, Y, W, H = values
                X_set.append(X)
                Y_set.append(Y)
                X_set.append(W)
                Y_set.append(H)

        
        if len(X_set) and len(Y_set):
            max_X = max(X_set)
            max_Y = max(Y_set)

            min_X = min(X_set)
            min_Y = min(Y_set)

            #print (min_X, min_Y, max_X, max_Y)
            return (min_X, min_Y, max_X, max_Y)
        else:
            return (0, 0, 0, 0)
        

    bounds = property(_get_bounds)

    def _get_center(self):
        '''Returns the center point of the path, disregarding transforms.
        '''
        (x1, y1, x2, y2) = self.bounds
        x = (x1 + x2) / 2
        y = (y1 + y2) / 2
        return (x, y)

    center = property(_get_center)

    def _get_contours(self):

        return bezier.contours(self)

    contours = property(_get_contours)

    ### Drawing methods ###
    def _get_transform(self):
        trans = self._transform.copy()
        if (self._transformmode == CENTER):
            (x, y, w, h) = self.bounds
            deltax = x+w/2
            deltay = y+h/2

            t = Transform()
            t.translate(-deltax, -deltay)
            trans.prepend(t)

            t = Transform()
            t.translate(deltax, deltay)
            trans.append(t)

        return trans

    transform = property(_get_transform)


        
    ### Mathematics ###
    def segmentlengths(self, relative=False, n=10):


        if relative: # Use the opportunity to store the segment cache.
            if self._segment_cache is None:
                self._segment_cache = bezier.segment_lengths(self, relative=True, n=n)
            return self._segment_cache
        else:
            return bezier.segment_lengths(self, relative=False, n=n)

    def _get_length(self, segmented=False, n=10):
        import bezier
        return bezier.length(self, segmented=segmented, n=n)

    length = property(_get_length)
        
    def point(self, t):
        import bezier
        return bezier.point(self, t)
        
    def points(self, amount=100):
        import bezier
        if len(self) == 0:
            raise NodeBoxError, "The given path is empty"

        # The delta value is divided by amount - 1, because we also want the last point (t=1.0)
        # If I wouldn't use amount - 1, I fall one point short of the end.
        # E.g. if amount = 4, I want point at t 0.0, 0.33, 0.66 and 1.0,
        # if amount = 2, I want point at t 0.0 and t 1.0
        try:
            delta = 1.0/(amount-1)
        except ZeroDivisionError:
            delta = 1.0

        for i in xrange(amount):
            yield self.point(delta*i)
            
    def addpoint(self, t):
        import bezier
        self._nsBezierPath = bezier.insert_point(self, t)._nsBezierPath
        self._segment_cache = None

class Point:
    '''
    Taken from Nodebox and modified
    '''
    def __init__(self, *args):
        if len(args) == 3:
            self.x, self.y, self.z = args
        if len(args) == 2:
            self.x, self.y = args
        elif len(args) == 1:
            self.x, self.y = args[0]
        elif len(args) == 0:
            self.x = self.y = 0.0
        else:
            raise Exception("Wrong initializer for Point object")

    def __repr__(self):
        return (self.x, self.y)
    def __str__(self):
        return "Point(%.3f, %.3f)" % (self.x, self.y)
    def __getitem__(self,key):
        return (float(self.x), float(self.y))[key]
    def __eq__(self, other):
        if other is None: return False
        return self.x == other.x and self.y == other.y
    def __ne__(self, other):
        return not self.__eq__(other)

class PathElement:
    '''
    Represents a single element in a Bezier path.

    The first argument should be a command string,
    following the proper values according to which element we want.

    Possible input:
        ('moveto', x, y)
        ('lineto', x, y)
        ('rlineto', x, y)
        ('curveto', c1x, c1y, c2x, c2y, x, y)
        ('rcurveto', c1x, c1y, c2x, c2y, x, y)
        ('arc', x, y, radius, angle1, angle2)
        ('ellipse', x, y, w, h)
        ('close',)

        Mind the trailing comma in the 'close' example, since it just needs
        an argument. The trailing comma is a way to tell python this really is
        supposed to be a tuple.
    '''
    def __init__(self, cmd, *args):
        self.cmd    = cmd
        self.values = args

        if cmd == MOVETO or cmd == RMOVETO:
            self.x, self.y = self.values
            self.c1x = self.c1y = self.c2x = self.c2y = None
        elif cmd == LINETO or cmd == RLINETO:
            self.x, self.y = self.values
        elif cmd == CURVETO or cmd == RCURVETO:
            self.c1x, self.c1y, self.c2x,self.c2y, self.x, self.y = self.values
        elif cmd == CLOSE:
            self.x = self.y = self.c1x = self.c1y = self.c2x = self.c2y = None
        elif cmd == ARC:
            self.x, self.y, self.radius, self.angle1, self.angle2 = self.values
        elif cmd == ELLIPSE:
            # it doesn't feel right having an "ellipse" element, but we need
            # some cairo specific functions to draw it in draw_cairo()
            self.x, self.y, self.w, self.h = self.values
        else:
            raise ShoebotError(_('Wrong initialiser for PathElement (got "%s")') % (cmd))

    def __getitem__(self,key):
        data = list(self.values)
        data.insert(0, self.cmd)
        return data[key]

    def __repr__(self):
        data = list(self.values)
        data.insert(0, self.cmd)
        return "PathElement" + str(tuple(data))

    def __eq__(self, other):
        if other is None: return False
        if self.cmd != other.cmd: return False
        if self.values != other.values: return False
        return True

    def __ne__(self, other):
        return not self.__eq__(other)

    def getXY(self):
        return self.values



