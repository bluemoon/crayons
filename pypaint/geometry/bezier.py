from pypaint.utils.defaults  import *
from pypaint.types.canvas    import *
from pypaint.cPathmatics     import linepoint
from pypaint.cPathmatics     import linelength
from pypaint.cPathmatics     import curvepoint
from pypaint.cPathmatics     import curvelength
from pypaint.geometry        import array

from math import sqrt, acos, cos, pi

import numpy

class TmpMixin:
    _fillcolor = None


epsilon = 1e-12

def segment_lengths(path, relative=False, n=20):
    """
    Returns a list with the lengths of each segment in the path.
    
    >>> path = BezierPath(TmpMixin)
    >>> segment_lengths(path)
    []
    >>> path.moveto(0, 0)
    >>> segment_lengths(path)
    []
    >>> path.lineto(100, 0)
    >>> segment_lengths(path)
    [100.0]
    >>> path.lineto(100, 300)
    >>> segment_lengths(path)
    [100.0, 300.0]
    >>> segment_lengths(path, relative=True)
    [0.25, 0.75]
    >>> path = BezierPath(None)
    >>> path.moveto(1, 2)
    >>> path.curveto(3, 4, 5, 6, 7, 8)
    >>> segment_lengths(path)
    [8.4852813742385695]
    """

    lengths = []
    first = True

    for el in path:
        if first == True:
            close_x, close_y = el.x, el.y
            first = False

        elif el.cmd == MOVETO:
            close_x, close_y = el.x, el.y
            lengths.append(0.0)

        elif el.cmd == CLOSE:
            lengths.append(linelength(x0, y0, close_x, close_y))

        elif el.cmd == LINETO:
            lengths.append(linelength(x0, y0, el.x, el.y))

        elif el.cmd == CURVETO:
            x3, y3, x1, y1, x2, y2 = el.x, el.y, el.ctrl1.x, el.ctrl1.y, el.ctrl2.x, el.ctrl2.y
            lengths.append(curvelength(x0, y0, x1, y1, x2, y2, x3, y3, n))
            
        if el.cmd != CLOSE:
            x0 = el.x
            y0 = el.y

    if relative:
        length = sum(lengths)
        try:
            return map(lambda l: l / length, lengths)
        except ZeroDivisionError: # If the length is zero, just return zero for all segments
            return [0.0] * len(lengths)
    else:
        return lengths

def length(path, segmented=False, n=20):

    """
    Returns the length of the path.

    Calculates the length of each spline in the path,
    using n as a number of points to measure.

    When segmented is True, returns a list
    containing the individual length of each spline
    as values between 0.0 and 1.0,
    defining the relative length of each spline
    in relation to the total path length.
    
    The length of an empty path is zero:
    >>> path = BezierPath(None)
    >>> length(path)
    0.0

    >>> path.moveto(0, 0)
    >>> path.lineto(100, 0)
    >>> length(path)
    100.0

    >>> path.lineto(100, 100)
    >>> length(path)
    200.0

    # Segmented returns a list of each segment
    >>> length(path, segmented=True)
    [0.5, 0.5]
    """

    if not segmented:
        return sum(segment_lengths(path, n=n), 0.0)
    else:
        return segment_lengths(path, relative=True, n=n)

def _locate(path, t, segments=None):
    
    """Locates t on a specific segment in the path.
    
    Returns (index, t, PathElement)
    
    A path is a combination of lines and curves (segments).
    The returned index indicates the start of the segment
    that contains point t.
    
    The returned t is the absolute time on that segment,
    in contrast to the relative t on the whole of the path.
    The returned point is the last MOVETO,
    any subsequent CLOSETO after i closes to that point.
    
    When you supply the list of segment lengths yourself,
    as returned from length(path, segmented=True),
    point() works about thirty times faster in a for-loop,
    since it doesn't need to recalculate the length
    during each iteration. Note that this has been deprecated:
    the BezierPath now caches the segment lengths the moment you use
    them.
    
    >>> path = BezierPath(None)
    >>> _locate(path, 0.0)
    Traceback (most recent call last):
        ...
    NodeBoxError: The given path is empty
    >>> path.moveto(0,0)
    >>> _locate(path, 0.0)
    Traceback (most recent call last):
        ...
    NodeBoxError: The given path is empty
    >>> path.lineto(100, 100)
    >>> _locate(path, 0.0)
    (0, 0.0, Point(x=0.0, y=0.0))
    >>> _locate(path, 1.0)
    (0, 1.0, Point(x=0.0, y=0.0))
    """
    
    if segments == None:
        segments = path.segmentlengths(relative=True)
        
    if len(segments) == 0:
        raise Exception("The given path is empty")
    
    for i, el in enumerate(path):
        if i == 0 or el.cmd == MOVETO:
            closeto = Point(el.x, el.y)
        if t <= segments[i] or i == len(segments)-1: break
        else: t -= segments[i]

    try: t /= segments[i]
    except ZeroDivisionError: pass
    if i == len(segments)-1 and segments[i] == 0: i -= 1
    
    return (i, t, closeto)

