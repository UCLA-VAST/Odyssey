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

from utils import *
from itertools import count
from collections import OrderedDict

def get_all_factors(n):
  factors = []
  for i in range(1, n+1):
    if n % i == 0:
      factors.append(i)
  return factors

def get_mm_inner_candidates(candidates, i_t0, j_t0, k_t0, design):
	local_candidates = []
	design_name = design.strip('.json')
	file_path = 'tmp/designs/register/' + design_name
	file_path = file_path.replace('/', '.')
	perf_model = importlib.import_module(file_path)
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
					params = perf_model.infer_params(params)
					if not perf_model.bound_check(params):
						continue
					local_candidates.append(params)
	return local_candidates

def get_mm_candidates(i_t0, j_t0, k_t0, k_new_factors, j_new_factors, i_new_factors, design):
	candidates = []
	
	i_t1_candidates = [x for x in range(1, i_t0+1) if i_t0 % x == 0]
	j_t1_candidates = [x for x in range(1, j_t0+1) if j_t0 % x == 0]
	k_t1_candidates = [x for x in range(1, k_t0+1) if k_t0 % x == 0]
	# print('all i factors: ', i_t1_candidates)
	# print('new i factors: ', i_new_factors)
	# print('all j factors: ', j_t1_candidates)
	# print('new j factors: ', j_new_factors)
	# print('all k factors: ', k_t1_candidates)
	# print('new k factors: ', k_new_factors)

	# print()
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
	
	candidates = pool.starmap(get_mm_inner_candidates, [(chunk, i_t0, j_t0, k_t0, design) for chunk in chunks])
	pool.close()
	candidates = [item for sublist in candidates for item in sublist]
	return candidates

def get_conv_inner_candidates(candidates, i_t0, o_t0, r_t0, c_t0, p_t0, q_t0, design):
	local_candidates = []
	design_name = design.strip('.json')
	file_path = 'tmp/designs/register/' + design_name
	file_path = file_path.replace('/', '.')
	perf_model = importlib.import_module(file_path)
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

def run_latency_search(candidates, resource_limits, design, num_top_results):
	design_name = design.strip('.json')
	file_path = 'tmp/designs/register/' + design_name
	file_path = file_path.replace('/', '.')
	perf_model = importlib.import_module(file_path)

	top_results = [{'cycles':[np.inf]}]*num_top_results
	count = 0
	for params in candidates:
		result = {}
		result['resources'] = perf_model.est_resource(params)
		if result['resources'][0]['DSP'] > resource_limits['DSP'] or result['resources'][0]['BRAM18K'] > resource_limits['BRAM18K']:
			continue
		result['cycles'] = perf_model.est_latency(params)
		result['params'] = params
		count += 1
		if result['cycles'][0] < top_results[-1]['cycles'][0]:
			for j in range(num_top_results):
				if result['cycles'][0] < top_results[j]['cycles'][0]:
					# insert result into results
					top_results.insert(j, result)
					# remove last element
					top_results.pop()
					break
	return [top_results, count]

def parallel_search(candidates, design, top_results, resource_limits, num_top_results, objective, alpha, min_latency, min_off_chip):
	
	if len(candidates) >= 72:
		num_processes = int(multiprocessing.cpu_count() * 1)
	elif len(candidates) == 0:
		return top_results, False
	else:
		num_processes = len(candidates)

	chunks = list_split(candidates, num_processes)
	pool = multiprocessing.Pool(processes = num_processes)

	if objective == 'latency':
		outputs = pool.starmap(run_latency_search, [(chunk, resource_limits, design, num_top_results) for chunk in chunks])
		results = []
		counts = []
		for output in outputs:
			results.append(output[0])
			counts.append(output[1])
		pool.close()
		results = [item for sublist in results for item in sublist]
		results = sorted(results, key=lambda x: x['cycles'][0])
		top_results.extend(results[:num_top_results])
		top_results = sorted(top_results, key=lambda x: x['cycles'][0])
		top_results = top_results[:num_top_results]
		return top_results, sum(counts)

