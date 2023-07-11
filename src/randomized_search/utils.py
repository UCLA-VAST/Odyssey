import time
import functools
import math
import logging
import itertools
from datetime import datetime
from subprocess import Popen, PIPE
import json
import pprint
import queue
import multiprocessing as mp
from pathos.pools import ProcessPool, ParallelPool
import copy
import os
import re
import importlib
from math import ceil, prod


prj_path = os.environ["PRJ_PATH"]

designs_lib_dir = prj_path + f'/data/designs_lib'
designs_dir = prj_path + '/tests/tmp/designs'
output_dir = prj_path + '/tests/tmp/outputs'

def copy_design(design, workload, permutation):
	os.system(f'cp {designs_lib_dir}/{workload}_{permutation}/{design} {designs_dir}')

def get_SA_sizes(sa_info, solution, workload):
	array_part = sa_info['array_part']
	latency_hiding = sa_info['latency_hiding']
	simd = sa_info['simd']
	# print(f'array_part: {array_part}')
	# print(f'latency_hiding: {latency_hiding}')
	# print(f'simd: {simd}')
	arch_sol = solution['arch_sol']
	space_time_mapping = sa_info['idx']
	array_part_sol = [arch_sol[ap] for ap in array_part]
	latency_hiding_sol = [arch_sol[lat] for lat in latency_hiding]
	simd_sol = [arch_sol[sim] for sim in simd]

	for idx in range(len(latency_hiding_sol)):
		ap = int(array_part_sol[idx])
		lh = int(latency_hiding_sol[idx])
		if ap // lh == 1:
			simd_sol.insert(0, 1)
	if workload == 'conv':
		simd_sol.insert(0, 3)
		simd_sol.insert(0, 3)
	sa_sizes = '"{kernel[]->space_time[' + space_time_mapping + '];kernel[]->array_part' + str(array_part_sol) + ';kernel[]->latency' + str(latency_hiding_sol) + ';kernel[]->simd' + str(simd_sol) + '}"'
	return sa_sizes

def get_SA_info(design):
	with open(f'{designs_dir}/{design}', 'r') as f:
		all_info = json.load(f)
	arch_info = all_info['compute']['PE']
	sa_info = {}
	sa_info['idx'] = re.split('kernel|_|\.|json', design)[1]
	sa_info['arch'] = {}
	sa_info['arch']['dims'] = len(arch_info['dims'])
	sa_info['arch']['simd'] = arch_info['unroll_factor']
	if sa_info['arch']['dims'] == 1:
		sa_info['arch']['sa_length'] = arch_info['dims'][0]
		sa_info['padding_dims'] = [arch_info['dims'][0][1]]
	elif sa_info['arch']['dims'] == 2:
		sa_info['arch']['sa_cols'] = arch_info['dims'][0]
		sa_info['arch']['sa_rows'] = arch_info['dims'][1]
		sa_info['padding_dims'] = [arch_info['dims'][0][1], arch_info['dims'][1][1]]

	SA_params = all_info['params']
	array_part = []
	latency_hiding = []    
	simd = []
	for param in SA_params:
		if param['attr'] == 'array_part_tiling_factor':
			array_part.append(param['name'])
		elif param['attr'] == 'latency_tiling_factor':
			latency_hiding.append(param['name'])
		elif param['attr'] == 'SIMD_tiling_factor':
			simd.append(param['name'])
	sa_info['array_part'] = array_part
	sa_info['latency_hiding'] = latency_hiding
	sa_info['simd'] = simd
	return sa_info

