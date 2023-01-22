# # DSP
# DSP = (i_t1/i_t2)*(j_t1/j_t2) * k_t2 * 5


# i_t1_dsp = (DSP_bound/5)**(1/3)
# j_t1_dsp = (DSP_bound/5)**(1/3)
# k_t1_dsp = (DSP_bound/5)**(1/3)
# i_t2_dsp = 1
# j_t2_dsp = 1
# k_t2_dsp = k_t1_dsp

# BRAM18K
def est_BRAM18K(ele_size, ele_num, pack):
  return f'ceil({ele_size}*8*{pack} / 36) * ceil({ele_num}/{pack}/512)'
from math import ceil
# res_meta = {}
A_IO_L2_in_unit_memory = est_BRAM18K('4', '(i_t2*k_t1)', 'p9')
# res_meta["A_IO_L2_in"] = {"ele_size": 4, "buf_size": (i_t2*k_t1), "data_pack_factor": 1, "num": (i_t1/i_t2)}
# res_meta["A_IO_L2_in"]["num"] *= 2
B_IO_L2_in_unit_memory = est_BRAM18K('4', '(j_t2*k_t1)', 'p10')
# res_meta["B_IO_L2_in"] = {"ele_size": 4, "buf_size": (j_t2*k_t1), "data_pack_factor": 1, "num": (j_t1/j_t2)}
# res_meta["B_IO_L2_in"]["num"] *= 2
C_drain_IO_L1_out_unit_memory = est_BRAM18K('4', '(i_t2*j_t2)','p12')
# res_meta["C_drain_IO_L1_out"] = {"ele_size": 4, "buf_size": (i_t2*j_t2), "data_pack_factor": 1, "num": ((j_t1/j_t2)*(i_t1/i_t2))}
PE_unit_memory = est_BRAM18K('4', '(i_t2*j_t2)', '1')
# res_meta["PE"] = {"ele_size": 4, "buf_size": (i_t2*j_t2), "data_pack_factor": 1, "num": ((i_t1/i_t2)*(j_t1/j_t2))}
print(f'{A_IO_L2_in_unit_memory} * 2 * (i_t1/i_t2) + ')
print(f'{B_IO_L2_in_unit_memory} * 2 * (j_t1/j_t2) + ')
print(f'{C_drain_IO_L1_out_unit_memory} * 1 * ((j_t1/j_t2)*(i_t1/i_t2)) + ')
print(f'{PE_unit_memory} * 1 * ((i_t1/i_t2)*(j_t1/j_t2))')

ceil(4*8*1 / 36) * ceil((i_t2*k_t1)/512) * 1 * (i_t1/i_t2) + 
ceil(4*8*1 / 36) * ceil((i_t2*k_t1)/512) * 1 * (i_t1/i_t2) + 
ceil(4*8*1 / 36) * ceil((j_t2*k_t1)/512) * 1 * (j_t1/j_t2) + 
ceil(4*8*1 / 36) * ceil((j_t2*k_t1)/512) * 1 * (j_t1/j_t2) + 
ceil(4*8*1 / 36) * ceil((i_t2*j_t2)/512) * 1 * ((j_t1/j_t2)*(i_t1/i_t2)) + 
ceil(4*8*1 / 36) * ceil((i_t2*j_t2)/512) * 1 * ((i_t1/i_t2)*(j_t1/j_t2))

# ceil(4*8*1 / 36) * 512 * 1 * i_t1 * k_t1 +
# ceil(4*8*1 / 36) * 512 * 1 * i_t1 * k_t1 +
# ceil(4*8*1 / 36) * 512 * 1 * k_t1 * j_t1 +
# ceil(4*8*1 / 36) * 512 * 1 * k_t1 * j_t1 +
# ceil(4*8*1 / 36) * 512 * 1 * j_t1 * i_t1 +
# ceil(4*8*1 / 36) * 512 * 1 * i_t1 * j_t1 = BRAMs
print(10/5/2)