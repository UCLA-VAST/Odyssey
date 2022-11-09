from utils import *

design = 'kernel7_2.json'
design_path = prj_path + '/scratch/tmp/designs/' + design

u250_info = json.load(open(prj_path + '/data/cst/u250.json'))
resource_limits = {'DSP': u250_info['DSP']['total']*u250_info['DSP']['ratio'], 'BRAM18K': u250_info['BRAM18K']['total']*u250_info['BRAM18K']['ratio']}

problem_size = {'i': 64, 'o': 64, 'r': 64, 'c': 64, 'p': 3, 'q': 3}

with open(design_path, 'r') as f:
  design_desc = json.load(f)

with open('solver_model.py', 'w') as f:
  print_model_params(f, design_desc, problem_size, resource_limits)
  print_latency_est_func(f, design_desc)
  print_model_constraints(f, design_desc)
  print_objective(f, design_desc)