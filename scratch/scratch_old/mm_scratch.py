from utils import *
from kernel3_2 import *

def solver_lower_bound_mm(i_t0, j_t0, k_t0, solver):
	# generate tmp.mod
	solver_model = open(prj_path + '/scratch/solver/tmp.mod', 'w')
	design_path = 'kernel3_2.json'
	with open(design_path, 'r') as f:
		design_desc = json.load(f)
	print_latency_est_func(solver_model, design_desc, 'mm')
	solver_model.close()

	# generate tmp.dat
	with open(prj_path + '/scratch/solver/tmp.dat', 'w') as f:
		print(f'param i := {i_t0};', file = f)
		print(f'param j := {j_t0};', file = f)
		print(f'param k := {k_t0};', file = f)
		print(f'param dsp_bound := 8601;', file = f)
		print(f'param bram_bound := 3763;', file = f)
		print(f'param data_w := 32;', file = f)
	
	# generate tmp.run
	with open(prj_path + '/scratch/solver/tmp.run', 'w') as f:
		print(f'option solver {solver};', file = f)
		print(f"option ipopt_options 'max_iter=10000';", file = f)
		print(f'reset;', file = f)
		print(f'model /home/suhailb/Projects/odyssey/scratch/solver/tmp.mod;', file = f)
		print(f'data /home/suhailb/Projects/odyssey/scratch/solver/tmp.dat;', file = f)
		print(f'solve;', file = f)
		print(f'display target,i_t1,j_t1,k_t1,i_t2,j_t2,k_t2;', file = f)

	# run solver
	cmd = f'ampl solver/tmp.run | grep target'
	try:
		# run the command and get the output
		output = subprocess.check_output(cmd, shell=True)
		# convert the output to a string
		output = output.decode('utf-8')
		print(f'{solver}', output)
		# target = #, get the number
		target = float(output.split()[2])
		return target
	except:
		return np.inf

def run_latency_search(candidates, resource_limits, num_top_results):
	top_results = [{'cycles':[np.inf]}]*num_top_results
	for params in candidates:
		result = {}
		result['cycles'] = est_latency(params)
		result['resources'] = est_resource(params)
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

def get_mm_inner_candidates(candidates, i_t0, j_t0, k_t0):
	local_candidates = []
	for i_t1, j_t1, k_t1 in candidates:
		i_t2_candidates = [x for x in range(1, i_t1+1) if i_t1 % x == 0]
		j_t2_candidates = [x for x in range(1, j_t1+1) if j_t1 % x == 0]
		k_t2_candidates = [x for x in range(1, k_t1+1) if k_t1 % x == 0]
		for i_t2 in i_t2_candidates:
			for j_t2 in j_t2_candidates:
				for k_t2 in k_t2_candidates:
					params = {}
					params["i"] = i_t0
					params["j"] = j_t0
					params["k"] = k_t0
					params["i_t1"] = i_t1
					params["j_t1"] = j_t1
					params["k_t1"] = k_t1
					params["i_t2"] = i_t2
					params["j_t2"] = j_t2
					params["k_t2"] = k_t2
					params = infer_params(params)
					if not bound_check(params):
						continue
					local_candidates.append(params)
	return local_candidates

def get_mm_candidates(i_t0, j_t0, k_t0):
	candidates = []
	i_t1_candidates = [x for x in range(1, i_t0+1) if i_t0 % x == 0]
	j_t1_candidates = [x for x in range(1, j_t0+1) if j_t0 % x == 0]
	k_t1_candidates = [x for x in range(1, k_t0+1) if k_t0 % x == 0]
	for i_t1 in i_t1_candidates:
		for j_t1 in j_t1_candidates:
			for k_t1 in k_t1_candidates:
				candidates.append((i_t1, j_t1, k_t1))
	if len(candidates) >= 72:
		num_processes = int(multiprocessing.cpu_count() * 1)
	else:
		num_processes = len(candidates)

	chunks = list_split(candidates, num_processes)
	pool = multiprocessing.Pool(processes = num_processes)
	
	candidates = pool.starmap(get_mm_inner_candidates, [(chunk, i_t0, j_t0, k_t0) for chunk in chunks])
	pool.close()
	candidates = [item for sublist in candidates for item in sublist]
	return candidates

def search(candidates, top_results, resource_limits, num_top_results):
	if len(candidates) >= 72:
		num_processes = int(multiprocessing.cpu_count() * 1)
	elif len(candidates) == 0:
		return top_results
	else:
		num_processes = len(candidates)
	chunks = list_split(candidates, num_processes)
	pool = multiprocessing.Pool(processes = num_processes)
	results = pool.starmap(run_latency_search, [(chunk, resource_limits, num_top_results) for chunk in chunks])
	pool.close()
	results = [item for sublist in results for item in sublist]
	results = sorted(results, key=lambda x: x['cycles'][0])
	top_results.extend(results[:num_top_results])
	top_results = sorted(top_results, key=lambda x: x['cycles'][0])
	top_results = top_results[:num_top_results]
	
	return top_results

import multiprocessing
import subprocess

workload = sys.argv[1]
problem_size = eval(sys.argv[2])
problem_dims = [problem_size[key] for key in problem_size.keys()]
problem_dims_str = '_'.join([str(dim) for dim in problem_dims])

num_top_results = int(sys.argv[3])
u250_info = json.load(open(prj_path + '/data/cst/u250.json'))
resource_limits = {'DSP': u250_info['DSP']['total']*u250_info['DSP']['ratio'], 'BRAM18K': u250_info['BRAM18K']['total']*u250_info['BRAM18K']['ratio']}

I, J, K = problem_size['i'], problem_size['j'], problem_size['k']
i_padding = 0
j_padding = 20
k_padding = 0

results_path = prj_path + f'/scratch/results/mm_{problem_dims_str}'
csv_file = open(results_path + '.csv', 'w')
print(f'I, J, K, solver, actual', file=csv_file)
csv_file.close()
actual_cycles_list = []
solver_cycles_list = []

for i_t0 in range(I, I + 1 + i_padding):
	for j_t0 in range(J, J + 1 + j_padding):
		for k_t0 in range(K, K + 1 + k_padding):
			top_results = [{'cycles':[np.inf]}]*num_top_results
			candidates = get_mm_candidates(i_t0, j_t0, k_t0)
			top_results = search(candidates, top_results, resource_limits, num_top_results)
			actual_cycles = top_results[0]['cycles'][0]
			solver_cycles = solver_lower_bound_mm(i_t0, j_t0, k_t0, 'ipopt')
			with open(results_path + '.csv', 'a') as csv_file:
				print(f'{i_t0}, {j_t0}, {k_t0}, {solver_cycles}, {actual_cycles}', file=csv_file)
			csv_file.close()
			actual_cycles_list.append(actual_cycles)
			solver_cycles_list.append(solver_cycles)

import matplotlib.pyplot as plt
import matplotlib.pyplot as plt
plt.plot(range(J, J + 1 + j_padding), actual_cycles_list, label='actual')
plt.plot(range(J, J + 1 + j_padding), solver_cycles_list, label='solver')
# x axis
plt.xlabel('j')
# y axis
plt.ylabel('cycles')
plt.legend()
plt.savefig(results_path + '.png')

# solvers = [
# 	# 'conopt',
# 	# 'loqo',
# 	# 'minos',
# 	# 'snopt',
# 	'ipopt',
# 	# 'baron',
# 	# 'lgo',
# 	# 'lindo',
# 	# 'octeract'
# ]
# for solver in solvers:
# 	solver_cycles = solver_lower_bound_mm(I, J, K, solver)