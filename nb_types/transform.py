from math import *

class Matrix:
    matrix = None

    def __init__(self, matrix=None):
        self.matrix = matrix

    def translate(self, draw, x, y):
        self.matrix = (1.0, 0.0, 0.0, 1.0, x, y)
        #self.transform(draw)
    
    #def transform(self, draw):
    #    draw.settransform(self.matrix)
        
class Transform(object):
    def __init__(self, transform=None):
        self._transforms = []
        self.stack = []

        if transform is None:
            pass

        elif isinstance(transform, Transform):
            self.append(transform)

        elif isinstance(transform, (list, tuple)):
            matrix = tuple(transform)
            t = Matrix(*matrix)
            self.append(t)

        elif isinstance(transform, Matrix):
            self.append(transform)

        else:
            raise ShoebotError, _("Transform: Don't know how to handle transform %s.") % transform

    def translate(self, x, y):
        t = ('translate', x, y)
        self.stack.append(t)

    def scale(self, x, y):
        t = ('scale', x, y)
        self.stack.append(t)

    def rotate(self, a):
        t = ('rotate', a)
        self.stack.append(t)

    def skew(self, x, y):
        t = ('skew', x, y)
        self.stack.append(t)

    def push(self):
        t = ('push',)
        self.stack.append(t)

    def pop(self):
        t = ('pop',)
        self.stack.append(t)

    def append(self, t):
        if isinstance(t, Transform):
            for item in t.stack:
                self.stack.append(item)
        elif isinstance(t, Matrix):
            self.stack.append(t)
        else:
            raise Exception("Transform: Can only append Transforms or Matrices (got %s)" % (t))

    def prepend(self,t):
        if isinstance(t, Transform):
            newstack = []
            for item in t.stack:
                newstack.append(item)
            for item in self.stack:
                newstack.append(item)
            self.stack = newstack
        elif isinstance(t, cairo.Matrix):
            self.stack.insert(0,t)
        else:
            raise Exception("Transform: Can only append Transforms or Matrices (got %s)" % (t))

    def copy(self):
        return self.__class__(self)

    def __iter__(self):
        for value in self.stack:
            yield value

    def __iter__(self):
        for value in self.matrix:
            yield value

    def rotate(self, degrees=0, radians=0):
        ## trans_affine(cos(a), sin(a), -sin(a), cos(a), 0.0, 0.0)
        if degrees:
            self._transforms.append((cos(degrees), sin(degrees), -sin(degrees), cos(degrees), 0.0, 0.0))
        else:
            degrees = (pi * radians)/180
            self._transforms.append((cos(degrees), sin(degrees), -sin(degrees), cos(degrees), 0.0, 0.0))


    def translate(self, x=0, y=0):
        self._transforms.append((1.0, 0.0, 0.0, 1.0, x, y))

    def scale(self, x=1, y=None):
        if y is None:
            self._transforms.append((x, 0.0, 0.0, x, 0.0, 0.0))
        else:
            self._transforms.append((x, 0.0, 0.0, y, 0.0, 0.0))

    def skew(self, x=0, y=0):
        ## trans_affine(1.0, tan(y), tan(x), 1.0, 0.0, 0.0)
        pass

    def getMatrixWCenter(self, x, y, mode):
        centerx = x
        centery = y
        m_archived = []
        
        for trans in self.stack: 
            if isinstance(trans, tuple) and trans[0] in TRANSFORMS:
                ## parse transform command
                cmd  = trans[0]
                args = trans[1:]
                
                if cmd == 'translate':       
                    xt = args[0]
                    yt = args[1]

                    self.translate(xt, yt)

                elif cmd == 'rotate':
                    #if mode == 'corner':                        
                        # apply existing transform to cornerpoint
                    #    deltax, deltay = m.transform_point(0,0)
                    #    a = args[0]

                    #    ct = cos(a)
                    #    st = sin(a)
                        #m *= cairo.Matrix(ct, st, -st, ct, deltax - (ct*deltax) + (st*deltay),deltay-(st*deltax)-(ct*deltay)) 

                    if mode == 'center':
                        # apply existing transform to centerpoint
                        deltax, deltay = m.transform_point(centerx, centery)
                        a = args[0]
                        
                        ct = cos(a)
                        st = sin(a)
                        m = Matrix(ct, st, -st, ct,deltax-(ct*deltax)+(st*deltay),deltay-(st*deltax)-(ct*deltay)) 

                elif cmd == 'scale':
                    if mode == 'corner':
                        self.scale(args[0], args[1])
                        #m *= t

                    elif mode == 'center':
                        # apply existing transform to centerpoint
                        deltax, deltay = m.transform_point(centerx, centery)
                        x, y = args
                        m1 = Matrix()
                        m2 = Matrix()
                        m1.translate(-deltax, -deltay)
                        m2.translate(deltax, deltay)
                        m *= m1
                        m *= cairo.Matrix(x,0,0,y,0,0)
                        m *= m2

                elif cmd == 'skew':
                    if mode == 'corner':
                        x, y = args
                        ## TODO: x and y should be the tangent of an angle
                        t *= Matrix(1,0,x,1,0,0)
                        t *= Matrix(1,y,0,1,0,0)
                        m *= t
                    elif mode == 'center':
                        # apply existing transform to centerpoint
                        deltax, deltay = m.transform_point(centerx, centery)
                        x,y = args
                        m1 = cairo.Matrix()
                        m2 = cairo.Matrix()
                        m1.translate(-deltax, -deltay)
                        m2.translate(deltax, deltay)
                        t *= m
                        t *= m1
                        t *= cairo.Matrix(1,0,x,1,0,0)
                        t *= cairo.Matrix(1,y,0,1,0,0)
                        t *= m2
                        m = t
                elif cmd == 'push':
                    m_archived.append(m)
                elif cmd == 'pop':
                    m = m_archived.pop()

        return self._transforms       

    def get_matrix(self):
        '''
        Returns this transform's matrix. Its centerpoint is presumed to be (0,0).
        '''

        return self.getMatrixWCenter(0,0)
