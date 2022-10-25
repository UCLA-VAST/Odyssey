from kernel3 import *
import os
import numpy as np
import json
import argparse
import copy
import multiprocessing
import subprocess
import time
import itertools
import matplotlib.pyplot as plt
import pandas as pd
import sys
from tqdm import tqdm

def printResults(results, I, J, K, objective, num_top_results, alpha):

  prj_path = os.environ['prj_path']

  dw = 4 #bytes

  with open(prj_path+f'/search/results/method_2_{objective}_top_{num_top_results}_{I}_{alpha}.csv', 'w') as f:
    if objective == 'latency_off_chip_comm':
      print('design_idx,objective,score,padded workload,fre,throughput (GFLOP/s),cycles,latency(ms),DSP eff, off-chip bytes, bandwidth (GB/s), CTC, DSPs,BRAMs,PEs,AL3_P,BL3_P,CL3_P,"(SA_COLs, SA_ROWs, SIMD)",sa_sizes', file=f)
    else:
      print('design_idx,objective,padded workload,fre,throughput (GFLOP/s),cycles,latency(ms),DSP eff, off-chip bytes, bandwidth (GB/s), CTC, DSPs,BRAMs,PEs,AL3_P,BL3_P,CL3_P,"(SA_COLs, SA_ROWs, SIMD)",sa_sizes', file=f)
    # print top 1000 results
    for idx, result in enumerate(results[:min(num_top_results, len(results))]):
      i = result['params']['i']
      j = result['params']['j']
      k = result['params']['k']
      i_t1 = result['params']['i_t1']
      j_t1 = result['params']['j_t1']
      k_t1 = result['params']['k_t1']
      i_t2 = result['params']['i_t2']
      j_t2 = result['params']['j_t2']
      k_t2 = result['params']['k_t2']
      AL3_P = result['params']['p9']
      BL3_P = result['params']['p10']
      CL3_P = result['params']['p12']
      result['design_idx'] = f'design_{idx+1}'

      padded_size = '"' + str((i, j, k)) + '"'

      # objective = 'latency'

      # Resources
      DSPs = result['resources'][0]['DSP']
      BRAMs = result['resources'][0]['BRAM18K']
      PEs = result['arch']['dims'][0]*result['arch']['dims'][1]
      SA_Dims = '"' + str((int(result['arch']['dims'][0]), int(result['arch']['dims'][1]), int(result['arch']['SIMD']))) + '"'
      
      # Performance
      fre = 300
      OPS = 2*I*J*K
      GFLOPS = OPS/1e9
      cycles = result['cycles'][0]
      latency = cycles/fre/1e3
      throughput = GFLOPS/latency*1e3
      peak_throughput = 2*(DSPs/5)*fre/1e3
      dsp_eff = (throughput/peak_throughput)*100

      # Memory
      off_chip_trans = result['off_chip_trans']
      off_chip_bytes = result['off_chip_trans']*4
      bandwidth = compute_bw(result['params'], dw, fre)
      
      # CTC
      CTC = compute_ctc(result['params'], OPS, off_chip_trans, dw)


      print(f'design_{idx+1},', end='', file=f)
      print(f'{objective},', end='', file=f)
      if objective == 'latency_off_chip_comm':
        score = result['score']
        print(f'{score:.5f},', end='', file=f)
      print(f'{padded_size},', end='', file=f)
      print(f'{fre:.0f},', end='', file=f)
      print(f'{throughput:.2f},', end='', file=f)
      print(f'{cycles:.0f},', end='', file=f)
      print(f'{latency:.5f},', end='', file=f)
      print(f'{dsp_eff:.2f}%,', end='', file=f)
      print(f'{off_chip_bytes:.0f},', end='', file=f)
      print(f'{bandwidth:.2f},', end='', file=f)
      print(f'{CTC:.2f},', end='', file=f)
      print(f'{DSPs:.0f},', end='', file=f)
      print(f'{BRAMs:.0f},', end='', file=f)
      print(f'{PEs:.0f},', end='', file=f)
      print(f'{AL3_P:.0f},', end='', file=f)
      print(f'{BL3_P:.0f},', end='', file=f)
      print(f'{CL3_P:.0f},', end='', file=f)
      print(f'{SA_Dims},', end='', file=f)
      print( '"{'+f'kernel[]->space_time[3];kernel[]->array_part[{i_t1},{j_t1},{k_t1}];kernel[]->latency[{i_t2},{j_t2}];kernel[]->simd[{k_t2}]' + '}"', end='', file=f)


      print(file=f)

