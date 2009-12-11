from pypaint.geometry.transform import *

import numpy

class Point:
    X = None
    Y = None

    def __init__(self, *arguments):
        if len(arguments) == 1 and isinstance(arguments[0], (list, tuple)):
            self.X = arguments[0][0]
            self.Y = arguments[0][1]
        

class Point_Set:
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
                if isinstance(k, Point):
                    self.point_set.append(k)
                elif isinstance(k, list) and len(k) == 2:
                    point = Point(k)
                    self.point_set.append(point)
                
    def add(self, *point):
        self._pointConv(*point)
    
    
    def bounds(self):
        x_min = 0
        x_max = 0
        y_min = 0
        y_max = 0

        for k in self.point_set:
            x_max = max(x_max, k.X)
            y_max = max(y_max, k.Y)
            x_min = min(x_min, k.X)
            y_min = min(y_min, k.Y)

        return (x_min, y_min, x_max, y_max)

    bound_box = property(bounds)

    def scale(self, X, Y=None):
        output = []

        self.transform = Scale(X, Y)

        for k in self.point_set:
            (k.X, k.Y) = self.transform.transformPoint((k.X, k.Y))


