import os
from pypaint.library.color_data  import *
from pypaint.types.color         import Color

def rgb(r, g, b, a=None, range=1.0, name=""):
    return ColorPalette((r, g, b, a))



_range = range

class ColorPalette(Color):
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
        for i in _range(len(wheel)-1):
            x0, y0 = wheel[i]    
            x1, y1 = wheel[i+1]
            if y1 < y0:
                y1 += 360
            if x0 <= a <= x1:
                h = 1.0 * y0 + (y1-y0) * (a-x0) / (x1-x0)
                break
    
        h = h % 360
        return Color(h/360, self.s, self.brightness, self.a, mode="hsb", name="")
    
    rotate = rotate_ryb
    complement = property(rotate_ryb)
    
    def invert(self):
        return rgb(1-self.r, 1-self.g, 1-self.b)
        
    inverse = property(invert)
    
    def analog(self, angle=20, d=0.5):
        clr = self.rotate_ryb(angle * (random()*2-1))
        clr.brightness += d * (random()*2-1)
        clr.saturation += d * (random()*2-1)
        return clr
        
    def nearest_hue(self, primary=False):
    
        """ Returns the name of the nearest named hue.
    
        For example,
        if you supply an indigo color (a color between blue and violet),
        the return value is "violet". If primary is set  to True,
        the return value is "purple".
    
        Primary colors leave out the fuzzy lime, teal, 
        cyan, azure and violet hues.
    
        """
     
        if self.is_black: return "black"
        if self.is_white: return "white"
        if self.is_grey : return "grey"
    
        if primary:
            hues = primary_hues
        else:
            hues = named_hues.keys()
        nearest, d = "", 1.0
        for hue in hues:
            if abs(self.hue-named_hues[hue])%1 < d:
                nearest, d = hue, abs(self.hue-named_hues[hue])%1
    
        return nearest
    
    def blend(self, clr, factor=0.5):
        
        """ Returns a mix of two colors.
        """
        
        r = self.r*(1-factor) + clr.r*factor
        g = self.g*(1-factor) + clr.g*factor
        b = self.b*(1-factor) + clr.b*factor
        a = self.a*(1-factor) + clr.a*factor
        return Color(r, g, b, a, mode="rgb")
    
    def distance(self, clr):
        
        """ Returns the Euclidean distance between two colors (0.0-1.0).
        
        Consider colors arranged on the color wheel:
        - hue is the angle of a color along the center
        - saturation is the distance of a color from the center
        - brightness is the elevation of a color from the center
          (i.e. we're on color a sphere)
        
        """
        
        coord = lambda a, d: (cos(radians(a))*d, sin(radians(a))*d)
        x0, y0 = coord(self.h*360, self.s)
        x1, y1 = coord(clr.h*360, clr.s)
        z0 = self.brightness
        z1 = clr.brightness
        d = sqrt((x1-x0)**2 + (y1-y0)**2 + (z1-z0)**2)
        return d
    
    def swatch(self, x, y, w=35, h=35, roundness=0):
    
        """ Rectangle swatch for this color.
        """
        
        _ctx.fill(self)
        _ctx.rect(x, y, w, h, roundness)

    draw = swatch

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

    def _radial_gradient_step(colors, i, n):
        l = len(colors)-1
        a = int(1.0*i/n*l)
        a = min(a+0, l)
        b = min(a+1, l)
        base = 1.0 * n/l * a
        d = (i-base) / (n/l)
        R = colors[a].r*(1-d) + colors[b].r*d
        G = colors[a].g*(1-d) + colors[b].g*d
        B = colors[a].b*(1-d) + colors[b].b*d
        return (R, G, B)

    def radial_gradient(colors, x, y, radius, steps=300):
        """ Radial gradient using the given list of colors. """
        for i in range(steps):
            ctx.fill(self._radial_gradient_step(colors, i, steps))
            ctx.oval(x+i, y+i, radius-i*2, radius-i*2)  
 

### COLOR ############################################################################################
# color(hex)
# color(r, g, b)
# color(c, m, y, k, mode="cmyk", range=1.0)
# color(h, s, b, a, mode="hsb", range=1.0)
# color(l, a, b, mode="lab")
def color(*args, **kwargs):
    return Color(*args, **kwargs)

