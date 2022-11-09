# # from matplotlib import pyplot as plt
# # import numpy as np
# # input_file = open("out128.log", "r").readlines()
# # i_indices = []
# # j_indices = []
# # theoretical_min_latencies = []
# # actual_min_latencies = []
# # for line in input_file:
# #   i, j, min_lat, act_lat = eval(line)
# #   i_indices.append(i)
# #   j_indices.append(j)
# #   theoretical_min_latencies.append(min_lat)
# #   actual_min_latencies.append(act_lat)

# # # plt.plot(i_indices, theoretical_min_latencies, 'o', color='b', markersize=1)
# # plt.plot(j_indices, actual_min_latencies, 'o', color='r', markersize=1)
# # plt.xlabel('i')
# # plt.ylabel('latency')
# # plt.savefig('latency_128.png')

# from math import ceil
# def est_latency(params):
# 	i, j, k, i_t1, j_t1, k_t1, i_t2, j_t2, k_t2, p9, p10, p11, p12 = params["i"], params["j"], params["k"], params["i_t1"], params["j_t1"], params["k_t1"], params["i_t2"], params["j_t2"], params["k_t2"], params["p9"], params["p10"], params["p11"], params["p12"]

# 	A_IO_L2_in_single_latency = ((i_t1/i_t2) * (i_t2*k_t1/p9) + 1)
# 	A_IO_L3_in_single_latency = (i_t1/i_t2) * (i_t2*k_t1/min(p9, 512/8/4))
# 	B_IO_L2_in_single_latency = ((j_t1/j_t2) * (j_t2*k_t1/p10) + 1)
# 	B_IO_L3_in_single_latency = (j_t1/j_t2) * (j_t2*k_t1/min(p10, 512/8/4))
# 	latency_prologue = max(A_IO_L2_in_single_latency, A_IO_L3_in_single_latency, B_IO_L2_in_single_latency, B_IO_L3_in_single_latency)

# 	C_drain_IO_L1_out_single_latency = (i_t1/i_t2) * (i_t2*j_t2/p12)
# 	C_drain_IO_L2_out_single_latency = (j_t1/j_t2) * (i_t1/i_t2) * (i_t2*j_t2/p12)
# 	C_drain_IO_L3_out_single_latency = (j_t1/j_t2) * (i_t1/i_t2) * (i_t2*j_t2/min(p12, 512/8/4))
# 	latency_epilogue = max(C_drain_IO_L1_out_single_latency, C_drain_IO_L2_out_single_latency, C_drain_IO_L3_out_single_latency)

# 	A_IO_L2_in_latency = ceil((i/i_t1)) * ceil((j/j_t1)) * ceil((k/k_t1)) * (max((i_t1/i_t2) * (i_t2*k_t1/p9), (k_t1/k_t2) * j_t2 * i_t2 * 1) + 1)
# 	A_IO_L3_in_latency = ceil((i/i_t1)) * ceil((j/j_t1)) * ceil((k/k_t1)) * (i_t1/i_t2) * (i_t2*k_t1/min(p9, 512/8/4))
# 	B_IO_L2_in_latency = ceil((i/i_t1)) * ceil((j/j_t1)) * ceil((k/k_t1)) * (max((j_t1/j_t2) * (j_t2*k_t1/p10), (k_t1/k_t2) * j_t2 * i_t2 * 1) + 1)
# 	B_IO_L3_in_latency = ceil((i/i_t1)) * ceil((j/j_t1)) * ceil((k/k_t1)) * (j_t1/j_t2) * (j_t2*k_t1/min(p10, 512/8/4))
# 	C_drain_IO_L1_out_latency = ceil((i/i_t1)) * ceil((j/j_t1)) * ((i_t1/i_t2) * (i_t2*j_t2/p12) + j_t2 * i_t2 * 1)
# 	C_drain_IO_L2_out_latency = ceil((i/i_t1)) * ceil((j/j_t1)) * (j_t1/j_t2) * (i_t1/i_t2) * (i_t2*j_t2/p12)
# 	C_drain_IO_L3_out_latency = ceil((i/i_t1)) * ceil((j/j_t1)) * (j_t1/j_t2) * (i_t1/i_t2) * (i_t2*j_t2/min(p12, 512/8/4))
# 	PE_latency = ceil((i/i_t1)) * ceil((j/j_t1)) * ceil((k/k_t1)) * (k_t1/k_t2) * j_t2 * i_t2 * 1
# 	latency_main = max(A_IO_L2_in_latency, A_IO_L3_in_latency, B_IO_L2_in_latency, B_IO_L3_in_latency, C_drain_IO_L1_out_latency, C_drain_IO_L2_out_latency, C_drain_IO_L3_out_latency, PE_latency)

# 	latency = latency_prologue + latency_main + latency_epilogue

