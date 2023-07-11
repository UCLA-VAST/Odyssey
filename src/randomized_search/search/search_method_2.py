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

def run_latency_search(candidates, resource_limits, num_top_results):
  top_results = [{'cycles':[np.inf]}]*num_top_results
  for candidate in candidates:
    params = infer_params(candidate)
    result = {}
    result['cycles'] = est_latency(params)
    result['resources'] = est_resource(params)
    result['arch'] = compute_arch_cst(params)
    result['params'] = params
    result['off_chip_trans'] = est_activity(params)['off_chip_acc_num']
    if result['resources'][0]['DSP'] > resource_limits['DSP'] or result['resources'][0]['BRAM18K'] > resource_limits['BRAM18K'] or (1.0 in result['arch']['dims']):
      continue

    if result['cycles'][0] < top_results[-1]['cycles'][0]:
      for j in range(num_top_results):
        if result['cycles'][0] < top_results[j]['cycles'][0]:
          # insert result into results
          top_results.insert(j, result)
          # remove last element
          top_results.pop()
          break
    
  return top_results

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

def run_off_chip_search(candidates, resource_limits, num_top_results):
  top_results = [{'off_chip_trans':np.inf}]*num_top_results
  for candidate in candidates:
    params = infer_params(candidate)
    result = {}
    result['cycles'] = est_latency(params)
    result['resources'] = est_resource(params)
    result['arch'] = compute_arch_cst(params)
    result['params'] = params
    result['off_chip_trans'] = est_activity(params)['off_chip_acc_num']
    if result['resources'][0]['DSP'] > resource_limits['DSP'] or result['resources'][0]['BRAM18K'] > resource_limits['BRAM18K'] or (1.0 in result['arch']['dims']):
      continue
    
    if result['off_chip_trans'] < top_results[-1]['off_chip_trans']:
      
      for j in range(num_top_results):
        if result['off_chip_trans'] < top_results[j]['off_chip_trans']:
          # insert result into results
          top_results.insert(j, result)
          # remove last element
          top_results.pop()
          break
  return top_results

def run_latency_off_chip_search(candidates, resource_limits, num_top_results, min_latency, min_off_chip_comm, alpha):
  top_results = [{'score':np.inf}]*num_top_results
  beta = 1 - alpha
  for candidate in candidates:
    params = infer_params(candidate)
    result = {}
    result['cycles'] = est_latency(params)
    result['resources'] = est_resource(params)
    result['arch'] = compute_arch_cst(params)
    result['params'] = params
    result['off_chip_trans'] = est_activity(params)['off_chip_acc_num']
    
    if result['resources'][0]['DSP'] > resource_limits['DSP'] or result['resources'][0]['BRAM18K'] > resource_limits['BRAM18K'] or (1.0 in result['arch']['dims']):
      continue

    norm_latency = min_latency/result['cycles'][0]
    norm_off_chip_comm = min_off_chip_comm/result['off_chip_trans']
    score = 1/(alpha*norm_latency + beta*norm_off_chip_comm)
    result['score'] = score

    if result['score'] < top_results[-1]['score']:
      
      for j in range(num_top_results):
        if result['score'] < top_results[j]['score']:
          # insert result into results
          top_results.insert(j, result)
          # remove last element
          top_results.pop()
          break
  
  return top_results

    # results.append(result)
  # return results

I, J, K = 1024, 1024, 1024
i, j, k = I, J, K
while(True):
  while(True):
    curr_min_latency = getBestDivisors(i, j, k)
    j += 1
    min_theoratical_latency = i*j*k/(resource_limits['DSP'])
    if min_theoratical_latency >= curr_min_latency:
      j = J
      break
  i += 1
  min_theoratical_latency = i*j*k/(resource_limits['DSP'])
  if min_theoratical_latency >= curr_min_latency:
    break
