from fontTools.ttLib    import TTFont
from pypaint.mixins     import *
from pypaint.path       import path
from aggdraw            import *

import glob

class text(Grob, TransformMixin, ColorMixin):
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

    def __init__(self, text, x, y, font_name=None, font_file=None, **kwargs):
        TransformMixin.__init__(self)
        ColorMixin.__init__(self, **kwargs)

        self.text = text
        self.x = x
        self.y = y

        self.fonts = {}
        self.font_by_name = {}
        self.find_fonts()
        self.fontsize = 10

        if font_name and self.font_by_name.has_key(font_name):
            self.fontfile = self.font_by_name[font_name]
        elif font_file:
            self.fontfile = font_file
        else:
            raise Exception('no font!')

    @property
    def bounds(self):
        tmp_canvas = Draw('RGB', (1000, 1000))
        font = Font((0.1), self.fontfile, self.fontsize)
        W, H = tmp_canvas.textsize(self.text, font)
        return (self.x, self.y, self.x+W, self.y+H)

    @property
    def center(self):
        (x1, y1, x2, y2) = self.bounds
        x = (x1 + x2) / 2
        y = (y1 + y2) / 2
        return (x, y)

    @property
    def X(self):
        return self.x

    @property
    def Y(self):
        return self.y

    @property
    def Text(self):
        return self.text

    @property
    def font_file(self):
        return self.fontfile

    @property
    def metrics(self):
        tmp_draw = Draw("RGB", (800, 600), "white")
        font = Font('black', self.fontfile, size=self.fontsize)
        return tmp_draw.textsize(self.text, font)

    def _get_font_size(self):
        return self.fontsize
    def _set_font_size(self, value):
        self.fontsize = value

    font_size = property(_get_font_size, _set_font_size)

    def get_short_name(self, font_handle):
	name   = ""
	family = ""
	for record in font_handle['name'].names:
            if record.nameID == self.FONT_SPECIFIER_NAME_ID and not name:
                if '\000' in record.string:
                    name = unicode(record.string, 'utf-16-be').encode('utf-8')
                else:
                    name = record.string
            elif record.nameID == self.FONT_SPECIFIER_FAMILY_ID and not family:
                if '\000' in record.string:
                    family = unicode(record.string, 'utf-16-be').encode('utf-8')
                else:
                    family = record.string
            if name and family:
                break
        return name, family

    def get_family(self, font_handle):
	HIBYTE = 65280
	LOBYTE = 255
	familyID = (font_handle['OS/2'].sFamilyClass&HIBYTE)>>8
	subFamilyID = font_handle['OS/2'].sFamilyClass&LOBYTE
        familyName, subFamilies = self.FAMILY_NAMES.get(familyID, ('RESERVED', None))

	if subFamilies:
            subFamily = subFamilies.get(subFamilyID, 'RESERVED')
	else:
            subFamily = 'ANY'
            
	return (familyName, subFamily)

    def find_fonts(self):
        paths = ["/usr/share/fonts/truetype/*/*.ttf"]
        files = []

        for path in paths:
            files.append(glob.glob(path))

        for file_set in files:
            for file in file_set:
                font_handle = TTFont(file)
                short_name = self.get_short_name(font_handle)
                self.font_by_name[short_name[0]] = file
                self.fonts[file] = short_name[0]
