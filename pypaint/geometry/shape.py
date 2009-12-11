import math
import numpy

EPSILON        = 1e-15
EPSILON_ONE    = 1 - EPSILON
EPSILON_M_ONE  = -1 + EPSILON
ANGULAR_UNIT   = 1.0
QUADRATIC      = 'quadratic'
CUBIC          = 'cubic'


class point:
    """
    >>> point((3.0, 4.0))
    <point [3.0, 4.0]>
    >>> p = point((4.0, 3.0))
    >>> p.X
    4.0
    >>> p.Y
    3.0

    """
    pos = None

    def __init__(self, *arguments):
        if len(arguments) == 1 and isinstance(arguments[0], (list, tuple)):
            self.pos = numpy.array([arguments[0][0], arguments[0][1]])
        else:
            self.pos = arguments[0]

    def __repr__(self):
        return '<point %s>' % (self.pos.tolist())

    def __div__(self, other):
        """
        >>> p1 = point((3.0, 4.0))
        >>> p2 = point((4.0, 3.0))
        >>> p1 /= p2
        >>> p1
        <point [3.5, 3.5]>

        """
        return self.midpoint_to(other)

    def _get_X(self):
        return self.pos[0]
    X = property(_get_X)

    def _get_Y(self):
        return self.pos[1]
    Y = property(_get_Y)

    def distance_to(self, obj):
        """
        >>> p1 = point((3.0, 4.0))
        >>> p2 = point((4.0, 3.0))
        >>> p1.distance_to(p2)
        1.4142135623730951
        
        """
        if isinstance(obj, point):
            return math.sqrt(sum((self.pos - obj.pos)**2))

    def midpoint_to(self, obj):
        ## Return a point in the middle of 
        ## the shortest line connecting this and obj.
        if isinstance(obj, point):
            return point(0.5 * (self.pos + obj.pos))
        else:
            return obj.midpoint_to(self)

    def projected_on(self, obj):
        if isinstance(obj, line):
            return point(obj.pos + dot(obj.pos, self.pos - obj.pos) * obj.normal)


class point_set:
    point_set = None

    def __init__(self, points):
        if not points:
            self.point_set = []

        elif isinstance(points, list):
            self.point_set = []
            self._pointConv(points)

        elif isinstance(points, Point_Set):
            self.point_set = points
    
        self.transform = Transform()

    def _pointConv(self, points):
        """ Convert from a xxx to a usable format """
        if isinstance(points, list):
            for k in points:
                if isinstance(k, point):
                    self.point_set.append(k)
                elif isinstance(k, list) and len(k) == 2:
                    point = point(k)
                    self.point_set.append(point)
                
    def add(self, *point):
        self._pointConv(*point)
    
    def mass_distribution(self):
        cm = numpy.zeros((1, 3))
        for p in self.point_set:
            cm += p.pos
        
        cm /= len(self.point_set)
        A = asmatrix(zeros((3, 3)))
        for p in self.point_set:
            r = asmatrix(p - cm)
            A += r.transpose() * r

        return asarray(cm).reshape(3), A

    def bounds(self):
        tmp =  numpy.array(self.point_set)
        
        xMin, yMin = numpy.minimum.reduce(tmp)
        xMax, yMax = numpy.maximum.reduce(tmp)
        return xMin, yMin, xMax, yMax

    bound_box = property(bounds)

    def scale(self, X, Y=None):
        output = []

        self.transform = Scale(X, Y)

        for k in self.point_set:
            (k.X, k.Y) = self.transform.transformPoint((k.X, k.Y))






