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
import random

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

def get_mm_candidates(i_t0, j_t0, k_t0, candidates, design):
	# candidates = []
	
	# i_t1_candidates = [x for x in range(1, i_t0+1) if i_t0 % x == 0]
	# j_t1_candidates = [x for x in range(1, j_t0+1) if j_t0 % x == 0]
	# k_t1_candidates = [x for x in range(1, k_t0+1) if k_t0 % x == 0]
	# for i_t1 in i_t1_candidates:
	# 	for j_t1 in j_t1_candidates:
	# 		for k_t1 in k_t1_candidates:
	# 			candidates.append((i_t1, j_t1, k_t1))
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
	cnt = 0
	for params in candidates:
		result = {}
		result['resources'] = perf_model.est_resource(params)
		if result['resources'][0]['DSP'] > resource_limits['DSP'] or result['resources'][0]['BRAM18K'] > resource_limits['BRAM18K']:
			continue
		result['cycles'] = perf_model.est_latency(params)
		result['params'] = params
		cnt += 1
		if result['cycles'][0] < top_results[-1]['cycles'][0]:
			for j in range(num_top_results):
				if result['cycles'][0] < top_results[j]['cycles'][0]:
					# insert result into results
					top_results.insert(j, result)
					# remove last element
					top_results.pop()
					break
	return [top_results, cnt]

def run_off_chip_search(candidates, resource_limits, design, num_top_results):
	design_name = design.strip('.json')
	file_path = 'tmp/designs/register/' + design_name
	file_path = file_path.replace('/', '.')
	perf_model = importlib.import_module(file_path)

	top_results = [{'off_chip_trans':np.inf}]*num_top_results
	for params in candidates:
		result = {}
		result['resources'] = perf_model.est_resource(params)
		if result['resources'][0]['DSP'] > resource_limits['DSP'] or result['resources'][0]['BRAM18K'] > resource_limits['BRAM18K']:
			continue
		result['off_chip_trans'] = perf_model.est_activity(params)['off_chip_acc_num']
		result['cycles'] = perf_model.est_latency(params)
		result['params'] = params
		if result['off_chip_trans'] < top_results[-1]['off_chip_trans']:
			for j in range(num_top_results):
				if result['off_chip_trans'] < top_results[j]['off_chip_trans']:
					# insert result into results
					top_results.insert(j, result)
					# remove last element
					top_results.pop()
					break

	return top_results

def run_latency_off_chip_search(candidates, resource_limits, workload, design, num_top_results, alpha, min_latency, min_off_chip):
	design_name = design.strip('.json')
	file_path = 'tmp/designs/register/' + design_name
	file_path = file_path.replace('/', '.')
	perf_model = importlib.import_module(file_path)

	top_results = [{'score':np.inf}]*num_top_results
	cnt = 0
	for params in candidates:
		result = {}
		result['resources'] = perf_model.est_resource(params)
		if result['resources'][0]['DSP'] > resource_limits['DSP'] or result['resources'][0]['BRAM18K'] > resource_limits['BRAM18K']:
			continue
		cnt += 1
		result['cycles'] = perf_model.est_latency(params)
		activity = perf_model.est_activity(params)
		result['off_chip_trans'] = est_off_chip_trans(activity, workload)
		result['params'] = params
		norm_latency = result['cycles'][0] / min_latency
		norm_off_chip = result['off_chip_trans'] / min_off_chip
		result['score'] = alpha * norm_latency + (1 - alpha) * norm_off_chip
		if result['score'] < top_results[-1]['score']:
			for j in range(num_top_results):
				if result['score'] < top_results[j]['score']:
					# insert result into results
					top_results.insert(j, result)
					# remove last element
					top_results.pop()
					break

	return [top_results, cnt]

