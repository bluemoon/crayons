from pypaint import cFluid
a = [0.0, 1.0, 1.0, 0.0]
b = [2.0, 2.0, 3.0, 3.0]
c = [2.2, 4.4, 2.0, 3.0]
d = [7.4, 2.0, 2.0, 5.0]

a = cFluid.fluid(16, 10, 10)

#X, Y, last X, last Y, time
#a.add_force(10, 10, 3, 3)
a.add_force(*b)
a.add_force(*c)
a.add_force(*d)
#print a.vectors()

for x in xrange(1):
    a.solve()
    print a.vectors()
