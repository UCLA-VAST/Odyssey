import os
import json
import importlib
import re
from math import ceil
from math import prod
import numpy as np
prj_path = os.environ["PRJ_PATH"]
import sys
sys.path.append(f'{prj_path}/src/randomized_search')
from design import Design
from math import log2, sqrt
from tqdm import tqdm
import itertools
import random
import pandas as pd

random.seed(0)
designs_lib_dir = prj_path + f'/data/designs_lib'
designs_dir = prj_path + '/tests/tmp/designs'
output_dir = prj_path + '/tests/tmp/outputs'

# def get_column_sum(df, column):
# 	return df[column].sum()
def get_data(workload, problem_dims_str, alpha, num_top_results, threshold, objective):
	prj_path = os.environ["PRJ_PATH"]
	results_path = f'{prj_path}/results/{workload}/{problem_dims_str}/design_all_all/{objective}/'

	cycles_dict = {}
	throughput_dict = {}
	runtime_dict = {}
	all_designs_dict = {}
	valid_designs_dict = {}

	# exhaustive
	search_method = 'exhaustive'
	cycles_dict[search_method] = 0
	throughput_dict[search_method] = 0
	runtime_dict[search_method] = 0
	all_designs_dict[search_method] = 0
	valid_designs_dict[search_method] = 0
	# regex first file ending with .csv
	if os.path.exists(f'{results_path}{search_method}/results/'):
		csv_file = f'{results_path}{search_method}/results/top_{num_top_results}_alpha_{alpha}.csv'
		if os.path.exists(csv_file):
			df = pd.read_csv(csv_file)
			# sort df by 'cycles'
			df = df.sort_values(by=['cycles'])
			# print cycles of top 1 design
			if len(df) > 0:
				cycles_dict[search_method] = df.iloc[0]["cycles"]
				throughput_dict[search_method] = df.iloc[0]["throughput (GFLOP/s)"]
				runtime_dict[search_method] = int(df['search_time'].sum())
				all_designs_dict[search_method] = int(sum([eval(x) for x in df['all_designs'].tolist()]))
				valid_designs_dict[search_method] = int(sum([eval(x) for x in df['valid_designs'].tolist()]))
			else:
				print(f'{csv_file} is empty')
		else:
			print(f'{csv_file} does not exist')
	else:
		print(f'{results_path}{search_method}/results/ does not exist')

	# non_divisors
	search_method = 'non_divisors'
	cycles_dict[search_method] = 0
	throughput_dict[search_method] = 0
	runtime_dict[search_method] = 0
	all_designs_dict[search_method] = 0
	valid_designs_dict[search_method] = 0
	# regex first file ending with .csv
	if os.path.exists(f'{results_path}{search_method}/results/'):
		csv_file = f'{results_path}{search_method}/results/top_{num_top_results}_alpha_{alpha}_thr_{threshold}.csv'
		if os.path.exists(csv_file):
			df = pd.read_csv(csv_file)
			# sort df by 'cycles'
			df = df.sort_values(by=['cycles'])
			# print cycles of top 1 design
			if len(df) > 0:
				cycles_dict[search_method] = df.iloc[0]["cycles"]
				throughput_dict[search_method] = df.iloc[0]["throughput (GFLOP/s)"]
				runtime_dict[search_method] = int(df['search_time'].sum())
				all_designs_dict[search_method] = int(sum([eval(x) for x in df['all_designs'].tolist()]))
				valid_designs_dict[search_method] = int(sum([eval(x) for x in df['valid_designs'].tolist()]))
			else:
				print(f'{csv_file} is empty')
		else:
			print(f'{csv_file} does not exist')
	else:
		print(f'{results_path}{search_method}/results/ does not exist')
	
	# divisors
	search_method = 'divisors'
	cycles_dict[search_method] = 0
	throughput_dict[search_method] = 0
	runtime_dict[search_method] = 0
	all_designs_dict[search_method] = 0
	valid_designs_dict[search_method] = 0
	# regex first file ending with .csv
	if os.path.exists(f'{results_path}{search_method}/results/'):
		csv_file = f'{results_path}{search_method}/results/top_{num_top_results}_alpha_{alpha}_thr_{0}.csv'
		if os.path.exists(csv_file):
			df = pd.read_csv(csv_file)
			# sort df by 'cycles'
			df = df.sort_values(by=['cycles'])
			# print cycles of top 1 design
			if len(df) > 0:
				cycles_dict[search_method] = df.iloc[0]["cycles"]
				throughput_dict[search_method] = df.iloc[0]["throughput (GFLOP/s)"]
				runtime_dict[search_method] = int(df['search_time'].sum())
				all_designs_dict[search_method] = int(sum([eval(x) for x in df['all_designs'].tolist()]))
				valid_designs_dict[search_method] = int(sum([eval(x) for x in df['valid_designs'].tolist()]))
			else:
				print(f'{csv_file} is empty')
		else:
			print(f'{csv_file} does not exist')
	else:
		print(f'{results_path}{search_method}/results/ does not exist')
	
	# odyssey
	search_method = 'odyssey'
	cycles_dict[search_method] = 0
	throughput_dict[search_method] = 0
	runtime_dict[search_method] = 0
	all_designs_dict[search_method] = 0
	valid_designs_dict[search_method] = 0
	# regex first file ending with .csv
	if os.path.exists(f'{results_path}{search_method}/results/'):
		csv_file = f'{results_path}{search_method}/results/alpha_{alpha}.csv'
		if os.path.exists(csv_file):
			df = pd.read_csv(csv_file)
			# sort df by 'cycles'
			df = df.sort_values(by=['cycles'])
			# print cycles of top 1 design
			if len(df) > 0:
				cycles_dict[search_method] = df.iloc[0]["cycles"]
				throughput_dict[search_method] = df.iloc[0]["throughput (GFLOP/s)"]
				runtime_dict[search_method] = int(df['search_time'].sum())
				all_designs_dict[search_method] = 0#int(sum([eval(x) for x in df['all_designs'].tolist()]))
				valid_designs_dict[search_method] = 0#int(sum([eval(x) for x in df['valid_designs'].tolist()]))
			else:
				print(f'{csv_file} is empty')
		else:
			print(f'{csv_file} does not exist')
	else:
		print(f'{results_path}{search_method}/results/ does not exist')
	
	return cycles_dict, throughput_dict, runtime_dict, all_designs_dict, valid_designs_dict

def sqrt_bound(dim, threshold):
	return threshold*sqrt(dim)

