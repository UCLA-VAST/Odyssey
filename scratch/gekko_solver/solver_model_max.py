from gekko import GEKKO

m = GEKKO()
m.options.SOLVER = 1
# m.options.IMODE = 3
m.options.MAX_ITER = 100000
# m.options.COLDSTART = 1
# m.options.NODES = 3
# m.options.MV_TYPE = 1

bram_bound = 3763
dsp_bound = 8601

q = 3
p = 3
o = 256
r = 256
c = 256
i = 256
r_t1 = m.Var(lb=1, ub=r, value=r)
c_t1 = m.Var(lb=1, ub=c, value=c)
o_t1 = m.Var(lb=1, ub=o, value=o)
i_t1 = m.Var(lb=1, ub=i, value=i)
r_t2 = m.Var(lb=1, ub=r, value=r)
c_t2 = m.Var(lb=1, ub=c, value=c)
o_t2 = m.Var(lb=1, ub=o, value=o)
i_t2 = m.Var(lb=1, ub=i, value=i)
p14 = m.Var(lb=1)
p15 = m.Var(lb=1)
p16 = m.Var(lb=1)
p17 = m.Var(lb=1)

cin_IO_L1_in_single_latency = ((r_t1/r_t2) * ((((r_t2-1)+(p-1))+1)*(((c_t2-1)+(q-1))+1)*i_t1/p14) + 1)
cin_IO_L2_in_single_latency = (c_t1/c_t2) * (r_t1/r_t2) * ((((r_t2-1)+(p-1))+1)*(((c_t2-1)+(q-1))+1)*i_t1/p14)
cin_IO_L3_in_single_latency = (c_t1/c_t2) * (r_t1/r_t2) * ((((r_t2-1)+(p-1))+1)*(((c_t2-1)+(q-1))+1)*i_t1/i_t1*(20+i_t1/(512/8/4)))
cout_IO_L1_in_single_latency = ((r_t1/r_t2) * (r_t2*c_t2*o_t1/p15) + 1)
cout_IO_L2_in_single_latency = (c_t1/c_t2) * (r_t1/r_t2) * (r_t2*c_t2*o_t1/p15)
cout_IO_L3_in_single_latency = (c_t1/c_t2) * (r_t1/r_t2) * (r_t2*c_t2*o_t1/o_t1*(20+o_t1/(512/8/4)))
w_IO_L2_in_single_latency = ((c_t1/c_t2) * (o_t1*((p-1)+1)*((q-1)+1)*i_t1/p17) + 1)
w_IO_L3_in_single_latency = (c_t1/c_t2) * (o_t1*((p-1)+1)*((q-1)+1)*i_t1/i_t1*(20+i_t1/(512/8/4)))

t1 = m.max2(cin_IO_L1_in_single_latency, cin_IO_L2_in_single_latency)
t2 = m.max2(t1, cin_IO_L3_in_single_latency)
t3 = m.max2(t2, cout_IO_L1_in_single_latency)
t4 = m.max2(t3, cout_IO_L2_in_single_latency)
t5 = m.max2(t4, cout_IO_L3_in_single_latency)
t6 = m.max2(t5, w_IO_L2_in_single_latency)
t7 = m.max2(t6, w_IO_L3_in_single_latency)

latency_prologue = t7

# m.Equation(cin_IO_L1_in_single_latency <= latency_prologue)
# m.Equation(cin_IO_L2_in_single_latency <= latency_prologue)
# m.Equation(cin_IO_L3_in_single_latency <= latency_prologue)
# m.Equation(cout_IO_L1_in_single_latency <= latency_prologue)
# m.Equation(cout_IO_L2_in_single_latency <= latency_prologue)
# m.Equation(cout_IO_L3_in_single_latency <= latency_prologue)
# m.Equation(w_IO_L2_in_single_latency <= latency_prologue)
# m.Equation(w_IO_L3_in_single_latency <= latency_prologue)


cout_IO_L1_out_single_latency = ((r_t1/r_t2) * (r_t2*c_t2*o_t1/p15) + 1)
cout_IO_L2_out_single_latency = (c_t1/c_t2) * (r_t1/r_t2) * (r_t2*c_t2*o_t1/p15)
cout_IO_L3_out_single_latency = (c_t1/c_t2) * (r_t1/r_t2) * (r_t2*c_t2*o_t1/o_t1*(20+o_t1/(512/8/4)))

