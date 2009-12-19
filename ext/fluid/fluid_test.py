from pypaint import cFluid
a = [0.0, 1.0, 1.0, 0.0]
b = [0.0, 2.0, 1.0, 0.0]
c = [0.0, 1.4, 2.0, 0.0]
d = [1.4, 0.0, 2.0, 1.0]

a = cFluid.fluid(36, 10, 10)

#X, Y, last X, last Y, time
a.add_force(10, 10, 1, 1)
a.add_force(*b)
a.add_force(*c)
a.add_force(*d)

for x in xrange(1):
    a.solve()
    print a.vectors()
