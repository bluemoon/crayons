
class Text(Grob, TransformMixin, ColorMixin):
    stateAttributes = ('_transform', '_transformmode', '_fillcolor', '_fontfile', '_fontsize', '_align', '_lineheight')
    
    def __init__(self, text, x=0, y=0, width=None, height=None, ctx=None, **kwargs):
        pass
