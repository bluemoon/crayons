from pypaint.types.paths import PathElement
from pypaint.mixins      import *
from aggdraw  import *

class path(Grob, TransformMixin, ColorMixin):
    def __init__(self, path=None, **kwargs):
        TransformMixin.__init__(self)
        ColorMixin.__init__(self, **kwargs)

        if path is None:
            self.data = []

        self.path = Path()

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
                x0, y0, x1, y1 = self._cubicBounds(current_point, (X1, Y1), (X2, Y2), (X3, Y3))

                X_set.append(x0)
                Y_set.append(y0)
                X_set.append(x1)
                Y_set.append(y1)

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
        self.path.moveto(x, y)     
        #self.data.append([MOVETO, x, y])

    def lineto(self, x, y):
        self.path.lineto(x, y)
        #self.data.append([LINETO, x, y])

    def curveto(self, c1x, c1y, c2x, c2y, x, y):
        self.path.curveto(c1x, c1y, c2x, c2y, x, y)
        #self.data.append([CURVETO, c1x, c1y, c2x, c2y, x, y])

    def curve3to(self, c1x, c1y, x, y):
        self.path.curveto(c1x, c1y, x, y)
        #self.data.append(PathElement(CURVE3TO, c1x, c1y, x, y))

    def curve4to(self, c1x, c1y, c2x, c2y, x, y):
        self.path.curveto(c1x, c1y, c2x, c2y, x, y)
        #self.data.append(PathElement(CURVE4TO, c1x, c1y, c2x, c2y, x, y))

    def relmoveto(self, x, y):
        #self.path.rlineto(x, y)
        #self.data.append(PathElement(RMOVETO, x, y))
        pass

    def rellineto(self, x, y):
        self.path.rlineto(x, y)
        #self.data.append([RLINETO, x, y])

    def relcurveto(self, c1x, c1y, c2x, c2y, x, y):
        self.path.rcurveto(c1x, c1y, c2x, c2y, x, y)
       # self.data.append(PathElement(RCURVETO, c1x, c1y, c2x, c2y, x, y))

    def arc(self, x, y, radius, angle1, angle2):
        self.path.curveto(c1x, c1y, c2x, c2y, x, y)
        #self.data.append([ARC, x, y, radius, angle1, angle2])

    def closepath(self):
        self.path.close()
        #self.data.append([CLOSE])
        #self.closed = True

    def ellipse(self,x,y,w,h):
        k = 0.5522847498    
        self.path.moveto(x, y+h/2)
        self.path.curveto(x, y+(1-k)*h/2, x+(1-k)*w/2, y, x+w/2, y)
        self.path.curveto(x+(1+k)*w/2, y, x+w, y+(1-k)*h/2, x+w, y+h/2)
        self.path.curveto(x+w, y+(1+k)*h/2, x+(1+k)*w/2, y+h,x+w/2, y+h)
        self.path.curveto(x+(1-k)*w/2, y+h, x, y+(1+k)*h/2, x, y+h/2)
        self.path.close()
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
        vertex = []

    def _quadraticBounds(self):
        pt1 = self.bezier[0:1][0]
        pt2 = self.bezier[1:2][0]
        pt3 = self.bezier[2:3][0]

        a, b, c = self._quadraticParameters(pt1, pt2, pt3)
        ## calc first derivative
        ax, ay = (a * 2)
        bx, by = b
        roots = []

        if ax != 0:
            roots.append(-bx/ax)
        if ay != 0:
            roots.append(-by/ay)

        points = [a * t * t + b * t + c for t in roots if 0 <= t < 1] + [pt1, pt3]
        
        xMin, yMin = numpy.minimum.reduce(points)
        xMax, yMax = numpy.maximum.reduce(points)
        
        return xMin, yMin, xMax, yMax

    def _cubicBounds(self, pt1, pt2, pt3, pt4):
        a, b, c, d = self.calculateCubicParameters(pt1, pt2, pt3, pt4)
        # calc first derivative
        ax, ay = a * 3.0
        bx, by = b * 2.0
        cx, cy = c
        xRoots = [t for t in self.solveQuadratic(ax, bx, cx) if 0 <= t < 1]
        yRoots = [t for t in self.solveQuadratic(ay, by, cy) if 0 <= t < 1]
        roots = xRoots + yRoots
    
        points = [(a*t*t*t + b*t*t + c * t + d) for t in roots] + [pt1, pt4]

        xMin, yMin = numpy.minimum.reduce(points)
        xMax, yMax = numpy.maximum.reduce(points)
        return xMin, yMin, xMax, yMax


    def solveQuadratic(self, a, b, c, sqrt=math.sqrt):
        """
        Solve a quadratic equation where a, b and c are real.
        a*x*x + b*x + c = 0
        This function returns a list of roots. Note that the returned list
        is neither guaranteed to be sorted nor to contain unique values!
        """
        if abs(a) < EPSILON:
            if abs(b) < EPSILON:
                ## We have a non-equation; therefore, we have no valid solution
                roots = []
            else:
                ## We have a linear equation with 1 root.
                roots = [-c/b]
        else:
            ## We have a true quadratic equation.  Apply the quadratic formula to find two roots.
            DD = b*b - 4.0*a*c
            if DD >= 0.0:
                rDD = sqrt(DD)
                roots = [(-b+rDD)/2.0/a, (-b-rDD)/2.0/a]
            else:
                ## complex roots, ignore
                roots = []

        return roots


    def solveCubic(self, a, b, c, d, abs=abs, pow=math.pow, sqrt=math.sqrt, cos=math.cos, acos=math.acos, pi=math.pi):
        """
        Solve a cubic equation where a, b, c and d are real.
        a*x*x*x + b*x*x + c*x + d = 0
        This function returns a list of roots. Note that the returned list
        is neither guaranteed to be sorted nor to contain unique values!
        """
        if abs(a) < epsilon:
            return self.solveQuadratic(b, c, d)

        a = float(a)
        a1 = b/a
        a2 = c/a
        a3 = d/a
        
        Q = (a1*a1 - 3.0*a2)/9.0
        R = (2.0*a1*a1*a1 - 9.0*a1*a2 + 27.0*a3)/54.0
        R2_Q3 = R*R - Q*Q*Q
    
        if R2_Q3 < 0:
            theta = acos(R/sqrt(Q*Q*Q))
            rQ2 = -2.0*sqrt(Q)
            x0 = rQ2*cos(theta/3.0) - a1/3.0
            x1 = rQ2*cos((theta+2.0*pi)/3.0) - a1/3.0
            x2 = rQ2*cos((theta+4.0*pi)/3.0) - a1/3.0
            return [x0, x1, x2]
        else:
            if Q == 0 and R == 0:
                x = 0
            else:
                x = pow(sqrt(R2_Q3)+abs(R), 1/3.0)
                x = x + Q/x
                if R >= 0.0:
                    x = -x
                    x = x - a1/3.0
                return [x]


    def _quadraticParameters(self, pt1, pt2, pt3):
        c = pt1
        b = (pt2 - c) * 2.0
        a = pt3 - c - b

        return a, b, c


    def calculateCubicParameters(self, pt1, pt2, pt3, pt4):
        pt1, pt2, pt3, pt4 = numpy.array((pt1, pt2, pt3, pt4))
        d = pt1
        c = (pt2 - d) * 3.0
        b = (pt3 - pt2) * 3.0 - c
        a = pt4 - d - c - b
        return a, b, c, d


    def calculateQuadraticPoints(self, a, b, c):
        pt1 = c
        pt2 = (b * 0.5) + c
        pt3 = a + b + c
        return pt1, pt2, pt3


    def calculateCubicPoints(self, a, b, c, d):
        pt1 = d
        pt2 = (c / 3.0) + d
        pt3 = (b + c) / 3.0 + pt2
        pt4 = a + d + c + b
        return pt1, pt2, pt3, pt4

    def in_path(self, point_):
        if isinstance(_point, point):
            test_X, test_Y = _point.pos
        elif isinstance(_point, (tuple, list)):
            test_X, test_Y = _point

        C = False
        
        for i in range(len(self.polygon)):
            if isinstance(self.polygon[i], bezier):
                interpolation = self.polygon[i].interpolate()
                for k in range(len(interpolation)):
                    pt = interpolation[k]
                    vertex.append([pt[0], pt[1]])

            elif isinstance(self.polygon[i], line):
                sub_1 = self.polygon[i].point
                sub_2 = self.polygon[i].point2
                vertex.append([sub_1.X, sub_1.Y])
                vertex.append([sub_2.X, sub_2.Y])
            
        j = len(vertex) - 1
        for k in range(len(vertex) - 1):
            j = k + 1

            if (((vertex[i][1] > test_Y) != (vertex[j][1] > test_Y))\
            and (test_X < (vertex[i][0] - vertex[j][0]) * ((test_Y - vertex[i][1])\
            / (vertex[j][1] - vertex[i][1]) + vertex[i][0]))):
                    C = not C


        return C
