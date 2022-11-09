import os
import numpy as np
import json
import argparse
import copy
import multiprocessing
import subprocess
import time
import itertools
import matplotlib.pyplot as plt
import pandas as pd
import sys
from tqdm import tqdm
import random
import re
from math import ceil
from math import prod
import importlib
sys.path.append('../src')
from design import Design
from utils import *
from itertools import count

def get_solution_info(results, design, workload, problem_size):
	design_name = design.strip('.json')
	file_path = 'tmp/designs/register/' + design_name
	file_path = file_path.replace('/', '.')
	perf_model = importlib.import_module(file_path)
	dw = 4
	fre = 300
	solutions = []
	for result in results:
		solution = {}
		params = result['params']
		resources = result['resources'][0]
		cycles = result['cycles'][0]
		activity = perf_model.est_activity(params)
		ops = compute_ops(workload, problem_size)
		solution['arch_sol'] = params
		solution['DSPs'] = resources['DSP']
		solution['BRAMs'] = resources['BRAM18K']
		solution['cycles'] = cycles
		solution['dsp_eff'] = compute_dsp_eff(cycles, workload, problem_size, resources['DSP'])*100
		solution['fre'] = fre
		solution['latency'] = cycles/(fre*1e6)
		solution['throughput'] = (ops/1e9)/(cycles/(fre*1e6))
		solution['off_chip_bytes'] = activity['off_chip_acc_num']*4 #bytes
		solution['bandwidth'] = compute_bw(params, cycles, activity['off_chip_acc_num'], dw, fre)
		solution['CTC'] = compute_ctc(params, workload, problem_size, activity['off_chip_acc_num'], dw)
		solution['cycles_details'] = result['cycles'][1]
		solutions.append(solution)
	return solutions

def search_mm(I, J, K, id, candidates, design, resource_limits, num_top_results, sa_info, objective, workload):
	design_name = design.strip('.json')
	file_path = 'tmp/designs/register/' + design_name
	file_path = file_path.replace('/', '.')
	perf_model = importlib.import_module(file_path)
	top_results = [{'cycles':[np.inf]}]*num_top_results
	cnt = 0
	for idx in tqdm(range(len(candidates))):
		i_t1, j_t1, k_t1 = candidates[idx]
		i_t2_candidates = [i for i in range(1, i_t1+1) if i_t1 % i == 0]
		j_t2_candidates = [j for j in range(1, j_t1+1) if j_t1 % j == 0]
		k_t2_candidates = [k for k in range(1, k_t1+1) if k_t1 % k == 0]
		for i_t2 in i_t2_candidates:
			for j_t2 in j_t2_candidates:
				for k_t2 in k_t2_candidates:
					params = {}
					params["i"] = ceil(I / i_t1) * i_t1
					params["j"] = ceil(J / j_t1) * j_t1
					params["k"] = ceil(K / k_t1) * k_t1
					params["i_t1"] = i_t1
					params["j_t1"] = j_t1
					params["k_t1"] = k_t1
					params["i_t2"] = i_t2
					params["j_t2"] = j_t2
					params["k_t2"] = k_t2
					params = perf_model.infer_params(params)
					if not perf_model.bound_check(params):
						continue
					result = {}
					result['resources'] = perf_model.est_resource(params)
					if result['resources'][0]['DSP'] > resource_limits['DSP'] or result['resources'][0]['BRAM18K'] > resource_limits['BRAM18K']:
						continue
					result['cycles'] = perf_model.est_latency(params)
					result['params'] = params
					if result['cycles'][0] < top_results[-1]['cycles'][0]:
						for j in range(num_top_results):
							if result['cycles'][0] < top_results[j]['cycles'][0]:
								# insert result into results
								top_results.insert(j, result)
								# remove last element
								top_results.pop()
								break
	return top_results