def search_latency(I, J, K, num_top_results, resource_limits):
  top_results = [{'cycles':[np.inf]}]*num_top_results
  min_theoratical_latency = np.inf
  i_t0 = I
  j_t0 = J
  k_t0 = K
  while(True):
    while(True):
      i_t1_candidates = [i for i in range(1, i_t0+1) if i_t0 % i == 0]
      j_t1_candidates = [j for j in range(1, j_t0+1) if j_t0 % j == 0]
      k_t1_candidates = [k for k in range(1, k_t0+1) if k_t0 % k == 0]
      candidates = []
      for i_t1 in i_t1_candidates:
        for j_t1 in j_t1_candidates:
          for k_t1 in k_t1_candidates:
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

                  if i_t2*j_t2 < 8*k_t2 or k_t2 > 16:
                    continue
                  candidates.append(params)


      num_processes = int(multiprocessing.cpu_count() * 1)

      chunks = list_split(candidates, num_processes)
      pool = multiprocessing.Pool(processes = num_processes)
      results = pool.starmap(run_latency_search, [(chunk, resource_limits, num_top_results) for chunk in chunks])
      pool.close()
      results = [item for sublist in results for item in sublist]
      results = sorted(results, key=lambda x: x['cycles'][0])
      top_results.extend(results[:num_top_results])
      top_results = sorted(top_results, key=lambda x: x['cycles'][0])
      top_results = top_results[:num_top_results]

      j_t0 += 1
      min_theoratical_latency = i_t0*j_t0*k_t0/(resource_limits['DSP']/5)
      print(f'candidate ({i_t0}, {j_t0}, {k_t0})','min_theoratical_latency = ', int(min_theoratical_latency), 'current min_latency = ', int(top_results[-1]['cycles'][0]))
      if min_theoratical_latency >= top_results[-1]['cycles'][0]:
        print(j_t0)
        j_t0 = J
        break
    i_t0 += 1
    min_theoratical_latency = i_t0*j_t0*k_t0/(resource_limits['DSP']/5)
    if min_theoratical_latency >= top_results[-1]['cycles'][0]:
      print(i_t0)
      break

  return top_results

def search_off_chip(I, J, K, num_top_results, resource_limits):
  top_results = [{'off_chip_trans':np.inf}]*num_top_results
  
  i_t0 = I
  j_t0 = J
  k_t0 = K
  min_theoratical_off_chip = est_min_off_chip_trans(i_t0, j_t0, k_t0, resource_limits)#(i_t0*j_t0 + j_t0*k_t0 + i_t0*k_t0)
  # min_off_chip = pruned_search(i_t0, j_t0, k_t0, resource_limits)
  # print(f'candidate ({i_t0}, {j_t0}, {k_t0})','min_theoratical_off_chip = ', int(min_theoratical_off_chip), 'current min_off_chip = ', min_off_chip)
  while(True):
    while(True):
      print(f'candidate ({i_t0}, {j_t0}, {k_t0})','min_theoratical_off_chip = ', int(min_theoratical_off_chip), 'current min_off_chip = ', top_results[-1]['off_chip_trans'])
      i_t1_candidates = [i for i in range(1, i_t0+1) if i_t0 % i == 0]
      j_t1_candidates = [j for j in range(1, j_t0+1) if j_t0 % j == 0]
      k_t1_candidates = [k for k in range(1, k_t0+1) if k_t0 % k == 0]
      candidates = []
      for i_t1 in i_t1_candidates:
        for j_t1 in j_t1_candidates:
          for k_t1 in k_t1_candidates:
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

                  if i_t2*j_t2 < 8*k_t2 or k_t2 > 16:
                    continue
                  candidates.append(params)

      # if min_off_chip < top_results[-1]['off_chip_trans']:
      num_processes = int(multiprocessing.cpu_count() * 1)
      chunks = list_split(candidates, num_processes)
      pool = multiprocessing.Pool(processes = num_processes)
      results = pool.starmap(run_off_chip_search, [(chunk, resource_limits, num_top_results) for chunk in chunks])
      pool.close()
      results = [item for sublist in results for item in sublist]
      results = sorted(results, key=lambda x: x['off_chip_trans'])
      top_results.extend(results[:num_top_results])
      top_results = sorted(top_results, key=lambda x: x['off_chip_trans'])
      top_results = top_results[:num_top_results]
      # else:
      #   print('skipping this search as the min_off_chip is less than the current min_off_chip')
      j_t0 += 1
      # min_theoratical_off_chip = (i_t0*j_t0 + j_t0*k_t0 + i_t0*k_t0)
      min_theoratical_off_chip = est_min_off_chip_trans(i_t0, j_t0, k_t0, resource_limits)
      # min_off_chip = pruned_search(i_t0, j_t0, k_t0, resource_limits)

      # my_min_off_chip = (i_t0*j_t0 + j_t0*k_t0 + i_t0*k_t0)**2/(resource_limits['BRAM18K']*19500/32)

      if min_theoratical_off_chip >= top_results[-1]['off_chip_trans']:
        print(j_t0)
        j_t0 = J
        break
    i_t0 += 1
    # min_theoratical_off_chip = (i_t0*j_t0 + j_t0*k_t0 + i_t0*k_t0)
    min_theoratical_off_chip = est_min_off_chip_trans(i_t0, j_t0, k_t0, resource_limits)
    # min_off_chip = pruned_search(i_t0, j_t0, k_t0, resource_limits)
    if min_theoratical_off_chip >= top_results[-1]['off_chip_trans']:
      print(i_t0)
      break

  return top_results