def search_mm_latency_off_chip(I, J, K, workload, candidates, design, resource_limits, num_top_results, alpha, min_latency, min_off_chip):
	design_name = design.strip('.json')
	file_path = 'tmp/designs/register/' + design_name
	file_path = file_path.replace('/', '.')
	perf_model = importlib.import_module(file_path)

	top_results = [{'score':np.inf}]*num_top_results
	all_designs = 0
	valid_designs = 0
	for idx in range(len(candidates)):
		i_t1, j_t1, k_t1 = candidates[idx]
		i_t2_candidates = [i for i in range(1, i_t1+1) if i_t1 % i == 0]
		j_t2_candidates = [j for j in range(1, j_t1+1) if j_t1 % j == 0]
		k_t2_candidates = [k for k in range(1, k_t1+1) if k_t1 % k == 0]
		for i_t2 in i_t2_candidates:
			for j_t2 in j_t2_candidates:
				for k_t2 in k_t2_candidates:
					params = {}
					params["i"] = I
					params["j"] = J
					params["k"] = K
					params["i_t1"] = i_t1
					params["j_t1"] = j_t1
					params["k_t1"] = k_t1
					params["i_t2"] = i_t2
					params["j_t2"] = j_t2
					params["k_t2"] = k_t2
					params = perf_model.infer_params(params)
					all_designs += 1
					if params == None or not perf_model.bound_check(params):
						continue
					result = {}
					result['resources'] = perf_model.est_resource(params)
					if result['resources'][0]['DSP'] > resource_limits['DSP'] or result['resources'][0]['BRAM18K'] > resource_limits['BRAM18K']:
						continue
					valid_designs += 1
					result['cycles'] = perf_model.est_latency(params)
					activity = perf_model.est_activity(params)
					result['off_chip_trans'] = est_off_chip_trans(activity, workload)
					result['params'] = params
					norm_latency = result['cycles'][0] / min_latency
					norm_off_chip = result['off_chip_trans'] / min_off_chip
					result['score'] = alpha * norm_latency + (1 - alpha) * norm_off_chip
					if result['score'] < top_results[-1]['score']:
						for j in range(num_top_results):
							if result['score'] < top_results[j]['score']:
								# insert result into results
								top_results.insert(j, result)
								# remove last element
								top_results.pop()
								break
	return [top_results, all_designs, valid_designs]

def search_conv_latency_off_chip(I, O, R, C, P, Q, workload, candidates, design, resource_limits, num_top_results, alpha, min_latency, min_off_chip):
	design_name = design.strip('.json')
	file_path = 'tmp/designs/register/' + design_name
	file_path = file_path.replace('/', '.')
	perf_model = importlib.import_module(file_path)

	top_results = [{'score':np.inf}]*num_top_results

	all_designs = 0
	valid_designs = 0
	for idx in range(len(candidates)):
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
						params["i"] = I
						params["o"] = O
						params["r"] = R
						params["c"] = C
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
						all_designs += 1
						if params == None or not perf_model.bound_check(params):
							continue
						result = {}
						result['resources'] = perf_model.est_resource(params)
						if result['resources'][0]['DSP'] > resource_limits['DSP'] or result['resources'][0]['BRAM18K'] > resource_limits['BRAM18K']:
							continue
						valid_designs += 1
						result['cycles'] = perf_model.est_latency(params)
						activity = perf_model.est_activity(params)
						result['off_chip_trans'] = est_off_chip_trans(activity, workload)
						result['params'] = params
						norm_latency = result['cycles'][0] / min_latency
						norm_off_chip = result['off_chip_trans'] / min_off_chip
						result['score'] = alpha * norm_latency + (1 - alpha) * norm_off_chip
						if result['score'] < top_results[-1]['score']:
							for j in range(num_top_results):
								if result['score'] < top_results[j]['score']:
									# insert result into results
									top_results.insert(j, result)
									# remove last element
									top_results.pop()
									break
	return [top_results, all_designs, valid_designs]

def mm_parallel_search(I, J, K, candidates, design, top_results, resource_limits, num_top_results, objective, alpha, min_latency, min_off_chip):
	random.shuffle(candidates)
	# print('Generated %d candidates' % len(candidates))
	if len(candidates) >= 72:
		num_processes = int(multiprocessing.cpu_count() * 1)
	elif len(candidates) == 0:
		return top_results, False, 0
	else:
		num_processes = len(candidates)
	# print('Parallelizing using %d processes...' % (num_processes))
	chunks = list_split(candidates, num_processes)
	pool = multiprocessing.Pool(processes = num_processes)
	outputs = pool.starmap(search_mm_latency_off_chip, [(I, J, K, workload, chunk, design, resource_limits, num_top_results, alpha, min_latency, min_off_chip) for idx, chunk in enumerate(chunks)])
	pool.close()
	results = []
	all_designs = []
	valid_designs = []
	for output in outputs:
		results.extend(output[0])
		all_designs.append(output[1])
		valid_designs.append(output[2])
	results = sorted(results, key=lambda x: x['score'])
	prev_top_results = copy.deepcopy(top_results)
	top_results.extend(results[:num_top_results])
	top_results = sorted(top_results, key=lambda x: x['score'])
	top_results = top_results[:num_top_results]
	if prev_top_results == top_results:
		return top_results, False, sum(all_designs), sum(valid_designs)
	else:
		return top_results, True, sum(all_designs), sum(valid_designs)

