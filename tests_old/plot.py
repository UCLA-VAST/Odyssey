from matplotlib import pyplot as plt
import numpy as np
import pandas as pd
import os
import sys
import argparse
import json



# search_methods = ['divisors', 'odyssey', 'non_divisors', 'exhaustive']
def plot(workload, problem_dims_str, alpha, objective, search_methods):
	prj_path = os.environ["PRJ_PATH"]
	results_path = f'{prj_path}/results/{workload}/{problem_dims_str}/design_all_all/{objective}/'
	output_file =f'plots/{workload}_{problem_dims_str}'
	csv_out_file = output_file + '.csv'
	image_file = output_file + '.png'

	cycles_dict = {}
	throughput_dict = {}
	# get problem_size result directory
	for search_method in search_methods:
		cycles_dict[search_method] = 0
		throughput_dict[search_method] = 0
		# regex first file ending with .csv
		if os.path.exists(f'{results_path}{search_method}/results/'):
			csv_file = [f for f in os.listdir(f'{results_path}{search_method}/results/') if f.endswith('.csv')][0]
			csv_path = f'{results_path}{search_method}/results/{csv_file}'
			if os.path.exists(csv_path):
				df = pd.read_csv(csv_path)
				# sort df by 'cycles'
				df = df.sort_values(by=['cycles'])
				# print cycles of top 1 design
				if len(df) > 0:
					print(f'{search_method}: {df.iloc[0]["cycles"]}')
					cycles_dict[search_method] = df.iloc[0]["cycles"]
					throughput_dict[search_method] = df.iloc[0]["throughput (GFLOP/s)"]

	with open(csv_out_file, 'w') as f:
		print('cycles_reduction_over_divisor,throughput_speedup_over_divisor', file = f)
		# cycles_reduction_over_divisor = cycles_dict['exhaustive'] / cycles_dict['divisors']
		# cycles_reduction_over_non_divisor = cycles_dict['exhaustive'] / cycles_dict['non_divisors']
		# throughput_speedup_over_divisor = throughput_dict['exhaustive'] / throughput_dict['divisors']
		# throughput_speedup_over_non_divisor = throughput_dict['exhaustive'] / throughput_dict['non_divisors']
		# print(f'{cycles_reduction_over_divisor:.2f},{throughput_speedup_over_divisor:.2f}', file = f)
	
	# plot cycles_dict in different colors
	# plt.bar(cycles_dict.keys(), cycles_dict.values(), color=['blue', 'red'])
	# # show speedup of non-divisor over divisor
	# plt.text(1, cycles_dict['non_divisors'], f'{(1-cycles_reduction_over_divisor)*100:.2f}% less cycles', ha='center', va='bottom')
	# plt.xlabel('Search Method')
	# plt.ylabel('Cycles')
	# plt.title(f'{workload} {problem_dims_str} {alpha} {objective}')
	# plt.savefig(f'cycles_{image_file}')
	# # clear plot
	# plt.clf()
	# plt.bar(throughput_dict.keys(), throughput_dict.values(), color=['blue', 'red'])
	# # show speedup of non-divisor over divisor
	# plt.text(1, throughput_dict['non_divisors'], f'{(throughput_speedup_over_divisor):.2f}x', ha='center', va='bottom')
	# plt.xlabel('Search Method')
	# plt.ylabel('throughput (GFLOP/s)')
	# plt.title(f'{workload} {problem_dims_str} {alpha} {objective}')
	# plt.savefig(f'throughput_{image_file}')
	# # clear plot
	# plt.clf()
	return cycles_dict, throughput_dict
	# # get csv files
	# csv_files = {}
	# workload_dir = results_dir + f'/{workload}/{problem_dims_str}'
	# folders = os.listdir(workload_dir)
	# folders.sort()
	# total_time = 0
	# for folder in folders:
	# 	csv_files[folder] = {}
	# 	for search_method in search_methods:
	# 		# if workload_dir + f'/{folder}/{objective}/{search_method}/results' exists
	# 		if os.path.exists(workload_dir + f'/{folder}/{objective}/{search_method}/results'):
	# 			file_name = os.listdir(workload_dir + f'/{folder}/{objective}/{search_method}/results')[0]

	# 			file_path = workload_dir + f'/{folder}/{objective}/{search_method}/results/{file_name}'
	# 			csv_files[folder][search_method] = pd.read_csv(file_path)
	# 		# if search_method != 'odyssey':
	# 		# 	log_name = os.listdir(workload_dir + f'/{folder}/{objective}/{search_method}/logs')[0]
	# 		# 	log_path =  workload_dir + f'/{folder}/{objective}/{search_method}/logs/{log_name}'
	# 		# 	with open(log_path, 'r') as f:
	# 		# 		data = json.load(f)
	# 		# 		print(data['all_designs'])
	# 		# 		total_time += float(data['total_time'])
	# # print(f'total time: {total_time}')
	# indices = []
	# colors = []
	# data = []
	# cntr = 0
	# for folder in folders:
	# 	for search_method in search_methods:
	# 		if len(csv_files[folder][search_method]) < 1:
	# 			continue
	# 		if len(csv_files[folder][search_method]) > 1:
	# 			print(folder, search_method, float(csv_files[folder][search_method]['throughput (GFLOP/s)'][0]))
	# 			cntr += 1
	# 			indices.append(cntr)
	# 			# add different color based on the search method
	# 			if search_method == 'divisors':
	# 				colors.append('red')
	# 			elif search_method == 'odyssey':
	# 				colors.append('blue')
	# 			elif search_method == 'non_divisors':
	# 				colors.append('green')
	# 			elif search_method == 'exhaustive':
	# 				colors.append('black')
	# 			data.append(float(csv_files[folder][search_method]['throughput (GFLOP/s)'][0]))
	# 		else:
	# 			print(folder, search_method, float(csv_files[folder][search_method]['throughput (GFLOP/s)']))
	# 			cntr += 1
	# 			indices.append(cntr)
	# 			# add different color based on the search method
	# 			if search_method == 'divisors':
	# 				colors.append('red')
	# 			elif search_method == 'odyssey':
	# 				colors.append('blue')
	# 			elif search_method == 'non_divisors':
	# 				colors.append('green')
	# 			elif search_method == 'exhaustive':
	# 				colors.append('black')
	# 			data.append(float(csv_files[folder][search_method]['throughput (GFLOP/s)']))
			

	# 	cntr += 1
	# 	indices.append(cntr)
	# 	colors.append('white')
	# 	data.append(0)
	# # plot
	# plt.figure(figsize=(10, 5))
	# plt.bar(indices, data, color=colors)
	# # plt.xticks(indices, folders, rotation=90)
	# plt.xlabel('Designs')
	# plt.ylabel('Throughput (GFLOP/s)')
	# # legend red = divisors, blue = odyssey, green = non_divisors, black = exhaustive
	# plt.legend(handles=[plt.Rectangle((0,0),1,1, color=c, ec="k") for c in ['red', 'blue', 'green', 'black']], labels=['divisors', 'genetic', 'non_divisors', 'exhaustive'])
	
	# plt.title(f'{workload} {problem_dims_str} {objective} {alpha}')
	# plt.savefig(f'./plots/{workload}_{problem_dims_str}_{objective}_{alpha}.png')

