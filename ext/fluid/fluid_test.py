from pypaint import cFluid
from pypaint.utils.p_random  import random
from math                    import *
from pypaint.shape           import shape
from pypaint.canvas          import Canvas
from pypaint.path            import path
from pypaint.pygtk           import paint_gtk
from pypaint.types.color     import Color
#from pypaint.pyglet          import *
import random

a = [0.0, 1.0, 1.0, 0.0]
b = [6.0, 2.0, 3.0, 3.0]
c = [2.2, 6.4, 2.0, 3.0]
d = [10.4, 2.0, 2.0, 5.0, 0.1, 1.0]

grid_size = 32
a = cFluid.fluid(grid_size, visc=0.00001)#, visc=0.1)

def vector_print(list):
    x = list[0]
    y = list[1]
    for idx, xy in enumerate(zip(x, y)):
        print "X, Y %d:%d %s" % (idx, idx, xy)


        
#X, Y, last X, last Y, time
#a.add_force(10, 10, 3, 3)

#print a.vectors()
#a.add_force(*b)
#a.add_force(*c)
#a.add_force(*d)
#pygame = PyGameCanvas(500, 500)

def draw():
    ctx = Canvas(width=500, height=500, gtk_draw=True)

    global m
    wn = 500.0 / (grid_size - 1)
    hn = 500.0 / (grid_size - 1)
    
    #bg = ctx.radial_gradient()

    a.solve()
    shapes = shape()
    length = int(sqrt(len(a.vectors()[0])))
    U = a.vectors()[0]
    V = a.vectors()[1]
    colors = a.rgb()

    s = shape()
    p = path()

    for i in xrange(length):
        for j in xrange(length):

            idx = (j * length) + i
            start_x = (i * wn)
            start_y = (j * hn)

            color = colors[idx]

            #r = s.rectangle(start_x, start_y, wn, hn)
            #r._strokecolor = Color(*color)
            #r._strokewidth = 0.25
            #ctx.add(r)

            p.moveto(start_x, start_y)
            p.rellineto(U[idx]*1000.0, V[idx]*1000.0)

    p._strokecolor = Color(0.0, 0.0, 0.0)
    p._stroke_width = 0.25
    ctx.add(p)
    
    if (m%100) == 0:
        a.add_force(random.randint(0, grid_size), 
                    random.randint(0, grid_size),
                    random.randint(0, grid_size),
                    random.randint(0, grid_size),
                    0,
                    0.00001
                    #random.random(),
                    #random.random()
                    )

    m += 1
    ctx.draw()
    return ctx.gtk()

def main():
    global m
    m = 0 

    draw()
    paint_gtk(callback=draw, width=500, height=500)




if __name__ == "__main__":
    benchmarking = False

    if benchmarking:
        import cProfile
        import pstats

        cProfile.run('main()', 'fluid_test.cprofile')
        p = pstats.Stats('fluid_test.cprofile')
        p.sort_stats('time').print_stats()
        #print 'INCOMING CALLERS:'
        #p.print_callers()
        
        #print 'OUTGOING CALLEES:'
        #p.print_callees('\(buildPenBrush')
    else:
        main()
