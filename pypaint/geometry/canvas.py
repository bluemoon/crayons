from pypaint.geometry.bezier import *

import numpy as np

class layer:
    objects = None

    def __init__(self):
        self.objects = []
        self.bounds  = []
        
    def add(self, Object):
        self.objects.append(Object)
        self.bounds.append(Object.bound_box)

class canvas:
    pass