def print_solution(idx, design, solution, sa_info, objective, workload, elapsed_time, all_designs, valid_designs, csv_path):
	file_path = 'tmp/designs/register/' + design.strip('.json')
	file_path = file_path.replace('/', '.')
	model = importlib.import_module(file_path)
	compute_arch_cst = model.compute_arch_cst

	original_workload_size = {}
	padded_workload_size = {}
	padding_dims = sa_info['padding_dims']
	# get elements from dictionary solution['arch_sol'] whose key ends with t1
	# and store them in t1_dims
	for dim in solution['arch_sol'].keys():
		if len(dim) == 1:
			original_workload_size[dim] = solution['arch_sol'][dim]
	t1_dims = {k:v for k, v in solution['arch_sol'].items() if k.endswith('t1')}
	for dim in solution['arch_sol'].keys():
		if dim in padding_dims:
			# get key and value from t1_dims if dim is in key
			t1_dim = [v for k, v in t1_dims.items() if dim in k][0]
			padded_workload_size[dim] = ceil(solution['arch_sol'][dim]/t1_dim)*t1_dim
	# for key in original_workload_size.keys():
	# 	if key not in padded_workload_size.keys():
	# 		padded_workload_size[key] = original_workload_size[key]
	# sort padded_workload_size by key
	padded_workload_size = dict(sorted(padded_workload_size.items()))
	# sort original_workload_size by key
	original_workload_size = dict(sorted(original_workload_size.items()))
	fre = solution['fre']
	throughput = solution['throughput']
	cycles = solution['cycles']
	latency = solution['latency']
	dsp_eff = solution['dsp_eff']
	off_chip_bytes = solution['off_chip_bytes']
	bandwidth = solution['bandwidth']
	CTC = solution['CTC']
	DSPs = solution['DSPs']
	BRAMs = solution['BRAMs']
	arch = compute_arch_cst(solution['arch_sol'])
	array_part_mapping = eval(open(f'{prj_path}/data/autosa_mappings/{workload}_array_part.csv').readlines()[int(sa_info['idx'])])
	latency_hiding_mapping = eval(open(f'{prj_path}/data/autosa_mappings/{workload}_latency_hiding.csv').readlines()[int(sa_info['idx'])])
	if len(arch['dims']) == 1:
		if array_part_mapping[0] not in latency_hiding_mapping:
			SA_Dims = '"' + str((int(arch['dims'][0])*int(arch['SIMD']), 1)) + '"'
			PEs = int(arch['dims'][0])*int(arch['SIMD'])
		else:
			SA_Dims = '"' + str((int(arch['dims'][0]), int(arch['SIMD']))) + '"'
			PEs = prod(arch['dims'])
	elif len(arch['dims']) == 2:
		if array_part_mapping[1] not in latency_hiding_mapping:
			SA_Dims = '"' + str((int(arch['dims'][0]), int(arch['dims'][1])*int(arch['SIMD']), 1)) + '"'
			PEs = int(arch['dims'][0])*int(arch['dims'][1])*int(arch['SIMD'])
		else:
			SA_Dims = '"' + str((int(arch['dims'][0]), int(arch['dims'][1]), int(arch['SIMD']))) + '"'
			PEs = prod(arch['dims'])

	sa_sizes = get_SA_sizes(sa_info, solution, workload)
	params = solution['arch_sol']
	# sort params by key
	params = dict(sorted(params.items()))
	csv_file = open(csv_path, 'a')
	print(f'{design.split(".")[0]}_{idx},', end='', file=csv_file)
	# print(f'{elapsed_time:.1f},', end='', file=csv_file)
	print(f'{objective},', end='', file=csv_file)
	print(f'"{original_workload_size}",', end='', file=csv_file)
	print(f'"{padded_workload_size}",', end='', file=csv_file)
	print(f'{fre:.0f},', end='', file=csv_file)
	print(f'{throughput:.2f},', end='', file=csv_file)
	print(f'{cycles:.0f},', end='', file=csv_file)
	print(f'{latency:.5f},', end='', file=csv_file)
	print(f'{dsp_eff:.2f}%,', end='', file=csv_file)
	print(f'{off_chip_bytes:.0f},', end='', file=csv_file)
	print(f'{bandwidth:.2f},', end='', file=csv_file)
	print(f'{CTC:.2f},', end='', file=csv_file)
	print(f'{DSPs:.0f},', end='', file=csv_file)
	print(f'{BRAMs:.0f},', end='', file=csv_file)
	print(f'{PEs:.0f},', end='', file=csv_file)
	print(f'{SA_Dims},', end='', file=csv_file)
	print(f'{elapsed_time:.1f},', end='', file=csv_file)
	print(f'{all_designs:_.0f},', end='', file=csv_file)
	print(f'{valid_designs:_.0f},', end='', file=csv_file)
	print(f'{(all_designs/elapsed_time):_.0f},', end='', file=csv_file)
	print(f'{(valid_designs/elapsed_time):_.0f},', end='', file=csv_file)
	print(f'{sa_sizes},', end='', file=csv_file)
	print(f'"{params}"', end='', file=csv_file)
	print(file=csv_file)
	csv_file.close()
	return