def point(path, t, segments=None):
    """
    Returns coordinates for point at t on the path.

    Gets the length of the path, based on the length
    of each curve and line in the path.
    Determines in what segment t falls.
    Gets the point on that segment.
    
    When you supply the list of segment lengths yourself,
    as returned from length(path, segmented=True),
    point() works about thirty times faster in a for-loop,
    since it doesn't need to recalculate the length
    during each iteration. Note that this has been deprecated:
    the BezierPath now caches the segment lengths the moment you use
    them.
    
    >>> path = BezierPath(None)
    >>> point(path, 0.0)
    Traceback (most recent call last):
        ...
    NodeBoxError: The given path is empty
    >>> path.moveto(0, 0)
    >>> point(path, 0.0)
    Traceback (most recent call last):
        ...
    NodeBoxError: The given path is empty
    >>> path.lineto(100, 0)
    >>> point(path, 0.0)
    PathElement(LINETO, ((0.0, 0.0),))
    >>> point(path, 0.1)
    PathElement(LINETO, ((10.0, 0.0),))
    """

    if len(path) == 0:
        raise Exception("The given path is empty")

    i, t, closeto = _locate(path, t, segments=segments)

    x0, y0 = path[i].x, path[i].y
    p1 = path[i+1]

    if p1.cmd == CLOSE:
        x, y = linepoint(t, x0, y0, closeto.x, closeto.y)
        return PathElement(LINETO, ((x, y),))
    elif p1.cmd == LINETO:
        x1, y1 = p1.x, p1.y
        x, y = linepoint(t, x0, y0, x1, y1)
        return PathElement(LINETO, ((x, y),))
    elif p1.cmd == CURVETO:
        x3, y3, x1, y1, x2, y2 = p1.x, p1.y, p1.ctrl1.x, p1.ctrl1.y, p1.ctrl2.x, p1.ctrl2.y
        x, y, c1x, c1y, c2x, c2y = curvepoint(t, x0, y0, x1, y1, x2, y2, x3, y3)
        return PathElement(CURVETO, ((c1x, c1y), (c2x, c2y), (x, y)))
    else:
        raise Exception("Unknown cmd for p1 %s" % p1)
        
def points(path, amount=100):
    """Returns an iterator with a list of calculated points for the path.
    This method calls the point method <amount> times, increasing t,
    distributing point spacing linearly.

    >>> path = BezierPath(None)
    >>> list(points(path))
    Traceback (most recent call last):
        ...
    NodeBoxError: The given path is empty
    >>> path.moveto(0, 0)
    >>> list(points(path))
    Traceback (most recent call last):
        ...
    NodeBoxError: The given path is empty
    >>> path.lineto(100, 0)
    >>> list(points(path, amount=4))
    [PathElement(LINETO, ((0.0, 0.0),)), PathElement(LINETO, ((25.0, 0.0),)), PathElement(LINETO, ((50.0, 0.0),)), PathElement(LINETO, ((75.0, 0.0),))]
    """

    if len(path) == 0:
        raise NodeBoxError, "The given path is empty"

    # The delta value is divided by amount - 1, because we also want the last point (t=1.0)
    # If I wouldn't use amount - 1, I fall one point short of the end.
    # E.g. if amount = 4, I want point at t 0.0, 0.33, 0.66 and 1.0,
    # if amount = 2, I want point at t 0.0 and t 1.0
    try:
        delta = 1.0/(amount-1)
    except ZeroDivisionError:
        delta = 1.0

    for i in xrange(amount):
        yield point(path, delta*i)

