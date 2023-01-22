import sys
sys.path.append('./src')
from utils import *
import argparse

def get_num_designs(num):
	# if number in billions
	if num >= 1e9:
		return f'{num/1e9:.2f}B'
	# if number in millions
	elif num >= 1e6:
		return f'{num/1e6:.2f}M'
	# if number in thousands
	elif num >= 1e3:
		return f'{num/1e3:.2f}K'

if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	# workload
	parser.add_argument('-w', '--workload', type=str, default='conv', help='workload name')
	# alpha
	parser.add_argument('-a', '--alpha', type=float, default=1.0, help='alpha')
	# threshold
	parser.add_argument('-thr', '--threshold', type=float, default=0.5, help='threshold')
	# objective
	parser.add_argument('-obj','--objective', type=str, default='latency_off_chip', help='objective')
	# num_top_designs
	parser.add_argument('-n', '--num_top_designs', type=int, default=1, help='num_top_designs')
	workload = parser.parse_args().workload
	alpha = parser.parse_args().alpha
	threshold = parser.parse_args().threshold
	objective = parser.parse_args().objective
	num_top_designs = parser.parse_args().num_top_designs

	# load workload data
	with open(f'{prj_path}/tests/workloads/mm.json') as f:
		mm_workloads_dict = json.load(f)
	mm_workloads = []
	for key in mm_workloads_dict:
		problem_sizes = mm_workloads_dict[key]
		for ps in problem_sizes:
			problem_size = eval(ps)
			problem_dims = [problem_size[key] for key in problem_size.keys()]
			problem_dims_str = '_'.join([str(dim) for dim in problem_dims])
			num_points = est_num_of_designs('mm', problem_size, 1000)
			mm_workloads.append((f'{key}_{problem_dims_str}', ps, num_points))
	# sort by number of points
	mm_workloads = sorted(mm_workloads, key=lambda x: x[2])

	with open(f'{prj_path}/tests/workloads/conv.json') as f:
		conv_workloads_dict = json.load(f)
	conv_workloads = []
	for key in conv_workloads_dict:
		problem_sizes = conv_workloads_dict[key]
		for ps in problem_sizes:
			problem_size = eval(ps)
			problem_dims = [problem_size[key] for key in problem_size.keys()]
			problem_dims_str = '_'.join([str(dim) for dim in problem_dims])
			num_points = est_num_of_designs('conv', problem_size, 1000)
			conv_workloads.append((f'{key}_{problem_dims_str}', ps, num_points))	

	# sort by number of points
	conv_workloads = sorted(conv_workloads, key=lambda x: x[2])
	# all_workloads = mm_workloads + conv_workloads

	cycle_dicts = []
	throughput_dicts = []
	workload_names = []
	problem_sizes = []

	for w in mm_workloads:
		name = w[0]
		problem_size = eval(w[1])
		problem_dims = [problem_size[key] for key in problem_size.keys()]
		problem_dims_str = '_'.join([str(dim) for dim in problem_dims])
		cycles_dict, throughput_dict, runtime_dict, all_designs_dict, _ = get_data('mm', problem_dims_str, alpha, num_top_designs, threshold, objective)
		cycle_dicts.append(cycles_dict)
		throughput_dicts.append(throughput_dict)
		workload_names.append(f'{name}')
		ds_reduction = all_designs_dict["exhaustive"]/all_designs_dict["non_divisors"]
		rt_speedup = runtime_dict["exhaustive"]/runtime_dict["non_divisors"]
		ex_num_designs = get_num_designs(all_designs_dict["exhaustive"])
		nd_num_designs = get_num_designs(all_designs_dict["non_divisors"])
		ex_rt_hours = runtime_dict["exhaustive"]/3600
		nd_rt_hours = runtime_dict["non_divisors"]/3600
		ge_rt_hours = runtime_dict["odyssey"]/3600
		print(ge_rt_hours)
		print(f'{name} & {ex_num_designs} & {ex_rt_hours:.2f} & {nd_num_designs} & {nd_rt_hours:.2f} & ${ds_reduction:.1f}\\times$ & ${rt_speedup:.1f}\\times$ \\\\')
	for w in conv_workloads:
		name = w[0]
		problem_size = eval(w[1])
		problem_dims = [problem_size[key] for key in problem_size.keys()]
		problem_dims_str = '_'.join([str(dim) for dim in problem_dims])
		cycles_dict, throughput_dict, runtime_dict, all_designs_dict, _ = get_data('conv', problem_dims_str, alpha, num_top_designs, threshold, objective)
		cycle_dicts.append(cycles_dict)
		throughput_dicts.append(throughput_dict)
		workload_names.append(f'{name}')
		ds_reduction = all_designs_dict["exhaustive"]/all_designs_dict["non_divisors"]
		rt_speedup = runtime_dict["exhaustive"]/runtime_dict["non_divisors"]
		ex_num_designs = get_num_designs(all_designs_dict["exhaustive"])
		nd_num_designs = get_num_designs(all_designs_dict["non_divisors"])
		ex_rt_hours = runtime_dict["exhaustive"]/3600
		nd_rt_hours = runtime_dict["non_divisors"]/3600
		ge_rt_hours = runtime_dict["odyssey"]/3600
		print(problem_dims_str, ge_rt_hours)
		# print(f'{name} & {ex_num_designs} & {ex_rt_hours:.2f} & {nd_num_designs} & {nd_rt_hours:.2f} & ${ds_reduction:.1f}\\times$ & ${rt_speedup:.1f}\\times$ \\\\')

	colors_dict = {
		'Completed Exhaustive': '#509d86',
		'Untractable Exhaustive': '#3b3838',
		'Padding Based Algorithm': '#e38b60', 
		'Hybrid Method': '#558bb8',
		'Divisor only': '#e4be64'
		}
	# plot
	import matplotlib.pyplot as plt
	x_values = []
	y_values = []
	colors = []
	edge_colors = []
	text_above_bars = []
	x_ticks = []
	counter = 0
	for idx, td in enumerate(throughput_dicts):

		if td['exhaustive'] == 0:
			continue
			x_values.append(counter)
			speedup = 1/(td['non_divisors']/td['divisors'])
			y_values.append(speedup)
			colors.append(colors_dict['Divisor only'])
			text_above_bars.append(f'{(speedup)*100:.2f}% ')
			edge_colors.append('white')
			counter += 1

			# x_values.append(counter)
			# speedup = 1/(td['non_divisors']/td['odyssey'])
			# y_values.append(speedup)
			# colors.append(colors_dict['Hybrid Method'])
			# text_above_bars.append(f'{(speedup)*100:.2f}% ')
			# edge_colors.append('white')
			# counter += 1

			x_values.append(counter)
			y_values.append(1)
			colors.append(colors_dict['Padding Based Algorithm'])
			text_above_bars.append(f'{td["non_divisors"]:.2f} GFLOP/s ')
			edge_colors.append('white')

			counter += 1

			x_values.append(counter)
			y_values.append(1)
			colors.append('white')#colors_dict['Untractable Exhaustive'])
			text_above_bars.append(f'')
			edge_colors.append('red')
			counter += 1

			if idx < len(throughput_dicts)-1:
				x_values.append(counter)
				y_values.append(0)
				colors.append('white')
				text_above_bars.append(f'')
				edge_colors.append('white')
				counter += 1
		else:

			x_values.append(counter)
			speedup = 1/(td['exhaustive']/td['divisors'])
			y_values.append(speedup)
			colors.append(colors_dict['Divisor only'])
			text_above_bars.append(f'{(speedup)*100:.2f}% ')
			edge_colors.append('white')
			counter += 1
			
			# x_values.append(counter)
			# speedup = 1/(td['exhaustive']/td['odyssey'])
			# y_values.append(speedup)
			# colors.append(colors_dict['Hybrid Method'])
			# text_above_bars.append(f'{(speedup)*100:.2f}% ')
			# edge_colors.append('white')
			# counter += 1

			speedup = 0
			x_values.append(counter)
			speedup = 1/(td['exhaustive']/td['non_divisors'])
			y_values.append(speedup)
			colors.append(colors_dict['Padding Based Algorithm'])
			text_above_bars.append(f'{(speedup)*100:.2f}% ')
			edge_colors.append('white')
			counter += 1

			x_values.append(counter)
			y_values.append(1)
			colors.append(colors_dict['Completed Exhaustive'])
			text_above_bars.append(f'{td["exhaustive"]:.2f} GFLOP/s ')
			edge_colors.append('white')
			counter += 1
			if idx < len(throughput_dicts)-1:
				x_values.append(counter)
				y_values.append(0)
				colors.append('white')
				text_above_bars.append(f'')
				edge_colors.append('white')
				counter += 1

	from matplotlib import pyplot as plt
	import os
	# wide figure with large font
	plt.rcParams['figure.figsize'] = [17, 3]
	# small left and right margines
	plt.rcParams['figure.subplot.left'] = 0.05
	plt.rcParams['figure.subplot.right'] = 0.99
		# let bottom margine fit all text
	if workload == 'conv':
		plt.rcParams['figure.subplot.bottom'] = 0.4
	else:
		plt.rcParams['figure.subplot.bottom'] = 0.4
	# plt.rcParams.update({'font.size': 22})
	# plot bars with text above them
	plt.bar(x_values, y_values, color=colors, width=0.9, edgecolor=edge_colors)
	for i in range(len(x_values)):
		plt.text(x_values[i], y_values[i], text_above_bars[i], ha='center', va='top', rotation=90, fontsize=10)
	
	# remove xticks
	plt.xticks([])
	# add workload_names under each designs_per_dict bars
	# print(workload_names)
	for i in range(len(workload_names)):
		plt.text(x_values[i*4]+1.5, 0, f'(K{i}) {workload_names[i]}', ha='right', va='top', rotation=24)

	# add legend at lower left corner based on colors_dict
	legend_elements = [
		plt.Line2D([0], [0], marker='o', color='w', label='Divisor only', markerfacecolor=colors_dict['Divisor only'], markersize=15),
		# plt.Line2D([0], [0], marker='o', color='w', label='Hybrid Method', markerfacecolor=colors_dict['Hybrid Method'], markersize=15), 
		plt.Line2D([0], [0], marker='o', color='w', label='Padding Based Algorithm', markerfacecolor=colors_dict['Padding Based Algorithm'], markersize=15), 
		plt.Line2D([0], [0], marker='o', color='w', label='Completed Exhaustive', markerfacecolor=colors_dict['Completed Exhaustive'], markersize=15), 
		plt.Line2D([0], [0], marker='o', color='w', label='Untractable Exhaustive (> 200 B Points)', markerfacecolor='white', markeredgecolor='red', markersize=15)
	]
	# lower left corner of the figure
	plt.legend(handles=legend_elements, loc='lower left', bbox_to_anchor=(0.0, 1.1), ncol=5, borderaxespad=0, frameon=False, fontsize=7.5)
	#x axis label at the 5 pt bellow the figure
	# plt.xlabel('Designs per Workload', labelpad=5)

	
	#y-axis name
	plt.ylabel('Normalized Throughput')

	#plot title
	# plt.title('Throughput Speedup')
	# if plots folder does not exist, create it
	if not os.path.exists(f'{prj_path}/plots'):
		os.makedirs(f'{prj_path}/plots')
	# save plot
	plt.savefig(f'{prj_path}/plots/all_throughput_speedup.png')
	# save as pdf
	plt.savefig(f'{prj_path}/plots/all_throughput_speedup.pdf')