# if __name__ == '__main__':
# 	# parse arguments
# 	parser = argparse.ArgumentParser()
# 	# workload or w
# 	parser.add_argument('-w', '--workload', type=str, default='mm', help='workload')
# 	# problem size or p
# 	parser.add_argument('-p', '--problem_size', type=str, default="{'i': 64, 'j' : 64, 'k' : 64}", help='problem size')
# 	# objective or obj
# 	parser.add_argument('-obj', '--objective', type=str, default='all', help='choose objective from: [latency, off_chip, latency_off_chip, all]')
# 	# design or d
# 	# parser.add_argument('-d', '--design', type=str, default='all', help='design')
# 	# alpha
# 	parser.add_argument('-a', '--alpha', type=float, default=0.5, help='weight of latency')

# 	# workload
# 	workload = parser.parse_args().workload

# 	# problem size
# 	problem_size = eval(parser.parse_args().problem_size)
# 	problem_dims = [problem_size[key] for key in problem_size.keys()]
# 	problem_dims_str = '_'.join([str(dim) for dim in problem_dims])

# 	# objective
# 	objective = parser.parse_args().objective
		
# 	# alpha 
# 	alpha = parser.parse_args().alpha

# 	plot(workload, problem_dims_str, objective, alpha)
# 	exit()
# 	# # design
# 	# design = parser.parse_args().design
# 	# if design=='all':
# 	# 	designs = []
# 	# 	for permutation in range(3):
# 	# 		designs.append(os.listdir(f'{designs_lib_dir}/{workload}_{permutation}'))
# 	# 	permutation = 'all'
# 	# 	dataflow = 'all'
# 	# 	designs.sort()
# 	# 	design_iter = range(len(designs))
# 	# else:
# 	# 	design = eval(parser.parse_args().design)
# 	# 	permutation = design[0]
# 	# 	dataflow = design[1]
# 	# 	designs = os.listdir(f'{designs_lib_dir}/{workload}_{permutation}')
# 	# 	designs.sort()
# 	# 	design_iter = [int(dataflow)]


