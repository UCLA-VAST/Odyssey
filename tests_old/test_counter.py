from utils import *
import time

conv_workloads = [
  {'i': 1024, 'o': 1024, 'r': 1024, 'c': 1024, 'p': 3, 'q': 3}, #resnet50
  # {'i': 64, 'o': 64, 'r': 56, 'c': 56, 'p': 1, 'q': 1}, #resnet50

  # {'i': 64, 'o': 64, 'r': 64, 'c': 64, 'p': 3, 'q': 3},
  # {'i': 144, 'o': 32, 'r': 28, 'c': 28, 'p': 3, 'q': 3},
  # {'i': 128, 'o': 128, 'r': 112, 'c': 112, 'p': 3, 'q': 3},
  # {'i': 512, 'o': 2048, 'r': 7, 'c': 7, 'p': 1, 'q': 1},
  # {'i': 384, 'o': 64, 'r': 14, 'c': 14, 'p': 1, 'q': 1},
  # {'i': 512, 'o': 256, 'r': 28, 'c': 28, 'p': 1, 'q': 1}
]

for problem_size in conv_workloads:
  num_designs_est = est_num_of_designs('conv', problem_size, 100)
  print(f'num_designs_est for {problem_size}: {num_designs_est:,}')

mm_workloads = [
  {'i': 1024, 'j': 1024, 'k': 1024}
]

for problem_size in mm_workloads:
  num_designs_est = est_num_of_designs('mm', problem_size, 100)
  print(f'num_designs_est for {problem_size}: {num_designs_est:,}')

exit()
# dim = 128
# problem_size = {'i': dim, 'j': dim, 'k': dim}
# workload = 'mm'

# time_start = time.time()
# num_designs = get_num_of_designs(workload, problem_size)
# time_end = time.time()
# print(f'num_designs: {num_designs:,} in {time_end - time_start} seconds')

# time_start = time.time()
# num_designs_est = est_num_of_designs(workload, problem_size, 100)
# time_end = time.time()
# print(f'num_designs_est: {num_designs_est:,} in {time_end - time_start} seconds')
# exit()

# dim = 64
# problem_size = {'i': dim, 'o': dim, 'r': dim, 'c': dim, 'p': dim, 'q': dim}
# workload = 'conv'

# time_start = time.time()
# num_designs = get_num_of_designs(workload, problem_size)
# time_end = time.time()
# print(f'num_designs: {num_designs:,} in {time_end - time_start} seconds')

# time_start = time.time()
# num_designs_est = est_num_of_designs(workload, problem_size, 100)
# time_end = time.time()
# print(f'num_designs_est: {num_designs_est:,} in {time_end - time_start} seconds')

from math import log10, sqrt

def log_bound(dim, threshold):
    return threshold*log10(dim)

def sqrt_bound(dim, threshold):
    return threshold*sqrt(dim)

dims = [64, 128, 256, 512, 1024, 2048, 4096, 8192]
for dim in dims:
  print(f'{dim:5} {int(log_bound(dim, 3)):5} {int(sqrt_bound(dim, 0.5)):5}')

# 0 <= threshold <= (dim-1)/log10(dim)
# print(f'lb: {0}, ub: {(dim-1)/log10(dim)}')
# threshold = 3
# print(f'log10({dim}) = {threshold*log10(dim)}')

# threshold = (dim-1)/log10(dim)
# print(f'log10({dim}) = {threshold*log10(dim)}')

# # 0 <= threshold <= (dim-1)/sqrt(dim)
# print(f'lb: {0}, ub: {(dim-1)/sqrt(dim)}')
# threshold = 0.5
# print(f'sqrt({dim}) = {threshold*sqrt(dim)}')

# threshold = (dim-1)/sqrt(dim)
# print(f'sqrt({dim}) = {threshold*sqrt(dim)}')