from pypaint import cGeometry
from pypaint.cGeometry import point
from pypaint.cGeometry import polygon
from pypaint.cGeometry import bezier

from math import *

import unittest

class testGeometry(unittest.TestCase):
    def test_in_polygon(self):
        test_point_x = 5
        test_point_y = 56

        polygonX = [1, 2, 4]
        polygonY = [2, 3, 5]

        in_poly = cGeometry.in_polygon(3, test_point_x, test_point_y, polygonX, polygonY)
        assert in_poly == False
        
    def test_points(self):
        p = point(3, 4)
        assert p.X == 3
        assert p.Y == 4
        
    def test_polygon(self):
        p1 = point(3, 4)
        p2 = point(4, 5)
        
        poly = polygon()
        poly.add_line(p1, p2)

    def test_bezier(self):
        ## 0, 60, 40, 100, 100, 100, 200, 200
        p1 = point(0, 60)
        p2 = point(40, 100)
        p3 = point(100, 100)
        p4 = point(200, 200)
        
        poly = bezier()
        poly.add_line(p1, p2, p3, p4)

        n = 600
        length = 0
        xi = p1.X
        yi = p1.Y

        for x in range(n):
            t = 1.0 * (x+1.0)/n
            (pt_x, pt_y) = poly.curve_point(t)[:2]
            print pt_x, pt_y
            c = sqrt(pow(abs(xi - pt_x), 2.0) + pow(abs(yi - pt_y), 2.0))
            length += c
            xi = pt_x
            yi = pt_y

        #print poly.line_set
    
        print length

if __name__ == '__main__':
    unittest.main()