def search_latency_off_chip(I, J, K, num_top_results, resource_limits, alpha):
  top_results = [{'score':np.inf}]*num_top_results
  i_t0 = I
  j_t0 = J
  k_t0 = K
  min_global_latency = i_t0*j_t0*k_t0/(resource_limits['DSP']/5)
  # min_global_off_chip = i_t0*j_t0 + j_t0*k_t0 + i_t0*k_t0
  min_global_off_chip = est_min_off_chip_trans(i_t0, j_t0, k_t0, resource_limits)
  min_theoratical_latency = min_global_latency/(i_t0*j_t0*k_t0/(resource_limits['DSP']/5))
  min_theoratical_off_chip = min_global_off_chip/est_min_off_chip_trans(i_t0, j_t0, k_t0, resource_limits)
  min_theoratical_score = 1
  while(True):
    while(True):
      i_t1_candidates = [i for i in range(1, i_t0+1) if i_t0 % i == 0]
      j_t1_candidates = [j for j in range(1, j_t0+1) if j_t0 % j == 0]
      k_t1_candidates = [k for k in range(1, k_t0+1) if k_t0 % k == 0]
      candidates = []
      for i_t1 in i_t1_candidates:
        for j_t1 in j_t1_candidates:
          for k_t1 in k_t1_candidates:
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

                  if i_t2*j_t2 < 8*k_t2 or k_t2 > 16:
                    continue
                  candidates.append(params)


      num_processes = int(multiprocessing.cpu_count() * 1)
      chunks = list_split(candidates, num_processes)
      pool = multiprocessing.Pool(processes = num_processes)
      results = pool.starmap(run_latency_off_chip_search, [(chunk, resource_limits, num_top_results, min_global_latency, min_global_off_chip, alpha) for chunk in chunks])
      pool.close()
      results = [item for sublist in results for item in sublist]
      results = sorted(results, key=lambda x: x['score'])
      top_results.extend(results[:num_top_results])
      top_results = sorted(top_results, key=lambda x: x['score'])
      top_results = top_results[:num_top_results]

      j_t0 += 1
      min_theoratical_latency = min_global_latency/(i_t0*j_t0*k_t0/(resource_limits['DSP']/5))
      min_theoratical_off_chip = min_global_off_chip/est_min_off_chip_trans(i_t0, j_t0, k_t0, resource_limits)
      beta = 1 - alpha
      min_theoratical_score = 1/(alpha*min_theoratical_latency + beta*min_theoratical_off_chip)
      print(f'candidate ({i_t0}, {j_t0}, {k_t0})','min theoratical score = ', min_theoratical_score, 'current min score = ', top_results[-1]['score'])
      if min_theoratical_score >= top_results[-1]['score']:
        print(j_t0)
        j_t0 = i_t0
        break
    i_t0 += 1
    min_theoratical_latency = min_global_latency/(i_t0*j_t0*k_t0/(resource_limits['DSP']/5))
    min_theoratical_off_chip = min_global_off_chip/est_min_off_chip_trans(i_t0, j_t0, k_t0, resource_limits)
    beta = 1 - alpha
    min_theoratical_score = 1/(alpha*min_theoratical_latency + beta*min_theoratical_off_chip)
    if min_theoratical_score >= top_results[-1]['score']:
      print(i_t0)
      break

  return top_results

def search(I, J, K, objective, num_top_results, alpha):
  prj_path = os.environ['prj_path']
  board_info = json.load(open(prj_path + '/search/u250.json'))
  resource_limits = {'DSP': board_info['DSP']['total']*board_info['DSP']['ratio'], 'BRAM18K': board_info['BRAM18K']['total']*board_info['BRAM18K']['ratio']}
  if objective == 'latency':
    return search_latency(I, J, K, num_top_results, resource_limits)
  elif objective == 'off_chip_comm':
    return search_off_chip(I, J, K, num_top_results, resource_limits)
  elif objective == 'latency_off_chip_comm':
    return search_latency_off_chip(I, J, K, num_top_results, resource_limits, alpha)

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

main()