_list = [].__class__
### COLOR LIST #######################################################################################
class ColorList(_list):
    def __init__(self, *args, **kwargs):

        """ Constructs a list of colors.
        
        Colors can be supplied as individual arguments,
        or in a list or tuple:
        ColorList(clr1, clr2)
        ColorList([clr1, clr2])
        ColorList((clr1, clr2))
        
        You can also supply an object from inside a
        web.kuler.search() or web.colr.search() list.
        
        Or a string with a named color, a descriptive feel,
        or the pathname of an image.
        
        ColorList furthermore takes two named parameters,
        a name and a list of tags.
        
        """
        
        _list.__init__(self)

        self.name = ""
        self.tags = []
        for arg in args:
            
            # From a Color object.

            self.append(color(arg.r, arg.g, arg.b, mode="rgb"))
                
            # From a Web.KulerTheme or Web.ColrTheme object.
            try:
                self.name = arg.label
                for r, g, b in arg:
                    self.append(color(r, g, b, mode="rgb"))
            except:
                pass
            
            # From a list or tuple of Color objects.
            if isinstance(arg, _list) \
            or isinstance(arg, tuple):
                for clr in arg:
                    if clr.__class__ == Color:
                        self.append(clr)
                    if clr.__class__ == BaseColor:
                        self.append(color(clr))

            # From a string (image/name/context).
            if isinstance(arg, (str, unicode)):
                if os.path.exists(arg):
                    n = 10
                    if "n" in kwargs.keys(): n = kwargs["n"]
                    self.image_to_rgb(arg, n)
                else:
                    clr = Color(arg)
                    if not clr.is_transparent:
                        self.append(clr)
                        self.name = arg
                    else:
                        self.extend(self.context_to_rgb(arg))
                        self.tags = arg
                        
        if "name" in kwargs.keys():
            self.name = kwargs["name"]
        if "tags" in kwargs.keys():
            self.tags = kwargs["tags"]

    def image_to_rgb(self, path, n=10):
    
        """ Returns a list of colors based on pixel values in the image.
        
        The Core Image library must be present to determine pixel colors.
        F. Albers: http://nodebox.net/code/index.php/shared_2007-06-11-11-37-05
        
        """

        try:
            coreimage = _ctx.ximport("coreimage")
            w, h = _ctx.imagesize(path)
            img = coreimage.canvas(w,h).layer(path)
            p = img.pixels()
            f = lambda p: p.get_pixel(int(p.w*random()), int(p.h*random()))
        except:
            # Systems that do not have Core Image might have PIL.
            try:
                from PIL import Image
                img = Image.open(path)
                p = img.getdata()
                f = lambda p: choice(p)
            except:
                raise NoCoreImageOrPIL

        for i in _range(n):
            rgba = f(p)
            if isinstance(rgba, BaseColor):
                # Newer Core Image versions will return a color object.
                clr = color(rgba)
            else:
                # Older versions and PIL return lists or arrays.
                rgba = list(rgba)
                if len(rgba) == 3: 
                    rgba.append(255)
                r, g, b, a = [v/255.0 for v in rgba]
                clr = color(r, g, b, a, mode="rgb")
            self.append(clr)

    def context_to_rgb(self, str):
    
        """ Returns the colors that have the given word in their context.
        
        For example, the word "anger" appears 
        in black, orange and red contexts,
        so the list will contain those three colors.
        
        """
    
        matches = []
        for clr in context:
            tags = context[clr]
            for tag in tags:
                if tag.startswith(str) \
                or str.startswith(tag):
                    matches.append(clr)
                    break
        
        matches = [color(name) for name in matches]
        return matches

    @property
    def context(self):
    
        """ Returns the intersection of each color's context.
    
        Get the nearest named hue of each color,
        and finds overlapping tags in each hue's colors.
        For example, a list containing yellow, deeppink and olive
        yields: femininity, friendship, happiness, joy.
    
        """
    
        tags1 = None
        for clr in self:
            overlap = []
            if   clr.is_black: name = "black"
            elif clr.is_white: name = "white"
            elif clr.is_grey : name = "grey"
            else:
                name = clr.nearest_hue(primary=True)
            if name == "orange" and clr.brightness < 0.6:
                name = "brown"
            tags2 = context[name]
            if tags1 == None:
                tags1 = tags2
            else:
                for tag in tags2:
                    if tag in tags1:
                        if tag not in overlap:
                            overlap.append(tag)
                tags1 = overlap
    
        overlap.sort()
        return overlap
    
    def copy(self):
        
        """ Returns a deep copy of the list.
        """
        
        return ColorList(
            [color(clr.r, clr.g, clr.b, clr.a, mode="rgb") for clr in self],
            name = self.name,
            tags = self.tags
        )

    @property
    def darkest(self):

        """ Returns the darkest color from the list.
    
        Knowing the contrast between a light and a dark swatch
        can help us decide how to display readable typography.
    
        """
    
        min, n = (1.0, 1.0, 1.0), 3.0
        for clr in self:
            if clr.r + clr.g + clr.b < n:
                min, n = clr, clr.r + clr.g + clr.b
    
        return min

    @property        
    def lightest(self):
        
        """ Returns the lightest color from the list.
        """
    
        max, n = (0.0, 0.0, 0.0), 0.0
        for clr in self:
            if clr.r + clr.g + clr.b > n:
                max, n = clr, clr.r + clr.g + clr.b
    
        return max

    @property    
    def average(self):
    
        """ Returns one average color for the colors in the list.
        """ 
    
        r, g, b, a = 0, 0, 0, 0
        for clr in self:
            r += clr.r
            g += clr.g
            b += clr.b
            a += clr.alpha
    
        r /= len(self)
        g /= len(self)
        b /= len(self)
        a /= len(self)

        return color(r, g, b, a, mode="rgb")
    
    def join(self): return self.average
    merge = join

    def blend(self, d=0.1):
        
        clrs = self.copy()
        for i in _range(len(clrs)):
            clrs[i] = clrs[i].blend(clrs[i-1], d)
        
        return clrs
        
    smooth = smoothen = blend

    def sort_by_distance(self, reversed=False):
        
        """ Returns a list with the smallest distance between two neighboring colors.
        The algorithm has a factorial complexity so it may run slow.
        """
        
        if len(self) == 0: return ColorList()
        
        # Find the darkest color in the list.
        root = self[0]
        for clr in self[1:]:
            if clr.brightness < root.brightness:
                root = clr
        
        # Remove the darkest color from the stack,
        # put it in the sorted list as starting element.
        stack = [clr for clr in self]
        stack.remove(root)
        sorted = [root]
        
        # Now find the color in the stack closest to that color.
        # Take this color from the stack and add it to the sorted list.
        # Now find the color closest to that color, etc.
        while len(stack) > 1:
            closest, distance = stack[0], stack[0].distance(sorted[-1])
            for clr in stack[1:]:
                d = clr.distance(sorted[-1])
                if d < distance:
                    closest, distance = clr, d
            stack.remove(closest)
            sorted.append(closest)
        sorted.append(stack[0])
        
        if reversed: _list.reverse(sorted)
        return ColorList(sorted)
    
    def _sorted_copy(self, comparison, reversed=False):
        
        """ Returns a sorted copy with the colors arranged according to the given comparison.
        """
        
        sorted = self.copy()    
        _list.sort(sorted, comparison)
        if reversed: 
            _list.reverse(sorted)
        return sorted        

    def sort_by_hue(self, reversed=False):
        return self._sorted_copy(lambda a, b: int(a.h < b.h)*2-1, reversed)     
    def sort_by_saturation(self, reversed=False):
        return self._sorted_copy(lambda a, b: int(a.s < b.s)*2-1, reversed) 
    def sort_by_brightness(self, reversed=False):
        return self._sorted_copy(lambda a, b: int(a.brightness < b.brightness)*2-1, reversed) 
    def sort_by_red(self, reversed=False):
        return self._sorted_copy(lambda a, b: int(a.r < b.r)*2-1, reversed)    
    def sort_by_green(self, reversed=False):
        return self._sorted_copy(lambda a, b: int(a.g < b.g)*2-1, reversed)  
    def sort_by_blue(self, reversed=False):
        return self._sorted_copy(lambda a, b: int(a.b < b.b)*2-1, reversed)
    def sort_by_alpha(self, reversed=False):
        return self._sorted_copy(lambda a, b: int(a.a < b.a)*2-1, reversed)  
    def sort_by_cyan(self, reversed=False):
        return self._sorted_copy(lambda a, b: int(a.c < b.c)*2-1, reversed)    
    def sort_by_magenta(self, reversed=False):
        return self._sorted_copy(lambda a, b: int(a.m < b.m)*2-1, reversed)  
    def sort_by_yellow(self, reversed=False):
        return self._sorted_copy(lambda a, b: int(a.y < b.y)*2-1, reversed)
    def sort_by_black(self, reversed=False):
        return self._sorted_copy(lambda a, b: int(a.k < b.k)*2-1, reversed)  

    def sort(self, comparison="hue", reversed=False):
        
        """ Return a copy sorted by a given color attribute.
        
        Note that there is no "universal solution to sorting a list of colors,
        since colors need to be represented in 2 or 3 dimensions.
        
        """
        
        return getattr(self, "sort_by_"+comparison)(reversed)
    
    def cluster_sort(self, cmp1="hue", cmp2="brightness", reversed=False, n=12):
        
        """ Sorts the list by cmp1, then cuts it into n pieces which are sorted by cmp2.
        
        If you want to cluster by hue, use n=12 (since there are 12 primary/secondary hues).
        The resulting list will not contain n even slices: 
        n is used rather to slice up the cmp1 property of the colors,
        e.g. cmp1=brightness and n=3 will cluster colors by brightness >= 0.66, 0.33, 0.0

        """
        
        sorted = self.sort(cmp1)
        clusters = ColorList()
        
        d = 1.0
        i = 0
        for j in _range(len(sorted)):
            if getattr(sorted[j], cmp1) < d:
                clusters.extend(sorted[i:j].sort(cmp2))
                d -= 1.0 / n
                i = j
        clusters.extend(sorted[i:].sort(cmp2))
        if reversed: _list.reverse(clusters)
        return clusters
        
    cluster = clustersort = cluster_sort
    
    def reverse(self):

        """ Returns a reversed copy of the list.
        """
        
        colors = ColorList.copy(self)
        _list.reverse(colors)
        return colors

    def repeat(self, n=2, oscillate=False, callback=None):
    
        """ Returns a list that is a repetition of the given list.
    
        When oscillate is True, 
        moves from the end back to the beginning,
        and then from the beginning to the end, and so on.
    
        """
       
        colorlist = ColorList()
        colors = ColorList.copy(self)
        for i in _range(n):
            colorlist.extend(colors)
            if oscillate: colors = colors.reverse()
            if callback : colors = callback(colors)
    
        return colorlist

    def __contains__(self, clr):
        
        """ Returns True if clr's RGB values match a color in the list.
        """
        
        for clr2 in self:
            if clr.r == clr2.r and \
               clr.g == clr2.g and \
               clr.b == clr2.b:
                return True
                break
        
        return False 
        
    def darken(self, step=0.1):
        return ColorList([clr.darken(step) for clr in self])

    darker = darken

    def lighten(self, step=0.1):
        return ColorList([clr.lighten(step) for clr in self])
    
    lighter = lighten
    
    def saturate(self, step=0.1):
        return ColorList([clr.saturate(step) for clr in self])
        
    def desaturate(self, step=0.1):
        return ColorList([clr.desaturate(step) for clr in self])
        
    def adjust_rgb(self, r=0.0, g=0.0, b=0.0, a=0.0):
        return ColorList([clr.adjust_rgb(r,g,b,a) for clr in self])

    def adjust_hsb(self, h=0.0, s=0.0, b=0.0, a=0.0): 
        return ColorList([clr.adjust_hsb(h,s,b,a) for clr in self])
        
    def adjust_contrast(self, step=0.1): 
        return ColorList([clr.adjust_contrast(step) for clr in self])

    def analog(self, angle=20, d=0.5):
        return ColorList([clr.analog(angle, d) for clr in self])

    def rotate(self, angle=180):
        return ColorList([clr.rotate(angle) for clr in self])
      
    complement = property(rotate)

    def invert(self):
        return ColorList([clr.invert() for clr in self])
        
    inverse = property(invert)

    def swatch(self, x, y, w=35, h=35, padding=0, roundness=0):
    
        """ Rectangle swatches for all the colors in the list.
        """
    
        for clr in self:
            clr.swatch(x, y, w, h, roundness)
            y += h+padding

    draw = swatch

    def swarm(self, x, y, r=100):

        """ Fancy random ovals for all the colors in the list.
        """
        
        sc = _ctx.stroke()
        sw = _ctx.strokewidth()
        
        _ctx.push()
        _ctx.transform(CORNER)
        _ctx.translate(x, y)
        for i in _range(r*3):
            clr = choice(self).copy()
            clr.alpha -= 0.5 * random()
            _ctx.fill(clr)
            clr = choice(self)
            _ctx.stroke(clr)
            _ctx.strokewidth(10 * random())
            _ctx.rotate(360 * random())
            r2 = r*0.5 * random()
            _ctx.oval(r*random(), 0, r2, r2)
        _ctx.pop()
        
        _ctx.strokewidth(sw)
        if sc == None: 
            _ctx.nostroke()
        else: 
            _ctx.stroke(sc)

    # Override some list behaviors
    # so slices return ColorList objects,
    # single Color objects can be added with +,
    # and * equals the repeat() method.

    def __getslice__(self, i, j):
        j = min(len(self), j)
        n = min(len(self), j-i)
        return colorlist([self[i+k] for k in _range(n)])
        
    def __add__(self, clr):
        if isinstance(clr, BaseColor):
            clr = [clr]
        colors = self.copy()
        colors.extend(clr)
        return colors
    
    def __iadd__(self, clr):
        return self.__add__(clr)
        
    def __mul__(self, i):
        return self.repeat(n=i)
        
    def __imul__(self, i):
        return self.__mul__(i)

