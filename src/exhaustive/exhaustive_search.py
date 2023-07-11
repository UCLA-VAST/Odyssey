import os
prj_path = os.environ['PRJ_PATH']
import sys
sys.path.append(f'{prj_path}/src')
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
from tqdm import tqdm
import random
import re
from math import ceil
from math import prod
import importlib
from utils import *
from itertools import count

def search_mm_latency(I, J, K, id, candidates, design, resource_limits, num_top_results):
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
					cnt += 1
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
	return [top_results, cnt]

def search_mm_latency_off_chip(I, J, K, workload, candidates, design, resource_limits, num_top_results, alpha, min_latency, min_off_chip):
	design_name = design.strip('.json')
	file_path = 'tmp/designs/register/' + design_name
	file_path = file_path.replace('/', '.')
	perf_model = importlib.import_module(file_path)

	top_results = [{'score':np.inf}]*num_top_results
	all_designs = 0
	valid_designs = 0
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

def search_conv_latency(I, O, R, C, P, Q, id, candidates, design, resource_limits, num_top_results):
	design_name = design.strip('.json')
	file_path = 'tmp/designs/register/' + design_name
	file_path = file_path.replace('/', '.')
	perf_model = importlib.import_module(file_path)
	top_results = [{'cycles':[np.inf]}]*num_top_results
	cnt = 0
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
						cnt += 1
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
	return [top_results, cnt]

def search_conv_latency_off_chip(I, O, R, C, P, Q, workload, candidates, design, resource_limits, num_top_results, alpha, min_latency, min_off_chip):
	design_name = design.strip('.json')
	file_path = 'tmp/designs/register/' + design_name
	file_path = file_path.replace('/', '.')
	perf_model = importlib.import_module(file_path)

	top_results = [{'score':np.inf}]*num_top_results

	all_designs = 0
	valid_designs = 0
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