t8 = m.max2(cout_IO_L1_out_single_latency, cout_IO_L2_out_single_latency)
t9 = m.max2(t8, cout_IO_L3_out_single_latency)

latency_epilogue = t9

# m.Equation(cout_IO_L1_out_single_latency <= latency_epilogue)
# m.Equation(cout_IO_L2_out_single_latency <= latency_epilogue)
# m.Equation(cout_IO_L3_out_single_latency <= latency_epilogue)

PE_latency = ((o/o_t1)) * ((i/i_t1)) * ((r/r_t1)) * ((c/c_t1)) * (1 + (o_t1/o_t2) * (i_t1/i_t2) * p * q * o_t2 * c_t2 * r_t2 * 1 + 1)
cin_IO_L1_in_latency = ((o/o_t1)) * ((i/i_t1)) * ((r/r_t1)) * ((c/c_t1)) * (m.max2((r_t1/r_t2) * ((((r_t2-1)+(p-1))+1)*(((c_t2-1)+(q-1))+1)*i_t1/p14), (o_t1/o_t2) * (i_t1/i_t2) * p * q * o_t2 * c_t2 * r_t2 * 1) + 1)
cin_IO_L2_in_latency = ((o/o_t1)) * ((i/i_t1)) * ((r/r_t1)) * ((c/c_t1)) * (c_t1/c_t2) * (r_t1/r_t2) * ((((r_t2-1)+(p-1))+1)*(((c_t2-1)+(q-1))+1)*i_t1/p14)
cin_IO_L3_in_latency = ((o/o_t1)) * ((i/i_t1)) * ((r/r_t1)) * ((c/c_t1)) * (c_t1/c_t2) * (r_t1/r_t2) * ((((r_t2-1)+(p-1))+1)*(((c_t2-1)+(q-1))+1)*i_t1/i_t1*(20+i_t1/(512/8/4)))
cout_IO_L1_in_latency = ((o/o_t1)) * ((r/r_t1)) * ((c/c_t1)) * (m.max2((r_t1/r_t2) * (r_t2*c_t2*o_t1/p15), (o_t1/o_t2) * o_t2 * c_t2 * r_t2 * 1) + 1)
cout_IO_L1_out_latency = ((o/o_t1)) * ((r/r_t1)) * ((c/c_t1)) * (m.max2((r_t1/r_t2) * (r_t2*c_t2*o_t1/p15), (o_t1/o_t2) * o_t2 * c_t2 * r_t2 * 1) + 1)
cout_IO_L2_in_latency = ((o/o_t1)) * ((r/r_t1)) * ((c/c_t1)) * (c_t1/c_t2) * (r_t1/r_t2) * (r_t2*c_t2*o_t1/p15)
cout_IO_L2_out_latency = ((o/o_t1)) * ((r/r_t1)) * ((c/c_t1)) * (c_t1/c_t2) * (r_t1/r_t2) * (r_t2*c_t2*o_t1/p15)
cout_IO_L3_in_latency = ((o/o_t1)) * ((r/r_t1)) * ((c/c_t1)) * (c_t1/c_t2) * (r_t1/r_t2) * (r_t2*c_t2*o_t1/o_t1*(20+o_t1/(512/8/4)))
cout_IO_L3_out_latency = ((o/o_t1)) * ((r/r_t1)) * ((c/c_t1)) * (c_t1/c_t2) * (r_t1/r_t2) * (r_t2*c_t2*o_t1/o_t1*(20+o_t1/(512/8/4)))
w_IO_L2_in_latency = ((o/o_t1)) * ((i/i_t1)) * (m.max2((c_t1/c_t2) * (o_t1*((p-1)+1)*((q-1)+1)*i_t1/p17), ((r/r_t1)) * ((c/c_t1)) * (o_t1/o_t2) * (i_t1/i_t2) * p * q * o_t2 * c_t2 * r_t2 * 1) + 1)
w_IO_L3_in_latency = ((o/o_t1)) * ((i/i_t1)) * (c_t1/c_t2) * (o_t1*((p-1)+1)*((q-1)+1)*i_t1/i_t1*(20+i_t1/(512/8/4)))