def get_num_of_designs_ub(workload, problem_size):
	""" Get the upper bound of the number of designs.
	"""
	if workload == 'mm':
		I, J, K = problem_size['i'], problem_size['j'], problem_size['k']
		i_t0_candidates = get_padded_candidates(I)
		j_t0_candidates = get_padded_candidates(J)
		k_t0_candidates = [K]
		i_t1_candidates = [x for x in range(1, I)]
		j_t1_candidates = [x for x in range(1, J)]
		k_t1_candidates = [x for x in range(1, K) if (log2(x) == int(log2(x)))]
		i_t1_candidates = i_t1_candidates + i_t0_candidates
		j_t1_candidates = j_t1_candidates + j_t0_candidates
		k_t1_candidates = k_t1_candidates + k_t0_candidates
		counter = 0
		for i_t1 in tqdm(i_t1_candidates):
			for j_t1 in j_t1_candidates:
				for k_t1 in k_t1_candidates:
					counter += i_t1*j_t1*k_t1
		return counter				
	elif workload == 'conv':
		I, O, R, C, P, Q = problem_size['i'], problem_size['o'], problem_size['r'], problem_size['c'], problem_size['p'], problem_size['q']
		i_t0_candidates = [I]
		o_t0_candidates = get_padded_candidates(O)
		r_t0_candidates = get_padded_candidates(R)
		c_t0_candidates = get_padded_candidates(C)
		i_t1_candidates = [x for x in range(1, I) if (log2(x) == int(log2(x)))]
		o_t1_candidates = [x for x in range(1, O)]
		r_t1_candidates = [x for x in range(1, R)]
		c_t1_candidates = [x for x in range(1, C)]		
		i_t1_candidates = i_t1_candidates + i_t0_candidates
		o_t1_candidates = o_t1_candidates + o_t0_candidates
		r_t1_candidates = r_t1_candidates + r_t0_candidates
		c_t1_candidates = c_t1_candidates + c_t0_candidates			
		counter = 0
		for i_t1 in tqdm(i_t1_candidates):
			for o_t1 in o_t1_candidates:
				for r_t1 in r_t1_candidates:
					for c_t1 in c_t1_candidates:
						counter += i_t1*o_t1*r_t1*c_t1
		return counter

def get_num_of_designs_lb(workload, problem_size):
	if workload == 'mm':
		I, J, K = problem_size['i'], problem_size['j'], problem_size['k']
		i_t0_candidates = get_padded_candidates(I)
		j_t0_candidates = get_padded_candidates(J)
		k_t0_candidates = [K]
		i_t1_candidates = [x for x in range(1, I)]
		j_t1_candidates = [x for x in range(1, J)]
		k_t1_candidates = [x for x in range(1, K) if (log2(x) == int(log2(x)))]
		i_t1_candidates = i_t1_candidates + i_t0_candidates
		j_t1_candidates = j_t1_candidates + j_t0_candidates
		k_t1_candidates = k_t1_candidates + k_t0_candidates
		counter = len(i_t1_candidates)*len(j_t1_candidates)*len(k_t1_candidates)
		return counter		
	elif workload == 'conv':
		I, O, R, C, P, Q = problem_size['i'], problem_size['o'], problem_size['r'], problem_size['c'], problem_size['p'], problem_size['q']
		i_t0_candidates = [I]
		o_t0_candidates = get_padded_candidates(O)
		r_t0_candidates = get_padded_candidates(R)
		c_t0_candidates = get_padded_candidates(C)
		i_t1_candidates = [x for x in range(1, I) if (log2(x) == int(log2(x)))]
		o_t1_candidates = [x for x in range(1, O)]
		r_t1_candidates = [x for x in range(1, R)]
		c_t1_candidates = [x for x in range(1, C)]		
		i_t1_candidates = i_t1_candidates + i_t0_candidates
		o_t1_candidates = o_t1_candidates + o_t0_candidates
		r_t1_candidates = r_t1_candidates + r_t0_candidates
		c_t1_candidates = c_t1_candidates + c_t0_candidates				
		counter = len(i_t1_candidates)*len(o_t1_candidates)*len(r_t1_candidates)*len(c_t1_candidates)
		return counter

def get_num_of_designs(workload, problem_size):
	if workload == 'mm':
		I, J, K = problem_size['i'], problem_size['j'], problem_size['k']
		i_t0_candidates = get_padded_candidates(I)
		j_t0_candidates = get_padded_candidates(J)
		k_t0_candidates = [K]
		i_t1_candidates = [x for x in range(1, I)]
		j_t1_candidates = [x for x in range(1, J)]
		k_t1_candidates = [x for x in range(1, K) if (log2(x) == int(log2(x)))]
		i_t1_candidates = i_t1_candidates + i_t0_candidates
		j_t1_candidates = j_t1_candidates + j_t0_candidates
		k_t1_candidates = k_t1_candidates + k_t0_candidates
		counter = 0
		for i_t1 in tqdm(i_t1_candidates):
			i_t2_candidates = [x for x in range(1, i_t1+1) if i_t1 % x == 0]
			for j_t1 in j_t1_candidates:
				j_t2_candidates = [x for x in range(1, j_t1+1) if j_t1 % x == 0]
				for k_t1 in k_t1_candidates:
					k_t2_candidates = [x for x in range(1, k_t1+1) if k_t1 % x == 0]  
					counter += len(i_t2_candidates)*len(j_t2_candidates)*len(k_t2_candidates)

		return counter
	elif workload == 'conv':
		I, O, R, C, P, Q = problem_size['i'], problem_size['o'], problem_size['r'], problem_size['c'], problem_size['p'], problem_size['q']
		i_t0_candidates = [I]
		o_t0_candidates = get_padded_candidates(O)
		r_t0_candidates = get_padded_candidates(R)
		c_t0_candidates = get_padded_candidates(C)
		i_t1_candidates = [x for x in range(1, I) if (log2(x) == int(log2(x)))]
		o_t1_candidates = [x for x in range(1, O)]
		r_t1_candidates = [x for x in range(1, R)]
		c_t1_candidates = [x for x in range(1, C)]		
		i_t1_candidates = i_t1_candidates + i_t0_candidates
		o_t1_candidates = o_t1_candidates + o_t0_candidates
		r_t1_candidates = r_t1_candidates + r_t0_candidates
		c_t1_candidates = c_t1_candidates + c_t0_candidates				
		counter = 0
		for i_t1 in tqdm(i_t1_candidates):
			i_t2_candidates = [x for x in range(1, i_t1+1) if i_t1 % x == 0]
			for o_t1 in o_t1_candidates:
				o_t2_candidates = [x for x in range(1, o_t1+1) if o_t1 % x == 0]
				for r_t1 in r_t1_candidates:
					r_t2_candidates = [x for x in range(1, r_t1+1) if r_t1 % x == 0]
					for c_t1 in c_t1_candidates:
						c_t2_candidates = [x for x in range(1, c_t1+1) if c_t1 % x == 0]
						counter += len(i_t2_candidates)*len(o_t2_candidates)*len(r_t2_candidates)*len(c_t2_candidates)
		return counter

