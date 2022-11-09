from utils import *
import json 
out_file = open("model.tex", "w")
with open('kernel3_2.json', 'r') as f:
  desp = json.load(f)

print_model_target(out_file, desp)
print_model_constraints(out_file, desp)

def isPowerofTwo(n):
  return np.log2(n) == np.floor(np.log2(n))