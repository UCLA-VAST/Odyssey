from matplotlib import pyplot as plt
import numpy as np
import pandas as pd
import os
import sys

n = 10
my_logs_path = 'logs'
ex_logs_path = 'exhaustive/logs'
my_results_path = 'results'
ex_results_path = 'exhaustive/results'
od_results_path = 'results'
workload = sys.argv[1]
problem_size = int(sys.argv[2])
threshold = int(sys.argv[3])
my_results_dir = os.listdir(f'{my_results_path}/{workload}')
my_results_dir.sort()
ex_results_dir = os.listdir(f'{ex_results_path}/{workload}')
ex_results_dir.sort()
od_results_dir = os.listdir(f'{od_results_path}')
od_results_dir.sort()

my_logs_dir = os.listdir(f'{my_logs_path}/{workload}')
my_logs_dir.sort()
ex_logs_dir = os.listdir(f'{ex_logs_path}/{workload}')
ex_logs_dir.sort()


def get_my_designs(results_dir, size, threshold):
  designs = []
  for result in results_dir:
    if f'{size}_{size}_{size}' in result and f'thr{threshold}' in result:
      designs.append(result)
  return designs

def get_exhaustive_designs(results_dir, size):
  designs = []
  for result in results_dir:
    if f'{size}_{size}_{size}' in result:
      designs.append(result)
  return designs

def get_od_designs(results_dir, workload, size):
  designs = []
  for result in results_dir:
    if f'{workload}_{size}_{size}_{size}' in result:
      designs.append(result)
  return designs

# my_logs = get_my_designs(my_logs_dir, problem_size, threshold)
# ex_logs = get_exhaustive_designs(ex_logs_dir, problem_size)
# out_log_file = f'plots/cycles_{workload}_{problem_size}_{threshold}.csv'
# time_list = []
# indices_list = []
# colors_list = []
# counter = 0
# with open(out_log_file, 'w') as f:
#   print('design,my_time,ex_time,speedup', file=f)
#   for idx in range(len(my_logs)):
#     my_log = open(f'{my_logs_path}/{workload}/{my_logs[idx]}', 'r')
#     ex_log = open(f'{ex_logs_path}/{workload}/{ex_logs[idx]}', 'r')
#     for line in my_log:
#       split_line = line.split()
#       my_num_designs = split_line[1].replace(',', '')
#       my_num_designs = int(my_num_designs)
#       my_time = float(split_line[5])
#       time_list.append(my_time)
#       colors_list.append('red')
#       counter += 1
#       indices_list.append(counter)
#     for line in ex_log:
#       split_line = line.split()
#       ex_num_designs = split_line[1].replace(',', '')
#       ex_num_designs = int(ex_num_designs)
#       ex_time = float(split_line[5])
#       time_list.append(ex_time)
#       colors_list.append('blue')
#       counter += 1
#       indices_list.append(counter)
#     time_list.append(0)
#     colors_list.append('white')
#     counter += 1
#     indices_list.append(counter)
#     speedup = ex_time / my_time
#     print(f'{idx},{my_time:.0f},{ex_time:.0f},{speedup:.0f}', file=f)

# # plot the time_list vs indices_list
# plt.figure(figsize=(10, 5))
# plt.bar(indices_list, time_list, color=colors_list)
# plt.xlabel('Designs')
# plt.ylabel('Time (s)')
# plt.title(f'{workload} {problem_size}x{problem_size}x{problem_size} {threshold}')
# show legend based on color
# blue is exhaustive
# red is our method
# white is the gap between designs
# plt.legend(['Exhaustive', 'Our Method'])
# plt.savefig(f'plots/time_{workload}_{problem_size}_{threshold}.png')
mysearch_designs = get_my_designs(my_results_dir, problem_size, threshold)
# exhaustive_designs = get_exhaustive_designs(ex_results_dir, problem_size)
# for design in mysearch_designs:
#   print(design)
# for design in exhaustive_designs:
#   print(design)
# exit()
od_designs = get_od_designs(od_results_dir, workload, problem_size)

cycles_list = []
indices_list = []
colors_list = []
labels_list = []
cntr = 0
od_design = od_designs[0]
od_df = pd.read_csv(f'{od_results_path}/{od_design}')
od_cycles = od_df['cycles'].values
for idx in range(len(mysearch_designs)):
  my_design = mysearch_designs[idx]
  # ex_design = exhaustive_designs[idx]
  my_df = pd.read_csv(f'{my_results_path}/{workload}/{my_design}')
  # ex_df = pd.read_csv(f'{ex_results_path}/{workload}/{ex_design}')
  my_cycles = my_df['cycles'].values
  # ex_cycles = ex_df['cycles'].values
  for i in range(3):
    cycles_list.append(od_cycles[idx*3 + i])
    labels_list.append(f'kernel_{idx}')
    indices_list.append(cntr)
    cntr += 1
    colors_list.append('green')
  for i in range(n):
    cycles_list.append(my_cycles[i])
    # cycles_list.append(ex_cycles[i])
    labels_list.append(f'kernel_{idx}')
    # labels_list.append(f'kernel_{idx}')
    # indices_list.append(cntr)
    # cntr += 1
    indices_list.append(cntr)
    cntr += 1
    colors_list.append('red')
    # colors_list.append('blue')

  cntr += 1
  cycles_list.append(np.nan)
  labels_list.append(f'')
  indices_list.append(cntr)
  colors_list.append('black')
    
print(len(cycles_list), len(indices_list), len(colors_list))

fig, ax = plt.subplots()
# make bar/column chart
ax.bar(indices_list, cycles_list, color=colors_list)
# y-axis cycles
ax.set_ylabel('Cycles')
# x-axis kernels
ax.set_xlabel('Kernels')
# show legend based on color
# red is my cycles
# blue is exhaustive cycles
# green is od cycles
# black is nan
ax.legend(handles=[plt.Rectangle((0,0),1,1, color=c, ec="k") for c in ['red', 'blue', 'green', 'black']], labels=['My Search', 'Exhaustive Search', 'Odyssey'])

# make figure wide
fig.set_figwidth(15)

# # save the plot
fig.savefig(f'plots/cycles_{workload}_{problem_size}_{threshold}.png')