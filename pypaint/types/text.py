from pypaint.utils.util   import *
from pypaint.types.mixins import *
from pypaint import ft2

class glyph(object):
    def __init__(self, **kwargs):
        self.__dict__['attributes'] = {}

        if kwargs:
            for key, value in kwargs.items():
                self.__dict__['attributes'][key] = value
        
    def __getattr__(self, attr):
        if self.__dict__['attributes'].has_key(attr):
            return self.__dict__['attributes'][attr]

    def __setattr__(self, attr, value):
        ## self.attributes[attr] = value
        self.__dict__['attributes'][attr] = value

    def __repr__(self):
        return "<%s:%s>" %  (type(self).__name__, self.attributes)

class Text(Grob, TransformMixin, ColorMixin):
    stateAttributes = ('_transform', '_transformmode', '_fillcolor', '_fontfile', '_fontsize', '_align', '_lineheight')
    
    def __init__(self, ctx, text, x=0, y=0, width=None, height=None,  **kwargs):
        self._ctx = ctx

        if ctx:
            copy_attrs(self._ctx, self, self.stateAttributes)
            
        self.text = unicode(text)
        self.x = x
        self.y = y
        self.width = width
        self.height = height

        self.font_lib = ft2.Library()

        
        f = open(self._fontfile)
        self._font_face = ft2.Face(self.font_lib, f, 0)
        self._metrics = self._font_face.getMetrics()
        # "(x_ppem, y_ppem, x_scale, y_scale, ascender, descender, height, "
        # "max_advance) as stored in FT_Face->size->metrics."
            #self._glyph = ft2.Glyph(self._font_face, thisIndex, 0)

        last_idx = 0

        self._glyph_data = []

        self.resolution = 72
        self.text_xmin = 0
        self.text_ymin = 0
        self.text_xmax = 0
        self.text_ymax = 0

        self.posX = 0
        self.posY = 0

        for index in range(self._font_face.num_charmaps):
            cm = ft2.CharMap(self._font_face, index)
            if cm.encoding_as_string == "unic":
                self._font_face.setCharMap(cm)
                break

        self._font_face.setCharSize(self._fontsize*64, self._fontsize*64, self.resolution, self.resolution)
        enc = self._font_face.encodingVector()
        
        for k in self.text:
            idx = enc[ord(k)]
            glyph = ft2.Glyph(self._font_face, idx, 0)

            kerning = self._font_face.getKerning(last_idx, idx, 0)
            self.posX += kerning[0] << 10
            self.posY += kerning[1] << 10

            self._glyph_data.append((glyph, self.posX, self.posY))

            self.posX += glyph.advance[0]
            self.posY += glyph.advance[1]

            last_idx = idx

            (gl_xmin, gl_ymin, gl_xmax, gl_ymax) = glyph.getCBox(ft2.ft_glyph_bbox_subpixels)
            gl_xmin += self.posX >> 10
            gl_ymin += self.posY >> 10 
            gl_xmax += self.posX >> 10
            gl_ymax += self.posY >> 10

            self.text_xmin = min(self.text_xmin, gl_xmin)
            self.text_ymin = min(self.text_ymin, gl_ymin)
            self.text_xmax = max(self.text_xmax, gl_xmax)
            self.text_ymax = max(self.text_ymax, gl_ymax)
            
        self.metrics_width  = (self.text_xmax - self.text_xmin) >> 6
        self.metrics_height = (self.text_ymax - self.text_ymin) >> 6




    def _get_glyph_data(self):
        return self._glyph_data

    glyph_data = property(_get_glyph_data)

    def _get_abs_bounds(self):
        return (self.text_xmin + self.x, self.text_ymin + self.y, self.text_xmax + self.x, self.text_ymax + self.y)

    abs_bounds = property(_get_abs_bounds)

    def _get_bounds(self):
        return (self.text_xmin, self.text_ymin, self.text_xmax, self.text_ymax)

    bounds = property(_get_bounds)

    def _get_center(self):
        '''Returns the center point of the path, disregarding transforms.
        '''
        (x1, y1, x2, y2) = self.bounds
        x = (x1 + x2) / 2
        y = (y1 + y2) / 2
        return (x, y)

    center = property(_get_center)

    ### Drawing methods ###
    def _get_transform(self):
        trans = self._transform.copy()
        if (self._transformmode == CENTER):
            (x, y, w, h) = self.bounds
            deltax = x+w/2
            deltay = y+h/2

            t = Transform()
            t.translate(-deltax, -deltay)
            trans.prepend(t)

            t = Transform()
            t.translate(deltax, deltay)
            trans.append(t)

        return trans

    transform = property(_get_transform)
    
    def _get_metrics(self):
        return (self.metrics_width, self.metrics_height)
    metrics = property(_get_metrics)

    def _get_baseline(self):
        print self._metrics[5]
        return (0)
    baseline = property(_get_baseline)
