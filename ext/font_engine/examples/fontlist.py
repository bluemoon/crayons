""" list informations about all fonts found in the directory
    specified on the command line
"""

import sys, os
import ft2

def usage():
    print """list information about all font files found in a direcotry 

             usage: python fontlist.py <directory>

          """

if len(sys.argv) < 2:
    usage()
    sys.exit()

lib = ft2.Library()

dirname = sys.argv[1]
if dirname[-1] != '/':
    dirname += '/'

files = os.listdir(sys.argv[1])
for fname in files:
    try:
         f = open(dirname + fname)
         face = ft2.Face(lib, f, 0)
    except:
         sys.stderr.write("error opening file %s\n" % (dirname + fname))
         continue
    print fname, face.getPostscriptName(), "bold:",
    if face.style_flags & ft2.FT_STYLE_FLAG_BOLD:
        print "yes",
    else:
        print "no ",
    if face.style_flags & ft2.FT_STYLE_FLAG_ITALIC:
        print "italic: yes",
    else:
        print "italic: no ",
    if face.face_flags & ft2.FT_FACE_FLAG_SCALABLE:
        print "scalable: yes"
    else:
        print "scalable: no "
    print face.family_name, "--", face.style_name