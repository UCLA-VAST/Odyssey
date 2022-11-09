from math import ceil

def get_prime_factors(n):
  factors = []
  for i in range(2, n+1):
    while n % i == 0:
      factors.append(i)
      n /= i
  return list(set(factors))

def get_all_factors(n):
  factors = []
  for i in range(1, n+1):
    if n % i == 0:
      factors.append(i)
  return factors


def get_sorted_padded_candidates(n, limit):
  candidates = [x for x in range(1,limit)]
  padded_sizes = []
  for i in candidates:
    padded_size = ceil(n/i)*i
    # print(i, padded_size)
    padded_sizes.append(padded_size)
  return list(set(padded_sizes))
import math
def isPrime(n):
  if n == 2:
    return True
  if n % 2 == 0 or n <= 1:
    return False
  sqr = int(math.sqrt(n)) + 1
  for divisor in range(3, sqr, 2):
    if n % divisor == 0:
      return False
  return True
divisor_candidates = get_sorted_padded_candidates(1024, 1024)
all_candidates = get_sorted_padded_candidates(1024, 2*1024-1)
other_candidates = [x for x in all_candidates if x not in divisor_candidates]
print(len(divisor_candidates))
print(len(all_candidates))
print(len(other_candidates))
# for i in other_candidates:
#   print(i, isPrime(i))
import numpy as np
import pandas as pd
# df = open('mm_1024.csv', 'r')
df = pd.read_csv('all.csv')
# get padded workload column
padded_workload = df['padded workload']
for pw in padded_workload:
  pw = eval(pw)
  if pw['i'] not in divisor_candidates:
    print('Error: i not in candidates')
    break
exit()
# 16, 16, 16, 4, 2, 8, 4, 1, 4
# 18, 20, 16, 3, 5, 8, 3, 1, 8
# 17, 25, 16, 17, 5, 8, 17, 5, 4
# from math import ceil

# dim = 16
# padded_sizes = get_sorted_padded_candidates(dim)
# all_factors_count = 0
# new_factors_count = 0
# seen_factors = []
# for padded_size in padded_sizes:
#   all_factors = get_all_factors(padded_size)
#   new_factors = [x for x in all_factors if x not in seen_factors]
#   seen_factors.extend(all_factors)
#   seen_factors = list(set(seen_factors))
#   all_factors_count += len(all_factors)
#   new_factors_count += len(new_factors)
#   print(all_factors, new_factors)

# print("All factors: {}".format(all_factors_count))
# print("New factors: {}".format(new_factors_count))
# print("Ratio: {}".format(all_factors_count/new_factors_count))
# print("Squared Ratio: {}".format((all_factors_count**2/new_factors_count**2)))
  # print(padded_size, all_factors, new_factors)
# dim = 64
# all_factors = 0
# new_factors = 0
# primes_set = []
# for i in range(dim, 2*dim):
#   primes = get_all_factors(i)
#   # get elements that are not in primes_set
#   new_primes = [x for x in primes if x not in primes_set]
#   print(i, new_primes)
#   all_factors += len(primes)
#   new_factors += len(new_primes)
#   # if primes is a subset of primes_set, then we can skip
#   # if set(primes).issubset(set(primes_set)):
#   #   continue
#   # else:
#     # print(i)
#   primes_set.extend(primes)
#     # primes_set = list(set(primes_set))
#     # count += 1

# print(all_factors, new_factors)
# print(count)
# exit()

def evaluate():
  return

from math import ceil, log2



design_points = []
I, J, K = 16, 16, 16
i_t1_candidates = [x for x in range(1, 2*I)]
j_t1_candidates = [x for x in range(1, 2*J)]
k_t1_candidates = [x for x in range(1, 2*K) if (log2(x) == int(log2(x)))]
for i_t1 in i_t1_candidates:
  i_t0 = ceil(I/i_t1)*i_t1
  i_t2_candidates = [x for x in range(1, i_t1+1) if i_t1 % x == 0]
  for j_t1 in j_t1_candidates:
    j_t0 = ceil(J/j_t1)*j_t1
    j_t2_candidates = [x for x in range(1, j_t1+1) if j_t1 % x == 0]
    for k_t1 in k_t1_candidates:
      k_t0 = ceil(K/k_t1)*k_t1
      k_t2_candidates = [x for x in range(1, k_t1+1) if k_t1 % x == 0]  
      for i_t2 in i_t2_candidates:
        for j_t2 in j_t2_candidates:
          for k_t2 in k_t2_candidates:
            design_points.append((i_t0, i_t1, i_t2, j_t0, j_t1, j_t2, k_t0, k_t1, k_t2))

print(len(design_points))
design_points = []
# print(len(design_points))

