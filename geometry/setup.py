from distutils.core import setup, Extension

module = Extension("_geometry", sources = ["geometry/_geometry.c"])

setup (name = "geometry",
       version = "1.0",
       author = "Tom De Smedt",
       description = "Common vector geometry functions.",
       ext_modules = [module])