def est_num_of_designs(workload, problem_size, num_trails):
	if workload == 'mm':
		I, J, K = problem_size['i'], problem_size['j'], problem_size['k']
		i_t0_candidates = get_padded_candidates(I)
		j_t0_candidates = get_padded_candidates(J)
		k_t0_candidates = [K]
		i_t1_candidates = [x for x in range(1, I)]
		j_t1_candidates = [x for x in range(1, J)]
		k_t1_candidates = [x for x in range(1, K) if (log2(x) == int(log2(x)))]
		i_t1_candidates = i_t1_candidates + i_t0_candidates
		j_t1_candidates = j_t1_candidates + j_t0_candidates
		k_t1_candidates = k_t1_candidates + k_t0_candidates
		rand_it_1 = random.sample(i_t1_candidates, min(num_trails, len(i_t1_candidates)))
		rand_jt_1 = random.sample(j_t1_candidates, min(num_trails, len(j_t1_candidates)))
		rand_kt_1 = random.sample(k_t1_candidates, min(num_trails, len(k_t1_candidates)))
		all_candidates = len(i_t1_candidates)*len(j_t1_candidates)*len(k_t1_candidates)
		avg_count = 0
		for idx in range(num_trails):
			i_t1, j_t1, k_t1 = rand_it_1[idx%len(i_t1_candidates)], rand_jt_1[idx%len(j_t1_candidates)], rand_kt_1[idx%len(k_t1_candidates)]
			i_t2_candidates = [x for x in range(1, i_t1+1) if i_t1 % x == 0]
			j_t2_candidates = [x for x in range(1, j_t1+1) if j_t1 % x == 0]
			k_t2_candidates = [x for x in range(1, k_t1+1) if k_t1 % x == 0]  
			avg_count += len(i_t2_candidates)*len(j_t2_candidates)*len(k_t2_candidates)
		avg_count = avg_count/num_trails
		counter = avg_count*all_candidates
		return int(counter)
	elif workload == 'conv':
		I, O, R, C, P, Q = problem_size['i'], problem_size['o'], problem_size['r'], problem_size['c'], problem_size['p'], problem_size['q']
		i_t0_candidates = [I]
		o_t0_candidates = get_padded_candidates(O)
		r_t0_candidates = get_padded_candidates(R)
		c_t0_candidates = get_padded_candidates(C)
		i_t1_candidates = [x for x in range(1, I) if (log2(x) == int(log2(x)))]
		o_t1_candidates = [x for x in range(1, O)]
		r_t1_candidates = [x for x in range(1, R)]
		c_t1_candidates = [x for x in range(1, C)]		
		i_t1_candidates = i_t1_candidates + i_t0_candidates
		o_t1_candidates = o_t1_candidates + o_t0_candidates
		r_t1_candidates = r_t1_candidates + r_t0_candidates
		c_t1_candidates = c_t1_candidates + c_t0_candidates		
		rand_it_1 = random.sample(i_t1_candidates, min(num_trails, len(i_t1_candidates)))
		rand_ot_1 = random.sample(o_t1_candidates, min(num_trails, len(o_t1_candidates)))
		rand_rt_1 = random.sample(r_t1_candidates, min(num_trails, len(r_t1_candidates)))
		rand_ct_1 = random.sample(c_t1_candidates, min(num_trails, len(c_t1_candidates)))
		all_candidates = len(i_t1_candidates)*len(o_t1_candidates)*len(r_t1_candidates)*len(c_t1_candidates)
		avg_count = 0
		for idx in range(num_trails):
			# get random points from candidates
			i_t1, o_t1, r_t1, c_t1 = rand_it_1[idx%len(i_t1_candidates)], rand_ot_1[idx%len(o_t1_candidates)], rand_rt_1[idx%len(r_t1_candidates)], rand_ct_1[idx%len(c_t1_candidates)]
			i_t2_candidates = [x for x in range(1, i_t1+1) if i_t1 % x == 0]
			o_t2_candidates = [x for x in range(1, o_t1+1) if o_t1 % x == 0]
			r_t2_candidates = [x for x in range(1, r_t1+1) if r_t1 % x == 0]
			c_t2_candidates = [x for x in range(1, c_t1+1) if c_t1 % x == 0]
			avg_count += len(i_t2_candidates)*len(o_t2_candidates)*len(r_t2_candidates)*len(c_t2_candidates)
		avg_count = avg_count/num_trails		
		counter = avg_count*all_candidates
		return int(counter)

def est_off_chip_trans(activity, workload):   
	off_chip_acc_num_meta = activity['off_chip_acc_num_meta']
	if workload == 'conv':
		cin_trans = 0
		w_trans = 0
		cout_trans = 0
		for module in off_chip_acc_num_meta:
			if module.startswith("cin"):
				cin_trans = off_chip_acc_num_meta[module]
			if module.startswith("w"):
				w_trans = off_chip_acc_num_meta[module]
			if module.startswith("cout"):
				cout_trans = off_chip_acc_num_meta[module]
		return cin_trans + w_trans + cout_trans
	elif workload == 'mm':
		return activity["off_chip_acc_num"]      

def get_padded_candidates(n):
	candidates = [x for x in range(1,n)]
	padded_sizes = []
	for i in candidates:
		padded_size = ceil(n/i)*i
		padded_sizes.append(padded_size)
	padded_sizes = list(set(padded_sizes))
	# sort
	padded_sizes.sort()
	return padded_sizes

def get_resource_limits(board):
	board_info = json.load(open(prj_path + f'/data/cst/{board}.json'))
	resource_limits = {'DSP': board_info['DSP']['total']*board_info['DSP']['ratio'], 'BRAM18K': board_info['BRAM18K']['total']*board_info['BRAM18K']['ratio']}
	return resource_limits

def get_paddable_dims(workload):
	if workload == 'mm':
		return ['i', 'j']
	elif workload == 'conv':
		return ['o', 'r', 'c']
	# with open(f'{designs_dir}/{design}', 'r') as f:
	# 	design_desc = json.load(f)
	# # load perf model
	# sa_dims = design_desc['compute']['PE']['dims']
	# sa_simd = design_desc['compute']['PE']['unroll_factor'][0]
	# paddable_dims = []
	# for dim in sa_dims:
	# 	if sa_simd != dim[1]:
	# 		paddable_dims.append(dim[1])
	# return paddable_dims