def list_split(ori_list, split_num):
  chunk_size = int(np.ceil(float(len(ori_list)) / split_num))
  chunks = [ori_list[i: i + min(chunk_size, len(ori_list) - i)] for i in range(0, len(ori_list), chunk_size)]
  return chunks


def pruned_search(i_t0, j_t0, k_t0, resource_limits):
  i_t1_candidates = [i for i in range(i_t0+1, 0, -1) if i_t0 % i == 0]
  j_t1_candidates = [j for j in range(j_t0+1, 0, -1) if j_t0 % j == 0]
  min_off_chip = np.inf
  for i_t1 in i_t1_candidates:
    for j_t1 in j_t1_candidates:
      i_t2_candidates = [i for i in range(i_t1+1, 0, -1) if i_t1 % i == 0]
      j_t2_candidates = [j for j in range(j_t1+1, 0, -1) if j_t1 % j == 0]
      for i_t2 in i_t2_candidates:
        for j_t2 in j_t2_candidates:
          params = {}
          params["i"] = i_t0
          params["j"] = j_t0
          params["k"] = k_t0
          params["i_t1"] = i_t1
          params["j_t1"] = j_t1
          params["k_t1"] = 1
          params["i_t2"] = i_t2
          params["j_t2"] = j_t2
          params["k_t2"] = 1
          params = infer_params(params)
          result = {}
          result['cycles'] = est_latency(params)
          result['resources'] = est_resource(params)
          result['arch'] = compute_arch_cst(params)
          result['params'] = params
          result['off_chip_trans'] = est_activity(params)['off_chip_acc_num']
          if result['resources'][0]['DSP'] > resource_limits['DSP'] or result['resources'][0]['BRAM18K'] > resource_limits['BRAM18K'] or (1.0 in result['arch']['dims']):
            continue
          if i_t2*j_t2 < 8:
            continue
          if result['off_chip_trans'] < min_off_chip:
            min_off_chip = result['off_chip_trans']    
  # if min_off_chip == np.inf:
  #   return 0
  return min_off_chip

def est_min_off_chip_trans(i_t0, j_t0, k_t0, resource_limits):
  if i_t0 > j_t0:
    factor = 1
    BRAMs = np.inf
    while BRAMs > resource_limits['BRAM18K']:
      params = {}
      params["i"] = i_t0
      params["j"] = j_t0
      params["k"] = k_t0
      params["i_t1"] = i_t0/factor
      params["j_t1"] = j_t0
      params["k_t1"] = 1
      params["i_t2"] = i_t0/factor
      params["j_t2"] = j_t0
      params["k_t2"] = 1
      params = infer_params(params)
      BRAMs = est_resource(params)[0]['BRAM18K']
      factor += 1
    return est_activity(params)['off_chip_acc_num']
  else:
    factor = 1
    BRAMs = np.inf
    while BRAMs > resource_limits['BRAM18K']:
      params = {}
      params["i"] = i_t0
      params["j"] = j_t0
      params["k"] = k_t0
      params["i_t1"] = i_t0
      params["j_t1"] = j_t0/factor
      params["k_t1"] = 1
      params["i_t2"] = i_t0
      params["j_t2"] = j_t0/factor
      params["k_t2"] = 1
      params = infer_params(params)
      BRAMs = est_resource(params)[0]['BRAM18K']
      factor += 1
    return est_activity(params)['off_chip_acc_num']