def search(design, paddable_dims, resource_limits, workload, problem_size, num_top_results, objective, alpha):
		
	if workload == 'mm':
		I = problem_size['i']
		J = problem_size['j']
		K = problem_size['k']
		
		min_latency = I*J*K/(resource_limits['DSP']/5)
		min_off_chip = I*J + J*K + I*K
		
		i_t0, j_t0, k_t0 = I, J, K
		candidates = []
		i_t0_candidates = get_padded_candidates(I)
		j_t0_candidates = get_padded_candidates(J)
		k_t0_candidates = get_padded_candidates(K)
		i_t1_candidates = [i for i in range(1, 2*i_t0) if i in i_t0_candidates or i <= I] if 'i' in paddable_dims else [i for i in range(1, i_t0+1) if i_t0 % i == 0]
		j_t1_candidates = [j for j in range(1, 2*j_t0) if j in j_t0_candidates or j <= J] if 'j' in paddable_dims else [j for j in range(1, j_t0+1) if j_t0 % j == 0]
		k_t1_candidates = [k for k in range(1, 2*k_t0) if k in k_t0_candidates or k <= K] if 'k' in paddable_dims else [k for k in range(1, k_t0+1) if k_t0 % k == 0]
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
		if objective == 'latency':
			outputs = pool.starmap(search_mm_latency, [(i_t0, j_t0, k_t0, idx, chunk, design, resource_limits, num_top_results) for idx, chunk in enumerate(chunks)])
			pool.close()
			results = []
			counts = []
			for output in outputs:
				results.extend(output[0])
				counts.append(output[1])
			results = sorted(results, key=lambda x: x['cycles'][0])
			top_results = results[:num_top_results]
			top_results = get_solution_info(top_results, design, workload, problem_size)
			return top_results, sum(counts)
		elif objective == 'latency_off_chip':
			outputs = pool.starmap(search_mm_latency_off_chip, [(i_t0, j_t0, k_t0, workload, chunk, design, resource_limits, num_top_results, alpha, min_latency, min_off_chip) for idx, chunk in enumerate(chunks)])
			pool.close()
			results = []
			all_designs = []
			valid_designs = []
			for output in outputs:
				results.extend(output[0])
				all_designs.append(output[1])
				valid_designs.append(output[2])
			results = sorted(results, key=lambda x: x['score'])
			top_results = results[:num_top_results]
			top_results = get_solution_info(top_results, design, workload, problem_size)
			return top_results, sum(all_designs), sum(valid_designs)

	elif workload == 'conv':
		I = problem_size['i']
		O = problem_size['o']
		R = problem_size['r']
		C = problem_size['c']
		P = problem_size['p']
		Q = problem_size['q']

		min_latency = I*O*R*C*P*Q/(resource_limits['DSP']/5)
		min_off_chip = I*(R+P-1)*(C+Q-1) + O*R*C + I*P*Q*O
		
		i_t0, o_t0, r_t0, c_t0, p_t0, q_t0 = I, O, R, C, P, Q
		candidates = []
		i_t0_candidates = get_padded_candidates(I)
		o_t0_candidates = get_padded_candidates(O)
		r_t0_candidates = get_padded_candidates(R)
		c_t0_candidates = get_padded_candidates(C)
		i_t1_candidates = [i for i in range(1, 2*i_t0) if i in i_t0_candidates or i <= I] if 'i' in paddable_dims else [i for i in range(1, i_t0+1) if i_t0 % i == 0]
		o_t1_candidates = [o for o in range(1, 2*o_t0) if o in o_t0_candidates or o <= O] if 'o' in paddable_dims else [o for o in range(1, o_t0+1) if o_t0 % o == 0]
		r_t1_candidates = [r for r in range(1, 2*r_t0) if r in r_t0_candidates or r <= R] if 'r' in paddable_dims else [r for r in range(1, r_t0+1) if r_t0 % r == 0]
		c_t1_candidates = [c for c in range(1, 2*c_t0) if c in c_t0_candidates or c <= C] if 'c' in paddable_dims else [c for c in range(1, c_t0+1) if c_t0 % c == 0]
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
		if objective == 'latency':
			outputs = pool.starmap(search_conv_latency, [(i_t0, o_t0, r_t0, c_t0, p_t0, q_t0, idx, chunk, design, resource_limits, num_top_results) for idx, chunk in enumerate(chunks)])
			pool.close()
			results = []
			counts = []
			for output in outputs:
				results.extend(output[0])
				counts.append(output[1])
			results = sorted(results, key=lambda x: x['cycles'][0])
			top_results = results[:num_top_results]
			top_results = get_solution_info(top_results, design, workload, problem_size)
			return top_results, sum(counts)
		elif objective == 'latency_off_chip':
			outputs = pool.starmap(search_conv_latency_off_chip, [(i_t0, o_t0, r_t0, c_t0, p_t0, q_t0, workload, chunk, design, resource_limits, num_top_results, alpha, min_latency, min_off_chip) for idx, chunk in enumerate(chunks)])
			pool.close()
			results = []
			all_designs = []
			valid_designs = []
			for output in outputs:
				results.extend(output[0])
				all_designs.append(output[1])
				valid_designs.append(output[2])
			results = sorted(results, key=lambda x: x['score'])
			top_results = results[:num_top_results]
			top_results = get_solution_info(top_results, design, workload, problem_size)
			return top_results, sum(all_designs), sum(valid_designs)

