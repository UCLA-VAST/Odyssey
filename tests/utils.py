import os
import json
import importlib
import re
from math import ceil
from math import prod
import numpy as np

prj_path = os.environ["PRJ_PATH"]
designs_lib_dir = prj_path + f'/data/designs_lib'
designs_dir = prj_path + '/tests/tmp/designs'
output_dir = prj_path + '/tests/tmp/outputs'

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

def copy_design(design, workload):
	os.system(f'cp {designs_lib_dir}/{workload}/{design} {designs_dir}')

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

def print_solution(idx, design, solution, sa_info, objective, workload, elapsed_time, csv_path):
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
	csv_file = open(csv_path, 'a')
	print(f'{design.split(".")[0]}_{idx},', end='', file=csv_file)
	print(f'{elapsed_time:.1f},', end='', file=csv_file)
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

