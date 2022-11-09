from math import ceil
import numpy as np
import random
import sys
import os
prj_path = os.environ['PRJ_PATH']
sys.path.insert(0, prj_path + '/src')
import utils
def est_resource(params):
	q, p, o, r, c, i, o_t1, r_t1, c_t1, i_t1, o_t2, r_t2, c_t2, i_t2, p14, p15, p16, p17 = params["q"], params["p"], params["o"], params["r"], params["c"], params["i"], params["o_t1"], params["r_t1"], params["c_t1"], params["i_t1"], params["o_t2"], params["r_t2"], params["c_t2"], params["i_t2"], params["p14"], params["p15"], params["p16"], params["p17"]

	# DSP
	DSP = ((o_t1/o_t2)*(r_t1/r_t2)) * i_t2 * 5

	# BRAM18K
	def est_BRAM18K(ele_size, ele_num, pack):
		return ceil(ele_size*8*pack / 36) * ceil(ele_num/pack/512)

	res_meta = {}
	PE_unit_memory = est_BRAM18K(4, ((r_t2*c_t1)*o_t2), 1)
	res_meta["PE"] = {"ele_size": 4, "buf_size": ((r_t2*c_t1)*o_t2), "data_pack_factor": 1, "num": ((o_t1/o_t2)*(r_t1/r_t2))}
	cin_IO_L2_in_unit_memory = est_BRAM18K(4, (((((r_t2-1)+(p-1))+1)*((((((c_t1/c_t2)-1)*c_t2)+(c_t2-1))+(q-1))+1))*i_t1), p14)
	res_meta["cin_IO_L2_in"] = {"ele_size": 4, "buf_size": (((((r_t2-1)+(p-1))+1)*((((((c_t1/c_t2)-1)*c_t2)+(c_t2-1))+(q-1))+1))*i_t1), "data_pack_factor": 1, "num": (r_t1/r_t2)}
	res_meta["cin_IO_L2_in"]["num"] *= 2
	cout_IO_L1_in_unit_memory = est_BRAM18K(4, ((r_t2*c_t1)*o_t2), p15)
	res_meta["cout_IO_L1_in"] = {"ele_size": 4, "buf_size": ((r_t2*c_t1)*o_t2), "data_pack_factor": 1, "num": ((r_t1/r_t2)*(o_t1/o_t2))}
	res_meta["cout_IO_L1_in"]["num"] *= 2
	cout_IO_L1_out_unit_memory = est_BRAM18K(4, ((r_t2*c_t1)*o_t2), p15)
	res_meta["cout_IO_L1_out"] = {"ele_size": 4, "buf_size": ((r_t2*c_t1)*o_t2), "data_pack_factor": 1, "num": ((r_t1/r_t2)*(o_t1/o_t2))}
	res_meta["cout_IO_L1_out"]["num"] *= 2
	w_IO_L2_in_unit_memory = est_BRAM18K(4, (((o_t2*((p-1)+1))*((q-1)+1))*i_t1), p17)
	res_meta["w_IO_L2_in"] = {"ele_size": 4, "buf_size": (((o_t2*((p-1)+1))*((q-1)+1))*i_t1), "data_pack_factor": 1, "num": (o_t1/o_t2)}
	res_meta["w_IO_L2_in"]["num"] *= 2
	BRAM18K = PE_unit_memory * 1 * ((o_t1/o_t2)*(r_t1/r_t2)) + cin_IO_L2_in_unit_memory * 2 * (r_t1/r_t2) + cout_IO_L1_in_unit_memory * 2 * ((r_t1/r_t2)*(o_t1/o_t2)) + cout_IO_L1_out_unit_memory * 2 * ((r_t1/r_t2)*(o_t1/o_t2)) + w_IO_L2_in_unit_memory * 2 * (o_t1/o_t2)

	# URAM
	URAM = 0

	res = {"DSP": DSP, "BRAM18K": BRAM18K, "URAM": URAM}
	res['PE_unit_memory'] = PE_unit_memory
	res['cin_IO_L2_in_unit_memory'] = cin_IO_L2_in_unit_memory
	res['cout_IO_L1_in_unit_memory'] = cout_IO_L1_in_unit_memory
	res['cout_IO_L1_out_unit_memory'] = cout_IO_L1_out_unit_memory
	res['w_IO_L2_in_unit_memory'] = w_IO_L2_in_unit_memory

	return res, res_meta