def est_min_latency(i_t0, j_t0, k_t0, resource_limits):
  if i_t0 > j_t0:
    DSPs = np.inf
    factor1 = 1
    factor2 = 1
    # while DSPs > resource_limits['DSP']:
    #   while DSPs > resource_limits['DSP']:
    while (True):
      while (True):
        # print(factor1, factor2)
        params = {}
        params["i"] = i_t0
        params["j"] = j_t0
        params["k"] = k_t0
        params["i_t1"] = i_t0/factor1
        params["j_t1"] = j_t0/factor2
        params["k_t1"] = 64
        params["i_t2"] = 1
        params["j_t2"] = 1
        params["k_t2"] = 8
        params = infer_params(params)
        if i_t0%factor1 == 0 and j_t0%factor2 == 0:
          DSPs = est_resource(params)[0]['DSP']
        else:
          DSPs = np.inf
        factor1 += 1
        if DSPs <= resource_limits['DSP'] or factor1 >= i_t0:
          print(factor1, factor2, DSPs)
          factor1 = 1
          break
      params = {}
      params["i"] = i_t0
      params["j"] = j_t0
      params["k"] = k_t0
      params["i_t1"] = i_t0/factor1
      params["j_t1"] = j_t0/factor2
      params["k_t1"] = 64
      params["i_t2"] = 1
      params["j_t2"] = 1
      params["k_t2"] = 8
      params = infer_params(params)
      # if i_t0%factor1 == 0 and j_t0%factor2 == 0:
      DSPs = est_resource(params)[0]['DSP']
      # else:
      #   DSPs = np.inf
      factor2 += 1
      if DSPs <= resource_limits['DSP'] or factor2 >= j_t0:
        factor2 = 1
        break
      # factor1 = 1
      # DSPs = np.inf
      # factor2 += 1
    return est_latency(params), params
  # else:
  #   factor = 1
  #   BRAMs = np.inf
  #   while BRAMs > resource_limits['BRAM18K']:
  #     params = {}
  #     params["i"] = i_t0
  #     params["j"] = j_t0
  #     params["k"] = k_t0
  #     params["i_t1"] = i_t0
  #     params["j_t1"] = j_t0/factor
  #     params["k_t1"] = 1
  #     params["i_t2"] = i_t0
  #     params["j_t2"] = j_t0/factor
  #     params["k_t2"] = 1
  #     params = infer_params(params)
  #     BRAMs = est_resource(params)[0]['BRAM18K']
  #     factor += 1
  #   return est_latency(params)


def main():
  objective = sys.argv[1]
  num_top_results = int(sys.argv[2])
  alpha = 0
  if len(sys.argv) == 4:
    alpha = float(sys.argv[3])

  I, J, K = 1024, 1024, 1024

  time_start = time.time()
  results = search(I, J, K, objective, num_top_results, alpha)
  time_end = time.time()
  # print time in seconds
  print('Search finished in %f seconds' % (time_end - time_start))

  if objective == 'latency':
    # results = [item for sublist in results for item in sublist]
    results = sorted(results, key=lambda x: x['cycles'][0])
  elif objective == 'off_chip_comm':
    results = sorted(results, key=lambda x: x['off_chip_trans'])
  elif objective == 'latency_off_chip_comm': 
    results = sorted(results, key=lambda x: x['score'])

  printResults(results, I, J, K, objective, num_top_results, alpha)

  # # save results tidy
  # print('Saving results..')
  # with open(prj_path + '/search/result_1.json', 'w') as f:
  #   json.dump(results[0], f, indent=1)
  # with open(prj_path + '/search/result_2.json', 'w') as f:
  #   json.dump(results[30], f, indent=1)
  time_end = time.time()
  # print time in seconds
  print('Program finished in %f seconds' % (time_end - time_start))

# main()
I, J, K = 1032, 1025, 1024
 
prj_path = os.environ['prj_path']
board_info = json.load(open(prj_path + '/search/u250.json'))
resource_limits = {'DSP': board_info['DSP']['total']*board_info['DSP']['ratio'], 'BRAM18K': board_info['BRAM18K']['total']*board_info['BRAM18K']['ratio']}
min_latency, params = est_min_latency(I, J, K, resource_limits)
print(min_latency[0])
print(params)