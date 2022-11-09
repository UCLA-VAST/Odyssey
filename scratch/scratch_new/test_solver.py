from utils import *
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

import re
from math import ceil
from math import prod
import importlib
from kernel7_2 import *

def get_conv_inner_candidates(candidates, i_t0, o_t0, r_t0, c_t0, p_t0, q_t0, design):
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
						params = infer_params(params)
						if not bound_check(params):
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

def run_latency_search(candidates, resource_limits, design, num_top_results):

	top_results = [{'cycles':[np.inf]}]*num_top_results
	for params in candidates:
		result = {}
		result['resources'] = est_resource(params)
		if result['resources'][0]['DSP'] > resource_limits['DSP'] or result['resources'][0]['BRAM18K'] > resource_limits['BRAM18K']:
			continue
		result['cycles'] = est_latency(params)
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

def parallel_search(candidates, design, top_results, resource_limits, num_top_results, objective):
	
	if len(candidates) >= 72:
		num_processes = int(multiprocessing.cpu_count() * 1)
	elif len(candidates) == 0:
		return top_results
	else:
		num_processes = len(candidates)

	chunks = list_split(candidates, num_processes)
	pool = multiprocessing.Pool(processes = num_processes)

	if objective == 'latency':
		results = pool.starmap(run_latency_search, [(chunk, resource_limits, design, num_top_results) for chunk in chunks])
		pool.close()
		results = [item for sublist in results for item in sublist]
		results = sorted(results, key=lambda x: x['cycles'][0])
		top_results.extend(results[:num_top_results])
		top_results = sorted(top_results, key=lambda x: x['cycles'][0])
		top_results = top_results[:num_top_results]
		return top_results

u250_info = json.load(open(prj_path + '/data/cst/u250.json'))
resource_limits = {'DSP': u250_info['DSP']['total']*u250_info['DSP']['ratio'], 'BRAM18K': u250_info['BRAM18K']['total']*u250_info['BRAM18K']['ratio']}


dim = 128
# p14_ub, p15_ub, p16_ub, p17_ub = 8, 4, 4, 16
# p14_candidates = [x for x in range(1, p14_ub+1) if p14_ub % x == 0]
# p15_candidates = [x for x in range(1, p15_ub+1) if p15_ub % x == 0]
# p16_candidates = [x for x in range(1, p16_ub+1) if p16_ub % x == 0]
# p17_candidates = [x for x in range(1, p17_ub+1) if p17_ub % x == 0]
# p_candidates = list(itertools.product(p14_candidates, p15_candidates, p16_candidates, p17_candidates))
# shuffle p_candidates
# random.shuffle(p_candidates)
p_ubs = [8, 4, 4, 16]
log_file = open('out.log', 'w')
log_file.close()
problem_size = {'i': dim, 'o': dim, 'r': dim, 'c': dim, 'p': 3, 'q': 3}
cycles_1, params_1 = get_solver_latency(problem_size, resource_limits, 1, p_ubs)
print(params_1)
exit()
cycles_2, params_2 = get_solver_latency(problem_size, resource_limits, 2, p_ubs)
cycles_3, params_3 = get_solver_latency(problem_size, resource_limits, 3, p_ubs)
solver = 'failed'
if min(cycles_1, cycles_2, cycles_3) == cycles_1:
	params = params_1
	cycles = cycles_1
	solver = 'APOPT'
elif min(cycles_1, cycles_2, cycles_3) == cycles_2:
	params = params_2
	cycles = cycles_2
	solver = 'BPOPT'
else:
	params = params_3
	cycles = cycles_3
	solver = 'IPOPT'
log_file = open('out.log', 'a')
print(cycles, solver, params, file=log_file)
log_file.close()
exit()
thrtcl_cycles_list = []
solver_cycles_list = []
actual_cycles_list = []
dim = 256
results_file = open('results.csv', 'w')
print(f'dim,theoretical_cycles,solver_cycles,actual_cycles', file=results_file)
results_file.close()
for pad in range(20):
	problem_size = {'i': dim, 'o': dim, 'r': dim+pad, 'c': dim, 'p': 3, 'q': 3}
	candidates = get_conv_candidates(problem_size['i'], problem_size['o'], problem_size['r'], problem_size['c'], problem_size['p'], problem_size['q'], None)
	thrtcl_cycles = problem_size['i']*problem_size['o']*problem_size['r']*problem_size['c']*problem_size['p']*problem_size['q']/(resource_limits['DSP']/5)
	solver_cycles = try_all_solvers(problem_size, resource_limits)
	actual_cycles = parallel_search(candidates, None, [], resource_limits, 1, 'latency')[0]['cycles'][0]
	thrtcl_cycles_list.append(thrtcl_cycles)
	solver_cycles_list.append(solver_cycles)
	actual_cycles_list.append(actual_cycles)
	results_file = open('results.csv', 'a')
	# split integers with commas after every 3 digits
	print(f'{dim},{thrtcl_cycles:_.0f},{solver_cycles:_.0f},{actual_cycles:_.0f}', file=results_file)
	results_file.close()
	# if pad != 0:
	#   print(f'{cycles[pad]} - {cycles[pad-1]} = {cycles[pad] - cycles[pad-1]}')
# problem_size = {'i': dim, 'o': dim, 'r': dim, 'c': dim, 'p': 3, 'q': 3}
# print(problem_size, try_all_solvers(problem_size, resource_limits))