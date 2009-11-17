import aggdraw

class PathWrap:
    def __init__(self):
        self.path = None

    def initPath(self):
        self.path = aggdraw.Path()

    def resetPath(self):
        self.path = aggdraw.Path()

    def _getPath(self):
        return self.path
    path = property(_getPath)

    def getBounds(self, *arguments):
        return (0, 0, 0, 0)
