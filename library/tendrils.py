import sys
import os

sys.path.append(os.getcwd()) 

from pyPaint import PyPaintContext as Context
from nb_types.canvas import BezierPath
from math    import pi, sin, cos, radians

from util_random import random

ctx = Context(width=600, height=600)

class Tendril:
    def __init__(self, x, y, width=3):
        """ 
        A new sinewy tendril at location x and y.
        Its segment width will gradually become smaller as it grows.
        """
        self.x = x
        self.y = y
        self.width = width
        self.angle = random(2*pi) - pi ## random angle in radians.
        self.segments = []
        self.v = 0
 
    def grow(self, distance=3.0, curl=1.0, step=0.01):
        """ Tendril segment growth using fluid, spiral sine functions,
        taken from the ART+COM Tendrils class for Processing.
        """
        ## Think of a tendril having a steering compass.
        ## For each new segment, the compass shifts a bit left or right.
        self.x += cos(self.angle) * distance
        self.y += sin(self.angle) * distance
        self.v += random(-step, step)
        self.v *= 0.9 + curl*0.1
        self.angle += self.v
        self.segments.append(
            (self.x, self.y, self.angle)
        )
        
    def draw(self, path=None):
        """ Draws all the segments in the tendril,
        as separate ovals or as a single path if one is supplied.
        """
        n = len(self.segments)
        for i, (x, y, angle) in enumerate(self.segments):
            r = (1-float(i)/n) * self.width # size gradually decreases.
            if path != None:
                path.oval(x, y, r, r)
            else:
                ctx.oval(x, y, r, r)
        
class Plant:
    def __init__(self, x, y, tendrils=30, width=6.0):
        """ A collection of tendrils.
        """
        self.x = x
        self.y = y
        self.tendrils = []
        for i in range(tendrils): 
            self.tendrils.append(
                Tendril(self.x, self.y, width)
            )
    
    def grow(self, distance=5.0, curl=1.0, step=0.01):
        """ Grow a new segment on each of the plant's tendrils.
        """
        for b in self.tendrils:
            b.grow(distance, curl, step)
            
    def draw(self):
        """ Draw the plant.
        """
        for tendril in self.tendrils:
            tendril.draw()
        
    def path(self):
        """ Return the plant as a path consisting of ovals.
        """
        path = BezierPath()
        for tendril in self.tendrils:
            tendril.draw(path)

        return path
 
ctx.background(0.12, 0.12, 0.06)
ctx.nofill()
ctx.stroke(1, 0.5)
ctx.strokewidth(0.5)
 
plant = Plant(300, 300, tendrils=50)
for i in range(20): 
    plant.grow(curl=5.0, step=0.01)
 
plant.draw()

ctx.save('')
