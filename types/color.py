import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.getcwd(), "nb_types")))

import util

class Color(object):
    '''
    Taken from Nodebox colors library and modified.
    Since we have no Cocoa, we have no way to use colour management for the moment.
    So we took another approach.

    Attributes:
    r, g, b (0-1)
    hue, saturation, lightness (0-1)

    This stores color values as a list of 4 floats (RGBA) in a 0-1 range.

    The value can come in the following flavours:
    - v
    - (v)
    - (v,a)
    - (r,g,b)
    - (r,g,b,a)
    - #RRGGBB
    - RRGGBB
    - #RRGGBBAA
    - RRGGBBAA
    
    The CMYK parts have been commented out, as it may slow down code execution
    and at this point is quite useless, left it in place for a possible future implementation
    '''

    def __init__(self, *args, **kwargs):
        parameters = len(args)

        # Values are supplied as a tuple.
        if parameters == 1 and isinstance(args[0], tuple):
            a = args[0]
            
        # No values or None, transparent black.
        if parameters == 0 or (parameters == 1 and args[0] == None):
            raise Exception("got Color() with value None!")
            self.r, self.g, self.b, self.a = 0, 0, 0, 0
            
        # One value, another color object.
        elif parameters == 1 and isinstance(args[0], Color):
            self.r, self.g, self.b, self.a = args[0].r, args[0].g, args[0].b, args[0].a
            
        # One value, a hexadecimal string.
        elif parameters == 1 and isinstance(args[0], str):
            r, g, b, a = util.hex2rgb(args[0])
            self.r, self.g, self.b, self.a = r, g, b, a
            
        # One value, grayscale.
        elif parameters == 1:
            if kwargs.has_key("color_range"):
                ra = int(kwargs["color_range"])
            else:
                ra = 1
            
            print type(args)
            self.r, self.g, self.b, self.a = args[0]/ra, args[0]/ra, args[0]/ra, 1
            
        # Two values, grayscale and alpha.
        elif parameters == 2:
            if kwargs.has_key("color_range"):
                ra = int(kwargs["color_range"])
            else:
                ra = 1

            print type(args[0])
            self.r, self.g, self.b, self.a = args[0]/ra, args[0]/ra, args[0]/ra, args[1]/ra
            
        # Three to five parameters, either RGB, RGBA, HSB, HSBA, CMYK, CMYKA
        # depending on the mode parameter.
        elif parameters >= 3:
            if kwargs.has_key("color_range"):
                ra = int(kwargs["color_range"])
            else:
                ra = 1            

            alpha, mode = 1, "rgb" 
            if parameters > 3: 
                alpha = args[-1]/ra
        
            if kwargs.has_key("mode"): 
                mode = kwargs["mode"].lower()
            if mode == "rgb":                
                self.r, self.g, self.b, self.a = args[0]/ra, args[1]/ra, args[2]/ra, alpha               
            elif mode == "hsb":                
                self.h, self.s, self.brightness, self.a = args[0]/ra, args[1]/ra, args[2]/ra, alpha


        self.red   = self.r
        self.green = self.g
        self.blue  = self.b
        self.alpha = self.a

        self.data = [self.r, self.g, self.b, self.a]


    def __repr__(self):
        return "%s(%.3f, %.3f, %.3f, %.3f)" % (self.__class__.__name__, 
            self.red, self.green, self.blue, self.alpha)

    def copy(self):
        return tuple(self.data)
        
    def _update_rgb(self, r, g, b):
        self.__dict__["__r"] = r
        self.__dict__["__g"] = g
        self.__dict__["__b"] = b
    
    #def _update_cmyk(self, c, m, y, k):
        #self.__dict__["__c"] = c
        #self.__dict__["__m"] = m
        #self.__dict__["__y"] = y
        #self.__dict__["__k"] = k
        
    def _update_hsb(self, h, s, b):
        self.__dict__["__h"] = h
        self.__dict__["__s"] = s
        self.__dict__["__brightness"] = b
    
    def _hasattrs(self, list):
        for a in list:
            if not self.__dict__.has_key(a):
                return False
        return True
    
    #added
    def __getitem__(self, index):
        return (self.r, self.g, self.b, self.a)[index]
        

    def __iter__(self):
        for i in range(len(self.data)):
           yield self.data[i]

    def __div__(self, other):
        value = float(other)
        return (self.red/value, self.green/value, self.blue/value, self.alpha/value)    
    #end added


    def __setattr__(self, a, v):
        
        if a in ["a", "alpha"]:
            self.__dict__["__"+a[0]] = max(0, min(v, 1))
        
        # RGB changes, update CMYK and HSB accordingly.
        elif a in ["r", "g", "b", "red", "green", "blue"]:
            self.__dict__["__"+a[0]] = max(0, min(v, 1))
            if self._hasattrs(("__r", "__g", "__b")):
                r, g, b = (
                    self.__dict__["__r"], 
                    self.__dict__["__g"], 
                    self.__dict__["__b"]
                )
                #self._update_cmyk(*util.rgb2cmyk(r, g, b))
                self._update_hsb(*util.rgb2hsb(r, g, b))
        
        # HSB changes, update RGB and CMYK accordingly.
        elif a in ["h", "s", "hue", "saturation", "brightness"]:
            if a != "brightness": a = a[0]
            if a == "h": v = min(v, 0.99999999)
            self.__dict__["__"+a] = max(0, min(v, 1))
            if self._hasattrs(("__h", "__s", "__brightness")):
                r, g, b = util.hsb2rgb(
                    self.__dict__["__h"], 
                    self.__dict__["__s"], 
                    self.__dict__["__brightness"]
                )
                self._update_rgb(r, g, b)
                #self._update_cmyk(*util.rgb2cmyk(r, g, b))
        
        # CMYK changes, update RGB and HSB accordingly.
        #elif a in ["c", "m", "y", "k", "cyan", "magenta", "yellow", "black"]:
            #if a != "black": a = a[0]
            #self.__dict__["__"+a] = max(0, min(v, 1))
            #if self._hasattrs(("__c", "__m", "__y", "__k")):
                #r, g, b = util.cmyk2rgb(
                    #self.__dict__["__c"], 
                    #self.__dict__["__m"], 
                    #self.__dict__["__y"], 
                    #self.__dict__["__k"]
                #)
                #self._update_rgb(r, g, b)
                #self._update_hsb(*util.rgb2hsb(r, g, b))
                
        else:
            self.__dict__[a] = v

    def __getattr__(self, a):
        
        """ Available properties:
        r, g, b, a or red, green, blue, alpha
        c, m, y, k or cyan, magenta, yellow, black,
        h, s or hue, saturation, brightness
        
        """
        
        if self.__dict__.has_key(a):
            return a
        #elif a == "black":
            #return self.__dict__["__k"]        
        elif a == "brightness":
            return self.__dict__["__brightness"]
        #CMYK
        #elif a in ["a", "alpha",
                   #"r", "g", "b", "red", "green", "blue",
                   #"h", "s", "hue", "saturation",
                   #"c", "m", "y", "k", "cyan", "magenta", "yellow"]:
        #NO-CMYK 
        elif a in ["a", "alpha",
                   "r", "g", "b", "red", "green", "blue",
                   "h", "s", "hue", "saturation"]:
            return self.__dict__["__"+a[0]]
        
        raise AttributeError, "'"+str(self.__class__)+"' object has no attribute '"+a+"'"

