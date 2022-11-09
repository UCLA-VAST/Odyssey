import os
import json
import importlib
import re
from math import ceil
from math import prod
import numpy as np

prj_path = os.environ["PRJ_PATH"]
designs_lib_dir = prj_path + f'/data/designs_lib'
designs_dir = prj_path + '/scratch_new/tmp/designs'
output_dir = prj_path + '/scratch_new/tmp/outputs'

def get_port_ub(i_t0, o_t0, r_t0, c_t0, term):
	max_bound = 0
	if 'i_t' in term:
		i_t1_candidates = [x for x in range(1, i_t0+1) if i_t0%x == 0]
		for i_t1 in i_t1_candidates:
			i_t2_candidates = [x for x in range(1, 8+1) if i_t1%x == 0]
			for i_t2 in i_t2_candidates:
				bound = eval(term)
				if bound > max_bound:
					max_bound = bound
		return max_bound
	elif 'o_t' in term:
		o_t1_candidates = [x for x in range(1, o_t0+1) if o_t0%x == 0]
		for o_t1 in o_t1_candidates:
			o_t2_candidates = [x for x in range(1, o_t1+1) if o_t1%x == 0]
			for o_t2 in o_t2_candidates:
				bound = eval(term)
				if bound > max_bound:
					max_bound = bound
		return max_bound
	elif 'r_t' in term:
		r_t1_candidates = [x for x in range(1, r_t0+1) if r_t0%x == 0]
		for r_t1 in r_t1_candidates:
			r_t2_candidates = [x for x in range(1, r_t1+1) if r_t1%x == 0]
			for r_t2 in r_t2_candidates:
				bound = eval(term)
				if bound > max_bound:
					max_bound = bound
		return max_bound
	elif 'c_t' in term:
		c_t1_candidates = [x for x in range(1, c_t0+1) if c_t0%x == 0]
		for c_t1 in c_t1_candidates:
			c_t2_candidates = [x for x in range(1, c_t1+1) if c_t1%x == 0]
			for c_t2 in c_t2_candidates:
				bound = eval(term)
				if bound > max_bound:
					max_bound = bound
		return max_bound

def print_model_params(f, desp, problem_size, resource_limits):
	f.write('from gekko import GEKKO\n')
	f.write('import numpy as np\n')
	f.write('\n')
	f.write('def get_solver_latency(problem_size, resource_limits, solver):\n')
	f.write('\tm = GEKKO(remote=False)\n')
	# f.write('\tm.options.SOLVER = 2\n')
	# f.write('\tm.options.IMODE = 3\n')
	f.write('\tm.options.MAX_ITER = 10000\n')
	# f.write('\tm.options.AUTO_COLD = 1\n')
	# f.write("\tm.solver_options = [\n")
	# f.write("\t	'nlp_maximum_iterations 100000',\n")
	# f.write("\t	'objective_convergence_tolerance 1.0e-6',\n")
	# f.write("\t	'constraint_convergence_tolerance 1.0e-3'\n")
	# f.write("\t]\n")
	# f.write('\tm.options.COLDSTART = 1\n')
	# f.write('\tm.options.NODES = 3\n')
	# f.write('\tm.options.MV_TYPE = 1\n')
	f.write('\n')
	f.write(f'\tbram_bound = int(resource_limits["BRAM18K"])\n')
	f.write(f'\tdsp_bound = int(resource_limits["DSP"])\n')
	f.write('\n')

	for p in desp["params"]:
		if p["name"] in problem_size:
			f.write(f'\t{p["name"]} = problem_size["{p["name"]}"]\n')
		elif 't1' in p["name"]:
			problem_dim = p["name"].split('_')[0]
			f.write(f'\t{p["name"]} = m.Var(value={problem_dim})\n')
			# f.write(f'\t{p["name"]} = m.Var(lb=1, ub={problem_dim}, value={problem_dim})\n')
		
		elif 't2' in p["name"]:
			problem_dim = p["name"].split('_')[0]
			f.write(f'\t{p["name"]} = m.Var(value={problem_dim})\n')
			# f.write(f'\t{p["name"]} = m.Var(lb=1, ub={problem_dim}, value={problem_dim})\n')
		
		else:
			# print(p['bounds'])
			# ub = re.sub(r'max', 'm.max2', p['bounds'][1])            
			# ub = re.sub(r'min', 'm.min2', ub) 
			i_t1 = problem_size['i']
			o_t1 = problem_size['o']
			r_t1 = problem_size['r']
			c_t1 = problem_size['c']
			i_t2 = 8
			o_t2 = o_t1
			r_t2 = r_t1
			c_t2 = c_t1
			ub = eval(p['bounds'][1])
			lb = 1#p["bounds"][0]
			# f.write(f'\t{p["name"]} = m.Var(lb={lb}, ub={ub}, value={ub})\n')
			# f.write(f'\t{p["name"]} = m.Var(lb=1)\n')
			f.write(f'\t{p["name"]} = m.Var(value={ub})\n')

	f.write('\n')

