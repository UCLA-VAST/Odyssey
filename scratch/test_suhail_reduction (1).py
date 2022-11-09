ri = i/i_t1 # x1
rj = j/j_t1 # x2
rk = k/k_t1

rijk = ri * rj * rj

rj1 = j_t1/j_t2 >= 1
rk1 = k_t1/k_t2

# j_t2 <= j_t1
# k_t2 <= min(k_t1,8)
# i_t2 <= i_t1
# kt2 power of two, why ?
# i_t2 * j_t2 >= 8 * k_t2

# p12 <= max(min(j_t2,4),1) <= 4
# p11 <= max(min(j_t2,4),1) <= 4
# p10 <= max(min(k_t1,16),k_t2) <= 16
# p9 <= max(min(k_t1,16),k_t2) <= 16
    
# A_IO_L2_in_latency = rijk * (max(i_t1 * rk1 * k_t2/p9, rk1 * j_t2 * i_t2 ) + 1)
# >= rijk * (i_t1 * k_t1/p9 + 1)
# >= rijk * (rk1 * j_t2 * i_t2 + 1)
# B_IO_L2_in_latency = rijk  * (max(rj1 * rk1 * k_t2/p10 * j_t2, rk1  * i_t2 * j_t2 ) + 1) 
BB = rijk * j_t2 * (max(i*k*rj/j_t2 + 1, rj1 * k_t1 /p10  + 1, rk1  * i_t2 + 1, 1/rk * (i_t1/p12 + i_t2 )))

# >= rijk * i_t1 * rk1 * k_t2/p9 + 1
# >= rijk * j_t2 * rj1 * rk1 * k_t2/p10  + 1
# >= rijk * j_t2 * rk1  * i_t2 + 1
# >= rijk * j_t2 * 1/rk * (i_t1/p12 + i_t2 )


# >= rijk * j_t1 * k_t1/p10
# >= rijk * j_t1 * rk1 * i_t2

# B_IO_L3_in_latency = rijk * j_t1 * k_t1/p10 # dominate per B_IO_L2_in_latency

# C_drain_IO_L3_out_latency = rijk/rk * j_t1 * 0.0625 # min useless # dominate per B_IO_L2_in_latency
# PE_latency = rijk * j_t2 * i_t2  * rk1  #k/k_t2 = rk * rk1 # rj * j_t2 = j / rj1 # dominate per B_IO_L2_in_latency


