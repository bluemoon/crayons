import os, sys

from distutils.core import setup, Extension

#Geometry = Extension("_geometry", sources = ["geometry/_geometry.c"])

setup (name = "pypaint",
       version = "0.0.1a",
       author = "Alex Toney",
       package_dir={
        'pypaint' : 'pypaint'
       },
       packages=['pypaint'],

       
)