def factorization(x):
    if x == 0:
        raise RuntimeError(f"Factorization of 0")
    prime_factors = []
    while x % 2 == 0:
        prime_factors.append(2)
        x = x / 2
    
    for i in range(3, int(math.sqrt(x)) + 1, 2):
        while x % i == 0:
            prime_factors.append(int(i))
            x = x / i
    
    if x > 2:
        prime_factors.append(int(x))

    return prime_factors

def get_divisors(x, filter=None):
    """ Return the divisors of the integer x
    Call the filter function to filter out the illegal one.
    """
    divisors = []
    large_divisors = []
    for i in range(1, int(math.sqrt(x) + 1)):
        if x % i == 0:
            if (filter and not filter(i)) or not filter:
                divisors.append(int(i))
            if i * i != x:
                if (filter and not filter(int(x / i))) or not filter:
                    large_divisors.append(int(x / i))
    for d in reversed(large_divisors):
        divisors.append(d)

    return divisors

def compute_tasks_latency(search_tasks, init_tasks):
    """ Aggregate the best latency of the search tasks.
    """
    # Collect the best single task latency
    task_latency = {}
    for task in search_tasks:
        found = False
        cur_latency = []
        task_prefix = str(task)[:str(task).find('d')]
        for i_task in init_tasks:
            if len(i_task.task_sols) == 1:
                i_task_prefix = i_task.task_sols[0]['hash']
                i_task_prefix = i_task_prefix[:i_task_prefix.find('d')]
                if i_task_prefix == task_prefix:
                    found = True
                    cur_latency.append(i_task.task_sols[0]['latency'])
        if not found:
            #raise RuntimeError(f"Task {str(task)} not found in the history.")
            return None
        task_latency[task.workload["name"]] = min(cur_latency)
    
    # Init tasks may contain fused tasks.
    # If the fused tasks help improve the latency, we will replace the old 
    # unfused task pairs with the fused tasks.
    for i_task in init_tasks:
        if len(i_task.task_sols) > 1:
            unfused_latency = 0
            for name in i_task.task_names:
                if name not in task_latency:
                    # This task has been handled by other fusion tasks
                    unfused_latency = 0
                    break
                unfused_latency += task_latency[name]
            if i_task.latency < unfused_latency:
                task_latency[''.join(i_task.task_names)] = i_task.latency
                for name in i_task.task_names:
                    del task_latency[name]

    latency = 0
    for k, v in task_latency.items():
        latency += v

    return latency