def est_latency(params):
	q, p, o, r, c, i, o_t1, r_t1, c_t1, i_t1, o_t2, r_t2, c_t2, i_t2, p14, p15, p16, p17 = params["q"], params["p"], params["o"], params["r"], params["c"], params["i"], params["o_t1"], params["r_t1"], params["c_t1"], params["i_t1"], params["o_t2"], params["r_t2"], params["c_t2"], params["i_t2"], params["p14"], params["p15"], params["p16"], params["p17"]

	cin_IO_L2_in_single_latency = ((r_t1/r_t2) * ((((r_t2-1)+(p-1))+1)*((((((c_t1/c_t2)-1)*c_t2)+(c_t2-1))+(q-1))+1)*i_t1/p14) + 1)
	cin_IO_L3_in_single_latency = (r_t1/r_t2) * ((((r_t2-1)+(p-1))+1)*((((((c_t1/c_t2)-1)*c_t2)+(c_t2-1))+(q-1))+1)*i_t1/i_t1*(20+i_t1/(512/8/4)))
	cout_IO_L1_in_single_latency = ((o_t1/o_t2) * (r_t2*c_t1*o_t2/p15) + 1)
	cout_IO_L2_in_single_latency = (r_t1/r_t2) * (o_t1/o_t2) * (r_t2*c_t1*o_t2/p15)
	cout_IO_L3_in_single_latency = (r_t1/r_t2) * (o_t1/o_t2) * (r_t2*c_t1*o_t2/o_t2*(20+o_t2/(512/8/4)))
	w_IO_L2_in_single_latency = ((o_t1/o_t2) * (o_t2*((p-1)+1)*((q-1)+1)*i_t1/p17) + 1)
	w_IO_L3_in_single_latency = (o_t1/o_t2) * (o_t2*((p-1)+1)*((q-1)+1)*i_t1/i_t1*(20+i_t1/(512/8/4)))
	latency_prologue = max(cin_IO_L2_in_single_latency, cin_IO_L3_in_single_latency, cout_IO_L1_in_single_latency, cout_IO_L2_in_single_latency, cout_IO_L3_in_single_latency, w_IO_L2_in_single_latency, w_IO_L3_in_single_latency)

	cout_IO_L1_out_single_latency = ((o_t1/o_t2) * (r_t2*c_t1*o_t2/p15) + 1)
	cout_IO_L2_out_single_latency = (r_t1/r_t2) * (o_t1/o_t2) * (r_t2*c_t1*o_t2/p15)
	cout_IO_L3_out_single_latency = (r_t1/r_t2) * (o_t1/o_t2) * (r_t2*c_t1*o_t2/o_t2*(20+o_t2/(512/8/4)))
	latency_epilogue = max(cout_IO_L1_out_single_latency, cout_IO_L2_out_single_latency, cout_IO_L3_out_single_latency)

	PE_latency = ceil((o/o_t1)) * ceil((i/i_t1)) * ceil((r/r_t1)) * ceil((c/c_t1)) * (1 + (c_t1/c_t2) * (i_t1/i_t2) * p * q * c_t2 * r_t2 * o_t2 * 1 + 1)
	cin_IO_L2_in_latency = ceil((o/o_t1)) * ceil((i/i_t1)) * ceil((r/r_t1)) * ceil((c/c_t1)) * (max((r_t1/r_t2) * ((((r_t2-1)+(p-1))+1)*((((((c_t1/c_t2)-1)*c_t2)+(c_t2-1))+(q-1))+1)*i_t1/p14), (c_t1/c_t2) * (i_t1/i_t2) * p * q * c_t2 * r_t2 * o_t2 * 1) + 1)
	cin_IO_L3_in_latency = ceil((o/o_t1)) * ceil((i/i_t1)) * ceil((r/r_t1)) * ceil((c/c_t1)) * (r_t1/r_t2) * ((((r_t2-1)+(p-1))+1)*((((((c_t1/c_t2)-1)*c_t2)+(c_t2-1))+(q-1))+1)*i_t1/i_t1*(20+i_t1/(512/8/4)))
	cout_IO_L1_in_latency = ceil((o/o_t1)) * ceil((r/r_t1)) * ceil((c/c_t1)) * (max((o_t1/o_t2) * (r_t2*c_t1*o_t2/p15), (c_t1/c_t2) * c_t2 * r_t2 * o_t2 * 1) + 1)
	cout_IO_L1_out_latency = ceil((o/o_t1)) * ceil((r/r_t1)) * ceil((c/c_t1)) * (max((o_t1/o_t2) * (r_t2*c_t1*o_t2/p15), (c_t1/c_t2) * c_t2 * r_t2 * o_t2 * 1) + 1)
	cout_IO_L2_in_latency = ceil((o/o_t1)) * ceil((r/r_t1)) * ceil((c/c_t1)) * (r_t1/r_t2) * (o_t1/o_t2) * (r_t2*c_t1*o_t2/p15)
	cout_IO_L2_out_latency = ceil((o/o_t1)) * ceil((r/r_t1)) * ceil((c/c_t1)) * (r_t1/r_t2) * (o_t1/o_t2) * (r_t2*c_t1*o_t2/p15)
	cout_IO_L3_in_latency = ceil((o/o_t1)) * ceil((r/r_t1)) * ceil((c/c_t1)) * (r_t1/r_t2) * (o_t1/o_t2) * (r_t2*c_t1*o_t2/o_t2*(20+o_t2/(512/8/4)))
	cout_IO_L3_out_latency = ceil((o/o_t1)) * ceil((r/r_t1)) * ceil((c/c_t1)) * (r_t1/r_t2) * (o_t1/o_t2) * (r_t2*c_t1*o_t2/o_t2*(20+o_t2/(512/8/4)))
	w_IO_L2_in_latency = ceil((o/o_t1)) * ceil((i/i_t1)) * (max((o_t1/o_t2) * (o_t2*((p-1)+1)*((q-1)+1)*i_t1/p17), ceil((r/r_t1)) * ceil((c/c_t1)) * (c_t1/c_t2) * (i_t1/i_t2) * p * q * c_t2 * r_t2 * o_t2 * 1) + 1)
	w_IO_L3_in_latency = ceil((o/o_t1)) * ceil((i/i_t1)) * (o_t1/o_t2) * (o_t2*((p-1)+1)*((q-1)+1)*i_t1/i_t1*(20+i_t1/(512/8/4)))
	latency_main = max(PE_latency, cin_IO_L2_in_latency, cin_IO_L3_in_latency, cout_IO_L1_in_latency, cout_IO_L1_out_latency, cout_IO_L2_in_latency, cout_IO_L2_out_latency, cout_IO_L3_in_latency, cout_IO_L3_out_latency, w_IO_L2_in_latency, w_IO_L3_in_latency)

	latency = latency_prologue + latency_main + latency_epilogue

	# Meta information, used for conv fusion only
	latency_meta = {"latency_prologue": {}, "latency_main": {}, "latency_epilogue": {}}
	latency_meta["latency_prologue"]["cin_IO_L2_in_single_latency"] = cin_IO_L2_in_single_latency
	latency_meta["latency_prologue"]["cin_IO_L3_in_single_latency"] = cin_IO_L3_in_single_latency
	latency_meta["latency_prologue"]["cout_IO_L1_in_single_latency"] = cout_IO_L1_in_single_latency
	latency_meta["latency_prologue"]["cout_IO_L2_in_single_latency"] = cout_IO_L2_in_single_latency
	latency_meta["latency_prologue"]["cout_IO_L3_in_single_latency"] = cout_IO_L3_in_single_latency
	latency_meta["latency_prologue"]["w_IO_L2_in_single_latency"] = w_IO_L2_in_single_latency
	latency_meta["latency_prologue"]["w_IO_L3_in_single_latency"] = w_IO_L3_in_single_latency
	latency_meta["latency_epilogue"]["cout_IO_L1_out_single_latency"] = cout_IO_L1_out_single_latency
	latency_meta["latency_epilogue"]["cout_IO_L2_out_single_latency"] = cout_IO_L2_out_single_latency
	latency_meta["latency_epilogue"]["cout_IO_L3_out_single_latency"] = cout_IO_L3_out_single_latency
	latency_meta["latency_main"]["PE_latency"] = PE_latency
	latency_meta["latency_main"]["cin_IO_L2_in_latency"] = cin_IO_L2_in_latency
	latency_meta["latency_main"]["cin_IO_L3_in_latency"] = cin_IO_L3_in_latency
	latency_meta["latency_main"]["cout_IO_L1_in_latency"] = cout_IO_L1_in_latency
	latency_meta["latency_main"]["cout_IO_L1_out_latency"] = cout_IO_L1_out_latency
	latency_meta["latency_main"]["cout_IO_L2_in_latency"] = cout_IO_L2_in_latency
	latency_meta["latency_main"]["cout_IO_L2_out_latency"] = cout_IO_L2_out_latency
	latency_meta["latency_main"]["cout_IO_L3_in_latency"] = cout_IO_L3_in_latency
	latency_meta["latency_main"]["cout_IO_L3_out_latency"] = cout_IO_L3_out_latency
	latency_meta["latency_main"]["w_IO_L2_in_latency"] = w_IO_L2_in_latency
	latency_meta["latency_main"]["w_IO_L3_in_latency"] = w_IO_L3_in_latency
	return latency, latency_meta