def search(design, paddable_dims, resource_limits, workload, problem_size, num_top_results, objective, alpha, threshold):

	top_results = [{'cycles':[np.inf], 'off_chip_trans':np.inf, 'score':np.inf}]*num_top_results

	if workload == 'mm':
		I = problem_size['i']
		J = problem_size['j']
		K = problem_size['k']

		min_latency = I*J*K/(resource_limits['DSP']/5)
		min_off_chip = I*J + J*K + I*K
		
		i_t0, j_t0, k_t0 = I, J, K

		i_bound = I*2-1 if 'i' in paddable_dims else I
		j_bound = J*2-1 if 'j' in paddable_dims else J
		k_bound = K*2-1 if 'k' in paddable_dims else K
		i_factors = []
		j_factors = []
		k_factors = []
		k_all_factors = get_all_factors(k_t0)
		k_new_factors = [factor for factor in k_all_factors if factor not in k_factors]
		j_all_factors = get_all_factors(j_t0)
		j_new_factors = [factor for factor in j_all_factors if factor not in j_factors]
		i_all_factors = get_all_factors(i_t0)
		i_new_factors = [factor for factor in i_all_factors if factor not in i_factors]
		while(True):
			i_all_factors = get_all_factors(i_t0)
			i_new_factors = [factor for factor in i_all_factors if factor not in i_factors]
			i_factors.extend(i_new_factors)
			while(True):
				j_all_factors = get_all_factors(j_t0)
				j_new_factors = [factor for factor in j_all_factors if factor not in j_factors]
				j_factors.extend(j_new_factors)
				while(True):
					k_all_factors = get_all_factors(k_t0)
					k_new_factors = [factor for factor in k_all_factors if factor not in k_factors]
					k_factors.extend(k_new_factors)
					# generate candidates
					time_start = time.time()
					candidates = get_mm_candidates(i_t0, j_t0, k_t0, k_new_factors, j_new_factors, i_new_factors, design)
					time_end = time.time()
					candidate_time = time_end - time_start
					# search
					time_start = time.time()
					top_results, counts = parallel_search(candidates, design, top_results, resource_limits, num_top_results, objective, alpha, min_latency, min_off_chip)
					time_end = time.time()
					search_time = time_end - time_start
					print(f'candidate ({i_t0}, {j_t0}, {k_t0})', 'current min_latency = ', top_results[-1]['cycles'][0])

					k_t0 += 1

					if k_t0 > k_bound:
						k_factors = []
						k_t0 = K
						break

				j_t0 += 1

				if j_t0 > j_bound:
					j_factors = []
					j_t0 = J
					break

			i_t0 += 1

			if i_t0 > i_bound:
				break

		top_results = get_solution_info(top_results, design, workload, problem_size)
		return top_results
					
								
	# elif workload == 'conv':
	# 	I = problem_size['i']
	# 	O = problem_size['o']
	# 	R = problem_size['r']
	# 	C = problem_size['c']
	# 	P = problem_size['p']
	# 	Q = problem_size['q']

	# 	min_latency = I*O*R*C*P*Q/(resource_limits['DSP']/5)
	# 	min_off_chip = I*(R + P - 1)*(C + Q - 1) + O*R*C + I*O*P*Q

	# 	i_t0, o_t0, r_t0, c_t0, p_t0, q_t0 = I, O, R, C, P, Q
		
	# 	i_bound = np.inf if 'i' in paddable_dims else I
	# 	o_bound = np.inf if 'o' in paddable_dims else O
	# 	r_bound = np.inf if 'r' in paddable_dims else R
	# 	c_bound = np.inf if 'c' in paddable_dims else C
	# 	i_counter = 0
	# 	o_counter = 0
	# 	r_counter = 0
	# 	c_counter = 0
	# 	is_c_updated = False
	# 	is_r_updated = False
	# 	is_o_updated = False
	# 	is_i_updated = False
		
	# 	while(True):
	# 		while(True):
	# 			while(True):
	# 				while(True):
	# 					# generate candidates
	# 					time_start = time.time()
	# 					candidates = get_conv_candidates(i_t0, o_t0, r_t0, c_t0, p_t0, q_t0, design)
	# 					time_end = time.time()
	# 					candidate_time = time_end - time_start
	# 					# search
	# 					time_start = time.time()
	# 					top_results, is_c_updated = parallel_search(candidates, design, top_results, resource_limits, num_top_results, objective, alpha, min_latency, min_off_chip)
	# 					time_end = time.time()
	# 					search_time = time_end - time_start
	# 					print(f'candidate ({i_t0}, {o_t0}, {r_t0}, {c_t0})', 'current min_latency = ', top_results[-1]['cycles'][0], is_c_updated, is_r_updated, is_o_updated, is_i_updated)

	# 					if is_c_updated:
	# 						c_counter = 0
	# 						is_r_updated = True
	# 					else:
	# 						c_counter += 1
	# 						is_r_updated = False

	# 					c_t0 += 1

	# 					if c_counter >= threshold or c_t0 > c_bound:
	# 						c_counter = 0
	# 						c_t0 = C
	# 						break

	# 				if is_r_updated:
	# 					r_counter = 0
	# 					is_o_updated = True
	# 				else:
	# 					r_counter += 1
	# 					is_o_updated = False

	# 				r_t0 += 1

	# 				if r_counter >= threshold or r_t0 > r_bound:
	# 					r_counter = 0
	# 					r_t0 = R
	# 					break
	# 			if is_o_updated:
	# 				o_counter = 0
	# 				is_i_updated = True
	# 			else:
	# 				o_counter += 1
	# 				is_i_updated = False

	# 			o_t0 += 1

	# 			if o_counter >= threshold or o_t0 > o_bound:
	# 				o_counter = 0
	# 				o_t0 = O
	# 				break

	# 		if is_i_updated:
	# 			i_counter = 0
	# 		else:
	# 			i_counter += 1

	# 		i_t0 += 1

	# 		if i_counter >= threshold or i_t0 > i_bound:
	# 			break

	# 	top_results = get_solution_info(top_results, design, workload, problem_size)
	# 	return top_results

