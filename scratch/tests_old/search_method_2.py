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
from collections import OrderedDict

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
		solution['params'] = params
		solutions.append(solution)
	return solutions

# def solver_lower_bound_mm(i_t0, j_t0, k_t0, design):
# 	solver_model = open(prj_path + '/tests/solver/tmp.mod', 'w')
# 	design_path = file_path = 'tmp/designs/' + design
# 	with open(design_path, 'r') as f:
# 		design_desc = json.load(f)
# 	print_latency_est_func(solver_model, design_desc, 'mm')
# 	solver_model.close()
# 	with open(prj_path + '/tests/solver/tmp.dat', 'w') as f:
# 		print(f'param i := {i_t0};', file = f)
# 		print(f'param j := {j_t0};', file = f)
# 		print(f'param k := {k_t0};', file = f)
# 		print(f'param dsp_bound := 8601;', file = f)
# 		print(f'param bram_bound := 3763;', file = f)
# 		print(f'param data_w := 32;', file = f)
# 	# close model file
	
# 	cmd = f'ampl solver/tmp.run | grep target'
# 	# run the command and get the output
# 	output = subprocess.check_output(cmd, shell=True)
# 	# convert the output to a string
# 	output = output.decode('utf-8')
# 	# target = #, get the number
# 	target = float(output.split()[2])
# 	return target

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
	# with open(prj_path + '/tests/tmp/designs/' + design, 'r') as f:
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
	design_path = prj_path + '/tests/tmp/designs/' + design
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

		with open(prj_path + '/tests/solver/tmp.dat', 'w') as f:
			print_data(f, design_desc, problem_size, resource_limits, other_ports)
		
		# generate tmp.mod
		with open(prj_path + '/tests/solver/tmp.mod', 'w') as f:
			print_model(f, design_desc, problem_size, resource_limits, solver_vars, solver_consts, other_ports)

		# generate tmp.run
		with open(prj_path + '/tests/solver/tmp.run', 'w') as f:
			print(f'option solver lgo;', file = f)
			# print(f"option ipopt_options 'max_iter=10000';", file = f)
			print(f'reset;', file = f)
			print(f'model {prj_path}/tests/solver/tmp.mod;', file = f)
			print(f'data {prj_path}/tests/solver/tmp.dat;', file = f)
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

def run_latency_search(candidates, resource_limits, design, num_top_results):
	design_name = design.strip('.json')
	file_path = 'tmp/designs/register/' + design_name
	file_path = file_path.replace('/', '.')
	perf_model = importlib.import_module(file_path)

	top_results = [{'cycles':[np.inf]}]*num_top_results
	for params in candidates:
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
						if not perf_model.bound_check(params):
							continue
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
		return top_results, False
	else:
		num_processes = len(candidates)
	chunks = list_split(candidates, num_processes)
	pool = multiprocessing.Pool(processes = num_processes)
	if objective == 'latency':
		results = pool.starmap(run_latency_search, [(chunk, resource_limits, design, num_top_results) for chunk in chunks])
	pool.close()
	results = [item for sublist in results for item in sublist]
	results = sorted(results, key=lambda x: x['cycles'][0])
	prev_top_results = copy.deepcopy(top_results)
	top_results.extend(results[:num_top_results])
	top_results = sorted(top_results, key=lambda x: x['cycles'][0])
	top_results = top_results[:num_top_results]
	if prev_top_results == top_results:
		return top_results, False
	else:
		return top_results, True

# def est_min_off_chip_trans(i_t0, j_t0, k_t0, perf_model, resource_limits):
#   if i_t0 > j_t0:
#     factor = 1
#     BRAMs = np.inf
#     while BRAMs > resource_limits['BRAM18K']:
#       params = {}
#       params["i"] = i_t0
#       params["j"] = j_t0
#       params["k"] = k_t0
#       params["i_t1"] = i_t0/factor
#       params["j_t1"] = j_t0
#       params["k_t1"] = 1
#       params["i_t2"] = i_t0/factor
#       params["j_t2"] = j_t0
#       params["k_t2"] = 1
#       params = perf_model.infer_params(params)
#       BRAMs = perf_model.est_resource(params)[0]['BRAM18K']
#       factor += 1
#     return perf_model.est_activity(params)['off_chip_acc_num']
#   else:
#     factor = 1
#     BRAMs = np.inf
#     while BRAMs > resource_limits['BRAM18K']:
#       params = {}
#       params["i"] = i_t0
#       params["j"] = j_t0
#       params["k"] = k_t0
#       params["i_t1"] = i_t0
#       params["j_t1"] = j_t0/factor
#       params["k_t1"] = 1
#       params["i_t2"] = i_t0
#       params["j_t2"] = j_t0/factor
#       params["k_t2"] = 1
#       params = perf_model.infer_params(params)
#       BRAMs = perf_model.est_resource(params)[0]['BRAM18K']
#       factor += 1
#     return perf_model.est_activity(params)['off_chip_acc_num']