# 	# Meta information, used for conv fusion only
# 	latency_meta = {"latency_prologue": {}, "latency_main": {}, "latency_epilogue": {}}
# 	latency_meta["latency_prologue"]["A_IO_L2_in_single_latency"] = A_IO_L2_in_single_latency
# 	latency_meta["latency_prologue"]["A_IO_L3_in_single_latency"] = A_IO_L3_in_single_latency
# 	latency_meta["latency_prologue"]["B_IO_L2_in_single_latency"] = B_IO_L2_in_single_latency
# 	latency_meta["latency_prologue"]["B_IO_L3_in_single_latency"] = B_IO_L3_in_single_latency
# 	latency_meta["latency_epilogue"]["C_drain_IO_L1_out_single_latency"] = C_drain_IO_L1_out_single_latency
# 	latency_meta["latency_epilogue"]["C_drain_IO_L2_out_single_latency"] = C_drain_IO_L2_out_single_latency
# 	latency_meta["latency_epilogue"]["C_drain_IO_L3_out_single_latency"] = C_drain_IO_L3_out_single_latency
# 	latency_meta["latency_main"]["A_IO_L2_in_latency"] = A_IO_L2_in_latency
# 	latency_meta["latency_main"]["A_IO_L3_in_latency"] = A_IO_L3_in_latency
# 	latency_meta["latency_main"]["B_IO_L2_in_latency"] = B_IO_L2_in_latency
# 	latency_meta["latency_main"]["B_IO_L3_in_latency"] = B_IO_L3_in_latency
# 	latency_meta["latency_main"]["C_drain_IO_L1_out_latency"] = C_drain_IO_L1_out_latency
# 	latency_meta["latency_main"]["C_drain_IO_L2_out_latency"] = C_drain_IO_L2_out_latency
# 	latency_meta["latency_main"]["C_drain_IO_L3_out_latency"] = C_drain_IO_L3_out_latency
# 	latency_meta["latency_main"]["PE_latency"] = PE_latency
# 	return latency, latency_meta

# params = {
#   'i': 1024,
#   'j': 1040,
#   'k': 1024,
#   'i_t1': 128,
#   'j_t1': 104,
#   'k_t1': 128,
#   'i_t2': 4,
#   'j_t2': 8,
#   'k_t2': 4,
#   'p9': 16,
#   'p10': 16,
#   'p11': 0,
#   'p12': 4
# }
# print(est_latency(params)[0])
# params = {
#   'i': 1024,
#   'j': 1024,
#   'k': 1024,
#   'i_t1': 256,
#   'j_t1': 256,
#   'k_t1': 256,
#   'i_t2': 4,
#   'j_t2': 32,
#   'k_t2': 4,
#   'p9': 16,
#   'p10': 16,
#   'p11': 0,
#   'p12': 4
# }
# print(est_latency(params)[0])

from math import ceil
import numpy as np
import random
import utils

def est_resource(params):
	i, j, k, i_t1, j_t1, k_t1, i_t2, j_t2, k_t2, p9, p10, p11, p12 = params["i"], params["j"], params["k"], params["i_t1"], params["j_t1"], params["k_t1"], params["i_t2"], params["j_t2"], params["k_t2"], params["p9"], params["p10"], params["p11"], params["p12"]

	# DSP
	DSP = ((i_t1/i_t2)*(j_t1/j_t2)) * k_t2 * 5

	# BRAM18K
	def est_BRAM18K(ele_size, ele_num, pack):
		return ceil(ele_size*8*pack / 36) * ceil(ele_num/pack/512)

	res_meta = {}
	A_IO_L2_in_unit_memory = est_BRAM18K(4, (i_t2*k_t1), p9)
	res_meta["A_IO_L2_in"] = {"ele_size": 4, "buf_size": (i_t2*k_t1), "data_pack_factor": 1, "num": (i_t1/i_t2)}
	res_meta["A_IO_L2_in"]["num"] *= 2
	B_IO_L2_in_unit_memory = est_BRAM18K(4, (j_t2*k_t1), p10)
	res_meta["B_IO_L2_in"] = {"ele_size": 4, "buf_size": (j_t2*k_t1), "data_pack_factor": 1, "num": (j_t1/j_t2)}
	res_meta["B_IO_L2_in"]["num"] *= 2
	C_drain_IO_L1_out_unit_memory = est_BRAM18K(4, (i_t2*j_t2), p12)
	res_meta["C_drain_IO_L1_out"] = {"ele_size": 4, "buf_size": (i_t2*j_t2), "data_pack_factor": 1, "num": ((j_t1/j_t2)*(i_t1/i_t2))}
	PE_unit_memory = est_BRAM18K(4, (i_t2*j_t2), 1)
	res_meta["PE"] = {"ele_size": 4, "buf_size": (i_t2*j_t2), "data_pack_factor": 1, "num": ((i_t1/i_t2)*(j_t1/j_t2))}
	BRAM18K = A_IO_L2_in_unit_memory * 2 * (i_t1/i_t2) + B_IO_L2_in_unit_memory * 2 * (j_t1/j_t2) + C_drain_IO_L1_out_unit_memory * 1 * ((j_t1/j_t2)*(i_t1/i_t2)) + PE_unit_memory * 1 * ((i_t1/i_t2)*(j_t1/j_t2))

	# URAM
	URAM = 0

	res = {"DSP": DSP, "BRAM18K": BRAM18K, "URAM": URAM}
	res['A_IO_L2_in_unit_memory'] = A_IO_L2_in_unit_memory
	res['B_IO_L2_in_unit_memory'] = B_IO_L2_in_unit_memory
	res['C_drain_IO_L1_out_unit_memory'] = C_drain_IO_L1_out_unit_memory
	res['PE_unit_memory'] = PE_unit_memory

	return res, res_meta

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

