from matplotlib import pyplot as plt
import numpy as np
from utils import *

# mm workload
workloads_dict = {'mm':[]}
workload_list = [64, 128, 256, 512, 1024]
for i in workload_list:
	for j in workload_list:
		for k in workload_list:
			workloads_dict['mm'].append(str({'i': i, 'j': j, 'k': k}))

# get 10 random workloads
import random
random.seed(67)
random.shuffle(workloads_dict['mm'])
workloads_dict['mm'] = workloads_dict['mm'][:10]


alpha = 1.0
threshold = 0.5 
objective = 'latency_off_chip'
num_top_designs = 1
workload = 'mm'
cycle_dicts = []
throughput_dicts = []
workload_names = []
problem_sizes = []
for idx in range(10):
	for mm in workloads_dict:
		ps = workloads_dict[mm][idx]
		problem_size = ps
		problem_dims = [problem_size[key] for key in problem_size.keys()]
		problem_dims_str = '_'.join([str(dim) for dim in problem_dims])
		workload_names.append(mm)
		problem_sizes.append(problem_dims_str)
		cycles_dict, throughput_dict = get_data(workload, problem_dims_str, alpha, num_top_designs, threshold, objective)
		cycle_dicts.append(cycles_dict)
		throughput_dicts.append(throughput_dict)

