from gekko import GEKKO

m = GEKKO()
m.options.SOLVER = 1
# m.options.IMODE = 3
m.options.MAX_ITER = 100000

x1 = m.Var()
x2 = m.Var()
x3 = m.Var()

x4 = m.Var()
x5 = m.Var()
x6 = m.Var()

x7 = m.Var()
x8 = m.Var()
x9 = m.Var()

m.Equation(x1 + x2 + x3 == 15)
m.Equation(x4 + x5 + x6 == 5)
m.Equation(x7 + x8 + x9 == 100)

t1 = m.max2(x1, m.max2(x2, x3))
t2 = m.max2(x4, m.max2(x5, x6))
t3 = m.max2(x7, m.max2(x8, x9))

m.Obj(t1 + t2 + t3)
m.solve()
print(m.options.OBJFCNVAL)

m = GEKKO()
m.options.SOLVER = 1
# m.options.IMODE = 3
m.options.MAX_ITER = 100000

x1 = m.Var()
x2 = m.Var()
x3 = m.Var()
z1 = m.Var()

m.Equation(z1 >= x1)
m.Equation(z1 >= x2)
m.Equation(z1 >= x3)

x4 = m.Var()
x5 = m.Var()
x6 = m.Var()
z2 = m.Var()

m.Equation(z2 >= x4)
m.Equation(z2 >= x5)
m.Equation(z2 >= x6)

x7 = m.Var()
x8 = m.Var()
x9 = m.Var()
z3 = m.Var()

m.Equation(z3 >= x7)
m.Equation(z3 >= x8)
m.Equation(z3 >= x9)

m.Equation(x1 + x2 + x3 == 15)
m.Equation(x4 + x5 + x6 == 5)
m.Equation(x7 + x8 + x9 == 100)


obj = z1 + z2 + z3

m.Obj(obj)
m.solve(disp=False)
print(m.options.OBJFCNVAL)