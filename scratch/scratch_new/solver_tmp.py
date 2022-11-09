from gekko import GEKKO
import numpy as np

def get_solver_latency(problem_size, resource_limits, solver):
	m = GEKKO(remote=False)
	m.options.MAX_ITER = 10000

	bram_bound = int(resource_limits["BRAM18K"])
	dsp_bound = int(resource_limits["DSP"])

	q = problem_size["q"]
	p = problem_size["p"]
	o = problem_size["o"]
	r = problem_size["r"]
	c = problem_size["c"]
	i = problem_size["i"]
	c_t1 = m.Var(lb=1, ub=c, value=c)
	o_t1 = m.Var(lb=1, ub=o, value=o)
	r_t1 = m.Var(lb=1, ub=r, value=r)
	i_t1 = m.Var(lb=1, ub=i, value=i)
	c_t2 = m.Var(lb=1, ub=c_t1, value=c_t1)
	o_t2 = m.Var(lb=1, ub=o_t1, value=o_t1)
	r_t2 = m.Var(lb=1, ub=r_t1, value=r_t1)
	i_t2 = m.Var(lb=1, ub=i_t1, value=i_t1)
	p14 = m.Var(lb=1)
	p15 = m.Var(lb=1)
	p16 = m.Var(lb=1)
	p17 = m.Var(lb=1)

	cin_IO_L1_in_single_latency = ((c_t1/c_t2) * (((((((r_t1/r_t2)-1)*r_t2)+(r_t2-1))+(p-1))+1)*(((c_t2-1)+(q-1))+1)*i_t1/p14) + 1)
	cin_IO_L2_in_single_latency = (c_t1/c_t2) * (((((((r_t1/r_t2)-1)*r_t2)+(r_t2-1))+(p-1))+1)*(((c_t2-1)+(q-1))+1)*i_t1/i_t1*(20+i_t1/(512/8/4)))
	cout_IO_L1_in_single_latency = ((c_t1/c_t2) * (r_t1*c_t2*o_t1/p15) + 1)
	cout_IO_L2_in_single_latency = (c_t1/c_t2) * (r_t1*c_t2*o_t1/o_t1*(20+o_t1/(512/8/4)))
	w_IO_L2_in_single_latency = ((o_t1*((p-1)+1)*((q-1)+1)*i_t1/i_t1*(20+i_t1/(512/8/4))) + 1)

	latency_prologue = m.Var()

	m.Equation(cin_IO_L1_in_single_latency <= latency_prologue)
	m.Equation(cin_IO_L2_in_single_latency <= latency_prologue)
	m.Equation(cout_IO_L1_in_single_latency <= latency_prologue)
	m.Equation(cout_IO_L2_in_single_latency <= latency_prologue)
	m.Equation(w_IO_L2_in_single_latency <= latency_prologue)


	cout_IO_L1_out_single_latency = ((c_t1/c_t2) * (r_t1*c_t2*o_t1/p15) + 1)
	cout_IO_L2_out_single_latency = (c_t1/c_t2) * (r_t1*c_t2*o_t1/o_t1*(20+o_t1/(512/8/4)))

	latency_epilogue = m.Var()

	m.Equation(cout_IO_L1_out_single_latency <= latency_epilogue)
	m.Equation(cout_IO_L2_out_single_latency <= latency_epilogue)


	PE_latency = ((o/o_t1)) * ((i/i_t1)) * ((r/r_t1)) * ((c/c_t1)) * (1 + (o_t1/o_t2) * (r_t1/r_t2) * (i_t1/i_t2) * p * q * r_t2 * o_t2 * c_t2 * 1 + 1)
	cin_IO_L1_in_latency = ((o/o_t1)) * ((i/i_t1)) * ((r/r_t1)) * ((c/c_t1)) * (m.max2((c_t1/c_t2) * (((((((r_t1/r_t2)-1)*r_t2)+(r_t2-1))+(p-1))+1)*(((c_t2-1)+(q-1))+1)*i_t1/p14), (o_t1/o_t2) * (r_t1/r_t2) * (i_t1/i_t2) * p * q * r_t2 * o_t2 * c_t2 * 1) + 1)
	cin_IO_L2_in_latency = ((o/o_t1)) * ((i/i_t1)) * ((r/r_t1)) * ((c/c_t1)) * (c_t1/c_t2) * (((((((r_t1/r_t2)-1)*r_t2)+(r_t2-1))+(p-1))+1)*(((c_t2-1)+(q-1))+1)*i_t1/i_t1*(20+i_t1/(512/8/4)))
	cout_IO_L1_in_latency = ((o/o_t1)) * ((r/r_t1)) * ((c/c_t1)) * (m.max2((c_t1/c_t2) * (r_t1*c_t2*o_t1/p15), (o_t1/o_t2) * (r_t1/r_t2) * r_t2 * o_t2 * c_t2 * 1) + 1)
	cout_IO_L1_out_latency = ((o/o_t1)) * ((r/r_t1)) * ((c/c_t1)) * (m.max2((c_t1/c_t2) * (r_t1*c_t2*o_t1/p15), (o_t1/o_t2) * (r_t1/r_t2) * r_t2 * o_t2 * c_t2 * 1) + 1)
	cout_IO_L2_in_latency = ((o/o_t1)) * ((r/r_t1)) * ((c/c_t1)) * (c_t1/c_t2) * (r_t1*c_t2*o_t1/o_t1*(20+o_t1/(512/8/4)))
	cout_IO_L2_out_latency = ((o/o_t1)) * ((r/r_t1)) * ((c/c_t1)) * (c_t1/c_t2) * (r_t1*c_t2*o_t1/o_t1*(20+o_t1/(512/8/4)))
	w_IO_L2_in_latency = ((o/o_t1)) * ((i/i_t1)) * ((r/r_t1)) * ((c/c_t1)) * (m.max2((o_t1*((p-1)+1)*((q-1)+1)*i_t1/i_t1*(20+i_t1/(512/8/4))), (o_t1/o_t2) * (r_t1/r_t2) * (i_t1/i_t2) * p * q * r_t2 * o_t2 * c_t2 * 1) + 1)

	latency_main = m.Var()

	m.Equation(PE_latency <= latency_main)
	m.Equation(cin_IO_L1_in_latency <= latency_main)
	m.Equation(cin_IO_L2_in_latency <= latency_main)
	m.Equation(cout_IO_L1_in_latency <= latency_main)
	m.Equation(cout_IO_L1_out_latency <= latency_main)
	m.Equation(cout_IO_L2_in_latency <= latency_main)
	m.Equation(cout_IO_L2_out_latency <= latency_main)
	m.Equation(w_IO_L2_in_latency <= latency_main)


	latency = latency_prologue + latency_main + latency_epilogue

	m.Equation((c_t1/c_t2) * i_t2 * 5 <= dsp_bound)

	m.Equation(
	(4*8*1 / 36) * (((r_t1*c_t2)*o_t1)/1/512) * 1 * (c_t1/c_t2) + 
	(4*8*p14 / 36) * (((((((((r_t1/r_t2)-1)*r_t2)+(r_t2-1))+(p-1))+1)*(((c_t2-1)+(q-1))+1))*i_t1)/p14/512) * 2 * (c_t1/c_t2) + 
	(4*8*p15 / 36) * (((r_t1*c_t2)*o_t1)/p15/512) * 2 * (c_t1/c_t2) + 
	(4*8*p15 / 36) * (((r_t1*c_t2)*o_t1)/p15/512) * 2 * (c_t1/c_t2) + 
	(4*8*p17 / 36) * ((((o_t1*((p-1)+1))*((q-1)+1))*i_t1)/p17/512) * 2 * 1
	<= bram_bound)

	m.Equation(c_t1 >= 1)
	m.Equation(c_t1 <= c)
	m.Equation(o_t1 >= 1)
	m.Equation(o_t1 <= o)
	m.Equation(r_t1 >= 1)
	m.Equation(r_t1 <= r)
	m.Equation(i_t1 >= 1)
	m.Equation(i_t1 <= i)
	m.Equation(c_t2 >= 1)
	m.Equation(c_t2 <= c_t1)
	m.Equation(o_t2 >= 1)
	m.Equation(o_t2 <= o_t1)
	m.Equation(r_t2 >= 1)
	m.Equation(r_t2 <= r_t1)
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
	m.Equation(	c_t2 * o_t2 * r_t2 >= i_t2 * 8)

	try:
		m.Obj(latency)
		m.options.SOLVER = solver
		m.solve()
		return m.options.OBJFCNVAL
	except:
		return np.inf

def try_all_solvers(problem_size, resource_limits):
	solvers = {1:'APOPT', 2:'BOPOPT', 3:'IPOPT'}
	cycles = []
	for i in range(3):
		cycles.append(get_solver_latency(problem_size, resource_limits, i))
		print(f'{solvers[i+1]}: {cycles[i]}', end=' ')
	print()
	return min(cycles)