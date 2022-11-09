
import numpy as np
# 256 x 256



def infer_params(i, j, k, i_t1, j_t1, k_t1, i_t2, j_t2, k_t2):

	p9_choices = [n*k_t2 for n in range(1, max(min(k_t1,16),k_t2)//k_t2+1) if max(min(k_t1,16),k_t2)%(n*k_t2)==0]
	if len(p9_choices) == 0:
		return None
	p9 = max(p9_choices)
	p10_choices = [n*k_t2 for n in range(1, max(min(k_t1,16),k_t2)//k_t2+1) if max(min(k_t1,16),k_t2)%(n*k_t2)==0]
	if len(p10_choices) == 0:
		return None
	p10 = max(p10_choices)
	p11_choices = [n*1 for n in range(1, max(min(j_t2,4),1)//1+1) if max(min(j_t2,4),1)%(n*1)==0]
	if len(p11_choices) == 0:
		return None
	p11 = max(p11_choices)
	p12_choices = [n*1 for n in range(1, max(min(j_t2,4),1)//1+1) if max(min(j_t2,4),1)%(n*1)==0]
	if len(p12_choices) == 0:
		return None
	p12 = max(p12_choices)

	return p9, p10, p11, p12

def filter_non_power_of_two(x):
    if np.log2(x) != int(np.log2(x)):
        return True
    return False

def bound_check(i, j, k, i_t1, j_t1, k_t1, i_t2, j_t2, k_t2):

    p9, p10, p11, p12 = infer_params(i, j, k, i_t1, j_t1, k_t1, i_t2, j_t2, k_t2)
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
        


# def est_latency(i, j, k, i_t1, j_t1, k_t1, i_t2, j_t2, k_t2):
# 	# i, j, k, i_t1, j_t1, k_t1, i_t2, j_t2, k_t2, p9, p10, p11, p12 = params["i"], params["j"], params["k"], params["i_t1"], params["j_t1"], params["k_t1"], params["i_t2"], params["j_t2"], params["k_t2"], params["p9"], params["p10"], params["p11"], params["p12"]
#     p9, p10, p11, p12 = infer_params(i, j, k, i_t1, j_t1, k_t1, i_t2, j_t2, k_t2)
#     A_IO_L2_in_single_latency = ((i_t1/i_t2) * (i_t2*k_t1/p9) + 1)
#     A_IO_L3_in_single_latency = (i_t1/i_t2) * (i_t2*k_t1/min(p9, 512/8/4))
#     B_IO_L2_in_single_latency = ((j_t1/j_t2) * (j_t2*k_t1/p10) + 1)
#     B_IO_L3_in_single_latency = (j_t1/j_t2) * (j_t2*k_t1/min(p10, 512/8/4))
#     latency_prologue = max(A_IO_L2_in_single_latency, A_IO_L3_in_single_latency, B_IO_L2_in_single_latency, B_IO_L3_in_single_latency)
    
#     C_drain_IO_L1_out_single_latency = (i_t1/i_t2) * (i_t2*j_t2/p12)
#     C_drain_IO_L2_out_single_latency = (j_t1/j_t2) * (i_t1/i_t2) * (i_t2*j_t2/p12)
#     C_drain_IO_L3_out_single_latency = (j_t1/j_t2) * (i_t1/i_t2) * (i_t2*j_t2/min(p12, 512/8/4))
#     latency_epilogue = max(C_drain_IO_L1_out_single_latency, C_drain_IO_L2_out_single_latency, C_drain_IO_L3_out_single_latency)
    
#     A_IO_L2_in_latency = ((i/i_t1)) * ((j/j_t1)) * ((k/k_t1)) * (max((i_t1/i_t2) * (i_t2*k_t1/p9), (k_t1/k_t2) * j_t2 * i_t2 * 1) + 1)
#     A_IO_L3_in_latency = ((i/i_t1)) * ((j/j_t1)) * ((k/k_t1)) * (i_t1/i_t2) * (i_t2*k_t1/min(p9, 512/8/4))
#     B_IO_L2_in_latency = ((i/i_t1)) * ((j/j_t1)) * ((k/k_t1)) * (max((j_t1/j_t2) * (j_t2*k_t1/p10), (k_t1/k_t2) * j_t2 * i_t2 * 1) + 1)
#     B_IO_L3_in_latency = ((i/i_t1)) * ((j/j_t1)) * ((k/k_t1)) * (j_t1/j_t2) * (j_t2*k_t1/min(p10, 512/8/4))
#     C_drain_IO_L1_out_latency = ((i/i_t1)) * ((j/j_t1)) * ((i_t1/i_t2) * (i_t2*j_t2/p12) + j_t2 * i_t2 * 1)
#     C_drain_IO_L2_out_latency = ((i/i_t1)) * ((j/j_t1)) * (j_t1/j_t2) * (i_t1/i_t2) * (i_t2*j_t2/p12)
#     C_drain_IO_L3_out_latency = ((i/i_t1)) * ((j/j_t1)) * (j_t1/j_t2) * (i_t1/i_t2) * (i_t2*j_t2/min(p12, 512/8/4))
#     PE_latency = ((i/i_t1)) * ((j/j_t1)) * ((k/k_t1)) * (k_t1/k_t2) * j_t2 * i_t2 * 1
#     latency_main = max(A_IO_L2_in_latency, A_IO_L3_in_latency, B_IO_L2_in_latency, B_IO_L3_in_latency, C_drain_IO_L1_out_latency, C_drain_IO_L2_out_latency, C_drain_IO_L3_out_latency, PE_latency)
    
#     return latency_prologue + latency_main + latency_epilogue


def est_latency(i, j, k, i_t1, j_t1, k_t1, i_t2, j_t2, k_t2):
	# i, j, k, i_t1, j_t1, k_t1, i_t2, j_t2, k_t2, p9, p10, p11, p12 = params["i"], params["j"], params["k"], params["i_t1"], params["j_t1"], params["k_t1"], params["i_t2"], params["j_t2"], params["k_t2"], params["p9"], params["p10"], params["p11"], params["p12"]
    p9, p10, p11, p12 = infer_params(i, j, k, i_t1, j_t1, k_t1, i_t2, j_t2, k_t2)
    A_IO_L2_in_single_latency = i_t1 * k_t1/p9 + 1
    A_IO_L3_in_single_latency = i_t1 * k_t1/min(p9, 512/8/4)
    B_IO_L2_in_single_latency = j_t1*k_t1/p10 + 1
    B_IO_L3_in_single_latency = j_t1 * k_t1/min(p10, 512/8/4)
    latency_prologue = max(A_IO_L2_in_single_latency, A_IO_L3_in_single_latency, B_IO_L2_in_single_latency, B_IO_L3_in_single_latency)
    # print(1,A_IO_L2_in_single_latency, A_IO_L3_in_single_latency, B_IO_L2_in_single_latency, B_IO_L3_in_single_latency)
    
    C_drain_IO_L1_out_single_latency = i_t1 * j_t2/p12
    C_drain_IO_L2_out_single_latency = j_t1 * i_t1/p12
    C_drain_IO_L3_out_single_latency = j_t1 * (i_t1/min(p12, 512/8/4))
    latency_epilogue = max(C_drain_IO_L1_out_single_latency, C_drain_IO_L2_out_single_latency, C_drain_IO_L3_out_single_latency)
    # print(2, C_drain_IO_L1_out_single_latency, C_drain_IO_L2_out_single_latency, C_drain_IO_L3_out_single_latency)

    # ri = 
    
    A_IO_L2_in_latency = ((i/i_t1)) * ((j/j_t1)) * ((k/k_t1)) * (max((i_t1) * (k_t1/p9), (k_t1/k_t2) * j_t2 * i_t2 * 1) + 1)
    A_IO_L3_in_latency = i * j/j_t1 * k/min(p9, 512/8/4)
    B_IO_L2_in_latency = i/i_t1 * j/j_t1 * k/k_t1 * (max((j_t1/j_t2) * (j_t2*k_t1/p10), (k_t1/k_t2) * j_t2 * i_t2 * 1) + 1)
    B_IO_L3_in_latency = i/i_t1 * j * k/min(p10, 512/8/4)
    C_drain_IO_L1_out_latency = ((i/i_t1)) * ((j/j_t1)) * ((i_t1) * (j_t2/p12) + j_t2 * i_t2 * 1)
    C_drain_IO_L2_out_latency = ((i/i_t1)) * ((j)) * (i_t1/p12)
    C_drain_IO_L3_out_latency = i * j/min(p12, 512/8/4)
    PE_latency = i/i_t1 * j/j_t1 * k/k_t2 * j_t2 * i_t2 * 1
    latency_main = max(A_IO_L2_in_latency, A_IO_L3_in_latency, B_IO_L2_in_latency, B_IO_L3_in_latency, C_drain_IO_L1_out_latency, C_drain_IO_L2_out_latency, C_drain_IO_L3_out_latency, PE_latency)
    # print(3,A_IO_L2_in_latency, A_IO_L3_in_latency, B_IO_L2_in_latency, B_IO_L3_in_latency, C_drain_IO_L1_out_latency, C_drain_IO_L2_out_latency, C_drain_IO_L3_out_latency, PE_latency)
    
    # print(4, latency_prologue, latency_main, latency_epilogue)
    return latency_prologue + latency_main + latency_epilogue


def find_all_divisor(x):
    res = []
    for i in range(1, x+1):
        if x % i == 0:
            res.append(i)
    return res

def find_all_multiple_and_divisor(x, N):
    #find all multiple and divisor of x that is smaller than N
    res = []
    for i in range(1, N+1):
        # print(i, x%i==0, i%x==0)
        if i % x == 0 or x % i == 0:
            res.append(i)
    return res

def find_all_divisor_and_equal(x, N):
    #find all divisor of x such that the divisor times x == N
    res = []
    for i in range(1, x+1):
        if x % i == 0 and x/i == N:
            res.append(i)
    return res

def find_padind(x, x_t1):
    for k in range(0, x*x_t1):
        if (x + k)%x_t1 == 0:
            return k

count = 0

import time

min_lat = float("inf")

t1 = time.time()

I = 1024
J = 1024
K = 1024

from joblib import Parallel, delayed
def process(i):
    return i * i



def suhail(x1):
    min_lat = float("inf")
    min_i_t1 = float("inf")
    min_j_t1 = float("inf")
    min_k_t1 = float("inf")
    min_i_t2 = float("inf")
    min_j_t2 = float("inf")
    min_k_t2 = float("inf")
    # for x2 in range(1,73):
    for x2 in [43]:
        # it1/it2 = x1
        # jt1/jt2 = x2
        b_it1 = find_all_multiple_and_divisor(x1, I)
        for i_t1 in b_it1:
            for j_t1 in find_all_multiple_and_divisor(x2, J):
                for i_t2 in find_all_divisor_and_equal(i_t1, x1):
                    for j_t2 in find_all_divisor_and_equal(j_t1, x2):

                        for k_t1 in find_all_divisor(K):
                            for k_t2 in find_all_divisor(k_t1):
                                # print all iterators
                                # print(i_t1, i_t2, j_t1, j_t2, k_t1, k_t2)
                                # count += 1
                                if bound_check(I + find_padind(I, i_t1), J + find_padind(J, j_t1), K, i_t1, j_t1, k_t1, i_t2, j_t2, k_t2):

                                    latency = est_latency(I + find_padind(I, i_t1), J + find_padind(J, j_t1), K, i_t1, j_t1, k_t1, i_t2, j_t2, k_t2)

                                    if latency < min_lat and ((i_t1/i_t2)*(j_t1/j_t2)) * k_t2 * 5 <= 8600:
                                        min_lat = latency
                                        min_i_t1 = i_t1
                                        min_j_t1 = j_t1
                                        min_k_t1 = k_t1
                                        min_i_t2 = i_t2
                                        min_j_t2 = j_t2
                                        min_k_t2 = k_t2

                                        print("i_t1: {}, j_t1: {}, k_t1: {}, i_t2: {}, j_t2: {}, k_t2: {}, latency: {}".format(i_t1, j_t1, k_t1, i_t2, j_t2, k_t2, latency))
                                        print("i: {}, j: {}, k: {}".format(I + find_padind(I, i_t1), J + find_padind(J, j_t1), K))
                                        print("x1: {}, x2: {}".format(x1, x2))
                                        print("")
    return min_lat, min_i_t1, min_j_t1, min_k_t1, min_i_t2, min_j_t2, min_k_t2
    
# results = Parallel(n_jobs=72)(delayed(suhail)(i) for i in range(1,73))
# print(results)  # prints [0, 1, 4, 9, 16, 25, 36, 49, 64, 81]
suhail(5)

# print(find_all_multiple_and_divisor(5, 1024))

# for x1 in range(1,256):
#     for x2 in range(1,256):
#         # it1/it2 = x1
#         # jt1/jt2 = x2
#         b_it1 = find_all_multiple_and_divisor(x1, I)
#         for i_t1 in b_it1:
#             for j_t1 in find_all_multiple_and_divisor(x2, J):
#                 for i_t2 in find_all_divisor_and_equal(i_t1, x1):
#                     for j_t2 in find_all_divisor_and_equal(j_t1, x2):

#                         for k_t1 in find_all_divisor(K):
#                             for k_t2 in find_all_divisor(k_t1):
#                                 # print all iterators
#                                 # print(i_t1, i_t2, j_t1, j_t2, k_t1, k_t2)
#                                 # count += 1

#                                 latency = est_latency(I + find_padind(I, i_t1), J + find_padind(J, j_t1), K, i_t1, j_t1, k_t1, i_t2, j_t2, k_t2)

#                                 if latency < min_lat and ((i_t1/i_t2)*(j_t1/j_t2)) * k_t2 * 5 <= 8600:
#                                     min_lat = latency
#                                     print("i_t1: {}, j_t1: {}, k_t1: {}, i_t2: {}, j_t2: {}, k_t2: {}, latency: {}".format(i_t1, j_t1, k_t1, i_t2, j_t2, k_t2, latency))
#                                     print("i: {}, j: {}, k: {}".format(I + find_padind(I, i_t1), J + find_padind(J, j_t1), K))
#                                     print("x1: {}, x2: {}".format(x1, x2))
#                                     print("")

t2 = time.time()

print(t2-t1)
print(count)

# mini = float("inf")
# min_i_t1 = float("inf")
# min_j_t1 = float("inf")
# min_k_t1 = float("inf")
# min_i_t2 = float("inf")
# min_j_t2 = float("inf")
# min_k_t2 = float("inf")


# for i_t1 in range(1,1024):
#     for i_t2 in find_all_divisor(i_t1):
#         for j_t1 in range(1,1024):
#             for j_t2 in find_all_divisor(j_t1):
#                 for k_t1 in find_all_divisor(1024):
#                     if 1024%k_t1 == 0:
#                         if k_t1 % 8 == 0:
#                             if i_t1/i_t2 == 5:
#                                 if j_t1/j_t2 == 43:
#                                     if ((i_t1/i_t2)*(j_t1/j_t2)) * 8 * 5 <= 8600:
#                                         if est_latency(1032, 1032, 1024, i_t1, j_t1, k_t1, i_t2, j_t2, 8) < mini:
#                                             mini = est_latency(1032, 1032, 1024, i_t1, j_t1, k_t1, i_t2, j_t2, 8)
#                                             min_i_t1 = i_t1
#                                             min_i_t2 = i_t2
#                                             min_j_t1 = j_t1
#                                             min_j_t2 = j_t2
#                                             min_k_t1 = k_t1
#                                             print("i_t1: {}, j_t1: {}, k_t1: {}, i_t2: {}, j_t2: {}, k_t2: {}, latency: {}".format(i_t1, j_t1, k_t1, i_t2, j_t2, 8, mini))

