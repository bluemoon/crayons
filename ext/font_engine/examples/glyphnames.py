""" the names of all glyphs found in the face object
"""

import sys, os
import ft2

def usage():
    print """list glyph names found in a font

             usage: python glyphnames.py <font file>

          """

if len(sys.argv) < 2:
    usage()
    sys.exit()

lib = ft2.Library()

try:
    face = ft2.Face(lib, sys.argv[1], 0)
except ft2.error, (errtext):
    print "can't open font file %s. reason: %s" % (sys.argv[1], errtext)
    sys.exit()

for index in range(face.num_charmaps):
    charmap = ft2.CharMap(face, index)
    print "charmap encoding: ", charmap.encoding_as_string
    print "platform id: %i encoding id: %i" % (charmap.platform_id, 
                                               charmap.encoding_id)
    face.setCharMap(charmap)
    d = face.encodingVector()
    
    klist = d.keys()
    klist.sort()
    
    for k in klist:
        print "%5i %5i %s" % (k, d[k], face.getGlyphName(d[k]))
    
    print