def gen_perf_model(design, workload, permutation):
	# gen performance model
	design_name = design.strip('.json')
	file_path = 'tmp/designs/register/' + design_name
	file_path = file_path.replace('/', '.')
	# os.system(f'rm -rf {designs_dir}/*')
	os.makedirs(f'tmp/designs/register', exist_ok=True)
	copy_design(design, workload, permutation)
	# generate performance model
	with open(f'{designs_dir}/{design}', 'r') as f:
		design_desc = json.load(f)
		Design(design_name).register(design_desc, f'tmp/designs/register/{design_name}.py')

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
		result['off_chip_trans'] = est_off_chip_trans(activity, workload)		
		ops = compute_ops(workload, problem_size)
		solution['arch_sol'] = params
		solution['DSPs'] = resources['DSP']
		solution['BRAMs'] = resources['BRAM18K']
		solution['cycles'] = cycles
		solution['dsp_eff'] = compute_dsp_eff(cycles, workload, problem_size, resources['DSP'])*100
		solution['fre'] = fre
		solution['latency'] = cycles/(fre*1e6)
		solution['throughput'] = (ops/1e9)/(cycles/(fre*1e6))
		solution['off_chip_bytes'] = result['off_chip_trans']*4 #bytes
		solution['bandwidth'] = compute_bw(params, cycles, result['off_chip_trans'], dw, fre)
		solution['CTC'] = compute_ctc(params, workload, problem_size, result['off_chip_trans'], dw)
		solution['params'] = params
		solutions.append(solution)
	return solutions

def print_model_params(f, desp, problem_size, resource_limits, solver_vars, solver_consts, other_ports):
	for p in desp["params"]:
		if p["name"] in problem_size:
			f.write(f'param {p["name"]};\n')
		elif 't' in p["name"]:
			problem_dim = p["name"].split('_')[0]
			f.write(f'var {p["name"]} integer >= 1, <= {problem_dim};\n')
	for port in other_ports.keys():
		f.write(f'param {port};\n')
	for port in solver_vars:
		f.write(f'var {port[0]} integer >= 1, <= {port[1]};\n')
	for port in solver_consts:
		f.write(f'var {port[0]} = {port[1]};\n')
	f.write(f'param bram_bound;\n')
	f.write(f'param dsp_bound;\n')