def print_objective(f, desp):
	# f.write('\n')
	# f.write('\tm.Obj(latency)\n')
	# f.write("\ttry:\n")
	# f.write("\t	m.options.SOLVER = 1\n")
	# f.write("\t	m.solve(disp=False)\n")
	# f.write("\t	apopt_solution = m.options.OBJFCNVAL\n")
	# f.write("\texcept:\n")
	# # f.write("\t	print('APOPT failed')\n")
	# f.write("\t	apopt_solution = np.inf\n")
	# f.write("\ttry:\n")
	# f.write("\t	m.options.SOLVER = 2\n")
	# f.write("\t	m.solve(disp=False)\n")
	# f.write("\t	bpopt_solution = m.options.OBJFCNVAL\n")
	# f.write("\texcept:\n")
	# # f.write("\t	print('BPOPT failed')\n")
	# f.write("\t	bpopt_solution = np.inf\n")
	# f.write("\ttry:\n")
	# f.write("\t	m.options.SOLVER = 3\n")
	# f.write("\t	m.solve(disp=False)\n")
	# f.write("\t	ipopt_solution = m.options.OBJFCNVAL\n")
	# f.write("\texcept:\n")
	# # f.write("\t	print('IPOPT failed')\n")
	# f.write("\t	ipopt_solution = np.inf\n")
	# f.write("\tprint(f'APOPT: {apopt_solution}, BPOPT: {bpopt_solution}, IPOPT: {ipopt_solution}')\n")
	# f.write("\treturn min(apopt_solution, bpopt_solution, ipopt_solution)\n")
	f.write("	try:\n")
	f.write("		m.Obj(latency)\n")
	f.write("		m.options.SOLVER = solver\n")
	f.write("		m.solve(disp=False)\n")
	f.write("		return m.options.OBJFCNVAL\n")
	f.write("	except:\n")
	f.write("		return np.inf\n")
	f.write("\n")
	f.write("def try_all_solvers(problem_size, resource_limits):\n")
	f.write("	solvers = {1:'APOPT', 2:'BOPOPT', 3:'IPOPT'}\n")
	f.write("	cycles = []\n")
	f.write("	for i in range(3):\n")
	f.write("		cycles.append(get_solver_latency(problem_size, resource_limits, i+1))\n")
	f.write("		print(f'{solvers[i+1]}: {cycles[i]}', end=' ')\n")
	f.write("	print()\n")
	f.write("	return min(cycles)\n")


