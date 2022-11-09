from utils import *
# from kernel7_2 import *
from collections import OrderedDict
import itertools
def get_port_ub(i_t0, o_t0, r_t0, c_t0, term):
	max_bound = 0
	if 'i_t' in term:
		i_t1_candidates = [x for x in range(1, i_t0+1) if i_t0%x == 0]
		for i_t1 in i_t1_candidates:
			i_t2_candidates = [x for x in range(1, 8+1) if i_t1%x == 0]
			for i_t2 in i_t2_candidates:
				bound = eval(term)
				if bound > max_bound:
					max_bound = bound
		return max_bound
	elif 'o_t' in term:
		o_t1_candidates = [x for x in range(1, o_t0+1) if o_t0%x == 0]
		for o_t1 in o_t1_candidates:
			o_t2_candidates = [x for x in range(1, o_t1+1) if o_t1%x == 0]
			for o_t2 in o_t2_candidates:
				bound = eval(term)
				if bound > max_bound:
					max_bound = bound
		return max_bound
	elif 'r_t' in term:
		r_t1_candidates = [x for x in range(1, r_t0+1) if r_t0%x == 0]
		for r_t1 in r_t1_candidates:
			r_t2_candidates = [x for x in range(1, r_t1+1) if r_t1%x == 0]
			for r_t2 in r_t2_candidates:
				bound = eval(term)
				if bound > max_bound:
					max_bound = bound
		return max_bound
	elif 'c_t' in term:
		c_t1_candidates = [x for x in range(1, c_t0+1) if c_t0%x == 0]
		for c_t1 in c_t1_candidates:
			c_t2_candidates = [x for x in range(1, c_t1+1) if c_t1%x == 0]
			for c_t2 in c_t2_candidates:
				bound = eval(term)
				if bound > max_bound:
					max_bound = bound
		return max_bound

def get_port_candidates(i_t0, o_t0, r_t0, c_t0, design, constraints, ports_upper_bounds, alias_ports):
	candidates = []
	p14_ub = get_port_ub(i_t0, o_t0, r_t0, c_t0, ports_upper_bounds['p14'])
	p15_ub = get_port_ub(i_t0, o_t0, r_t0, c_t0, ports_upper_bounds['p15'])
	p16_ub = get_port_ub(i_t0, o_t0, r_t0, c_t0, ports_upper_bounds['p16'])
	p17_ub = get_port_ub(i_t0, o_t0, r_t0, c_t0, ports_upper_bounds['p17'])
	if 'p18' in ports_upper_bounds:
		p18_ub = get_port_ub(i_t0, o_t0, r_t0, c_t0, ports_upper_bounds['p18'])
	else:
		p18_ub = 1

	# p14_cnt, p15_cnt, p16_cnt, p17_cnt, p18_cnt = 0, 0, 0, 0, 0
	# with open(prj_path + '/scratch/tmp/designs/' + design, 'r') as f:
	# 	lines = f.readlines()
	# 	for line in lines:
	# 		if 'p14' in line:
	# 			p14_cnt += 1
	# 		elif 'p15' in line:
	# 			p15_cnt += 1
	# 		elif 'p16' in line:
	# 			p16_cnt += 1
	# 		elif 'p17' in line:
	# 			p17_cnt += 1
	# 		elif 'p18' in line:
	# 			p18_cnt += 1
	# port_counts = {'p14': p14_cnt, 'p15': p15_cnt, 'p16': p16_cnt, 'p17': p17_cnt, 'p18': p18_cnt}
	port_ubs = {'p14': p14_ub, 'p15': p15_ub, 'p16': p16_ub, 'p17': p17_ub, 'p18': p18_ub}
	# print('port_ubs: ', port_ubs)
	# print('alias_ports: ', alias_ports)
	solver_vars = []
	solver_consts = []
	other_vars = []
	other_consts = []
	vars = []
	consts = []
	for port in port_ubs.keys():
		is_const = False
		for alias in alias_ports:
			if port == alias[1]:
				consts.append((port, port_ubs[port]))
				is_const = True
		if not is_const:
			vars.append((port, port_ubs[port]))

	# sort var tuples by their upper bound
	vars = sorted(vars, key=lambda x: x[1], reverse=True)

	solver_vars = vars[:2]
	other_vars = vars[2:]
	for var in solver_vars:
		for alias in alias_ports:
			if var[0] == alias[0]:
				solver_consts.append((alias[1], alias[0]))
	for var in other_vars:
		for alias in alias_ports:
			if var[0] == alias[0]:
				other_consts.append((alias[1], alias[0]))
	
	return solver_vars, solver_consts, other_vars, other_consts

