from pypaint.utils import util

class Color(object):
    '''
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
            
            self.r, self.g, self.b, self.a = args[0]/ra, args[0]/ra, args[0]/ra, 1
            
        # Two values, grayscale and alpha.
        elif parameters == 2:
            if kwargs.has_key("color_range"):
                ra = int(kwargs["color_range"])
            else:
                ra = 1

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

    def darken(self, step=0.1):
        return Color(self.h, self.s, self.brightness-step, self.a, mode="hsb", name="")
        
    def lighten(self, step=0.1):
        return Color(self.h, self.s, self.brightness+step, self.a, mode="hsb", name="")

    def desaturate(self, step=0.1):
        return Color(self.h, self.s-step, self.brightness, self.a, mode="hsb", name="")

    def saturate(self, step=0.1):
        return Color(self.h, self.s+step, self.brightness, self.a, mode="hsb", name="")

    def adjust_rgb(self, r=0.0, g=0.0, b=0.0, a=0.0):
        return Color(self.r+r, self.g+g, self.b+b, self.a+a, mode="rgb", name="")

    def adjust_hsb(self, h=0.0, s=0.0, b=0.0, a=0.0):
        return Color((self.h+h)%1.0, self.s+s, self.brightness+b, self.a+a, mode="hsb", name="")

    def adjust_contrast(self, step=0.1):
        if self.brightness <= 0.5:
            return self.darken(step)
        else:
            return self.lighten(step)
    
    def rotate_rgb(self, angle=180):
        h = (self.h + 1.0*angle/360)%1
        return Color(h, self.s, self.brightness, self.a, mode="hsb", name="")
    
    def rotate_ryb(self, angle=180):

        """ Returns a color rotated on the artistic RYB color wheel.
        
        An artistic color wheel has slightly different opposites
        (e.g. purple-yellow instead of purple-lime).
        It is mathematically incorrect but generally assumed
        to provide better complementary colors.
    
        http://en.wikipedia.org/wiki/RYB_color_model
    
        """

        h = self.h * 360
        angle = angle % 360

        # Approximation of Itten's RYB color wheel.
        # In HSB, colors hues range from 0-360.
        # However, on the artistic color wheel these are not evenly distributed. 
        # The second tuple value contains the actual distribution.
        wheel = [
            (  0,   0), ( 15,   8),
            ( 30,  17), ( 45,  26),
            ( 60,  34), ( 75,  41),
            ( 90,  48), (105,  54),
            (120,  60), (135,  81),
            (150, 103), (165, 123),
            (180, 138), (195, 155),
            (210, 171), (225, 187),
            (240, 204), (255, 219),
            (270, 234), (285, 251),
            (300, 267), (315, 282),
            (330, 298), (345, 329),
            (360, 0  )
        ]
    
        # Given a hue, find out under what angle it is
        # located on the artistic color wheel.
        for i in _range(len(wheel)-1):
            x0, y0 = wheel[i]    
            x1, y1 = wheel[i+1]
            if y1 < y0:
                y1 += 360
            if y0 <= h <= y1:
                a = 1.0 * x0 + (x1-x0) * (h-y0) / (y1-y0)
                break
    
        # And the user-given angle (e.g. complement).
        a = (a+angle) % 360

        # For the given angle, find out what hue is
        # located there on the artistic color wheel.
        for i in range(len(wheel)-1):
            x0, y0 = wheel[i]    
            x1, y1 = wheel[i+1]
            if y1 < y0:
                y1 += 360
            if x0 <= a <= x1:
                h = 1.0 * y0 + (y1-y0) * (a-x0) / (x1-x0)
                break
    
        h = h % 360
        return Color(h/360, self.s, self.brightness, self.a, mode="hsb", name="")
    complement = property(rotate_ryb)

    @property
    def is_black(self):
        if self.r == self.g == self.b < 0.08:
            return True
        return False
        
    @property
    def is_white(self):
        if self.r == self.g == self.b == 1:
            return True
        return False
    
    @property
    def is_grey(self):
        if self.r == self.g == self.b: 
            return True
        return False
        
    is_gray = is_grey
    
    @property
    def is_transparent(self):
        if self.a == 0:
            return True
        return False

    @property
    def hex(self):
        r, g, b = [int(n * 255) for n in (self.r, self.g, self.b)]
        s = "#%2x%2x%2x" % (r, g, b)
        return s.replace(" ", "0")
