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


prj_path = os.environ["PRJ_PATH"]
designs_lib_dir = prj_path + f'/data/designs_lib'
designs_dir = prj_path + '/tests/tmp/designs'
output_dir = prj_path + '/tests/tmp/outputs'

def copy_design(design, workload):
	os.system(f'cp {designs_lib_dir}/{workload}/{design} {designs_dir}')

def list_split(ori_list, split_num):
  chunk_size = int(np.ceil(float(len(ori_list)) / split_num))
  chunks = [ori_list[i: i + min(chunk_size, len(ori_list) - i)] for i in range(0, len(ori_list), chunk_size)]
  return chunks

def print_solution(idx, design, solution, sa_info, objective, workload, csv_file):
	file_path = 'tmp/designs/register/' + design.strip('.json')
	file_path = file_path.replace('/', '.')
	model = importlib.import_module(file_path)
	compute_arch_cst = model.compute_arch_cst

	original_workload_size = {}
	padded_workload_size = {}
	padding_dims = sa_info['padding_dims']
	# get elements from dictionary solution['arch_sol'] whose key ends with t1
	# and store them in t1_dims
	for dim in solution['arch_sol'].keys():
		if len(dim) == 1:
			original_workload_size[dim] = solution['arch_sol'][dim]
	t1_dims = {k:v for k, v in solution['arch_sol'].items() if k.endswith('t1')}
	for dim in solution['arch_sol'].keys():
		if dim in padding_dims:
			# get key and value from t1_dims if dim is in key
			t1_dim = [v for k, v in t1_dims.items() if dim in k][0]
			padded_workload_size[dim] = ceil(solution['arch_sol'][dim]/t1_dim)*t1_dim
	# for key in original_workload_size.keys():
	# 	if key not in padded_workload_size.keys():
	# 		padded_workload_size[key] = original_workload_size[key]
	# sort padded_workload_size by key
	padded_workload_size = dict(sorted(padded_workload_size.items()))
	# sort original_workload_size by key
	original_workload_size = dict(sorted(original_workload_size.items()))
	fre = solution['fre']
	throughput = solution['throughput']
	cycles = solution['cycles']
	latency = solution['latency']
	dsp_eff = solution['dsp_eff']
	off_chip_bytes = solution['off_chip_bytes']
	bandwidth = solution['bandwidth']
	CTC = solution['CTC']
	DSPs = solution['DSPs']
	BRAMs = solution['BRAMs']
	arch = compute_arch_cst(solution['arch_sol'])
	array_part_mapping = eval(open(f'{prj_path}/tests/{workload}_array_part.csv').readlines()[int(sa_info['idx'])])
	latency_hiding_mapping = eval(open(f'{prj_path}/tests/{workload}_latency_hiding.csv').readlines()[int(sa_info['idx'])])
	if len(arch['dims']) == 1:
		if array_part_mapping[0] not in latency_hiding_mapping:
			SA_Dims = '"' + str((int(arch['dims'][0])*int(arch['SIMD']), 1)) + '"'
			PEs = int(arch['dims'][0])*int(arch['SIMD'])
		else:
			SA_Dims = '"' + str((int(arch['dims'][0]), int(arch['SIMD']))) + '"'
			PEs = prod(arch['dims'])
	elif len(arch['dims']) == 2:
		if array_part_mapping[1] not in latency_hiding_mapping:
			SA_Dims = '"' + str((int(arch['dims'][0]), int(arch['dims'][1])*int(arch['SIMD']), 1)) + '"'
			PEs = int(arch['dims'][0])*int(arch['dims'][1])*int(arch['SIMD'])
		else:
			SA_Dims = '"' + str((int(arch['dims'][0]), int(arch['dims'][1]), int(arch['SIMD']))) + '"'
			PEs = prod(arch['dims'])

	sa_sizes = get_SA_sizes(sa_info, solution, workload)
	csv_file = open(results_file, 'a')
	print(f'{design.split(".")[0]}_{idx},', end='', file=csv_file)
	print(f'{objective},', end='', file=csv_file)
	print(f'"{original_workload_size}",', end='', file=csv_file)
	print(f'"{padded_workload_size}",', end='', file=csv_file)
	print(f'{fre:.0f},', end='', file=csv_file)
	print(f'{throughput:.2f},', end='', file=csv_file)
	print(f'{cycles:.0f},', end='', file=csv_file)
	print(f'{latency:.5f},', end='', file=csv_file)
	print(f'{dsp_eff:.2f}%,', end='', file=csv_file)
	print(f'{off_chip_bytes:.0f},', end='', file=csv_file)
	print(f'{bandwidth:.2f},', end='', file=csv_file)
	print(f'{CTC:.2f},', end='', file=csv_file)
	print(f'{DSPs:.0f},', end='', file=csv_file)
	print(f'{BRAMs:.0f},', end='', file=csv_file)
	print(f'{PEs:.0f},', end='', file=csv_file)
	print(f'{SA_Dims},', end='', file=csv_file)
	print(f'{sa_sizes}', end='', file=csv_file)
	print(file=csv_file)
	csv_file.close()
	return