# def est_cycles(i_t0, j_t0, k_t0, perf_model, resource_limits):
# 	factor = 1
# 	DSPs = np.inf
# 	while DSPs > resource_limits['DSP']:
# 		params = {}
# 		params["i"] = i_t0
# 		params["j"] = j_t0
# 		params["k"] = k_t0
# 		params["i_t1"] = i_t0/2
# 		params["j_t1"] = j_t0/factor
# 		params["k_t1"] = 16
# 		params["i_t2"] = 1
# 		params["j_t2"] = 16
# 		params["k_t2"] = 1
# 		params = perf_model.infer_params(params)
# 		DSPs = perf_model.est_resource(params)[0]['DSP']
# 		factor += 1
# 	return perf_model.est_latency(params)[0]


def search_latency(design, objective, workload, problem_size, num_top_results, threshold):
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
		i_t0, j_t0, k_t0 = I, J, K

		i_bound = np.inf if 'i' in paddable_dims else I
		j_bound = np.inf if 'j' in paddable_dims else J
		k_bound = np.inf if 'k' in paddable_dims else K
		i_counter = 0
		j_counter = 0
		k_counter = 0
		is_k_updated = False
		is_j_updated = False
		is_i_updated = False
		
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
					top_results, is_k_updated = search(candidates, design, top_results, resource_limits, num_top_results)
					time_end = time.time()
					search_time = time_end - time_start
					print(f'candidate ({i_t0}, {j_t0}, {k_t0})','current min_latency = ', top_results[-1]['cycles'][0], is_k_updated, is_j_updated, is_i_updated)

					if is_k_updated:
						k_counter = 0
						is_j_updated = True
					else:
						k_counter += 1
						is_j_updated = False

					k_t0 += 1

					if k_counter >= threshold or k_t0 > k_bound:
						k_counter = 0
						k_t0 = K
						break
				
				if is_j_updated:
					j_counter = 0
					is_i_updated = True
				else:
					j_counter += 1
					is_i_updated = False
				
				j_t0 += 1

				if j_counter >= threshold or j_t0 > j_bound:
					j_counter = 0
					j_t0 = J
					break
			if is_i_updated:
				i_counter = 0
			else:
				i_counter += 1

			i_t0 += 1

			if i_counter >= threshold or i_t0 > i_bound:
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
		padded_problem_size = {'i':i_t0, 'o':o_t0, 'r':r_t0, 'c':c_t0, 'p':p_t0, 'q':q_t0}
		min_theoratical_latency = solver_lower_bound_conv(i_t0, o_t0, r_t0, c_t0, p_t0, q_t0, design, padded_problem_size, resource_limits)
		
		i_bound = np.inf if 'i' in paddable_dims else I
		o_bound = np.inf if 'o' in paddable_dims else O
		r_bound = np.inf if 'r' in paddable_dims else R
		c_bound = np.inf if 'c' in paddable_dims else C
		i_counter = 0
		o_counter = 0
		r_counter = 0
		c_counter = 0
		is_c_updated = False
		is_r_updated = False
		is_o_updated = False
		is_i_updated = False
		
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
						top_results, is_c_updated = search(candidates, design, top_results, resource_limits, num_top_results)
						time_end = time.time()
						search_time = time_end - time_start
						print(f'candidate ({i_t0}, {o_t0}, {r_t0}, {c_t0})', 'current min_latency = ', top_results[-1]['cycles'][0], is_c_updated, is_r_updated, is_o_updated, is_i_updated)

						if is_c_updated:
							c_counter = 0
							is_r_updated = True
						else:
							c_counter += 1
							is_r_updated = False

						c_t0 += 1

						if c_counter >= threshold or c_t0 > c_bound:
							c_counter = 0
							c_t0 = C
							break

					if is_r_updated:
						r_counter = 0
						is_o_updated = True
					else:
						r_counter += 1
						is_o_updated = False

					r_t0 += 1

					if r_counter >= threshold or r_t0 > r_bound:
						r_counter = 0
						r_t0 = R
						break
				if is_o_updated:
					o_counter = 0
					is_i_updated = True
				else:
					o_counter += 1
					is_i_updated = False

				o_t0 += 1

				if o_counter >= threshold or o_t0 > o_bound:
					o_counter = 0
					o_t0 = O
					break

			if is_i_updated:
				i_counter = 0
			else:
				i_counter += 1

			i_t0 += 1

			if i_counter >= threshold or i_t0 > i_bound:
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
results_file = prj_path + f'/tests/results/{workload}_{problem_dims_str}_search_method_2'
csv_file = open(results_file + '.csv', 'w')
print('design_idx,search time (s),objective,original workload,padded workload,fre,throughput (GFLOP/s),cycles,latency(ms),DSP eff,off-chip bytes,bandwidth (GB/s),CTC,DSPs,BRAMs,PEs,SA_dims,sa_sizes', file=csv_file)
csv_file.close()
id = 0
total_time_start = time.time()
threshold = 10
num_top_results = 10
for idx in range(7,8):#len(designs)):
	for objective in objectives:
		for trial in range(1):
			id += 1
			time_start = time.time()
			solutions = search_latency(designs[idx],objective, workload, problem_size, num_top_results, threshold)
			# solution = solutions[0]
			time_end = time.time()
			elapsed_time = time_end - time_start
			sa_info = get_SA_info(designs[idx])
			for solution in solutions:
				print_solution(id, designs[idx], solution, sa_info, objective, workload, elapsed_time, results_file + '.csv')
total_time_end = time.time()
with open(results_file + '.log', 'w') as f:
	print(f'Elapsed time: {total_time_end - total_time_start:.2f} seconds', file=f)