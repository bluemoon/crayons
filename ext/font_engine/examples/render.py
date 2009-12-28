""" render a short text and display it on the the screen.
    This propgram requires PIL
"""

import sys, os
import ft2
try:
    import Image
except ImportError:
    print """can't import Image module. You must have PIL installed to run this program"""
    sys.exit()

def usage(err):
    if err: print err
    print """list information about all font files found in a direcotry 

             usage: python render.py [options] fontfile text
             
             options:
                --encoding <encoding name>
                    specify the encoding for the conversion of the
                    text string into unicode. default: iso-8859-1
                --size <number>
                    set the font size in point. default: 30 point
                --resolution <number>
                    set the resolution to be used for rendering (dpi)
                    default: 72 dpi
                --streamio
                    use a StreamIO object to font face
                --attach
                    filename of a file with additional font information, 
                    like a Type 1 AFM file.

          """

lib = ft2.Library()

encoding = 'iso-8859-1'
size = 12
resolution = 72
strio = 0
attach = ""

while len(sys.argv) >= 2 and sys.argv[1][0:2] == '--':
    #xxx for options
    opt = sys.argv.pop(1)
    if opt == "--encoding":
        encoding = sys.argv.pop(1)
    elif opt == "--size":
        size = int(sys.argv.pop(1))
    elif opt == "--resolution":
        resolution = int(sys.argv.pop(1))
    elif opt == "--streamio":
        strio = 1
    elif opt == "--attach":
        attach = sys.argv.pop(1)
    else:
        usage("unknown option %s" % opt)
        sys.exit()

if len(sys.argv) < 3:
    usage("not enough arguments")
    sys.exit()

fname = sys.argv[1]
f = open(fname)
if strio:
    # if we want so, we can use a StringIO object to feed the font data
    # to the ft2 module
    # Any other object providing the method read, seek and tell should
    # work too.
    import StringIO
    s = f.read()
    f.close()
    f = StringIO.StringIO(s)

face = ft2.Face(lib, f, 0)
if attach:
    f = open(attach)
    if strio:
        s = f.read()
        f.close()
        f = StringIO.StringIO(s)
    face.attach(f)

text = ' '.join(sys.argv[2:])

# try to use the unicode charmap; if that is not available, fall
# to the next available charmap, without any checking...

use_unicode = 0

for index in range(face.num_charmaps):
    cm = ft2.CharMap(face, index)
    if cm.encoding_as_string == "unic":
        use_unicode = 1
        face.setCharMap(cm)
        break

if use_unicode:
    text = unicode(text, encoding)
else:
    face.setCharMap(ft2.CharMap(face, 0, 0))
    # don't bother to do any serious charset conversion...

face.setCharSize(size*64, size*64, resolution, resolution)

enc = face.encodingVector()

# The following is mainly a "Python translation" of the example
# in the Freetype tutorial, Step 2, "Simpe text rendering: kerning
# + centering"

# get the bbox of the entire string

# glyphdata will at first contain [glyph, pen_x, pen_y] for each glyph
glyphdata = []
posx = posy = 0
lastIndex = 0
text_xmin = text_ymin = 0
text_xmax = text_ymax = 0

for c in text:
    thisIndex = enc[ord(c)]
    glyph = ft2.Glyph(face, thisIndex, 0)
    kerning = face.getKerning(lastIndex, thisIndex, 0)
    posx += kerning[0] << 10
    posy += kerning[1] << 10
    print "kern ", lastIndex, thisIndex, kerning
    glyphdata.append((glyph, posx, posy))
    posx += glyph.advance[0]
    posy += glyph.advance[1]
    lastIndex = thisIndex
    (gl_xmin, gl_ymin, gl_xmax, gl_ymax) = glyph.getCBox(ft2.ft_glyph_bbox_subpixels)
    gl_xmin += posx >> 10
    gl_ymin += posy >> 10 
    gl_xmax += posx >> 10
    gl_ymax += posy >> 10
    text_xmin = min(text_xmin, gl_xmin)
    text_ymin = min(text_ymin, gl_ymin)
    text_xmax = max(text_xmax, gl_xmax)
    text_ymax = max(text_ymax, gl_ymax)
    

width = (text_xmax - text_xmin) >> 6
height = (text_ymax - text_ymin) >> 6
# make sure that we have a minimal image height and width; xv will otherwise
# expand the image..
height = max(30, height) 
width = max(100, width)
v_offset = text_ymax >> 6
print "bbox", text_xmin, text_ymin, text_xmax, text_ymax
print "w, h", width, height

im = Image.new('L', (width, height), 255)

for glyph, posx, posy in glyphdata:
    ft2mask = ft2.Bitmap(glyph, ft2.FT_RENDER_MODE_NORMAL, posx, posy)
    if (ft2mask.width and ft2mask.rows):
        mask = Image.fromstring('L', (ft2mask.width, ft2mask.rows), ft2mask.bitmap)
        fg = Image.new('L', (ft2mask.width, ft2mask.rows), 0)
        im.paste(fg, ((posx >> 16) + ft2mask.left, v_offset - ft2mask.top), mask)
        print "px, py, top, left", posx >> 16, posy >> 16, ft2mask.left, ft2mask.top
im.show()

