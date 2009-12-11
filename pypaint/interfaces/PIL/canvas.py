from pypaint.interfaces.PIL.helper  import PILHelper
from pypaint.interfaces.PIL.context import PILContext
from pypaint.interfaces.PIL.path    import PathWrap
from pypaint.types.transform        import Transform
from pypaint.types.text             import Text
from pypaint.types.paths            import BezierPath
from pypaint.utils.defaults         import *
from pypaint.types.mixins           import *
from pypaint.utils.util             import *
from pypaint                        import ft2

from fontTools.ttLib                import TTFont

from PIL      import Image
from uuid     import uuid4
from aggdraw  import *

import os


class PILCanvas:
    def __init__(self, width=None, height=None):
        self.canvas      = Image.new("RGB", (width, height), "white")
        self.AGG_canvas  = Draw(self.canvas)
        self.helper      = PILHelper()
        self.context     = PILContext()
        
        self.AGG_canvas.setantialias(True)

    def show(self, *arguments):
        self.AGG_canvas.flush()
        self.canvas.show()
        
    def output(self, filename, file_ext):
        self.AGG_canvas.flush()
        self.canvas.save(filename, file_ext)
        
    def draw(self, ctx=None):
        if not ctx:
            ctx = self.context

        ## Draws things
        while not self.grobStack.empty():
            (priority, item) = self.grobStack.get()
            if isinstance(item, RestoreCtx):
                ctx.restore()
            else:
                if isinstance(item, BezierPath):
                    deltax, deltay = item.center
                    m = item._transform.getMatrixWCenter(deltax, deltay, item._transformmode)
                    self.AGG_canvas.settransform(tuple(m))
                    self.drawpath(item, ctx)

                elif isinstance(item, Text):
                    x, y = item.bounds
                    deltax, deltay = item.center
                    m = item._transform.getMatrixWCenter(deltax, deltay-item.line_height, item._transformmode)
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
        #print text.draw_glyph._sentence
        R, G, B, A = text._fillcolor
        R=int(R/1.0*255)
        G=int(G/1.0*255)
        B=int(B/1.0*255)
        font = Font((R, G, B), text._fontfile, size=text._fontsize)
        self.AGG_canvas.text((text.x, text.y), text.text, font)

    def drawclip(self, path, ctx=None):
        '''Passes the path to a Cairo context.'''
        if not isinstance(path, ClippingPath):
            raise Exception("drawpath(): Expecting a ClippingPath, got %s" % path)

        if not ctx:
            ctx = self._context

        for element in path.data:
            cmd = element[0]
            values = element[1:]

            ## apply cairo context commands
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

            elif cmd == CURVE3TO:
                nPath.curve3to(*values)

            elif cmd == CURVE4TO:
                nPath.curve4to(*values)

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