class vector:
    def __init__(self, *arguments):
        if len(arguments) == 1 and isinstance(arguments[0], point):
            self.vector = arguments[0].pos
        elif len(arguments) == 2 and isinstance(arguments[0], (float, int)) and isinstance(arguments[1], (float, int)):
            self.vector = point(arguments[0]).pos - point(arguments[1]).pos
        else:
            raise Exception('wtf: %s' % repr(arguments))

        self.norm = numpy.linalg.norm(self.vector)

    def __repr__(self):
        p = self.points()
        return "<vector(%s, %s)>" % (repr(p[0]),repr(p[1]))

    def __str__(self):
        return repr(self)

    def __add__(self, other):
        _sum = self.vector + other.vector
        return vector(_sum[0], _sum[1])

    def __sub__(self, other):
        _total = self.vector - other.vector
        return vector(_total[0], _total[1])

    def __mul__(self, other):
        _total = self.vector * other.vector
        return vector(_total[0], _total[1])

    def __rmul__(self, other):
        return self.__mul__(other)
    
    def __div__(self, other):
        _total = self.vector / other.vector
        return vector(_total[0], _total[1])

    def __neg__(self):
        return vector(-self.vector[0], -self.vector[1])

    def __abs__(self):
        return self.length()

    def __getitem__(self, index):
        if index == 0:
            return self.vector[0]
        elif index == 1:
            return self.vector[1]
        else:
            raise IndexError

    def __iter__(self):
        return self.__vec2__.__iter__()

    def __len__(self):
        """The number of dimensions for the vector, always two."""
        return 2

    def _get_bounds(self):
        x_min, y_min, x_max, y_max = (1e308, 1e308, 0, 0)
        for x in (self.pt_1, self.pt_2):
            x_min = min(x_min, x.X)
            y_min = min(y_min, x.Y)
            x_max = max(x_max, x.X)
            y_max = max(y_max, x.Y)

        return (x_min, y_min, x_max, y_max)

    bounds = property(_get_bounds)

    def _get_X(self):
        return self.vector[0]
    X = property(_get_X)

    def _get_Y(self):
        return self.vector[1]
    Y = property(_get_Y)

    def angle(self, _vector=None):
        """
        Return the length of the given vector.
        >>> b = vector(25, 0)
        >>> b.angle()
        3.1415926535897931

        """
        if not _vector:
            _vector = vector(0, 1) 

        return numpy.arccos((numpy.dot(self.vector, _vector.vector)) / (self.magnitude() * _vector.magnitude())) 

    def angle_in_degrees(self, Vector=None):
        """
        Return the length of the given vector.
        >>> b = vector(25.0, 0.0)
        >>> b.angle_in_degrees()
        180.0

        """
        return (self.angle(Vector) * 180) /math.pi 

    def normalize(self):
        len = self.magnitude()
        return (self.vector/len)

    def magnitude(self):
        """
        Return the length of the given vector.
        >>> b = vector(25, 0)
        >>> b.magnitude()
        25.0

        """
        return numpy.sqrt(numpy.dot(self.vector, self.vector))

    def magnitude_squared(self):
        return sum(self.vector ** 2)

    def perpendicular(self):
        return vector(-self.vector[0], self.vector[1])

    def unit(self):
        return self.vector / self.magnitude() 

    def projection(self, Vector):
        """
        Return the length of the given vector.
        formula: b(dot(a,b)/(|b|^2))
        >>> b = vector(25, 0)
        """
        print self * numpy.dot(self.vector, Vector.vector) / numpy.dot(self.vector, self.vector)
        length = Vector.magnitude_squared()
        k = self.vector * numpy.dot(Vector.vector, self.vector)/numpy.dot(self.vector, self.vector)
        length = k/length
        m = length * Vector.vector
        print m

        #magnitude  = numpy.sqrt(n)
        #projection = k/magnitude

        return k.tolist()


    def cross(self, vector):
        return self.vector[0] * vector.vector[1] - self.vector[1] * vector.vector[0] 
    

    def transform(self, transformation):
        #transformation
        pass

class line:
    def __init__(self, *arguments):
        self.base   = None
        self.vector = None

        if len(arguments) == 2 and isinstance(arguments[0], point) and isinstance(arguments[1], point):
            self.point  = point_1
            self.point2 = point_2
            self.vector = vector(self.point)
            self.vector2 = vector(self.point2)

        elif len(arguments) == 4 and map(lambda x: isinstance(x, (int, float)), arguments):
            self.point   = point((arguments[0], arguments[1]))
            self.point2  = point((arguments[2], arguments[3]))
            self.vector  = vector(self.point)
            self.vector2 = vector(self.point)

        self.along = (self.vector2 - self.vector)
        self.distance = self.point.pos - self.point2.pos

        

    def _get_bounds(self):
        return (0,0,0,0)
    bounds = property(_get_bounds)

    def points(self):
        """
        >>> b = line(25, 0, 50, 100)
        >>> b.points()
        (25.0, 0.0, 50.0, 100.0)
        >>> b = line(25, 0, 190, 100)
        >>> b.points()
        (25.0, 0.0, 190.0, 100.0)
    
        """
        parallel = self.along.projection(self.point2.pos)
        return parallel + self.offset

        #o_vector = vector(self.point)
        #projection = self.along.projection(o_vector)
        #print projection * self.vector.vector * self.distance
        #return (float(self.point.X), float(self.point.Y), projection[0], projection[1])


    def distance_to(self, obj):
        if isinstance(obj, point):
            return obj.distance_to(self)

        elif isinstance(obj, line):
            d = obj.normal - self.normal
            n = cross(self.normal, obj.normal)

            if abs2(n) < 1e-16: # parallel lines
                return math.sqrt(abs2(cross(d, self.normal)))
            else:
                return abs(dot(d,n))/math.sqrt(abs2(n))

    def angle_to(self, obj):
        if isinstance(obj, vector):
            return math.acos(min(1, abs(dot(self.normal, obj.normal))))

    def midpoint_to(self,obj):
        """ Return a point in the middle of the shortest line connecting this and obj. """
        if isinstance(obj, point):
            return obj.midpoint_to(obj.projected_on(self))
        elif isinstance(obj, vector):
            d = obj.r - self.r
            t1t2 = dot(self.t,obj.t)
            if abs(abs(t1t2)-1) < 1e-12: #parallel case                
                d = orthogonalized_to(d,self.t)
                return point(self.r + 0.5*d)
            else:
                t1d = dot(d, self.t)
                t2d = dot(d, obj.t)
                s = (t1t2*t2d - t1d)/(t1t2**2-1)
                u = (t1t2*t1d - t2d)/(t1t2**2-1)
                return Point(0.5*(obj.r + u*obj.t  + self.r + s*self.t))                
        else:
            return obj.midpoint_to(self)