def contours(path):
    """Returns a list of contours in the path.
    
    A contour is a sequence of lines and curves
    separated from the next contour by a MOVETO.
    
    For example, the glyph "o" has two contours:
    the inner circle and the outer circle.

    >>> path = BezierPath(None)
    >>> path.moveto(0, 0)
    >>> path.lineto(100, 100)
    >>> len(contours(path))
    1
    
    A new contour is defined as something that starts with a moveto:
    >>> path.moveto(50, 50)
    >>> path.curveto(150, 150, 50, 250, 80, 95)
    >>> len(contours(path))
    2

    Empty moveto's don't do anything:
    >>> path.moveto(50, 50) 
    >>> path.moveto(50, 50)
    >>> len(contours(path))
    2
    
    It doesn't matter if the path is closed or open:
    >>> path.closepath()
    >>> len(contours(path))
    2
    """
    contours = []
    current_contour = None
    empty = True
    for i, el in enumerate(path):
        if el.cmd == MOVETO:
            if not empty:
                contours.append(current_contour)
            current_contour = BezierPath(path._ctx)
            current_contour.moveto(el.x, el.y)
            empty = True
        elif el.cmd == LINETO:
            empty = False
            current_contour.lineto(el.x, el.y)
        elif el.cmd == CURVETO:
            empty = False
            current_contour.curveto(el.ctrl1.x, el.ctrl1.y,
                el.ctrl2.x, el.ctrl2.y, el.x, el.y)
        elif el.cmd == CLOSE:
            current_contour.closepath()
    if not empty:
        contours.append(current_contour)
    return contours
    
def findpath(points, curvature=1.0):
    
    """Constructs a path between the given list of points.
    
    Interpolates the list of points and determines
    a smooth bezier path betweem them.
    
    The curvature parameter offers some control on
    how separate segments are stitched together:
    from straight angles to smooth curves.
    Curvature is only useful if the path has more than  three points.
    """
    
    # The list of points consists of Point objects,
    # but it shouldn't crash on something straightforward
    # as someone supplying a list of (x,y)-tuples.
    
    from types import TupleType
    for i, pt in enumerate(points):
        if type(pt) == TupleType:
            points[i] = Point(pt[0], pt[1])
    
    if len(points) == 0: return None
    if len(points) == 1:
        path = BezierPath(None)
        path.moveto(points[0].x, points[0].y)
        return path
    if len(points) == 2:
        path = BezierPath(None)
        path.moveto(points[0].x, points[0].y)
        path.lineto(points[1].x, points[1].y)
        return path
              
    # Zero curvature means straight lines.
    
    curvature = max(0, min(1, curvature))
    if curvature == 0:
        path = BezierPath(None)
        path.moveto(points[0].x, points[0].y)
        for i in range(len(points)): 
            path.lineto(points[i].x, points[i].y)
        return path
        
    curvature = 4 + (1.0-curvature)*40
    
    dx = {0: 0, len(points)-1: 0}
    dy = {0: 0, len(points)-1: 0}
    bi = {1: -0.25}
    ax = {1: (points[2].x-points[0].x-dx[0]) / 4}
    ay = {1: (points[2].y-points[0].y-dy[0]) / 4}
    
    for i in range(2, len(points)-1):
        bi[i] = -1 / (curvature + bi[i-1])
        ax[i] = -(points[i+1].x-points[i-1].x-ax[i-1]) * bi[i]
        ay[i] = -(points[i+1].y-points[i-1].y-ay[i-1]) * bi[i]
        
    r = range(1, len(points)-1)
    r.reverse()
    for i in r:
        dx[i] = ax[i] + dx[i+1] * bi[i]
        dy[i] = ay[i] + dy[i+1] * bi[i]

    path = BezierPath(None)
    path.moveto(points[0].x, points[0].y)
    for i in range(len(points)-1):
        path.curveto(points[i].x + dx[i], 
                     points[i].y + dy[i],
                     points[i+1].x - dx[i+1], 
                     points[i+1].y - dy[i+1],
                     points[i+1].x,
                     points[i+1].y)
    
    return path

