import sys
import os
prj_path = os.environ['PRJ_PATH']
sys.path.append(f'{prj_path}/src')
from utils import *
import argparse
import os

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
	with open(f'{prj_path}/tests/{workload}.json') as f:
		workloads_dict = json.load(f)

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
			print(f'workload: {name}, problem size: {problem_dims_str}')
			
			# divisors
			print(f'Running divisors for {name} {ps}')
			cmd = f'python {prj_path}/src/divisor_only/divisors.py        		-w={workload} -p="{ps}" -obj={objective} -a={alpha} -n={num_top_designs}'
			os.system(cmd)

			# padding_based algorithm
			print(f'Running non_divisors for {name} {ps}')
			cmd = f'python {prj_path}/src/padding_based/non_divisors.py        -w={workload} -p="{ps}" -obj={objective} -a={alpha} -n={num_top_designs}   -thr={threshold}'
			os.system(cmd)

			# odyssey
			print(f'Running odyssey for {name} {ps}')
			cmd = f'python {prj_path}/src/randomized_search/odyssey.py             -w={workload} -p="{ps}" -obj={objective} -a={alpha} --trials=1 -to=10'
			os.system(cmd)

			# exhausitve
			estimated_points = est_num_of_designs(workload, problem_size, 1000)
			if estimated_points < 20_000_000_000:
				print(f'Running exhaustive for {name} {ps:40} {estimated_points:_}')
				cmd = f'python {prj_path}/src/exhaustive/exhaustive_search.py -w={workload} -p="{ps}" -obj={objective} -a={alpha} -n={num_top_designs}'
				path = f'{prj_path}/results/{workload}/{problem_dims_str}/design_all_all/{objective}/exhaustive'
				if not os.path.exists(path):
					print(cmd, estimated_points)
					os.system(cmd)
			else:
				print(f'Estimated points: {estimated_points:_}')
				print(f'Not running exhaustive for {name} {ps:40}')


