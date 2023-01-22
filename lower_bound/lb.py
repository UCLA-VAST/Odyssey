from utils import *
from kernel3_2 import *
import multiprocessing
from math import log2, ceil

def get_padded_candidates(n):
	candidates = [x for x in range(1,n)]
	padded_sizes = []
	for i in candidates:
		padded_size = ceil(n/i)*i
		padded_sizes.append(padded_size)
	padded_sizes = list(set(padded_sizes))
	# sort
	padded_sizes.sort()
	return padded_sizes

def search_mm_latency(I, J, K, candidates, resource_limits):
	num_top_results = 1
	top_results = [{'cycles':[np.inf]}]*num_top_results
	for idx in range(len(candidates)):
		i_t1, j_t1, k_t1 = candidates[idx]
		i_t2_candidates = [i for i in range(1, i_t1+1) if i_t1 % i == 0]
		j_t2_candidates = [j for j in range(1, j_t1+1) if j_t1 % j == 0]
		k_t2_candidates = [k for k in range(1, k_t1+1) if k_t1 % k == 0]
		for i_t2 in i_t2_candidates:
			for j_t2 in j_t2_candidates:
				for k_t2 in k_t2_candidates:
					params = {}
					params["i"] = ceil(I / i_t1) * i_t1
					params["j"] = ceil(J / j_t1) * j_t1
					params["k"] = ceil(K / k_t1) * k_t1
					params["i_t1"] = i_t1
					params["j_t1"] = j_t1
					params["k_t1"] = k_t1
					params["i_t2"] = i_t2
					params["j_t2"] = j_t2
					params["k_t2"] = k_t2
					params['p9'] = 1
					params['p10'] = 1
					params['p11'] = 1
					params['p12'] = 1
					# params = infer_params(params)
					# if not bound_check(params):
					# 	continue
					result = {}
					result['resources'] = est_resource(params)
					if result['resources'][0]['DSP'] > resource_limits['DSP'] or result['resources'][0]['BRAM18K'] > resource_limits['BRAM18K']:
						continue
					result['cycles'] = est_latency(params)
					result['params'] = params
					if result['cycles'][0] < top_results[-1]['cycles'][0]:
						for j in range(num_top_results):
							if result['cycles'][0] < top_results[j]['cycles'][0]:
								# insert result into results
								top_results.insert(j, result)
								# remove last element
								top_results.pop()
								break
	return top_results


def search(problem_size, paddable_dims, resource_limits):
		
		I = problem_size['i']
		J = problem_size['j']
		K = problem_size['k']
		
		i_t0, j_t0, k_t0 = I, J, K
		candidates = []
		i_t0_candidates = get_padded_candidates(I)
		j_t0_candidates = get_padded_candidates(J)
		k_t0_candidates = get_padded_candidates(K)
		i_t1_candidates = [i for i in range(1, 2*i_t0) if i in i_t0_candidates or i <= I] if 'i' in paddable_dims else [i for i in range(1, i_t0+1) if i_t0 % i == 0]
		j_t1_candidates = [j for j in range(1, 2*j_t0) if j in j_t0_candidates or j <= J] if 'j' in paddable_dims else [j for j in range(1, j_t0+1) if j_t0 % j == 0]
		k_t1_candidates = [k for k in range(1, 2*k_t0) if k in k_t0_candidates or k <= K] if 'k' in paddable_dims else [k for k in range(1, k_t0+1) if k_t0 % k == 0]
		for i_t1 in i_t1_candidates:
			for j_t1 in j_t1_candidates:
				for k_t1 in k_t1_candidates:
					candidates.append((i_t1, j_t1, k_t1))
		# shuffle candidates
		random.shuffle(candidates)
		# print('Generated %d candidates' % len(candidates))
		num_processes = int(multiprocessing.cpu_count() * 0.5)
		# print('Parallelizing using %d processes...' % (num_processes))
		chunks = list_split(candidates, num_processes)
		pool = multiprocessing.Pool(processes = num_processes)
		results = pool.starmap(search_mm_latency, [(i_t0, j_t0, k_t0, chunk, resource_limits) for idx, chunk in enumerate(chunks)])
		pool.close()
		# flatten results
		results = [item for sublist in results for item in sublist]
		results = sorted(results, key=lambda x: x['cycles'][0])
		return results[0]