# colorlist(list, name="", tags=[])
# colorlist(tuple)
# colorlist(ColorList)
# colorlist(Web.KulerTheme)
# colorlist(name)
# colorlist(context)
# colorlist(imagepath)    
def colorlist(*args, **kwargs):
    return ColorList(*args, **kwargs)
    
list = colorlist

#clrs = list("anger")
#print red() in clrs
#print clrs.darkest == black
#clrs.swatch(100,100)

#clrs = list(yellow(), deeppink(), olive())
#clrs.swarm(100,100)
#print clrs.context

#clrs = list("sea.jpg")
#image("sea.jpg", 0, 0)
#background(clrs.darkest)
#swatch(clrs.sort(), 50, 0)

#### COLOR HARMONY ###################################################################################

def complement(clr):
    
    """ Returns the color and its complement in a list.
    """
    
    clr = color(clr)
    colors = colorlist(clr)
    colors.append(clr.complement)

    return colors   

def complementary(clr):
    
    """ Returns a list of complementary colors.
    
    The complement is the color 180 degrees across
    the artistic RYB color wheel.
    The list contains darker and softer contrasting
    and complementing colors.

    """
    
    clr = color(clr)
    colors = colorlist(clr)
    
    # A contrasting color: much darker or lighter than the original.
    c = clr.copy()
    if clr.brightness > 0.4:
        c.brightness = 0.1 + c.brightness*0.25
    else:
        c.brightness = 1.0 - c.brightness*0.25
    colors.append(c)
    
    # A soft supporting color: lighter and less saturated.
    c = clr.copy()
    c.brightness = 0.3 + c.brightness
    c.saturation = 0.1 + c.saturation*0.3
    colors.append(c)
    
    # A contrasting complement: very dark or very light.
    clr = clr.complement
    c = clr.copy()
    if clr.brightness > 0.3:
        c.brightness = 0.1 + clr.brightness*0.25
    else:
        c.brightness = 1.0 - c.brightness*0.25
    colors.append(c)    
    
    # The complement and a light supporting variant.
    colors.append(clr)
    
    c = clr.copy()
    c.brightness = 0.3 + c.brightness
    c.saturation = 0.1 + c.saturation*0.25
    colors.append(c)

    return colors
    
def split_complementary(clr):
    
    """ Returns a list with the split complement of the color.
    
    The split complement are the two colors to the left and right
    of the color's complement.
    
    """
    
    clr = color(clr)
    colors = colorlist(clr)
    clr = clr.complement
    colors.append(clr.rotate_ryb(-30).lighten(0.1))
    colors.append(clr.rotate_ryb(30).lighten(0.1))

    return colors    

def left_complement(clr):
    
    """ Returns the left half of the split complement.
    
    A list is returned with the same darker and softer colors
    as in the complementary list, but using the hue of the
    left split complement instead of the complement itself.
    
    """
    
    left = split_complementary(clr)[1]
    colors = complementary(clr)
    colors[3].h = left.h
    colors[4].h = left.h
    colors[5].h = left.h
    
    colors = colorlist(
        colors[0], colors[2], colors[1], colors[3], colors[4], colors[5]
    )
    
    return colors

def right_complement(clr):
    
    """ Returns the right half of the split complement.
    """
    
    right = split_complementary(clr)[2]
    colors = complementary(clr)
    colors[3].h = right.h
    colors[4].h = right.h
    colors[5].h = right.h
    
    colors = colorlist(
        colors[0], colors[2], colors[1], colors[5], colors[4], colors[3]
    )
    
    return colors
    
def analogous(clr, angle=10, contrast=0.25):
    
    """ Returns colors that are next to each other on the wheel.
    
    These yield natural color schemes (like shades of water or sky).
    The angle determines how far the colors are apart, 
    making it bigger will introduce more variation.
    The contrast determines the darkness/lightness of
    the analogue colors in respect to the given colors.
    
    """

    contrast = max(0, min(contrast, 1.0))
    
    clr = color(clr)
    colors = colorlist(clr)
    
    for i, j in [(1,2.2), (2,1), (-1,-0.5), (-2,1)]:
        c = clr.rotate_ryb(angle*i)
        t = 0.44-j*0.1
        if clr.brightness - contrast*j < t:
            c.brightness = t
        else:
            c.brightness = clr.brightness - contrast*j
        c.saturation -= 0.05
        colors.append(c)

    return colors

def monochrome(clr):
    
    """ Returns colors in the same hue with varying brightness/saturation.
    """
    
    def _wrap(x, min, threshold, plus):
        if x - min < threshold:
            return x + plus
        else:
            return x - min
    
    colors = colorlist(clr)

    c = clr.copy()
    c.brightness = _wrap(clr.brightness, 0.5, 0.2, 0.3)
    c.saturation = _wrap(clr.saturation, 0.3, 0.1, 0.3)
    colors.append(c)

    c = clr.copy()
    c.brightness = _wrap(clr.brightness, 0.2, 0.2, 0.6)
    colors.append(c)

    c = clr.copy()
    c.brightness = max(0.2, clr.brightness+(1-clr.brightness)*0.2)
    c.saturation = _wrap(clr.saturation, 0.3, 0.1, 0.3)
    colors.append(c)

    c = clr.copy()
    c.brightness = _wrap(clr.brightness, 0.5, 0.2, 0.3)
    colors.append(c)
    
    return colors

def triad(clr, angle=120):
    
    """ Returns a triad of colors.
    
    The triad is made up of this color and two other colors
    that together make up an equilateral triangle on 
    the artistic color wheel.
    
    """
    
    clr = color(clr)
    colors = colorlist(clr)
    colors.append(clr.rotate_ryb(angle).lighten(0.1))
    colors.append(clr.rotate_ryb(-angle).lighten(0.1))

    return colors

def tetrad(clr, angle=90):
    
    """ Returns a tetrad of colors.
    
    The tetrad is made up of this color and three other colors
    that together make up a cross on the artistic color wheel.
    
    """
    
    clr = color(clr)
    colors = colorlist(clr)
    
    c = clr.rotate_ryb(angle)
    if clr.brightness < 0.5:
        c.brightness += 0.2
    else:
        c.brightness -= -0.2
    colors.append(c)

    c = clr.rotate_ryb(angle*2)
    if clr.brightness < 0.5:
        c.brightness += 0.1
    else:
        c.brightness -= -0.1
    colors.append(c)

    colors.append(clr.rotate_ryb(angle*3).lighten(0.1))

    return colors