def print_latency_est_func(f, desp):
	def extract_latency_expr(lat, info):
		ret = ""
		if lat["type"] == "block":
			info["has_for_child"] = 0
			no_for_child = True
			is_first = True
			ret += "("
			for child in lat["child"]:
				if not is_first:
					ret += " + "                    
				ret += extract_latency_expr(child, info)                    
				if info["has_for_child"] == 1:
					no_for_child = False
				is_first = False
			ret += ")"
			if no_for_child:
				ret = "1"
		elif lat["type"] == "for":                
			child = lat["child"]
			expr = extract_latency_expr(child, info)                
			if info["valid"]:
				ret = lat["bounds"][1] + " * " + expr
			else:
				ret = expr
			info["has_for_child"] = 1
		elif lat["type"] == "mark":      
			if info["under_mark"] and lat["content"] == info["under_mark"]:
				info["valid"] = True
			if lat["content"] == "simd":
				if info["valid"]:
					ret = "1"
				else:
					ret = "0"
			else:
				child = lat["child"]
				ret = extract_latency_expr(child, info)
			if info["under_mark"] and lat["content"] == info["under_mark"]:
				info["valid"] = False
		elif lat["type"] == "user":
			user_expr = lat["child"]["user_expr"]
			if 'inter_intra' in user_expr or 'intra_inter' in user_expr:                    
				if user_expr[:-2].split(".")[-1] == "1":
					double_buffer = 1
				else:
					double_buffer = 0                    
				# Plug in submodule latency
				if f"{info['name']}_inter" in info["modules"]:
					inter_expr = info["modules"][f"{info['name']}_inter"]
				else:
					inter_expr = None
				if f"{info['name']}_intra" in info["modules"]:
					intra_expr = info["modules"][f"{info['name']}_intra"]
				else:
					intra_expr = None

				if inter_expr and intra_expr:
					if info["in"] == 1 or info["in"] == 0:
						ret = inter_expr
					else:
						if double_buffer:
							ret = f"max({inter_expr}, {intra_expr})"
						else:
							ret = f"({inter_expr} + {intra_expr})"
					info["has_for_child"] = 1
				else:                        
					ret = "1"                        
				if not info["valid"]:
					ret = "0"
			elif "inter_trans" in user_expr:
				# Plug in submodule latency
				if f"{info['name']}_inter" in info["modules"]:
					ret = info["modules"][f"{info['name']}_inter"]
				else:
					ret = "1"
				if not info["valid"]:
					ret = "0"
			elif "intra_trans" in user_expr:
				# Plug in submodule latency                    
				if f"{info['name']}_intra" in info["modules"]:
					ret = info["modules"][f"{info['name']}_intra"]
				else:
					ret = "1"
				if not info["valid"]:
					ret = "0"
			else:
				ret = "1"
		elif lat["type"] == "if":
			# Only examine the first child
			child = lat["child"][0]
			ret = extract_latency_expr(child, info)
		elif lat["type"] == "array_tile":      
			if info["module_attr"]["to_dram"] == 1:
				if info["module_attr"]["serialize"] == 0:
					# Consider the DRAM latency here.
					ret = "(" + f"{lat['size']}/{lat['last_dim']}*(20+{lat['last_dim']}/(512/8/{lat['ele_size']}))" + ")"
				else:
					ret = "(" + lat["size"] + "/" + f"min({lat['data_pack_factor']}, 512/8/{lat['ele_size']})" + ")"
			else:
				ret = "(" + lat["size"] + "/" + lat["data_pack_factor"] + ")"                    
		else:
			raise RuntimeError(f"Unsupported latency node type {lat['type']}")

		return ret

	# Check if drain module can be omitted
	# Note: It should be supported in the codegen of AutoSA. However, currently,
	# we move it here in the tuner.        
	out_module = {}
	out_drain_module = {}
	for module in desp["memory"]:
		module_mem = desp["memory"][module]
		if module.endswith('_out'):
			item = {'buf_size': module_mem['buf_size'], 
					'num': module_mem['num']}
			if module.find('drain') != -1:
				item['merged'] = 0
				out_drain_module[module_mem['array']] = item
			else:                    
				if module_mem['array'] not in out_module:
					out_module[module_mem['array']] = [item]
				else:
					out_module[module_mem['array']].append(item)
	for array in out_drain_module:
		if array in out_module:
			for m in out_module[array]:                
				if m['buf_size'] == out_drain_module[array]['buf_size'] and \
					m['num'] == out_drain_module[array]['num']:
					out_drain_module[array]['merged'] = 1

	# Latency prologue
	latency_prologue_items = []
	info = {"has_for_child": 0, "name": None, "modules": {}}
	for i in range(2):
		for module in desp["latency"]:
			if desp["attr"][module]["in"] != 1:
				continue
			if "inter" in module or "intra" in module:                    
				# Keep all the latency AST under the mark.
				info["valid"] = True
				info["under_mark"] = None
				info["in"] = 1
			else:
				# Only keep the latency AST under the mark.
				info["valid"] = False
				info["under_mark"] = "array"
				info["in"] = 1
			module_lat = desp["latency"][module]  
			info["name"] = module     
			info["module_attr"] = desp["attr"][module]
			info["modules"][module] = extract_latency_expr(module_lat, info)
	for module in info["modules"]:
		if "inter" in module or "intra" in module:
			continue
		if module.find('drain') != -1 and out_drain_module[module_mem['array']]['merged'] == 1:
			continue
		info["modules"][module] = re.sub(r'ceil', '', info["modules"][module])
		info["modules"][module] = re.sub(r'max', 'm.max2', info["modules"][module])            
		info["modules"][module] = re.sub(r'min', 'm.min2', info["modules"][module])            
		f.write(f"\t{module}_single_latency = ")                        
		f.write(info["modules"][module])
		f.write(f"\n")      
		latency_prologue_items.append(f"{module}_single_latency")
	f.write("\n\tlatency_prologue = m.Var()\n\n")
	for module in info["modules"]:
		if "inter" in module or "intra" in module:
			continue 
		if module.find('drain') != -1 and out_drain_module[module_mem['array']]['merged'] == 1:
			continue           
		f.write(f"\tm.Equation({module}_single_latency <= latency_prologue)\n")
	f.write("\n\n")

	# Latency epilogue
	latency_epilogue_items = []
	info = {"has_for_child": 0, "name": None, "modules": {}}
	for i in range(2):
		for module in desp["latency"]:
			if desp["attr"][module]["in"] != 0:
				continue
			if "inter" in module or "intra" in module:
				info["valid"] = True
				info["under_mark"] = None
				info["in"] = 0
			else:
				info["valid"] = False
				info["under_mark"] = "array"
				info["in"] = 0
			module_lat = desp["latency"][module]  
			info["name"] = module                
			info["module_attr"] = desp["attr"][module]
			info["modules"][module] = extract_latency_expr(module_lat, info)
	for module in info["modules"]:            
		if "inter" in module or "intra" in module:
			continue
		if module.find('drain') != -1:
			array_name = module[:module.find("_drain_IO")]                
			if out_drain_module[array_name]['merged'] == 1:
				continue
		info["modules"][module] = re.sub(r'ceil', '', info["modules"][module])   
		info["modules"][module] = re.sub(r'max', 'm.max2', info["modules"][module])            
		info["modules"][module] = re.sub(r'min', 'm.min2', info["modules"][module])            
		f.write(f"\t{module}_single_latency = ")                        
		f.write(info["modules"][module])
		latency_epilogue_items.append(f"{module}_single_latency")
		f.write(f"\n")        
	cnt = 0
	for module in info["modules"]:
		if "inter" in module or "intra" in module:
			continue    
		if module.find('drain') != -1:
			array_name = module[:module.find("_drain_IO")]                
			if out_drain_module[array_name]['merged'] == 1:
				continue                 
		cnt += 1
	if cnt == 1:
		f.write("\n\tlatency_epilogue = m.Var()\n\n")
	else:
		f.write("\n\tlatency_epilogue = m.Var()\n\n")
	for module in info["modules"]:
		if "inter" in module or "intra" in module:
			continue    
		if module.find('drain') != -1:
			array_name = module[:module.find("_drain_IO")]                
			if out_drain_module[array_name]['merged'] == 1:
				continue                    
		f.write(f"\tm.Equation({module}_single_latency <= latency_epilogue)\n")
	if cnt == 1:            
		f.write("\n\n")
	else:
		f.write("\n\n")

	# Latency main
	latency_main_items = []
	info = {"has_for_child": 0, "name": None, "modules": {}}
	for i in range(2):
		# Run second time to fill in the incomplete expression            
		for module in desp["latency"]:
			module_lat = desp["latency"][module]  
			info["name"] = module
			info["valid"] = True
			info["under_mark"] = None
			info["in"] = -1
			info["module_attr"] = desp["attr"][module]
			info["modules"][module] = extract_latency_expr(module_lat, info)            
	for module in info["modules"]:
		if "inter" in module or "intra" in module:
			continue
		if module.find('drain') != -1:
			array_name = module[:module.find("_drain_IO")]                
			if out_drain_module[array_name]['merged'] == 1:
				continue                  
		f.write(f"\t{module}_latency = ")    
		info["modules"][module] = re.sub(r'ceil', '', info["modules"][module])    
		info["modules"][module] = re.sub(r'max', 'm.max2', info["modules"][module])            
		info["modules"][module] = re.sub(r'min', 'm.min2', info["modules"][module])            
		f.write(info["modules"][module])
		f.write(f"\n")        
		latency_main_items.append(f"{module}_latency")
	f.write("\n\tlatency_main = m.Var()\n\n")
	for module in info["modules"]:
		if "inter" in module or "intra" in module:
			continue   
		if module.find('drain') != -1:
			array_name = module[:module.find("_drain_IO")]                
			if out_drain_module[array_name]['merged'] == 1:
				continue                      
		f.write(f"\tm.Equation({module}_latency <= latency_main)\n")
	f.write("\n\n")
	f.write('\tlatency = latency_prologue + latency_main + latency_epilogue\n\n')

