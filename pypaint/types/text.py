from pypaint.utils.util          import *
from pypaint.types.mixins        import *
from pypaint.types.paths         import BezierPath
from pypaint.types.paths         import PathElement
from pypaint                     import ft2
from pypaint.geometry.points     import Point_Set
from pypaint.geometry.bezier     import *
from pypaint.geometry.transform  import *
from pypaint.geometry.array      import *
from fontTools.ttLib          import TTFont
from fontTools.pens.basePen   import BasePen

import numpy
import math
import unicodedata
import os

glyph_swap = {
    " ":"space",
}

class Text(Grob, TransformMixin, ColorMixin):
    stateAttributes = ('_transform', '_transformmode', '_fillcolor', '_fontfile', '_fontsize', '_align', '_lineheight')
    
    FONT_SPECIFIER_NAME_ID   = 4
    FONT_SPECIFIER_FAMILY_ID = 1

    FAMILY_NAMES = {
	0: ("ANY",{}),
	1: ("SERIF-OLD", {
		0: "ANY",
		1: "ROUNDED-LEGIBILITY",
		2: "GARALDE",
		3: "VENETIAN",
		4: "VENETIAN-MODIFIED",
		5: "DUTCH-MODERN",
		6: "DUTCH-TRADITIONAL",
		7: "CONTEMPORARY",
		8: "CALLIGRAPHIC",
		15: "MISCELLANEOUS",
	}),
	2: ("SERIF-TRANSITIONAL", {
		0: "ANY",
		1: "DIRECT-LINE",
		2: "SCRIPT",
		15: "MISCELLANEOUS",
	}),
	3: ("SERIF", {
		0: "ANY",
		1: "ITALIAN",
		2: "SCRIPT",
		15: "MISCELLANEOUS",
	}),
	4: ("SERIF-CLARENDON",{
		0: "ANY",
		1: "CLARENDON",
		2: "MODERN",
		3: "TRADITIONAL",
		4: "NEWSPAPER",
		5: "STUB-SERIF",
		6: "MONOTYPE",
		7: "TYPEWRITER",
		15: "MISCELLANEOUS",
	}),
	5: ("SERIF-SLAB",{
		0: 'ANY',
		1: 'MONOTONE',
		2: 'HUMANIST',
		3: 'GEOMETRIC',
		4: 'SWISS',
		5: 'TYPEWRITER',
		15: 'MISCELLANEOUS',
	}),
	7: ("SERIF-FREEFORM",{
		0: 'ANY',
		1: 'MODERN',
		15: 'MISCELLANEOUS',
	}),
	8: ("SANS",{
		0: 'ANY',
		1: 'GOTHIC-NEO-GROTESQUE-IBM',
		2: 'HUMANIST',
		3: 'ROUND-GEOMETRIC-LOW-X',
		4: 'ROUND-GEOMETRIC-HIGH-X',
		5: 'GOTHIC-NEO-GROTESQUE',
		6: 'GOTHIC-NEO-GROTESQUE-MODIFIED',
		9: 'GOTHIC-TYPEWRITER',
		10: 'MATRIX',
		15: 'MISCELLANEOUS',
	}),
	9: ("ORNAMENTAL",{
		0: 'ANY',
		1: 'ENGRAVER',
		2: 'BLACK-LETTER',
		3: 'DECORATIVE',
		4: 'THREE-DIMENSIONAL',
		15: 'MISCELLANEOUS',
	}),
	10:("SCRIPT",{
		0: 'ANY',
		1: 'UNCIAL',
		2: 'BRUSH-JOINED',
		3: 'FORMAL-JOINED',
		4: 'MONOTONE-JOINED',
		5: 'CALLIGRAPHIC',
		6: 'BRUSH-UNJOINED',
		7: 'FORMAL-UNJOINED',
		8: 'MONOTONE-UNJOINED',
		15: 'MISCELLANEOUS',
	}),
	12:("SYMBOL",{
		0: 'ANY',
		3: 'MIXED-SERIF',
		6: 'OLDSTYLE-SERIF',
		7: 'NEO-GROTESQUE-SANS',
		15: 'MISCELLANEOUS',
                }),
        }

    WEIGHT_NAMES = {
        'thin':100,
	'extralight':200,
	'ultralight':200,
	'light':300,
	'normal':400,
	'regular':400,
	'plain':400,
	'medium':500,
	'semibold':600,
	'demibold':600,
	'bold':700,
	'extrabold':800,
	'ultrabold':800,
	'black':900,
	'heavy':900,
        }

    WEIGHT_NUMBERS = {}

    def __init__(self, context, text, x=0, y=0, path=None, **kwargs):
        self._ctx = context

        if context:
            copy_attrs(self._ctx, self, self.stateAttributes)

        self.font_handle = TTFont(self._fontfile)        

        self.x = x
        self.y = y

        self.text        = unicode(text)
        self.path        = path
        self.resolution  = 72
        self.width       = 0
        self.height      = 0
        self.text_xmin   = 0
        self.text_ymin   = 0
        self.text_xmax   = 0
        self.text_ymax   = 0
        self.posX        = 0
        self.posY        = 0
        self.kerning     = 0
        self.scale       = float(self._fontsize)/float(self.char_height)



        self.encoding    = None
        self.current_pt  = (0, 0)
        self.t_scale     = Scale(self.scale, self.scale)
        self.offset      = 0
        self.metrics     = {}

        ## cx, cy should be the center point
        fx, fy = (-self.scale, self.scale)
        C = math.cos(math.pi)
        S = math.sin(math.pi)
        
        self.aux_transform = Transform(fx*C, fx*S, -S*fy, C*fy, self.x, self.y)
        
        for key, value in self.WEIGHT_NAMES.items():
            self.WEIGHT_NUMBERS.setdefault(value,[]).append(key)
            
        if self.encoding is None:
            self.table = self.font_handle['cmap'].tables
            self.encoding = (self.table[0].platformID, self.table[0].platEncID)

        self.table = self.font_handle['cmap'].getcmap(*self.encoding)

        for glyph in self.text:
            glyfName = self.table.cmap.get(ord(glyph))
            self.width += self.glyph_width(glyfName)

        self.height = self.char_height * self.scale

        print "metrics: w:%f h:%f" % (self.width, self.height)
        #print "scale: %f" % (self.scale)
        ## self.vorg = self.font_handle['VORG']
        #print self.table.__dict__

        
    def _get_abs_bounds(self):
        return (self.x, self.y, self.width + self.x, self.height + self.y)
    abs_bounds = property(_get_abs_bounds)

    def _get_bounds(self):
        return (self.width, self.height)
    bounds = property(_get_bounds)

    def _get_center(self):
        (x1, y1, x2, y2) = self.abs_bounds
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
    get_transform = property(_get_transform)
    

    def _get_ascent(self):
        return self.font_handle['OS/2'].sTypoAscender
    ascent = property(_get_ascent)

    def _get_descent(self):
        return self.font_handle['OS/2'].sTypoDescender
    descent = property(_get_descent)

    def _get_line_height(self):
        return self.char_height + self.font_handle['OS/2'].sTypoLineGap
    line_height = property(_get_line_height)

    def _get_char_height(self):
	if self.descent > 0:
            descent = -self.descent
        else:
            descent = self.descent
	return self.ascent - descent
    char_height = property(_get_char_height)
    
    def _get_short_name(self):
        """Get the short name from the font's names table"""
	name   = ""
	family = ""
	for record in self.font_handle['name'].names:
            if record.nameID == FONT_SPECIFIER_NAME_ID and not name:
                if '\000' in record.string:
                    name = unicode(record.string, 'utf-16-be').encode('utf-8')
                else:
                    name = record.string
            elif record.nameID == FONT_SPECIFIER_FAMILY_ID and not family:
                if '\000' in record.string:
                    family = unicode(record.string, 'utf-16-be').encode('utf-8')
                else:
                    family = record.string
            if name and family:
                break

        return name, family
    short_name = property(_get_short_name)
    
    def _get_family(self):
	"""Get the family (and sub-family) for a font"""
	HIBYTE = 65280
	LOBYTE = 255
	familyID = (self.font_handle['OS/2'].sFamilyClass&HIBYTE)>>8
	subFamilyID = self.font_handle['OS/2'].sFamilyClass&LOBYTE
        familyName, subFamilies = self.FAMILY_NAMES.get(familyID, ('RESERVED', None))

	if subFamilies:
            subFamily = subFamilies.get(subFamilyID, 'RESERVED')
	else:
            subFamily = 'ANY'

	return (familyName, subFamily)
    family = property(_get_family)
    
    def _get_weight(self):
        return self.font_handle['OS/2'].usWeightClass
    weight = property(_get_weight)

    def _get_italic(self):
        return (self.font_handle['OS/2'].fsSelection &1 or self.font_handle['head'].macStyle&2)
    italic = property(_get_italic)

    def decomposeQuad(self, points):
        n = len(points) - 1
	assert n > 0
	quadSegments = []
	for i in range(n - 1):
            x, y = points[i]
            nx, ny = points[i+1]
            impliedPt = (0.5 * (x + nx), 0.5 * (y + ny))
            quadSegments.append((points[i], impliedPt))

	quadSegments.append((points[-2], points[-1]))
	return quadSegments

    def _q_curveTo(self, *points):
        n = len(points) - 1

        if points[-1] is None:
            x, y   = points[-2]  ## last off-curve point
            nx, ny = points[0]   ## first off-curve point

            impliedStartPoint = (0.5 * (x + nx), 0.5 * (y + ny))
            impliedStartPoint = self.aux_transform.transformPoint(impliedStartPoint)
            self.currentPoint = impliedStartPoint
            self.path.moveto(impliedStartPoint)

            points = points[:-1] + (impliedStartPoint,)

        if n > 0:
            for pt1, pt2 in self.decomposeQuad(points):
                #self.path.moveto()
                pt0 = self.aux_transform.transformPoint(pt1)
                pt1 = self.aux_transform.transformPoint(pt2)
                self.path.curve3to(pt0[0], pt0[1], pt1[0], pt1[1])
                self.current_pt = (pt1[0], pt1[1])
        else: 
            (X, Y) = self.aux_transform.transformPoint((points[0][0], points[0][1]))
            self.path.lineto(X, Y)
            self.current_pt = (pt2[0], pt2[1])

    def glyph_width(self, glyph_name):
        try:
            return self.font_handle['hmtx'].metrics[glyph_name][0]*self.scale
	except KeyError:
            raise ValueError( """Couldn't find glyph for glyphName %r""" % (glyphName))

    def has_glyph(self, glyph_name, encoding=None):
	""" Check to see if font appears to have explicit glyph for char """
        cmap = self.font_handle['cmap']
	if encoding is None:
            table = self.font_handle['cmap'].tables
            encoding = (table.platformID, table.platEncID)

	table    = cmap.getcmap(*encoding)
	glyfName = table.cmap.get(ord(char))

	if glyfName is None:
            return False
        else:
            return True

    def kerning(self):
        kern = 0
        if idx+1 < len(self.text):
            L = self.text[idx]
            R = self.text[idx+1]

            left  = glyph_set._ttFont.getGlyphName(ord(L))
            right = glyph_set._ttFont.getGlyphName(ord(R))
            
            try:
                kern = glyph_set._ttFont['kern'].kernTables[0].__dict__['kernTable'][(L, R)]
            except:
                pass
        #c_width = 
        #if not self.metrics.has_key(letter):
        #    self.metrics[letter] = {}

        #self.metrics[letter].update(glyph_set._ttFont.tables['OS/2'].__dict__)
        #self.metrics[letter].update(glyph_set._ttFont.tables['maxp'].__dict__)
        #self.metrics[letter].update(glyph_set._ttFont.tables['hhea'].__dict__)
        #self.metrics[letter].update(glyph_set._ttFont.tables['head'].__dict__)
    
    def decomposeOutline(self, glyph, letter, glyph_set, halign='center'):
        hmtx = glyph_set._ttFont['hmtx']
        width_, lsb = hmtx[letter]
        rsb = width_ - lsb - (glyph.xMax - glyph.xMin)
        extent = lsb + (glyph.xMax - glyph.xMin)
        coordinates, end_points, flags = glyph.getCoordinates(self.glyph_table)
        
        offsetx_ = 0
        idx = self.text.index(letter)
        if idx+1 < len(self.text):
            _letter = self.text[idx+1]
            _glyph  = self.glyph_table[_letter]

            next_width = ((hmtx[_letter][0] + hmtx[_letter][1]) * self.scale)*0.5
            _offsetx = (glyph.xMin + next_width)

        if halign=='center':
            offsetx = (glyph.xMin + width_)
        elif halign=='right': 
            offsetx = glyph.xMin + width_
        else: 
            offsetx = glyph.xMin

        offsetx = (offsetx + offsetx_) * self.scale


        
        idx = self.text.index(letter)
        if idx+1 < len(self.text):
            n_width = hmtx[self.text[idx+1]]
        
        self.aux_transform *= Transform(dx=offsetx)

        if not coordinates.any():
            return
        
        ## in the rare case that it doesnt have an xMin
        if hasattr(glyph, "xMin"):
            #offset = (lsb_*self.scale - glyph.xMin*self.scale)
            offset = 0
        else:
            offset = 0

        start = 0
        for end in end_points:
            end = end + 1
            contour = coordinates[start:end].tolist()
            contour_flags = flags[start:end].tolist()
            start = end
            
            if 1 not in contour_flags:
                contour.append(None)
                self._q_curveTo(*contour)
            else:
                f_on_curve = contour_flags.index(1) + 1
                contour    = contour[f_on_curve:] + contour[:f_on_curve]
                contour_flags = contour_flags[f_on_curve:] + contour_flags[:f_on_curve]
                
                (X, Y) = self.aux_transform.transformPoint(contour[-1])
                self.path.moveto(X, Y)
                self.current_pt=(X, Y)

                while contour:
                    n_on_curve = contour_flags.index(1) + 1
                    if n_on_curve == 1:
                        (X, Y) = self.aux_transform.transformPoint(contour[0])
                        self.path.lineto(X, Y)
                        self.current_pt=(X, Y)
                    else:
                        self._q_curveTo(*contour[:n_on_curve])

                    contour        = contour[n_on_curve:]
                    contour_flags  = contour_flags[n_on_curve:]
                
            self.path.closepath()

        self.aux_transform *= Transform(dx=(rsb*self.scale))

    def sentence(self):
        for letter in self.text:
            rendered = self.draw(letter)


    def draw(self, letter):
        glyph_set   = self.font_handle.getGlyphSet()
        self.glyph_table = glyph_set._ttFont['glyf']
        #self.metrics[letter] = self.font_handle['hmtx'].metrics[letter]
        glyph = self.glyph_table[letter]
        self.decomposeOutline(glyph, letter, glyph_set)