def compound(clr, flip=False):
    
    """ Roughly the complement and some far analogs.
    """

    def _wrap(x, min, threshold, plus):
        if x - min < threshold:
            return x + plus
        else:
            return x - min

    d = 1
    if flip: d = -1
    
    clr = color(clr)
    colors = colorlist(clr)

    c = clr.rotate_ryb(30*d)
    c.brightness = _wrap(clr.brightness, 0.25, 0.6, 0.25)
    colors.append(c)

    c = clr.rotate_ryb(30*d)
    c.saturation = _wrap(clr.saturation, 0.4, 0.1, 0.4)
    c.brightness = _wrap(clr.brightness, 0.4, 0.2, 0.4)
    colors.append(c)

    c = clr.rotate_ryb(160*d)
    c.saturation = _wrap(clr.saturation, 0.25, 0.1, 0.25)
    c.brightness = max(0.2, clr.brightness)
    colors.append(c)
    
    c = clr.rotate_ryb(150*d)
    c.saturation = _wrap(clr.saturation, 0.1, 0.8, 0.1)
    c.brightness = _wrap(clr.brightness, 0.3, 0.6, 0.3)
    colors.append(c)

    c = clr.rotate_ryb(150*d)
    c.saturation = _wrap(clr.saturation, 0.1, 0.8, 0.1)
    c.brightness = _wrap(clr.brightness, 0.4, 0.2, 0.4)
    #colors.append(c)
    
    return colors

rules = [
    "complement", 
    "complementary", 
    "split complementary", 
    "left complement", 
    "right complement",
    "analogous",
    "monochrome",
    "triad",
    "tetrad",
    "compound",
    "flipped compound"
]

def rule(name, clr, angle=None, contrast=0.3, flip=False):
    
    name = name.replace(" ", "_")

    if name == "complement":
        return complement(clr)
    if name == "complementary":
        return complementary(clr)
    if name == "split_complementary":
        return split_complementary(clr)
    if name == "left_complement":
        return left_complement(clr)
    if name == "right_complement":
        return right_complement(clr)
    if name == "analogous":
        if angle == None: 
            angle = 10
        return analogous(clr, angle, contrast)
    if name == "monochrome":
        return monochrome(clr)
    if name == "triad":
        if angle == None: 
            angle = 120
        return triad(clr, angle)
    if name == "tetrad":
        if angle == None: 
            angle = 90
        return tetrad(clr, angle)
    if name == "compound":
        return compound(clr, flip)
    if name == "flipped_compound":
        return compound(clr, not flip)

## More analog colors:
#clr = rgb(0.5,0,0.3)
#c = list([clr.analog() for i in _range(10)]) + clr
#c.swarm(200,200)
#c.swatch(50,50)

#### COLOR GRADIENTS #################################################################################

class Gradient(ColorList):
    
    def __init__(self, *colors, **kwargs):
        
        """ Creates a list of gradient colors based on a few given base colors.
        
        The colors can be supplied as a list or tuple of colors,
        or simply an enumeration of color parameters.
        
        The steps named parameter defining how many colors are in the list.
        The spread named parameter controls the midpoint of the gradient
        
        """
        
        if len(colors) == 1:
            if isinstance(colors[0], _list) \
            or isinstance(colors[0], tuple):
                self._colors = _list(colors[0])
            else:
                self._colors = [colors[0]]
        else:
            self._colors = _list(colors)
        self._colors = [color(clr) for clr in self._colors]
        
        self._steps = 100
        if kwargs.has_key("steps"):
            self._steps = kwargs["steps"]
        if kwargs.has_key("steps"):
            self._steps = kwargs["steps"]
        
        self._spread = 0.5
        if kwargs.has_key("spread"):
            self._spread = kwargs["spread"]
            
        self._cache()
        
    def _get_steps(self):
        return self._steps
    def _set_steps(self, n=100):
        self._steps = n
        self._cache()
    steps = property(_get_steps, _set_steps)

    def _get_spread(self):
        return self._spread
    def _set_spread(self, d=0.5):
        self._spread = d
        self._cache()
    spread = property(_get_spread, _set_spread)

    def _interpolate(self, colors, n=100):
        """ Returns intermediary colors for given list of colors.
        """

        gradient = []
        for i in _range(n):
    
            l = len(colors)-1
            x = int(1.0*i/n*l)
            x = min(x+0, l)
            y = min(x+1, l)
        
            base = 1.0 * n/l * x
            d = (i-base) / (1.0*n/l)
            r = colors[x].r*(1-d) + colors[y].r*d
            g = colors[x].g*(1-d) + colors[y].g*d
            b = colors[x].b*(1-d) + colors[y].b*d
            a = colors[x].a*(1-d) + colors[y].a*d
        
            gradient.append(color(r, g, b, a, mode="rgb"))
        
        gradient.append(colors[-1])
        return gradient
        
    def _cache(self):
        """ Populates the list with a number of gradient colors.
    
        The list has Gradient.steps colors that interpolate between 
        the fixed base Gradient.colors.
    
        The spread parameter controls the midpoint of the gradient,
        you can shift it right and left. A separate gradient is
        calculated for each half and then glued together.
    
        """ 
        
        n = self.steps

        # Only one color in base list.
        if len(self._colors) == 1:
            ColorList.__init__(self, [self._colors[0] for i in _range(n)])
            return
        
        # Expand the base list so we can chop more accurately.
        colors = self._interpolate(self._colors, 40)

        # Chop into left half and right half.
        # Make sure their ending and beginning match colors.
        left  = colors[:len(colors)/2]
        right = colors[len(colors)/2:]
        left.append(right[0])
        right.insert(0, left[-1])
    
        # Calculate left and right gradient proportionally to spread.
        gradient = self._interpolate(left, int(n*self.spread))[:-1]
        gradient.extend(
            self._interpolate(right, n-int(n*self.spread))[1:]
        )
    
        if self.spread > 1: gradient = gradient[:n]
        if self.spread < 0: gradient = gradient[-n:]
        ColorList.__init__(self, gradient)        

# gradient([clr1, clr2], steps=100, spread=0.5)
# gradient(clr1, clr2, clr3, steps=100, spread=0.5)
def gradient(*colors, **kwargs):
    return Gradient(*colors, **kwargs)

#g = gradient(color(0,0.6,0.8), color(0.2,0,0.4), color(0.4,0,0.6), spread=0.5)
#g.spread = 0.4
#g.swatch(10, 10, h=7)    

def outline(path, colors, precision=0.4, continuous=True):

    """ Outlines each contour in a path with the colors in the list.
    
    Each contour starts with the first color in the list,
    and ends with the last color in the list.
    
    Because each line segment is drawn separately,
    works only with corner-mode transforms.
    
    """
    
    # The count of points in a given path/contour.
    def _point_count(path, precision):
        return max(int(path.length*precision*0.5), 10)
    
    # The total count of points in the path.
    n = sum([_point_count(contour, precision) for contour in path.contours])

    # For a continuous gradient,
    # we need to calculate a subrange in the list of colors
    # for each contour to draw colors from.
    contour_i = 0
    contour_n = len(path.contours)-1
    if contour_n == 0: continuous = False
    
    i = 0
    for contour in path.contours:
        
        if not continuous: i = 0
        
        # The number of points for each contour.
        j = _point_count(contour, precision)

        first = True
        for pt in contour.points(j):
            if first:
                first = False
            else:
                if not continuous:
                    # If we have a list of 100 colors and 50 points,
                    # point i maps to color i*2.
                    clr = float(i) / j * len(colors)
                else:
                    # In a continuous gradient of 100 colors,
                    # the 2nd contour in a path with 10 contours
                    # draws colors between 10-20 
                    clr = float(i) / n * len(colors)-1 * contour_i / contour_n
                _ctx.stroke(colors[int(clr)])
                _ctx.line(x0, y0, pt.x, pt.y)
            x0 = pt.x
            y0 = pt.y
            i += 1
            
        pt = contour.point(0.9999999) # Fix in pathmatics!
        _ctx.line(x0, y0, pt.x, pt.y)
        contour_i += 1
                
#g = gradient(color(0,0,1,0.5), color(0,0,0.5), color(1,0,0.5))
#g = g.repeat(oscillate=True)
#g.swatch(10, 10, h=3)

#fontsize(130)
#strokewidth(3.0)
#path = textpath("GRADIENT", 100, 200)
#outline(path, g, continuous=True)

#transform(CORNER)
#translate(200, 200)
#strokewidth(0.2)
#autoclosepath(False)
#for i in _range(100):
#    beginpath(0,0)
#    curveto(200, 200, 300*random(), 400*random(), 500, 200)
#    path = endpath(draw=False)
#    outline(path, g)

#### FAVORITE COLOR LISTS ############################################################################

class Favorites:
    
    def __getattr__(self, q):

        """ Returns the favorite colors list which name/tags matches q.
        """

        if q == None:
            return self

        candidate = None
        if _favorites.data.has_key(q):
            candidate = q
        for name, (tags, colors) in _favorites.data.iteritems():
            if q in tags:
                candidate = name
        
        if candidate:
            tags, colors = _favorites.data[candidate]
            colors = ColorList([color(r, g, b, a) for r, g, b, a in colors], name= candidate)
            colors.tags = tags.split(" ")            
            return colors
            
        return None
            