def get_other_candidates(vars, consts):
	candidates = []
	port_list = [x[0] for x in vars]
	candidate_list = []
	for var in vars:
		# power of 2 less or equal to the upper bound
		candidate_list.append([x for x in range(1, var[1]+1) if var[1]%x == 0])
	# generate all combinations
	candidate_list = list(itertools.product(*candidate_list))
	for candidate in candidate_list:
		candidate_dict = {}
		for i in range(len(candidate)):
			candidate_dict[port_list[i]] = candidate[i]
		candidates.append(candidate_dict)
	
	# add consts
	for const in consts:
		for candidate in candidates:
			candidate[const[0]] = candidate[const[1]]
		
	return candidates

def solver_lower_bound_conv(i_t0, o_t0, r_t0, c_t0, p_t0, q_t0, design, problem_size, resource_limits):
	design_path = prj_path + '/scratch/tmp/designs/' + design
	with open(design_path, 'r') as f:
		design_desc = json.load(f)
	port_params = []
	for param in design_desc['params']:
		if param['attr'] == 'data_pack_factor':
			port_params.append(param)
	
	alias_ports = []
	for i in range(len(port_params)):
		param1 = port_params[i]
		for j in range(i+1, len(port_params)):
			param2 = port_params[j]
			if param1['bounds'] == param2['bounds'] and param1['name'] != param2['name']:
				alias_ports.append((param1['name'], param2['name']))

	ports_upper_bounds = {}
	for p in design_desc["params"]:
		if 'data_pack_factor' == p["attr"]:
			ports_upper_bounds[p['name']] = p['bounds'][1]
	# convert ports_upper_bounds to an ordered dict
	ports_upper_bounds = OrderedDict(sorted(ports_upper_bounds.items(), key=lambda x: x[0]))
	ports_of_same_ub = []
	for i in range(len(ports_upper_bounds)):
		ub1 = ports_upper_bounds[list(ports_upper_bounds.keys())[i]]
		for j in range(i+1, len(ports_upper_bounds)):
			ub2 = ports_upper_bounds[list(ports_upper_bounds.keys())[j]]
			if ub1 == ub2:
				ports_of_same_ub.append([list(ports_upper_bounds.keys())[i], list(ports_upper_bounds.keys())[j]])
	solver_vars, solver_consts, other_vars, other_consts = get_port_candidates(i_t0, o_t0, r_t0, c_t0, design, ports_of_same_ub, ports_upper_bounds, alias_ports)
	candidates = get_other_candidates(other_vars, other_consts)
	min_cycles = np.inf
	for other_ports in candidates:

		with open(prj_path + '/scratch/solver/tmp.dat', 'w') as f:
			print_data(f, design_desc, problem_size, resource_limits, other_ports)
		
		# generate tmp.mod
		with open(prj_path + '/scratch/solver/tmp.mod', 'w') as f:
			print_model(f, design_desc, problem_size, resource_limits, solver_vars, solver_consts, other_ports)

		# generate tmp.run
		with open(prj_path + '/scratch/solver/tmp.run', 'w') as f:
			print(f'option solver lgo;', file = f)
			# print(f"option ipopt_options 'max_iter=10000';", file = f)
			print(f'reset;', file = f)
			print(f'model /home/suhailb/Projects/odyssey/scratch/solver/tmp.mod;', file = f)
			print(f'data /home/suhailb/Projects/odyssey/scratch/solver/tmp.dat;', file = f)
			print(f'solve;', file = f)
			print(f'display target,i_t1,o_t1,r_t1,c_t1,i_t2,o_t2,r_t2,c_t2;', file = f)

		# run solver
		cmd = f'ampl solver/tmp.run | grep target'
		# run the command and get the output
		output = subprocess.check_output(cmd, shell=True)
		# convert the output to a string
		output = output.decode('utf-8')
		# target = #, get the number
		target = float(output.split()[2])
		if target < min_cycles:
			min_cycles = target
	return min_cycles