def print_model_target(f, desp):
	def extract_latency_expr(lat, info):
		ret = ""
		if lat["type"] == "block":
			info["has_for_child"] = 0
			no_for_child = True
			is_first = True
			ret += "("
			for child in lat["child"]:
				if not is_first:
					ret += " + "                    
				ret += extract_latency_expr(child, info)                    
				if info["has_for_child"] == 1:
					no_for_child = False
				is_first = False
			ret += ")"
			if no_for_child:
				ret = "1"
		elif lat["type"] == "for":                
			child = lat["child"]
			expr = extract_latency_expr(child, info)                
			if info["valid"]:
				ret = lat["bounds"][1] + " * " + expr
			else:
				ret = expr
			info["has_for_child"] = 1
		elif lat["type"] == "mark":      
			if info["under_mark"] and lat["content"] == info["under_mark"]:
				info["valid"] = True
			if lat["content"] == "simd":
				if info["valid"]:
					ret = "1"
				else:
					ret = "0"
			else:
				child = lat["child"]
				ret = extract_latency_expr(child, info)
			if info["under_mark"] and lat["content"] == info["under_mark"]:
				info["valid"] = False
		elif lat["type"] == "user":
			user_expr = lat["child"]["user_expr"]
			if 'inter_intra' in user_expr or 'intra_inter' in user_expr:                    
				if user_expr[:-2].split(".")[-1] == "1":
					double_buffer = 1
				else:
					double_buffer = 0                    
				# Plug in submodule latency
				if f"{info['name']}_inter" in info["modules"]:
					inter_expr = info["modules"][f"{info['name']}_inter"]
				else:
					inter_expr = None
				if f"{info['name']}_intra" in info["modules"]:
					intra_expr = info["modules"][f"{info['name']}_intra"]
				else:
					intra_expr = None

				if inter_expr and intra_expr:
					if info["in"] == 1 or info["in"] == 0:
						ret = inter_expr
					else:
						if double_buffer:
							ret = f"max({inter_expr}, {intra_expr})"
						else:
							ret = f"({inter_expr} + {intra_expr})"
					info["has_for_child"] = 1
				else:                        
					ret = "1"                        
				if not info["valid"]:
					ret = "0"
			elif "inter_trans" in user_expr:
				# Plug in submodule latency
				if f"{info['name']}_inter" in info["modules"]:
					ret = info["modules"][f"{info['name']}_inter"]
				else:
					ret = "1"
				if not info["valid"]:
					ret = "0"
			elif "intra_trans" in user_expr:
				# Plug in submodule latency                    
				if f"{info['name']}_intra" in info["modules"]:
					ret = info["modules"][f"{info['name']}_intra"]
				else:
					ret = "1"
				if not info["valid"]:
					ret = "0"
			else:
				ret = "1"
		elif lat["type"] == "if":
			# Only examine the first child
			child = lat["child"][0]
			ret = extract_latency_expr(child, info)
		elif lat["type"] == "array_tile":      
			if info["module_attr"]["to_dram"] == 1:
				if info["module_attr"]["serialize"] == 0:
					# Consider the DRAM latency here.
					ret = "(" + f"{lat['size']}/{lat['last_dim']}*(20+{lat['last_dim']}/(512/8/{lat['ele_size']}))" + ")"
				else:
					ret = "(" + lat["size"] + "/" + f"min({lat['data_pack_factor']}, 512/8/{lat['ele_size']})" + ")"
			else:
				ret = "(" + lat["size"] + "/" + lat["data_pack_factor"] + ")"                    
		else:
			raise RuntimeError(f"Unsupported latency node type {lat['type']}")

		return ret

	# Check if drain module can be omitted
	# Note: It should be supported in the codegen of AutoSA. However, currently,
	# we move it here in the tuner.        
	out_module = {}
	out_drain_module = {}
	for module in desp["memory"]:
		module_mem = desp["memory"][module]
		if module.endswith('_out'):
			item = {'buf_size': module_mem['buf_size'], 
					'num': module_mem['num']}
			if module.find('drain') != -1:
				item['merged'] = 0
				out_drain_module[module_mem['array']] = item
			else:                    
				if module_mem['array'] not in out_module:
					out_module[module_mem['array']] = [item]
				else:
					out_module[module_mem['array']].append(item)
	for array in out_drain_module:
		if array in out_module:
			for m in out_module[array]:                
				if m['buf_size'] == out_drain_module[array]['buf_size'] and \
					m['num'] == out_drain_module[array]['num']:
					out_drain_module[array]['merged'] = 1

	f.write('\n')
	f.write('minimize target:\n')
	
	f.write('max(\n')
	# Latency prologue
	latency_prologue_items = []
	info = {"has_for_child": 0, "name": None, "modules": {}}
	for i in range(2):
			for module in desp["latency"]:
					if desp["attr"][module]["in"] != 1:
							continue
					if "inter" in module or "intra" in module:                    
							# Keep all the latency AST under the mark.
							info["valid"] = True
							info["under_mark"] = None
							info["in"] = 1
					else:
							# Only keep the latency AST under the mark.
							info["valid"] = False
							info["under_mark"] = "array"
							info["in"] = 1
					module_lat = desp["latency"][module]  
					info["name"] = module     
					info["module_attr"] = desp["attr"][module]
					info["modules"][module] = extract_latency_expr(module_lat, info)
	num_modules = 0
	for module in info["modules"]: 
		if "inter" in module or "intra" in module:
				continue
		if module.find('drain') != -1 and out_drain_module[module_mem['array']]['merged'] == 1:
				continue
		num_modules += 1
	counter = 0
	for module in info["modules"]: 
			if "inter" in module or "intra" in module:
					continue
			if module.find('drain') != -1 and out_drain_module[module_mem['array']]['merged'] == 1:
					continue
			info["modules"][module] = re.sub(r'ceil\(', '(', info["modules"][module])  
			# info["modules"][module] = re.sub(r'p16', 'p15', info["modules"][module])             
			f.write('\t' + info["modules"][module])
			counter += 1
			if counter <= num_modules - 1:
				f.write(',\n')
			else:
				f.write('\n')
	f.write(') + \n')

	f.write('max(\n')
	# Latency epilogue
	latency_epilogue_items = []
	info = {"has_for_child": 0, "name": None, "modules": {}}
	for i in range(2):
			for module in desp["latency"]:
					if desp["attr"][module]["in"] != 0:
							continue
					if "inter" in module or "intra" in module:
							info["valid"] = True
							info["under_mark"] = None
							info["in"] = 0
					else:
							info["valid"] = False
							info["under_mark"] = "array"
							info["in"] = 0
					module_lat = desp["latency"][module]  
					info["name"] = module                
					info["module_attr"] = desp["attr"][module]
					info["modules"][module] = extract_latency_expr(module_lat, info)
	num_modules = 0
	for module in info["modules"]:            
		if "inter" in module or "intra" in module:
				continue
		if module.find('drain') != -1:
				array_name = module[:module.find("_drain_IO")]                
				if out_drain_module[array_name]['merged'] == 1:
						continue
		num_modules += 1
	counter = 0
	for module in info["modules"]:            
			if "inter" in module or "intra" in module:
					continue
			if module.find('drain') != -1:
					array_name = module[:module.find("_drain_IO")]                
					if out_drain_module[array_name]['merged'] == 1:
							continue
			info["modules"][module] = re.sub(r'ceil\(', '(', info["modules"][module])
			# info["modules"][module] = re.sub(r'p16', 'p15', info["modules"][module])             
			f.write('\t' + info["modules"][module])
			counter += 1
			if counter <= num_modules - 1:
				f.write(',\n')
			else:
				f.write('\n')
	f.write(') + \n')

	f.write('max(\n')

	# Latency main
	latency_main_items = []
	info = {"has_for_child": 0, "name": None, "modules": {}}
	for i in range(2):
		# Run second time to fill in the incomplete expression            
		for module in desp["latency"]:
			module_lat = desp["latency"][module]  
			info["name"] = module
			info["valid"] = True
			info["under_mark"] = None
			info["in"] = -1
			info["module_attr"] = desp["attr"][module]
			info["modules"][module] = extract_latency_expr(module_lat, info)            
	num_modules = 0
	for module in info["modules"]:
		if "inter" in module or "intra" in module:
			continue
		if module.find('drain') != -1:
			array_name = module[:module.find("_drain_IO")]                
			if out_drain_module[array_name]['merged'] == 1:
				continue
		num_modules += 1
	counter = 0
	for module in info["modules"]:
		if "inter" in module or "intra" in module:
			continue
		if module.find('drain') != -1:
			array_name = module[:module.find("_drain_IO")]                
			if out_drain_module[array_name]['merged'] == 1:
				continue
		# regex replace ceil with ceil_ceil
		info["modules"][module] = re.sub(r'ceil\(', '(', info["modules"][module])
		# info["modules"][module] = re.sub(r'p16', 'p15', info["modules"][module])             
		f.write('\t'+info["modules"][module])
		counter += 1
		if counter <= num_modules - 1:
			f.write(',\n')
		else:
			f.write('\n')
	f.write(');\n') 
	f.write('\n')
	# if workload == 'mm':
	# 	f.write('subject to DSP_cst:\n')
	# 	f.write('	0 <= (i_t1/i_t2)*(j_t1/j_t2)*k_t2*5 <= dsp_bound;\n')
	# 	f.write('\n')
	# 	f.write('subject to latency_hiding_cst:\n')
	# 	f.write('	i_t2*j_t2 >= 8*k_t2;\n')
	# elif workload == 'conv':
		# f.write('subject to DSP_cst:\n')
		# f.write('	0 <= (r_t1/r_t2)*(c_t1/c_t2)*i_t2*5 <= dsp_bound;\n')
		# f.write('\n')
		# f.write('subject to BRAM_cst:\n')
		# f.write(f'\t0 <= \n')
		# f.write(f'\tceil(4*8*1 / 36) * ceil(((r_t2*c_t2)*o_t1)/1/512) * 1 * ((r_t1/r_t2)*(c_t1/c_t2)) + \n')
		# f.write(f'\tceil(4*8*1 / 36) * ceil((((((r_t2-1)+(p-1))+1)*(((c_t2-1)+(q-1))+1))*i_t1)/1/512) * 2 * ((c_t1/c_t2)*(r_t1/r_t2)) + \n')
		# f.write(f'\tceil(4*8*1 / 36) * ceil(((r_t2*c_t2)*o_t1)/1/512) * 2 * ((c_t1/c_t2)*(r_t1/r_t2)) + \n')
		# f.write(f'\tceil(4*8*1 / 36) * ceil(((r_t2*c_t2)*o_t1)/1/512) * 2 * ((c_t1/c_t2)*(r_t1/r_t2)) + \n')
		# f.write(f'\tceil(4*8*1 / 36) * ceil((((o_t1*((p-1)+1))*((q-1)+1))*i_t1)/1/512) * 2 * (c_t1/c_t2) \n')
		# f.write(f'\t<= bram_bound;\n')
		# f.write('\n')
		# f.write('subject to latency_hiding_cst:\n')
		# f.write('	r_t2*c_t2*o_t2 >= 8*i_t2;\n')
		# f.write('subject to no_1_dim:\n')
		# f.write('	r_t1 >= r_t2;\n')
		# f.write('subject to no_2_dim:\n')
		# f.write('	c_t1 >= c_t2;\n')
		# f.write('subject to no_3_dim:\n')
		# f.write('	o_t1 >= o_t2;\n')
		# f.write('subject to no_4_dim:\n')
		# f.write('	min(i_t1,8) >= i_t2;\n')
		# f.write('subject to no_5_dim:\n')
		# f.write('	p14 <= max(min(i_t1,4),i_t2);\n')
		# f.write('subject to no_5_dim:\n')
		# f.write(' i_t2 <= 8;\n')
		# latency_main_items.append(f"{module}_latency")
	# f.write("\tlatency_main = max(")
	# is_first = True
	# for module in info["modules"]:
	# 	if "inter" in module or "intra" in module:
	# 		continue   
	# 	if module.find('drain') != -1:
	# 		array_name = module[:module.find("_drain_IO")]                
	# 		if out_drain_module[array_name]['merged'] == 1:
	# 			continue                      
	# 	if not is_first:
	# 		f.write(", ")
	# 	f.write(f"{module}_latency")
	# 	is_first = False
	# f.write(")\n\n")

	#f.write("\tprint(latency_prologue, latency_main, latency_epilogue)\n\n")

	# f.write("\tlatency = latency_prologue + latency_main + latency_epilogue\n\n")
	
	# f.write("\t# Meta information, used for conv fusion only\n")
	# f.write("\tlatency_meta = {\"latency_prologue\": {}, \"latency_main\": {}, \"latency_epilogue\": {}}\n")
	# # Prologue        
	# for item in latency_prologue_items:            
	# 	f.write(f"\tlatency_meta[\"latency_prologue\"][\"{item}\"] = {item}\n")
	# # Epilogue
	# for item in latency_epilogue_items:            
	# 	f.write(f"\tlatency_meta[\"latency_epilogue\"][\"{item}\"] = {item}\n")
	# # Main
	# for item in latency_main_items:            
	# 	f.write(f"\tlatency_meta[\"latency_main\"][\"{item}\"] = {item}\n")

	# f.write("\treturn latency, latency_meta\n")
	# f.write("\n")