def get_DSP_lb(I, J, K, resource_limits):
	def get_latency(params):
		i, j, k, i_t1, j_t1, k_t1, i_t2, j_t2, k_t2, p9, p10, p11, p12 = params["i"], params["j"], params["k"], params["i_t1"], params["j_t1"], params["k_t1"], params["i_t2"], params["j_t2"], params["k_t2"], params["p9"], params["p10"], params["p11"], params["p12"]
		PE_latency = ((i/i_t1)) * ((j/j_t1)) * ((k/k_t1)) * (k_t1/k_t2) * j_t2 * i_t2 * 1
		return PE_latency
	DSP_bound = resource_limits['DSP']
	params = {}
	params['i'] = I
	params['j'] = J
	params['k'] = K
	params['i_t1'] = (DSP_bound/5)**(1/3)
	params['j_t1'] = (DSP_bound/5)**(1/3)
	params['k_t1'] = (DSP_bound/5)**(1/3)
	params['i_t2'] = 1
	params['j_t2'] = 1
	params['k_t2'] = (DSP_bound/5)**(1/3)
	params['p9'] = 1
	params['p10'] = 1
	params['p11'] = 1
	params['p12'] = 1
	cycles = get_latency(params)
	return cycles

def get_BRAM_lb(I, J, K, resource_limits):
	def get_latency(params):
		i, j, k, i_t1, j_t1, k_t1, i_t2, j_t2, k_t2, p9, p10, p11, p12 = params["i"], params["j"], params["k"], params["i_t1"], params["j_t1"], params["k_t1"], params["i_t2"], params["j_t2"], params["k_t2"], params["p9"], params["p10"], params["p11"], params["p12"]
		PE_latency = ((i/i_t1)) * ((j/j_t1)) * ((k/k_t1)) * (k_t1/k_t2) * j_t2 * i_t2 * 1
		return PE_latency
	BRAM_bound = resource_limits['BRAM18K']
	params = {}
	params['i'] = I
	params['j'] = J
	params['k'] = K
	params['i_t1'] = (BRAM_bound/(6*ceil(4*8*1 / 36) / 512))**(1/2)
	params['j_t1'] = (BRAM_bound/(6*ceil(4*8*1 / 36) / 512))**(1/2)
	params['k_t1'] = (BRAM_bound/(6*ceil(4*8*1 / 36) / 512))**(1/2)

	params['i_t2'] = 1
	params['j_t2'] = 1
	params['k_t2'] = 1
	params['p9'] = 1
	params['p10'] = 1
	params['p11'] = 1
	params['p12'] = 1
	cycles = get_latency(params)
	return cycles

resource_limits = get_resource_limits('u250')
resource_limits['BRAM18K'] = 50
I, J, K = 64, 64, 64
paddable_dims = []
actual_cycles_list = []
DSP_lower_cycles_list = []
BRAM_lower_cycles_list = []
x_list = []
for j_t0 in range(J, min(2*J, J+32)):
	i_t0 = I
	k_t0 = K
	print('Running for j_t0 = %d' % j_t0)
	problem_size = {'i':i_t0, 'j':j_t0, 'k':k_t0}
	result = search(problem_size, paddable_dims, resource_limits)
	print(result['resources'][0]['BRAM18K'])
	actual_cycles = result['cycles'][0]
	DSP_lower_cycles = get_DSP_lb(i_t0, j_t0, k_t0, resource_limits)
	BRAM_lower_cycles = get_BRAM_lb(i_t0, j_t0, k_t0, resource_limits)
	x_list.append(j_t0)
	actual_cycles_list.append(actual_cycles)
	DSP_lower_cycles_list.append(DSP_lower_cycles)
	BRAM_lower_cycles_list.append(BRAM_lower_cycles)

from matplotlib import pyplot as plt
# plot points with small dots
plt.scatter(x_list, actual_cycles_list, label='Actual', color='red', marker='o', s=10)
plt.plot(x_list, DSP_lower_cycles_list, label='DSP Lower Bound')
plt.plot(x_list, BRAM_lower_cycles_list, label='BRAM Lower Bound')
plt.xlabel('J')
plt.ylabel('Cycles')
plt.legend()
# save plot
plt.savefig(f'plots/plot_{I}_{J}_{K}.png')