i_t0_candidates = get_sorted_padded_candidates(I) #[16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31]
j_t0_candidates = get_sorted_padded_candidates(J) #[16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31]
k_t0_candidates = [K] #[16]
for i_t0 in i_t0_candidates:
  i_t1_candidates = [x for x in range(1, i_t0+1) if i_t0 % x == 0]
  for j_t0 in j_t0_candidates:
    j_t1_candidates = [x for x in range(1, j_t0+1) if j_t0 % x == 0]
    for k_t0 in k_t0_candidates:
      k_t1_candidates = [x for x in range(1, k_t0+1) if k_t0 % x == 0 and log2(x) == int(log2(x))]
      for i_t1 in i_t1_candidates:
        i_t2_candidates = [x for x in range(1, i_t1+1) if i_t1 % x == 0]
        for j_t1 in j_t1_candidates:
          j_t2_candidates = [x for x in range(1, j_t1+1) if j_t1 % x == 0]
          for k_t1 in k_t1_candidates:
            k_t2_candidates = [x for x in range(1, k_t1+1) if k_t1 % x == 0]  
            for i_t2 in i_t2_candidates:
              for j_t2 in j_t2_candidates:
                for k_t2 in k_t2_candidates:
                  design_points.append((i_t0, i_t1, i_t2, j_t0, j_t1, j_t2, k_t0, k_t1, k_t2))
                  # evaluate((i_t0, i_t1, i_t2, j_t0, j_t1, j_t2, k_t0, k_t1, k_t2))

print(len(design_points))
design_points = []
# print(len(design_points))

def get_new_t1_candidates(t0, t1_seen_candidates):
  t1_candidates = [x for x in range(1, t0+1) if t0 % x == 0]
  t1_candidates = [x for x in t1_candidates if x not in t1_seen_candidates]
  t1_seen_candidates.extend(t1_candidates)
  t1_seen_candidates = list(set(t1_seen_candidates))
  return t1_candidates, t1_seen_candidates


i_t0_candidates = get_sorted_padded_candidates(I)
j_t0_candidates = get_sorted_padded_candidates(J)
k_t0_candidates = [K]
i_t1_seen_candidates = []
for i_t0 in i_t0_candidates:
  i_t1_candidates, i_t1_seen_candidates = get_new_t1_candidates(i_t0, i_t1_seen_candidates)
  j_t1_seen_candidates = []
  for j_t0 in j_t0_candidates:
    j_t1_candidates, j_t1_seen_candidates = get_new_t1_candidates(j_t0, j_t1_seen_candidates)
    k_t1_seen_candidates = []
    for k_t0 in k_t0_candidates:
      k_t1_candidates, k_t1_seen_candidates = get_new_t1_candidates(k_t0, k_t1_seen_candidates)
      for i_t1 in i_t1_candidates:
        i_t2_candidates = [x for x in range(1, i_t1+1) if i_t1 % x == 0]
        for j_t1 in j_t1_candidates:
          j_t2_candidates = [x for x in range(1, j_t1+1) if j_t1 % x == 0]
          for k_t1 in k_t1_candidates:
            k_t2_candidates = [x for x in range(1, k_t1+1) if k_t1 % x == 0]  
            for i_t2 in i_t2_candidates:
              for j_t2 in j_t2_candidates:
                for k_t2 in k_t2_candidates:
                  # evaluate((i_t0, i_t1, i_t2, j_t0, j_t1, j_t2, k_t0, k_t1, k_t2))
                  design_points.append((i_t0, j_t0, k_t0, i_t1, j_t1, k_t1, i_t2, j_t2, k_t2))

print(len(design_points))

i_t0_candidates = get_sorted_padded_candidates(I)
j_t0_candidates = get_sorted_padded_candidates(J)
k_t0 = K
min_cycles = inf
opt_params = None
for i_t0 in i_t0_candidates:
  for j_t0 in j_t0_candidates:
    results = actual_min_cycles(i_t0, j_t0, k_t0)
    top_results = get_top_results(results, n)

min_cycles = inf
opt_params = None
k_t0 = K
for i_t0 in i_t0_candidates:
  for j_t0 in j_t0_candidates:
    # if the last design in top resuls is better than the lower bound
    if theoretical_min_cycles(i_t0, j_t0, k_t0) < top_results[-1]:
      break
    results = actual_min_cycles(i_t0, j_t0, k_t0)
    top_results = get_top_results(results, n)

def theoretical_min_cycles(i_t0, j_t0, k_t0):
  return MP_solver(i_t0, j_t0, k_t0)

threshold = 10 # 1 <= threshold <= 2*problem size
k_t0 = K

for i_t0 in i_t0_candidates:
  for j_t0 in j_t0_candidates:
    results = actual_min_cycles(i_t0, j_t0, k_t0)
    top_results, is_j_updated = get_top_results(results, n)
