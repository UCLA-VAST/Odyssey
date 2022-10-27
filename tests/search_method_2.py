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
		solutions.append(solution)
	return solutions

def run_latency_search(candidates, resource_limits, design, num_top_results):
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

def get_mm_inner_candidates(candidates, i_t0, j_t0, k_t0, design, workload, problem_size):
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
					# params["p9"] = 16
					# params["p10"] = 16
					# params["p11"] = 16
					# params["p12"] = 16
					params = perf_model.infer_params(params)
					if not perf_model.bound_check(params):
						continue
					local_candidates.append(params)
	return local_candidates

def get_mm_candidates(i_t0, j_t0, k_t0, design, workload, problem_size):
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
	
	candidates = pool.starmap(get_mm_inner_candidates, [(chunk, i_t0, j_t0, k_t0, design, workload, problem_size) for chunk in chunks])
	pool.close()
	candidates = [item for sublist in candidates for item in sublist]
	return candidates

def get_conv_inner_candidates(candidates, i_t0, o_t0, r_t0, c_t0, p_t0, q_t0, design, workload, problem_size):
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
						# if not perf_model.bound_check(params):
						# 	continue
						local_candidates.append(params)
	return local_candidates

def get_conv_candidates(i_t0, o_t0, r_t0, c_t0, p_t0, q_t0, design, workload, problem_size):
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
	candidates = pool.starmap(get_conv_inner_candidates, [(chunk, i_t0, o_t0, r_t0, c_t0, p_t0, q_t0, design, workload, problem_size) for chunk in chunks])
	pool.close()
	candidates = [item for sublist in candidates for item in sublist]
	return candidates

def search(candidates, design, top_results, resource_limits, num_top_results):
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
	
	return top_results#[results[0]]

def est_min_off_chip_trans(i_t0, j_t0, k_t0, perf_model, resource_limits):
  if i_t0 > j_t0:
    factor = 1
    BRAMs = np.inf
    while BRAMs > resource_limits['BRAM18K']:
      params = {}
      params["i"] = i_t0
      params["j"] = j_t0
      params["k"] = k_t0
      params["i_t1"] = i_t0/factor
      params["j_t1"] = j_t0
      params["k_t1"] = 1
      params["i_t2"] = i_t0/factor
      params["j_t2"] = j_t0
      params["k_t2"] = 1
      params = perf_model.infer_params(params)
      BRAMs = perf_model.est_resource(params)[0]['BRAM18K']
      factor += 1
    return perf_model.est_activity(params)['off_chip_acc_num']
  else:
    factor = 1
    BRAMs = np.inf
    while BRAMs > resource_limits['BRAM18K']:
      params = {}
      params["i"] = i_t0
      params["j"] = j_t0
      params["k"] = k_t0
      params["i_t1"] = i_t0
      params["j_t1"] = j_t0/factor
      params["k_t1"] = 1
      params["i_t2"] = i_t0
      params["j_t2"] = j_t0/factor
      params["k_t2"] = 1
      params = perf_model.infer_params(params)
      BRAMs = perf_model.est_resource(params)[0]['BRAM18K']
      factor += 1
    return perf_model.est_activity(params)['off_chip_acc_num']

def est_cycles(i_t0, j_t0, k_t0, perf_model, resource_limits):
	factor = 1
	DSPs = np.inf
	while DSPs > resource_limits['DSP']:
		params = {}
		params["i"] = i_t0
		params["j"] = j_t0
		params["k"] = k_t0
		params["i_t1"] = i_t0/2
		params["j_t1"] = j_t0/factor
		params["k_t1"] = 16
		params["i_t2"] = 1
		params["j_t2"] = 16
		params["k_t2"] = 1
		params = perf_model.infer_params(params)
		DSPs = perf_model.est_resource(params)[0]['DSP']
		factor += 1
	return perf_model.est_latency(params)[0]