if __name__ == '__main__':
	# parse arguments
	parser = argparse.ArgumentParser()
	# workload or w
	parser.add_argument('-w', '--workload', type=str, default='mm', help='workload')
	# problem size or p
	parser.add_argument('-p', '--problem_size', type=str, default="{'i': 64, 'j' : 64, 'k' : 64}", help='problem size')
	# number of top results or n
	parser.add_argument('-n', '--num_top_results', type=int, default=1, help='number of top results')
	# threshold or t
	parser.add_argument('-t', '--threshold', type=int, default=10, help='threshold')
	# alpha or a
	parser.add_argument('-a', '--alpha', type=float, default=0.5, help='weight of latency')
	# objective or obj
	parser.add_argument('-obj', '--objective', type=str, default='all', help='choose objective from: [latency, off_chip, latency_off_chip, all]')
	# design or d
	parser.add_argument('-d', '--design', type=str, default='all', help='design')
	
	# workload
	workload = parser.parse_args().workload

	# problem size
	problem_size = eval(parser.parse_args().problem_size)
	problem_dims = [problem_size[key] for key in problem_size.keys()]
	problem_dims_str = '_'.join([str(dim) for dim in problem_dims])

	# number of top results
	num_top_results = parser.parse_args().num_top_results

	# threshold
	threshold = parser.parse_args().threshold

	# alpha
	alpha = parser.parse_args().alpha

	# objective
	objective = parser.parse_args().objective
	if objective == 'all':
		objectives = ['latency', 'off_chip', 'latency_off_chip']
	else:
		objectives = [objective]

	# design
	designs = os.listdir(f'{designs_lib_dir}/{workload}')
	designs.sort()
	design = parser.parse_args().design
	if design=='all':
		design_iter = range(len(designs))
	else:
		design_iter = [int(design)]

	resource_limits = get_resource_limits('u250')

	# create csv file for results
	file_name = f'{workload}/design_{design}_{problem_dims_str}_top_{num_top_results}_thr{threshold}_exhaustive'
	results_file = prj_path + f'/new_tests/results/{file_name}.csv'
	log_file = prj_path + f'/new_tests/logs/{file_name}.log'
	csv_file = open(results_file, 'w')
	print('design_idx,objective,original workload,padded workload,fre,throughput (GFLOP/s),cycles,latency(ms),DSP eff,off-chip bytes,bandwidth (GB/s),CTC,DSPs,BRAMs,PEs,SA_dims,sa_sizes', file=csv_file)
	csv_file.close()
	id = 0
	total_time_start = time.time()
	threshold = 10
	num_top_results = 10
	for idx in design_iter:
		for objective in objectives:
			for trial in range(1):
				id += 1
				gen_perf_model(designs[idx], workload)
				paddable_dims = get_paddable_dims(designs[idx])
				time_start = time.time()
				solutions = search(designs[idx], paddable_dims, resource_limits, workload, problem_size, num_top_results, objective, alpha, threshold)
				time_end = time.time()
				elapsed_time = time_end - time_start
				sa_info = get_SA_info(designs[idx])
				for solution in solutions:
					print_solution(id, designs[idx], solution, sa_info, objective, workload, elapsed_time, results_file)
					
	total_time_end = time.time()
	with open(log_file, 'w') as f:
		print(f'Elapsed time: {total_time_end - total_time_start:.2f} seconds', file=f)