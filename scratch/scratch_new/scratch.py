from gekko import GEKKO
import numpy as np

def est_resources(params):
	i = params['i']
	o = params['o']
	r = params['r']
	c = params['c']
	p = params['p']
	q = params['q']
	i_t1 = params['i_t1']
	o_t1 = params['o_t1']
	r_t1 = params['r_t1']
	c_t1 = params['c_t1']
	i_t2 = params['i_t2']
	o_t2 = params['o_t2']
	r_t2 = params['r_t2']
	c_t2 = params['c_t2']
	p14 = params['p14']
	p15 = params['p15']
	p16 = params['p16']
	p17 = params['p17']
	BRAMs = (4*8*1 / 36) * (((r_t2*c_t2)*o_t1)/1/512) * 1 * ((r_t1/r_t2)*(c_t1/c_t2)) + \
	(4*8*p14 / 36) * ((((((r_t2-1)+(p-1))+1)*(((c_t2-1)+(q-1))+1))*i_t1)/p14/512) * 2 * ((c_t1/c_t2)*(r_t1/r_t2)) + \
	(4*8*p15 / 36) * (((r_t2*c_t2)*o_t1)/p15/512) * 2 * ((c_t1/c_t2)*(r_t1/r_t2)) + \
	(4*8*p15 / 36) * (((r_t2*c_t2)*o_t1)/p15/512) * 2 * ((c_t1/c_t2)*(r_t1/r_t2)) + \
	(4*8*p17 / 36) * ((((o_t1*((p-1)+1))*((q-1)+1))*i_t1)/p17/512) * 2 * (c_t1/c_t2)
	DSPs = ((r_t1/r_t2)*(c_t1/c_t2)) * i_t2 * 5
	return {'BRAM18K': BRAMs, 'DSP': DSPs}
def get_solver_latency(problem_size, resource_limits, solver):
	m = GEKKO(remote=False)
	m.options.MAX_ITER = 100000

	bram_bound = int(resource_limits["BRAM18K"])
	dsp_bound = int(resource_limits["DSP"])

	q = problem_size["q"]
	p = problem_size["p"]
	o = problem_size["o"]
	r = problem_size["r"]
	c = problem_size["c"]
	i = problem_size["i"]
	r_t1 	= m.Var(lb=1, value=i, integer=True)
	c_t1 	= m.Var(lb=1, value=c, integer=True)
	o_t1 	= m.Var(lb=1, value=o, integer=True)
	i_t1 	= m.Var(lb=1, value=i, integer=True)
	r_t2 	= m.Var(lb=1, value=i, integer=True)
	c_t2 	= m.Var(lb=1, value=c, integer=True)
	o_t2 	= m.Var(lb=1, value=o, integer=True)
	i_t2 	= m.Var(lb=1, value=i, integer=True)
	p14 	= m.Var(lb=1)
	p15 	= m.Var(lb=1)
	p16 	= m.Var(lb=1)
	p17 	= m.Var(lb=1)

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
	m.Equation(	r_t2 * c_t2 * o_t2 >= i_t2 * 8)
	ci = m.Var(integer=True)
	m.Equation(i_t1 == ci*i_t2)
	co = m.Var(integer=True)
	m.Equation(o_t1 == co*o_t2)
	cr = m.Var(integer=True)
	m.Equation(r_t1 == cr*r_t2)
	cc = m.Var(integer=True)
	m.Equation(c_t1 == cc*c_t2)
	try:
		m.Obj(latency)
		m.options.SOLVER = solver
		m.solve(disp=False)
		params = {}
		params['i'] = i
		params['o'] = o
		params['r'] = r
		params['c'] = c
		params['p'] = p
		params['q'] = q
		params['i_t1'] = i_t1.value[0]
		params['o_t1'] = o_t1.value[0]
		params['r_t1'] = r_t1.value[0]
		params['c_t1'] = c_t1.value[0]
		params['r_t2'] = r_t2.value[0]
		params['c_t2'] = c_t2.value[0]
		params['o_t2'] = o_t2.value[0]
		params['i_t2'] = i_t2.value[0]
		params['p14'] = p14.value[0]
		params['p15'] = p15.value[0]
		params['p16'] = p16.value[0]
		params['p17'] = p17.value[0]
		return m.options.OBJFCNVAL, params
	except:
		return np.inf, None

def try_all_solvers(problem_size, resource_limits):
	solvers = {1:'APOPT', 2:'BPOPT', 3:'IPOPT'}
	cycles = []
	for i in range(3):
		cycle, params = get_solver_latency(problem_size, resource_limits, i+1)
		cycles.append(cycle)
		print(f'{solvers[i+1]}: {cycles[i]}')
		if params != None:
			print(params)
			print(resource_limits)
			print(est_resources(params))

	print()
	return min(cycles)