def solver_lower_bound_conv_ipopt(i_t0, o_t0, r_t0, c_t0, p_t0, q_t0, design, problem_size, resource_limits):
	design_path = prj_path + '/scratch/tmp/designs/' + design
	with open(design_path, 'r') as f:
		design_desc = json.load(f)
	port_params = []
	for param in design_desc['params']:
		if param['attr'] == 'data_pack_factor':
			port_params.append(param)
	
	alias_ports = []
	for i in range(len(port_params)):
		param1 = port_params[i]
		for j in range(i+1, len(port_params)):
			param2 = port_params[j]
			if param1['bounds'] == param2['bounds'] and param1['name'] != param2['name']:
				alias_ports.append((param1['name'], param2['name']))

	ports_upper_bounds = {}
	for p in design_desc["params"]:
		if 'data_pack_factor' == p["attr"]:
			ports_upper_bounds[p['name']] = p['bounds'][1]
	# convert ports_upper_bounds to an ordered dict
	ports_upper_bounds = OrderedDict(sorted(ports_upper_bounds.items(), key=lambda x: x[0]))
	ports_of_same_ub = []
	for i in range(len(ports_upper_bounds)):
		ub1 = ports_upper_bounds[list(ports_upper_bounds.keys())[i]]
		for j in range(i+1, len(ports_upper_bounds)):
			ub2 = ports_upper_bounds[list(ports_upper_bounds.keys())[j]]
			if ub1 == ub2:
				ports_of_same_ub.append([list(ports_upper_bounds.keys())[i], list(ports_upper_bounds.keys())[j]])
	
	p14_ub = get_port_ub(i_t0, o_t0, r_t0, c_t0, ports_upper_bounds['p14'])
	p15_ub = get_port_ub(i_t0, o_t0, r_t0, c_t0, ports_upper_bounds['p15'])
	p16_ub = get_port_ub(i_t0, o_t0, r_t0, c_t0, ports_upper_bounds['p16'])
	p17_ub = get_port_ub(i_t0, o_t0, r_t0, c_t0, ports_upper_bounds['p17'])
	if 'p18' in ports_upper_bounds:
		p18_ub = get_port_ub(i_t0, o_t0, r_t0, c_t0, ports_upper_bounds['p18'])
	else:
		p18_ub = 1
	solver_vars = [
		('p14', p14_ub),
		('p15', p15_ub),
		('p16', p16_ub),
		('p17', p17_ub),
		('p18', p18_ub)
	]
	solver_consts = []
	other_ports = {}

	with open(prj_path + '/scratch/solver/tmp.dat', 'w') as f:
			print_data(f, design_desc, problem_size, resource_limits, other_ports)
		
	# generate tmp.mod
	with open(prj_path + '/scratch/solver/tmp.mod', 'w') as f:
		print_model(f, design_desc, problem_size, resource_limits, solver_vars, solver_consts, other_ports)

	# generate tmp.run
	with open(prj_path + '/scratch/solver/tmp.run', 'w') as f:
		print(f'option solver ipopt;', file = f)
		print(f"option ipopt_options 'max_iter=10000';", file = f)
		print(f'reset;', file = f)
		print(f'model /home/suhailb/Projects/odyssey/scratch/solver/tmp.mod;', file = f)
		print(f'data /home/suhailb/Projects/odyssey/scratch/solver/tmp.dat;', file = f)
		print(f'solve;', file = f)
		print(f'display target,i_t1,o_t1,r_t1,c_t1,i_t2,o_t2,r_t2,c_t2;', file = f)

	# run solver
	cmd = f'ampl solver/tmp.run | grep target'
	# run the command and get the output
	output = subprocess.check_output(cmd, shell=True)
	# convert the output to a string
	output = output.decode('utf-8')
	# target = #, get the number
	target = float(output.split()[2])
	return target

def run_latency_search(candidates, resource_limits, num_top_results, design):
	local_candidates = []
	design_name = design.strip('.json')
	file_path = 'tmp/designs/register/' + design_name
	file_path = file_path.replace('/', '.')
	perf_model = importlib.import_module(file_path)
	
	top_results = [{'cycles':[np.inf]}]*num_top_results
	for params in candidates:
		result = {}
		result['cycles'] = perf_model.est_latency(params)
		result['resources'] = perf_model.est_resource(params)
		result['params'] = params
		if result['resources'][0]['DSP'] > resource_limits['DSP'] or result['resources'][0]['BRAM18K'] > resource_limits['BRAM18K']:
			continue

		if result['cycles'][0] < top_results[-1]['cycles'][0]:
			for j in range(num_top_results):
				if result['cycles'][0] < top_results[j]['cycles'][0]:
					# insert result into results
					top_results.insert(j, result)
					# remove last element
					top_results.pop()
					break
	return top_results

