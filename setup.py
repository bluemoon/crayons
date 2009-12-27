import os, sys
import nose

from setuptools import setup, find_packages
from distutils.extension import Extension

FREETYPE = False
FFTW     = False

FREETYPE_ROOT = "/usr"
AGG_EXT = "ext/aggdraw/"

agg_defines      = []
agg_include_dirs = [AGG_EXT+"agg2/include"]
agg_library_dirs = []
agg_libraries    = []

agg_sources = [
    AGG_EXT+"agg2/src/agg_arc.cpp",
    AGG_EXT+"agg2/src/agg_bezier_arc.cpp",
    AGG_EXT+"agg2/src/agg_curves.cpp",
    AGG_EXT+"agg2/src/agg_path_storage.cpp",
    AGG_EXT+"agg2/src/agg_rasterizer_scanline_aa.cpp",
    AGG_EXT+"agg2/src/agg_trans_affine.cpp",
    AGG_EXT+"agg2/src/agg_vcgen_contour.cpp",
    AGG_EXT+"agg2/src/agg_vcgen_stroke.cpp",
    AGG_EXT+"aggdraw.cxx",
    ]

if FREETYPE:
    agg_defines.append(("HAVE_FREETYPE2", None))
    agg_sources.extend([AGG_EXT+"agg2/font_freetype/agg_font_freetype.cpp",])
    agg_include_dirs.append(AGG_EXT+"agg2/font_freetype")
    agg_include_dirs.append(os.path.join(FREETYPE_ROOT, "include"))
    agg_include_dirs.append(os.path.join(FREETYPE_ROOT, "include/freetype2"))
    agg_library_dirs.append(os.path.join(FREETYPE_ROOT, "lib"))
    agg_libraries.append("freetype")

if sys.platform == "win32":
    agg_libraries.extend(["kernel32", "user32", "gdi32"])



Aggdraw     = Extension("aggdraw", sources=agg_sources, libraries=agg_libraries, include_dirs=agg_include_dirs, library_dirs=agg_library_dirs)
Geometry    = Extension("pypaint.cGeometry",     sources = ["ext/geometry/_geometry.c"])
Pathmatics  = Extension("pypaint.cPathmatics",   sources = ["ext/pathmatics/path.c"])
Supershape  = Extension("pypaint.cSuperformula", sources = ["ext/supershape/superformula.c"])

modules     = [Aggdraw, Geometry, Pathmatics, Supershape]

if FFTW:
    Fluids  = Extension("pypaint.cFluid", sources = ["ext/fluid/fluid.c"], libraries=['fftw', 'rfftw'])

setup( 
    name = "pypaint",
    version = "0.0.2b",
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
    install_requires = ['scipy>=0.0', 'numpy>=0.0'],
    ext_modules=modules,
)

#import nose
### configure paths, etc here
#nose.run()
### do other stuff here