def print_model_constraints(f, desp):
	# DSP constraints
	f.write(f"\tm.Equation({desp['compute']['PE']['num']} * ")
	f.write(f"{desp['compute']['PE']['unroll_factor']} * ")
	if desp["compute"]["PE"]["ele_type"] == "float":
			f.write(f"5 <= dsp_bound)\n")
	else:
			raise RuntimeError(f"Unsupported data type {desp['compute']['PE']['ele_type']} in resource estimation")        
	f.write("\n")

	# BRAM constraints
	f.write(f'\tm.Equation(\n')
	# Print function est_BRAM18K
	# Check if drain module can be merged.
	# Note: It should be supported in the codegen of AutoSA. However, currently, 
	# we move it here in the tuner.
	mem_meta_info = {}
	out_module = {}
	out_drain_module = {}
	for module in desp["memory"]:
		module_mem = desp["memory"][module]
		if module.endswith('_out'):
			item = {'buf_size': module_mem['buf_size'], 
				'num': module_mem['num']}
			if module.find('drain') != -1:
				item['merged'] = 0
				out_drain_module[module_mem['array']] = item
			else:                    
				if module_mem['array'] not in out_module:
					out_module[module_mem['array']] = [item]
				else:
					out_module[module_mem['array']].append(item)
	for array in out_drain_module:
		if array in out_module:
			for m in out_module[array]:                
				if m['buf_size'] == out_drain_module[array]['buf_size'] and \
					m['num'] == out_drain_module[array]['num']:
					out_drain_module[array]['merged'] = 1

	modules_dict = {}
	for module in desp["memory"]:
		module_mem = desp["memory"][module]
		if module.find('drain') != -1 and out_drain_module[module_mem['array']]['merged'] == 1:
			continue
		# ceil(ele_size*8*pack / 36) * ceil(ele_num/pack/512)
		ele_size = module_mem['ele_size']
		ele_num = module_mem['buf_size'] 
		if "data_pack_factor_inter" in module_mem:
			pack = module_mem["data_pack_factor_inter"]
		else:
			pack = 1
		modules_dict[module] = f'\t({ele_size}*8*{pack} / 36) * ({ele_num}/{pack}/512)'

	is_first = True
	for module in desp["memory"]:
		module_mem = desp["memory"][module]
		if module.find('drain') != -1 and out_drain_module[module_mem['array']]['merged'] == 1:
			continue
		module_unit_brams = modules_dict[module]
		if not is_first:
			f.write(" + \n")            
		f.write(module_unit_brams)
		if module_mem["double_buffer"]:
			f.write(f" * 2")
		else:
			f.write(f" * 1")
		f.write(f" * {module_mem['num']}")            
		is_first = False
	f.write("\n\t<= bram_bound)\n")
	f.write("\n")

	# Other constraints
	params_config = {"external": {}, "tunable": {}, "infer": {}}
	for param in desp["params"]:
		if param["tunable"]:
			params_config["tunable"][param["name"]] = param
		else:
			if "external" in param["tags"]:
				params_config["external"][param["name"]] = param
			elif "auto_infer" in param["tags"]:
				params_config["infer"][param["name"]] = param
	# Load parameters
	counter = 0
	for p in desp["params"]:
		if "bounds" in p:
			counter += 1
			p['bounds'][0] = re.sub(r'max', 'm.max2', p['bounds'][0])            
			p['bounds'][0] = re.sub(r'min', 'm.min2', p['bounds'][0])  
			f.write(f"\tm.Equation({p['name']} >= {p['bounds'][0]})\n")
			# f.write(f"\t\treturn False\n")
			# If the parameter is the first-level tiling factors, 
			# ignore the upper bounds.
			# if not p['name'].endswith('t1'):
			counter += 1
			p['bounds'][1] = re.sub(r'max', 'm.max2', p['bounds'][1])            
			p['bounds'][1] = re.sub(r'min', 'm.min2', p['bounds'][1]) 
			f.write(f"\tm.Equation({p['name']} <= {p['bounds'][1]})\n")
			# print(f"Add constraints for {p['name']}")
					# f.write(f"\t\treturn False\n")
			# if "tags" in p and "power_of_two" in p["tags"]:
			# 		f.write(f"\tif filter_non_power_of_two({p['name']}):\n")
			# 		f.write(f"\t\treturn False\n")
	# Latency hiding
	if "PE" in desp["memory"]:
		f.write(f"\tm.Equation(")
		simd = None
		latency_hiding = []
		for p, param in params_config["tunable"].items():
			if param["attr"] == "latency_tiling_factor":
					latency_hiding.append(param['name'])
			if param["attr"] == "SIMD_tiling_factor":
				simd = param['name']
		data_type = desp["memory"]["PE"]["ele_type"]
		latency_hiding_str = " * ".join(latency_hiding)
		if data_type == "float":
			f.write(f"\t{latency_hiding_str} >= {simd} * 8)\n")
		else:
			raise RuntimeError(f"Unsupported data type in random sample generation: {data_type}")
	# # check if 2d SA has dim = 1
	# dims = desp['compute']['PE']['dims']
	# if len(dims) == 2:
	# 		f.write(f'\tif {dims[0]} <= 1:\n')
	# 		f.write(f'\t\treturn False\n')
	# 		f.write(f'\tif {dims[1]} <= 1:\n')
	# 		f.write(f'\t\treturn False\n')