def conv_parallel_search(I, O, R, C, P, Q, candidates, design, top_results, resource_limits, num_top_results, objective, alpha, min_latency, min_off_chip):
	random.shuffle(candidates)
	if len(candidates) >= 72:
		num_processes = int(multiprocessing.cpu_count() * 1)
	elif len(candidates) == 0:
		return top_results, False, 0
	else:
		num_processes = len(candidates)
	chunks = list_split(candidates, num_processes)
	pool = multiprocessing.Pool(processes = num_processes)
	outputs = pool.starmap(search_conv_latency_off_chip, [(I, O, R, C, P, Q, workload, chunk, design, resource_limits, num_top_results, alpha, min_latency, min_off_chip) for idx, chunk in enumerate(chunks)])
	pool.close()
	results = []
	all_designs = []
	valid_designs = []
	for output in outputs:
		results.extend(output[0])
		all_designs.append(output[1])
		valid_designs.append(output[2])
	results = sorted(results, key=lambda x: x['score'])
	prev_top_results = copy.deepcopy(top_results)
	top_results.extend(results[:num_top_results])
	top_results = sorted(top_results, key=lambda x: x['score'])
	top_results = top_results[:num_top_results]
	if prev_top_results == top_results:
		return top_results, False, sum(all_designs), sum(valid_designs)
	else:
		return top_results, True, sum(all_designs), sum(valid_designs)

# def parallel_search(candidates, design, top_results, resource_limits, num_top_results, objective, alpha, min_latency, min_off_chip):
	
# 	if len(candidates) >= 72:
# 		num_processes = int(multiprocessing.cpu_count() * 1)
# 	elif len(candidates) == 0:
# 		return top_results, False, 0
# 	else:
# 		num_processes = len(candidates)

# 	chunks = list_split(candidates, num_processes)
# 	pool = multiprocessing.Pool(processes = num_processes)

# 	if objective == 'latency':
# 		outputs = pool.starmap(run_latency_search, [(chunk, resource_limits, design, num_top_results) for chunk in chunks])
# 		pool.close()
# 		results = []
# 		counts = []
# 		for output in outputs:
# 			results.extend(output[0])
# 			counts.append(output[1])
# 		results = sorted(results, key=lambda x: x['cycles'][0])
# 		prev_top_results = copy.deepcopy(top_results)
# 		top_results.extend(results[:num_top_results])
# 		top_results = sorted(top_results, key=lambda x: x['cycles'][0])
# 		top_results = top_results[:num_top_results]
# 		if prev_top_results == top_results:
# 			return top_results, False, sum(counts)
# 		else:
# 			return top_results, True, sum(counts)

# 	elif objective == 'off_chip_comm':
# 		results = pool.starmap(run_off_chip_search, [(chunk, resource_limits, design, num_top_results) for chunk in chunks])
# 		pool.close()
# 		results = [item for sublist in results for item in sublist]
# 		results = sorted(results, key=lambda x: x['off_chip_trans'])
# 		prev_top_results = copy.deepcopy(top_results)
# 		top_results.extend(results[:num_top_results])
# 		top_results = sorted(top_results, key=lambda x: x['off_chip_trans'])
# 		top_results = top_results[:num_top_results]
# 		if prev_top_results == top_results:
# 			return top_results, False
# 		else:
# 			return top_results, True

# 	elif objective == 'latency_off_chip':
# 		outputs = pool.starmap(run_latency_off_chip_search, [(chunk, resource_limits, workload, design, num_top_results, alpha, min_latency, min_off_chip) for chunk in chunks])
# 		pool.close()
# 		results = []
# 		counts = []
# 		for output in outputs:
# 			results.extend(output[0])
# 			counts.append(output[1])
# 		results = sorted(results, key=lambda x: x['score'])
# 		prev_top_results = copy.deepcopy(top_results)
# 		top_results.extend(results[:num_top_results])
# 		top_results = sorted(top_results, key=lambda x: x['score'])
# 		top_results = top_results[:num_top_results]
# 		if prev_top_results == top_results:
# 			return top_results, False, sum(counts)
# 		else:
# 			return top_results, True, sum(counts)