favorites = Favorites()    

### COLOR RANGE ######################################################################################

class ColorRange(ColorList):
    
    def __init__(self, h=(0.0,1.0), s=(0.0,1.0), b=(0.0,1.0), a=(1.0,1.0), 
                 grayscale=False, name="", length=100):
        
        """ A stateless list of colors whose HSB values are confined to a range.

        Hue, saturation and brightness are confined to a (min, max) tuple,
        or a list of (min, max) tuples for discontinuous ranges, or to a single value.
        This way you can describe concepts such as "light", "dark", etc.        

        With stateless we mean that you are never sure which colors are
        in the ColorRange, different colors that fall within the ranges 
        are returned each time when calling color() or colors().
        
        ColorRange has all the ColorList transformations (such as darken()),
        these return ColorList objects. It's like a snapshot of the original
        stateless ColorRange.
        
        """
        
        ColorList.__init__(self)
        
        self.name = name
        
        self.h = h
        self.s = s
        self.b = b
        self.a = a
        
        self.grayscale = grayscale
        if not grayscale:
            self.black = ColorRange((0,1), 0, 0, 1, True, name)
            self.white = ColorRange((0,1), 0, 1, 1, True, name)
            
        self.length = length
    
    def constrain_hue(self, min, max=None):
        if max == None: max = min
        self.h = (min, max)
    def constrain_saturation(self, min, max=None):
        if max == None: max = min
        self.s = (min, max)
    def constrain_brightness(self, min, max=None):
        if max == None: max = min
        self.b = (min, max)   
    def constrain_alpha(self, min, max=None):
        if max == None: max = min
        self.a = (min, max)    
    
    def copy(self, clr=None, d=0.0):
        
        """ Returns a copy of the range.
        
        Optionally, supply a color to get a range copy
        limited to the hue of that color.
        
        """
        
        cr = ColorRange()
        cr.name = self.name
        
        cr.h = deepcopy(self.h)
        cr.s = deepcopy(self.s)
        cr.b = deepcopy(self.b)
        cr.a = deepcopy(self.a)
        
        cr.grayscale = self.grayscale
        if not self.grayscale:
            cr.black = self.black.copy()
            cr.white = self.white.copy()
        
        if clr != None:
            cr.h, cr.a = clr.h+d*(random()*2-1), clr.a
        
        return cr
     
    def color(self, clr=None, d=0.035):
        
        """ Returns a color with random values in the defined h, s b, a ranges.
        
        If a color is given, use that color's hue and alpha,
        and generate its saturation and brightness from the shade.
        The hue is varied with the given d.
        
        In this way you could have a "warm" color range
        that returns all kinds of warm colors.
        When a red color is given as parameter it would generate
        all kinds of warm red colors.
        
        """
        
        # Revert to grayscale for black, white and grey hues.
        if clr != None and not isinstance(clr, Color):
            clr = color(clr)
        if clr != None and not self.grayscale:
            if clr.is_black: return self.black.color(clr, d)
            if clr.is_white: return self.white.color(clr, d)
            if clr.is_grey : return choice(
                (self.black.color(clr, d), self.white.color(clr, d))
            )
        
        h, s, b, a = self.h, self.s, self.b, self.a
        if clr != None:
            h, a = clr.h+d*(random()*2-1), clr.a
        
        hsba = []
        for v in [h, s, b, a]:
            if isinstance(v, _list):
                min, max = choice(v)
            elif isinstance(v, tuple):
                min, max = v
            else:
                min, max = v, v
            hsba.append(min + (max-min)*random())
        
        h, s, b, a = hsba
        return color(h, s, b, a, mode="hsb")
    
    def colors(self, clr=None, n=10, d=0.035):
        
        return colorlist([self.color(clr, d) for i in _range(n)])
    
    colorlist = colors
    
    def contains(self, clr):
        
        """ Returns True if the given color is part of this color range.

        Check whether each h, s, b, a component of the color
        falls within the defined range for that component.
        
        If the given color is grayscale,
        checks against the definitions for black and white.
        
        """
        
        if not isinstance(clr, Color):
            return False
        
        if not isinstance(clr, _list):
            clr = [clr]
        
        for clr in clr:
        
            if clr.is_grey and not self.grayscale:
                return (self.black.contains(clr) or \
                        self.white.contains(clr))
            
            for r, v in [(self.h, clr.h), (self.s, clr.s), (self.b, clr.brightness), (self.a, clr.a)]:
                if isinstance(r, _list):
                    pass
                elif isinstance(r, tuple):
                    r = [r]
                else:
                    r = [(r,r)]
                for min, max in r:
                    if not (min <= v <= max):
                        return False
        
        return True

    def __add__(self, colorrange):
        
        """ Combines two ColorRange objects into one.
        
        For example, if you merge a dark green range and a light red range,
        you get a range returning dark and light variations of green and red.
        
        """
        
        # You can add single colors and lists to ranges,
        # however, you'll lose the brightness and saturation info.
        # Only hues are copied and the shades in the original range are applied.
        if isinstance(colorrange, Color):
            colorrange = ColorList(colorrange)
        if isinstance(colorrange, ColorList) \
        and not isinstance(colorrange, ColorRange):
            colorrange = ColorRange([(clr.h,clr.h) for clr in colorrange], [], [])
            
        hsba = [[], [], [], []]
        for r in [self, colorrange]:
            for i in _range(4):
                v = [r.h, r.s, r.b, r.a][i]
                if isinstance(v, _list):
                    hsba[i].extend(v)
                elif isinstance(v, tuple):
                    hsba[i].append(v)
                else:
                    hsba[i].append((v, v))

        r = ColorRange(*hsba)
        return r
        
    def __iadd__(self, colorrange):
        return self.__add__(colorrange)

    # ColorRange behaves as a stateless list.
    # You can do:
    # * if clr in ColorRange() - which is the same as ColorRange().contains(clr)
    # * for clr in ColorRange()
    # * ColorRange()[i]
    # * ColorRange()[i:j]

    # ColorRange will then behave as a list 
    # of 100 random colors within the range.
    
    def __contains__(self, clr):
        return self.contains(clr)
        
    def __len__(self):
        return self.length
    
    def __getitem__(self, i):
        return self.color()
        
    def __getslice__(self, i, j):
        j = min(len(self), j)
        n = min(len(self), j-i)
        return colorlist([self.color() for i in _range(n)])
    
    def __iter__(self):
        colors = [self.color() for i in _range(len(self))]
        return iter(colors)
    
    # ColorRange behaves as a stateless function.
    
    def __call__(self, clr=None, d=0.035, n=1):
        if isinstance(clr, _list):
            return colorlist([self.color(clr, d) for clr in clr])
        elif n > 1:
            return colorlist([self.color(clr, d) for i in _range(n)])
        else:
            return self.color(clr, d)

    # ColorRange behaves as a string containing its name.
    
    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name

def colorrange(h=(0.0,1.0), s=(0.0,1.0), b=(0.0,1.0), a=(1.0,1.0), 
               grayscale=False, name="", length=100):
    return ColorRange(h, s, b, a, grayscale, name, length)
    
range = colorrange

#### COLOR SHADES ####################################################################################

# Shades are color ranges that define a combination of saturation and brightness.
# Shades are perceptonyms that map to a range of possible values.
# For example: warm-cool is a "perceptonym pair" because it describes a perceptual property.
# Cool colors look icy, cold, bright and desaturated.
# Thus, cool colors are mapped to a saturation ranging between 5-25% 
# and a brightness ranging between 90-100%.

# Light shades are bright and light.
light = ColorRange(name="light",
    s = (0.3, 0.7), 
    b = (0.9, 1.0)
)
light.black.b = (0.15, 0.30)

# Dark shades are deep and colorfully saturated.
dark = ColorRange(name="dark",
    s = (0.7, 1.0), 
    b = (0.15, 0.4)
)
dark.white.b = (0.5, 0.75)

# Bright shades are colorful and friendly.
bright = ColorRange(name="bright",
    s = (0.8, 1.0), 
    b = (0.8, 1.0)
)

# Weak shades are neither light, soft nor neutral.
weak = ColorRange(name="weak",
    s = (0.15, 0.3),
    b = (0.7, 1.0)
)
weak.black.b = 0.2