t10 = m.max2(PE_latency, cin_IO_L1_in_latency)
t11 = m.max2(t10, cin_IO_L2_in_latency)
t12 = m.max2(t11, cin_IO_L3_in_latency)
t13 = m.max2(t12, cout_IO_L1_in_latency)
t14 = m.max2(t13, cout_IO_L1_out_latency)
t15 = m.max2(t14, cout_IO_L2_in_latency)
t16 = m.max2(t15, cout_IO_L2_out_latency)
t17 = m.max2(t16, cout_IO_L3_in_latency)
t18 = m.max2(t17, cout_IO_L3_out_latency)
t19 = m.max2(t18, w_IO_L2_in_latency)
t20 = m.max2(t19, w_IO_L3_in_latency)

latency_main = t20

# m.Equation(PE_latency <= latency_main)
# m.Equation(cin_IO_L1_in_latency <= latency_main)
# m.Equation(cin_IO_L2_in_latency <= latency_main)
# m.Equation(cin_IO_L3_in_latency <= latency_main)
# m.Equation(cout_IO_L1_in_latency <= latency_main)
# m.Equation(cout_IO_L1_out_latency <= latency_main)
# m.Equation(cout_IO_L2_in_latency <= latency_main)
# m.Equation(cout_IO_L2_out_latency <= latency_main)
# m.Equation(cout_IO_L3_in_latency <= latency_main)
# m.Equation(cout_IO_L3_out_latency <= latency_main)
# m.Equation(w_IO_L2_in_latency <= latency_main)
# m.Equation(w_IO_L3_in_latency <= latency_main)

latency = latency_prologue + latency_main + latency_epilogue

m.Equation(((r_t1/r_t2)*(c_t1/c_t2)) * i_t2 * 5 <= dsp_bound)

m.Equation(
	(4*8*1 / 36) * (((r_t2*c_t2)*o_t1)/1/512) * 1 * ((r_t1/r_t2)*(c_t1/c_t2)) + 
	(4*8*p14 / 36) * ((((((r_t2-1)+(p-1))+1)*(((c_t2-1)+(q-1))+1))*i_t1)/p14/512) * 2 * ((c_t1/c_t2)*(r_t1/r_t2)) + 
	(4*8*p15 / 36) * (((r_t2*c_t2)*o_t1)/p15/512) * 2 * ((c_t1/c_t2)*(r_t1/r_t2)) + 
	(4*8*p15 / 36) * (((r_t2*c_t2)*o_t1)/p15/512) * 2 * ((c_t1/c_t2)*(r_t1/r_t2)) + 
	(4*8*p17 / 36) * ((((o_t1*((p-1)+1))*((q-1)+1))*i_t1)/p17/512) * 2 * (c_t1/c_t2)
	<= bram_bound)

m.Equation(r_t1 >= 1)
m.Equation(r_t1 <= r)
m.Equation(c_t1 >= 1)
m.Equation(c_t1 <= c)
m.Equation(o_t1 >= 1)
m.Equation(o_t1 <= o)
m.Equation(i_t1 >= 1)
m.Equation(i_t1 <= i)
m.Equation(r_t2 >= 1)
m.Equation(r_t2 <= r_t1)
m.Equation(c_t2 >= 1)
m.Equation(c_t2 <= c_t1)
m.Equation(o_t2 >= 1)
m.Equation(o_t2 <= o_t1)
m.Equation(i_t2 >= 1)
m.Equation(i_t2 <= m.min2(i_t1,8))
m.Equation(p14 >= i_t2)
m.Equation(p14 <= m.max2(m.min2(i_t1,4),i_t2))
m.Equation(p15 >= 1)
m.Equation(p15 <= m.max2(m.min2(o_t1,4),1))
m.Equation(p16 >= 1)
m.Equation(p16 <= m.max2(m.min2(o_t1,4),1))
m.Equation(p17 >= i_t2)
m.Equation(p17 <= m.max2(m.min2(i_t1,16),i_t2))
m.Equation(	r_t2 * c_t2 * o_t2 >= i_t2 * 8)

m.Obj(latency)
m.solve(disp=False)
print(r, m.options.OBJFCNVAL)