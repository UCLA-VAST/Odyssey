from gekko import GEKKO

bram_bound = 3763
dsp_bound = 8601

def get_latencies(I, O, R, C, P, Q, padding):
  latencies = []
  for pad in range(padding):
    m = GEKKO()
    i = I
    o = O
    r = R + pad
    c = C
    p = P
    q = Q
    i_t1 = m.Var(lb=1, ub=i, value=i)
    o_t1 = m.Var(lb=1, ub=o, value=o)
    r_t1 = m.Var(lb=1, ub=r, value=r)
    c_t1 = m.Var(lb=1, ub=c, value=c)
    i_t2 = m.Var(lb=1, ub=i, value=1)
    o_t2 = m.Var(lb=1, ub=o, value=1)
    r_t2 = m.Var(lb=1, ub=r, value=1)
    c_t2 = m.Var(lb=1, ub=c, value=1)
    p14 = m.Var(lb=1, ub=16)
    p15 = m.Var(lb=1, ub=4)
    p16 = m.Var(lb=1, ub=4)
    p17 = m.Var(lb=1, ub=16)

    cin_IO_L1_in_single_latency = ((r_t1/r_t2) * ((((r_t2-1)+(p-1))+1)*(((c_t2-1)+(q-1))+1)*i_t1/p14) + 1)
    cin_IO_L2_in_single_latency = (c_t1/c_t2) * (r_t1/r_t2) * ((((r_t2-1)+(p-1))+1)*(((c_t2-1)+(q-1))+1)*i_t1/p14)
    cin_IO_L3_in_single_latency = (c_t1/c_t2) * (r_t1/r_t2) * ((((r_t2-1)+(p-1))+1)*(((c_t2-1)+(q-1))+1)*i_t1/i_t1*(20+i_t1/(512/8/4)))
    cout_IO_L1_in_single_latency = ((r_t1/r_t2) * (r_t2*c_t2*o_t1/p15) + 1)
    cout_IO_L2_in_single_latency = (c_t1/c_t2) * (r_t1/r_t2) * (r_t2*c_t2*o_t1/p15)
    cout_IO_L3_in_single_latency = (c_t1/c_t2) * (r_t1/r_t2) * (r_t2*c_t2*o_t1/o_t1*(20+o_t1/(512/8/4)))
    w_IO_L2_in_single_latency = ((c_t1/c_t2) * (o_t1*((p-1)+1)*((q-1)+1)*i_t1/p17) + 1)
    w_IO_L3_in_single_latency = (c_t1/c_t2) * (o_t1*((p-1)+1)*((q-1)+1)*i_t1/i_t1*(20+i_t1/(512/8/4)))

    latency_prologue = m.Var()
    
    m.Equation(cin_IO_L1_in_single_latency <= latency_prologue)
    m.Equation(cin_IO_L2_in_single_latency <= latency_prologue)
    m.Equation(cin_IO_L3_in_single_latency <= latency_prologue)
    m.Equation(cout_IO_L1_in_single_latency <= latency_prologue)
    m.Equation(cout_IO_L2_in_single_latency <= latency_prologue)
    m.Equation(cout_IO_L3_in_single_latency <= latency_prologue)
    m.Equation(w_IO_L2_in_single_latency <= latency_prologue)
    m.Equation(w_IO_L3_in_single_latency <= latency_prologue)
    
    cout_IO_L1_out_single_latency = ((r_t1/r_t2) * (r_t2*c_t2*o_t1/p15) + 1)
    cout_IO_L2_out_single_latency = (c_t1/c_t2) * (r_t1/r_t2) * (r_t2*c_t2*o_t1/p15)
    cout_IO_L3_out_single_latency = (c_t1/c_t2) * (r_t1/r_t2) * (r_t2*c_t2*o_t1/o_t1*(20+o_t1/(512/8/4)))

    latency_epilogue = m.Var()

    m.Equation(cout_IO_L1_out_single_latency <= latency_epilogue)
    m.Equation(cout_IO_L2_out_single_latency <= latency_epilogue)
    m.Equation(cout_IO_L3_out_single_latency <= latency_epilogue)

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

    latency_main = m.Var()

    m.Equation(PE_latency <= latency_main)
    m.Equation(cin_IO_L1_in_latency <= latency_main)
    m.Equation(cin_IO_L2_in_latency <= latency_main)
    m.Equation(cin_IO_L3_in_latency <= latency_main)
    m.Equation(cout_IO_L1_in_latency <= latency_main)
    m.Equation(cout_IO_L1_out_latency <= latency_main)
    m.Equation(cout_IO_L2_in_latency <= latency_main)
    m.Equation(cout_IO_L2_out_latency <= latency_main)
    m.Equation(cout_IO_L3_in_latency <= latency_main)
    m.Equation(cout_IO_L3_out_latency <= latency_main)
    m.Equation(w_IO_L2_in_latency <= latency_main)
    m.Equation(w_IO_L3_in_latency <= latency_main)

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
    m.Equation(r_t2 * c_t2 * o_t2 >= i_t2 * 8)


    m.Obj(latency)
    m.options.SOLVER = 1
    m.options.MAX_ITER = 100000
    m.solve(disp=False)
    print(r, m.options.OBJFCNVAL)
    latencies.append(m.options.OBJFCNVAL)
  return latencies

from matplotlib import pyplot as plt
dim = 64
I, O, R, C, P, Q = dim, dim, dim, dim, 3, 3
padding = 1
latencies = get_latencies(I, O, R, C, P, Q, padding)
plt.plot(latencies)
# plt.show()
plt.savefig('latencies.png')