def print_model(f, desp, problem_size, resource_limits, solver_vars, solver_consts, other_ports):
	print_model_params(f, desp, problem_size, resource_limits, solver_vars, solver_consts, other_ports)
	print_model_target(f, desp)
	print_model_constraints(f, desp)

def print_data(f, desp, problem_size, resource_limits, remaining_ports):
	for p in desp["params"]:
		if p["name"] in problem_size:
			f.write(f'param {p["name"]} := {problem_size[p["name"]]};\n')
		elif 't' not in p["name"] and p["name"] in remaining_ports:
			# max(min(i_t1,4),i_t2)
			# get the 4
			# bound = p["bounds"][1].split(',')
			# bound = bound[1].strip(')')
			f.write(f'param {p["name"]} := {remaining_ports[p["name"]]};\n')
	f.write(f'param bram_bound := {int(resource_limits["BRAM18K"])};\n')
	f.write(f'param dsp_bound := {int(resource_limits["DSP"])};\n')

def compute_ops(workload, problem_size):
	""" Compute the total amount of operations of the workload.
	"""        
	if "mm" in workload:
			return problem_size["i"] * problem_size["j"] * problem_size["k"] * 2
	elif "conv" in workload:
			return problem_size["i"] * problem_size["o"] * problem_size["r"] * problem_size["c"] * problem_size["p"] * problem_size["q"] * 2
	else:
			raise RuntimeError(f"Not supported workload: {self.workload['name']}")