# n = 10
# my_logs_path = 'logs'
# ex_logs_path = 'exhaustive/logs'
# my_results_path = 'results'
# ex_results_path = 'exhaustive/results'
# od_results_path = 'results'
# workload = sys.argv[1]
# problem_size = int(sys.argv[2])
# threshold = int(sys.argv[3])
# my_results_dir = os.listdir(f'{my_results_path}/{workload}')
# my_results_dir.sort()
# ex_results_dir = os.listdir(f'{ex_results_path}/{workload}')
# ex_results_dir.sort()
# od_results_dir = os.listdir(f'{od_results_path}')
# od_results_dir.sort()

# my_logs_dir = os.listdir(f'{my_logs_path}/{workload}')
# my_logs_dir.sort()
# ex_logs_dir = os.listdir(f'{ex_logs_path}/{workload}')
# ex_logs_dir.sort()


# def get_my_designs(results_dir, size, threshold):
# 	designs = []
# 	for result in results_dir:
# 		if f'{size}_{size}_{size}' in result and f'thr{threshold}' in result:
# 			designs.append(result)
# 	return designs

# def get_exhaustive_designs(results_dir, size):
# 	designs = []
# 	for result in results_dir:
# 		if f'{size}_{size}_{size}' in result:
# 			designs.append(result)
# 	return designs

# def get_od_designs(results_dir, workload, size):
# 	designs = []
# 	for result in results_dir:
# 		if f'{workload}_{size}_{size}_{size}' in result:
# 			designs.append(result)
# 	return designs

# # my_logs = get_my_designs(my_logs_dir, problem_size, threshold)
# # ex_logs = get_exhaustive_designs(ex_logs_dir, problem_size)
# # out_log_file = f'plots/cycles_{workload}_{problem_size}_{threshold}.csv'
# # time_list = []
# # indices_list = []
# # colors_list = []
# # counter = 0
# # with open(out_log_file, 'w') as f:
# #   print('design,my_time,ex_time,speedup', file=f)
# #   for idx in range(len(my_logs)):
# #     my_log = open(f'{my_logs_path}/{workload}/{my_logs[idx]}', 'r')
# #     ex_log = open(f'{ex_logs_path}/{workload}/{ex_logs[idx]}', 'r')
# #     for line in my_log:
# #       split_line = line.split()
# #       my_num_designs = split_line[1].replace(',', '')
# #       my_num_designs = int(my_num_designs)
# #       my_time = float(split_line[5])
# #       time_list.append(my_time)
# #       colors_list.append('red')
# #       counter += 1
# #       indices_list.append(counter)
# #     for line in ex_log:
# #       split_line = line.split()
# #       ex_num_designs = split_line[1].replace(',', '')
# #       ex_num_designs = int(ex_num_designs)
# #       ex_time = float(split_line[5])
# #       time_list.append(ex_time)
# #       colors_list.append('blue')
# #       counter += 1
# #       indices_list.append(counter)
# #     time_list.append(0)
# #     colors_list.append('white')
# #     counter += 1
# #     indices_list.append(counter)
# #     speedup = ex_time / my_time
# #     print(f'{idx},{my_time:.0f},{ex_time:.0f},{speedup:.0f}', file=f)

