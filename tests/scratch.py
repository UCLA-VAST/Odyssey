import numpy as np

# def get_prime_factors(n):
#   factors = []
#   d = 2
#   while n > 1:
#       while n % d == 0:
#           factors.append(d)
#           n /= d
#       d = d + 1
#   return list(set(factors))
clock_period = 3.33*1e-9
fre = 1/clock_period
DSPs = 8600


peak_perf = (DSPs/5)*2/clock_period #flops/s
peak_perf = peak_perf/1e9 #GFlops/s
bw = (512*3/8)*fre #bytes/second
bw = bw/1e9 #GB/s
print(f'peak perf: {peak_perf} GFLOPS')
print(f'bw: {bw} GB/s')
ctc_points = np.linspace(0.1, 100, 100)
perf_points = bw*ctc_points

# import matplotlib.pyplot as plt
# # plot bw curve
# plt.plot(ctc_points, perf_points)
# # plot peak perf as a horizontal line
# plt.plot([0, 100], [peak_perf/1e9, peak_perf/1e9], '--')
# # save the figure
# plt.savefig('roofline.png')


I, J, K = 64, 64, 64
ops = 2 * I * J * K
min_bytes = (I * J + J * K + I * K)*4
ctc = ops/min_bytes
perf = min(bw*ops/min_bytes, peak_perf)

cycles_1 = ops/(peak_perf*1e9/fre)

cycles_2 = ops/(perf*1e9/fre)
print(f'cycles_1: {8*min_bytes/(512*3)}')
print(f'cycles_2: {ops/((DSPs/5)*2)}')

cycles = max(8*min_bytes/(512*3), ops/((DSPs/5)*2))
print(f'cycles: {cycles}')
# perf_1 = perf_1*1e9
# perf_2 = perf_2*1e9
# print(f'perf_1: {perf_1}')
# print(f'perf_2: {perf_2}')
# perf_1 = perf_1/fre
# perf_2 = perf_2/fre
# print(f'perf_1: {perf_1}')
# print(f'perf_2: {perf_2}')
# cycles_1 = ops/perf_1
# cycles_2 = ops/perf_2
# print(f'cycles_1: {cycles_1}')
# print(f'cycles_2: {cycles_2}')
# min_theoratical_cycles = (ops/2)/(8600/5) #cycles
# min_theoratical_latency = min_theoratical_cycles*3.33*1e-9 #seconds

# # ctc = #ops/bytes
# ctc = ops/((I*J + J*K + I*K)*4)
# # plot roofline model
# import matplotlib.pyplot as plt
# import numpy as np
# # y axis: GOPS/s
# x axis: bytes



# for i in range(1024, 1124):
#   print(i, get_prime_factors(i))

# I, J, K = 128, 128, 128
# ctc = I*J*K / (I*J + J*K + K*I)
# print(ctc)
# I, O, R, C, P, Q = 16, 16, 256, 256, 3, 3
# ctc = I*O*R*C*P*Q / (I*(R+2)*(C+2) + O*R*C + I*P*Q*O)
# print(ctc)

# candidate (1024, 1024, 1024, 1139) min_theoratical_latency =  6398186057 current min_latency =  7740164096
# candidate (1024, 1024, 1024, 1140) min_theoratical_latency =  6403803428 current min_latency =  7740164096
# candidate (1024, 1024, 1024, 1141) min_theoratical_latency =  6409420800 current min_latency =  7740164096
# candidate (1024, 1024, 1024, 1142) min_theoratical_latency =  6415038171 current min_latency =  7740164096
# candidate (1024, 1024, 1024, 1143) min_theoratical_latency =  6420655542 current min_latency =  7740164096
# candidate (1024, 1024, 1024, 1144) min_theoratical_latency =  6426272914 current min_latency =  7740164096
# candidate (1024, 1024, 1024, 1145) min_theoratical_latency =  6431890285 current min_latency =  7740164096
# candidate (1024, 1024, 1024, 1146) min_theoratical_latency =  6437507657 current min_latency =  7740164096
# candidate (1024, 1024, 1024, 1147) min_theoratical_latency =  6443125028 current min_latency =  7740164096
# candidate (1024, 1024, 1024, 1148) min_theoratical_latency =  6448742400 current min_latency =  7740164096
# candidate (1024, 1024, 1024, 1149) min_theoratical_latency =  6454359771 current min_latency =  7740164096
# candidate (1024, 1024, 1024, 1150) min_theoratical_latency =  6459977142 current min_latency =  7740164096
# candidate (1024, 1024, 1024, 1151) min_theoratical_latency =  6465594514 current min_latency =  7740164096


# import matplotlib.pyplot as plt

# min_theoretical_latencies = []
# curr_min_latencies = []
# i_indices = []
# j_indices = []

# input_file = open("out.log", "r").readlines()
# for line in input_file:
#   i, j, min_lat, cur_lat = eval(line)
#   i_indices.append(i)
#   j_indices.append(j)
#   min_theoretical_latencies.append(min_lat)
#   curr_min_latencies.append(cur_lat)
#   # plot the point and color it based on j
#   # darken color as j increases
#   j_color = 1 - (j - 1024) / (1083 - 1024)
#   plt.plot(i, min_lat, 'o', color=(0, j_color, 0), markersize=1)
  # draw horizontal line at cur_lat between i=1024 and i=1046
# plt.plot([1024, 1046], [1052673, 1052673], color='r', linewidth=0.5)
# plt.xlabel('i')
# plt.ylabel('latency')
# plt.savefig('latency_1.png')

# plt.plot([1024, 1046], [706082, 706082], color='r', linewidth=0.5)
# plt.xlabel('i')
# plt.ylabel('latency')
# plt.savefig('latency_2.png')

# plt.plot([1024, 1046], [681572, 681572], color='r', linewidth=0.5)
# plt.xlabel('i')
# plt.ylabel('latency')
# plt.savefig('latency_3.png')

# plt.plot([1024, 1046], [660353, 660353], color='r', linewidth=0.5)
# plt.xlabel('i')
# plt.ylabel('latency')
# plt.savefig('latency_4.png')

# plt.plot([1024, 1046], [639876, 639876], color='r', linewidth=0.5)
# plt.xlabel('i')
# plt.ylabel('latency')
# plt.savefig('latency_5.png')

# plt.plot([1024, 1046], [637832, 637832], color='r', linewidth=0.5)
# plt.xlabel('i')
# plt.ylabel('latency')
# plt.savefig('latency_6.png')