def est_latency_no_ceil(params):
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

	A_IO_L2_in_latency = ((i/i_t1)) * ((j/j_t1)) * ((k/k_t1)) * (max((i_t1/i_t2) * (i_t2*k_t1/p9), (k_t1/k_t2) * j_t2 * i_t2 * 1) + 1)
	A_IO_L3_in_latency = ((i/i_t1)) * ((j/j_t1)) * ((k/k_t1)) * (i_t1/i_t2) * (i_t2*k_t1/min(p9, 512/8/4))
	B_IO_L2_in_latency = ((i/i_t1)) * ((j/j_t1)) * ((k/k_t1)) * (max((j_t1/j_t2) * (j_t2*k_t1/p10), (k_t1/k_t2) * j_t2 * i_t2 * 1) + 1)
	B_IO_L3_in_latency = ((i/i_t1)) * ((j/j_t1)) * ((k/k_t1)) * (j_t1/j_t2) * (j_t2*k_t1/min(p10, 512/8/4))
	C_drain_IO_L1_out_latency = ((i/i_t1)) * ((j/j_t1)) * ((i_t1/i_t2) * (i_t2*j_t2/p12) + j_t2 * i_t2 * 1)
	C_drain_IO_L2_out_latency = ((i/i_t1)) * ((j/j_t1)) * (j_t1/j_t2) * (i_t1/i_t2) * (i_t2*j_t2/p12)
	C_drain_IO_L3_out_latency = ((i/i_t1)) * ((j/j_t1)) * (j_t1/j_t2) * (i_t1/i_t2) * (i_t2*j_t2/min(p12, 512/8/4))
	PE_latency = ((i/i_t1)) * ((j/j_t1)) * ((k/k_t1)) * (k_t1/k_t2) * j_t2 * i_t2 * 1
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
	latency_meta["prologue"] = latency_prologue
	latency_meta["main"] = latency_main
	latency_meta["epilogue"] = latency_epilogue
	latency_meta["bottleneck"] = 0
	if max([latency_prologue, latency_main, latency_epilogue]) == latency_prologue:
		latency_meta["bottleneck"] = 'prologue'
	elif max([latency_prologue, latency_main, latency_epilogue]) == latency_main:
		latency_meta["bottleneck"] = 'main'
	elif max([latency_prologue, latency_main, latency_epilogue]) == latency_epilogue:
		latency_meta["bottleneck"] = 'epilogue'
	return latency, latency_meta

