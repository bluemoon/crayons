import pypaint.cPathmatics

from timeit import Timer
import unittest

class testPathmatics(unittest.TestCase):
    def test_linepoint(self):
        #pypaint.cPathmatics.linepoint(1, 2, 3, 4, 5)
        t = Timer("pypaint.cPathmatics.linepoint(1, 2, 3, 4, 5)", "import pypaint.cPathmatics")
        print t.repeat()

"""
print "linelength"
t = Timer("linelength(1, 2, 3, 4)", "from pathmatics import linelength")
print t.repeat()
t = Timer("linelength(1, 2, 3, 4)", "from cPathmatics import linelength")
print t.repeat()

print "curvepoint"
t = Timer("curvepoint(1, 2, 3, 4, 5, 6, 7, 8, 9)", "from pathmatics import curvepoint")
print t.repeat()
t = Timer("curvepoint(1, 2, 3, 4, 5, 6, 7, 8, 9)", "from cPathmatics import curvepoint")
print t.repeat()

print "curvelength"
t = Timer("curvelength(1, 2, 3, 4, 5, 6, 7, 8)", "from pathmatics import curvelength")
print t.repeat(number=100000)
t = Timer("curvelength(1, 2, 3, 4, 5, 6, 7, 8)", "from cPathmatics import curvelength")
print t.repeat(number=100000)

print "curvelength n=100"
t = Timer("curvelength(1, 2, 3, 4, 5, 6, 7, 8, 100)", "from pathmatics import curvelength")
print t.repeat(number=10000)
t = Timer("curvelength(1, 2, 3, 4, 5, 6, 7, 8, 100)", "from cPathmatics import curvelength")
print t.repeat(number=10000)
"""