class PerfCounter(object):
    def __init__(self, logger=None):
        self.logger = logger
        self.counters = {}
    
    def init_counter(self, name):        
        self.counters[name] = {'start': time.perf_counter(), 'elapsed': 0}
        
    def update_counter(self, name):
        if name not in self.counters:
            raise RuntimeError(f"Counter {name} is not defined")
        now = time.perf_counter()
        self.counters[name]['elapsed'] += (now - self.counters[name]['start'])
        self.counters[name]['start'] = now

    def get_counter(self, name):
        if name not in self.counters:
            raise RuntimeError(f"Counter {name} is not defined")
        return self.counters[name]['elapsed']

    def print_counter(self, name):
        if name not in self.counters:
            raise RuntimeError(f"Counter {name} is not defined")
        if not self.logger:
            raise RuntimeError(f"Logger is not defined")
        self.logger.info(f'[Event: {name}] Total elapsed time: {self.counters[name]["elapsed"]:.4f} s')

    def print_counters(self):
        if not self.logger:
            raise RuntimeError(f"Logger is not defined")
        for name in self.counters:
            self.logger.info(f'[Event: {name}] Total elapsed time: {self.counters[name]["elapsed"]:.4f} s')    

def init_logger(outdir):	
    logger = logging.getLogger('AutoSA-Tuner')
    # If there is already any handlers, remove them	
    for handler in logger.handlers[:]:
        handler.close()
        logger.removeHandler(handler)
    formatter = logging.Formatter(
                '[%(name)s %(asctime)s] %(levelname)s: %(message)s',
                '%Y-%m-%d %H:%M:%S')
    logger.setLevel(logging.INFO)
    s_handler = logging.StreamHandler()    	
    f_handler = logging.FileHandler(f'{outdir}/tuning.log', 'a')
    s_handler.setLevel(level=logging.INFO)
    f_handler.setLevel(level=logging.INFO)    
    s_handler.setFormatter(formatter)
    f_handler.setFormatter(formatter)
    logger.addHandler(s_handler)
    logger.addHandler(f_handler)
    
    return logger    

