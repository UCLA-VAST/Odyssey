import os
import sys
import json
from utils import *
import pandas as pd
from plot import plot
# workloads_path = prj_path + '/data/workload/'

# workload_files = os.listdir(workloads_path)

# cnns = ['vgg16', 'mobilenetv2', 'resnet152', 'resnet50']
# cnn_layers = {}
# for workload_file in workload_files:
#   cnn_name = workload_file.strip('.json')
#   if cnn_name in cnns:
#     cnn_layers[cnn_name] = []
#     with open(workloads_path + workload_file) as f:
#       workloads = json.load(f)['workloads']
#       for workload in workloads:
#         if 'conv' in workload['tags']:
#           if workload['params'] not in cnn_layers[cnn_name]:
#             cnn_layers[cnn_name].append(workload['params'])

# all_layers = []
# cntr = 0
# for cnn in cnns:
#   for layer in cnn_layers[cnn]:
#     num_designs_est = est_num_of_designs('conv', layer, 1000)
#     print(f'{cnn} {layer} {num_designs_est:,.0f}')
#     all_layers.append((cnn, layer, num_designs_est))
    
# all_layers.sort(key=lambda x: x[2])
# # save to csv
# with open(prj_path + '/tests/conv_layers_new.csv', 'w') as f:
#   f.write('cnn,layer,num_designs_est\n')
#   for cnn, layer, num_designs_est in all_layers:
#     f.write(f'{cnn},"{layer}",{num_designs_est:_.0f}\n')
# exit()
# print(len(uniqe_workloads))
# print(len(final_workloads))
# sort by first element of the tuple
# final_workloads.sort(key=lambda x: x[0])
# for workload in final_workloads:
#   print(workload)

# exit()

# # get 5 random workloads
# import random
# random.seed(67)
# random.shuffle(uniqe_workloads)
# uniqe_workloads = uniqe_workloads[:5]
# for workload in uniqe_workloads:
#   print(workload)

# conv_workloads = [
#   {'i': 144, 'o': 32, 'r': 28, 'c': 28, 'p': 3, 'q': 3},
#   {'i': 128, 'o': 128, 'r': 112, 'c': 112, 'p': 3, 'q': 3},
#   {'i': 512, 'o': 2048, 'r': 7, 'c': 7, 'p': 1, 'q': 1},
#   {'i': 384, 'o': 64, 'r': 14, 'c': 14, 'p': 1, 'q': 1},
#   {'i': 512, 'o': 256, 'r': 28, 'c': 28, 'p': 1, 'q': 1}
# ]
# load conv_layer.csv
with open(prj_path + '/tests/conv_layers_new.csv') as f:
  df = pd.read_csv(f)

networks = df['cnn'].tolist()
conv_workloads = df['layer'].tolist()
# map networks to workloads through tuples
workloads = list(zip(networks, conv_workloads))
# conv_workloads = [eval(layer) for layer in conv_workloads]
print(len(workloads))
# remove duplicates of same conv_workloads and different networks
unique_conv_workloads = []
unique_workloads = []
for workload in workloads:
  if workload[1] not in unique_conv_workloads:
    unique_conv_workloads.append(workload[1])
    unique_workloads.append(workload)

# get four random workloads from each network
import random
random.seed(21)#67)
random.shuffle(unique_workloads)
# workloads_dict = {'vgg16': [], 'mobilenetv2': [], 'resnet152': [], 'resnet50': []}
# for workload in unique_workloads:
#   cnn = workload[0]
#   if len(workloads_dict[cnn]) < 4:
#     workloads_dict[cnn].append(workload[1])

workload_dicts = {'mm':[]}
workload_list = [64, 128, 256, 512, 1024]
for i in workload_list:
  for j in workload_list:
    for k in workload_list:
      workload_dicts['mm'].append({'i': i, 'j': j, 'k': k})

# get 10 random workloads
import random
random.seed(67)
random.shuffle(workload_dicts['mm'])
workload_dicts['mm'] = workload_dicts['mm'][:10]
# for workload in workload_dicts['mm']:
#   print(workload) 
# exit()