def search_latency(design, objective, workload, problem_size, num_top_results):
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

	top_results = [{'cycles':[np.inf]}]*num_top_results
	

	if workload == 'mm':
		I = problem_size['i']
		J = problem_size['j']
		K = problem_size['k']
		DRAM_bits = 512
		i_t0, j_t0, k_t0 = I, J, K
		# min_off_chip_bits = est_min_off_chip_trans(i_t0, j_t0, k_t0, perf_model, resource_limits)*32
		# min_theoratical_latency = max(I*J*K/(resource_limits['DSP']/5), min_off_chip_bits/DRAM_bits)
		min_theoratical_latency = i_t0*j_t0*k_t0/(resource_limits['DSP']/5)
		# min_theoratical_latency = est_cycles(i_t0, j_t0, k_t0, perf_model, resource_limits)
		i_bound = np.inf if 'i' in paddable_dims else I
		j_bound = np.inf if 'j' in paddable_dims else J
		k_bound = np.inf if 'k' in paddable_dims else K
		while(True):
			while(True):
				while(True):
					# generate candidates
					time_start = time.time()
					candidates = get_mm_candidates(i_t0, j_t0, k_t0, design, workload, problem_size)
					time_end = time.time()
					candidate_time = time_end - time_start
					# search
					time_start = time.time()
					top_results = search(candidates, design, top_results, resource_limits, num_top_results)
					time_end = time.time()
					search_time = time_end - time_start
					# print(f'')
					if top_results[-1]["cycles"][0] != np.inf:
						print(f'[{i_t0}, {j_t0}, {int(min_theoratical_latency)}, {int(top_results[-1]["cycles"][0])}, "{top_results[-1]["params"]}"]')
						prologue_latencies = [top_results[-1]['cycles'][1]['latency_prologue'][key] for key in top_results[-1]['cycles'][1]['latency_prologue'].keys()]
						main_latencies = [top_results[-1]['cycles'][1]['latency_main'][key] for key in top_results[-1]['cycles'][1]['latency_main'].keys()]
						epilogue_latencies = [top_results[-1]['cycles'][1]['latency_epilogue'][key] for key in top_results[-1]['cycles'][1]['latency_epilogue'].keys()]
						print(f'prologue: {prologue_latencies}')
						print(f'main: {main_latencies}')
						print(f'epilogue: {epilogue_latencies}')
						latency = max(prologue_latencies) + max(main_latencies) + max(epilogue_latencies)
						print(f'latency: {latency}')
					else:
						print(f'[{i_t0}, {j_t0}, {int(min_theoratical_latency)}, {top_results[-1]["cycles"][0]}]')
					exit()
					# print(f'candidate ({i_t0}, {j_t0}, {k_t0})','min_theoratical_latency = ', min_theoratical_latency, 'current min_latency = ', top_results[-1]['cycles'][0], f'candidate_time = {candidate_time}, search_time = {search_time}')

					k_t0 += 1
					# min_off_chip_bits = est_min_off_chip_trans(i_t0, j_t0, k_t0, perf_model, resource_limits)*32
					# min_theoratical_latency = max(i_t0*j_t0*k_t0/(resource_limits['DSP']/5), min_off_chip_bits/DRAM_bits)
					min_theoratical_latency = i_t0*j_t0*k_t0/(resource_limits['DSP']/5)
					# min_theoratical_latency = est_cycles(i_t0, j_t0, k_t0, perf_model, resource_limits)
					if min_theoratical_latency >= top_results[-1]['cycles'][0] or k_t0 > k_bound:
						k_t0 = K
						break
				j_t0 += 1
				# min_off_chip_bits = est_min_off_chip_trans(i_t0, j_t0, k_t0, perf_model, resource_limits)*32
				# min_theoratical_latency = max(i_t0*j_t0*k_t0/(resource_limits['DSP']/5), min_off_chip_bits/DRAM_bits)
				# min_theoratical_latency = i_t0*j_t0*k_t0/(resource_limits['DSP']/5)
				min_theoratical_latency = est_cycles(i_t0, j_t0, k_t0, perf_model, resource_limits)
				if min_theoratical_latency >= top_results[-1]['cycles'][0] or j_t0 > j_bound:
					j_t0 = J
					break
			i_t0 += 1
			# min_off_chip_bits = est_min_off_chip_trans(i_t0, j_t0, k_t0, perf_model, resource_limits)*32
			# min_theoratical_latency = max(i_t0*j_t0*k_t0/(resource_limits['DSP']/5), min_off_chip_bits/DRAM_bits)
			min_theoratical_latency = i_t0*j_t0*k_t0/(resource_limits['DSP']/5)
			# min_theoratical_latency = est_cycles(i_t0, j_t0, k_t0, perf_model, resource_limits)
			if min_theoratical_latency >= top_results[-1]['cycles'][0] or i_t0 > i_bound:
				break

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
		i_bound = np.inf if 'i' in paddable_dims else I
		o_bound = np.inf if 'o' in paddable_dims else O
		r_bound = np.inf if 'r' in paddable_dims else R
		c_bound = np.inf if 'c' in paddable_dims else C
		while(True):
			while(True):
				while(True):
					while(True):
						# generate candidates
						time_start = time.time()
						candidates = get_conv_candidates(i_t0, o_t0, r_t0, c_t0, p_t0, q_t0, design, workload, problem_size)
						time_end = time.time()
						candidate_time = time_end - time_start
						# search
						time_start = time.time()
						top_results = search(candidates, design, top_results, resource_limits, num_top_results)
						time_end = time.time()
						search_time = time_end - time_start
						print(f'candidate ({i_t0}, {o_t0}, {r_t0}, {c_t0})','min_theoratical_latency = ', min_theoratical_latency, 'current min_latency = ', top_results[-1]['cycles'][0], f'candidate_time = {candidate_time}, search_time = {search_time}')

						c_t0 += 1
						min_theoratical_latency = i_t0 * o_t0 * r_t0 * c_t0 * p_t0 * q_t0/(resource_limits['DSP']/5)
						if min_theoratical_latency >= top_results[-1]['cycles'][0] or c_t0 > c_bound:
							c_t0 = C
							break
					r_t0 += 1
					min_theoratical_latency = i_t0 * o_t0 * r_t0 * c_t0 * p_t0 * q_t0/(resource_limits['DSP']/5)
					if min_theoratical_latency >= top_results[-1]['cycles'][0] or r_t0 > r_bound:
						r_t0 = R
						break
				o_t0 += 1
				min_theoratical_latency = i_t0 * o_t0 * r_t0 * c_t0 * p_t0 * q_t0/(resource_limits['DSP']/5)
				if min_theoratical_latency >= top_results[-1]['cycles'][0] or o_t0 > o_bound:
					o_t0 = O
					break
			i_t0 += 1
			min_theoratical_latency = i_t0 * o_t0 * r_t0 * c_t0 * p_t0 * q_t0/(resource_limits['DSP']/5)
			if min_theoratical_latency >= top_results[-1]['cycles'][0] or i_t0 > i_bound:
				break

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
results_file = prj_path + f'/tests/results/{workload}_{problem_dims_str}_search_method_2.csv'
csv_file = open(results_file, 'w')
print('design_idx,search time (s),objective,original workload,padded workload,fre,throughput (GFLOP/s),cycles,latency(ms),DSP eff,off-chip bytes,bandwidth (GB/s),CTC,DSPs,BRAMs,PEs,SA_dims,sa_sizes', file=csv_file)
csv_file.close()
id = 0
total_time_start = time.time()
for idx in range(3,4):#len(designs)):
	for objective in objectives:
		for trial in range(1):
			id += 1
			time_start = time.time()
			solutions = search_latency(designs[idx],objective, workload, problem_size, 1)
			solution = solutions[0]
			time_end = time.time()
			elapsed_time = time_end - time_start
			sa_info = get_SA_info(designs[idx])
			print_solution(id, designs[idx], solution, sa_info, objective, workload, elapsed_time, results_file)
total_time_end = time.time()
# print(f'Elapsed time: {total_time_end - total_time_start:.2f} seconds', file=outfile)