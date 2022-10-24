import os
import sys
import re
import pandas as pd

prj_path = os.environ['PRJ_PATH']
folders_only = [f for f in os.listdir('.') if os.path.isdir(f)]

# sort folders
folders_only.sort()
passed_all = True
for folder in folders_only:
  if folder != 'logs': 
    src_file = f'{folder}/src/kernel_kernel.cpp'
    # count the number of 'PE_wrapper' in the file
    src_PE_num = -1 # to exclude the function name
    # if file exists
    if os.path.isfile(src_file):
      with open(src_file, 'r') as f:
        lines = f.readlines()
        for line in lines:
          if 'PE_wrapper' in line:
            src_PE_num += 1
      design_info_file = f'{folder}/design_info.csv'
      design_info = pd.read_csv(design_info_file)
      for i, row in design_info.iterrows():
        design_PE_num = row['PEs']
      if src_PE_num != design_PE_num:
        print(f'Error: {folder} {src_PE_num} vs {design_PE_num} PEs')
        passed_all = False
      else:
        print(f'Passed: {folder}')
    else:
      print(f'Error: {src_file} does not exist')
      passed_all = False

if passed_all:
  print('All passed')
else:
  print('Some failed')
