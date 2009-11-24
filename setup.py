import os, sys
import nose

from distutils.core import setup
from distutils.extension import Extension

Geometry    = Extension("pypaint.cGeometry",     sources = ["ext/geometry/_geometry.c"])
Pathmatics  = Extension("pypaint.cPathmatics",   sources = ["ext/pathmatics/path.c"])
Supershape  = Extension("pypaint.cSuperformula", sources = ["ext/supershape/superformula.c"])
FontEngine  = Extension("pypaint.ft2",           sources = ["ext/font_engine/ft2module.c"], libraries=["freetype"], library_dirs=["/usr/local/lib"], include_dirs=["/usr/local/include/freetype2/", "/usr/include/freetype2/"])

setup( 
    name = "pypaint",
    version = "0.0.1a",
    author = "Alex Toney",
    
    packages=[
        'pypaint',
        'pypaint.utils',
        'pypaint.types',
        'pypaint.geometry',
        'pypaint.interfaces', 
        'pypaint.interfaces.PIL',
        'pypaint.library', 
        ],

    ext_modules=[Geometry, Pathmatics, Supershape, FontEngine],
)

#import nose
### configure paths, etc here
#nose.run()
### do other stuff here