def insert_point(path, t):
    """
    Returns a path copy with an extra point at t.
    
    >>> path = BezierPath(None)
    >>> path.moveto(0, 0)
    >>> insert_point(path, 0.1)
    Traceback (most recent call last):
        ...
    NodeBoxError: The given path is empty
    >>> path.moveto(0, 0)
    >>> insert_point(path, 0.2)
    Traceback (most recent call last):
        ...
    NodeBoxError: The given path is empty
    >>> path.lineto(100, 50)
    >>> len(path)
    2
    >>> path = insert_point(path, 0.5)
    >>> len(path)
    3
    >>> path[1]
    PathElement(LINETO, ((50.0, 25.0),))
    >>> path = BezierPath(None)
    >>> path.moveto(0, 100)
    >>> path.curveto(0, 50, 100, 50, 100, 100)
    >>> path = insert_point(path, 0.5)
    >>> path[1]
    PathElement(LINETO, ((25.0, 62.5), (0.0, 75.0), (50.0, 62.5))
    """
    
    i, t, closeto = _locate(path, t)
    
    x0 = path[i].x
    y0 = path[i].y
    p1 = path[i+1]
    p1cmd, x3, y3, x1, y1, x2, y2 = p1.cmd, p1.x, p1.y, p1.ctrl1.x, p1.ctrl1.y, p1.ctrl2.x, p1.ctrl2.y
    
    if p1cmd == CLOSE:
        pt_cmd = LINETO
        pt_x, pt_y = linepoint(t, x0, y0, closeto.x, closeto.y)
    elif p1cmd == LINETO:
        pt_cmd = LINETO
        pt_x, pt_y = linepoint(t, x0, y0, x3, y3)
    elif p1cmd == CURVETO:
        pt_cmd = CURVETO
        pt_x, pt_y, pt_c1x, pt_c1y, pt_c2x, pt_c2y, pt_h1x, pt_h1y, pt_h2x, pt_h2y = \
            curvepoint(t, x0, y0, x1, y1, x2, y2, x3, y3, True)
    else:
        raise Exception("Locate should not return a MOVETO")
    
    new_path = BezierPath(None)
    new_path.moveto(path[0].x, path[0].y)
    for j in range(1, len(path)):
        if j == i+1:
            if pt_cmd == CURVETO:
                new_path.curveto(pt_h1x, pt_h1y,
                             pt_c1x, pt_c1y,
                             pt_x, pt_y)
                new_path.curveto(pt_c2x, pt_c2y,
                             pt_h2x, pt_h2y,
                             path[j].x, path[j].y)
            elif pt_cmd == LINETO:
                new_path.lineto(pt_x, pt_y)
                if path[j].cmd != CLOSE:
                    new_path.lineto(path[j].x, path[j].y)
                else:
                    new_path.closepath()
            else:
                raise Exception("Didn't expect pt_cmd %s here" % pt_cmd)
            
        else:
            if path[j].cmd == MOVETO:
                new_path.moveto(path[j].x, path[j].y)
            if path[j].cmd == LINETO:
                new_path.lineto(path[j].x, path[j].y)
            if path[j].cmd == CURVETO:
                new_path.curveto(path[j].ctrl1.x, path[j].ctrl1.y,
                             path[j].ctrl2.x, path[j].ctrl2.y,
                             path[j].x, path[j].y)
            if path[j].cmd == CLOSE:
                new_path.closepath()

    return new_path


##### New Bezier #####
def calculateQuadraticBounds(pt1, pt2, pt3):
    """
    Return the bounding rectangle for a qudratic bezier segment.
    pt1 and pt3 are the "anchor" points, pt2 is the "handle".
    
    >>> calculateQuadraticBounds((0, 0), (50, 100), (100, 0))
    (0.0, 0.0, 100.0, 50.0)
    >>> calculateQuadraticBounds((0, 0), (100, 0), (100, 100))
    (0.0, 0.0, 100.0, 100.0)
    """

    a, b, c = calculateQuadraticParameters(pt1, pt2, pt3)
    ## calc first derivative
    ax, ay = a * 2
    bx, by = b
    roots = []
    if ax != 0:
        roots.append(-bx/ax)
	if ay != 0:
            roots.append(-by/ay)
        points = [a*t*t + b*t + c for t in roots if 0 <= t < 1] + [pt1, pt3]
        return calcBounds(points)


