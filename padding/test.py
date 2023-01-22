import numpy as np
import time
from tqdm import tqdm
import matplotlib.pyplot as plt
from math import ceil

def get_padded_candidates(n):
	candidates = [x for x in range(1,n)]
	padded_sizes = []
	for i in candidates:
		padded_size = ceil(n/i)*i
		padded_sizes.append(padded_size)
	padded_sizes = list(set(padded_sizes))
	# sort
	padded_sizes.sort()
	return padded_sizes

def est_DSP(params):
  i, j, k, i_t1, j_t1, k_t1 = params['i'], params['j'], params['k'], params['i_t1'], params['j_t1'], params['k_t1']
  DSP = i_t1*j_t1*k_t1*5
  return DSP

def est_BRAM(params):
  i, j, k, i_t1, j_t1, k_t1 = params['i'], params['j'], params['k'], params['i_t1'], params['j_t1'], params['k_t1']
  BRAM = i_t1*j_t1 + j_t1*k_t1 + i_t1*k_t1
  return BRAM

def est_cycles(params):
  i, j, k, i_t1, j_t1, k_t1 = params['i'], params['j'], params['k'], params['i_t1'], params['j_t1'], params['k_t1']
  cycles = np.ceil(i/i_t1) * np.ceil(j/j_t1) * np.ceil(k/k_t1)
  return cycles

def search_padded_candidate(I, J, K, DSP_limit, BRAM_limit, non_div=True):
  i_t1_candidates = [x for x in range(1, I+1) if I % x == 0] if not non_div else [x for x in range(1, I+1)]
  j_t1_candidates = [x for x in range(1, J+1) if J % x == 0] if not non_div else [x for x in range(1, J+1)]
  k_t1_candidates = [x for x in range(1, K+1) if K % x == 0] if not non_div else [x for x in range(1, K+1)]
  min_cycles = np.inf
  top_result = None
  for i_t1 in i_t1_candidates:
    for j_t1 in j_t1_candidates:
      for k_t1 in k_t1_candidates:
        params = {'i': I, 'j': J, 'k': K, 'i_t1': i_t1, 'j_t1': j_t1, 'k_t1': k_t1}
        DSPs = est_DSP(params)
        BRAMs = est_BRAM(params)
        cycles = est_cycles(params)
        if DSPs > DSP_limit or BRAMs > BRAM_limit:
          continue
        result = {'DSP': DSPs,  'BRAM': BRAMs, 'cycles': cycles, 'params': params}
        if cycles < min_cycles:
          min_cycles = cycles
          top_result = result
  return top_result

DSP_limit = 5000
BRAM_limit = 190
I, J, K = 64, 64, 64
# print(search_padded_candidate(I, J, K, DSP_limit, BRAM_limit, False))
# exit()
i_t0_candidates = get_padded_candidates(I)
j_t0_candidates = get_padded_candidates(J)
k_t0_candidates = get_padded_candidates(K)

best_result = {'DSP': np.inf, 'BRAM': np.inf, 'cycles': np.inf, 'params': None}
x_axis = []
y_axis = []
actual_cycles_list = []
lower_cycles_list = []
x_colors = []
y_colors = []
for i_t0 in tqdm(i_t0_candidates):
  for j_t0 in j_t0_candidates:
    for k_t0 in k_t0_candidates:
      x_axis.append(i_t0)
      y_axis.append(j_t0)
      x_colors.append('blue' if i_t0 == I else 'red')
      y_colors.append('blue' if j_t0 == J else 'red')
      result = search_padded_candidate(i_t0, j_t0, k_t0, DSP_limit, BRAM_limit)
      actual_cycles_list.append(result['cycles'])
      lower_cycles = i_t0*j_t0*k_t0/(DSP_limit/5)
      lower_cycles_list.append(lower_cycles)
      if result['cycles'] < best_result['cycles']:
        best_result = result
print(best_result)
#make a 3d plot
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')
ax.scatter(x_axis, y_axis, actual_cycles_list, c=
# ax.scatter(x_axis, y_axis, lower_cycles_list, c='b', marker='o')
ax.set_xlabel('i_t0')
ax.set_ylabel('j_t0')
ax.set_zlabel('cycles')
plt.show()
# save the figure
plt.savefig('3d_plot.png') 
# plt.plot(x_axis, actual_cycles_list)
# plt.plot(x_axis, lower_cycles_list)
# # save the figure
# # add vertical line at 2*I
# plt.axvline(x=2*I, color='r', linestyle='--')
# plt.savefig(f'test_{I}_{J}_{K}.png')
# # clear the figure
# plt.clf()

# A = []
# B = []
# C = []

# Ti = 64
# Tj = 64
# Tk = 64

# for i in range(I/Ti):
#   for j in range(J/Tj):
#     for k in range(K/Tk):
#       for ti in range(Ti):
#         for tj in range(Tj):
#           for tk in range(Tk):