# Neutral shades are desaturated and neither bright nor dark.
neutral = ColorRange(name="neutral",
    s = (0.25, 0.35), 
    b = (0.3, 0.7)
)
neutral.white.b = (0.9, 1.0)
neutral.black.b = (0.15, 0.15)

# Fresh shades are light and friendly 
# with a higher saturation than soft shades.
fresh = ColorRange(name="fresh",
    s = (0.4, 0.8), 
    b = (0.8, 1.0)
)
fresh.white.b = (0.8, 1.0)
fresh.black.b = (0.05, 0.3)

# Soft shades produce gentle pastel colors
# with small difference in saturation.
soft = ColorRange(name="soft",
    s = (0.2, 0.3), 
    b = (0.6, 0.9)
)
soft.white.b = (0.6, 0.9)
soft.black.b = (0.05, 0.15)

# Hard shades have powerful colors 
# but lighter than intense shades.
hard = ColorRange(name="hard",
    s = (0.9, 1.0), 
    b = (0.4, 1.0)
)

# Warm shades are gently saturated and gently bright.
warm = ColorRange(name="warm",
    s = (0.6, 0.9), 
    b = (0.4, 0.9)
)
warm.white.b = (0.8, 1.0)
warm.black.b = 0.2

# Cool shades are cold, bright and desaturated.
cool = ColorRange(name="cool",
    s = (0.05, 0.2), 
    b = (0.9, 1.0)
)
cool.white.b = (0.95, 1.0)

# Intense shades have powerful deep/bright contrasts.
intense = ColorRange(name="intense",
    s = (0.9, 1.0), 
    b = [(0.2, 0.35), (0.8, 1.0)]
)

shades = [light, dark, bright, weak, neutral, fresh, soft, hard, warm, cool, intense]

def shade(name):
    
    for shade in shades:
        if shade.name == name:
            return shade

shade_opposites = {
    # XXX - not sure if all of these are correct.
    "light"   : dark,
    "dark"    : light,
    "bright"  : weak,
    "weak"    : bright,
    "neutral" : fresh,
    "fresh"   : neutral,
    "soft"    : hard,
    "hard"    : soft,
    "warm"    : cool,
    "cool"    : warm
}

def shade_opposite(shade):
    
    if str(shade) in shade_opposites:
        return shade_opposites[str(shade)]
    else:
        return None

#clr = color(choice(named_colors.keys()))
#x = 20
#y = 20
#for shade in shades:
#    fill(0)
#    fontsize(14)
#    text(str(shade), x, y-5)
#    snapshot = shade.colors(clr, 20)
#    snapshot.swatch(x, 20)
#    y = 20
#    x += 50

#print shade_opposite(bright)

#intense(olive(), n=8).swatch(50, 50)
#neutral(olive(), (n=8).swatch(100, 50)
#r = intense + neutral
#r = r(olive(), n=8).swatch(150, 49)

def guess_name(clr):
    
    """ Guesses the shade and hue name of a color.
    
    If the given color is named in the named_colors list, return that name.
    Otherwise guess its nearest hue and shade range.
    
    """
    
    clr = Color(clr)
    
    if clr.is_transparent: return "transparent"
    if clr.is_black: return "black"
    if clr.is_white: return "white"
    if clr.is_black: return "black"
    
    for name in named_colors:
        try: r,g,b = named_colors[name]
        except: continue
        if r == clr.r and g == clr.g and b == clr.b:
            return name
    
    for shade in shades:
        if clr in shade:
            return shade.name + " " + clr.nearest_hue()
            break
            
    return clr.nearest_hue()

#print guess_name(color(0.8,0,0))

#### COLOR SHADER ####################################################################################

def shader(x, y, dx, dy, radius=300, angle=0, spread=90):
    
    """ Returns a 0.0 - 1.0 brightness adjusted to a light source.
    
    The light source is positioned at dx, dy.
    The returned float is calculated for x, y position
    (e.g. an oval at x, y should have this brightness).
    
    The radius influences the strength of the light,
    angle and spread control the direction of the light.
    
    """
    
    if angle != None:
        radius *= 2
    
    # Get the distance and angle between point and light source.
    d = sqrt((dx-x)**2 + (dy-y)**2)
    a = degrees(atan2(dy-y, dx-x)) + 180
    
    # If no angle is defined, 
    # light is emitted evenly in all directions
    # and carries as far as the defined radius
    # (e.g. like a radial gradient).
    if d <= radius:
        d1 = 1.0 * d / radius
    else:
        d1 = 1.0
    if angle == None:
        return 1-d1  

    # Normalize the light's direction and spread
    # between 0 and 360.
    angle = 360-angle%360
    spread = max(0, min(spread, 360))
    if spread == 0:
        return 0.0    
    
    # Objects that fall within the spreaded direction
    # of the light are illuminated.
    d = abs(a-angle)
    if d <= spread/2:
        d2 = d / spread + d1
    else:
        d2 = 1.0
    
    # Wrapping from 0 to 360:
    # a light source with a direction of 10 degrees
    # and a spread of 45 degrees illuminates
    # objects between 0 and 35 degrees and 350 and 360 degrees.
    if 360-angle <= spread/2:
        d = abs(360-angle+a)
        if d <= spread/2:
            d2 = d / spread + d1
    # Wrapping from 360 to 0.
    if angle < spread/2:
        d = abs(360+angle-a)
        if d <= spread/2:
            d2 = d / spread + d1
    
    return 1 - max(0, min(d2, 1))
    
#size(500, 500)
#background(0.1,0,0.05)
#colormode(HSB)
#shadow()
#for i in _range(4000):
#    x = WIDTH*random()
#    y = HEIGHT*random()
#    r = 10 + 20*random()
#    d = shader(x, y, 450, 450, angle=135)
#    # HSB is brighter and opaque in the centre of the light.
#    fill(0.84+d*0.1, 1, 0.2+0.8*d, d)
#    oval(x, y, r, r)

#### COLOR AGGREGATE #################################################################################

DEFAULT_CACHE = os.path.join(os.path.dirname(__file__), "aggregated")

_aggregated_name = ""
_aggregated_dict = {}
def aggregated(cache=DEFAULT_CACHE):
    
    """ A dictionary of all aggregated words.
    
    They keys in the dictionary correspond to subfolders in the aggregated cache.
    Each key has a list of words. Each of these words is the name of an XML-file
    in the subfolder. The XML-file contains color information harvested from the web
    (or handmade).
    
    """
    
    global _aggregated_name, _aggregated_dict
    if _aggregated_name != cache:
        _aggregated_name = cache
        _aggregated_dict = {}
        for path in glob(os.path.join(cache, "*")):
            if os.path.isdir(path):
                p = os.path.basename(path)
                _aggregated_dict[p] = glob(os.path.join(path, "*"))
                _aggregated_dict[p] = [os.path.basename(f)[:-4] for f in _aggregated_dict[p]]
     
    return _aggregated_dict

class ColorThemeNotFound(Exception): pass

