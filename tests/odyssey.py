import os
import sys
import json
import re
from math import ceil
from math import prod
import importlib
import time


prj_path = os.environ["PRJ_PATH"]
designs_lib_dir = prj_path + f'/data/designs_lib'
designs_dir = prj_path + '/tests/tmp/designs'
output_dir = prj_path + '/tests/tmp/outputs'

def copy_design(design, workload):
	os.system(f'cp {designs_lib_dir}/{workload}/{design} {designs_dir}')

def run_odyssey(design, objective, workload):
	os.system(f'rm -rf {designs_dir}/*')
	# print(f'{designs_lib_dir}/{workload}/{design}')
	copy_design(design, workload)
	os.system(prj_path + f'/tests/odyssey.sh {workload} {objective} {designs_dir}')
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



# for design in designs:
# 	copy_design(design, workload)
# 	sa_info = get_SA_info(design)
# 	print(sa_info)
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
objectives = ['latency', 'off_chip_comm']
# create csv file for results
results_file = prj_path + f'/tests/results/{workload}.csv'
csv_file = open(results_file, 'w')
print('design_idx,objective,original workload,padded workload,fre,throughput (GFLOP/s),cycles,latency(ms),DSP eff,off-chip bytes,bandwidth (GB/s),CTC,DSPs,BRAMs,PEs,SA_dims,sa_sizes', file=csv_file)
csv_file.close()
id = 0 
outfile = open(f'{prj_path}/tests/results/{workload}_{problem_dims_str}_odyssey.csv', 'w')
# print('design_idx, cycles, search time', file=outfile)
total_time_start = time.time()
for idx in range(len(designs)):
	for objective in objectives:
		for trial in range(1):
			id += 1
			time_start = time.time()
			run_odyssey(designs[idx], objective, workload)
			solution = get_solution()
			time_end = time.time()
			elapsed_time = time_end - time_start
			# print(f'{idx}, {solution["cycles"]:.0f}, {elapsed_time:.1f}', file=outfile)
			sa_info = get_SA_info(designs[idx])
			print_solution(id, designs[idx], solution, sa_info, objective, workload, csv_file)
total_time_end = time.time()
# print(f'Elapsed time: {total_time_end - total_time_start:.2f} seconds', file=outfile)