def search(design, paddable_dims, resource_limits, workload, problem_size, num_top_results, objective, alpha, threshold):

	top_results = [{'cycles':[np.inf], 'off_chip_trans':np.inf, 'score':np.inf}]*num_top_results
	total_all_designs = 0
	total_valid_designs = 0
	if workload == 'mm':
		I = problem_size['i']
		J = problem_size['j']
		K = problem_size['k']
		min_latency = I*J*K/(resource_limits['DSP']/5)
		min_off_chip = I*J + J*K + I*K
		i_t0, j_t0, k_t0 = I, J, K
		i_t0_candidates = get_padded_candidates(I) if 'i' in paddable_dims else [I]
		j_t0_candidates = get_padded_candidates(J) if 'j' in paddable_dims else [J]
		k_t0_candidates = get_padded_candidates(K) if 'k' in paddable_dims else [K]
		i_counter = 0
		j_counter = 0
		k_counter = 0
		i_threshold = ceil(threshold*(I**0.5))#max(ceil(threshold*I), 5)
		j_threshold = ceil(threshold*(J**0.5))#max(ceil(threshold*J), 5)
		k_threshold = ceil(threshold*(K**0.5))#max(ceil(threshold*K), 5)
		i_t1_seen_candidates = []
		for i_t0 in i_t0_candidates:
			i_t1_candidates = [x for x in range(1, i_t0+1) if i_t0 % x == 0]
			i_t1_candidates = [x for x in i_t1_candidates if x not in i_t1_seen_candidates]
			i_t1_seen_candidates.extend(i_t1_candidates)
			i_t1_seen_candidates = list(set(i_t1_seen_candidates))
			j_t1_seen_candidates = []
			is_i_updated = False
			for j_t0 in j_t0_candidates:
				j_t1_candidates = [x for x in range(1, j_t0+1) if j_t0 % x == 0]
				j_t1_candidates = [x for x in j_t1_candidates if x not in j_t1_seen_candidates]
				j_t1_seen_candidates.extend(j_t1_candidates)
				j_t1_seen_candidates = list(set(j_t1_seen_candidates))
				k_t1_seen_candidates = []
				is_j_updated = False
				for k_t0 in k_t0_candidates:
					k_t1_candidates = [x for x in range(1, k_t0+1) if k_t0 % x == 0]
					k_t1_candidates = [x for x in k_t1_candidates if x not in k_t1_seen_candidates]
					k_t1_seen_candidates.extend(k_t1_candidates)
					k_t1_seen_candidates = list(set(k_t1_seen_candidates))
					is_k_updated = False
					# generate candidates
					candidates = list(itertools.product(i_t1_candidates, j_t1_candidates, k_t1_candidates))
					is_updated = False
					top_results, is_updated, all_designs, valid_designs = mm_parallel_search(i_t0, j_t0, k_t0, candidates, design, top_results, resource_limits, num_top_results, objective, alpha, min_latency, min_off_chip)
					total_all_designs += all_designs
					total_valid_designs += valid_designs
					print(f'candidate ({i_t0}, {j_t0}, {k_t0})', 'current min_latency = ', top_results[-1]['score'], \
						(is_k_updated, k_counter), (is_j_updated, j_counter), (is_i_updated, i_counter))
					if is_k_updated:
						is_k_updated = True
						is_j_updated = True
						is_i_updated = True
						k_counter = 0
					else:
						k_counter += 1

					if k_counter >= k_threshold:
						k_counter = 0
						break
				
				if is_j_updated:
					j_counter = 0
				else:
					j_counter += 1
				
				if j_counter >= j_threshold:
					j_counter = 0
					break

			if is_i_updated:
				i_counter = 0
			else:
				i_counter += 1

			if i_counter >= i_threshold:
				break

		top_results = get_solution_info(top_results, design, workload, problem_size)
		return top_results, total_all_designs, total_valid_designs
											
	elif workload == 'conv':
		I = problem_size['i']
		O = problem_size['o']
		R = problem_size['r']
		C = problem_size['c']
		P = problem_size['p']
		Q = problem_size['q']

		min_latency = I*O*R*C*P*Q/(resource_limits['DSP']/5)
		min_off_chip = I*(R + P - 1)*(C + Q - 1) + O*R*C + I*O*P*Q

		i_t0, o_t0, r_t0, c_t0, p_t0, q_t0 = I, O, R, C, P, Q
		
		i_t0_candidates = get_padded_candidates(I) if 'i' in paddable_dims else [I]
		o_t0_candidates = get_padded_candidates(O) if 'o' in paddable_dims else [O]
		r_t0_candidates = get_padded_candidates(R) if 'r' in paddable_dims else [R]
		c_t0_candidates = get_padded_candidates(C) if 'c' in paddable_dims else [C]
		
		i_counter = 0
		o_counter = 0
		r_counter = 0
		c_counter = 0
		# i_threshold = max(ceil(I*threshold), 5)
		# o_threshold = max(ceil(O*threshold), 5)
		# r_threshold = max(ceil(R*threshold), 5)
		# c_threshold = max(ceil(C*threshold), 5)
		i_threshold = ceil(threshold*(I**0.5))
		o_threshold = ceil(threshold*(O**0.5))
		r_threshold = ceil(threshold*(R**0.5))
		c_threshold = ceil(threshold*(C**0.5))
		# print('i_threshold = ', i_threshold)
		# print('o_threshold = ', o_threshold)
		# print('r_threshold = ', r_threshold)
		# print('c_threshold = ', c_threshold)

		i_t1_seen_candidates = []
		for i_t0 in i_t0_candidates:
			i_t1_candidates = [x for x in range(1, i_t0+1) if i_t0 % x == 0]
			i_t1_candidates = [x for x in i_t1_candidates if x not in i_t1_seen_candidates]
			i_t1_seen_candidates.extend(i_t1_candidates)
			i_t1_seen_candidates = list(set(i_t1_seen_candidates))
			o_t1_seen_candidates = []
			is_i_updated = False
			for o_t0 in o_t0_candidates:
				o_t1_candidates = [x for x in range(1, o_t0+1) if o_t0 % x == 0]
				o_t1_candidates = [x for x in o_t1_candidates if x not in o_t1_seen_candidates]
				o_t1_seen_candidates.extend(o_t1_candidates)
				o_t1_seen_candidates = list(set(o_t1_seen_candidates))
				r_t1_seen_candidates = []
				is_o_updated = False
				for r_t0 in r_t0_candidates:
					r_t1_candidates = [x for x in range(1, r_t0+1) if r_t0 % x == 0]
					r_t1_candidates = [x for x in r_t1_candidates if x not in r_t1_seen_candidates]
					r_t1_seen_candidates.extend(r_t1_candidates)
					r_t1_seen_candidates = list(set(r_t1_seen_candidates))
					c_t1_seen_candidates = []
					is_r_updated = False
					for c_t0 in c_t0_candidates:
						c_t1_candidates = [x for x in range(1, c_t0+1) if c_t0 % x == 0]
						c_t1_candidates = [x for x in c_t1_candidates if x not in c_t1_seen_candidates]
						c_t1_seen_candidates.extend(c_t1_candidates)
						c_t1_seen_candidates = list(set(c_t1_seen_candidates))
						is_c_updated = False
						# generate candidates
						candidates = list(itertools.product(i_t1_candidates, o_t1_candidates, r_t1_candidates, c_t1_candidates))
						is_updated = False
						top_results, is_updated, all_designs, valid_designs = conv_parallel_search(i_t0, o_t0, r_t0, c_t0, P, Q, candidates, design, top_results, resource_limits, num_top_results, objective, alpha, min_latency, min_off_chip)
						total_all_designs += all_designs
						total_valid_designs += valid_designs
						print(f'candidate ({i_t0}, {o_t0}, {r_t0}, {c_t0})', 'current min_latency = ', top_results[-1]['score'],\
							(is_c_updated, c_counter), (is_r_updated, r_counter), (is_o_updated, o_counter), (is_i_updated, i_counter))
						if is_updated:
							is_c_updated = True
							is_r_updated = True
							is_o_updated = True
							is_i_updated = True
							c_counter = 0
						else:
							c_counter += 1

						if c_counter >= c_threshold:
							c_counter = 0
							break

					if is_r_updated:
						r_counter = 0
					else:
						r_counter += 1

					if r_counter >= r_threshold:
						r_counter = 0
						break

				if is_o_updated:
					o_counter = 0
				else:
					o_counter += 1

				if o_counter >= o_threshold:
					o_counter = 0
					break

			if is_i_updated:
				i_counter = 0
			else:
				i_counter += 1

			if i_counter >= i_threshold:
				break

		top_results = get_solution_info(top_results, design, workload, problem_size)
		return top_results, total_all_designs, total_valid_designs

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
	parser.add_argument('-thr', '--threshold', type=float, default=0.02, help='threshold')
	# alpha or a
	parser.add_argument('-a', '--alpha', type=float, default=0.5, help='weight of latency')
	# objective or obj
	parser.add_argument('-obj', '--objective', type=str, default='all', help='choose objective from: [latency, off_chip_comm, latency_off_chip, all]')
	# design or d
	parser.add_argument('-d', '--design', type=str, default='all', help='design')
	# trials
	parser.add_argument('-tr', '--trials', type=int, default=1, help='number of trials')
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
		objectives = ['latency', 'off_chip_comm', 'latency_off_chip']
	else:
		objectives = [objective]

	# design
	design = parser.parse_args().design
	if design=='all':
		designs = []
		for permutation in range(3):
			designs.extend(os.listdir(f'{designs_lib_dir}/{workload}_{permutation}'))
		permutation = 'all'
		dataflow = 'all'
		designs.sort()
		design_iter = range(len(designs))
	else:
		design = eval(parser.parse_args().design)
		permutation = design[0]
		dataflow = design[1]
		designs = os.listdir(f'{designs_lib_dir}/{workload}_{permutation}')
		designs.sort()
		design_iter = [int(dataflow)]

	# trials
	trials = parser.parse_args().trials

	resource_limits = get_resource_limits('u250')

	results_dir = prj_path + f'/results/{workload}/{problem_dims_str}/design_{permutation}_{dataflow}/{objective}/non_divisors'
	if not os.path.exists(results_dir):
		os.makedirs(results_dir + '/results')
		os.makedirs(results_dir + '/logs')
	logs_dir = results_dir + '/logs/'
	results_dir = results_dir + '/results/'
	# create csv file for results
	file_name = f'top_{num_top_results}_alpha_{alpha}_thr_{threshold}'
	results_file = results_dir + f'{file_name}.csv'
	log_file = logs_dir + f'{file_name}.json'
	csv_file = open(results_file, 'w')
	print('design_idx,objective,original workload,padded workload,fre,throughput (GFLOP/s),cycles,latency(ms),DSP eff,off-chip bytes,bandwidth (GB/s),CTC,DSPs,BRAMs,PEs,SA_dims,search_time,all_designs,valid_designs,adps,vdps,sa_sizes,params', file=csv_file)
	csv_file.close()
	id = 0
	total_time_start = time.time()
	for idx in design_iter:
		for objective in objectives:
			for trial in range(trials):
				id += 1
				gen_perf_model(designs[idx], workload, permutation)
				paddable_dims = get_paddable_dims(workload)
				time_start = time.time()
				solutions, all_designs, valid_designs = search(designs[idx], paddable_dims, resource_limits, workload, problem_size, num_top_results, objective, alpha, threshold)
				time_end = time.time()
				elapsed_time = time_end - time_start
				sa_info = get_SA_info(designs[idx])
				for solution in solutions:
					print_solution(id, designs[idx], solution, sa_info, objective, workload, elapsed_time, all_designs, valid_designs, results_file)
	total_time_end = time.time()
	with open(log_file, 'w') as f:
		info = {
			'all_designs':all_designs, 
			'valid_designs': valid_designs, 
			'total_time':total_time_end-total_time_start, 
			'all_designs_per_second':all_designs/(total_time_end-total_time_start),
			'valid_designs_per_second':valid_designs/(total_time_end-total_time_start)
		}
		f.write(json.dumps(info))
	import shutil
	new_file_name = f'{workload}_non_divisors_{problem_dims_str}_design_{permutation}_{dataflow}_{objective}_top_{num_top_results}_alpha_{alpha}_thr_{threshold}'
	results_dir = prj_path + f'/results/all/'
	# copy results_file and log_file to new_file_name
	shutil.copy(results_file, results_dir + f'{new_file_name}.csv')
	shutil.copy(log_file, results_dir + f'{new_file_name}.json')