# may need be fixed for conv workloads: TODO
def compute_bw(params, cycles, off_chip_trans, dw, fre):
	""" Compute the bandwidth requirement of the task.
	Note: Only works for 32-bit data
	"""
	latency = cycles
	bw = off_chip_trans * dw / (latency / (fre * 1e6)) / 1e9 # GB/s
	return bw

def compute_ctc(params, workload, problem_size, off_chip_trans, dw):
	""" Compute the compute-to-communication ratio of the task.
	"""
	ops = compute_ops(workload, problem_size)
	comm = off_chip_trans * dw
	ctc = ops / comm

	return ctc

def compute_dsp_eff(cycles, workload, problem_size, dsp):
	""" Compute the DSP efficiency of the current design.
	Note: Only works for FP32 on Xilinx FPGA
	"""
	return (compute_ops(workload, problem_size) / (dsp / 5 * 2)) / cycles

def copy_design(design, workload):
	os.system(f'cp {designs_lib_dir}/{workload}/{design} {designs_dir}')

def list_split(ori_list, split_num):
	chunk_size = int(np.ceil(float(len(ori_list)) / split_num))
	chunks = [ori_list[i: i + min(chunk_size, len(ori_list) - i)] for i in range(0, len(ori_list), chunk_size)]
	return chunks

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

def print_solution(idx, design, solution, sa_info, objective, workload, elapsed_time, csv_path):
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
	array_part_mapping = eval(open(f'{prj_path}/tests/{workload}_array_part.csv').readlines()[int(sa_info['idx'])])
	latency_hiding_mapping = eval(open(f'{prj_path}/tests/{workload}_latency_hiding.csv').readlines()[int(sa_info['idx'])])
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
	csv_file = open(csv_path, 'a')
	print(f'{design.split(".")[0]}_{idx},', end='', file=csv_file)
	print(f'{elapsed_time:.1f},', end='', file=csv_file)
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
	print(f'{sa_sizes}', end='', file=csv_file)
	print(file=csv_file)
	csv_file.close()
	return

