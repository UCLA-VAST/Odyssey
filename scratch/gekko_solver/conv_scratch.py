from utils import *

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
	design_name = design.strip('.json')
	file_path = 'tmp/designs/register/' + design_name
	file_path = file_path.replace('/', '.')
	print(file_path)
	perf_model = importlib.import_module(file_path)
	exit()
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
	results_path = prj_path + f'/gekko_solver/results/conv_{design_name}_{problem_dims_str}'
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
					# top_results = search(candidates, top_results, resource_limits, num_top_results, design)
					# actual_cycles = top_results[0]['cycles'][0]
					# solver_cycles = 0
					# with open(results_path + '.csv', 'a') as csv_file:
					# 	print(f'{i_t0}, {o_t0}, {r_t0}, {c_t0}, {p_t0}, {q_t0}, {solver_cycles}, {actual_cycles}', file=csv_file)
					# csv_file.close()
					# actual_cycles_list.append(actual_cycles)
					# solver_cycles_list.append(solver_cycles)
	exit()
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