def est_activity(params):
	i, j, k, i_t1, j_t1, k_t1, i_t2, j_t2, k_t2, p9, p10, p11, p12 = params["i"], params["j"], params["k"], params["i_t1"], params["j_t1"], params["k_t1"], params["i_t2"], params["j_t2"], params["k_t2"], params["p9"], params["p10"], params["p11"], params["p12"]

	activity = {}
	activity["off_chip_acc_num_meta"] = {}
	off_chip_acc_num = 0
	A_IO_L3_in_off_chip_acc_num = ceil((i/i_t1)) * ceil((j/j_t1)) * ceil((k/k_t1)) * (i_t1/i_t2) * (i_t2*k_t1)
	activity["off_chip_acc_num_meta"]["A_IO_L3_in"] = A_IO_L3_in_off_chip_acc_num
	off_chip_acc_num += A_IO_L3_in_off_chip_acc_num
	B_IO_L3_in_off_chip_acc_num = ceil((i/i_t1)) * ceil((j/j_t1)) * ceil((k/k_t1)) * (j_t1/j_t2) * (j_t2*k_t1)
	activity["off_chip_acc_num_meta"]["B_IO_L3_in"] = B_IO_L3_in_off_chip_acc_num
	off_chip_acc_num += B_IO_L3_in_off_chip_acc_num
	C_drain_IO_L3_out_off_chip_acc_num = ceil((i/i_t1)) * ceil((j/j_t1)) * (j_t1/j_t2) * (i_t1/i_t2) * (i_t2*j_t2)
	activity["off_chip_acc_num_meta"]["C_drain_IO_L3_out"] = C_drain_IO_L3_out_off_chip_acc_num
	off_chip_acc_num += C_drain_IO_L3_out_off_chip_acc_num
	activity["off_chip_acc_num"] = off_chip_acc_num

	noc_hop_num = 0
	A_IO_L2_in_io_noc_hop_num = (1 + (i_t1/i_t2)) / 2
	A_IO_L2_in_io_noc_hop_num *= ceil((i/i_t1)) * ceil((j/j_t1)) * ceil((k/k_t1)) * (((i_t1/i_t2) * (i_t2*k_t1)) + 0)
	noc_hop_num += A_IO_L2_in_io_noc_hop_num
	A_IO_L3_in_io_noc_hop_num = (1 + 1) / 2
	A_IO_L3_in_io_noc_hop_num *= ceil((i/i_t1)) * ceil((j/j_t1)) * ceil((k/k_t1)) * (i_t1/i_t2) * (i_t2*k_t1)
	noc_hop_num += A_IO_L3_in_io_noc_hop_num
	B_IO_L2_in_io_noc_hop_num = (1 + (j_t1/j_t2)) / 2
	B_IO_L2_in_io_noc_hop_num *= ceil((i/i_t1)) * ceil((j/j_t1)) * ceil((k/k_t1)) * (((j_t1/j_t2) * (j_t2*k_t1)) + 0)
	noc_hop_num += B_IO_L2_in_io_noc_hop_num
	B_IO_L3_in_io_noc_hop_num = (1 + 1) / 2
	B_IO_L3_in_io_noc_hop_num *= ceil((i/i_t1)) * ceil((j/j_t1)) * ceil((k/k_t1)) * (j_t1/j_t2) * (j_t2*k_t1)
	noc_hop_num += B_IO_L3_in_io_noc_hop_num
	C_drain_IO_L1_out_io_noc_hop_num = (1 + (i_t1/i_t2)) / 2
	C_drain_IO_L1_out_io_noc_hop_num *= ceil((i/i_t1)) * ceil((j/j_t1)) * ((i_t1/i_t2) * (i_t2*j_t2))
	C_drain_IO_L1_out_io_noc_hop_num *= (j_t1/j_t2)
	noc_hop_num += C_drain_IO_L1_out_io_noc_hop_num
	C_drain_IO_L2_out_io_noc_hop_num = (1 + (j_t1/j_t2)) / 2
	C_drain_IO_L2_out_io_noc_hop_num *= ceil((i/i_t1)) * ceil((j/j_t1)) * (j_t1/j_t2) * (i_t1/i_t2) * (i_t2*j_t2)
	noc_hop_num += C_drain_IO_L2_out_io_noc_hop_num
	C_drain_IO_L3_out_io_noc_hop_num = (1 + 1) / 2
	C_drain_IO_L3_out_io_noc_hop_num *= ceil((i/i_t1)) * ceil((j/j_t1)) * (j_t1/j_t2) * (i_t1/i_t2) * (i_t2*j_t2)
	noc_hop_num += C_drain_IO_L3_out_io_noc_hop_num
	A_IO_L2_in_pe_noc_hop_num = ((i_t1/i_t2)*(j_t1/j_t2))
	A_IO_L2_in_pe_noc_hop_num *= ceil((i/i_t1)) * ceil((j/j_t1)) * ceil((k/k_t1)) * (((k_t1/k_t2) * j_t2 * i_t2 * 1) + 0)
	A_IO_L2_in_pe_noc_hop_num *= k_t2
	noc_hop_num += A_IO_L2_in_pe_noc_hop_num
	B_IO_L2_in_pe_noc_hop_num = ((i_t1/i_t2)*(j_t1/j_t2))
	B_IO_L2_in_pe_noc_hop_num *= ceil((i/i_t1)) * ceil((j/j_t1)) * ceil((k/k_t1)) * (((k_t1/k_t2) * j_t2 * i_t2 * 1) + 0)
	B_IO_L2_in_pe_noc_hop_num *= k_t2
	noc_hop_num += B_IO_L2_in_pe_noc_hop_num
	C_drain_IO_L1_out_pe_noc_hop_num = ((i_t1/i_t2)*(j_t1/j_t2))
	C_drain_IO_L1_out_pe_noc_hop_num *= ceil((i/i_t1)) * ceil((j/j_t1)) * (j_t2 * i_t2 * 1)
	C_drain_IO_L1_out_pe_noc_hop_num *= 1
	noc_hop_num += C_drain_IO_L1_out_pe_noc_hop_num
	activity["noc_hop_num"] = noc_hop_num

	compute_stmt_call_num = 0
	compute_stmt_call_num = k_t2
	compute_stmt_call_num *= ceil((i/i_t1)) * ceil((j/j_t1)) * ceil((k/k_t1)) * (k_t1/k_t2) * j_t2 * i_t2 * 1
	compute_stmt_call_num *= ((i_t1/i_t2)*(j_t1/j_t2))
	activity["compute_stmt_call_num"] = compute_stmt_call_num

	io_module_mem_acc_num = 0
	A_IO_L2_in_mem_acc_num = ceil((i/i_t1)) * ceil((j/j_t1)) * ceil((k/k_t1)) * (((i_t1/i_t2) * (i_t2*k_t1/p9) + (k_t1/k_t2) * j_t2 * i_t2 * 1) + 0)
	A_IO_L2_in_mem_acc_num *= p9
	io_module_mem_acc_num += A_IO_L2_in_mem_acc_num
	B_IO_L2_in_mem_acc_num = ceil((i/i_t1)) * ceil((j/j_t1)) * ceil((k/k_t1)) * (((j_t1/j_t2) * (j_t2*k_t1/p10) + (k_t1/k_t2) * j_t2 * i_t2 * 1) + 0)
	B_IO_L2_in_mem_acc_num *= p10
	io_module_mem_acc_num += B_IO_L2_in_mem_acc_num
	C_drain_IO_L1_out_mem_acc_num = ceil((i/i_t1)) * ceil((j/j_t1)) * ((i_t1/i_t2) * (i_t2*j_t2/p12) + j_t2 * i_t2 * 1)
	C_drain_IO_L1_out_mem_acc_num *= p12
	io_module_mem_acc_num += C_drain_IO_L1_out_mem_acc_num
	activity["io_module_mem_acc_num"] = io_module_mem_acc_num

	pe_module_reg_acc_num = 0
	pe_module_mem_acc_num = 0
	pe_module_reg_acc_num = 2
	pe_module_mem_acc_num = 2
	pe_module_reg_acc_num *= k_t2
	pe_module_reg_acc_num *= ceil((i/i_t1)) * ceil((j/j_t1)) * ceil((k/k_t1)) * (k_t1/k_t2) * j_t2 * i_t2 * 1
	pe_module_reg_acc_num *= ((i_t1/i_t2)*(j_t1/j_t2))
	pe_module_mem_acc_num *= k_t2
	pe_module_mem_acc_num *= ceil((i/i_t1)) * ceil((j/j_t1)) * ceil((k/k_t1)) * (k_t1/k_t2) * j_t2 * i_t2 * 1
	pe_module_mem_acc_num *= ((i_t1/i_t2)*(j_t1/j_t2))
	activity["pe_module_reg_acc_num"] = pe_module_reg_acc_num
	activity["pe_module_mem_acc_num"] = pe_module_mem_acc_num

	return activity