def print_latencies(idx, design, solution, sa_info, objective, workload, elapsed_time, csv_path):
	file_path = 'tmp/designs/register/' + design.strip('.json')
	file_path = file_path.replace('/', '.')
	model = importlib.import_module(file_path)
	compute_arch_cst = model.compute_arch_cst
	cycles = solution['cycles']
	cycles_details = solution['cycles_details']
	A_IO_L2_in_single_latency = cycles_details['latency_prologue']['A_IO_L2_in_single_latency']
	A_IO_L3_in_single_latency = cycles_details['latency_prologue']['A_IO_L3_in_single_latency']
	B_IO_L2_in_single_latency = cycles_details['latency_prologue']['B_IO_L2_in_single_latency']
	B_IO_L3_in_single_latency = cycles_details['latency_prologue']['B_IO_L3_in_single_latency']
	A_IO_L2_in_latency = cycles_details['latency_main']['A_IO_L2_in_latency']
	A_IO_L3_in_latency = cycles_details['latency_main']['A_IO_L3_in_latency']
	B_IO_L2_in_latency = cycles_details['latency_main']['B_IO_L2_in_latency']
	B_IO_L3_in_latency = cycles_details['latency_main']['B_IO_L3_in_latency']
	C_drain_IO_L1_out_latency = cycles_details['latency_main']['C_drain_IO_L1_out_latency']
	C_drain_IO_L2_out_latency = cycles_details['latency_main']['C_drain_IO_L2_out_latency']
	C_drain_IO_L3_out_latency = cycles_details['latency_main']['C_drain_IO_L3_out_latency']
	PE_latency = cycles_details['latency_main']['PE_latency']
	C_drain_IO_L1_out_single_latency = cycles_details['latency_epilogue']['C_drain_IO_L1_out_single_latency']
	C_drain_IO_L2_out_single_latency = cycles_details['latency_epilogue']['C_drain_IO_L2_out_single_latency']
	C_drain_IO_L3_out_single_latency = cycles_details['latency_epilogue']['C_drain_IO_L3_out_single_latency']
	csv_file = open(csv_path, 'a')
	print(f'{cycles:.0f},', end='', file=csv_file)
	print(f'{A_IO_L2_in_single_latency:.0f},', end='', file=csv_file)
	print(f'{A_IO_L3_in_single_latency:.0f},', end='', file=csv_file)
	print(f'{B_IO_L2_in_single_latency:.0f},', end='', file=csv_file)
	print(f'{B_IO_L3_in_single_latency:.0f},', end='', file=csv_file)
	print(f'{A_IO_L2_in_latency:.0f},', end='', file=csv_file)
	print(f'{A_IO_L3_in_latency:.0f},', end='', file=csv_file)
	print(f'{B_IO_L2_in_latency:.0f},', end='', file=csv_file)
	print(f'{B_IO_L3_in_latency:.0f},', end='', file=csv_file)
	print(f'{C_drain_IO_L1_out_latency:.0f},', end='', file=csv_file)
	print(f'{C_drain_IO_L2_out_latency:.0f},', end='', file=csv_file)
	print(f'{C_drain_IO_L3_out_latency:.0f},', end='', file=csv_file)
	print(f'{PE_latency:.0f},', end='', file=csv_file)
	print(f'{C_drain_IO_L1_out_single_latency:.0f},', end='', file=csv_file)
	print(f'{C_drain_IO_L2_out_single_latency:.0f},', end='', file=csv_file)
	print(f'{C_drain_IO_L3_out_single_latency:.0f}', end='', file=csv_file)
	print(file=csv_file)
	csv_file.close()
	return

# def print_result(idx, design, solution, sa_info, objective, workload, elapsed_time, csv_path):
# 	file_path = 'tmp/designs/register/' + design.strip('.json')
# 	file_path = file_path.replace('/', '.')
# 	model = importlib.import_module(file_path)
# 	compute_arch_cst = model.compute_arch_cst