# # # plot the time_list vs indices_list
# # plt.figure(figsize=(10, 5))
# # plt.bar(indices_list, time_list, color=colors_list)
# # plt.xlabel('Designs')
# # plt.ylabel('Time (s)')
# # plt.title(f'{workload} {problem_size}x{problem_size}x{problem_size} {threshold}')
# # show legend based on color
# # blue is exhaustive
# # red is our method
# # white is the gap between designs
# # plt.legend(['Exhaustive', 'Our Method'])
# # plt.savefig(f'plots/time_{workload}_{problem_size}_{threshold}.png')
# mysearch_designs = get_my_designs(my_results_dir, problem_size, threshold)
# # exhaustive_designs = get_exhaustive_designs(ex_results_dir, problem_size)
# # for design in mysearch_designs:
# #   print(design)
# # for design in exhaustive_designs:
# #   print(design)
# # exit()
# od_designs = get_od_designs(od_results_dir, workload, problem_size)

# cycles_list = []
# indices_list = []
# colors_list = []
# labels_list = []
# cntr = 0
# od_design = od_designs[0]
# od_df = pd.read_csv(f'{od_results_path}/{od_design}')
# od_cycles = od_df['cycles'].values
# for idx in range(len(mysearch_designs)):
# 	my_design = mysearch_designs[idx]
# 	# ex_design = exhaustive_designs[idx]
# 	my_df = pd.read_csv(f'{my_results_path}/{workload}/{my_design}')
# 	# ex_df = pd.read_csv(f'{ex_results_path}/{workload}/{ex_design}')
# 	my_cycles = my_df['cycles'].values
# 	# ex_cycles = ex_df['cycles'].values
# 	for i in range(3):
# 		cycles_list.append(od_cycles[idx*3 + i])
# 		labels_list.append(f'kernel_{idx}')
# 		indices_list.append(cntr)
# 		cntr += 1
# 		colors_list.append('green')
# 	for i in range(n):
# 		cycles_list.append(my_cycles[i])
# 		# cycles_list.append(ex_cycles[i])
# 		labels_list.append(f'kernel_{idx}')
# 		# labels_list.append(f'kernel_{idx}')
# 		# indices_list.append(cntr)
# 		# cntr += 1
# 		indices_list.append(cntr)
# 		cntr += 1
# 		colors_list.append('red')
# 		# colors_list.append('blue')

# 	cntr += 1
# 	cycles_list.append(np.nan)
# 	labels_list.append(f'')
# 	indices_list.append(cntr)
# 	colors_list.append('black')
		
# print(len(cycles_list), len(indices_list), len(colors_list))

# fig, ax = plt.subplots()
# # make bar/column chart
# ax.bar(indices_list, cycles_list, color=colors_list)
# # y-axis cycles
# ax.set_ylabel('Cycles')
# # x-axis kernels
# ax.set_xlabel('Kernels')
# # show legend based on color
# # red is my cycles
# # blue is exhaustive cycles
# # green is od cycles
# # black is nan
# ax.legend(handles=[plt.Rectangle((0,0),1,1, color=c, ec="k") for c in ['red', 'blue', 'green', 'black']], labels=['My Search', 'Exhaustive Search', 'Odyssey'])

# # make figure wide
# fig.set_figwidth(15)

# # # save the plot
# fig.savefig(f'plots/cycles_{workload}_{problem_size}_{threshold}.png')