class ColorTheme(_list):
    
    def __init__(self, name="", ranges=[], top=5, cache=DEFAULT_CACHE, blue="blue", guess=False, length=100):

        """ A set of weighted ranges linked to colors.
        
        A ColorTheme is a set of allowed colors (e.g. red, black)
        and ranges (e.g. dark, intense) for these colors.
        These are supplied as lists of (color, range, weight) tuples.
        Ranges with a greater weight will occur more in the combined range.
        
        A ColorTheme is expected to have a name,
        so it can be stored and retrieved in the XML cache.
        
        The blue parameter denotes a color correction.
        Since most web aggregated results will yield "blue" instead of "azure" or "cyan",
        we may never see these colors (e.g. azure beach will not propagate).
        So instead of true blue we pass "dodgerblue", which will yield more all-round shades of blue.
        To ignore this, set blue="blue".
        
        """

        self.name = name
        self.ranges = []
        self.cache = cache
        self.top = top
        self.tags = []
        self.blue = blue
        self.guess = False
        self.length = 100
        
        self.group_swatches = False

        # See if we can load data from cache first.
        # Check subfolders in the cache as well.
        # If the query is in a  subfolder, adjust the cache path.
        path = os.path.join(self.cache, self.name+".xml")
        if os.path.exists(path):
            self._load(self.top, self.blue)
        else:
            a = aggregated(self.cache)
            for key in a:
                if self.name != "" and self.name in a[key]:
                    self.cache = os.path.join(self.cache, key)
                    self._load(self.top, self.blue)
                    self.tags.append(key.replace("_"," "))
                    self.group_swatches = True
                    break
            
        # Otherwise, we expect some parameters to specify the data.
        if len(ranges) > 0:
            self.ranges = ranges

        # Nothing in the cache matches the query
        # and no parameters were specified, so we're going to guess.
        # This works reasonably well for obvious things like
        # abandon -> abandoned, frail -> fragile
        if len(self.ranges) == 0 and guess:
            a = aggregated(self.cache)
            for key in a:
                m = difflib.get_close_matches(self.name, a[key], cutoff=0.8)
                if len(m) > 0:
                    self.name = m[0]
                    self.cache = os.path.join(self.cache, key)
                    self._load(top, blue)
                    self.tags.append(key.replace("_"," "))
                    self.group_swatches = True
                    self.guess = True
                    break
                    
        if self.name != "" and len(self.ranges) == 0:
            raise ColorThemeNotFound

    def add_range(self, range, clr=None, weight=1.0):
        
        # You can also supply range and color as a string,
        # e.g. "dark ivory".
        if isinstance(range, str) and clr == None:
            for word in range.split(" "):
                if word in named_hues \
                or word in named_colors:
                    clr = named_color(word)
                if shade(word) != None:
                    range = shade(word)
                    
        self.ranges.append((color(clr), range, weight))

    def copy(self):
        
        t = ColorTheme(
            name = self.name,
            ranges = [(clr.copy(), rng.copy(), wgt) for clr, rng, wgt in self],
            top = self.top,
            cache = self.cache,
            blue = self.blue,
            guess = self.guess,
            lenght = self.length
        )
        t.tags = self.tags
        t.group_swatches = self.group_swatches
        return t
        
    def _weight_by_hue(self):
        
        """ Returns a list of (hue, ranges, total weight, normalized total weight)-tuples.
        
        ColorTheme is made up out of (color, range, weight) tuples.
        For consistency with XML-output in the old Prism format
        (i.e. <color>s made up of <shade>s) we need a group
        weight per different hue.
        
        The same is true for the swatch() draw method.
        Hues are grouped as a single unit (e.g. dark red, intense red, weak red)
        after which the dimensions (rows/columns) is determined.
        
        """
        
        grouped = {}
        weights = []
        for clr, rng, weight in self.ranges:
            h = clr.nearest_hue(primary=False)
            if grouped.has_key(h):
                ranges, total_weight = grouped[h]
                ranges.append((clr, rng, weight))
                total_weight += weight
                grouped[h] = (ranges, total_weight)
            else:
                grouped[h] = ([(clr, rng, weight)], weight)

        # Calculate the normalized (0.0-1.0) weight for each hue,
        # and transform the dictionary to a list.
        s = 1.0 * sum([w for r, w in grouped.values()])
        grouped = [(grouped[h][1], grouped[h][1]/s, h, grouped[h][0]) for h in grouped]
        grouped.sort()
        grouped.reverse()

        return grouped

    @property
    def xml(self):

        """ Returns the color information as XML.
        
        The XML has the following structure:
        <colors query="">
            <color name="" weight="" />
                <rgb r="" g="" b="" />
                <shade name="" weight="" />
            </color>
        </colors>
        
        Notice that ranges are stored by name and retrieved in the _load()
        method with the shade() command - and are thus expected to be
        shades (e.g. intense, warm, ...) unless the shade() command would
        return any custom ranges as well. This can be done by appending custom
        ranges to the shades list.
        
        """

        grouped = self._weight_by_hue()
        
        xml = "<colors query=\""+self.name+"\" tags=\""+", ".join(self.tags)+"\">\n\n"
        for total_weight, normalized_weight, hue, ranges in grouped:
            if hue == self.blue: hue = "blue"
            clr = color(hue)
            xml += "\t<color name=\""+clr.name+"\" weight=\""+str(normalized_weight)+"\">\n "
            xml += "\t\t<rgb r=\""+str(clr.r)+"\" g=\""+str(clr.g)+"\" "
            xml += "b=\""+str(clr.b)+"\" a=\""+str(clr.a)+"\" />\n "
            for clr, rng, wgt in ranges:
                xml += "\t\t<shade name=\""+str(rng)+"\" weight=\""+str(wgt/total_weight)+"\" />\n "
            xml = xml.rstrip(" ") + "\t</color>\n\n"
        xml += "</colors>"
        
        return xml

    def _save(self):
        
        """ Saves the color information in the cache as XML.        
        """

        if not os.path.exists(self.cache):
            os.makedirs(self.cache)
        
        path = os.path.join(self.cache, self.name+".xml")
        f = open(path, "w")
        f.write(self.xml)
        f.close()
    
    def _load(self, top=5, blue="blue"):

        """ Loads a theme from aggregated web data.
       
        The data must be old-style Prism XML: <color>s consisting of <shade>s.
        Colors named "blue" will be overridden with the blue parameter.
        
        """
        
        path = os.path.join(self.cache, self.name+".xml")
        xml = open(path).read()
        dom = parseString(xml).documentElement
        
        attr = lambda e, a: e.attributes[a].value
        
        for e in dom.getElementsByTagName("color")[:top]:
            w = float(attr(e, "weight")) 
            try:
                rgb = e.getElementsByTagName("rgb")[0]
                clr = color(
                    float(attr(rgb, "r")),
                    float(attr(rgb, "g")),
                    float(attr(rgb, "b")),
                    float(attr(rgb, "a")),
                    mode="rgb"
                )
                try: 
                    clr.name = attr(e, "name")
                    if clr.name == "blue": clr = color(blue)
                except: 
                    pass
            except:
                name = attr(e, "name")
                if name == "blue": name = blue
                clr = color(name)
               
            for s in e.getElementsByTagName("shade"):
                self.ranges.append((
                    clr, 
                    shade(attr(s, "name")),
                    w * float(attr(s, "weight"))                
                ))
                
    def color(self, d=0.035):

        """ Returns a random color within the theme.
        
        Fetches a random range (the weight is taken into account,
        so ranges with a bigger weight have a higher chance of propagating)
        and hues it with the associated color.
        
        """

        s = sum([w for clr, rng, w in self.ranges])
        r = random()
        for clr, rng, weight in self.ranges:
            if weight/s >= r: break
            r -= weight/s
        
        return rng(clr, d)  
        
    def colors(self, n=10, d=0.035):
      
        """ Returns a number of random colors from the theme.
        """
      
        s = sum([w for clr, rng, w in self.ranges])
        colors = colorlist()
        for i in _range(n):
            r = random()
            for clr, rng, weight in self.ranges:
                if weight/s >= r: break
                r -= weight/s
            colors.append(rng(clr, d))
        
        return colors
    
    colorlist = colors

    def contains(self, clr):
        for c, rng, weight in self.ranges:
            if clr in rng: return True
        return False
    
    # You can do: if clr in aggregate.
    
    def __contains__(self, clr):
        return self.contains(clr)

    # Behaves as a list.

    def __len__(self):
        return self.length
    
    def __getitem__(self, i):
        return self.color()
        
    def __getslice__(self, i, j):
        j = min(len(self), j)
        n = min(len(self), j-i)
        return colorlist([self.color() for i in _range(n)])
    
    def __iter__(self):
        colors = [self.color() for i in _range(len(self))]
        return iter(colors)
    
    # You can do + and += operations.
    
    def __add__(self, theme):
        t = self.copy()
        t.ranges.extend(theme.ranges)
        t.tags.extend(theme.tags)
        return t
        
    def __iadd__(self, theme):
        return self.__add__(theme)
        
    # Callable as a stateless function.
    
    def __call__(self, n=1, d=0.035):
        if n > 1:
            return self.colors(n, d)
        else:
            return self.color(d)
        
    # Behaves as a string.
    
    def __str__(self):
        return self.name
    
    def __repr__(self):
        return self.name
    
    def recombine(self, other, d=0.7):
        
        """ Genetic recombination of two themes using cut and splice technique.
        """
        
        a, b = self, other
        d1  = max(0, min(d, 1))
        d2 = d1
        
        c = ColorTheme(
            name = a.name[:int(len(a.name)*d1) ] + 
                   b.name[ int(len(b.name)*d2):],
            ranges = a.ranges[:int(len(a.ranges)*d1) ] + 
                     b.ranges[ int(len(b.ranges)*d2):],
            top = a.top,
            cache = os.path.join(DEFAULT_CACHE, "recombined"),
            blue = a.blue,
            length = a.length*d1 + b.length*d2
        )
        c.tags  = a.tags[:int(len(a.tags)*d1) ] 
        c.tags += b.tags[ int(len(b.tags)*d2):]
        return c

    def swatch(self, x, y, w=35, h=35, padding=4, roundness=0, n=12, d=0.035, grouped=None):
        
        """ Draws a weighted swatch with approximately n columns and rows.
        
        When the grouped parameter is True, colors are grouped in blocks of the same hue
        (also see the _weight_by_hue() method).
        
        """
        
        if grouped == None: # should be True or False
            grouped = self.group_swatches
        
        # If we dont't need to make groups,
        # just display an individual column for each weight
        # in the (color, range, weight) tuples.
        if not grouped:
            s = sum([wgt for clr, rng, wgt in self.ranges])
            for clr, rng, wgt in self.ranges:
                cols = max(1, int(wgt/s*n))
                for i in _range(cols):
                    rng.colors(clr, n=n, d=d).swatch(x, y, w, h, padding=padding, roundness=roundness)
                    x += w+padding
            
            return x, y+n*(h+padding)
        
        # When grouped, combine hues and display them
        # in batches of rows, then moving on to the next hue.
        grouped = self._weight_by_hue()
        for total_weight, normalized_weight, hue, ranges in grouped:
            dy = y
            rc = 0
            for clr, rng, weight in ranges:
                dx = x
                cols = int(normalized_weight*n)
                cols = max(1, min(cols, n-len(grouped)))
                if clr.name == "black": rng = rng.black
                if clr.name == "white": rng = rng.white
                for i in _range(cols):
                    rows = int(weight/total_weight*n)
                    rows = max(1, rows)
                    # Each column should add up to n rows,
                    # if not due to rounding errors, add a row at the bottom.
                    if (clr, rng, weight) == ranges[-1] and rc+rows < n: rows += 1
                    rng.colors(clr, n=rows, d=d).swatch(dx, dy, w, h, padding=padding, roundness=roundness)
                    dx += w + padding
                dy += (w+padding) * rows #+ padding
                rc = rows
            x += (w+padding) * cols + padding

        return x, dy

    draw = swatch
    
    def swarm(self, x, y, r=100):
        colors = self.colors(100)
        colors.swarm(x, y, r)

