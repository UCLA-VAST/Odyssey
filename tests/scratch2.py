# from matplotlib import pyplot as plt
# import numpy as np
# input_file = open("out128.log", "r").readlines()
# i_indices = []
# j_indices = []
# theoretical_min_latencies = []
# actual_min_latencies = []
# for line in input_file:
#   i, j, min_lat, act_lat = eval(line)
#   i_indices.append(i)
#   j_indices.append(j)
#   theoretical_min_latencies.append(min_lat)
#   actual_min_latencies.append(act_lat)

# # plt.plot(i_indices, theoretical_min_latencies, 'o', color='b', markersize=1)
# plt.plot(j_indices, actual_min_latencies, 'o', color='r', markersize=1)
# plt.xlabel('i')
# plt.ylabel('latency')
# plt.savefig('latency_128.png')

from math import ceil
def est_latency(params):
	i, j, k, i_t1, j_t1, k_t1, i_t2, j_t2, k_t2, p9, p10, p11, p12 = params["i"], params["j"], params["k"], params["i_t1"], params["j_t1"], params["k_t1"], params["i_t2"], params["j_t2"], params["k_t2"], params["p9"], params["p10"], params["p11"], params["p12"]

	A_IO_L2_in_single_latency = ((i_t1/i_t2) * (i_t2*k_t1/p9) + 1)
	A_IO_L3_in_single_latency = (i_t1/i_t2) * (i_t2*k_t1/min(p9, 512/8/4))
	B_IO_L2_in_single_latency = ((j_t1/j_t2) * (j_t2*k_t1/p10) + 1)
	B_IO_L3_in_single_latency = (j_t1/j_t2) * (j_t2*k_t1/min(p10, 512/8/4))
	latency_prologue = max(A_IO_L2_in_single_latency, A_IO_L3_in_single_latency, B_IO_L2_in_single_latency, B_IO_L3_in_single_latency)

	C_drain_IO_L1_out_single_latency = (i_t1/i_t2) * (i_t2*j_t2/p12)
	C_drain_IO_L2_out_single_latency = (j_t1/j_t2) * (i_t1/i_t2) * (i_t2*j_t2/p12)
	C_drain_IO_L3_out_single_latency = (j_t1/j_t2) * (i_t1/i_t2) * (i_t2*j_t2/min(p12, 512/8/4))
	latency_epilogue = max(C_drain_IO_L1_out_single_latency, C_drain_IO_L2_out_single_latency, C_drain_IO_L3_out_single_latency)

	A_IO_L2_in_latency = ceil((i/i_t1)) * ceil((j/j_t1)) * ceil((k/k_t1)) * (max((i_t1/i_t2) * (i_t2*k_t1/p9), (k_t1/k_t2) * j_t2 * i_t2 * 1) + 1)
	A_IO_L3_in_latency = ceil((i/i_t1)) * ceil((j/j_t1)) * ceil((k/k_t1)) * (i_t1/i_t2) * (i_t2*k_t1/min(p9, 512/8/4))
	B_IO_L2_in_latency = ceil((i/i_t1)) * ceil((j/j_t1)) * ceil((k/k_t1)) * (max((j_t1/j_t2) * (j_t2*k_t1/p10), (k_t1/k_t2) * j_t2 * i_t2 * 1) + 1)
	B_IO_L3_in_latency = ceil((i/i_t1)) * ceil((j/j_t1)) * ceil((k/k_t1)) * (j_t1/j_t2) * (j_t2*k_t1/min(p10, 512/8/4))
	C_drain_IO_L1_out_latency = ceil((i/i_t1)) * ceil((j/j_t1)) * ((i_t1/i_t2) * (i_t2*j_t2/p12) + j_t2 * i_t2 * 1)
	C_drain_IO_L2_out_latency = ceil((i/i_t1)) * ceil((j/j_t1)) * (j_t1/j_t2) * (i_t1/i_t2) * (i_t2*j_t2/p12)
	C_drain_IO_L3_out_latency = ceil((i/i_t1)) * ceil((j/j_t1)) * (j_t1/j_t2) * (i_t1/i_t2) * (i_t2*j_t2/min(p12, 512/8/4))
	PE_latency = ceil((i/i_t1)) * ceil((j/j_t1)) * ceil((k/k_t1)) * (k_t1/k_t2) * j_t2 * i_t2 * 1
	latency_main = max(A_IO_L2_in_latency, A_IO_L3_in_latency, B_IO_L2_in_latency, B_IO_L3_in_latency, C_drain_IO_L1_out_latency, C_drain_IO_L2_out_latency, C_drain_IO_L3_out_latency, PE_latency)

	latency = latency_prologue + latency_main + latency_epilogue

	# Meta information, used for conv fusion only
	latency_meta = {"latency_prologue": {}, "latency_main": {}, "latency_epilogue": {}}
	latency_meta["latency_prologue"]["A_IO_L2_in_single_latency"] = A_IO_L2_in_single_latency
	latency_meta["latency_prologue"]["A_IO_L3_in_single_latency"] = A_IO_L3_in_single_latency
	latency_meta["latency_prologue"]["B_IO_L2_in_single_latency"] = B_IO_L2_in_single_latency
	latency_meta["latency_prologue"]["B_IO_L3_in_single_latency"] = B_IO_L3_in_single_latency
	latency_meta["latency_epilogue"]["C_drain_IO_L1_out_single_latency"] = C_drain_IO_L1_out_single_latency
	latency_meta["latency_epilogue"]["C_drain_IO_L2_out_single_latency"] = C_drain_IO_L2_out_single_latency
	latency_meta["latency_epilogue"]["C_drain_IO_L3_out_single_latency"] = C_drain_IO_L3_out_single_latency
	latency_meta["latency_main"]["A_IO_L2_in_latency"] = A_IO_L2_in_latency
	latency_meta["latency_main"]["A_IO_L3_in_latency"] = A_IO_L3_in_latency
	latency_meta["latency_main"]["B_IO_L2_in_latency"] = B_IO_L2_in_latency
	latency_meta["latency_main"]["B_IO_L3_in_latency"] = B_IO_L3_in_latency
	latency_meta["latency_main"]["C_drain_IO_L1_out_latency"] = C_drain_IO_L1_out_latency
	latency_meta["latency_main"]["C_drain_IO_L2_out_latency"] = C_drain_IO_L2_out_latency
	latency_meta["latency_main"]["C_drain_IO_L3_out_latency"] = C_drain_IO_L3_out_latency
	latency_meta["latency_main"]["PE_latency"] = PE_latency
	return latency, latency_meta

params = {
  'i': 1024,
  'j': 1040,
  'k': 1024,
  'i_t1': 128,
  'j_t1': 104,
  'k_t1': 128,
  'i_t2': 4,
  'j_t2': 8,
  'k_t2': 4,
  'p9': 16,
  'p10': 16,
  'p11': 0,
  'p12': 4
}
print(est_latency(params)[0])
params = {
  'i': 1024,
  'j': 1024,
  'k': 1024,
  'i_t1': 256,
  'j_t1': 256,
  'k_t1': 256,
  'i_t2': 4,
  'j_t2': 32,
  'k_t2': 4,
  'p9': 16,
  'p10': 16,
  'p11': 0,
  'p12': 4
}
print(est_latency(params)[0])