class bezier:
    def __init__(self, *arguments):
        self.type = None

        if len(arguments) == 1:
            self.bezier = arguments[0]

        elif len(arguments) == 3:
            self.bezier = numpy.array(arguments)
            self.type   = QUADRATIC

        elif len(arguments) == 4:
            self.bezier = numpy.array(arguments)
            self.type   = CUBIC

    def _get_bounds(self):
        if self.type == QUADRATIC:
            return self._quadraticBounds()
        elif self.type == CUBIC:
            return self._cubicBounds()

    bounds = property(_get_bounds)

    def interpolate(self, precision=100):
        if self.type == QUADRATIC:
            return self._quadraticBounds()
        elif self.type == CUBIC:
            return self.interpolateCubic(precision=precision)


    def _quadraticBounds(self):
        """
        Return the bounding rectangle for a qudratic bezier segment.

        >>> b = bezier([0, 0], [50, 100], [100, 0])
        >>> b.bounds
        (0.0, 0.0, 100.0, 50.0)

        >>> b = bezier([0, 0], [100, 0], [100, 100])
        >>> b.bounds
        (0.0, 0.0, 100.0, 100.0)

        """
        
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

    def _cubicBounds(self):
        """
        Return the bounding rectangle for a cubic bezier segment.
        
        >>> b = bezier([0, 0], [25, 100], [75, 100], [100, 0])
        >>> b.bounds
        (0.0, 0.0, 100.0, 75.0)
        >>> b = bezier((0, 0), (50, 0), (100, 50), (100, 100))
        >>> b.bounds
        (0.0, 0.0, 100.0, 100.0)
        >>> b = bezier((50, 0), (0, 100), (100, 100), (50, 0))
        >>> b.bounds
        (35.566243270259356, 0.0, 64.433756729740679, 75.0)
        """
        pt1 = self.bezier[0:1][0]
        pt2 = self.bezier[1:2][0]
        pt3 = self.bezier[2:3][0]
        pt4 = self.bezier[3:4][0]

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

    def interpolateCubic(self, precision=1000):
        """
        Return the bounding rectangle for a cubic bezier segment.
        
        >>> b = bezier([0, 0], [25, 100], [75, 100], [100, 0])
        >>> b.interpolate(precision=3)
        array([[  0.        ,   0.        ],
               [ 30.55555556,  70.37037037],
               [ 61.11111111,  96.2962963 ]])
        """
        out = []

        pt1 = self.bezier[0:1][0]
        pt2 = self.bezier[1:2][0]
        pt3 = self.bezier[2:3][0]
        pt4 = self.bezier[2:3][0]
        
        
        for t in range(precision):
            t = t/float(precision)
            mint = 1 - t
            
            P1 = pt1 * mint + pt2 * t
            P2 = pt2 * mint + pt3 * t
            P3 = pt3 * mint + pt4 * t

            C1 = P1 * mint + P2 * t
            C2 = P2 * mint + P3 * t
            
            output = C1 * mint + C2 * t
            out.append(output)

        return numpy.array(out)