def get_conv_inner_candidates(candidates, i_t0, o_t0, r_t0, c_t0, p_t0, q_t0, design):
	design_name = design.strip('.json')
	file_path = 'tmp/designs/register/' + design_name
	file_path = file_path.replace('/', '.')
	perf_model = importlib.import_module(file_path)

	local_candidates = []
	for i_t1, o_t1, r_t1, c_t1 in candidates:
		i_t2_candidates = [x for x in range(1, i_t1+1) if i_t1 % x == 0]
		o_t2_candidates = [x for x in range(1, o_t1+1) if o_t1 % x == 0]
		r_t2_candidates = [x for x in range(1, r_t1+1) if r_t1 % x == 0]
		c_t2_candidates = [x for x in range(1, c_t1+1) if c_t1 % x == 0]
		for i_t2 in i_t2_candidates:
			for o_t2 in o_t2_candidates:
				for r_t2 in r_t2_candidates:
					for c_t2 in c_t2_candidates:
						params = {}
						params["i"] = i_t0
						params["o"] = o_t0
						params["r"] = r_t0
						params["c"] = c_t0
						params["p"] = p_t0
						params["q"] = q_t0
						params["i_t1"] = i_t1
						params["o_t1"] = o_t1
						params["r_t1"] = r_t1
						params["c_t1"] = c_t1
						params["i_t2"] = i_t2
						params["o_t2"] = o_t2
						params["r_t2"] = r_t2
						params["c_t2"] = c_t2
						# params["p14"] = 4
						# params["p15"] = 4
						# params["p16"] = 4
						# params["p17"] = 16
						# params["p18"] = 1
						params = perf_model.infer_params(params)
						if not perf_model.bound_check(params):
							continue
						local_candidates.append(params)
	return local_candidates

def get_conv_candidates(i_t0, o_t0, r_t0, c_t0, p_t0, q_t0, design):
	candidates = []
	i_t1_candidates = [x for x in range(1, i_t0+1) if i_t0 % x == 0]
	o_t1_candidates = [x for x in range(1, o_t0+1) if o_t0 % x == 0]
	r_t1_candidates = [x for x in range(1, r_t0+1) if r_t0 % x == 0]
	c_t1_candidates = [x for x in range(1, c_t0+1) if c_t0 % x == 0]
	for i_t1 in i_t1_candidates:
		for o_t1 in o_t1_candidates:
			for r_t1 in r_t1_candidates:
				for c_t1 in c_t1_candidates:
					candidates.append((i_t1, o_t1, r_t1, c_t1))
	num_processes = int(multiprocessing.cpu_count() * 1)
	chunks = list_split(candidates, num_processes)
	pool = multiprocessing.Pool(processes = num_processes)
	candidates = pool.starmap(get_conv_inner_candidates, [(chunk, i_t0, o_t0, r_t0, c_t0, p_t0, q_t0, design) for chunk in chunks])
	pool.close()
	candidates = [item for sublist in candidates for item in sublist]
	return candidates

def search(candidates, top_results, resource_limits, num_top_results, design):
	if len(candidates) >= 72:
		num_processes = int(multiprocessing.cpu_count() * 1)
	elif len(candidates) == 0:
		return top_results
	else:
		num_processes = len(candidates)
	chunks = list_split(candidates, num_processes)
	pool = multiprocessing.Pool(processes = num_processes)
	results = pool.starmap(run_latency_search, [(chunk, resource_limits, num_top_results, design) for chunk in chunks])
	pool.close()
	results = [item for sublist in results for item in sublist]
	results = sorted(results, key=lambda x: x['cycles'][0])
	top_results.extend(results[:num_top_results])
	top_results = sorted(top_results, key=lambda x: x['cycles'][0])
	top_results = top_results[:num_top_results]
	
	return top_results

def gen_perf_model(design, workload):
	design_name = design.strip('.json')
	file_path = 'tmp/designs/register/' + design_name
	file_path = file_path.replace('/', '.')
	# os.system(f'rm -rf {designs_dir}/*')
	copy_design(design, workload)
	os.makedirs(f'tmp/designs/register', exist_ok=True)
	# generate performance model
	with open(f'{designs_dir}/{design}', 'r') as f:
		design_desc = json.load(f)
		Design(design_name).register(design_desc, f"tmp/designs/register/{design_name}.py")
	return design_desc