def theme(name="", ranges=[], top=5, cache=DEFAULT_CACHE, blue="dodgerblue", guess=False):
    return ColorTheme(name, ranges, top, cache, blue, guess)
    
aggregate = theme

# Our own theme of ancient colors:
#t = colors.theme()
#t.name = "ancient egypt"
#t.add_range(colors.soft, colors.ivory(), 0.5)
#t.add_range(colors.dark, colors.darkgoldenrod(), 0.2)
#t.add_range(colors.intense, colors.gold(), 0.2)
#t.add_range(colors.warm, colors.brown(), 0.2)
#t.add_range(colors.neutral, colors.teal(), 0.1)
#t.add_range(colors.intense, colors.red(), 0.1)

## ancient egypt + love = ancient eve!
##t2 = colors.aggregate("love")
##t = t.recombine(t2)
##print t.name

#stroke(0)
#strokewidth(0.2)
#t.swatch(50,50,n=12, grouped=False)

#### COLORS FROM WEB #################################################################################

def search_engine(query, top=5, service="google", license=None, 
                  cache=os.path.join(DEFAULT_CACHE, "google")):
    
    """ Return a color aggregate from colors and ranges parsed from the web.
    T. De Smedt, http://nodebox.net/code/index.php/Prism
    """

    # Check if we have cached information first.
    try:
        a = theme(query, cache=cache)
        return a
    except:
        pass

    if service == "google":
        from web import google
        search_engine = google
    if service == "yahoo":
        from web import yahoo
        search_engine = yahoo
        if license: 
            yahoo.license_key = license

    # Sort all the primary hues (plus black and white) for q.
    sorted_colors = search_engine.sort(
        [h for h in primary_hues]+["black", "white"], 
        context=query, strict=True, cached=True
    )

    # Sort all the shades (bright, hard, ...) for q.
    sorted_shades = search_engine.sort(
        [str(s) for s in shades], 
        context= query, strict=True, cached=True
    )

    # Reforms '"black death"' to 'black'.
    f = lambda x: x.strip("\"").split()[0]

    # Take the top most relevant hues.
    n2 = sum([w for h, w in sorted_colors[:top]])
    sorted_colors = [(color(f(h)), w/n2) for h, w in sorted_colors[:top]]

    # Take the three most relevant shades.
    n2 = sum([w for s, w in sorted_shades[:3]])
    sorted_shades = [(shade(f(s)), w/n2) for s, w in sorted_shades[:3]]

    a = theme(cache=cache)
    a.name = query
    for clr, w1 in sorted_colors:
        for rng, w2 in sorted_shades:
            a.add_range(rng, clr, w1*w2)
    
    a._save()
    return a

def google(query, top=5, license=None, cache=os.path.join(DEFAULT_CACHE, "google")):
    return search_engine(query, top, "google", license, cache)

prism = google

def yahoo(query, top=5, license=None, cache=os.path.join(DEFAULT_CACHE, "yahoo")):
    return search_engine(query, top, "yahoo", license, cache)

#a = yahoo("love") #rust sky
#stroke(0.2)
#strokewidth(0.5)        
#a.swatch(50,50)
#a.swarm(100,550)

#stroke(0.2)
#strokewidth(0.5)
#a = yahoo("love")
#b = yahoo("rust")
#b.swatch(500,50)
#a += b # a is now a color range
#a.swatch(445,-85, h=17)
#a.swarm(400,400)

#nostroke()

def morguefile(query, n=10, top=10):

    """ Returns a list of colors drawn from a morgueFile image.
    
    With the Web library installed,
    downloads a thumbnail from morgueFile and retrieves pixel colors.
    
    """
    
    from web import morguefile
    images = morguefile.search(query)[:top]
    path = choice(images).download(thumbnail=True, wait=10)
    
    return ColorList(path, n, name=query)

#colors = morguefile("office", n=10)
#colors.swatch(20, 20)
#colors.swarm(200, 200) # bleak office...
#intense(colors).swarm(100, 200) 
#intense(colors).swarm(200, 200) # kindergarten!

#a = yahoo("love")
#x, y = a.swatch(0,0)
#b = morguefile("office")
#b.swatch(0, y)
#a += b
#a.length = 10
#a.swatch(400,0)

def colorwheel(x, y, r=250, labels=True, scope=1.0, shift=0.0):
    keys = named_hues.keys()
    def cmp(a, b):
        if named_hues[a] < named_hues[b]: return 1
        return -1

    keys.sort(cmp)

    _ctx.fill(0,0,0)
    _ctx.oval(x-r, y-r, r*2, r*2)

    for i in _range(10):
        ri = r/6 * (1-i*0.1)
        _ctx.fill(i*0.1)
        _ctx.oval(x-ri, y-ri, ri*2, ri*2)
        
    #_ctx.transform(CORNER)
    #_ctx.translate(x, y)
    #_ctx.rotate(65)
    a = 360.0/len(named_hues)
    for name in keys:
        _ctx.rotate(a)
        h = (named_hues[name]*scope+shift)%1
        for i in _range(20):
            if i < 2: continue
            x = r/40.0 * (25-i)
            #_ctx.push()
            #_ctx.rotate(2*i)
            #_ctx.translate(-0.1*i)
            _ctx.fill(color(0,0,0,0.1, mode="rgb"))
            _ctx.oval(x, 2, x*0.7, x*0.7)
            _ctx.fill(color(h, 2.1-i*0.1, i*0.1, i*0.03, mode="hsb"))
            p = _ctx.oval(x, 0, x*0.7, x*0.7)
            #_ctx.pop()
        
        if labels and scope==1 and shift==0:
            _ctx.fill(color(h, 1, 0.4, mode="hsb"))
            #_ctx.push()
            #_ctx.rotate(-14)
            #_ctx.fontsize(r/16)
            #_ctx.text(name, r*i*0.015, -r/6.5)
            #_ctx.pop()
    
    #_ctx.reset()

#colorwheel(301, 266)


if __name__ == "__main__":
    from pypaint.context import Context
    _ctx = Context(width=600, height=600)
    clrs = colorlist(color(0.0, 1.0, 0.4))
    
    swatch(clrs.sort(), 50, 0)
    #colorwheel(301, 266)
    _ctx.save('')