def search_conv(I, O, R, C, P, Q, id, candidates, design, resource_limits, num_top_results, sa_info, objective, workload):
	design_name = design.strip('.json')
	file_path = 'tmp/designs/register/' + design_name
	file_path = file_path.replace('/', '.')
	perf_model = importlib.import_module(file_path)
	top_results = [{'cycles':[np.inf]}]*num_top_results
	for idx in tqdm(range(len(candidates))):
		i_t1, o_t1, r_t1, c_t1 = candidates[idx]
		i_t2_candidates = [i for i in range(1, i_t1+1) if i_t1 % i == 0]
		o_t2_candidates = [o for o in range(1, o_t1+1) if o_t1 % o == 0]
		r_t2_candidates = [r for r in range(1, r_t1+1) if r_t1 % r == 0]
		c_t2_candidates = [c for c in range(1, c_t1+1) if c_t1 % c == 0]
		for i_t2 in i_t2_candidates:
			for o_t2 in o_t2_candidates:
				for r_t2 in r_t2_candidates:
					for c_t2 in c_t2_candidates:
						params = {}
						params["i"] = ceil(I / i_t1) * i_t1
						params["o"] = ceil(O / o_t1) * o_t1
						params["r"] = ceil(R / r_t1) * r_t1
						params["c"] = ceil(C / c_t1) * c_t1
						params["p"] = P
						params["q"] = Q
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
						result = {}
						result['resources'] = perf_model.est_resource(params)
						if result['resources'][0]['DSP'] > resource_limits['DSP'] or result['resources'][0]['BRAM18K'] > resource_limits['BRAM18K']:
							continue
						result['cycles'] = perf_model.est_latency(params)
						result['params'] = params
						if result['cycles'][0] < top_results[-1]['cycles'][0]:
							for j in range(num_top_results):
								if result['cycles'][0] < top_results[j]['cycles'][0]:
									# insert result into results
									top_results.insert(j, result)
									# remove last element
									top_results.pop()
									break
	return top_results

def search(design, objective, workload, problem_size, num_top_results):
	design_name = design.strip('.json')
	file_path = 'tmp/designs/register/' + design_name
	file_path = file_path.replace('/', '.')
	os.system(f'rm -rf {designs_dir}/*')
	copy_design(design, workload)
	os.makedirs(f'tmp/designs/register', exist_ok=True)
	# generate performance model
	with open(f'{designs_dir}/{design}', 'r') as f:
		design_desc = json.load(f)
		Design(design_name).register(design_desc, f"tmp/designs/register/{design_name}.py")
	# load perf model
	perf_model = importlib.import_module(file_path)
	sa_dims = design_desc['compute']['PE']['dims']
	sa_simd = design_desc['compute']['PE']['unroll_factor'][0]
	paddable_dims = []
	for dim in sa_dims:
		if sa_simd != dim[1]:
			paddable_dims.append(dim[1])

	u250_info = json.load(open(prj_path + '/data/cst/u250.json'))
	resource_limits = {'DSP': u250_info['DSP']['total']*u250_info['DSP']['ratio'], 'BRAM18K': u250_info['BRAM18K']['total']*u250_info['BRAM18K']['ratio']}

	sa_info = get_SA_info(design)
	
	top_results = [{'cycles':[np.inf]}]*num_top_results
	
	if workload == 'mm':
		I = problem_size['i']
		J = problem_size['j']
		K = problem_size['k']
		i_t0, j_t0, k_t0 = I, J, K
		candidates = []
		i_t1_candidates = [i for i in range(1, 2*i_t0)] if 'i' in paddable_dims else [i for i in range(1, i_t0+1) if i_t0 % i == 0]
		j_t1_candidates = [j for j in range(1, 2*j_t0)] if 'j' in paddable_dims else [j for j in range(1, j_t0+1) if j_t0 % j == 0]
		k_t1_candidates = [k for k in range(1, 2*k_t0)] if 'k' in paddable_dims else [k for k in range(1, k_t0+1) if k_t0 % k == 0]
		for i_t1 in i_t1_candidates:
			for j_t1 in j_t1_candidates:
				for k_t1 in k_t1_candidates:
					candidates.append((i_t1, j_t1, k_t1))
		# shuffle candidates
		random.shuffle(candidates)
		print('Generated %d candidates' % len(candidates))
		num_processes = int(multiprocessing.cpu_count() * 1)
		print('Parallelizing using %d processes...' % (num_processes))
		chunks = list_split(candidates, num_processes)
		pool = multiprocessing.Pool(processes = num_processes)
		results = pool.starmap(search_mm, [(i_t0, j_t0, k_t0, idx, chunk, design, resource_limits, num_top_results, sa_info, objective, workload) for idx, chunk in enumerate(chunks)])
		pool.close()
		results = [item for sublist in results for item in sublist]
		results = sorted(results, key=lambda x: x['cycles'][0])
		top_results = results[:num_top_results]
		top_results = get_solution_info(top_results, design, workload, problem_size)
		return top_results

	elif workload == 'conv':
		I = problem_size['i']
		O = problem_size['o']
		R = problem_size['r']
		C = problem_size['c']
		P = problem_size['p']
		Q = problem_size['q']
		i_t0, o_t0, r_t0, c_t0, p_t0, q_t0 = I, O, R, C, P, Q
		candidates = []
		i_t1_candidates = [i for i in range(1, 2*i_t0)] if 'i' in paddable_dims else [i for i in range(1, i_t0+1) if i_t0 % i == 0]
		o_t1_candidates = [o for o in range(1, 2*o_t0)] if 'o' in paddable_dims else [o for o in range(1, o_t0+1) if o_t0 % o == 0]
		r_t1_candidates = [r for r in range(1, 2*r_t0)] if 'r' in paddable_dims else [r for r in range(1, r_t0+1) if r_t0 % r == 0]
		c_t1_candidates = [c for c in range(1, 2*c_t0)] if 'c' in paddable_dims else [c for c in range(1, c_t0+1) if c_t0 % c == 0]
		for i_t1 in i_t1_candidates:
			for o_t1 in o_t1_candidates:
				for r_t1 in r_t1_candidates:
					for c_t1 in c_t1_candidates:
						candidates.append((i_t1, o_t1, r_t1, c_t1))
		# shuffle candidates
		random.shuffle(candidates)
		print('Generated %d candidates' % len(candidates))
		num_processes = int(multiprocessing.cpu_count() * 1)
		print('Parallelizing using %d processes...' % (num_processes))
		chunks = list_split(candidates, num_processes)
		pool = multiprocessing.Pool(processes = num_processes)
		results = pool.starmap(search_conv, [(i_t0, o_t0, r_t0, c_t0, P, Q, idx, chunk, design, resource_limits, num_top_results, sa_info, objective, workload) for idx, chunk in enumerate(chunks)])
		pool.close()
		results = [item for sublist in results for item in sublist]
		results = sorted(results, key=lambda x: x['cycles'][0])
		top_results = results[:num_top_results]
		top_results = get_solution_info(top_results, design, workload, problem_size)
		return top_results

