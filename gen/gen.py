# read csv file
import csv
import pandas as pd
import sys
import os
import re

prj_path = os.environ['PRJ_PATH']
workload = sys.argv[1]
# read csv file
designs_file = prj_path + f'/tests/results/{workload}.csv'
designs_df = pd.read_csv(designs_file)
designs_lines = open(designs_file, 'r').readlines()
target = 'autosa_hls_c'
for index, row in designs_df.iterrows():
	design_name = row['design_idx']
	sa_sizes = row['sa_sizes']
	original_workload_size = eval(row['original workload'])
	padded_workload_size = eval(row['padded workload'])
	for key in original_workload_size.keys():
		if key not in padded_workload_size.keys():
			padded_workload_size[key] = original_workload_size[key]
	original_workload_size = dict(sorted(original_workload_size.items()))
	padded_workload_size = dict(sorted(padded_workload_size.items()))
	# print(padded_workload_size)
	sa_dims = eval(row["SA_dims"])
	sa_dims = [int(x) for x in sa_dims]
	# convert tuple to elems seperated by _
	sa_dims_str = '_'.join(str(x) for x in sa_dims)
	with open(prj_path + f'/workloads/{workload}/kernel.h', 'w') as f:
		print('#include "stdio.h"', file=f)
		print('#include "stdlib.h"', file=f)
		print('#include "math.h"', file=f)
		print('', file=f)
		print('typedef float data_t;', file=f)
		for dim in padded_workload_size.keys():
			# captilize dim
			print(f'#define {dim.upper()} {padded_workload_size[dim]}', file=f)
	#mem_type: 0 FF, 1 LUTRAM, 2 BRAM, 3 URAM, 4 original autoSA, 5 no pragmas
	for mem_type in range(2, 3):
		design_name_new = f'{workload}_HLS_{design_name}_mem_{mem_type}_dims_{sa_dims_str}' if target == 'autosa_hls_c' else f'TAPA_{design_name}_mem_{mem_type}_dims_{sa_dims_str}_{workload}'
		cmd = f'{prj_path}/gen/gen.sh {design_name_new} "{sa_sizes}" {target} {mem_type} {workload} &> {prj_path}/designs/logs/{design_name_new}.log'
		print('Running command: ', cmd)
		os.system(cmd)
		with open(prj_path + f'/designs/orig/{design_name_new}/design_info.csv', 'w') as f:
			print('design_idx,objective,original workload,padded workload,fre,throughput (GFLOP/s),cycles,latency(ms),DSP eff,off-chip bytes,bandwidth (GB/s),CTC,DSPs,BRAMs,PEs,SA_dims,sa_sizes', file=f)
			print(designs_lines[index+1], file=f)