def print_model_constraints(f, desp):
	# DSP constraints
	f.write('subject to DSP_cst:\n')
	f.write(f"\t0 <= {desp['compute']['PE']['num']} * ")
	f.write(f"{desp['compute']['PE']['unroll_factor']} * ")
	if desp["compute"]["PE"]["ele_type"] == "float":
			f.write(f"5 <= dsp_bound;\n")
	else:
			raise RuntimeError(f"Unsupported data type {desp['compute']['PE']['ele_type']} in resource estimation")        
	f.write("\n")

	# BRAM constraints
	f.write('subject to BRAM_cst:\n')
	f.write(f'\t0 <= \n')
	# Print function est_BRAM18K
	# Check if drain module can be merged.
	# Note: It should be supported in the codegen of AutoSA. However, currently, 
	# we move it here in the tuner.
	mem_meta_info = {}
	out_module = {}
	out_drain_module = {}
	for module in desp["memory"]:
		module_mem = desp["memory"][module]
		if module.endswith('_out'):
			item = {'buf_size': module_mem['buf_size'], 
				'num': module_mem['num']}
			if module.find('drain') != -1:
				item['merged'] = 0
				out_drain_module[module_mem['array']] = item
			else:                    
				if module_mem['array'] not in out_module:
					out_module[module_mem['array']] = [item]
				else:
					out_module[module_mem['array']].append(item)
	for array in out_drain_module:
		if array in out_module:
			for m in out_module[array]:                
				if m['buf_size'] == out_drain_module[array]['buf_size'] and \
					m['num'] == out_drain_module[array]['num']:
					out_drain_module[array]['merged'] = 1

	modules_dict = {}
	for module in desp["memory"]:
		module_mem = desp["memory"][module]
		if module.find('drain') != -1 and out_drain_module[module_mem['array']]['merged'] == 1:
			continue
		# ceil(ele_size*8*pack / 36) * ceil(ele_num/pack/512)
		ele_size = module_mem['ele_size']
		ele_num = module_mem['buf_size'] 
		if "data_pack_factor_inter" in module_mem:
			pack = module_mem["data_pack_factor_inter"]
		else:
			pack = 1
		modules_dict[module] = f'\tceil({ele_size}*8*{pack} / 36) * ceil({ele_num}/{pack}/512)'

	is_first = True
	for module in desp["memory"]:
		module_mem = desp["memory"][module]
		if module.find('drain') != -1 and out_drain_module[module_mem['array']]['merged'] == 1:
			continue
		module_unit_brams = modules_dict[module]
		if not is_first:
			f.write(" + \n")            
		f.write(module_unit_brams)
		if module_mem["double_buffer"]:
			f.write(f" * 2")
		else:
			f.write(f" * 1")
		f.write(f" * {module_mem['num']}")            
		is_first = False
	f.write("\n\t<= bram_bound;\n")
	f.write("\n")

	# Other constraints
	params_config = {"external": {}, "tunable": {}, "infer": {}}
	for param in desp["params"]:
		if param["tunable"]:
			params_config["tunable"][param["name"]] = param
		else:
			if "external" in param["tags"]:
				params_config["external"][param["name"]] = param
			elif "auto_infer" in param["tags"]:
				params_config["infer"][param["name"]] = param
	# Load parameters
	counter = 0
	for p in desp["params"]:
		if "bounds" in p and p['bounds'][0] != '1':
			counter += 1
			f.write(f"subject to const_{counter}:\n\t{p['name']} >= {p['bounds'][0]};\n")
			# f.write(f"\t\treturn False\n")
			# If the parameter is the first-level tiling factors, 
			# ignore the upper bounds.
			# if not p['name'].endswith('t1'):
			# 	counter += 1
			# 	f.write(f"subject to const_{counter}:\n\t{p['name']} <= {p['bounds'][1]};\n")
					# f.write(f"\t\treturn False\n")
			# if "tags" in p and "power_of_two" in p["tags"]:
			# 		f.write(f"\tif filter_non_power_of_two({p['name']}):\n")
			# 		f.write(f"\t\treturn False\n")
	# Latency hiding
	# if "PE" in desp["memory"]:
	# 		f.write(f"\tlatency_factors = 1\n")
	# 		for p, param in params_config["tunable"].items():
	# 				if param["attr"] == "latency_tiling_factor":
	# 						f.write(f"\tlatency_factors *= {param['name']}\n")
	# 				if param["attr"] == "SIMD_tiling_factor":
	# 						f.write(f"\tsimd_factor = {param['name']}\n")
	# 		data_type = desp["memory"]["PE"]["ele_type"]
	# 		if data_type == "float":
	# 				f.write(f"\tif latency_factors < 8 * simd_factor:\n")
	# 				f.write(f"\t\treturn False\n")
	# 		else:
	# 				raise RuntimeError(f"Unsupported data type in random sample generation: {data_type}")
	# # check if 2d SA has dim = 1
	# dims = desp['compute']['PE']['dims']
	# if len(dims) == 2:
	# 		f.write(f'\tif {dims[0]} <= 1:\n')
	# 		f.write(f'\t\treturn False\n')
	# 		f.write(f'\tif {dims[1]} <= 1:\n')
	# 		f.write(f'\t\treturn False\n')

