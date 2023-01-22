import pandas as pd
import os
problem_sizes = [
	{'i': 64, 'o': 128, 'r': 112, 'c': 112, 'p': 3, 'q': 3},
	{'i': 16, 'o': 96, 'r': 112, 'c': 112, 'p': 1, 'q': 1},
	{'i': 2048, 'o': 512, 'r': 7, 'c': 7, 'p': 1, 'q': 1},
	{'i': 128, 'o': 512, 'r': 28, 'c': 28, 'p': 1, 'q': 1},
	{'i': 256, 'o': 512, 'r': 28, 'c': 28, 'p': 3, 'q': 3},
	{'i': 96, 'o': 576, 'r': 14, 'c': 14, 'p': 1, 'q': 1},
	{'i': 1024, 'o': 512, 'r': 7, 'c': 7, 'p': 1, 'q': 1},
	{'i': 512, 'o': 512, 'r': 7, 'c': 7, 'p': 3, 'q': 3},
	{'i': 64, 'o': 64, 'r': 224, 'c': 224, 'p': 3, 'q': 3},
	{'i': 64, 'o': 192, 'r': 14, 'c': 14, 'p': 1, 'q': 1},
	{'i': 1024, 'o': 256, 'r': 14, 'c': 14, 'p': 1, 'q': 1},
	{'i': 128, 'o': 128, 'r': 28, 'c': 28, 'p': 3, 'q': 3},
	{'i': 512, 'o': 512, 'r': 14, 'c': 14, 'p': 3, 'q': 3},
	{'i': 64, 'o': 384, 'r': 14, 'c': 14, 'p': 1, 'q': 1},
	{'i': 256, 'o': 1024, 'r': 14, 'c': 14, 'p': 1, 'q': 1},
	{'i': 512, 'o': 2048, 'r': 7, 'c': 7, 'p': 1, 'q': 1}
]
prj_path = os.environ["PRJ_PATH"]
workload = 'conv'
objective = 'latency_off_chip'
search_methods = ['divisors', 'non_divisors']
divisor_designs = []
non_divisor_designs = []
for problem_size in problem_sizes:
	problem_dims = [problem_size[key] for key in problem_size.keys()]
	problem_dims_str = '_'.join([str(dim) for dim in problem_dims])
	results_path = f'{prj_path}/results/{workload}/{problem_dims_str}/design_all_all/{objective}/'
	for search_method in search_methods:
		# regex first file ending with .csv
		csv_file = [f for f in os.listdir(f'{results_path}{search_method}/results/') if f.endswith('.csv')][0]
		csv_path = f'{results_path}{search_method}/results/{csv_file}'
		df = pd.read_csv(csv_path)
		# sort df by 'cycles'
		df = df.sort_values(by=['cycles'])
		for i in range(1):
			design_name = df.iloc[i]['design_idx']
			cycles = df.iloc[i]['cycles']
			throughput = df.iloc[i]['throughput (GFLOP/s)']
			DSPs = df.iloc[i]['DSPs']
			BRAMs = df.iloc[i]['BRAMs']
			if search_method == 'divisors':
				divisor_designs.append([problem_dims_str, search_method, design_name, cycles, throughput, DSPs, BRAMs])
			elif search_method == 'non_divisors':
				non_divisor_designs.append([problem_dims_str, search_method, design_name, cycles, throughput, DSPs, BRAMs])
		# print cycles of top 1 design
		# print(f'{search_method}: {df.iloc[0]["cycles"]}')

for div, non_div in zip(divisor_designs, non_divisor_designs):
	speedup = div[3] / non_div[3]
	print(f'{div[0]} vs {non_div[2]}: {speedup}')