import sys
sys.path.append('./src')
from utils import *
import argparse

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
	with open(f'{prj_path}/tests/workloads/{workload}.json') as f:
		workloads_dict = json.load(f)
		

	cycle_dicts = []
	throughput_dicts = []
	runtime_dicts = []
	all_designs_dicts = []
	valid_designs_dicts = []
	workload_names = []
	problem_sizes = []
	# get first item from workloads_dict
	for key in workloads_dict:
		designs_per_dict = len(workloads_dict[key])
		break
	for idx in range(designs_per_dict):
		for name in workloads_dict:
			ps = workloads_dict[name][idx]
			problem_size = eval(ps)
			problem_dims = [problem_size[key] for key in problem_size.keys()]
			problem_dims_str = '_'.join([str(dim) for dim in problem_dims])

			cycles_dict, throughput_dict, runtime_dict, all_designs_dict, valid_designs_dict = get_data(workload, problem_dims_str, alpha, num_top_designs, threshold, objective)
			runtime_dicts.append(runtime_dict)
			all_designs_dicts.append(all_designs_dict)
			valid_designs_dicts.append(valid_designs_dict)
			workload_names.append(f'{name}_{problem_dims_str}')
			# if runtime_dict['exhaustive'] != 0:
			# 	seconds = runtime_dict['exhaustive'] 
			# 	hours = seconds / 3600
			# 	days = hours / 24
			# 	print(f'Exhaustive {ps}: {seconds} seconds, {hours} hours, {days} days')
			# cycle_dicts.append(cycles_dict)
			# throughput_dicts.append(throughput_dict)
			# workload_names.append(f'{name}_{problem_dims_str}')
			# problem_sizes.append(problem_dims_str)
	with open('mm_runtime.csv', 'w') as f:
		for name, rt, ad in zip(workload_names, runtime_dicts, all_designs_dicts):
			if rt['exhaustive'] != 0:
				exhaustive_hours = rt['exhaustive'] / 3600
				exhaustive_ad = ad['exhaustive']
				non_div_hours = rt['non_divisors'] / 3600
				non_div_ad = ad['non_divisors']
				time_speedup = exhaustive_hours / non_div_hours
				ad_percentage = (non_div_ad/exhaustive_ad)
				print(f'{name}, {exhaustive_ad:}, {exhaustive_hours:.2f},  {non_div_ad:}, {non_div_hours:.2f}, {ad_percentage:.10f}, {time_speedup:.2f}', file=f)
			# print(f'non_divisor_speedup_over_exhaustive: {non_divisor_speedup_over_exhaustive:.2f}, genetic_speedup_over_exhaustive: {genetic_speedup_over_exhaustive:.2f}')
	# for ad in all_designs_dicts:
	# 	if ad['exhaustive'] != 0:
	# 		all_designs = ad['exhaustive']
	# 		non_divisor_all_designs = ad['non_divisors']
	# 		percentage = (non_divisor_all_designs / all_designs)*100
	# 		print(f'{all_designs}, {non_divisor_all_designs}, {percentage:.2f}%')
	exit()
	colors_dict = {
		'Completed Exhaustive': 'green',
		'Untractable Exhaustive': 'black',
		'Padding Based Algorithm': 'blue', 
		'Hybrid Method': 'orange',
		'Divisor only': 'red'
		}
	# plot
	import matplotlib.pyplot as plt
	x_values = []
	y_values = []
	colors = []
	text_above_bars = []
	x_ticks = []
	counter = 0
	for idx, rt in enumerate(runtime_dicts):

		if rt['exhaustive'] == 0:
			continue
			x_values.append(counter)
			speedup = 1/(td['non_divisors']/td['divisors'])
			y_values.append(speedup)
			colors.append(colors_dict['Divisor only'])
			text_above_bars.append(f'{(speedup)*100:.2f}%')
			counter += 1

			x_values.append(counter)
			speedup = 1/(td['non_divisors']/td['odyssey'])
			y_values.append(speedup)
			colors.append(colors_dict['Hybrid Method'])
			text_above_bars.append(f'{(speedup)*100:.2f}%')
			counter += 1

			x_values.append(counter)
			y_values.append(1)
			colors.append(colors_dict['Padding Based Algorithm'])
			text_above_bars.append(f'')
			counter += 1

			x_values.append(counter)
			y_values.append(1)
			colors.append(colors_dict['Untractable Exhaustive'])
			text_above_bars.append(f'')
			counter += 1

			if idx < len(throughput_dicts)-1:
				x_values.append(counter)
				y_values.append(0)
				colors.append('white')
				text_above_bars.append(f'')
				counter += 1
		else:
			
			x_values.append(counter)
			y_values.append(rt['odyssey'])
			colors.append(colors_dict['Hybrid Method'])
			# text_above_bars.append(f'{(speedup)*100:.2f}%')
			counter += 1

			speedup = 0
			x_values.append(counter)
			y_values.append(rt['non_divisors'])
			colors.append(colors_dict['Padding Based Algorithm'])
			# text_above_bars.append(f'{(speedup)*100:.2f}%')
			counter += 1

			x_values.append(counter)
			y_values.append(rt['exhaustive'])
			colors.append(colors_dict['Completed Exhaustive'])
			# text_above_bars.append(f'')
			counter += 1
			if idx < len(throughput_dicts)-1:
				x_values.append(counter)
				y_values.append(0)
				colors.append('white')
				# text_above_bars.append(f'')
				counter += 1

	from matplotlib import pyplot as plt
	import os
	# wide figure with large font
	plt.rcParams['figure.figsize'] = [20, 4]
	# small left and right margines
	plt.rcParams['figure.subplot.left'] = 0.05
	plt.rcParams['figure.subplot.right'] = 0.95
		# let bottom margine fit all text
	if workload == 'conv':
		plt.rcParams['figure.subplot.bottom'] = 0.45
	else:
		plt.rcParams['figure.subplot.bottom'] = 0.3
	# plt.rcParams.update({'font.size': 22})
	# plot bars with text above them
	plt.bar(x_values, y_values, color=colors)
	# logaritmic scale
	plt.yscale('log')
	# for i in range(len(x_values)):
	# 	plt.text(x_values[i], y_values[i], text_above_bars[i], ha='center', va='top', rotation=90)
	
	# remove xticks
	plt.xticks([])
	# add workload_names under each designs_per_dict bars
	# print(workload_names)
	# for i in range(len(workload_names)):
	# 	plt.text(x_values[i*5]+1.5, 0, workload_names[i], ha='left', va='top', rotation=-45)

	# add legend at lower left corner based on colors_dict
	legend_elements = [plt.Line2D([0], [0], marker='o', color='w', label='Completed Exhaustive', markerfacecolor=colors_dict['Completed Exhaustive'], markersize=15), 
		plt.Line2D([0], [0], marker='o', color='w', label='Untractable Exhaustive', markerfacecolor=colors_dict['Untractable Exhaustive'], markersize=15), 
		plt.Line2D([0], [0], marker='o', color='w', label='Padding Based Algorithm', markerfacecolor=colors_dict['Padding Based Algorithm'], markersize=15), 
		plt.Line2D([0], [0], marker='o', color='w', label='Hybrid Method', markerfacecolor=colors_dict['Hybrid Method'], markersize=15), 
		plt.Line2D([0], [0], marker='o', color='w', label='Divisor only', markerfacecolor=colors_dict['Divisor only'], markersize=15)]
	# lower left corner of the figure
	plt.legend(handles=legend_elements, loc='lower left', bbox_to_anchor=(0, 1.01), ncol=5, borderaxespad=0, frameon=False)
	#y-axis name
	# plt.ylabel('Normalized Throughput Speedup')

	#plot title
	# plt.title('Throughput Speedup')
	# if plots folder does not exist, create it
	if not os.path.exists(f'{prj_path}/plots'):
		os.makedirs(f'{prj_path}/plots')
	# save plot
	plt.savefig(f'{prj_path}/plots/{workload}_runtime_speedup.png')
	# save as pdf
	# plt.savefig(f'{prj_path}/plots/{workload}_throughput_speedup.pdf')