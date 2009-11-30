from pypaint.shape        import shape
from pypaint.mixins       import *
from pypaint.types.canvas import *


class Canvas(CanvasMixin):
    def __init__(self, width=None, height=None, backend=PILCanvas):
        CanvasMixin.__init__(self, width, height)
        self.backend = backend(width, height)
        self.width  = width
        self.height = height

    def draw(self):
        self.backend.draw(stack=self.data)

    def show(self):
        self.backend.show()

    def save(self, filename, file_ext):
        self.backend.save(filename, file_ext)
        
    def background(self):
        s = shape()
        rect = s.rectangle(0, 0, self.width, self.height)
        return rect
