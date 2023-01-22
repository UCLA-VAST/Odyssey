from matplotlib import pyplot as plt
import numpy as np
import pandas as pd
from utils import *

# conv workloads
with open(prj_path + '/tests/conv_layers_new.csv') as f:
	df = pd.read_csv(f)

networks = df['cnn'].tolist()
conv_workloads = df['layer'].tolist()
# map networks to workloads through tuples
workloads = list(zip(networks, conv_workloads))

unique_conv_workloads = []
unique_workloads = []
for workload in workloads:
	if workload[1] not in unique_conv_workloads:
		unique_conv_workloads.append(workload[1])
		unique_workloads.append(workload)

# get four random workloads from each network
import random
random.seed(21)
random.shuffle(unique_workloads)
workloads_dict = {'vgg16': [], 'mobilenetv2': [], 'resnet152': [], 'resnet50': []}
for workload in unique_workloads:
	cnn = workload[0]
	if len(workloads_dict[cnn]) < 4:
		workloads_dict[cnn].append(workload[1])

alpha = 1.0
threshold = 0.5 
objective = 'latency_off_chip'
num_top_designs = 1
workload = 'conv'
cycle_dicts = []
throughput_dicts = []
workload_names = []
problem_sizes = []
for idx in range(4):
	for cnn in workloads_dict:
		ps = workloads_dict[cnn][idx]
		problem_size = eval(ps)
		problem_dims = [problem_size[key] for key in problem_size.keys()]
		problem_dims_str = '_'.join([str(dim) for dim in problem_dims])
		workload_names.append(cnn)
		problem_sizes.append(problem_dims_str)
		cycles_dict, throughput_dict = get_data(workload, problem_dims_str, alpha, num_top_designs, threshold, objective)
		cycle_dicts.append(cycles_dict)
		throughput_dicts.append(throughput_dict)