def est_activity(params):
	q, p, o, r, c, i, o_t1, r_t1, c_t1, i_t1, o_t2, r_t2, c_t2, i_t2, p14, p15, p16, p17 = params["q"], params["p"], params["o"], params["r"], params["c"], params["i"], params["o_t1"], params["r_t1"], params["c_t1"], params["i_t1"], params["o_t2"], params["r_t2"], params["c_t2"], params["i_t2"], params["p14"], params["p15"], params["p16"], params["p17"]

	activity = {}
	activity["off_chip_acc_num_meta"] = {}
	off_chip_acc_num = 0
	cin_IO_L3_in_off_chip_acc_num = ceil((o/o_t1)) * ceil((i/i_t1)) * ceil((r/r_t1)) * ceil((c/c_t1)) * (r_t1/r_t2) * ((((r_t2-1)+(p-1))+1)*((((((c_t1/c_t2)-1)*c_t2)+(c_t2-1))+(q-1))+1)*i_t1)
	activity["off_chip_acc_num_meta"]["cin_IO_L3_in"] = cin_IO_L3_in_off_chip_acc_num
	off_chip_acc_num += cin_IO_L3_in_off_chip_acc_num
	cout_IO_L3_in_off_chip_acc_num = ceil((o/o_t1)) * ceil((r/r_t1)) * ceil((c/c_t1)) * (r_t1/r_t2) * (o_t1/o_t2) * (r_t2*c_t1*o_t2)
	activity["off_chip_acc_num_meta"]["cout_IO_L3_in"] = cout_IO_L3_in_off_chip_acc_num
	off_chip_acc_num += cout_IO_L3_in_off_chip_acc_num
	cout_IO_L3_out_off_chip_acc_num = ceil((o/o_t1)) * ceil((r/r_t1)) * ceil((c/c_t1)) * (r_t1/r_t2) * (o_t1/o_t2) * (r_t2*c_t1*o_t2)
	activity["off_chip_acc_num_meta"]["cout_IO_L3_out"] = cout_IO_L3_out_off_chip_acc_num
	off_chip_acc_num += cout_IO_L3_out_off_chip_acc_num
	w_IO_L3_in_off_chip_acc_num = ceil((o/o_t1)) * ceil((i/i_t1)) * (o_t1/o_t2) * (o_t2*((p-1)+1)*((q-1)+1)*i_t1)
	activity["off_chip_acc_num_meta"]["w_IO_L3_in"] = w_IO_L3_in_off_chip_acc_num
	off_chip_acc_num += w_IO_L3_in_off_chip_acc_num
	activity["off_chip_acc_num"] = off_chip_acc_num

	noc_hop_num = 0
	cin_IO_L2_in_io_noc_hop_num = (1 + (r_t1/r_t2)) / 2
	cin_IO_L2_in_io_noc_hop_num *= ceil((o/o_t1)) * ceil((i/i_t1)) * ceil((r/r_t1)) * ceil((c/c_t1)) * (((r_t1/r_t2) * ((((r_t2-1)+(p-1))+1)*((((((c_t1/c_t2)-1)*c_t2)+(c_t2-1))+(q-1))+1)*i_t1)) + 0)
	noc_hop_num += cin_IO_L2_in_io_noc_hop_num
	cin_IO_L3_in_io_noc_hop_num = (1 + 1) / 2
	cin_IO_L3_in_io_noc_hop_num *= ceil((o/o_t1)) * ceil((i/i_t1)) * ceil((r/r_t1)) * ceil((c/c_t1)) * (r_t1/r_t2) * ((((r_t2-1)+(p-1))+1)*((((((c_t1/c_t2)-1)*c_t2)+(c_t2-1))+(q-1))+1)*i_t1)
	noc_hop_num += cin_IO_L3_in_io_noc_hop_num
	cout_IO_L1_in_io_noc_hop_num = (1 + (o_t1/o_t2)) / 2
	cout_IO_L1_in_io_noc_hop_num *= ceil((o/o_t1)) * ceil((r/r_t1)) * ceil((c/c_t1)) * (((o_t1/o_t2) * (r_t2*c_t1*o_t2)) + 0)
	cout_IO_L1_in_io_noc_hop_num *= (r_t1/r_t2)
	noc_hop_num += cout_IO_L1_in_io_noc_hop_num
	cout_IO_L1_out_io_noc_hop_num = (1 + (o_t1/o_t2)) / 2
	cout_IO_L1_out_io_noc_hop_num *= ceil((o/o_t1)) * ceil((r/r_t1)) * ceil((c/c_t1)) * (((o_t1/o_t2) * (r_t2*c_t1*o_t2)) + 0)
	cout_IO_L1_out_io_noc_hop_num *= (r_t1/r_t2)
	noc_hop_num += cout_IO_L1_out_io_noc_hop_num
	cout_IO_L2_in_io_noc_hop_num = (1 + (r_t1/r_t2)) / 2
	cout_IO_L2_in_io_noc_hop_num *= ceil((o/o_t1)) * ceil((r/r_t1)) * ceil((c/c_t1)) * (r_t1/r_t2) * (o_t1/o_t2) * (r_t2*c_t1*o_t2)
	noc_hop_num += cout_IO_L2_in_io_noc_hop_num
	cout_IO_L2_out_io_noc_hop_num = (1 + (r_t1/r_t2)) / 2
	cout_IO_L2_out_io_noc_hop_num *= ceil((o/o_t1)) * ceil((r/r_t1)) * ceil((c/c_t1)) * (r_t1/r_t2) * (o_t1/o_t2) * (r_t2*c_t1*o_t2)
	noc_hop_num += cout_IO_L2_out_io_noc_hop_num
	cout_IO_L3_in_io_noc_hop_num = (1 + 1) / 2
	cout_IO_L3_in_io_noc_hop_num *= ceil((o/o_t1)) * ceil((r/r_t1)) * ceil((c/c_t1)) * (r_t1/r_t2) * (o_t1/o_t2) * (r_t2*c_t1*o_t2)
	noc_hop_num += cout_IO_L3_in_io_noc_hop_num
	cout_IO_L3_out_io_noc_hop_num = (1 + 1) / 2
	cout_IO_L3_out_io_noc_hop_num *= ceil((o/o_t1)) * ceil((r/r_t1)) * ceil((c/c_t1)) * (r_t1/r_t2) * (o_t1/o_t2) * (r_t2*c_t1*o_t2)
	noc_hop_num += cout_IO_L3_out_io_noc_hop_num
	w_IO_L2_in_io_noc_hop_num = (1 + (o_t1/o_t2)) / 2
	w_IO_L2_in_io_noc_hop_num *= ceil((o/o_t1)) * ceil((i/i_t1)) * (((o_t1/o_t2) * (o_t2*((p-1)+1)*((q-1)+1)*i_t1)) + 0)
	noc_hop_num += w_IO_L2_in_io_noc_hop_num
	w_IO_L3_in_io_noc_hop_num = (1 + 1) / 2
	w_IO_L3_in_io_noc_hop_num *= ceil((o/o_t1)) * ceil((i/i_t1)) * (o_t1/o_t2) * (o_t2*((p-1)+1)*((q-1)+1)*i_t1)
	noc_hop_num += w_IO_L3_in_io_noc_hop_num
	cin_IO_L2_in_pe_noc_hop_num = ((o_t1/o_t2)*(r_t1/r_t2))
	cin_IO_L2_in_pe_noc_hop_num *= ceil((o/o_t1)) * ceil((i/i_t1)) * ceil((r/r_t1)) * ceil((c/c_t1)) * (((c_t1/c_t2) * (i_t1/i_t2) * p * q * c_t2 * r_t2 * o_t2 * 1) + 0)
	cin_IO_L2_in_pe_noc_hop_num *= i_t2
	noc_hop_num += cin_IO_L2_in_pe_noc_hop_num
	cout_IO_L1_in_pe_noc_hop_num = ((o_t1/o_t2)*(r_t1/r_t2))
	cout_IO_L1_in_pe_noc_hop_num *= ceil((o/o_t1)) * ceil((r/r_t1)) * ceil((c/c_t1)) * (((c_t1/c_t2) * c_t2 * r_t2 * o_t2 * 1) + 0)
	cout_IO_L1_in_pe_noc_hop_num *= 1
	noc_hop_num += cout_IO_L1_in_pe_noc_hop_num
	cout_IO_L1_out_pe_noc_hop_num = ((o_t1/o_t2)*(r_t1/r_t2))
	cout_IO_L1_out_pe_noc_hop_num *= ceil((o/o_t1)) * ceil((r/r_t1)) * ceil((c/c_t1)) * (((c_t1/c_t2) * c_t2 * r_t2 * o_t2 * 1) + 0)
	cout_IO_L1_out_pe_noc_hop_num *= 1
	noc_hop_num += cout_IO_L1_out_pe_noc_hop_num
	w_IO_L2_in_pe_noc_hop_num = ((o_t1/o_t2)*(r_t1/r_t2))
	w_IO_L2_in_pe_noc_hop_num *= ceil((o/o_t1)) * ceil((i/i_t1)) * ((ceil((r/r_t1)) * ceil((c/c_t1)) * (c_t1/c_t2) * (i_t1/i_t2) * p * q * c_t2 * r_t2 * o_t2 * 1) + 0)
	w_IO_L2_in_pe_noc_hop_num *= i_t2
	noc_hop_num += w_IO_L2_in_pe_noc_hop_num
	activity["noc_hop_num"] = noc_hop_num

	compute_stmt_call_num = 0
	compute_stmt_call_num = i_t2
	compute_stmt_call_num *= ceil((o/o_t1)) * ceil((i/i_t1)) * ceil((r/r_t1)) * ceil((c/c_t1)) * (0 + (c_t1/c_t2) * (i_t1/i_t2) * p * q * c_t2 * r_t2 * o_t2 * 1 + 0)
	compute_stmt_call_num *= ((o_t1/o_t2)*(r_t1/r_t2))
	activity["compute_stmt_call_num"] = compute_stmt_call_num

	io_module_mem_acc_num = 0
	cin_IO_L2_in_mem_acc_num = ceil((o/o_t1)) * ceil((i/i_t1)) * ceil((r/r_t1)) * ceil((c/c_t1)) * (((r_t1/r_t2) * ((((r_t2-1)+(p-1))+1)*((((((c_t1/c_t2)-1)*c_t2)+(c_t2-1))+(q-1))+1)*i_t1/p14) + (c_t1/c_t2) * (i_t1/i_t2) * p * q * c_t2 * r_t2 * o_t2 * 1) + 0)
	cin_IO_L2_in_mem_acc_num *= p14
	io_module_mem_acc_num += cin_IO_L2_in_mem_acc_num
	cout_IO_L1_in_mem_acc_num = ceil((o/o_t1)) * ceil((r/r_t1)) * ceil((c/c_t1)) * (((o_t1/o_t2) * (r_t2*c_t1*o_t2/p15) + (c_t1/c_t2) * c_t2 * r_t2 * o_t2 * 1) + 0)
	cout_IO_L1_in_mem_acc_num *= p15
	io_module_mem_acc_num += cout_IO_L1_in_mem_acc_num
	cout_IO_L1_out_mem_acc_num = ceil((o/o_t1)) * ceil((r/r_t1)) * ceil((c/c_t1)) * (((o_t1/o_t2) * (r_t2*c_t1*o_t2/p15) + (c_t1/c_t2) * c_t2 * r_t2 * o_t2 * 1) + 0)
	cout_IO_L1_out_mem_acc_num *= p15
	io_module_mem_acc_num += cout_IO_L1_out_mem_acc_num
	w_IO_L2_in_mem_acc_num = ceil((o/o_t1)) * ceil((i/i_t1)) * (((o_t1/o_t2) * (o_t2*((p-1)+1)*((q-1)+1)*i_t1/p17) + ceil((r/r_t1)) * ceil((c/c_t1)) * (c_t1/c_t2) * (i_t1/i_t2) * p * q * c_t2 * r_t2 * o_t2 * 1) + 0)
	w_IO_L2_in_mem_acc_num *= p17
	io_module_mem_acc_num += w_IO_L2_in_mem_acc_num
	activity["io_module_mem_acc_num"] = io_module_mem_acc_num

	pe_module_reg_acc_num = 0
	pe_module_mem_acc_num = 0
	pe_module_reg_acc_num = 2
	pe_module_mem_acc_num = 2
	pe_module_reg_acc_num *= i_t2
	pe_module_reg_acc_num *= ceil((o/o_t1)) * ceil((i/i_t1)) * ceil((r/r_t1)) * ceil((c/c_t1)) * (0 + (c_t1/c_t2) * (i_t1/i_t2) * p * q * c_t2 * r_t2 * o_t2 * 1 + 0)
	pe_module_reg_acc_num *= ((o_t1/o_t2)*(r_t1/r_t2))
	pe_module_mem_acc_num *= i_t2
	pe_module_mem_acc_num *= ceil((o/o_t1)) * ceil((i/i_t1)) * ceil((r/r_t1)) * ceil((c/c_t1)) * (0 + (c_t1/c_t2) * (i_t1/i_t2) * p * q * c_t2 * r_t2 * o_t2 * 1 + 0)
	pe_module_mem_acc_num *= ((o_t1/o_t2)*(r_t1/r_t2))
	activity["pe_module_reg_acc_num"] = pe_module_reg_acc_num
	activity["pe_module_mem_acc_num"] = pe_module_mem_acc_num

	return activity