class complex_polygon:
    polygon = None

    def __init__(self):
        self.polygon = []

    def add(self, Object):
        if isinstance(Object, line):
            self.polygon.append(Object)
        elif isinstance(Object, bezier):
            self.polygon.append(Object)
        else:
            raise Exception('WrongType: should be a bezier or a line not a %s' % (type(Object)))

    def _get_bounds(self):
        """
        >>> p = complex_polygon()
        >>> p.add(line(1, 3, 5, 7))
        >>> p.add(line(5, 7, 6, 8))
        >>> p.add(line(6, 8, 1, 3))
        
        
        """
        x_min, y_min, x_max, y_max = (1e308, 1e308, 0, 0)
        for x in self.polygon:
            x_min = min(x_min, x.bounds[0])
            y_min = min(y_min, x.bounds[1])
            x_max = max(x_max, x.bounds[2])
            y_max = max(y_max, x.bounds[3])
        
        return (x_min, y_min, x_max, y_max)

    bounds = property(_get_bounds)

    def in_polygon(self, _point):
        """
        >>> p = complex_polygon()
        >>> p.add(line(1, 3, 5, 7))
        >>> p.add(line(5, 7, 6, 8))
        >>> p.add(line(6, 8, 1, 3))

        >>> p.in_polygon((0, 0))
        False
        >>> p.in_polygon((3, 4))
        True

        >>> p = complex_polygon()
        >>> p.add(bezier([0, 0], [25, 100], [75, 100], [100, 0]))
        >>> p.add(line(0, 0, 100, 200))
        >>> p.add(line(100, 200, 75, 100))
        >>> p.in_polygon((1, 1))
        True
        >>> p.in_polygon((100, 100))
        False

        """
        vertex = []

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

class layer:
    objects = None

    def __init__(self):
        self.objects = []
        self.bounds  = []
        
    def add(self, Object):
        self.objects.append(Object)
        self.bounds.append(Object.bounds)

    def _get_bounds(self):
        x_min, y_min, x_max, y_max = (1e308, 1e308, 0, 0)

        for x in self.bounds:
            x_min = min(x_min, x.bounds[0])
            y_min = min(y_min, x.bounds[1])
            x_max = max(x_max, x.bounds[2])
            y_max = max(y_max, x.bounds[3])
        
        return (x_min, y_min, x_max, y_max)

    bounds = property(_get_bounds)