def calculateCubicBounds(pt1, pt2, pt3, pt4):
	"""
        Return the bounding rectangle for a cubic bezier segment.
	pt1 and pt4 are the "anchor" points, pt2 and pt3 are the "handles".

        >>> calculateCubicBounds((0, 0), (25, 100), (75, 100), (100, 0))
        (0.0, 0.0, 100.0, 75.0)
        >>> calculateCubicBounds((0, 0), (50, 0), (100, 50), (100, 100))
        (0.0, 0.0, 100.0, 100.0)
        >>> calculateCubicBounds((50, 0), (0, 100), (100, 100), (50, 0))
        (35.5662432703, 0.0, 64.4337567297, 75.0)

	"""
	a, b, c, d = calculateCubicParameters(pt1, pt2, pt3, pt4)
	# calc first derivative
	ax, ay = a * 3.0
	bx, by = b * 2.0
	cx, cy = c
	xRoots = [t for t in solveQuadratic(ax, bx, cx) if 0 <= t < 1]
	yRoots = [t for t in solveQuadratic(ay, by, cy) if 0 <= t < 1]
	roots = xRoots + yRoots
	
	points = [(a*t*t*t + b*t*t + c * t + d) for t in roots] + [pt1, pt4]
	return calcBounds(points)


def splitLine(pt1, pt2, where, isHorizontal):
	"""Split the line between pt1 and pt2 at position 'where', which
	is an x coordinate if isHorizontal is False, a y coordinate if
	isHorizontal is True. Return a list of two line segments if the
	line was successfully split, or a list containing the original
	line.

		>>> printSegments(splitLine((0, 0), (100, 100), 50, True))
		((0, 0), (50.0, 50.0))
		((50.0, 50.0), (100, 100))
		>>> printSegments(splitLine((0, 0), (100, 100), 100, True))
		((0, 0), (100, 100))
		>>> printSegments(splitLine((0, 0), (100, 100), 0, True))
		((0, 0), (0.0, 0.0))
		((0.0, 0.0), (100, 100))
		>>> printSegments(splitLine((0, 0), (100, 100), 0, False))
		((0, 0), (0.0, 0.0))
		((0.0, 0.0), (100, 100))
	"""
	pt1, pt2 = numpy.array((pt1, pt2))
	a = (pt2 - pt1)
	b = pt1
	ax = a[isHorizontal]
	if ax == 0:
		return [(pt1, pt2)]
	t = float(where - b[isHorizontal]) / ax
	if 0 <= t < 1:
		midPt = a * t + b
		return [(pt1, midPt), (midPt, pt2)]
	else:
		return [(pt1, pt2)]


def splitQuadratic(pt1, pt2, pt3, where, isHorizontal):
	"""Split the quadratic curve between pt1, pt2 and pt3 at position 'where',
	which is an x coordinate if isHorizontal is False, a y coordinate if
	isHorizontal is True. Return a list of curve segments.

		>>> printSegments(splitQuadratic((0, 0), (50, 100), (100, 0), 150, False))
		((0, 0), (50, 100), (100, 0))
		>>> printSegments(splitQuadratic((0, 0), (50, 100), (100, 0), 50, False))
		((0.0, 0.0), (25.0, 50.0), (50.0, 50.0))
		((50.0, 50.0), (75.0, 50.0), (100.0, 0.0))
		>>> printSegments(splitQuadratic((0, 0), (50, 100), (100, 0), 25, False))
		((0.0, 0.0), (12.5, 25.0), (25.0, 37.5))
		((25.0, 37.5), (62.5, 75.0), (100.0, 0.0))
		>>> printSegments(splitQuadratic((0, 0), (50, 100), (100, 0), 25, True))
		((0.0, 0.0), (7.32233047034, 14.6446609407), (14.6446609407, 25.0))
		((14.6446609407, 25.0), (50.0, 75.0), (85.3553390593, 25.0))
		((85.3553390593, 25.0), (92.6776695297, 14.6446609407), (100.0, -7.1054273576e-15))
		>>> # XXX I'm not at all sure if the following behavior is desirable:
		>>> printSegments(splitQuadratic((0, 0), (50, 100), (100, 0), 50, True))
		((0.0, 0.0), (25.0, 50.0), (50.0, 50.0))
		((50.0, 50.0), (50.0, 50.0), (50.0, 50.0))
		((50.0, 50.0), (75.0, 50.0), (100.0, 0.0))
	"""
	a, b, c = calcQuadraticParameters(pt1, pt2, pt3)
	solutions = solveQuadratic(a[isHorizontal], b[isHorizontal],
		c[isHorizontal] - where)
	solutions = [t for t in solutions if 0 <= t < 1]
	solutions.sort()
	if not solutions:
		return [(pt1, pt2, pt3)]
	return _splitQuadraticAtT(a, b, c, *solutions)