def infer_params(params):
	q, p, o, r, c, i, o_t1, r_t1, c_t1, i_t1, o_t2, r_t2, c_t2, i_t2 = params["q"], params["p"], params["o"], params["r"], params["c"], params["i"], params["o_t1"], params["r_t1"], params["c_t1"], params["i_t1"], params["o_t2"], params["r_t2"], params["c_t2"], params["i_t2"]

	p14_choices = [n*i_t2 for n in range(1, max(min(i_t1,16),i_t2)//i_t2+1) if max(min(i_t1,16),i_t2)%(n*i_t2)==0]
	if len(p14_choices) == 0:
		return None
	params["p14"] = max(p14_choices)
	p15_choices = [n*1 for n in range(1, max(min(o_t2,4),1)//1+1) if max(min(o_t2,4),1)%(n*1)==0]
	if len(p15_choices) == 0:
		return None
	params["p15"] = max(p15_choices)
	p16_choices = [n*1 for n in range(1, max(min(o_t2,4),1)//1+1) if max(min(o_t2,4),1)%(n*1)==0]
	if len(p16_choices) == 0:
		return None
	params["p16"] = max(p16_choices)
	p17_choices = [n*i_t2 for n in range(1, max(min(i_t1,16),i_t2)//i_t2+1) if max(min(i_t1,16),i_t2)%(n*i_t2)==0]
	if len(p17_choices) == 0:
		return None
	params["p17"] = max(p17_choices)

	return params

def random_sampling(params):
	def filter_non_power_of_two(x):
		if np.log2(x) != int(np.log2(x)):
			return True
		return False

	q = params["q"]
	p = params["p"]
	o = params["o"]
	r = params["r"]
	c = params["c"]
	i = params["i"]
	while True:
		sample = random.randint(int(1), int(o))
		o_t1 = sample
		params["o_t1"] = sample
		sample = random.randint(int(1), int(c))
		c_t1 = sample
		params["c_t1"] = sample
		sample = random.randint(int(1), int(r))
		r_t1 = sample
		params["r_t1"] = sample
		sample = random.randint(int(1), int(i))
		i_t1 = sample
		params["i_t1"] = sample
		sample = random.sample(utils.get_divisors(int(o_t1), None), 1)[-1]
		o_t2 = sample
		params["o_t2"] = sample
		sample = random.sample(utils.get_divisors(int(c_t1), None), 1)[-1]
		c_t2 = sample
		params["c_t2"] = sample
		sample = random.sample(utils.get_divisors(int(r_t1), None), 1)[-1]
		r_t2 = sample
		params["r_t2"] = sample
		sample = random.sample(utils.get_divisors(int(min(i_t1,8)), filter_non_power_of_two), 1)[-1]
		i_t2 = sample
		params["i_t2"] = sample
		latency_factors = 1
		latency_factors *= o_t2
		latency_factors *= r_t2
		latency_factors *= c_t2
		simd_factor = i_t2
		if latency_factors >= 8 * simd_factor:
			break

	return params

def bound_check(params):
	def filter_non_power_of_two(x):
		if np.log2(x) != int(np.log2(x)):
			return True
		return False

	q, p, o, r, c, i, o_t1, r_t1, c_t1, i_t1, o_t2, r_t2, c_t2, i_t2, p14, p15, p16, p17 = params["q"], params["p"], params["o"], params["r"], params["c"], params["i"], params["o_t1"], params["r_t1"], params["c_t1"], params["i_t1"], params["o_t2"], params["r_t2"], params["c_t2"], params["i_t2"], params["p14"], params["p15"], params["p16"], params["p17"]

	if o_t1 < 1:
		return False
	if r_t1 < 1:
		return False
	if c_t1 < 1:
		return False
	if i_t1 < 1:
		return False
	if o_t2 < 1:
		return False
	if o_t2 > o_t1:
		return False
	if r_t2 < 1:
		return False
	if r_t2 > r_t1:
		return False
	if c_t2 < 1:
		return False
	if c_t2 > c_t1:
		return False
	if i_t2 < 1:
		return False
	if i_t2 > min(i_t1,8):
		return False
	if filter_non_power_of_two(i_t2):
		return False
	if p14 < i_t2:
		return False
	if p14 > max(min(i_t1,16),i_t2):
		return False
	if filter_non_power_of_two(p14):
		return False
	if p15 < 1:
		return False
	if p15 > max(min(o_t2,4),1):
		return False
	if filter_non_power_of_two(p15):
		return False
	if p16 < 1:
		return False
	if p16 > max(min(o_t2,4),1):
		return False
	if filter_non_power_of_two(p16):
		return False
	if p17 < i_t2:
		return False
	if p17 > max(min(i_t1,16),i_t2):
		return False
	if filter_non_power_of_two(p17):
		return False
	latency_factors = 1
	latency_factors *= o_t2
	latency_factors *= r_t2
	latency_factors *= c_t2
	simd_factor = i_t2
	if latency_factors < 8 * simd_factor:
		return False
	if (o_t1/o_t2) <= 1:
		return False
	if (r_t1/r_t2) <= 1:
		return False
	return True

def compute_arch_cst(params):
	q, p, o, r, c, i, o_t1, r_t1, c_t1, i_t1, o_t2, r_t2, c_t2, i_t2, p14, p15, p16, p17 = params["q"], params["p"], params["o"], params["r"], params["c"], params["i"], params["o_t1"], params["r_t1"], params["c_t1"], params["i_t1"], params["o_t2"], params["r_t2"], params["c_t2"], params["i_t2"], params["p14"], params["p15"], params["p16"], params["p17"]

	arch_features = {}
	arch_features['dims'] = []
	arch_features["dims"].append((o_t1/o_t2))
	if arch_features["dims"][-1] == 0:
		return None
	arch_features["dims"].append((r_t1/r_t2))
	if arch_features["dims"][-1] == 0:
		return None
	arch_features["SIMD"] = i_t2
	arch_features["data_pack"] = {}

	return arch_features

from gekko import GEKKO
import numpy as np

def get_solver_latency(problem_size, resource_limits, solver):
	m = GEKKO(remote=False)
	m.options.MAX_ITER = 10000

	bram_bound = int(resource_limits["BRAM18K"])
	dsp_bound = int(resource_limits["DSP"])

	q = problem_size["q"]
	p = problem_size["p"]
	o = problem_size["o"]
	r = problem_size["r"]
	c = problem_size["c"]
	i = problem_size["i"]
	o_t1 = m.Var(lb=1, ub=o, value=o)
	r_t1 = m.Var(lb=1, ub=r, value=r)
	c_t1 = m.Var(lb=1, ub=c, value=c)
	i_t1 = m.Var(lb=1, ub=i, value=i)
	o_t2 = m.Var(lb=1, ub=o_t1, value=o_t1)
	r_t2 = m.Var(lb=1, ub=r_t1, value=r_t1)
	c_t2 = m.Var(lb=1, ub=c_t1, value=c_t1)
	i_t2 = m.Var(lb=1, ub=i_t1, value=i_t1)
	p14 = m.Var(lb=1)
	p15 = m.Var(lb=1)
	p16 = m.Var(lb=1)
	p17 = m.Var(lb=1)

	cin_IO_L2_in_single_latency = ((r_t1/r_t2) * ((((r_t2-1)+(p-1))+1)*((((((c_t1/c_t2)-1)*c_t2)+(c_t2-1))+(q-1))+1)*i_t1/p14) + 1)
	cin_IO_L3_in_single_latency = (r_t1/r_t2) * ((((r_t2-1)+(p-1))+1)*((((((c_t1/c_t2)-1)*c_t2)+(c_t2-1))+(q-1))+1)*i_t1/i_t1*(20+i_t1/(512/8/4)))
	cout_IO_L1_in_single_latency = ((o_t1/o_t2) * (r_t2*c_t1*o_t2/p15) + 1)
	cout_IO_L2_in_single_latency = (r_t1/r_t2) * (o_t1/o_t2) * (r_t2*c_t1*o_t2/p15)
	cout_IO_L3_in_single_latency = (r_t1/r_t2) * (o_t1/o_t2) * (r_t2*c_t1*o_t2/o_t2*(20+o_t2/(512/8/4)))
	w_IO_L2_in_single_latency = ((o_t1/o_t2) * (o_t2*((p-1)+1)*((q-1)+1)*i_t1/p17) + 1)
	w_IO_L3_in_single_latency = (o_t1/o_t2) * (o_t2*((p-1)+1)*((q-1)+1)*i_t1/i_t1*(20+i_t1/(512/8/4)))

	latency_prologue = m.Var()

	m.Equation(cin_IO_L2_in_single_latency <= latency_prologue)
	m.Equation(cin_IO_L3_in_single_latency <= latency_prologue)
	m.Equation(cout_IO_L1_in_single_latency <= latency_prologue)
	m.Equation(cout_IO_L2_in_single_latency <= latency_prologue)
	m.Equation(cout_IO_L3_in_single_latency <= latency_prologue)
	m.Equation(w_IO_L2_in_single_latency <= latency_prologue)
	m.Equation(w_IO_L3_in_single_latency <= latency_prologue)


	cout_IO_L1_out_single_latency = ((o_t1/o_t2) * (r_t2*c_t1*o_t2/p15) + 1)
	cout_IO_L2_out_single_latency = (r_t1/r_t2) * (o_t1/o_t2) * (r_t2*c_t1*o_t2/p15)
	cout_IO_L3_out_single_latency = (r_t1/r_t2) * (o_t1/o_t2) * (r_t2*c_t1*o_t2/o_t2*(20+o_t2/(512/8/4)))

	latency_epilogue = m.Var()

	m.Equation(cout_IO_L1_out_single_latency <= latency_epilogue)
	m.Equation(cout_IO_L2_out_single_latency <= latency_epilogue)
	m.Equation(cout_IO_L3_out_single_latency <= latency_epilogue)


	PE_latency = ((o/o_t1)) * ((i/i_t1)) * ((r/r_t1)) * ((c/c_t1)) * (1 + (c_t1/c_t2) * (i_t1/i_t2) * p * q * c_t2 * r_t2 * o_t2 * 1 + 1)
	cin_IO_L2_in_latency = ((o/o_t1)) * ((i/i_t1)) * ((r/r_t1)) * ((c/c_t1)) * (m.max2((r_t1/r_t2) * ((((r_t2-1)+(p-1))+1)*((((((c_t1/c_t2)-1)*c_t2)+(c_t2-1))+(q-1))+1)*i_t1/p14), (c_t1/c_t2) * (i_t1/i_t2) * p * q * c_t2 * r_t2 * o_t2 * 1) + 1)
	cin_IO_L3_in_latency = ((o/o_t1)) * ((i/i_t1)) * ((r/r_t1)) * ((c/c_t1)) * (r_t1/r_t2) * ((((r_t2-1)+(p-1))+1)*((((((c_t1/c_t2)-1)*c_t2)+(c_t2-1))+(q-1))+1)*i_t1/i_t1*(20+i_t1/(512/8/4)))
	cout_IO_L1_in_latency = ((o/o_t1)) * ((r/r_t1)) * ((c/c_t1)) * (m.max2((o_t1/o_t2) * (r_t2*c_t1*o_t2/p15), (c_t1/c_t2) * c_t2 * r_t2 * o_t2 * 1) + 1)
	cout_IO_L1_out_latency = ((o/o_t1)) * ((r/r_t1)) * ((c/c_t1)) * (m.max2((o_t1/o_t2) * (r_t2*c_t1*o_t2/p15), (c_t1/c_t2) * c_t2 * r_t2 * o_t2 * 1) + 1)
	cout_IO_L2_in_latency = ((o/o_t1)) * ((r/r_t1)) * ((c/c_t1)) * (r_t1/r_t2) * (o_t1/o_t2) * (r_t2*c_t1*o_t2/p15)
	cout_IO_L2_out_latency = ((o/o_t1)) * ((r/r_t1)) * ((c/c_t1)) * (r_t1/r_t2) * (o_t1/o_t2) * (r_t2*c_t1*o_t2/p15)
	cout_IO_L3_in_latency = ((o/o_t1)) * ((r/r_t1)) * ((c/c_t1)) * (r_t1/r_t2) * (o_t1/o_t2) * (r_t2*c_t1*o_t2/o_t2*(20+o_t2/(512/8/4)))
	cout_IO_L3_out_latency = ((o/o_t1)) * ((r/r_t1)) * ((c/c_t1)) * (r_t1/r_t2) * (o_t1/o_t2) * (r_t2*c_t1*o_t2/o_t2*(20+o_t2/(512/8/4)))
	w_IO_L2_in_latency = ((o/o_t1)) * ((i/i_t1)) * (m.max2((o_t1/o_t2) * (o_t2*((p-1)+1)*((q-1)+1)*i_t1/p17), ((r/r_t1)) * ((c/c_t1)) * (c_t1/c_t2) * (i_t1/i_t2) * p * q * c_t2 * r_t2 * o_t2 * 1) + 1)
	w_IO_L3_in_latency = ((o/o_t1)) * ((i/i_t1)) * (o_t1/o_t2) * (o_t2*((p-1)+1)*((q-1)+1)*i_t1/i_t1*(20+i_t1/(512/8/4)))

	latency_main = m.Var()

	m.Equation(PE_latency <= latency_main)
	m.Equation(cin_IO_L2_in_latency <= latency_main)
	m.Equation(cin_IO_L3_in_latency <= latency_main)
	m.Equation(cout_IO_L1_in_latency <= latency_main)
	m.Equation(cout_IO_L1_out_latency <= latency_main)
	m.Equation(cout_IO_L2_in_latency <= latency_main)
	m.Equation(cout_IO_L2_out_latency <= latency_main)
	m.Equation(cout_IO_L3_in_latency <= latency_main)
	m.Equation(cout_IO_L3_out_latency <= latency_main)
	m.Equation(w_IO_L2_in_latency <= latency_main)
	m.Equation(w_IO_L3_in_latency <= latency_main)


	latency = latency_prologue + latency_main + latency_epilogue

	m.Equation(((o_t1/o_t2)*(r_t1/r_t2)) * i_t2 * 5 <= dsp_bound)

	m.Equation(
	(4*8*1 / 36) * (((r_t2*c_t1)*o_t2)/1/512) * 1 * ((o_t1/o_t2)*(r_t1/r_t2)) + 
	(4*8*p14 / 36) * ((((((r_t2-1)+(p-1))+1)*((((((c_t1/c_t2)-1)*c_t2)+(c_t2-1))+(q-1))+1))*i_t1)/p14/512) * 2 * (r_t1/r_t2) + 
	(4*8*p15 / 36) * (((r_t2*c_t1)*o_t2)/p15/512) * 2 * ((r_t1/r_t2)*(o_t1/o_t2)) + 
	(4*8*p15 / 36) * (((r_t2*c_t1)*o_t2)/p15/512) * 2 * ((r_t1/r_t2)*(o_t1/o_t2)) + 
	(4*8*p17 / 36) * ((((o_t2*((p-1)+1))*((q-1)+1))*i_t1)/p17/512) * 2 * (o_t1/o_t2)
	<= bram_bound)

	m.Equation(o_t1 >= 1)
	m.Equation(o_t1 <= o)
	m.Equation(r_t1 >= 1)
	m.Equation(r_t1 <= r)
	m.Equation(c_t1 >= 1)
	m.Equation(c_t1 <= c)
	m.Equation(i_t1 >= 1)
	m.Equation(i_t1 <= i)
	m.Equation(o_t2 >= 1)
	m.Equation(o_t2 <= o_t1)
	m.Equation(r_t2 >= 1)
	m.Equation(r_t2 <= r_t1)
	m.Equation(c_t2 >= 1)
	m.Equation(c_t2 <= c_t1)
	m.Equation(i_t2 >= 1)
	m.Equation(i_t2 <= m.min2(i_t1,8))
	m.Equation(p14 >= i_t2)
	m.Equation(p14 <= m.max2(m.min2(i_t1,16),i_t2))
	m.Equation(p15 >= 1)
	m.Equation(p15 <= m.max2(m.min2(o_t2,4),1))
	m.Equation(p16 >= 1)
	m.Equation(p16 <= m.max2(m.min2(o_t2,4),1))
	m.Equation(p17 >= i_t2)
	m.Equation(p17 <= m.max2(m.min2(i_t1,16),i_t2))
	m.Equation(	o_t2 * r_t2 * c_t2 >= i_t2 * 8)
	try:
		m.Obj(latency)
		m.options.SOLVER = solver
		m.solve(disp=False)
		return m.options.OBJFCNVAL
	except:
		return np.inf

def try_all_solvers(problem_size, resource_limits):
	solvers = {1:'APOPT', 2:'BOPOPT', 3:'IPOPT'}
	cycles = []
	for i in range(3):
		cycles.append(get_solver_latency(problem_size, resource_limits, i))
		print(f'{solvers[i+1]}: {cycles[i]}', end=' ')
	print()
	return min(cycles)