class transform:
    """
    2x2 transformation matrix plus offset, a.k.a. Affine transform.
    Transform instances are immutable: all transforming methods, eg.
    rotate(), return a new Transform instance.
    
    Examples:
    
    >>> t = transform()
    >>> t
    <transform [1 0 0 1 0 0]>
    >>> t.scale(2)
    <transform [2 0 0 2 0 0]>
    >>> t.scale(2.5, 5.5)
    <transform [2.5 0.0 0.0 5.5 0 0]>
    >>>
    >>> t.scale(2, 3).transformPoint((100, 100))
    (200, 300)
	
    """
    
    def __init__(self, xx=1, xy=0, yx=0, yy=1, dx=0, dy=0):
        """Transform's constructor takes six arguments, all of which are
        optional, and can be used as keyword arguments:
        
        >>> transform(12)
        <transform [12 0 0 1 0 0]>
        >>> transform(dx=12)
        <transform [1 0 0 1 12 0]>
        >>> transform(yx=12)
        <transform [1 0 12 1 0 0]>
        >>>
        
        """
        self.__affine = xx, xy, yx, yy, dx, dy
        
    def transformPoint(self, (x, y)):
        """Transform a point.
        
        Example:
        >>> t = transform()
        >>> t = t.scale(2.5, 5.5)
        >>> t.transformPoint((100, 100))
        (250.0, 550.0)
        """
        xx, xy, yx, yy, dx, dy = self.__affine
        return (xx*x + yx*y + dx, xy*x + yy*y + dy)

    def transformPoints(self, points):
        """
        Transform a list of points.
        
        """
        xx, xy, yx, yy, dx, dy = self.__affine
        return [(xx*x + yx*y + dx, xy*x + yy*y + dy) for x, y in points]

    def translate(self, x=0, y=0):
        """
        Return a new transformation, translated (offset) by x, y.
        
        Example:
        >>> t = transform()
        >>> t.translate(20, 30)
        <transform [1 0 0 1 20 30]>
        >>>
        """
        return self.transform((1, 0, 0, 1, x, y))
    
    def scale(self, x=1, y=None):
        """Return a new transformation, scaled by x, y. The 'y' argument
        may be None, which implies to use the x value for y as well.
        
        Example:
        >>> t = transform()
        >>> t.scale(5)
        <transform [5 0 0 5 0 0]>
        >>> t.scale(5, 6)
        <transform [5 0 0 6 0 0]>
        >>>
        """
        if y is None:
            y = x
            
        return self.transform((x, 0, 0, y, 0, 0))
    
    def rotate(self, angle):
        """
        Return a new transformation, rotated by 'angle' (radians).
       
        >>>
        """

        c = normSinCos(math.cos(angle * (180/math.pi)))
        s = normSinCos(math.sin(angle * (180/math.pi)))
        return self.transform((c, s, -s, c, 0, 0))

    def skew(self, x=0, y=0):
        """Return a new transformation, skewed by x and y.
        
        Example:
        >>> import math
        >>> t = transform()
        >>> t.skew(math.pi / 4)
        <transform [1.0 0.0 1.0 1.0 0 0]>
        >>>
        """
        import math
        return self.transform((1, math.tan(y), math.tan(x), 1, 0, 0))

    def transform(self, other):
        """Return a new transformation, transformed by another
        transformation.
        
        Example:
        >>> t = transform(2, 0, 0, 3, 1, 6)
        >>> t.transform((4, 3, 2, 1, 5, 6))
        <transform [8 9 4 3 11 24]>
        >>>
        """
        xx1, xy1, yx1, yy1, dx1, dy1 = other
        xx2, xy2, yx2, yy2, dx2, dy2 = self.__affine
        return self.__class__(
            xx1*xx2 + xy1*yx2, 
            xx1*xy2 + xy1*yy2,
            yx1*xx2 + yy1*yx2,
            yx1*xy2 + yy1*yy2,
            xx2*dx1 + yx2*dy1 + dx2,
            xy2*dx1 + yy2*dy1 + dy2)
    
    def reverseTransform(self, other):
        """Return a new transformation, which is the other transformation
        transformed by self. self.reverseTransform(other) is equivalent to
        other.transform(self).
        
        Example:
        >>> t = transform(2, 0, 0, 3, 1, 6)
        >>> t.reverseTransform((4, 3, 2, 1, 5, 6))
        <transform [8 6 6 3 21 15]>
        >>> transform(4, 3, 2, 1, 5, 6).transform((2, 0, 0, 3, 1, 6))
        <transform [8 6 6 3 21 15]>
        >>>
        """
        xx1, xy1, yx1, yy1, dx1, dy1 = self.__affine
        xx2, xy2, yx2, yy2, dx2, dy2 = other
        return self.__class__(
            xx1*xx2 + xy1*yx2,
            xx1*xy2 + xy1*yy2,
            yx1*xx2 + yy1*yx2,
            yx1*xy2 + yy1*yy2,
            xx2*dx1 + yx2*dy1 + dx2,
            xy2*dx1 + yy2*dy1 + dy2
            )
    
    def inverse(self):
        """Return the inverse transformation.
        
        >>>
        """
        if self.__affine == (1, 0, 0, 1, 0, 0):
            return self
        xx, xy, yx, yy, dx, dy = self.__affine
        det = float(xx*yy - yx*xy)
        xx, xy, yx, yy = yy/det, -xy/det, -yx/det, xx/det
        dx, dy = -xx*dx - yx*dy, -xy*dx - yy*dy
        return self.__class__(xx, xy, yx, yy, dx, dy)
    
    def toPS(self):
        """
        Return a PostScript representation:
        """
        return "[%s %s %s %s %s %s]" % self.__affine
        
    def __add__(self, other):
        return self.transform(other)
    
    def __len__(self):
        """Transform instances also behave like sequences of length 6:
        >>>
        """
        return 6

    def __getitem__(self, index):
        """Transform instances also behave like sequences of length 6:

        """
        return self.__affine[index]

    def __getslice__(self, i, j):
        """Transform instances also behave like sequences and even support
        slicing:

        >>>
        """

        return self.__affine[i:j]

    def __cmp__(self, other):
        """Transform instances are comparable:

        """
        xx1, xy1, yx1, yy1, dx1, dy1 = self.__affine
        xx2, xy2, yx2, yy2, dx2, dy2 = other
        return cmp((xx1, xy1, yx1, yy1, dx1, dy1),
                   (xx2, xy2, yx2, yy2, dx2, dy2))

    def __hash__(self):
        """Transform instances are hashable, meaning you can use them as
        keys in dictionaries:

        """
        return hash(self.__affine)
    
    def __repr__(self):
        return "<%s [%s %s %s %s %s %s]>" % ((self.__class__.__name__,)
                                             + tuple(map(str, self.__affine)))

class canvas:
    pass





if __name__ == "__main__":
    import doctest
    doctest.testmod()