class SearchRecord(object):
    """ Data struct for storing the searching results
    """
    def __init__(self, max=1):
        self.cst = None
        self.max = max
        if self.max == 1:
            self.reward = 0
        else:
            self.reward = float("inf")
        self.reward_meta = None
        self.latency = 0
        self.throughput = 0
        self.energy = 0
        self.dsp_eff = 0
        self.design = None
        self.ops = 0
        self.task_names = []
        self.metric = None
        self.fuse = -1
        self.split_pos = -1
        self.partition = None
        self.n_array = -1
        self.bw = 0
        self.ctc = 0
        self.exec_model = []
        self.converge_time = 0
        # Design frequency
        self.fre = 300 
        self.off_chip_trans = 0
        self.dw = 4 # Float
        self.valid = 0        
        
        # Fixed array architecture solution
        self.arch_sol = None
        # Mapped tasks solutions
        self.task_sols = []
        # Sub task records
        self.records = None
        self.history = []

    def reset(self):
        self.cst = None        
        if self.max == 1:
            self.reward = 0
        else:
            self.reward = float("inf")
        self.reward_meta = None
        self.latency = 0
        self.throughput = 0
        self.energy = 0
        self.dsp_eff = 0
        self.design = None
        self.ops = 0
        self.task_names = []
        self.metric = None
        self.fuse = -1
        self.split_pos = -1
        self.partition = None
        self.n_array = -1
        self.bw = 0
        self.ctc = 0
        self.exec_model = []
        self.converge_time = 0
        # Design frequency
        self.fre = 300 
        self.off_chip_trans = 0
        self.valid = 0

        self.arch_sol = None
        self.task_sols = []
        self.records = None        
        self.history = []

        return self

    def update(self, new_record, save=0):  
        """ Update the old records if new record is better.
        If "save" is set to 1, store the current record to history.
        """
        if new_record.valid == 0:
            return False

        if self.max != new_record.max:
            raise RuntimeError("Inconsistent search record configuration")
        status = False
        if self.max == 1:
            if new_record.reward > self.reward:				
                status = True
        else:
            if new_record.reward < self.reward:
                status = True
        if status:
            self.cst = copy.deepcopy(new_record.cst)
            self.reward = new_record.reward
            self.reward_meta = copy.deepcopy(new_record.reward_meta)
            self.latency = new_record.latency
            self.throughput = new_record.throughput
            self.energy = new_record.energy
            self.dsp_eff = new_record.dsp_eff
            self.design = new_record.design            
            self.ops = new_record.ops
            self.task_names = new_record.task_names
            self.fuse = new_record.fuse
            self.split_pos = new_record.split_pos
            self.partition = new_record.partition
            self.n_array = new_record.n_array
            self.bw = new_record.bw
            self.ctc = new_record.ctc
            self.exec_model = new_record.exec_model
            self.metric = new_record.metric
            self.converge_time = new_record.converge_time
            self.off_chip_trans = new_record.off_chip_trans
            self.valid = new_record.valid            

            self.arch_sol = new_record.arch_sol
            self.task_sols = new_record.task_sols
            self.records = new_record.records
        
        if save == 1:
            self.history.append(new_record)

        return status

    def dup(self):
        """ Duplicate the current record.
        """
        new_record = SearchRecord()
        new_record.cst = copy.deepcopy(self.cst)
        new_record.max = self.max
        new_record.reward = self.reward
        new_record.reward_meta = self.reward_meta
        new_record.latency = self.latency
        new_record.throughput = self.throughput
        new_record.energy = self.energy
        new_record.dsp_eff = self.dsp_eff
        new_record.design = self.design
        new_record.ops = self.ops
        new_record.task_names = copy.deepcopy(self.task_names)
        new_record.metric = self.metric
        new_record.fuse = self.fuse
        new_record.split_pos = self.split_pos
        new_record.partition = self.partition
        new_record.n_array = self.n_array
        new_record.bw = self.bw
        new_record.ctc = self.ctc
        new_record.exec_model = copy.deepcopy(self.exec_model)
        new_record.converge_time = self.converge_time
        new_record.off_chip_trans = self.off_chip_trans
        new_record.valid = self.valid
        new_record.arch_sol = copy.deepcopy(self.arch_sol)
        new_record.task_sols = copy.deepcopy(self.task_sols)
        if self.records:
            new_record.records = []
            for record in self.records:
                new_record.records.append(record.dup())
        
        return new_record

    def extract_from_tuner_single_acc(self, tuner):
        """ Extract the sinlge accelerator search results from the tuner.
        """
        if tuner.best_sol:
            self.cst = tuner.best_sol_cst
            self.reward = tuner.best_reward
            self.reward_meta = tuner.best_reward_meta
            self.ops = tuner.search_task.compute_ops()
            if tuner.search_obj == "latency":
                self.latency = 1 / self.reward
                self.throughput = self.ops / self.latency
                # Compute the updated DSP efficiency
                # Note: Only applicable for FP32
                self.dsp_eff = tuner.search_task.compute_dsp_eff(self.latency, self.cst["DSP"])
            elif tuner.search_obj in ["off_chip_comm", "dsp_num"]:
                self.latency = self.reward_meta["latency"]["latency"]
                self.throughput = self.ops / self.latency
                self.dsp_eff = tuner.search_task.compute_dsp_eff(self.latency, self.cst["DSP"])
            elif tuner.search_obj == "energy":
                self.energy = 1 / self.reward
                self.latency = self.reward_meta["latency"]["latency"]
                self.throughput = self.ops / self.latency
                self.dsp_eff = tuner.search_task.compute_dsp_eff(self.latency, self.cst["DSP"])
            elif tuner.search_obj == "latency_off_chip":
                self.latency = self.reward_meta["latency"]["latency"]
                self.throughput = self.ops / self.latency
                self.dsp_eff = tuner.search_task.compute_dsp_eff(self.latency, self.cst["DSP"])
            else:
                raise RuntimeError("Unsupported search objective: ", tuner.search_obj)
            self.design = tuner.search_task.design.name            
            self.task_names = [tuner.search_task.workload["name"]]
            #self.fuse = tuner.search_task.fuse
            self.split_pos = -1
            self.metric = tuner.search_obj
            self.bw = tuner.search_task.compute_bw(tuner.best_sol)
            self.ctc = tuner.search_task.compute_ctc(tuner.best_sol)
            self.exec_model.append(tuner.search_task.workload["name"])
            self.converge_time = tuner.converge_time
            self.off_chip_trans = tuner.search_task.est_off_chip_trans(tuner.best_sol)

            # Solutions
            self.arch_sol = tuner.search_task.arch_sol
            self.task_sols = [{
                "name": tuner.search_task.workload["name"],
                "hash": str(tuner.search_task),
                "ops": tuner.search_task.compute_ops(),
                "sol": tuner.best_sol,
                "latency": self.latency,
                "CTC": self.ctc,
                "DSP_eff": self.dsp_eff,
                "reward_meta": tuner.best_reward_meta,
                "BW": self.bw
            }]            
            self.records = None

            self.valid = 1

        return self

    def extract_from_tuner_multi_acc(self, records, reward, latency, cst, throughput, dsp_eff, split_pos=-1, partition=None, n_array=-1, meta=None):
        """ Extract multi-acc search records from the tuner.
        If meta is set, this is Arch3 (multi2), we use a different method to calcualte BW.
        """
        self.valid = 1
        for record in records:
            if record.valid == 0:
                self.valid = 0
        self.cst = cst
        self.latency = latency
        self.reward = reward
        self.dsp_eff = dsp_eff
        self.throughput = throughput
        self.split_pos = split_pos
        self.partition = partition
        self.n_array = n_array
        self.metric = records[0].metric
        for record in records:
            self.task_names += copy.deepcopy(record.task_names)
        #for record in records:
        #    self.bw += record.bw
        # Use the 1/throughput as the maximal latency
        # Accumulate the total data communication for all the arrays 
        # For single-workload array, check if the on-chips streaming buffers are used.
        if not meta:
            max_latency = 1 / throughput
            total_off_chip_trans = 0
            for record in records:
                total_off_chip_trans += record.off_chip_trans 
            self.bw = total_off_chip_trans * self.dw / (max_latency / (self.fre * 1e6)) / 1e9 # GB/s
        else:
            bw = 0
            for r in range(len(meta['round_info'])):
                total_off_chip_trans = meta['round_info'][r]['total_off_chip_trans']
                round_latency = meta['round_info'][r]['latency']
                bw = max(bw, total_off_chip_trans * self.dw / (round_latency / (self.fre * 1e6)) / 1e9)
            self.bw = bw                

        self.records = copy.deepcopy(records)

        return self

    def __repr__(self):
        return self.to_str()

    def to_dict(self):
        data_dict = {}
        if self.valid:
            # DSPs = (self.arch_sol['i_t1']/self.arch_sol['i_t2']) * (self.arch_sol['j_t1']/self.arch_sol['j_t2']) * (self.arch_sol['k_t2']) * 5
            data_dict['cst'] = self.cst
            data_dict['fre'] = self.fre
            data_dict['DSPs'] = self.cst['DSP']
            data_dict['BRAMs'] = self.cst['BRAM18K']
            data_dict['cycles'] = self.latency
            data_dict['latency'] = self.latency/(self.fre*1e6)
            data_dict['throughput (Op/cycle)'] = self.throughput
            data_dict['throughput (GOP/s)'] = self.throughput*self.fre*1e6/1e9
            data_dict['dsp_eff'] = self.dsp_eff
            data_dict['bw'] = self.bw
            data_dict['ops'] = self.ops
            data_dict['CTC(FLOP/byte)'] = self.ctc
            data_dict['off-chip communication (Bytes)'] = self.off_chip_trans * self.dw
            data_dict['arch sol'] = self.arch_sol
    
        return data_dict

    def to_str(self):
        to_print = ""
        if self.valid:        
            to_print += f"\nreward: {self.reward}"
            to_print += f"\ncst: {pprint.pformat(self.cst, indent=2)}"
            to_print += f"\nlatency: {self.latency}"
            to_print += f"\nthroughput: {self.throughput}"            
            to_print += f"\nenergy(mJ/normalized): {self.energy:.6f}"
            to_print += f"\nDSP efficiency: {self.dsp_eff:.2f}"
            to_print += f"\nBW(GB/s): {self.bw:.2f}"
            to_print += f"\nops: {self.ops:.2f}"
            to_print += f"\nCTC(FLOP/byte): {self.ctc:.2f}"
            to_print += f"\ndesign: {self.design}"
            to_print += f"\nconverge time: {self.converge_time}"
            to_print += f"\noff-chip communication (Bytes): {self.off_chip_trans * self.dw}"
            if self.fuse != -1:
                to_print += f"\nfuse: {self.fuse}"
            if self.split_pos != -1:
                to_print += f"\nsplit position: {self.split_pos}"            
            if self.partition:
                to_print += f"\npartition: {self.partition}"
            if self.n_array != -1:
                to_print += f"\n#array: {self.n_array}"            
            if len(self.exec_model) > 0:
                to_print += f"\nexec model: {self.exec_model}"
            to_print += f"\ntask names: {self.task_names}"
            if self.arch_sol:
                to_print += f"\narch sol: {pprint.pformat(self.arch_sol, indent=2)}"
            if self.task_sols:
                to_print += f"\ntask sols: \n{pprint.pformat(self.task_sols, indent=2)}"
            if self.records:                
                to_print += f"\nrecords: "
                for record_idx in range(len(self.records)):
                    print(record_idx, 50*'-')
                    to_print += f"\n<record{record_idx}><begin>"
                    to_print += f"{self.records[record_idx].to_str()}"
                    to_print += f"<record{record_idx}><end>"                
            if len(self.history) > 1:
                to_print += f"\nhistory records: "
                for record_idx in range(len(self.history)):
                    print(record_idx, 50*'-', 'history')
                    to_print += f"\n<record{record_idx}><begin>"
                    to_print += f"{self.history[record_idx].to_str()}"
                    to_print += f"<record{record_idx}><end>"
        else:
            to_print += f"\ninvalid record"
        to_print += "\n"

        return to_print

    def append(self, record):
        """ Append another record to the current record.
        All the records should share the same architecture.
        We will append the task solutions of the next record to the current record.
        """
        if record.valid == 0:
            self.valid = 0

        if len(self.task_sols) == 0:
            self = copy.deepcopy(record)
        else:
            if self.max != 1:
                raise RuntimeError("Appending records is only suppported under the max mode.")
            if self.metric == "latency":
                if record.latency != 0:
                    self.dsp_eff = (self.dsp_eff * self.latency + record.dsp_eff * record.latency) / (self.latency + record.latency)
                self.latency += record.latency
                if self.latency != 0:
                    self.reward = 1 / self.latency
            else:
                raise RuntimeError(f"Unsupported metric: {self.metric}.")			
            self.ops += record.ops
            self.throughput = self.ops / self.latency
            self.off_chip_trans += record.off_chip_trans
            self.bw = max(self.bw, record.bw)
            self.task_names += copy.deepcopy(record.task_names)
            self.exec_model += copy.deepcopy(record.exec_model)

            # Solutions
            self.task_sols += copy.deepcopy(record.task_sols)

        return self

    def merge(self, record1, record2):
        """ Merge another record to the current record.
        All the records should share the same architecture.
        We will append the next record to the current record lists.
        """                
        if record1.valid == 0 or record2.valid == 0:
            self.valid = 0
            return self
                
        self.valid = 1
        # Update the metadata
        self.cst = record1.cst        
        for item in self.cst:
            if record2.cst[item] > self.cst[item]:
                self.cst[item] = record2.cst[item]
        self.metric = record1.metric
        if self.metric == "latency":
            self.latency = record1.latency + record2.latency
            self.reward = 1 / self.latency
            # Update the DSP efficiency
            self.dsp_eff = (record1.dsp_eff * record1.latency + record2.dsp_eff * record2.latency) / (record1.latency + record2.latency)
        else:
            #print(self)
            raise RuntimeError(f"Unsupported metric: {self.metric}")        
        self.ops = record1.ops + record2.ops
        self.off_chip_trans = record1.off_chip_trans + record2.off_chip_trans
        self.bw = max(record1.bw, record2.bw)        
        self.design = record1.design
        for t_name in record1.task_names:
            self.task_names.append(t_name)
        for t_name in record2.task_names:
            self.task_names.append(t_name)     

        self.exec_model = copy.deepcopy(record1.exec_model)        
        if record1.fuse == 1 or record2.fuse == 1:            
            #print(record1.exec_model)
            #print(record2.exec_model)
            #print(record1.fuse, record2.fuse)
            self.exec_model = [self.exec_model, record2.exec_model]
            #print(self.exec_model)
        else:
            self.exec_model += record2.exec_model         
        self.arch_sol = record1.arch_sol

        # Solutions                
        #new_record.records = [copy.deepcopy(self), copy.deepcopy(record)]
        #self.records = [record1, record2]
        self.records = [record1.dup(), record2.dup()]

        return self

