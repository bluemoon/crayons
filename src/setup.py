import os, sys
from distutils.core import setup, Extension

Geometry = Extension("_geometry", sources = ["geometry/_geometry.c"])

setup (name = "geometry",
       version = "1.0",
       author = "Tom De Smedt",
       description = "Common vector geometry functions.",
       ext_modules = [Geometry]
)

