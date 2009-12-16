from pypaint import cFluid
a = [0.0, 1.0, 1.0, 0.0]
b = [0.0, 2.0, 1.0, 0.0]
c = [0.0, 1.4, 2.0, 0.0]
d = [1.4, 0.0, 2.0, 1.0]

#print cFluid.solver(a, b, c, d)
a = cFluid.fluid(36, 6, 6)

#a.add_force(1, 1, 2, 6)
#a.add_force(2, 2, 6, 6)
#a.add_force(2, 2, 1, 1)
print a.vectors()
a.solve()
print a.vectors()
a.solve()
print a.vectors()