class NoDaemonProcess(mp.Process):
	# Make "daemon" attribute always return false
	def _get_daemon(self):
		return False
	def _set_daemon(self, value):
		pass
	daemon = property(_get_daemon, _set_daemon)

class MyExecutor(object):
	def __init__(self, n_thread):
		self.n_thread = n_thread
		self.timeout = 1800 # 30 minutes
		self.task_queue = mp.Queue()
		self.ret_queue = mp.Queue()
		self.proc_list = []		
		self.ret = {}		
		if n_thread > 1:
			manager = mp.Manager()
			self.return_dict = manager.dict()
			for i in range(self.n_thread):				
				p = NoDaemonProcess(target=self.runner, args=(self.task_queue, self.return_dict))
				self.proc_list.append(p)			
			for i in range(self.n_thread):
				self.proc_list[i].start()
	
	def runner(self, q, return_dict):
		while True:
			task = q.get()
			if task is None:
				break
			task_hash = task[0]
			task_func = task[1]
			task_args = task[2]
			ret = task_func(*task_args)			
			return_dict[task_hash] = ret

	def prune_jobs(self, jobs):
		""" Prune jobs with the same hash
		"""
		job_list = []
		cache = []

		for job in jobs:
			if job['job_hash'] in cache:
				continue
			else:
				job_list.append(job)
				cache.append(job['job_hash'])

		return job_list	

	def exec(self, job_list):
		""" Submit the job to the executor.
		job and job_args are both lists.
		Return a list of job results.
		"""				
		# Prune away redundant jobs
		job_list = self.prune_jobs(job_list)			
				
		results = {}
		if self.n_thread > 1:			
			for job in job_list:
				self.task_queue.put((job['job_hash'], job['func'], job['args']))			
			for i in range(self.n_thread):
				self.task_queue.put(None)			
			start = time.time()
			while time.time() - start <= self.timeout:				
				if not any(p.is_alive() for p in self.proc_list):
					break
				time.sleep(.1)				
			else:
				# Timeout, kill all the processes
				for p in self.proc_list:
					p.terminate()								
			for p in self.proc_list:
				p.join()			
			
			for job in job_list:
				if job['job_hash'] in self.return_dict:
					results[job['job_hash']] = self.return_dict[job['job_hash']]
				else:
					results[job['job_hash']] = SearchRecord().reset()
		else:
			for job in job_list:
				job_args = job['args']
				results[job['job_hash']] = job['func'](*job_args)
		
		return results