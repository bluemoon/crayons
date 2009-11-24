from math import pi, sin, cos, radians
_range = range

TWOPI = pi * 2
try:
    from pypaint.cSuperformula import supercalc
except:
    # Else, use the native python
    # calculation of supershapes.
    def supercalc(m, n1, n2, n3, phi):
        a = 1.0
        b = 1.0
        
        t1 = cos(m * phi / 4) / a
        t1 = abs(t1)
        t1 = pow(t1, n2)
    
        t2 = sin(m * phi / 4) / b
        t2 = abs(t2)
        t2 = pow(t2, n3)
        
        r = pow(t1 + t2, 1 / n1)
        if abs(r) == 0:
            return (0,0)
        else:
            r = 1 / r
            return (r * cos(phi), r * sin(phi))

def path(ctx, x, y, w, h, m, n1, n2, n3, points=1000, percentage=1.0, range=TWOPI):
    first = True
    for i in _range(points):
        if i > points*percentage: 
            continue
        phi = i * range / points
        dx, dy = supercalc(m, n1, n2, n3, phi)
        dx = (dx * w) + x
        dy = (dy * h) + y
        if first:
            ctx.beginpath(dx, dy)
            first = False
        else:
            ctx.lineto(dx, dy)
    return ctx.endpath()
    
def transform(ctx, path, m, n1, n2, n3, points=100, range=TWOPI):
    first = True
    for i in _range(points):
        pt = path.point(float(i)/points)
        phi = i * range / points
        dx, dy = supercalc(m, n1, n2, n3, phi)
        if first:
            ctx.beginpath(pt.x+dx, pt.y+dy)
            first = False
        else:
            ctx.lineto(pt.x+dx, pt.y+dy)
    return ctx.endpath(draw=False)



if __name__ == "__main__":
    from pypaint.context import Context
    ctx = Context(width=400, height=400)

    def setup():    
        global x, y, w, h, m, n1, n2, n3, i
        
        x, y = 200, 200
        w, h = 100, 100
        m = 6.0
        n1 = 1.0
        n2 = 1.0
        n3 = 1.0
        i = 0.0

    def draw():
        global x, y, w, h, m, n1, n2, n3, i
        
        m = 12
        n1 = 5.0 + sin(i)
        n2 = 10 + cos(i) * 10
        n3 = sin(i) * 10
        i += 0.05
        
        ctx.rotate(i*10)
        p = path(ctx, x, y, w, h, m, n1, n2, n3)
        ctx.drawpath(p)
    
    setup()
    draw()

    ctx.save('test_images/supershape.png')