# for cnn in workloads_dict:
#   print(f'cnn: {cnn}')
#   for workload in workloads_dict[cnn]:
#     print(f'\t{workload}')
# exit()
# # for conv_workload in conv_workloads
conv_workloads = unique_workloads#[conv_workloads[0]]
# conv_workloads = [
#   {'i': 3, 'o': 32, 'r': 224, 'c': 224, 'p': 3, 'q': 3}
# ]
# conv_dataflows = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
# conv_permutations = [0, 1, 2]
import time
alpha = 1
threshold = 0.5 #20% of problem size
objective = 'latency_off_chip'
num_top_designs = 1
counter = 0
# search_methods = ['exhaustive_search', 'non_divisors', 'divisors', 'odyssey']
cycle_dicts = []
throughput_dicts = []
# workload_dicts = []
for idx in range(10):
  for cnn in workload_dicts:
    # if counter < 16:
      ps = workload_dicts[cnn][idx]
      # for d in conv_dataflows:
      #   for p in conv_permutations:
      # print(f'Running divisors for {cnn} {ps}')
      problem_size = ps
      problem_dims = [problem_size[key] for key in problem_size.keys()]
      problem_dims_str = '_'.join([str(dim) for dim in problem_dims])
      # /home/suhailb/Projects/odyssey/results/conv/64_128_112_112_3_3/design_all_all/latency_off_chip/divisors/results/top_1_alpha_1.0_thr_0.csv
      # divisor_old_results = pd.read_csv(f'{prj_path}/results/conv/{problem_dims_str}/design_all_all/{objective}/divisors/results/top_{num_top_designs}_alpha_{alpha}.0_thr_0.csv')
      # if len(divisor_old_results) < 30:
      # print(f'Running exhaustive for {cnn} {ps}')
      # cmd = f'python divisors.py            -w="mm" -p="{ps}" -obj={objective} -a={alpha} -n=1'
      # os.system(cmd)
      # print(f'Running non_divisors for {cnn} {ps}')
      # cmd = f'python non_divisors.py        -w="mm" -p="{ps}" -obj={objective} -a={alpha} -n=1   -thr={threshold}'
      # os.system(cmd)
      # print(f'Running odyssey for {cnn} {ps}')
      # cmd = f'python odyssey.py             -w="mm" -p="{ps}" -obj={objective} -a={alpha}        --trials=2 -to=10'
      # os.system(cmd)
      # estimated_points = est_num_of_designs('conv', eval(ps), 1000)
      # if estimated_points < 1_000_000_000:
        # cmd = f'python exhaustive_search.py   -w="conv" -p="{ps}" -obj={objective} -a={alpha} -n=1'
        # print(cmd, estimated_points)
        # os.system(cmd)
        # print(ps)
      # print(f'Running exhaustive for {cnn} {ps}')
      # cycle_dict, throughput_dict = plot('mm', problem_dims_str, alpha, objective, ['non_divisors', 'odyssey', 'divisors'])
      # cycle_dicts.append(cycle_dict)
      # throughput_dicts.append(throughput_dict)
      # workload_dicts.append(problem_dims_str)
      # throughput_speedup_over_divisor = results[2]
      # throughput_speedup_over_non_divisor = results[3]
      # throughputs_over_divisor.append(throughput_speedup_over_divisor)
      # throughputs_over_non_divisor.append(throughput_speedup_over_non_divisor)
        # counter += 1
exit()
x_values = []
y_values = []
colors = []
text_above_bars = []
x_ticks = []
counter = 0
for idx, td in enumerate(throughput_dicts):
  td['exhaustive'] = 0
  ps = ''#workload_dicts[idx]
  if td['exhaustive'] == 0:
    # continue
    x_ticks.append(ps)

    x_values.append(counter)
    speedup = 1/(td['non_divisors']/td['divisors'])
    y_values.append(speedup)
    colors.append('red')
    text_above_bars.append(f'{(speedup)*100:.2f}%')
    counter += 1

    x_values.append(counter)
    speedup = 1/(td['non_divisors']/td['odyssey'])
    y_values.append(speedup)
    colors.append('orange')
    text_above_bars.append(f'{(speedup)*100:.2f}%')
    counter += 1

    x_values.append(counter)
    y_values.append(1)
    colors.append('blue')
    text_above_bars.append(f'')
    counter += 1

    x_values.append(counter)
    y_values.append(0)
    colors.append('white')
    text_above_bars.append(f'')
    counter += 1
  else:
    continue
    x_values.append(counter)
    speedup = 1/(td['exhaustive']/td['divisors'])
    y_values.append(speedup)
    colors.append('red')
    text_above_bars.append(f'{(speedup)*100:.2f}%')
    counter += 1
    
    x_values.append(counter)
    speedup = 1/(td['exhaustive']/td['odyssey'])
    y_values.append(speedup)
    colors.append('orange')
    text_above_bars.append(f'{(speedup)*100:.2f}%')
    counter += 1

    speedup = 0
    x_values.append(counter)
    speedup = 1/(td['exhaustive']/td['non_divisors'])
    y_values.append(speedup)
    colors.append('blue')
    text_above_bars.append(f'{(speedup)*100:.2f}%')
    counter += 1

    x_values.append(counter)
    y_values.append(1)
    colors.append('green')
    text_above_bars.append(f'')
    counter += 1

    x_values.append(counter)
    y_values.append(0)
    colors.append('white')
    text_above_bars.append(f'')
    counter += 1

from matplotlib import pyplot as plt
# wide figure with large font
plt.figure(figsize=(40, 10))
# plt.rcParams.update({'font.size': 22})
# plot bars with text above them
plt.bar(x_values, y_values, color=colors)
for i in range(len(x_values)):
  plt.text(x_values[i], y_values[i], text_above_bars[i], ha='center', va='bottom')
#x-axis name
plt.xlabel('Convolutional Layers')
#y-axis name
plt.ylabel('Throughput Speedup')
# for each four bars, add a x-axis label

# double the width of the plot
# plt.rcParams["figure.figsize"] = (20, 5)

#plot title
plt.title('Throughput Speedup of Non-Divisors over Divisors')
# legend based on colors, blue for divisor, red for non-divisor
# plt.legend(['Divisors', 'Non-Divisors'])


# save plot
plt.savefig('mm_throughput_speedup.png')

