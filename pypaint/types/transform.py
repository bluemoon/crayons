from math import *
import numpy as np
from numpy import array

TRANSFORMS = ['translate', 'scale', 'rotate', 'skew', 'push', 'pop']

class Matrix:
    matrix = None

    def __init__(self, matrix=None):
        if not matrix:
            self.matrix = np.array([1.0, 0.0, 0.0, 1.0, 0.0, 0.0])
        else:
            self.matrix = np.array(matrix)

    def _setTuple(self, matrix):
        self.matrix = matrix

    def _toTuple(self):
        return self.matrix.tolist()
    
    Tuple = property(_toTuple, _setTuple)

    def _setNumpy(self, matrix):
        self.matrix = np.array(matrix)
        
    def _getNumpy(self):
        return self.matrix
    
    numpy = property(_getNumpy, _setNumpy)

    def __add__(self, other_add):
        (sx1, shy1, shx1, sy1, tx1, ty1) = self._toTuple()
        (sx2, shy2, shx2, sy2, tx2, ty2) = other_add.Tuple

        return Matrix([sx2, shy1+shy2, shx1+shx2, sy2, tx1+tx2, ty1+ty2])




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
            raise Exception("Transform: Don't know how to handle transform %s." % transform)
        
        
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
        elif isinstance(t, Matrix):
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

    def transform_point(self, x, y, matrix):
        (sx, shy, shx, sy, tx, ty) = matrix.tolist()
        deltax = x * sx  +  y * shx + tx
        deltay = x * shy +  y * sy  + ty
        return (x-deltax, y-deltay)

    def getMatrixWCenter(self, x, y, mode):
        centerx = x
        centery = y

        m_archived = []

        m = Matrix()

        for trans in self.stack: 
            if isinstance(trans, tuple) and trans[0] in TRANSFORMS:
                ## parse transform command
                cmd  = trans[0]
                args = trans[1:]
                
                if cmd == 'translate':       
                    xt = args[0]
                    yt = args[1]
                    
                    m += Matrix([1.0, 0.0, 0.0, 1.0,  xt,  yt])

                elif cmd == 'rotate':
                    if mode == 'corner':                        
                        # apply existing transform to cornerpoint
                        deltax, deltay = m.transform_point(0, 0)
                        
                        a = args[0]

                        ct = cos(a)
                        st = sin(a)

                        m += Matrix([ct, st, -st, ct, deltax - (ct*deltax) + (st*deltay), deltay-(st*deltax)-(ct*deltay)]) 

                    if mode == 'center':
                        ## apply existing transform to centerpoint
                        ## sx(1.0), shy(0.0), shx(0.0), sy(1.0), tx(0.0), ty(0.0)

                        radians = args[0]
                        m_ = np.array([cos(radians), sin(radians), -sin(radians), cos(radians), 0, 0])
                        (deltax, deltay) = self.transform_point(centerx, centery, m_)

                        m += Matrix([cos(radians), sin(radians), -sin(radians), cos(radians), deltax, deltay])

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
        
        
        if isinstance(m, Matrix):
            return m.Tuple
        else:
            return m.tolist()

    def get_matrix(self):
        '''
        Returns this transform's matrix. Its centerpoint is presumed to be (0,0).
        '''

        return self.getMatrixWCenter(0,0)