def print_model(f, desp, problem_size, resource_limits, solver_vars, solver_consts, other_ports):
	print_model_params(f, desp, problem_size, resource_limits, solver_vars, solver_consts, other_ports)
	print_model_target(f, desp)
	print_model_constraints(f, desp)

def print_data(f, desp, problem_size, resource_limits, remaining_ports):
	for p in desp["params"]:
		if p["name"] in problem_size:
			f.write(f'param {p["name"]} := {problem_size[p["name"]]};\n')
		elif 't' not in p["name"] and p["name"] in remaining_ports:
			# max(min(i_t1,4),i_t2)
			# get the 4
			# bound = p["bounds"][1].split(',')
			# bound = bound[1].strip(')')
			f.write(f'param {p["name"]} := {remaining_ports[p["name"]]};\n')
	f.write(f'param bram_bound := {int(resource_limits["BRAM18K"])};\n')
	f.write(f'param dsp_bound := {int(resource_limits["DSP"])};\n')
def compute_ops(workload, problem_size):
	""" Compute the total amount of operations of the workload.
	"""        
	if "mm" in workload:
			return problem_size["i"] * problem_size["j"] * problem_size["k"] * 2
	elif "conv" in workload:
			return problem_size["i"] * problem_size["o"] * problem_size["r"] * problem_size["c"] * problem_size["p"] * problem_size["q"] * 2
	else:
			raise RuntimeError(f"Not supported workload: {self.workload['name']}")

# may need be fixed for conv workloads: TODO
def compute_bw(params, cycles, off_chip_trans, dw, fre):
	""" Compute the bandwidth requirement of the task.
	Note: Only works for 32-bit data
	"""
	latency = cycles
	bw = off_chip_trans * dw / (latency / (fre * 1e6)) / 1e9 # GB/s
	return bw

def compute_ctc(params, workload, problem_size, off_chip_trans, dw):
	""" Compute the compute-to-communication ratio of the task.
	"""
	ops = compute_ops(workload, problem_size)
	comm = off_chip_trans * dw
	ctc = ops / comm

	return ctc

def compute_dsp_eff(cycles, workload, problem_size, dsp):
	""" Compute the DSP efficiency of the current design.
	Note: Only works for FP32 on Xilinx FPGA
	"""
	return (compute_ops(workload, problem_size) / (dsp / 5 * 2)) / cycles

def copy_design(design, workload, permutation):
	os.system(f'cp {designs_lib_dir}/{workload}_{permutation}/{design} {designs_dir}')

def list_split(ori_list, split_num):
	chunk_size = int(np.ceil(float(len(ori_list)) / split_num))
	chunks = [ori_list[i: i + min(chunk_size, len(ori_list) - i)] for i in range(0, len(ori_list), chunk_size)]
	return chunks

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

def get_SA_sizes(sa_info, solution, workload):
	array_part = sa_info['array_part']
	latency_hiding = sa_info['latency_hiding']
	simd = sa_info['simd']
	# print(f'array_part: {array_part}')
	# print(f'latency_hiding: {latency_hiding}')
	# print(f'simd: {simd}')
	arch_sol = solution['arch_sol']
	space_time_mapping = sa_info['idx']
	array_part_sol = [arch_sol[ap] for ap in array_part]
	latency_hiding_sol = [arch_sol[lat] for lat in latency_hiding]
	simd_sol = [arch_sol[sim] for sim in simd]

	for idx in range(len(latency_hiding_sol)):
		ap = int(array_part_sol[idx])
		lh = int(latency_hiding_sol[idx])
		if ap // lh == 1:
			simd_sol.insert(0, 1)
	if workload == 'conv':
		simd_sol.insert(0, 3)
		simd_sol.insert(0, 3)
	sa_sizes = '"{kernel[]->space_time[' + space_time_mapping + '];kernel[]->array_part' + str(array_part_sol) + ';kernel[]->latency' + str(latency_hiding_sol) + ';kernel[]->simd' + str(simd_sol) + '}"'
	return sa_sizes

def print_solution(idx, design, solution, sa_info, objective, workload, elapsed_time, all_designs, valid_designs, csv_path):
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
	array_part_mapping = eval(open(f'{prj_path}/data/autosa_mappings/{workload}_array_part.csv').readlines()[int(sa_info['idx'])])
	latency_hiding_mapping = eval(open(f'{prj_path}/data/autosa_mappings/{workload}_latency_hiding.csv').readlines()[int(sa_info['idx'])])
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
	params = solution['arch_sol']
	# sort params by key
	params = dict(sorted(params.items()))
	csv_file = open(csv_path, 'a')
	print(f'{design.split(".")[0]}_{idx},', end='', file=csv_file)
	# print(f'{elapsed_time:.1f},', end='', file=csv_file)
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
	print(f'{elapsed_time:.1f},', end='', file=csv_file)
	print(f'{all_designs:_.0f},', end='', file=csv_file)
	print(f'{valid_designs:_.0f},', end='', file=csv_file)
	print(f'{(all_designs/elapsed_time):_.0f},', end='', file=csv_file)
	print(f'{(valid_designs/elapsed_time):_.0f},', end='', file=csv_file)
	print(f'{sa_sizes},', end='', file=csv_file)
	print(f'"{params}"', end='', file=csv_file)
	print(file=csv_file)
	csv_file.close()
	return

