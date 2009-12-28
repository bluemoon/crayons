from distutils.core import setup, Extension

# xxx how to "guess" the include dir for freetype??

setup(name         = "ft2", 
      version      = "0.3", 
      description  = "Python extension module for Freetype 2",
      author       = "Abel Deuring",
      author_email = "a.deuring@satzbau-gmbh.de",
      licence      = "GPL",
      ext_modules  = [Extension("ft2", 
                                ["ft2module.c"], 
                                libraries=["freetype"],
                                library_dirs=["/usr/local/lib"],
                                include_dirs=["/usr/local/include/freetype2/",
                                              "/usr/include/freetype2/"],
                                extra_compile_args=["-Wall"]
                               )],
     )