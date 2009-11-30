from pypaint.types.paths import PathElement
from pypaint.mixins      import *

class path(Grob, TransformMixin, ColorMixin, GeometryMixin):
    def __init__(self, path=None, **kwargs):
        TransformMixin.__init__(self)
        ColorMixin.__init__(self, **kwargs)

        if path is None:
            self.data = []

    def __setitem__(self, index, value):
        self.data[index] = value

    def __getitem__(self, index):
        return self.data[index]

    def __iter__(self):
        for i in range(len(self.data)):
            yield self.data[i]

    def __len__(self):
        return len(self.data)

    def _get_bounds(self):
        X, Y  = 0, 0

        X_set = []
        Y_set = []
        current_point = (0, 0)
        for element in self.data:
            cmd    = element[0]
            values = element[1:]

            if cmd == MOVETO:
                X = values[0]
                Y = values[1]
                current_point = (X, Y)
                X_set.append(X)
                Y_set.append(Y)

            elif cmd == LINETO:
                X1, Y1 = values

                X_set.append(X)
                Y_set.append(Y)
                X_set.append(X1)
                Y_set.append(Y1)

            elif cmd == CURVETO:
                X1, Y1, X2, Y2, X3, Y3 = values
                print self.cubicBounds(current_point, (X1, Y1), (X2, Y2), (X3, Y3))

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

                #calculateQuadraticBounds((X1, Y1), (X2, Y2), (X3, Y3))

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

        
        max_X = max(X_set)
        max_Y = max(Y_set)
        min_X = min(X_set)
        min_Y = min(Y_set)
        return (min_X, min_Y, max_X, max_Y)

    bounds = property(_get_bounds)

    def _get_center(self):
        x1, y1, x2, y2 = self.bounds
        half_x = (x2 + x1)/2
        half_y = (y2 + y1)/2
        return half_x, half_y
    center = property(_get_center)

    def _get_abs_center(self):
        x1, y1, x2, y2 = self.bounds
        half_x = (x2 + x1)/2
        half_y = (y2 + y1)/2
        return self.point((half_x, half_y))

    abs_center = property(_get_abs_center)
    
    contours = None

    def moveto(self, x, y):
        self.current_point = (x, y)
        self.data.append(PathElement(MOVETO, x, y))

    def lineto(self, x, y):
        self.data.append(PathElement(LINETO, x, y))

    def curveto(self, c1x, c1y, c2x, c2y, x, y):
        self.data.append(PathElement(CURVETO, c1x, c1y, c2x, c2y, x, y))

    def curve3to(self, c1x, c1y, x, y):
        self.data.append(PathElement(CURVE3TO, c1x, c1y, x, y))

    def curve4to(self, c1x, c1y, c2x, c2y, x, y):
        self.data.append(PathElement(CURVE4TO, c1x, c1y, c2x, c2y, x, y))


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
        self.x = x
        self.y = y

        self.moveto(x, y)
        self.rellineto(w, 0)
        self.rellineto(0, h)
        self.rellineto(-w, 0)
        self.rellineto(0, -h)

    def setlinewidth(self, width):
        self.linewidth = width

    def line(self, x1, y1, x2, y2):
        self.moveto(x1, y1)
        self.lineto(x2, y2)