def infer_params(params):
	i, j, k, i_t1, j_t1, k_t1, i_t2, j_t2, k_t2 = params["i"], params["j"], params["k"], params["i_t1"], params["j_t1"], params["k_t1"], params["i_t2"], params["j_t2"], params["k_t2"]

	p9_choices = [n*k_t2 for n in range(1, max(min(k_t1,16),k_t2)//k_t2+1) if max(min(k_t1,16),k_t2)%(n*k_t2)==0]
	if len(p9_choices) == 0:
		return None
	params["p9"] = max(p9_choices)
	p10_choices = [n*k_t2 for n in range(1, max(min(k_t1,16),k_t2)//k_t2+1) if max(min(k_t1,16),k_t2)%(n*k_t2)==0]
	if len(p10_choices) == 0:
		return None
	params["p10"] = max(p10_choices)
	p11_choices = [n*1 for n in range(1, max(min(j_t2,4),1)//1+1) if max(min(j_t2,4),1)%(n*1)==0]
	if len(p11_choices) == 0:
		return None
	params["p11"] = max(p11_choices)
	p12_choices = [n*1 for n in range(1, max(min(j_t2,4),1)//1+1) if max(min(j_t2,4),1)%(n*1)==0]
	if len(p12_choices) == 0:
		return None
	params["p12"] = max(p12_choices)

	return params

def random_sampling(params):
	def filter_non_power_of_two(x):
		if np.log2(x) != int(np.log2(x)):
			return True
		return False

	i = params["i"]
	j = params["j"]
	k = params["k"]
	while True:
		sample = random.randint(int(1), int(i))
		i_t1 = sample
		params["i_t1"] = sample
		sample = random.randint(int(1), int(k))
		k_t1 = sample
		params["k_t1"] = sample
		sample = random.randint(int(1), int(j))
		j_t1 = sample
		params["j_t1"] = sample
		sample = random.sample(utils.get_divisors(int(i_t1), None), 1)[-1]
		i_t2 = sample
		params["i_t2"] = sample
		sample = random.sample(utils.get_divisors(int(min(k_t1,8)), filter_non_power_of_two), 1)[-1]
		k_t2 = sample
		params["k_t2"] = sample
		sample = random.sample(utils.get_divisors(int(j_t1), None), 1)[-1]
		j_t2 = sample
		params["j_t2"] = sample
		latency_factors = 1
		latency_factors *= i_t2
		latency_factors *= j_t2
		simd_factor = k_t2
		if latency_factors >= 8 * simd_factor:
			break

	return params

def bound_check(params):
	def filter_non_power_of_two(x):
		if np.log2(x) != int(np.log2(x)):
			return True
		return False

	i, j, k, i_t1, j_t1, k_t1, i_t2, j_t2, k_t2, p9, p10, p11, p12 = params["i"], params["j"], params["k"], params["i_t1"], params["j_t1"], params["k_t1"], params["i_t2"], params["j_t2"], params["k_t2"], params["p9"], params["p10"], params["p11"], params["p12"]

	if i_t1 < 1:
		return False
	if j_t1 < 1:
		return False
	if k_t1 < 1:
		return False
	if i_t2 < 1:
		return False
	if i_t2 > i_t1:
		return False
	if j_t2 < 1:
		return False
	if j_t2 > j_t1:
		return False
	if k_t2 < 1:
		return False
	if k_t2 > min(k_t1,8):
		return False
	if filter_non_power_of_two(k_t2):
		return False
	if p9 < k_t2:
		return False
	if p9 > max(min(k_t1,16),k_t2):
		return False
	if filter_non_power_of_two(p9):
		return False
	if p10 < k_t2:
		return False
	if p10 > max(min(k_t1,16),k_t2):
		return False
	if filter_non_power_of_two(p10):
		return False
	if p11 < 1:
		return False
	if p11 > max(min(j_t2,4),1):
		return False
	if filter_non_power_of_two(p11):
		return False
	if p12 < 1:
		return False
	if p12 > max(min(j_t2,4),1):
		return False
	if filter_non_power_of_two(p12):
		return False
	latency_factors = 1
	latency_factors *= i_t2
	latency_factors *= j_t2
	simd_factor = k_t2
	if latency_factors < 8 * simd_factor:
		return False
	return True

def compute_arch_cst(params):
	i, j, k, i_t1, j_t1, k_t1, i_t2, j_t2, k_t2, p9, p10, p11, p12 = params["i"], params["j"], params["k"], params["i_t1"], params["j_t1"], params["k_t1"], params["i_t2"], params["j_t2"], params["k_t2"], params["p9"], params["p10"], params["p11"], params["p12"]

	arch_features = {}
	arch_features['dims'] = []
	arch_features["dims"].append((i_t1/i_t2))
	if arch_features["dims"][-1] == 0:
		return None
	arch_features["dims"].append((j_t1/j_t2))
	if arch_features["dims"][-1] == 0:
		return None
	arch_features["SIMD"] = k_t2
	arch_features["data_pack"] = {}

	return arch_features

def list_split(ori_list, split_num):
	chunk_size = int(np.ceil(float(len(ori_list)) / split_num))
	chunks = [ori_list[i: i + min(chunk_size, len(ori_list) - i)] for i in range(0, len(ori_list), chunk_size)]
	return chunks


def theoretical_bound(i_t0, j_t0, k_t0, resource_limits):
	return i_t0*j_t0*k_t0/(resource_limits['DSP']/5)

# def new_bound(i_t0, j_t0, k_t0, resource_limits):
# 	results = []
# 	k_t1_candidates = [x for x in range(1, k_t0 + 1) if k_t0 % x == 0]
# 	k_t2_candidates = [1, 2, 4, 8]
# 	for i in range(i_t0):
# 		for j in range(j_t0):
# 			for k_t1 in k_t1_candidates:
# 				for k_t2 in k_t2_candidates:
# 					params = {}
# 					params["i"] = i_t0
# 					params["j"] = j_t0
# 					params["k"] = k_t0
# 					params["i_t1"] = i_t0 - i
# 					params["j_t1"] = j_t0 - j
# 					params["k_t1"] = k_t1
# 					params["i_t2"] = 1 + i
# 					params["j_t2"] = 1 + j
# 					params["k_t2"] = k_t2
# 					params = infer_params(params)
# 					if params == None or params["i_t1"]/params["i_t2"] != 0 or params["j_t1"]/params["j_t2"] != 0:
# 						continue
# 					if not bound_check(params):
# 						continue
# 					resources = est_resource(params)[0]
# 					DSPs = resources["DSP"]
# 					BRAMs = resources["BRAM18K"]
# 					if DSPs <= resource_limits['DSP'] and BRAMs <= resource_limits['BRAM18K']:
# 						PE_latency = ceil((params['i']/params['i_t1'])) * ceil((params['j']/params['j_t1'])) * ceil((params['k']/params['k_t1'])) * (params['k_t1']/params['k_t2']) * params['j_t2'] * params['i_t2'] 
# 						results.append((PE_latency, params))
# 	# sort by PE latency
# 	results.sort(key=lambda x: x[0])
# 	return results[0]

def search_mm(i_t0, j_t0, k_t0, candidates, resource_limits):
	num_top_results = 10
	top_results = [{'cycles':np.inf, 'params':None}]*num_top_results
	# for idx in tqdm(range(len(candidates))):
	for idx in range(len(candidates)):
		i_t1, j_t1, k_t1 = candidates[idx]
		i_t2_candidates = [i for i in range(1, i_t1+1) if i_t1 % i == 0]
		j_t2_candidates = [j for j in range(1, j_t1+1) if j_t1 % j == 0]
		k_t2_candidates = [k for k in range(1, k_t1+1) if k_t1 % k == 0]
		for i_t2 in i_t2_candidates:
			for j_t2 in j_t2_candidates:
				for k_t2 in k_t2_candidates:
					params = {}
					params["i"] = i_t0
					params["j"] = j_t0
					params["k"] = k_t0
					params["i_t1"] = i_t1
					params["j_t1"] = j_t1
					params["k_t1"] = k_t1
					params["i_t2"] = i_t2
					params["j_t2"] = j_t2
					params["k_t2"] = k_t2
					# 'p9': 16, 'p10': 16, 'p11': 4, 'p12': 4
					# params['p9'] = 16
					# params['p10'] = 16
					# params['p11'] = 4
					# params['p12'] = 4
					params = infer_params(params)
					if not bound_check(params):
						continue
					result = {}
					result['resources'] = est_resource(params)
					if result['resources'][0]['DSP'] > resource_limits['DSP'] or result['resources'][0]['BRAM18K'] > resource_limits['BRAM18K']:
						continue
					result['cycles'] = est_latency(params)
					if result['cycles'][0] < top_results[-1]['cycles']:
						for j in range(num_top_results):
							if result['cycles'][0] < top_results[j]['cycles']:
								# insert result into results
								top_results.insert(j, {'cycles':result['cycles'][0], 'params':params})
								# remove last element
								top_results.pop()
								break
						
	return top_results

def actual_bound(i_t0, j_t0, k_t0, resource_limits):
	candidates = []
	i_t1_candidates = [i for i in range(1, i_t0+1) if i_t0 % i == 0]
	j_t1_candidates = [j for j in range(1, j_t0+1) if j_t0 % j == 0]
	k_t1_candidates = [k for k in range(1, k_t0+1) if k_t0 % k == 0]
	for i_t1 in i_t1_candidates:
		for j_t1 in j_t1_candidates:
			for k_t1 in k_t1_candidates:
				candidates.append((i_t1, j_t1, k_t1))
	# shuffle candidates
	random.shuffle(candidates)
	# print('Generated %d candidates' % len(candidates))
	num_processes = int(multiprocessing.cpu_count() * 1)
	# print('Parallelizing using %d processes...' % (num_processes))
	chunks = list_split(candidates, num_processes)
	pool = multiprocessing.Pool(processes = num_processes)
	results = pool.starmap(search_mm, [(i_t0, j_t0, k_t0, chunk, resource_limits) for chunk in chunks])
	pool.close()
	# flatten results
	results = [item for sublist in results for item in sublist]
	# sort by cycles
	results.sort(key=lambda x: x['cycles'])
	same_results = []
	min_cycles = results[0]['cycles']
	for result in results:
		if result['cycles'] == min_cycles:
			same_results.append(result)
		else:
			break
	return same_results

def search_mm_nd(i_t0, j_t0, k_t0, candidates, resource_limits):
	num_top_results = 10
	top_results = [{'cycles':np.inf, 'params':None}]*num_top_results
	# for idx in tqdm(range(len(candidates))):
	for idx in range(len(candidates)):
		i_t1, j_t1, k_t1 = candidates[idx]
		i_t2_candidates = [i for i in range(1, i_t1+1)]
		j_t2_candidates = [j for j in range(1, j_t1+1)]
		k_t2_candidates = [k for k in range(1, k_t1+1)]
		for i_t2 in i_t2_candidates:
			for j_t2 in j_t2_candidates:
				for k_t2 in k_t2_candidates:
					params = {}
					params["i"] = i_t0
					params["j"] = j_t0
					params["k"] = k_t0
					params["i_t1"] = i_t1
					params["j_t1"] = j_t1
					params["k_t1"] = k_t1
					params["i_t2"] = i_t2
					params["j_t2"] = j_t2
					params["k_t2"] = k_t2
					# 'p9': 16, 'p10': 16, 'p11': 4, 'p12': 4
					# params['p9'] = 16
					# params['p10'] = 16
					# params['p11'] = 4
					# params['p12'] = 4
					params = infer_params(params)
					if params == None:
						continue
					if not bound_check(params):
						continue
					result = {}
					result['resources'] = est_resource(params)
					if result['resources'][0]['DSP'] > resource_limits['DSP'] or result['resources'][0]['BRAM18K'] > resource_limits['BRAM18K']:
						continue
					result['cycles'] = est_latency_no_ceil(params)
					if result['cycles'][0] < top_results[-1]['cycles']:
						for j in range(num_top_results):
							if result['cycles'][0] < top_results[j]['cycles']:
								# insert result into results
								top_results.insert(j, {'cycles':result['cycles'][0], 'params':params, 'resources':result['resources']})
								# remove last element
								top_results.pop()
								break
						
	return top_results

def actual_bound_nd(i_t0, j_t0, k_t0, resource_limits):
	candidates = []
	i_t1_candidates = [i for i in range(1, i_t0+1)]
	j_t1_candidates = [j for j in range(1, j_t0+1)]
	k_t1_candidates = [k for k in range(1, k_t0+1)]
	for i_t1 in i_t1_candidates:
		for j_t1 in j_t1_candidates:
			for k_t1 in k_t1_candidates:
				candidates.append((i_t1, j_t1, k_t1))
	# shuffle candidates
	random.shuffle(candidates)
	# print('Generated %d candidates' % len(candidates))
	num_processes = int(multiprocessing.cpu_count() * 1)
	# print('Parallelizing using %d processes...' % (num_processes))
	chunks = list_split(candidates, num_processes)
	pool = multiprocessing.Pool(processes = num_processes)
	results = pool.starmap(search_mm_nd, [(i_t0, j_t0, k_t0, chunk, resource_limits) for chunk in chunks])
	pool.close()
	# flatten results
	results = [item for sublist in results for item in sublist]
	# sort by cycles
	results.sort(key=lambda x: x['cycles'])
	same_results = []
	min_cycles = results[0]['cycles']
	for result in results:
		if result['cycles'] == min_cycles:
			same_results.append(result)
		else:
			break
	return same_results

def get_lower_bound_search(i_t0, j_t0, k_t0, candidates, resource_limits):
	min_cycles = np.inf
	for i_t1, j_t1, k_t1 in candidates:
		params = {'i': i_t0, 'j': j_t0, 'k': k_t0, 'i_t1': i_t1, 'j_t1': j_t1, 'k_t1': k_t1, 'i_t2': 1, 'j_t2': 8, 'k_t2': 1}#, 'p9': 16, 'p10': 16, 'p11': 4, 'p12': 4
		params = infer_params(params)
		cycles_nd = est_latency_no_ceil(params)[0]
		if not bound_check(params):
			continue
		result['resources'] = est_resource(params)
		if result['resources'][0]['DSP'] > resource_limits['DSP'] or result['resources'][0]['BRAM18K'] > resource_limits['BRAM18K']:
			continue
		if cycles_nd < min_cycles:
			min_cycles = cycles_nd
	return min_cycles

def get_lower_bound(i_t0, j_t0, k_t0, resource_limits):
	candidates = []
	k_t1_candidates = [8, 16, 32]
	for i_t1 in range(1, i_t0 + 1):
		for j_t1 in range(1, j_t0 + 1):
			for k_t1 in k_t1_candidates:
				candidates.append((i_t1, j_t1, k_t1))
	# shuffle candidates
	random.shuffle(candidates)
	num_processes = int(multiprocessing.cpu_count() * 1)
	# print('Parallelizing using %d processes...' % (num_processes))
	chunks = list_split(candidates, num_processes)
	pool = multiprocessing.Pool(processes = num_processes)
	results = pool.starmap(get_lower_bound_search, [(i_t0, j_t0, k_t0, chunk, resource_limits) for chunk in chunks])
	pool.close()
	# sort results
	results.sort()
	return results[0]



def solver_lower_bound(i_t0, j_t0, k_t0):
	with open('solver/tmp.dat', 'w') as f:
		print(f'param i := {i_t0};', file = f)
		print(f'param j := {j_t0};', file = f)
		print(f'param k := {k_t0};', file = f)
		print(f'param dsp_bound := 8601;', file = f)
		print(f'param bram_bound := 3763;', file = f)
		print(f'param data_w := 32;', file = f)
	cmd = 'cd solver; ampl tmp.run | grep target'
	# run the command and get the output
	output = subprocess.check_output(cmd, shell=True)
	# convert the output to a string
	output = output.decode('utf-8')
	# target = #, get the number
	target = float(output.split()[2])
	return target

import os
import sys
import json
import time
from tqdm import tqdm
import multiprocessing
import subprocess
# from utils import print_latency_est_func
# design_path = '/home/suhailb/Projects/odyssey/tests/tmp/designs/kernel3_2.json'
# with open(design_path, 'r') as f:
# 	design = json.load(f)
# out_file = open('/home/suhailb/Projects/odyssey/tests/solver/test.py', 'w')
# print_latency_est_func(out_file, design)
# exit()

prj_path = os.environ["PRJ_PATH"]
u250_info = json.load(open(prj_path + '/data/cst/u250.json'))
resource_limits = {'DSP': u250_info['DSP']['total']*u250_info['DSP']['ratio'], 'BRAM18K': u250_info['BRAM18K']['total']*u250_info['BRAM18K']['ratio']}

theoretical_latencies = []
actual_latencies = []
actual_nd_latencies = []
solver_latencies = []

i_padding = 0
j_padding = 100
# print(f'i, j, k, cycles, i_t1, j_t1, k_t1, i_t2, j_t2, k_t2, p9, p10, p11, p12, DSP, BRAM18K, PE, A_L2, A_L3, B_L2, B_L3, C_L1, C_L2, C_L3, main bottleneck, epilogue, main, prologue, overall bottleneck')
i_t0, j_t0, k_t0 = 1024, 1024, 1024

for i in range(i_t0, i_t0 + 1 + i_padding):
	for j in range(j_t0, j_t0 + 1 + j_padding):
		theoretical_latency = theoretical_bound(i, j, k_t0, resource_limits)
		theoretical_latencies.append(theoretical_latency)
		results = actual_bound(i, j, k_t0, resource_limits)
		actual_latency = results[0]['cycles']
		actual_latencies.append(actual_latency)
		# cycles_nd = get_lower_bound(i, j, k_t0, resource_limits)
		# actual_nd_latencies.append(cycles_nd)
		solver_latency = 0#solver_lower_bound(i, j, k_t0)
		solver_latencies.append(solver_latency)
		
		print(f'{i}, {j}, {k_t0}, {theoretical_latency}, {solver_latency}, {actual_latency}')


import matplotlib.pyplot as plt
plt.plot(range(j_t0, j_t0 + 1 + j_padding), theoretical_latencies, label='theoretical')
plt.plot(range(j_t0, j_t0 + 1 + j_padding), actual_latencies, label='actual')
# plt.plot(range(j_t0, j_t0 + 1 + j_padding), solver_latencies, label='solver')
# x axis
plt.xlabel('j')
# y axis
plt.ylabel('cycles')
plt.legend()

plt.savefig('mm1024.png')
exit()



# def search(i_t0, j_t0, k_t0, candidates, resource_limits):
# 	param_candidates = []
# 	for i, j, k in tqdm(candidates):
# 		k_1_candidates = [x for x in range(1, k_t0+1) if k_t0%x == 0]
# 		for i_t1 in range(1, i_t0 + 1):
# 			for j_t1 in range(1, j_t0 + 1):
# 				for k_t1 in k_1_candidates:
# 					i_t2_candidates = [x for x in range(1, i_t1+1) if i_t1 % x == 0]
# 					j_t2_candidates = [x for x in range(1, j_t1+1) if j_t1 % x == 0]
# 					for i_t2 in i_t2_candidates:
# 						for j_t2 in j_t2_candidates:
# 							params = {}
# 							params["i"] = ceil(i_t0 / i_t1) * i_t1
# 							params["j"] = ceil(j_t0 / j_t1) * j_t1
# 							params["k"] = ceil(k_t0 / k_t1) * k_t1
# 							params["i_t1"] = i_t1
# 							params["j_t1"] = j_t1
# 							params["k_t1"] = k_t1
# 							params["i_t2"] = i_t2
# 							params["j_t2"] = j_t2
# 							params["k_t2"] = k
# 							if i_t1/i_t2 != i or j_t1/j_t2 != j or i_t1%i_t2 != 0 or j_t1%j_t2 != 0:
# 								continue
# 							params = infer_params(params)
# 							if params == None:
# 								continue
# 							BRAMs = est_resource(params)[0]['BRAM18K']
# 							if not bound_check(params) or BRAMs > resource_limits['BRAM18K']:
# 								continue
# 							param_candidates.append((i_t1, j_t1, k_t1, i_t2, j_t2, k))
# 	return param_candidates

# i_t0, j_t0, k_t0 = 64, 64, 64
# i_candidates = [x for x in range(1, i_t0+1)]
# j_candidates = [x for x in range(1, j_t0+1)]
# k_candidates = [1, 2, 4, 8]
# candidates = []
# for i in i_candidates:
# 	for j in j_candidates:
# 		for k in k_candidates:
# 			# print(i, j, k)
# 			if i*j*k <= (resource_limits['DSP']/5):
# 				candidates.append((i, j, k))
# num_processes = 72
# chunks = list_split(candidates, num_processes)
# pool = multiprocessing.Pool(processes = num_processes)
# param_candidates = pool.starmap(search, [(i_t0, j_t0, k_t0, chunk, resource_limits) for chunk in chunks])
# pool.close()
# param_candidates = [item for sublist in param_candidates for item in sublist]
# print(len(param_candidates))