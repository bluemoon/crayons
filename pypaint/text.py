from pypaint.types.mixins import *
from pypaint.path         import path

class text(Grob, TransformMixin, ColorMixin):
    def __init__(self, **kwargs):
        TransformMixin.__init__(self)
        ColorMixin.__init__(self, **kwargs)
        