def splitCubic(pt1, pt2, pt3, pt4, where, isHorizontal):
	"""Split the cubic curve between pt1, pt2, pt3 and pt4 at position 'where',
	which is an x coordinate if isHorizontal is False, a y coordinate if
	isHorizontal is True. Return a list of curve segments.

		>>> printSegments(splitCubic((0, 0), (25, 100), (75, 100), (100, 0), 150, False))
		((0, 0), (25, 100), (75, 100), (100, 0))
		>>> printSegments(splitCubic((0, 0), (25, 100), (75, 100), (100, 0), 50, False))
		((0.0, 0.0), (12.5, 50.0), (31.25, 75.0), (50.0, 75.0))
		((50.0, 75.0), (68.75, 75.0), (87.5, 50.0), (100.0, 0.0))
		>>> printSegments(splitCubic((0, 0), (25, 100), (75, 100), (100, 0), 25, True))
		((0.0, 0.0), (2.2937927384, 9.17517095361), (4.79804488188, 17.5085042869), (7.47413641001, 25.0))
		((7.47413641001, 25.0), (31.2886200204, 91.6666666667), (68.7113799796, 91.6666666667), (92.52586359, 25.0))
		((92.52586359, 25.0), (95.2019551181, 17.5085042869), (97.7062072616, 9.17517095361), (100.0, 1.7763568394e-15))
	"""
	a, b, c, d = calcCubicParameters(pt1, pt2, pt3, pt4)
	solutions = solveCubic(a[isHorizontal], b[isHorizontal], c[isHorizontal],
		d[isHorizontal] - where)
	solutions = [t for t in solutions if 0 <= t < 1]
	solutions.sort()
	if not solutions:
		return [(pt1, pt2, pt3, pt4)]
	return _splitCubicAtT(a, b, c, d, *solutions)


def splitQuadraticAtT(pt1, pt2, pt3, *ts):
	"""
        Split the quadratic curve between pt1, pt2 and pt3 at one or more
	values of t. Return a list of curve segments.

        >>> printSegments(splitQuadraticAtT((0, 0), (50, 100), (100, 0), 0.5))
        ((0.0, 0.0), (25.0, 50.0), (50.0, 50.0))
        ((50.0, 50.0), (75.0, 50.0), (100.0, 0.0))
        >>> printSegments(splitQuadraticAtT((0, 0), (50, 100), (100, 0), 0.5, 0.75))
        ((0.0, 0.0), (25.0, 50.0), (50.0, 50.0))
        ((50.0, 50.0), (62.5, 50.0), (75.0, 37.5))
        ((75.0, 37.5), (87.5, 25.0), (100.0, 0.0))
	"""
	a, b, c = calcQuadraticParameters(pt1, pt2, pt3)
	return _splitQuadraticAtT(a, b, c, *ts)


def splitCubicAtT(pt1, pt2, pt3, pt4, *ts):
	"""Split the cubic curve between pt1, pt2, pt3 and pt4 at one or more
	values of t. Return a list of curve segments.

		>>> printSegments(splitCubicAtT((0, 0), (25, 100), (75, 100), (100, 0), 0.5))
		((0.0, 0.0), (12.5, 50.0), (31.25, 75.0), (50.0, 75.0))
		((50.0, 75.0), (68.75, 75.0), (87.5, 50.0), (100.0, 0.0))
		>>> printSegments(splitCubicAtT((0, 0), (25, 100), (75, 100), (100, 0), 0.5, 0.75))
		((0.0, 0.0), (12.5, 50.0), (31.25, 75.0), (50.0, 75.0))
		((50.0, 75.0), (59.375, 75.0), (68.75, 68.75), (77.34375, 56.25))
		((77.34375, 56.25), (85.9375, 43.75), (93.75, 25.0), (100.0, 0.0))
	"""
	a, b, c, d = calcCubicParameters(pt1, pt2, pt3, pt4)
	return _splitCubicAtT(a, b, c, d, *ts)


