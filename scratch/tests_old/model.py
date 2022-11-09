

	A_IO_L2_in_single_latency = ((i_t1) * (k_t1/p9) + 1)
	A_IO_L3_in_single_latency = (i_t1) * (k_t1/min(p9, 512/8/4))
	B_IO_L2_in_single_latency = ((j_t1) * (k_t1/p10) + 1)
	B_IO_L3_in_single_latency = (j_t1) * (k_t1/min(p10, 512/8/4))
	latency_prologue = max(A_IO_L2_in_single_latency, A_IO_L3_in_single_latency, B_IO_L2_in_single_latency, B_IO_L3_in_single_latency)

	C_drain_IO_L1_out_single_latency = (i_t1) * (j_t2/p12)
	C_drain_IO_L2_out_single_latency = (j_t1) * (i_t1) * (1/p12)
	C_drain_IO_L3_out_single_latency = (j_t1) * (i_t1) * (1/min(p12, 512/8/4))
	latency_epilogue = max(C_drain_IO_L1_out_single_latency, C_drain_IO_L2_out_single_latency, C_drain_IO_L3_out_single_latency)

	A_IO_L2_in_latency        = ((i/i_t1)) * ((j/j_t1)) * ((k/k_t1)) * (max((i_t1/i_t2) * (i_t2*k_t1/p9), (k_t1/k_t2) * j_t2 * i_t2 * 1) + 1)
	A_IO_L3_in_latency        = ((i)) * ((j/j_t1)) * ((k)) * (1/min(p9, 512/8/4))
	B_IO_L2_in_latency        = ((i/i_t1)) * ((j/j_t1)) * ((k/k_t1)) * (max((j_t1/j_t2) * (j_t2*k_t1/p10), (k_t1/k_t2) * j_t2 * i_t2 * 1) + 1)
	B_IO_L3_in_latency        = ((i/i_t1)) * ((j)) * ((k)) * (1/min(p10, 512/8/4))
	C_drain_IO_L1_out_latency = ((i)) * ((j/j_t1)) * (j_t2/p12) + ((i/i_t1)) * ((j/j_t1)) * j_t2 * i_t2 * 1
	C_drain_IO_L2_out_latency = ((i)) * ((j)) * (1/p12)
	C_drain_IO_L3_out_latency = ((i)) * ((j)) * (1/min(p12, 512/8/4))
	PE_latency                = ((i/i_t1)) * ((j/j_t1)) * ((k)) * (1/k_t2) * j_t2 * i_t2 * 1
	latency_main = max(A_IO_L2_in_latency, A_IO_L3_in_latency, B_IO_L2_in_latency, B_IO_L3_in_latency, C_drain_IO_L1_out_latency, C_drain_IO_L2_out_latency, C_drain_IO_L3_out_latency, PE_latency)

	latency = latency_prologue + latency_main + latency_epilogue


minimize target:
	max(
		((i/i_t1)) * ((j/j_t1)) * ((k/k_t1)) * (max((i_t1/i_t2) * (i_t2*k_t1/p9), (k_t1/k_t2) * j_t2 * i_t2 * 1) + 1),
		((i/i_t1)) * ((j/j_t1)) * ((k/k_t1)) * (i_t1/i_t2) * (i_t2*k_t1/min(p9, 512/8/4)),
		((i/i_t1)) * ((j/j_t1)) * ((k/k_t1)) * (max((j_t1/j_t2) * (j_t2*k_t1/p10), (k_t1/k_t2) * j_t2 * i_t2 * 1) + 1),
		((i/i_t1)) * ((j/j_t1)) * ((k/k_t1)) * (j_t1/j_t2) * (j_t2*k_t1/min(p10, 512/8/4)),
		((i/i_t1)) * ((j/j_t1)) * ((i_t1/i_t2) * (i_t2*j_t2/p12) + j_t2 * i_t2 * 1),
		((i/i_t1)) * ((j/j_t1)) * (j_t1/j_t2) * (i_t1/i_t2) * (i_t2*j_t2/p12),
		((i/i_t1)) * ((j/j_t1)) * (j_t1/j_t2) * (i_t1/i_t2) * (i_t2*j_t2/min(p12, 512/8/4)),
		((i/i_t1)) * ((j/j_t1)) * ((k/k_t1)) * (k_t1/k_t2) * j_t2 * i_t2 * 1
	);

minimize target:
	max(
		((i/i_t1)) * ((j/j_t1)) * ((k/k_t1)) * (max((i_t1/i_t2) * (i_t2*k_t1/p9), (k_t1/k_t2) * j_t2 * i_t2 * 1) + 1),
		((i)) * ((j/j_t1)) * ((k)) * (1/min(p9, 512/8/4)),
		((i/i_t1)) * ((j/j_t1)) * ((k/k_t1)) * (max((j_t1/j_t2) * (j_t2*k_t1/p10), (k_t1/k_t2) * j_t2 * i_t2 * 1) + 1),
		((i/i_t1)) * ((j)) * ((k)) * (1/min(p10, 512/8/4)),
		((i)) * ((j/j_t1)) * (j_t2/p12) + ((i/i_t1)) * ((j/j_t1)) * j_t2 * i_t2 * 1,
		((i)) * ((j)) * (1/p12),
		((i)) * ((j)) * (1/min(p12, 512/8/4)),
		((i/i_t1)) * ((j/j_t1)) * ((k)) * (1/k_t2) * j_t2 * i_t2 * 1
	);