import multiprocessing
import subprocess
import sys
sys.path.append('../src')
from design import Design

workload = sys.argv[1]

problem_size = eval(sys.argv[2])
problem_dims = [problem_size[key] for key in problem_size.keys()]
problem_dims_str = '_'.join([str(dim) for dim in problem_dims])

num_top_results = 1

u250_info = json.load(open(prj_path + '/data/cst/u250.json'))
resource_limits = {'DSP': u250_info['DSP']['total']*u250_info['DSP']['ratio'], 'BRAM18K': u250_info['BRAM18K']['total']*u250_info['BRAM18K']['ratio']}

designs = os.listdir(f'{designs_lib_dir}/{workload}')
designs.sort()

padding = 20
padding -= 1

if len(sys.argv) > 3:
	design_idx = int(sys.argv[3])
	first_design = design_idx
	last_design = design_idx + 1
else:
	first_design = 0
	last_design = len(designs)

for d_idx in range(first_design, last_design):
	design = designs[d_idx]

	design_desc = gen_perf_model(design, workload)

	sa_dims = design_desc['compute']['PE']['dims']
	sa_simd = design_desc['compute']['PE']['unroll_factor'][0]
	paddable_dims = []
	for dim in sa_dims:
		if sa_simd != dim[1]:
			paddable_dims.append(dim[1])

	I, O, R, C, P, Q = problem_size['i'], problem_size['o'], problem_size['r'], problem_size['c'], problem_size['p'], problem_size['q']
	paddings = {}
	
	for param in problem_size:
		if len(paddable_dims) > 0 and param == paddable_dims[0]:
			paddings[param] = padding
		else:
			paddings[param] = 0

	design_name = design.strip('.json')
	results_path = prj_path + f'/scratch/results/conv_{design_name}_{problem_dims_str}'
	csv_file = open(results_path + '.csv', 'w')
	print(f'I, O, R, C, P, Q, solver, actual', file=csv_file)
	csv_file.close()
	actual_cycles_list = []
	solver_cycles_list = []
	for i_t0 in range(I, I + 1 + paddings['i']):
		for o_t0 in range(O, O + 1 + paddings['o']):
			for r_t0 in range(R, R + 1 + paddings['r']):
				for c_t0 in range(C, C + 1 + paddings['c']):
					p_t0, q_t0 = P + paddings['p'], Q + paddings['q']
					padded_problem_size = {}
					padded_problem_size['i'] = i_t0
					padded_problem_size['o'] = o_t0
					padded_problem_size['r'] = r_t0
					padded_problem_size['c'] = c_t0
					padded_problem_size['p'] = p_t0
					padded_problem_size['q'] = q_t0
					top_results = [{'cycles':[np.inf]}]*num_top_results
					candidates = get_conv_candidates(i_t0, o_t0, r_t0, c_t0, p_t0, q_t0, design)
					top_results = search(candidates, top_results, resource_limits, num_top_results, design)
					# print(top_results[0]['params'])
					actual_cycles = top_results[0]['cycles'][0]
					solver_cycles = 0#solver_lower_bound_conv_ipopt(i_t0, o_t0, r_t0, c_t0, p_t0, q_t0, design, padded_problem_size, resource_limits)
					with open(results_path + '.csv', 'a') as csv_file:
						print(f'{i_t0}, {o_t0}, {r_t0}, {c_t0}, {p_t0}, {q_t0}, {solver_cycles}, {actual_cycles}', file=csv_file)
					csv_file.close()
					actual_cycles_list.append(actual_cycles)
					solver_cycles_list.append(solver_cycles)

	if len(paddable_dims) > 0:
		bound = problem_size[paddable_dims[0]]
		import matplotlib.pyplot as plt
		# plt.plot(range(bound, bound + 1 + padding), actual_cycles_list, label='actual')
		plt.plot(range(bound, bound + 1 + padding), solver_cycles_list, label='solver')
		# x axis
		plt.xlabel(paddable_dims[0])
		# y axis
		plt.ylabel('cycles')
		plt.legend()
		# clear the plot
		plt.savefig(results_path + '.png')
		plt.clf()