def print_latencies(idx, design, solution, sa_info, objective, workload, elapsed_time, csv_path):
	file_path = 'tmp/designs/register/' + design.strip('.json')
	file_path = file_path.replace('/', '.')
	model = importlib.import_module(file_path)
	compute_arch_cst = model.compute_arch_cst
	cycles = solution['cycles']
	cycles_details = solution['cycles_details']
	A_IO_L2_in_single_latency = cycles_details['latency_prologue']['A_IO_L2_in_single_latency']
	A_IO_L3_in_single_latency = cycles_details['latency_prologue']['A_IO_L3_in_single_latency']
	B_IO_L2_in_single_latency = cycles_details['latency_prologue']['B_IO_L2_in_single_latency']
	B_IO_L3_in_single_latency = cycles_details['latency_prologue']['B_IO_L3_in_single_latency']
	A_IO_L2_in_latency = cycles_details['latency_main']['A_IO_L2_in_latency']
	A_IO_L3_in_latency = cycles_details['latency_main']['A_IO_L3_in_latency']
	B_IO_L2_in_latency = cycles_details['latency_main']['B_IO_L2_in_latency']
	B_IO_L3_in_latency = cycles_details['latency_main']['B_IO_L3_in_latency']
	C_drain_IO_L1_out_latency = cycles_details['latency_main']['C_drain_IO_L1_out_latency']
	C_drain_IO_L2_out_latency = cycles_details['latency_main']['C_drain_IO_L2_out_latency']
	C_drain_IO_L3_out_latency = cycles_details['latency_main']['C_drain_IO_L3_out_latency']
	PE_latency = cycles_details['latency_main']['PE_latency']
	C_drain_IO_L1_out_single_latency = cycles_details['latency_epilogue']['C_drain_IO_L1_out_single_latency']
	C_drain_IO_L2_out_single_latency = cycles_details['latency_epilogue']['C_drain_IO_L2_out_single_latency']
	C_drain_IO_L3_out_single_latency = cycles_details['latency_epilogue']['C_drain_IO_L3_out_single_latency']
	csv_file = open(csv_path, 'a')
	print(f'{cycles:.0f},', end='', file=csv_file)
	print(f'{A_IO_L2_in_single_latency:.0f},', end='', file=csv_file)
	print(f'{A_IO_L3_in_single_latency:.0f},', end='', file=csv_file)
	print(f'{B_IO_L2_in_single_latency:.0f},', end='', file=csv_file)
	print(f'{B_IO_L3_in_single_latency:.0f},', end='', file=csv_file)
	print(f'{A_IO_L2_in_latency:.0f},', end='', file=csv_file)
	print(f'{A_IO_L3_in_latency:.0f},', end='', file=csv_file)
	print(f'{B_IO_L2_in_latency:.0f},', end='', file=csv_file)
	print(f'{B_IO_L3_in_latency:.0f},', end='', file=csv_file)
	print(f'{C_drain_IO_L1_out_latency:.0f},', end='', file=csv_file)
	print(f'{C_drain_IO_L2_out_latency:.0f},', end='', file=csv_file)
	print(f'{C_drain_IO_L3_out_latency:.0f},', end='', file=csv_file)
	print(f'{PE_latency:.0f},', end='', file=csv_file)
	print(f'{C_drain_IO_L1_out_single_latency:.0f},', end='', file=csv_file)
	print(f'{C_drain_IO_L2_out_single_latency:.0f},', end='', file=csv_file)
	print(f'{C_drain_IO_L3_out_single_latency:.0f}', end='', file=csv_file)
	print(file=csv_file)
	csv_file.close()
	return

# def print_result(idx, design, solution, sa_info, objective, workload, elapsed_time, csv_path):
# 	file_path = 'tmp/designs/register/' + design.strip('.json')
# 	file_path = file_path.replace('/', '.')
# 	model = importlib.import_module(file_path)
# 	compute_arch_cst = model.compute_arch_cst

# 	original_workload_size = {}
# 	padded_workload_size = {}
# 	padding_dims = sa_info['padding_dims']
# 	# get elements from dictionary solution['arch_sol'] whose key ends with t1
# 	# and store them in t1_dims
# 	for dim in solution['arch_sol'].keys():
# 		if len(dim) == 1:
# 			original_workload_size[dim] = solution['arch_sol'][dim]
# 	t1_dims = {k:v for k, v in solution['arch_sol'].items() if k.endswith('t1')}
# 	for dim in solution['arch_sol'].keys():
# 		if dim in padding_dims:
# 			# get key and value from t1_dims if dim is in key
# 			t1_dim = [v for k, v in t1_dims.items() if dim in k][0]
# 			padded_workload_size[dim] = ceil(solution['arch_sol'][dim]/t1_dim)*t1_dim
# 	# for key in original_workload_size.keys():
# 	# 	if key not in padded_workload_size.keys():
# 	# 		padded_workload_size[key] = original_workload_size[key]
# 	# sort padded_workload_size by key
# 	padded_workload_size = dict(sorted(padded_workload_size.items()))
# 	# sort original_workload_size by key
# 	original_workload_size = dict(sorted(original_workload_size.items()))
# 	fre = solution['fre']
# 	throughput = solution['throughput']
# 	cycles = solution['cycles']
# 	latency = solution['latency']
# 	dsp_eff = solution['dsp_eff']
# 	off_chip_bytes = solution['off_chip_bytes']
# 	bandwidth = solution['bandwidth']
# 	CTC = solution['CTC']
# 	DSPs = solution['DSPs']
# 	BRAMs = solution['BRAMs']
# 	arch = compute_arch_cst(solution['arch_sol'])
# 	array_part_mapping = eval(open(f'{prj_path}/tests/{workload}_array_part.csv').readlines()[int(sa_info['idx'])])
# 	latency_hiding_mapping = eval(open(f'{prj_path}/tests/{workload}_latency_hiding.csv').readlines()[int(sa_info['idx'])])
# 	if len(arch['dims']) == 1:
# 		if array_part_mapping[0] not in latency_hiding_mapping:
# 			SA_Dims = '"' + str((int(arch['dims'][0])*int(arch['SIMD']), 1)) + '"'
# 			PEs = int(arch['dims'][0])*int(arch['SIMD'])
# 		else:
# 			SA_Dims = '"' + str((int(arch['dims'][0]), int(arch['SIMD']))) + '"'
# 			PEs = prod(arch['dims'])
# 	elif len(arch['dims']) == 2:
# 		if array_part_mapping[1] not in latency_hiding_mapping:
# 			SA_Dims = '"' + str((int(arch['dims'][0]), int(arch['dims'][1])*int(arch['SIMD']), 1)) + '"'
# 			PEs = int(arch['dims'][0])*int(arch['dims'][1])*int(arch['SIMD'])
# 		else:
# 			SA_Dims = '"' + str((int(arch['dims'][0]), int(arch['dims'][1]), int(arch['SIMD']))) + '"'
# 			PEs = prod(arch['dims'])

# 	sa_sizes = get_SA_sizes(sa_info, solution, workload)
# 	csv_file = open(csv_path, 'a')
# 	print(f'{design.split(".")[0]}_{idx},', end='', file=csv_file)
# 	print(f'{elapsed_time:.1f},', end='', file=csv_file)
# 	print(f'{objective},', end='', file=csv_file)
# 	print(f'"{original_workload_size}",', end='', file=csv_file)
# 	print(f'"{padded_workload_size}",', end='', file=csv_file)
# 	print(f'{fre:.0f},', end='', file=csv_file)
# 	print(f'{throughput:.2f},', end='', file=csv_file)
# 	print(f'{cycles:.0f},', end='', file=csv_file)
# 	print(f'{latency:.5f},', end='', file=csv_file)
# 	print(f'{dsp_eff:.2f}%,', end='', file=csv_file)
# 	print(f'{off_chip_bytes:.0f},', end='', file=csv_file)
# 	print(f'{bandwidth:.2f},', end='', file=csv_file)
# 	print(f'{CTC:.2f},', end='', file=csv_file)
# 	print(f'{DSPs:.0f},', end='', file=csv_file)
# 	print(f'{BRAMs:.0f},', end='', file=csv_file)
# 	print(f'{PEs:.0f},', end='', file=csv_file)
# 	print(f'{SA_Dims},', end='', file=csv_file)
# 	print(f'{sa_sizes}', end='', file=csv_file)
# 	print(file=csv_file)
# 	csv_file.close()
# 	return