def _splitQuadraticAtT(a, b, c, *ts):
	ts = list(ts)
	segments = []
	ts.insert(0, 0.0)
	ts.append(1.0)
	for i in range(len(ts) - 1):
		t1 = ts[i]
		t2 = ts[i+1]
		delta = (t2 - t1)
		# calc new a, b and c
		a1 = a * delta**2
		b1 = (2*a*t1 + b) * delta
		c1 = a*t1**2 + b*t1 + c
		pt1, pt2, pt3 = calcQuadraticPoints(a1, b1, c1)
		segments.append((pt1, pt2, pt3))
	return segments


def _splitCubicAtT(a, b, c, d, *ts):
	ts = list(ts)
	ts.insert(0, 0.0)
	ts.append(1.0)
	segments = []
	for i in range(len(ts) - 1):
		t1 = ts[i]
		t2 = ts[i+1]
		delta = (t2 - t1)
		# calc new a, b, c and d
		a1 = a * delta**3
		b1 = (3*a*t1 + b) * delta**2
		c1 = (2*b*t1 + c + 3*a*t1**2) * delta
		d1 = a*t1**3 + b*t1**2 + c*t1 + d
		pt1, pt2, pt3, pt4 = calcCubicPoints(a1, b1, c1, d1)
		segments.append((pt1, pt2, pt3, pt4))
	return segments


#
# Equation solvers.
#

def solveQuadratic(a, b, c, sqrt=sqrt):
	"""Solve a quadratic equation where a, b and c are real.
	    a*x*x + b*x + c = 0
	This function returns a list of roots. Note that the returned list
	is neither guaranteed to be sorted nor to contain unique values!
	"""
	if abs(a) < epsilon:
		if abs(b) < epsilon:
			# We have a non-equation; therefore, we have no valid solution
			roots = []
		else:
			# We have a linear equation with 1 root.
			roots = [-c/b]
	else:
		# We have a true quadratic equation.  Apply the quadratic formula to find two roots.
		DD = b*b - 4.0*a*c
		if DD >= 0.0:
			rDD = sqrt(DD)
			roots = [(-b+rDD)/2.0/a, (-b-rDD)/2.0/a]
		else:
			# complex roots, ignore
			roots = []
	return roots


def solveCubic(a, b, c, d,
		abs=abs, pow=pow, sqrt=sqrt, cos=cos, acos=acos, pi=pi):
	"""Solve a cubic equation where a, b, c and d are real.
	    a*x*x*x + b*x*x + c*x + d = 0
	This function returns a list of roots. Note that the returned list
	is neither guaranteed to be sorted nor to contain unique values!
	"""
	#
	# adapted from:
	#   CUBIC.C - Solve a cubic polynomial
	#   public domain by Ross Cottrell
	# found at: http://www.strangecreations.com/library/snippets/Cubic.C
	#
	if abs(a) < epsilon:
		# don't just test for zero; for very small values of 'a' solveCubic()
		# returns unreliable results, so we fall back to quad.
		return solveQuadratic(b, c, d)
	a = float(a)
	a1 = b/a
	a2 = c/a
	a3 = d/a
	
	Q = (a1*a1 - 3.0*a2)/9.0
	R = (2.0*a1*a1*a1 - 9.0*a1*a2 + 27.0*a3)/54.0
	R2_Q3 = R*R - Q*Q*Q

	if R2_Q3 < 0:
		theta = acos(R/sqrt(Q*Q*Q))
		rQ2 = -2.0*sqrt(Q)
		x0 = rQ2*cos(theta/3.0) - a1/3.0
		x1 = rQ2*cos((theta+2.0*pi)/3.0) - a1/3.0
		x2 = rQ2*cos((theta+4.0*pi)/3.0) - a1/3.0
		return [x0, x1, x2]
	else:
		if Q == 0 and R == 0:
			x = 0
		else:
			x = pow(sqrt(R2_Q3)+abs(R), 1/3.0)
			x = x + Q/x
		if R >= 0.0:
			x = -x
		x = x - a1/3.0
		return [x]