def get_SA_info(design):
	with open(f'{designs_dir}/{design}', 'r') as f:
		all_info = json.load(f)
	arch_info = all_info['compute']['PE']
	sa_info = {}
	sa_info['idx'] = re.split('kernel|_|\.|json', design)[1]
	sa_info['arch'] = {}
	sa_info['arch']['dims'] = len(arch_info['dims'])
	sa_info['arch']['simd'] = arch_info['unroll_factor']
	if sa_info['arch']['dims'] == 1:
		sa_info['arch']['sa_length'] = arch_info['dims'][0]
		sa_info['padding_dims'] = [arch_info['dims'][0][1]]
	elif sa_info['arch']['dims'] == 2:
		sa_info['arch']['sa_cols'] = arch_info['dims'][0]
		sa_info['arch']['sa_rows'] = arch_info['dims'][1]
		sa_info['padding_dims'] = [arch_info['dims'][0][1], arch_info['dims'][1][1]]

	SA_params = all_info['params']
	array_part = []
	latency_hiding = []    
	simd = []
	for param in SA_params:
		if param['attr'] == 'array_part_tiling_factor':
			array_part.append(param['name'])
		elif param['attr'] == 'latency_tiling_factor':
			latency_hiding.append(param['name'])
		elif param['attr'] == 'SIMD_tiling_factor':
			simd.append(param['name'])
	sa_info['array_part'] = array_part
	sa_info['latency_hiding'] = latency_hiding
	sa_info['simd'] = simd
	return sa_info

def generate_candidates(design, workload, problem_size):
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
	
	if workload == 'mm':
		I = problem_size['i']
		J = problem_size['j']
		K = problem_size['k']
		i_candidates = [x for x in range(I , I + 4)] if 'i' in paddable_dims else [I]
		j_candidates = [x for x in range(J , J + 4)] if 'j' in paddable_dims else [J]
		k_candidates = [x for x in range(K , K + 4)] if 'k' in paddable_dims else [K]
		candidates = []
		for i_t0 in i_candidates:
			for j_t0 in j_candidates:
				for k_t0 in k_candidates:
					i_t1_candidates = [x for x in range(1, i_t0+1) if i_t0 % x == 0]
					j_t1_candidates = [x for x in range(1, j_t0+1) if j_t0 % x == 0]
					k_t1_candidates = [x for x in range(1, k_t0+1) if k_t0 % x == 0]
					for i_t1 in i_t1_candidates:
						for j_t1 in j_t1_candidates:
							for k_t1 in k_t1_candidates:
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
											if perf_model.bound_check(params):
												continue
											candidates.append(params)
	elif workload == 'conv':
		I = problem_size['i']
		O = problem_size['o']
		R = problem_size['r']
		C = problem_size['c']
		P = problem_size['p']
		Q = problem_size['q']
		i_candidates = [x for x in range(I , I + 4)] if 'i' in paddable_dims else [I]
		o_candidates = [x for x in range(O , O + 4)] if 'o' in paddable_dims else [O]
		r_candidates = [x for x in range(R , R + 4)] if 'r' in paddable_dims else [R]
		c_candidates = [x for x in range(C , C + 4)] if 'c' in paddable_dims else [C]
		candidates = []
		for i_t0 in i_candidates:
			for o_t0 in o_candidates:
				for r_t0 in r_candidates:
					for c_t0 in c_candidates:
						i_t1_candidates = [x for x in range(1, i_t0+1) if i_t0 % x == 0]
						o_t1_candidates = [x for x in range(1, o_t0+1) if o_t0 % x == 0]
						r_t1_candidates = [x for x in range(1, r_t0+1) if r_t0 % x == 0]
						c_t1_candidates = [x for x in range(1, c_t0+1) if c_t0 % x == 0]
						for i_t1 in i_t1_candidates:
							for o_t1 in o_t1_candidates:
								for r_t1 in r_t1_candidates:
									for c_t1 in c_t1_candidates:
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
														if perf_model.bound_check(params):
															continue
														candidates.append(params)
	return candidates, perf_model

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
		result['arch'] = perf_model.compute_arch_cst(params)
		result['params'] = params
		result['off_chip_trans'] = perf_model.est_activity(params)['off_chip_acc_num']
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