if __name__ == '__main__':
	# parse arguments
	parser = argparse.ArgumentParser()
	# workload or w
	parser.add_argument('-w', '--workload', type=str, default='mm', help='workload')
	# problem size or p
	parser.add_argument('-p', '--problem_size', type=str, default="{'i': 64, 'j' : 64, 'k' : 64}", help='problem size')
	# number of top results or n
	parser.add_argument('-n', '--num_top_results', type=int, default=1, help='number of top results')
	# alpha or a
	parser.add_argument('-a', '--alpha', type=float, default=0.5, help='weight of latency')
	# objective or obj
	parser.add_argument('-obj', '--objective', type=str, default='all', help='choose objective from: [latency, off_chip_comm, latency_off_chip, all]')
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

	resource_limits = get_resource_limits('u250')

	results_dir = prj_path + f'/results/{workload}/{problem_dims_str}/design_{permutation}_{dataflow}/{objective}/exhaustive'
	if not os.path.exists(results_dir):
		os.makedirs(results_dir + '/results')
		os.makedirs(results_dir + '/logs')
	logs_dir = results_dir + '/logs/'
	results_dir = results_dir + '/results/'

	# create csv file for results
	file_name = f'top_{num_top_results}_alpha_{alpha}'
	results_file = results_dir + f'{file_name}.csv'
	log_file = logs_dir + f'{file_name}.json'

	csv_file = open(results_file, 'w')
	print('design_idx,objective,original workload,padded workload,fre,throughput (GFLOP/s),cycles,latency(ms),DSP eff,off-chip bytes,bandwidth (GB/s),CTC,DSPs,BRAMs,PEs,SA_dims,search_time,all_designs,valid_designs,adps,vdps,sa_sizes,params', file=csv_file)
	csv_file.close()
	id = 0
	total_time_start = time.time()
	for idx in design_iter:
		for objective in objectives:
			for trial in range(1):
				id += 1
				gen_perf_model(designs[idx], workload, permutation)
				paddable_dims = get_paddable_dims(workload)
				time_start = time.time()
				solutions, all_designs, valid_designs = search(designs[idx], paddable_dims, resource_limits, workload, problem_size, num_top_results, objective, alpha)
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
	new_file_name = f'{workload}_exhaustive_{problem_dims_str}_design_{permutation}_{dataflow}_{objective}_top_{num_top_results}_alpha_{alpha}'
	results_dir = prj_path + f'/results/all/'
	# copy results_file and log_file to new_file_name
	shutil.copy(results_file, results_dir + f'{new_file_name}.csv')
	shutil.copy(log_file, results_dir + f'{new_file_name}.json')
# 	# u250_info = json.load(open(prj_path + '/data/cst/u250.json'))
# 	# resource_limits = {'DSP': u250_info['DSP']['total']*u250_info['DSP']['ratio'], 'BRAM18K': u250_info['BRAM18K']['total']*u250_info['BRAM18K']['ratio']}
# 	# design = designs[7]
# 	# design_name = design.strip('.json')
# 	# file_path = 'tmp/designs/register/' + design_name
# 	# file_path = file_path.replace('/', '.')
# 	# perf_model = importlib.import_module(file_path)
# 	# params = {'i': 64, 'o': 64, 'r': 66, 'c': 64, 'p': 3, 'q': 3, 'i_t1': 64, 'o_t1': 64, 'r_t1': 66, 'c_t1': 16, 'i_t2': 8, 'o_t2': 8, 'r_t2': 3, 'c_t2': 4, 'p14': 8, 'p15': 4, 'p16': 4, 'p17': 16}
# 	# if not perf_model.bound_check(params):
# 	# 	print('params out of bound')
# 	# 	exit()
# 	# result = {}
# 	# result['resources'] = perf_model.est_resource(params)
# 	# if result['resources'][0]['DSP'] > resource_limits['DSP'] or result['resources'][0]['BRAM18K'] > resource_limits['BRAM18K']:
# 	# 	print('resource out of bound')
# 	# 	exit()
# 	# cycles = perf_model.est_latency(params)[0]
# 	# print(cycles)
# 	# candidates = [(params['i_t1'], params['o_t1'], params['r_t1'], params['c_t1'])]
# 	# top_results = search_conv(params['i'], params['o'], params['r'], params['c'], params['p'], params['q'], 0, candidates, design, resource_limits, num_top_results, None, None, workload)
# 	# print(top_results[0]['cycles'][0])
# 	# exit()