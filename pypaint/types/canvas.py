from pypaint.interfaces.PIL.helper  import PILHelper
from pypaint.interfaces.PIL.context import PILContext
from pypaint.types.transform        import Transform
from pypaint.types.text             import Text
from pypaint.path                   import path
from pypaint.text                   import text
from pypaint.utils.defaults         import *
from pypaint.mixins                 import *
from pypaint.grid                   import Grid
from pypaint.utils.util             import *
from fontTools.ttLib                import TTFont

from PIL      import Image
from uuid     import uuid4
import aggdraw 

import os
import numpy

class PILCanvas(CanvasMixin):
    def __init__(self, width=None, height=None, gtk=False):
        CanvasMixin.__init__(self, width, height)
        
        #self.canvas      = Image.new("RGBA", (width, height), "white")
        self.AGG_canvas  = aggdraw.Draw("RGBA", (width, height), "white")
        self.gtk_draw    = gtk
        
        self.AGG_canvas.setantialias(False)

    def reset_canvas(self, r, g, b):
        self.AGG_canvas.clear((r, g, b))
        
    def show(self, *arguments):
        self.AGG_canvas.flush()
        self.canvas.show()

    def gtk(self):
        return self.AGG_canvas.tostring()
        
    def output(self, filename, file_ext):
        if not self.gtk_draw:
            self.AGG_canvas.flush()

        self.canvas.save(filename, file_ext)
        
    def draw(self, stack=None):
        ## for   = 0.373 per call
        ## while = 0.441 per call
        last_transform = None
        for item in stack:
            transform = item.transform
            data = item.data
            if last_transform != transform.affine:
                self.AGG_canvas.settransform(transform)
                last_transform = transform.affine

            if path.type == 'path':
                """
                n_path = aggdraw.Path()
                for element in data:
                    cmd    = element[0]
                    values = element[1:]
                    
                    if cmd == 'moveto':
                        n_path.moveto(*values)
                    elif cmd == 'lineto':
                        n_path.lineto(*values)
                    elif cmd == 'curveto':
                        n_path.curveto(*values)
                    elif cmd == CURVE3TO:
                        n_path.curve3to(*values)
                    elif cmd == CURVE4TO:
                        n_path.curve4to(*values)
                    elif cmd == RLINETO:
                        n_path.rlineto(*values)
                    elif cmd == RCURVETO:
                        n_path.rcurveto(*values)
                    elif cmd == ARC:
                        n_path.curveto(*values)
                    elif cmd == CLOSE:
                        n_path.close()
                    elif cmd == ELLIPSE:
                        x, y, w, h = values
                        k = 0.5522847498    
                        n_path.moveto(x, y+h/2)
                        n_path.curveto(x, y+(1-k)*h/2, x+(1-k)*w/2, y, x+w/2, y)
                        n_path.curveto(x+(1+k)*w/2, y, x+w, y+(1-k)*h/2, x+w, y+h/2)
                        n_path.curveto(x+w, y+(1+k)*h/2, x+(1+k)*w/2, y+h,x+w/2, y+h)
                        n_path.curveto(x+(1-k)*w/2, y+h, x, y+(1+k)*h/2, x, y+h/2)
                        n_path.close()

                    else:
                        raise Exception("PathElement(): error parsing path element command (got '%s')" % cmd)
                """
                arguments = self.buildPenBrush(item, templateArgs=item.path)
                self.AGG_canvas.path(*arguments)

                if not self.gtk_draw:
                    self.AGG_canvas.flush()

            elif isinstance(item, text):
                (R, G, B, A)= item.fill_color
                R = int(R/1.0*255)
                G = int(G/1.0*255)
                B = int(B/1.0*255)

                font = Font((R, G, B), item.font_file, item.font_size)

                self.AGG_canvas.settransform(item.transform)
                self.AGG_canvas.text((item.X, item.Y), item.Text, font)

    def decToRgba(self, RGBA):
        R = int(RGBA.r * 255)
        G = int(RGBA.g * 255)
        B = int(RGBA.b * 255)
        A = int(RGBA.a * 255)
        return (R, G, B, A)

    def buildPenBrush(self, path, templateArgs=None):
        if templateArgs:
            PathArgs      = [templateArgs]
        else:
            PathArgs      = []

        PenArguments  = []
        PenDict       = {}
        brush = None

        fillcolor = path._fillcolor
        strokecolor = path._strokecolor
        if fillcolor:
            (R, G, B, A) = self.decToRgba(fillcolor)
            color = (R, G, B)
            brush = aggdraw.Brush(color, opacity=A)

        if strokecolor:
            (R, G, B, A) = self.decToRgba(strokecolor)
            PenDict["color"]   = (R, G, B)
            PenDict["opacity"] = A
        
        PenDict["width"] = path._strokewidth

        if PenDict.has_key("color"):
            PathArgs.append(aggdraw.Pen(**PenDict))
        if brush:
            PathArgs.append(brush)
        
        arguments = tuple(PathArgs)
        return arguments