def run(candidates, objective, design, num_top_results):

	num_processes = 32#int(multiprocessing.cpu_count() * 1)

	print('Parallelizing using %d processes...' % (num_processes))

	u250_info = json.load(open(prj_path + '/data/cst/u250.json'))
	resource_limits = {'DSP': u250_info['DSP']['total']*u250_info['DSP']['ratio'], 'BRAM18K': u250_info['BRAM18K']['total']*u250_info['BRAM18K']['ratio']}

	chunks = list_split(candidates, num_processes)
	pool = multiprocessing.Pool(processes = num_processes)
	
	if objective == 'latency':
		results = pool.starmap(run_latency_search, [(chunk, resource_limits, design, num_top_results) for chunk in chunks])
	# elif objective == 'off_chip_comm':
	# 	results = pool.starmap(run_off_chip_search, [(chunk, resource_limits, num_top_results) for chunk in chunks])
	# elif objective == 'latency_off_chip_comm':
	# 	results = pool.starmap(run_latency_off_chip_search, [(chunk, resource_limits, num_top_results, I, J, K, alpha) for chunk in chunks])
	pool.close()
	print('Finished the search!')
	# flatten the list of lists
	print('Flattening the list of lists..')
	results = [item for sublist in results for item in sublist]
	results = sorted(results, key=lambda x: x['cycles'][0])
	return results[0]

workload = sys.argv[1]
problem_size = eval(sys.argv[2])
problem_dims = [problem_size[key] for key in problem_size.keys()]
# convert [1, 2, 3] to 1_2_3
problem_dims_str = '_'.join([str(dim) for dim in problem_dims])

designs = os.listdir(f'{designs_lib_dir}/{workload}')
designs.sort()
objectives = ['latency']
# create csv file for results
results_file = prj_path + f'/tests/results/{workload}.csv'
csv_file = open(results_file, 'w')
print('design_idx,objective,original workload,padded workload,fre,throughput (GFLOP/s),cycles,latency(ms),DSP eff,off-chip bytes,bandwidth (GB/s),CTC,DSPs,BRAMs,PEs,SA_dims,sa_sizes', file=csv_file)
csv_file.close()
id = 0
outfile = open(f'{prj_path}/tests/results/{workload}_{problem_dims_str}_search_method_1.csv', 'w')
print('design_idx, cycles, search time', file=outfile)
total_time_start = time.time()
for idx in range(len(designs)):
	for objective in objectives:
		for trial in range(1):
			id += 1
			time_start = time.time()
			candidates, perf_model = generate_candidates(designs[idx], workload, problem_size)
			print(f'Generated {len(candidates)} candidates for design {designs[idx]}')
			solution = run(candidates, objective, designs[idx], 1)
			time_end = time.time()
			elapsed_time = time_end - time_start
			print(f'{idx}, {solution["cycles"][0]:.0f}, {elapsed_time:.1f}', file=outfile)

			# sa_info = get_SA_info(designs[idx])
			# print_solution(id, designs[idx], solution, sa_info, objective, workload, csv_file)
total_time_end = time.time()
print(f'Elapsed time: {total_time_end - total_time_start:.2f} seconds', file=outfile)