## Conversion routines for points to parameters and vice versa
def calculateQuadraticParameters(pt1, pt2, pt3):
	pt1, pt2, pt3 = numpy.array((pt1, pt2, pt3))
	c = pt1
	b = (pt2 - c) * 2.0
	a = pt3 - c - b
	return a, b, c


def calculateCubicParameters(pt1, pt2, pt3, pt4):
	pt1, pt2, pt3, pt4 = numpy.array((pt1, pt2, pt3, pt4))
	d = pt1
	c = (pt2 - d) * 3.0
	b = (pt3 - pt2) * 3.0 - c
	a = pt4 - d - c - b
	return a, b, c, d


def calculateQuadraticPoints(a, b, c):
    pt1 = c
    pt2 = (b * 0.5) + c
    pt3 = a + b + c
    return pt1, pt2, pt3


def calculateCubicPoints(a, b, c, d):
    pt1 = d
    pt2 = (c / 3.0) + d
    pt3 = (b + c) / 3.0 + pt2
    pt4 = a + d + c + b
    return pt1, pt2, pt3, pt4


def _segmentrepr(obj):
    """
    >>> _segmentrepr([1, [2, 3], [], [[2, [3, 4], numpy.array([0.1, 2.2])]]])
    '(1, (2, 3), (), ((2, (3, 4), (0.1, 2.2))))'
    """
    try:
        it = iter(obj)
    except TypeError:
        return str(obj)
    else:
        return "(%s)" % ", ".join([_segmentrepr(x) for x in it])


def printSegments(segments):
    """
    Helper for the doctests, displaying each segment in a list of
    segments on a single line as a tuple.
    """
    for segment in segments:
        print _segmentrepr(segment)


def decomposeSuperBezierSegment(points):
    """
    Split the SuperBezier described by 'points' into a list of regular
    bezier segments. The 'points' argument must be a sequence with length
    3 or greater, containing (x, y) coordinates. The last point is the
    destination on-curve point, the rest of the points are off-curve points.
    The start point should not be supplied.
    
    This function returns a list of (pt1, pt2, pt3) tuples, which each
    specify a regular curveto-style bezier segment.
    """
    n = len(points) - 1
    assert n > 1
    bezierSegments = []
    pt1, pt2, pt3 = points[0], None, None
    for i in range(2, n+1):
        # calculate points in between control points.
        nDivisions = min(i, 3, n-i+2)
        d = float(nDivisions)
        for j in range(1, nDivisions):
            factor = j / d
            temp1 = points[i-1]
            temp2 = points[i-2]
            temp = (temp2[0] + factor * (temp1[0] - temp2[0]),
                    temp2[1] + factor * (temp1[1] - temp2[1]))
            if pt2 is None:
                pt2 = temp
            else:
                pt3 = (0.5 * (pt2[0] + temp[0]),
                       0.5 * (pt2[1] + temp[1]))
                bezierSegments.append((pt1, pt2, pt3))
                pt1, pt2, pt3 = temp, None, None

    bezierSegments.append((pt1, points[-2], points[-1]))

    return bezierSegments


def decomposeQuadraticSegment(points):
    """
    Split the quadratic curve segment described by 'points' into a list
    of "atomic" quadratic segments. The 'points' argument must be a sequence
    with length 2 or greater, containing (x, y) coordinates. The last point
    is the destination on-curve point, the rest of the points are off-curve
    points. The start point should not be supplied.
    
    This function returns a list of (pt1, pt2) tuples, which each specify a
    plain quadratic bezier segment.
    """
    n = len(points) - 1

    assert n > 0

    quadSegments = []

    for i in range(n - 1):
        x, y = points[i]
        nx, ny = points[i+1]
        impliedPt = (0.5 * (x + nx), 0.5 * (y + ny))
        quadSegments.append((points[i], impliedPt))

    quadSegments.append((points[-2], points[-1]))
    return quadSegments

    
def _test():
    import doctest, bezier
    return doctest.testmod(bezier)

if __name__=='__main__':
    _test()
