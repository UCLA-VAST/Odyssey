import os
import sys
import json
import re
from math import ceil
from math import prod
import importlib
import time
from utils import *
import argparse

def run_odyssey(design, permutation, objective, workload, time_out, alpha):
	os.system(f'rm -rf {designs_dir}/*')
	# print(f'{designs_lib_dir}/{workload}/{design}')
	os.makedirs(f'tmp/designs/register', exist_ok=True)
	copy_design(design, workload, permutation)
	os.system(prj_path + f'/tests/src/odyssey.sh {workload} {objective} {designs_dir} {time_out} {alpha}')
	return

def get_solution():
	solution = {}
	outputs = os.listdir(output_dir)
	# read results
	search_result = json.load(open(f'{output_dir}/{outputs[0]}/history_0.json'))
	solution['arch_sol'] = search_result["arch sol"]
	solution['DSPs'] = search_result["cst"]["DSP"]
	solution['BRAMs'] = search_result["cst"]["BRAM18K"]
	solution['cycles'] = search_result["cycles"]
	solution['dsp_eff'] = search_result["dsp_eff"]*100
	solution['fre'] = search_result["fre"]
	solution['latency'] = search_result['latency']
	solution['throughput'] = search_result['throughput (GOP/s)']
	solution['off_chip_bytes'] = search_result['off-chip communication (Bytes)']
	solution['bandwidth'] = search_result['bw']
	solution['CTC'] = search_result['CTC(FLOP/byte)']
	return solution

if __name__ == '__main__':
	# parse arguments
	parser = argparse.ArgumentParser()
	# workload or w
	parser.add_argument('-w', '--workload', type=str, default='mm', help='workload')
	# problem size or p
	parser.add_argument('-p', '--problem_size', type=str, default="{'i': 64, 'j' : 64, 'k' : 64}", help='problem size')
	# objective or obj
	parser.add_argument('-obj', '--objective', type=str, default='all', help='choose objective from: [latency, off_chip, latency_off_chip, all]')
	# design or d
	parser.add_argument('-d', '--design', type=str, default='all', help='design')
	# alpha
	parser.add_argument('-a', '--alpha', type=float, default=0.5, help='weight of latency')
	# time out
	parser.add_argument('-to', '--time_out', type=int, default=60, help='time out')
	# trials
	parser.add_argument('-tr', '--trials', type=int, default=1, help='trials')

	# workload
	workload = parser.parse_args().workload

	# problem size
	problem_size = eval(parser.parse_args().problem_size)
	problem_dims = [problem_size[key] for key in problem_size.keys()]
	problem_dims_str = '_'.join([str(dim) for dim in problem_dims])

	# quick hack to set the problem size: TODO: fix this
	with open(f'{prj_path}/data/workload/{workload}.json', 'r') as f:
		workload_info = json.load(f)
	workload_info['workloads'][0]['params'] = problem_size
	with open(f'{prj_path}/data/workload/{workload}.json', 'w') as f:
		json.dump(workload_info, f, indent=1)

	# objective
	objective = parser.parse_args().objective
	if objective == 'all':
		objectives = ['latency', 'off_chip', 'latency_off_chip']
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

	# alpha
	alpha = parser.parse_args().alpha

	# time out
	time_out = parser.parse_args().time_out

	# trials
	trials = parser.parse_args().trials

	results_dir = prj_path + f'/results/{workload}/{problem_dims_str}/design_{permutation}_{dataflow}/{objective}/odyssey'
	if not os.path.exists(results_dir):
		os.makedirs(results_dir + '/results')
		os.makedirs(results_dir + '/logs')
	logs_dir = results_dir + '/logs/'
	results_dir = results_dir + '/results/'
	# create csv file for results
	file_name = f'alpha_{alpha}'
	results_file = results_dir + f'{file_name}.csv'
	log_file = logs_dir + f'{file_name}.json'
	csv_file = open(results_file, 'w')
	print('design_idx,objective,original workload,padded workload,fre,throughput (GFLOP/s),cycles,latency(ms),DSP eff,off-chip bytes,bandwidth (GB/s),CTC,DSPs,BRAMs,PEs,SA_dims,search_time,all_designs,valid_designs,adps,vdps,sa_sizes,params', file=csv_file)
	csv_file.close()
	id = 0

	for idx in design_iter:
		for objective in objectives:
			for trial in range(trials):
				id += 1
				time_start = time.time()
				run_odyssey(designs[idx], permutation, objective, workload, time_out, alpha)
				solution = get_solution()
				time_end = time.time()
				elapsed_time = time_end - time_start
				sa_info = get_SA_info(designs[idx])
				print_solution(id, designs[idx], solution, sa_info, objective, workload, elapsed_time, 1, 1, results_file)
	
	import shutil
	new_file_name = f'{workload}_odyssey_{problem_dims_str}_design_{permutation}_{dataflow}_{objective}_alpha_{alpha}'
	results_dir = prj_path + f'/results/all/'
	# copy results_file and log_file to new_file_name
	shutil.copy(results_file, results_dir + f'{new_file_name}.csv')