workload = sys.argv[1]
problem_size = eval(sys.argv[2])
problem_dims = [problem_size[key] for key in problem_size.keys()]
# convert [1, 2, 3] to 1_2_3
problem_dims_str = '_'.join([str(dim) for dim in problem_dims])
designs = os.listdir(f'{designs_lib_dir}/{workload}')
designs.sort()
objectives = ['latency']
# create csv file for results
results_path = prj_path + f'/tests/results/{workload}_{problem_dims_str}_exhaustive'
results_file = results_path + '.csv'
log_file = results_path + '.log'
csv_file = open(results_file, 'w')
print('design_idx,search time (s),objective,original workload,padded workload,fre,throughput (GFLOP/s),cycles,latency(ms),DSP eff,off-chip bytes,bandwidth (GB/s),CTC,DSPs,BRAMs,PEs,SA_dims,sa_sizes', file=csv_file)
csv_file.close()
id = 0
num_top_results = 10
total_time_start = time.time()
for idx in range(7,8):
	for objective in objectives:
		for trial in range(1):
			id += 1
			time_start = time.time()
			solutions = search(designs[idx],objective, workload, problem_size, num_top_results)
			time_end = time.time()
			elapsed_time = time_end - time_start
			sa_info = get_SA_info(designs[idx])
			for solution in solutions:
				print_solution(id, designs[idx], solution, sa_info, objective, workload, elapsed_time, results_file)
total_time_end = time.time()
with open(log_file, 'w') as f:
	print(f'Elapsed time: {total_time_end - total_time_start:.2f} seconds', file=f)


# u250_info = json.load(open(prj_path + '/data/cst/u250.json'))
# resource_limits = {'DSP': u250_info['DSP']['total']*u250_info['DSP']['ratio'], 'BRAM18K': u250_info['BRAM18K']['total']*u250_info['BRAM18K']['ratio']}
# design = designs[7]
# design_name = design.strip('.json')
# file_path = 'tmp/designs/register/' + design_name
# file_path = file_path.replace('/', '.')
# perf_model = importlib.import_module(file_path)
# params = {'i': 64, 'o': 64, 'r': 66, 'c': 64, 'p': 3, 'q': 3, 'i_t1': 64, 'o_t1': 64, 'r_t1': 66, 'c_t1': 16, 'i_t2': 8, 'o_t2': 8, 'r_t2': 3, 'c_t2': 4, 'p14': 8, 'p15': 4, 'p16': 4, 'p17': 16}
# if not perf_model.bound_check(params):
# 	print('params out of bound')
# 	exit()
# result = {}
# result['resources'] = perf_model.est_resource(params)
# if result['resources'][0]['DSP'] > resource_limits['DSP'] or result['resources'][0]['BRAM18K'] > resource_limits['BRAM18K']:
# 	print('resource out of bound')
# 	exit()
# cycles = perf_model.est_latency(params)[0]
# print(cycles)
# candidates = [(params['i_t1'], params['o_t1'], params['r_t1'], params['c_t1'])]
# top_results = search_conv(params['i'], params['o'], params['r'], params['c'], params['p'], params['q'], 0, candidates, design, resource_limits, num_top_results, None, None, workload)
# print(top_results[0]['cycles'][0])
# exit()