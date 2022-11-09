import os
import sys
import json
import re
from math import ceil
from math import prod
import importlib
import time
from utils import *

def run_odyssey(design, objective, workload):
	os.system(f'rm -rf {designs_dir}/*')
	# print(f'{designs_lib_dir}/{workload}/{design}')
	copy_design(design, workload)
	os.system(prj_path + f'/new_tests/odyssey.sh {workload} {objective} {designs_dir}')
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

workload = sys.argv[1]
problem_size = eval(sys.argv[2])
problem_dims = [problem_size[key] for key in problem_size.keys()]
# convert [1, 2, 3] to 1_2_3
problem_dims_str = '_'.join([str(dim) for dim in problem_dims])
# quick hack to set the problem size: TODO: fix this
with open(f'{prj_path}/data/workload/{workload}.json', 'r') as f:
	workload_info = json.load(f)
workload_info['workloads'][0]['params'] = problem_size
with open(f'{prj_path}/data/workload/{workload}.json', 'w') as f:
	json.dump(workload_info, f, indent=1)

designs = os.listdir(f'{designs_lib_dir}/{workload}')
designs.sort()
objectives = ['latency']
# create csv file for results
results_file = prj_path + f'/new_tests/results/{workload}_{problem_dims_str}_odyssey.csv'
csv_file = open(results_file, 'w')
print('design_idx,search time (s),objective,original workload,padded workload,fre,throughput (GFLOP/s),cycles,latency(ms),DSP eff,off-chip bytes,bandwidth (GB/s),CTC,DSPs,BRAMs,PEs,SA_dims,sa_sizes', file=csv_file)
csv_file.close()
id = 0 
total_time_start = time.time()
for idx in range(3,4):
	for objective in objectives:
		for trial in range(1):
			id += 1
			time_start = time.time()
			run_odyssey(designs[idx], objective, workload)
			solution = get_solution()
			time_end = time.time()
			elapsed_time = time_end - time_start
			sa_info = get_SA_info(designs[idx])
			print_solution(id, designs[idx], solution, sa_info, objective, workload, elapsed_time, results_file)
total_time_end = time.time()
# print(f'Elapsed time: {total_time_end - total_time_start:.2f} seconds', file=outfile)