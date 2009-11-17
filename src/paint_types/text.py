
class Text(Grob, TransformMixin, ColorMixin):
    stateAttributes = ('_transform', '_transformmode', '_fillcolor', '_fontname', '_fontsize', '_align', '_lineheight')
    kwargs = ('fill', 'font', 'fontsize', 'align', 'lineheight')
    
    def __init__(self, ctx, text, x=0, y=0, width=None, height=None, **kwargs):
        pass
