from mixins import *

class Path:
    def __init__(self):
        self.path = aggdraw.Path()

    ### Path methods ###
    def moveTo(self, x, y):
        self.path.moveto(x, y)

    def lineTo(self, x, y):
        self.path.lineto(x, y)

    def curveTo(self, x1, y1, x2, y2, x3, y3):
        self.path.curveto(x1, y1, x2, y2, x3, y3)

    def closePath(self):
        self.path.close()

    def setLineWidth(self, width):
        self.linewidth = width

    def rect(self, x, y, width, height):
        aggdraw.rectangle(x, y)
        
    def oval(self, x, y, width, height):
        aggdraw.ellipse(x, y)
        
    def line(self, x1, y1, x2, y2):
        self.path.moveto(x1, y1)
        self.path.rlineto(x2, y2)


class PathElement(object):
    def __init__(self, cmd=None, pts=None):
        self.cmd = cmd
        if cmd == MOVETO:
            assert len(pts) == 1
            self.x, self.y = pts[0]
            self.ctrl1 = Point(pts[0])
            self.ctrl2 = Point(pts[0])

        elif cmd == LINETO:
            assert len(pts) == 1
            self.x, self.y = pts[0]
            self.ctrl1 = Point(pts[0])
            self.ctrl2 = Point(pts[0])

        elif cmd == CURVETO:
            assert len(pts) == 3
            self.ctrl1 = Point(pts[0])
            self.ctrl2 = Point(pts[1])
            self.x, self.y = pts[2]

        elif cmd == CLOSE:
            assert pts is None or len(pts) == 0
            self.x = self.y = 0.0
            self.ctrl1 = Point(0.0, 0.0)
            self.ctrl2 = Point(0.0, 0.0)

        else:
            self.x = self.y = 0.0
            self.ctrl1 = Point()
            self.ctrl2 = Point()

    def __repr__(self):
        if self.cmd == MOVETO:
            return "PathElement(MOVETO, ((%.3f, %.3f),))" % (self.x, self.y)
        elif self.cmd == LINETO:
            return "PathElement(LINETO, ((%.3f, %.3f),))" % (self.x, self.y)
        elif self.cmd == CURVETO:
            return "PathElement(CURVETO, ((%.3f, %.3f), (%.3f, %s), (%.3f, %.3f))" % \
                (self.ctrl1.x, self.ctrl1.y, self.ctrl2.x, self.ctrl2.y, self.x, self.y)
        elif self.cmd == CLOSE:
            return "PathElement(CLOSE)"
            
    def __eq__(self, other):
        if other is None: return False
        if self.cmd != other.cmd: return False
        return self.x == other.x and self.y == other.y \
            and self.ctrl1 == other.ctrl1 and self.ctrl2 == other.ctrl2
        
    def __ne__(self, other):
        return not self.__eq__(other)

class ClippingPath(Grob):
    def __init__(self, ctx, path):
        self._ctx = ctx
        self.path = path
        self._grobs = []
        
    def append(self, grob):
        self._grobs.append(grob)
        
    def _draw(self):
        _save()
        cp = self.path.transform.transformBezierPath(self.path)
        cp._nsBezierPath.addClip()
        for grob in self._grobs:
            grob._draw()
        _restore()