# 	original_workload_size = {}
# 	padded_workload_size = {}
# 	padding_dims = sa_info['padding_dims']
# 	# get elements from dictionary solution['arch_sol'] whose key ends with t1
# 	# and store them in t1_dims
# 	for dim in solution['arch_sol'].keys():
# 		if len(dim) == 1:
# 			original_workload_size[dim] = solution['arch_sol'][dim]
# 	t1_dims = {k:v for k, v in solution['arch_sol'].items() if k.endswith('t1')}
# 	for dim in solution['arch_sol'].keys():
# 		if dim in padding_dims:
# 			# get key and value from t1_dims if dim is in key
# 			t1_dim = [v for k, v in t1_dims.items() if dim in k][0]
# 			padded_workload_size[dim] = ceil(solution['arch_sol'][dim]/t1_dim)*t1_dim
# 	# for key in original_workload_size.keys():
# 	# 	if key not in padded_workload_size.keys():
# 	# 		padded_workload_size[key] = original_workload_size[key]
# 	# sort padded_workload_size by key
# 	padded_workload_size = dict(sorted(padded_workload_size.items()))
# 	# sort original_workload_size by key
# 	original_workload_size = dict(sorted(original_workload_size.items()))
# 	fre = solution['fre']
# 	throughput = solution['throughput']
# 	cycles = solution['cycles']
# 	latency = solution['latency']
# 	dsp_eff = solution['dsp_eff']
# 	off_chip_bytes = solution['off_chip_bytes']
# 	bandwidth = solution['bandwidth']
# 	CTC = solution['CTC']
# 	DSPs = solution['DSPs']
# 	BRAMs = solution['BRAMs']
# 	arch = compute_arch_cst(solution['arch_sol'])
# 	array_part_mapping = eval(open(f'{prj_path}/tests/{workload}_array_part.csv').readlines()[int(sa_info['idx'])])
# 	latency_hiding_mapping = eval(open(f'{prj_path}/tests/{workload}_latency_hiding.csv').readlines()[int(sa_info['idx'])])
# 	if len(arch['dims']) == 1:
# 		if array_part_mapping[0] not in latency_hiding_mapping:
# 			SA_Dims = '"' + str((int(arch['dims'][0])*int(arch['SIMD']), 1)) + '"'
# 			PEs = int(arch['dims'][0])*int(arch['SIMD'])
# 		else:
# 			SA_Dims = '"' + str((int(arch['dims'][0]), int(arch['SIMD']))) + '"'
# 			PEs = prod(arch['dims'])
# 	elif len(arch['dims']) == 2:
# 		if array_part_mapping[1] not in latency_hiding_mapping:
# 			SA_Dims = '"' + str((int(arch['dims'][0]), int(arch['dims'][1])*int(arch['SIMD']), 1)) + '"'
# 			PEs = int(arch['dims'][0])*int(arch['dims'][1])*int(arch['SIMD'])
# 		else:
# 			SA_Dims = '"' + str((int(arch['dims'][0]), int(arch['dims'][1]), int(arch['SIMD']))) + '"'
# 			PEs = prod(arch['dims'])

# 	sa_sizes = get_SA_sizes(sa_info, solution, workload)
# 	csv_file = open(csv_path, 'a')
# 	print(f'{design.split(".")[0]}_{idx},', end='', file=csv_file)
# 	print(f'{elapsed_time:.1f},', end='', file=csv_file)
# 	print(f'{objective},', end='', file=csv_file)
# 	print(f'"{original_workload_size}",', end='', file=csv_file)
# 	print(f'"{padded_workload_size}",', end='', file=csv_file)
# 	print(f'{fre:.0f},', end='', file=csv_file)
# 	print(f'{throughput:.2f},', end='', file=csv_file)
# 	print(f'{cycles:.0f},', end='', file=csv_file)
# 	print(f'{latency:.5f},', end='', file=csv_file)
# 	print(f'{dsp_eff:.2f}%,', end='', file=csv_file)
# 	print(f'{off_chip_bytes:.0f},', end='', file=csv_file)
# 	print(f'{bandwidth:.2f},', end='', file=csv_file)
# 	print(f'{CTC:.2f},', end='', file=csv_file)
# 	print(f'{DSPs:.0f},', end='', file=csv_file)
# 	print(f'{BRAMs:.0f},', end='', file=csv_file)
# 	print(f'{PEs:.0f},', end='', file=csv_file)
# 	print(f'{SA_Dims},', end='', file=csv_file)
# 	print(f'{sa_sizes}', end='', file=csv_file)
# 	print(file=csv_file)
# 	csv_file.close()
# 	return

