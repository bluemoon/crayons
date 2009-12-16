class statistics_mixin(object):
    def _count(self):
        return len(self)
    count = property(_count)
    def _used(self):
        return len(filter(lambda cell: cell.has_content(), self))
    used = property(_used)
    def _empty(self):
        return len(self) - self.used
    empty = property(_empty)
    def _numeric(self):
        return filter(lambda cell: cell.has_content() and cell.content.is_numeric(), self)
    numeric = property(_numeric)
    def _numbers(self):
        return [float(cell.content) for cell in self.numeric]
    numbers = property(_numbers)
    def _sum(self):
        return sum(self.numbers)
    sum = property(_sum)
    def _avg(self):
        return self.sum / len(self.numeric)
    mean = average = avg = property(_avg)
    def _min(self):
        return min(self.numbers)
    min = property(_min)
    def _max(self):
        return max(self.numbers)
    max = property(_max)
    def _variance(self):
        avg = self.avg
        return sum([(x-avg)**2 for x in self.numbers]) / (len(self.numeric)-1)
    variance = property(_variance)
    def _stdev(self):
        return sqrt(self.variance)
    stdev = property(_stdev)


class Cells(list, statistics_mixin):
    def __init__(self, data=[], parent=None):
        list.__init__(self, data)
        self._id = _unique_id()
        self.parent = parent
        self.name = ""

    def __eq__(self, other):
        return self._id == other._id
    def __add__(self, other):
        return cells(list.__add__(self, other))
    def __getslice__(self, i, j):
        slice = list(self)[i:j]
        return cells(slice)
    def _get_property(self, k):
        p = getattr(self[0], k)
        for cell in self:
            if getattr(cell, k) != p: return None
        return p
    def _set_property(self, k, v):
        for cell in self: setattr(cell, k, v)
    
    def _get_root(self): return self._get_property("root")
    root = property(_get_root)

    def _get_styles(self): return self._get_property("styles")
    style = property(_get_styles)
    
    def _get_style(self)    : return self._get_property("style")
    def _set_style(self, v) : self._set_property("style", v)
    style = property(_get_style, _set_style)

    def _get_content(self)    : return self._get_property("content")
    def _set_content(self, v) : self._set_property("content", content(v))
    content = value = property(_get_content, _set_content)

    def _get_content_width(self)  : return self._get_property("content_width")
    def _get_content_height(self) : return self._get_property("content_height")
    content_width  = property(_get_content_width)
    content_height = property(_get_content_height)
    
    def _get_width(self)    : return self._get_property("width")
    def _set_width(self, v) : self._set_property("width", v)
    width = property(_get_width, _set_width)    

    def _get_height(self)    : return self._get_property("height")
    def _set_height(self, v) : self._set_property("height", v)
    height = property(_get_height, _set_height)

    def _get_fixed(self)    : return self._get_property("fixed")
    def _set_fixed(self, v) : self._set_property("fixed", v)
    fixed = property(_get_fixed, _set_fixed)

    def _get_x(self): return 0
    def _get_y(self): return self._get_property("y")
    x = property(_get_x)
    y = property(_get_y)

    def flow_horizontal(self, recursive=True):
        for cell in self:
            cell.flow_horizontal(recursive)

    def flow_vertical(self, recursive=True):
        for cell in self:
            cell.flow_vertical(recursive)
    
